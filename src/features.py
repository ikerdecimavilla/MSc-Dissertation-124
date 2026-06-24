import numpy as np
import pandas as pd
from .sections import SECTION_CALCS

# Section types that have a genuine strong/weak axis distinction. For these,
# buckling_axis MUST be supplied; SHS and CHS are symmetric (I_major == I_minor)
# so the axis is irrelevant and may be left blank.
_ASYMMETRIC = {"RHS", "I", "H"}


def add_features(df):
    out = df.copy()

    # 1. Base Geometry
    geom = out.apply(_section_props, axis=1, result_type="expand")
    out[["A", "I_major", "I_minor"]] = geom

    # 2. Critical Inertia (axis-aware, fails loudly on missing axis)
    I_crit = _critical_inertia(out)

    # 3. Radius of Gyration (Capital R)
    out["R"] = np.sqrt(I_crit / out["A"])

    # 4. Standard Slenderness (lambda)
    out["lambda"] = out["Le"] / out["R"]

    # 5. Euler Elastic Buckling Load (kN)
    out["N_cr"] = (np.pi**2 * out["E0"] * I_crit / out["Le"]**2) / 1000

    # 6. Yield Load (kN, using 0.2% proof stress)
    out["N_y"] = out["A"] * out["sigma_02"] / 1000

    # 7. Non-dimensional Slenderness (ratio — unaffected by the kN scaling)
    out["lambda_bar"] = np.sqrt(out["N_y"] / out["N_cr"])

    # 8. Strength Reduction Factor (now kN / kN)
    out["chi"] = out["N_u"] / out["N_y"]

    # 9. Total effective global imperfection (magnitude of the net offset)
    out["w_total"] = _total_imperfection(out)

    # NOTE: epsilon (material factor) is computed canonically in classify.py,
    # which runs immediately after add_features in the build. It was previously
    # duplicated here; removed to keep a single source of truth.

    return out


def _section_props(row):
    fn = SECTION_CALCS.get(row["section_type"])
    if fn is None:
        raise ValueError(
            f"No section calc for {row['section_type']!r} "
            f"(ref_key={row.get('ref_key')})")
    return fn(row)


def _critical_inertia(out):
    """Select I about the buckling axis.

    major -> I_major, minor -> I_minor. For symmetric sections (SHS/CHS) the two
    are equal, so a blank/`-`/NaN axis is acceptable and resolves to I_minor.
    For sections with a real major/minor distinction (RHS/I/H) a missing axis is
    an error and is raised loudly rather than silently defaulting to the minor
    axis (which previously corrupted lambda_bar, e.g. the Afshan RHS rows).
    """
    axis = out["buckling_axis"]
    I_crit = np.select(
        [axis == "major", axis == "minor"],
        [out["I_major"], out["I_minor"]],
        default=np.nan,
    )

    symmetric = ~out["section_type"].isin(_ASYMMETRIC)
    I_crit = np.where(np.isnan(I_crit) & symmetric.to_numpy(),
                      out["I_minor"].to_numpy(), I_crit)

    missing = np.isnan(I_crit)
    if missing.any():
        bad = out.loc[missing, "specimen_id"].tolist()
        raise ValueError(
            "buckling_axis is mandatory for RHS/I/H sections but is missing for: "
            f"{bad}. Populate it from the source before building.")
    return I_crit


def _total_imperfection(out):
    """Total effective global imperfection experienced by the column.

    Stored as a non-negative magnitude. w_0 (measured bow) and w_e (applied
    eccentricity) carry a direction sign within each source, so the net midspan
    offset is their algebraic sum; severity is the magnitude of that sum. This
    prevents the negative w_total values produced by a raw signed sum.

    For CHS members with biaxial imperfections, if the per-axis components are
    present (w_0_1, w_e_1, w_0_2, w_e_2) the resultant of the two net axis
    offsets is used instead, per Rasmussen-style 2D measurements.
    """
    w_total = (out["w_0"].fillna(0) + out["w_e"].fillna(0)).abs()

    biax_cols = {"w_0_1", "w_e_1", "w_0_2", "w_e_2"}
    if biax_cols.issubset(out.columns):
        chs = out["section_type"] == "CHS"
        net1 = out["w_0_1"].fillna(0) + out["w_e_1"].fillna(0)
        net2 = out["w_0_2"].fillna(0) + out["w_e_2"].fillna(0)
        resultant = np.sqrt(net1**2 + net2**2)
        w_total = w_total.where(~chs, resultant)

    return w_total