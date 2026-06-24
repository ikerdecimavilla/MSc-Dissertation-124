import numpy as np
import pandas as pd
from .sections import SECTION_CALCS

# Section types with a genuine strong/weak axis distinction. SHS and CHS are
# perfectly symmetric (I_major == I_minor), so no orthogonal axis is weaker and
# the buckling axis is recorded as "-".
_ASYMMETRIC = {"RHS", "I", "H"}

# Effective-length factors, EN end conditions (data_dictionary.md, Le row).
_K_FACTOR = {"pin-pin": 1.0, "fixed-fixed": 0.5, "fixed-pin": 0.7, "fixed-free": 2.0}


def add_features(df):
    out = df.copy()

    # 1. Base geometry (A, I_major, I_minor)
    geom = out.apply(_section_props, axis=1, result_type="expand")
    out[["A", "I_major", "I_minor"]] = geom

    # 2. Effective length: reported, else derived from L * k(boundary_condition)
    out["Le"], out["Le_source"] = _effective_length(out)

    # 3. Buckling axis: reported -> symmetric "-" -> derived minor (+ provenance)
    axis_info = out.apply(
        lambda r: _resolve_buckling_axis(r, r["I_major"], r["I_minor"]),
        axis=1, result_type="expand")
    out["buckling_axis"], out["buckling_axis_source"] = axis_info[0], axis_info[1]
    I_crit = np.where(out["buckling_axis"] == "major", out["I_major"], out["I_minor"])

    # 4. Radius of gyration about the buckling axis
    out["R"] = np.sqrt(I_crit / out["A"])

    # 5. Standard (dimensional) slenderness
    out["lambda"] = out["Le"] / out["R"]

    # 6. Euler elastic critical load (kN)
    out["N_cr"] = (np.pi**2 * out["E0"] * I_crit / out["Le"]**2) / 1000

    # 7. Squash (yield) load (kN)
    out["N_y"] = out["A"] * out["sigma_02"] / 1000

    # 8. Non-dimensional slenderness (ratio — unaffected by the kN scaling)
    out["lambda_bar"] = np.sqrt(out["N_y"] / out["N_cr"])

    # 9. Experimental strength reduction factor
    out["chi"] = out["N_u"] / out["N_y"]

    # 10. Total effective global imperfection (non-negative magnitude)
    out["w_total"] = _total_imperfection(out)

    return out


def _section_props(row):
    fn = SECTION_CALCS.get(row["section_type"])
    if fn is None:
        raise ValueError(
            f"No section calc for {row['section_type']!r} "
            f"(ref_key={row.get('ref_key')})")
    return fn(row)


def _effective_length(out):
    """Effective buckling length Le (mm), with provenance.

    Honours a reported Le; otherwise derives Le = k * L using the EN effective
    length factor for the row's boundary_condition (k = 1.0 pin-pin, 0.5
    fixed-fixed, 0.7 fixed-pin, 2.0 fixed-free). Raises if Le is absent and the
    boundary_condition is missing/unrecognised, so a length is never invented.
    """
    if "Le" in out.columns:
        Le = pd.to_numeric(out["Le"], errors="coerce").copy()
    else:
        Le = pd.Series(np.nan, index=out.index)

    source = pd.Series(np.where(Le.notna(), "reported", "derived"), index=out.index)

    missing = Le.isna()
    if missing.any():
        k = out.loc[missing, "boundary_condition"].map(_K_FACTOR)
        Le.loc[missing] = out.loc[missing, "L"] * k

    unresolved = Le.isna()
    if unresolved.any():
        bad = out.loc[unresolved, "specimen_id"].tolist()
        raise ValueError(
            "Le is not reported and cannot be derived (boundary_condition "
            f"missing or unrecognised) for: {bad}")
    return Le, source


def _resolve_buckling_axis(row, I_major, I_minor):
    """Determine the flexural buckling axis and record how it was obtained.

      reported  -- axis stated in the source ('major'/'minor'); honoured as-is.
      symmetric -- SHS/CHS (or I_major == I_minor): no weaker axis exists -> "-".
      derived   -- asymmetric (RHS/I/H), axis not reported. In a standard
                   pin-ended test with no intermediate lateral bracing the
                   column buckles about its minor axis, since I_minor < I_major
                   gives the smaller r, the highest lambda_bar and the lowest
                   N_cr (path of least resistance).

    If a source intentionally braced the member to force major-axis buckling,
    set buckling_axis='major' in that extracted CSV; it is then 'reported'.
    """
    # Symmetric sections take precedence: no orthogonal axis is weaker -> "-",
    # even if a source loosely names one.
    if row["section_type"] not in _ASYMMETRIC or np.isclose(I_major, I_minor, rtol=1e-3):
        return "-", "symmetric"

    ax = row.get("buckling_axis")
    if ax in ("major", "minor"):
        return ax, "reported"

    return "minor", "derived"


def _total_imperfection(out):
    """Total effective global imperfection, stored as a non-negative magnitude.

    w_0 (measured bow) and w_e (applied eccentricity) carry a direction sign, so
    the net midspan offset is their algebraic sum; severity is its magnitude.
    (This refines the dictionary's literal w_0 + w_e, which can go negative when
    the two oppose — undesirable for the Stage-2 imperfection feature.)
    For CHS with biaxial imperfections, if per-axis components are present
    (w_0_1, w_e_1, w_0_2, w_e_2) the resultant of the two net axis offsets is used.
    """
    w_total = (out["w_0"].fillna(0) + out["w_e"].fillna(0)).abs()

    biax_cols = {"w_0_1", "w_e_1", "w_0_2", "w_e_2"}
    if biax_cols.issubset(out.columns):
        chs = out["section_type"] == "CHS"
        net1 = out["w_0_1"].fillna(0) + out["w_e_1"].fillna(0)
        net2 = out["w_0_2"].fillna(0) + out["w_e_2"].fillna(0)
        w_total = w_total.where(~chs, np.sqrt(net1**2 + net2**2))

    return w_total