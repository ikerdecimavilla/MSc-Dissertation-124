from pathlib import Path
import numpy as np
import pandas as pd
from src.features import add_features
from src.classify import classify

# Anchor paths relative to this script's exact location
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXTRACTED = DATA_DIR / "extracted"
PROCESSED = DATA_DIR / "processed"


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

    # 3. lambda_bar dual-formula guard: sqrt(N_y/N_cr) vs (Le/(pi*R))*sqrt(f_y/E).
    lbar_alt = (master["Le"] / (np.pi * master["R"])) * \
        np.sqrt(master["sigma_02"] / master["E0"])
    assert np.allclose(master["lambda_bar"], lbar_alt, rtol=1e-6), \
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

    # 7. No local-contaminated (Class 4) row may be flagged eligible for the
    #    global flexural buckling training set.
    bad_elig = master["global_buckling_eligible"] & (master["section_class"] == 4)
    assert not bad_elig.any(), \
        f"Class-4 row marked global-buckling eligible: {master.loc[bad_elig, 'specimen_id'].tolist()}"


def build():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    frames = []

    csv_files = list(EXTRACTED.glob("*.csv"))
    if not csv_files:
        return print(f"No CSVs found in {EXTRACTED}. Pipeline halted.")

    for csv in sorted(csv_files):
        print(f"Processing: {csv.name}")
        df = pd.read_csv(csv)

        df = df.dropna(subset=["section_type"])

        enriched = add_features(df)      # geometry + mechanics (A, I, lambda_bar, ...)
        classified = classify(enriched)  # EN 1993-1-4 class + inferred_failure_mode
        classified.to_csv(PROCESSED / csv.name, index=False)
        frames.append(classified)

    # Combine, validate, and save master dataset
    if frames:
        master = pd.concat(frames, ignore_index=True)
        _validate(master)
        master.to_csv(DATA_DIR / "master.csv", index=False)
        print("Success! master.csv updated.")


if __name__ == "__main__":
    build()