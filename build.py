from pathlib import Path
import logging
import numpy as np
import pandas as pd
from src.features import add_geometry, add_mechanics
from src.classify import classify_sections, infer_failure_modes
from src.kgw_batch import add_predictions

# Anchor paths relative to this script's exact location
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXTRACTED = DATA_DIR / "extracted"
PROCESSED = DATA_DIR / "processed"

# Tidy column order for master.csv; any extra columns are appended untouched.
_COLUMN_ORDER = [
    # provenance
    "specimen_id", "source_id", "study_id", "data_type",
    # material
    "material_grade", "material_type", "forming_route",
    "E0", "sigma_02", "n", "n_source", "sigma_10", "n_prime", "sigma_u",
    # raw geometry
    "section_type", "b", "h", "t", "t_f", "t_w", "L",
    "boundary_condition", "Le", "Le_source",
    "buckling_axis", "buckling_axis_source",
    # imperfections
    "w_0", "w_e", "w_0_1", "w_e_1", "w_0_2", "w_e_2", "w_total", "w_total_norm",
    # test outputs
    "N_u", "reported_failure_mode",
    # computed section properties
    "A", "I_major", "I_minor", "R", "N_cr", "epsilon",
    "section_class", "cs_slenderness_norm", "lambda_0",
    "A_eff", "rho_eff", "N_squash",
    # ML features / targets
    "lambda_bar", "chi_exp", "Delta", "aspect_ratio", "hardening_ratio",
    # solver predictions (KGW + Eurocode baselines)
    "chi_perfect", "chi_kgw", "chi_eurocode",
    "N_perfect", "N_kgw", "N_eurocode", "kgw_convergence_flag",
    # failure-mode inference and scope
    "inferred_failure_mode", "anomalous_interactive_mode", "flexural_scope",
]


def _validate(master):
    """Loud, build-time integrity checks on the assembled master frame."""
    # 1. Major axis must carry the larger inertia, by definition.
    swapped = master["I_major"] < master["I_minor"] - 1e-9
    assert not swapped.any(), \
        f"I_major < I_minor for: {master.loc[swapped, 'specimen_id'].tolist()}"

    # 2. Effective length must be resolved for every row.
    no_le = master["Le"].isna()
    assert not no_le.any(), \
        f"Le unresolved for: {master.loc[no_le, 'specimen_id'].tolist()}"

    # 3. lambda_bar dual-formula guard on the A_eff basis:
    #    sqrt(N_squash/N_cr) == (Le/(pi*R)) * sqrt(f_y/E) * sqrt(A_eff/A).
    lbar_alt = (master["Le"] / (np.pi * master["R"])) * \
        np.sqrt(master["sigma_02"] / master["E0"]) * \
        np.sqrt(master["A_eff"] / master["A"])
    both = master["lambda_bar"].notna() & lbar_alt.notna()
    assert np.allclose(master.loc[both, "lambda_bar"], lbar_alt[both], rtol=1e-6), \
        "lambda_bar disagrees with its closed-form equivalent (unit error?)"

    # 4. Welded open sections must use the 0.20 plateau (EN 1993-1-4 Table 5.3).
    welded_open = master["section_type"].isin(["I", "H"]) & \
        master["forming_route"].isin(["welded", "laser_welded"])
    bad_l0 = welded_open & (master["lambda_0"] != 0.20)
    assert not bad_l0.any(), \
        f"welded open section with lambda_0 != 0.20: {master.loc[bad_l0, 'specimen_id'].tolist()}"

    # 5. Total imperfection is a magnitude and must be non-negative.
    neg = master["w_total"] < 0
    assert not neg.any(), \
        f"negative w_total for: {master.loc[neg, 'specimen_id'].tolist()}"

    # 6. Class must agree with the governing-plate utilisation: Class 4 iff the
    #    governing plate is past its Class 3 limit (norm > 1).
    cl, norm = master["section_class"], master["cs_slenderness_norm"]
    known = cl.notna() & norm.notna()
    bad_c4 = known & (cl == 4) & (norm <= 1 - 1e-9)
    bad_lo = known & (cl < 4) & (norm > 1 + 1e-9)
    assert not bad_c4.any(), \
        f"Class 4 with utilisation <= 1: {master.loc[bad_c4, 'specimen_id'].tolist()}"
    assert not bad_lo.any(), \
        f"Class 1-3 with utilisation > 1: {master.loc[bad_lo, 'specimen_id'].tolist()}"

    # 7. Effective area sanity: Class 1-3 fully effective (A_eff == A); Class 4
    #    reduced (A_eff <= A) and strictly reduced away from the class boundary;
    #    rho_eff in (0, 1] wherever defined.
    #    NB equality is permitted for marginal Class 4 flat-element sections:
    #    EN 1993-1-4:2006 places the rho = 1 point of Eq. 5.1 (lambda_p 0.5409)
    #    fractionally above the Class 3 limit 30.7*eps (lambda_p 0.5405), so a
    #    section a sliver past the limit is Class 4 yet fully effective
    #    (e.g. huang2013_08, utilisation 1.0006).
    known = master["section_class"].notna() & master["A_eff"].notna()
    c13 = known & (master["section_class"] < 4)
    c4 = known & (master["section_class"] == 4)
    assert np.allclose(master.loc[c13, "A_eff"], master.loc[c13, "A"], rtol=1e-12), \
        "Class 1-3 row with A_eff != A"
    bad_c4a = c4 & (master["A_eff"] > master["A"] + 1e-9)
    assert not bad_c4a.any(), \
        f"Class 4 row with A_eff > A: {master.loc[bad_c4a, 'specimen_id'].tolist()}"
    away = c4 & (master["cs_slenderness_norm"] > 1.002)          # past boundary sliver
    bad_c4b = away & (master["A_eff"] >= master["A"] - 1e-9) & \
        master["section_type"].isin(["RHS", "SHS", "I", "H"])
    assert not bad_c4b.any(), \
        f"clearly Class 4 row without reduction: {master.loc[bad_c4b, 'specimen_id'].tolist()}"
    rho = master.loc[known, "rho_eff"]
    assert ((rho > 0) & (rho <= 1 + 1e-12)).all(), "rho_eff outside (0, 1]"

    # 8. Every in-scope row must be fully resolved for training.
    scoped = master["flexural_scope"]
    needed = ["A_eff", "N_squash", "lambda_bar", "chi_exp"]
    incomplete = scoped & master[needed].isna().any(axis=1)
    assert not incomplete.any(), \
        f"in-scope row with unresolved features: {master.loc[incomplete, 'specimen_id'].tolist()}"

    # 9. Anomalous rows (local participation on Class 1-3) never enter scope.
    bad_anom = master["anomalous_interactive_mode"] & master["flexural_scope"]
    assert not bad_anom.any(), \
        f"anomalous row marked in-scope: {master.loc[bad_anom, 'specimen_id'].tolist()}"

    # 10. Solver predictions: converged rows carry finite chi values; the
    #     corrected solve cannot exceed the perfect one at or above the
    #     transition slenderness (below it the correction may raise the load,
    #     KGW Fig. 8); the Eurocode curve is capped at 1; every N_* equals
    #     chi_* x N_squash; and at least one row must have converged.
    conv = master["kgw_convergence_flag"].astype(bool)
    assert conv.any(), "KGW batch: zero rows converged - systemic failure"
    bad_nan = conv & master[["chi_perfect", "chi_kgw"]].isna().any(axis=1)
    assert not bad_nan.any(), \
        f"converged row with NaN chi: {master.loc[bad_nan, 'specimen_id'].tolist()}"
    hi = conv & (master["lambda_bar"] >= 0.9)
    bad_ord = hi & (master["chi_kgw"] > master["chi_perfect"] + 1e-9)
    assert not bad_ord.any(), \
        f"chi_kgw > chi_perfect at lambda_bar >= 0.9: {master.loc[bad_ord, 'specimen_id'].tolist()}"
    ec = master["chi_eurocode"].dropna()
    assert ((ec > 0) & (ec <= 1.0 + 1e-12)).all(), "chi_eurocode outside (0, 1]"
    for chi_col, n_col in (("chi_perfect", "N_perfect"),
                           ("chi_kgw", "N_kgw"),
                           ("chi_eurocode", "N_eurocode")):
        expect = master[chi_col] * master["N_squash"]
        both = expect.notna() & master[n_col].notna()
        assert np.allclose(master.loc[both, n_col], expect[both], rtol=1e-12), \
            f"{n_col} != {chi_col} * N_squash"


def _order_columns(df):
    ordered = [c for c in _COLUMN_ORDER if c in df.columns]
    extras = [c for c in df.columns if c not in _COLUMN_ORDER]
    return df[ordered + extras]


def build():
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    PROCESSED.mkdir(parents=True, exist_ok=True)
    frames = []

    csv_files = list(EXTRACTED.glob("*.csv"))
    if not csv_files:
        return print(f"No CSVs found in {EXTRACTED}. Pipeline halted.")

    for csv in sorted(csv_files):
        print(f"Processing: {csv.name}")
        df = pd.read_csv(csv)

        df = df.dropna(subset=["section_type"])

        # `failure_mode` in extracted inputs is the source-reported mode; carry
        # it as `reported_failure_mode` (ground truth for scope decisions).
        if "failure_mode" in df.columns and "reported_failure_mode" not in df.columns:
            df = df.rename(columns={"failure_mode": "reported_failure_mode"})

        enriched = add_geometry(df)                # gross A, I_major, I_minor
        classified = classify_sections(enriched)   # EN class + A_eff / rho_eff
        enriched = add_mechanics(classified)       # N_squash, lambda_bar, chi_exp, ...
        final = infer_failure_modes(enriched)      # inferred mode + flags + scope
        final = add_predictions(final)             # KGW + Eurocode baselines
        final = _order_columns(final)
        final.to_csv(PROCESSED / csv.name, index=False)
        frames.append(final)

    # Combine, validate, and save master dataset
    if frames:
        master = pd.concat(frames, ignore_index=True)
        master = _order_columns(master)
        _validate(master)
        master.to_csv(DATA_DIR / "master.csv", index=False)
        n_conv = int(master["kgw_convergence_flag"].sum())
        print("Success! master.csv updated.")
        print(f"  rows: {len(master)}  |  in flexural scope: "
              f"{int(master['flexural_scope'].sum())}  |  anomalous: "
              f"{int(master['anomalous_interactive_mode'].sum())}  |  "
              f"KGW converged: {n_conv}/{len(master)}")


if __name__ == "__main__":
    build()
