"""Geometric and mechanical feature engineering for the master dataset.

Two entry points, split around classify.classify_sections because the
effective area of Class 4 sections feeds the squash load and hence
lambda_bar / chi_exp (KGW Eqs. 16-17 basis):

  add_geometry(df)   gross section properties (A, I_major, I_minor)
  add_mechanics(df)  Le, buckling axis, R, N_cr, N_squash, lambda_bar,
                     chi_exp, Delta, aspect_ratio, hardening_ratio,
                     imperfection features
                     (requires A_eff: run classify.classify_sections first)
"""
import numpy as np
import pandas as pd
from .sections import SECTION_CALCS

# Section types with a genuine strong/weak axis distinction. SHS and CHS are
# perfectly symmetric (I_major == I_minor), so no orthogonal axis is weaker and
# the buckling axis is recorded as "-".
_ASYMMETRIC = {"RHS", "I", "H"}

# Effective-length factors, EN end conditions (data_dictionary.md, Le row).
_K_FACTOR = {"pin-pin": 1.0, "fixed-fixed": 0.5, "fixed-pin": 0.7, "fixed-free": 2.0}


def add_geometry(df):
    """Gross cross-section properties from raw dimensions."""
    out = df.copy()
    geom = out.apply(_section_props, axis=1, result_type="expand")
    out[["A", "I_major", "I_minor"]] = geom
    return out


def add_mechanics(df):
    """Member mechanics and ML features on the effective-area basis.

    Squash load (KGW: P_y = A f_y, or A_eff f_y for Class 4). A_eff equals A
    for Class 1-3 by construction, so a single expression covers both:
        N_squash = A_eff * sigma_02
    lambda_bar and chi_exp follow on the same basis (EC3 Class 4 definition
    lambda_bar = sqrt(A_eff f_y / N_cr); N_cr remains on gross I).
    """
    out = df.copy()

    # 1. Effective length: reported, else derived from L * k(boundary_condition)
    out["Le"], out["Le_source"] = _effective_length(out)

    # 2. Buckling axis: reported -> symmetric "-" -> derived minor (+ provenance)
    axis_info = out.apply(
        lambda r: _resolve_buckling_axis(r, r["I_major"], r["I_minor"]),
        axis=1, result_type="expand")
    out["buckling_axis"], out["buckling_axis_source"] = axis_info[0], axis_info[1]
    I_crit = np.where(out["buckling_axis"] == "major", out["I_major"], out["I_minor"])

    # 3. Radius of gyration about the buckling axis (gross section)
    out["R"] = np.sqrt(I_crit / out["A"])

    # 4. Euler elastic critical load (kN) -- gross section properties
    out["N_cr"] = (np.pi**2 * out["E0"] * I_crit / out["Le"]**2) / 1000

    # 5. Squash load (kN) on the effective-area basis (A_eff == A for Class 1-3)
    out["N_squash"] = out["A_eff"] * out["sigma_02"] / 1000

    # 6. Non-dimensional slenderness, KGW / EC3 definition sqrt(N_squash / N_cr)
    out["lambda_bar"] = np.sqrt(out["N_squash"] / out["N_cr"])

    # 7. Experimental strength reduction factor on the same basis
    out["chi_exp"] = out["N_u"] / out["N_squash"]

    # 8. Delta = f_y / E: the material ratio governing the transition
    #    slenderness in KGW (direct model input alongside n and lambda_bar)
    out["Delta"] = out["sigma_02"] / out["E0"]

    # 9. Cross-section aspect ratio (1.0 for SHS/CHS by construction)
    out["aspect_ratio"] = _aspect_ratio(out)

    # 10. Strain-hardening capacity (nullable where sigma_u unreported)
    sigma_u = out.get("sigma_u", pd.Series(np.nan, index=out.index))
    out["hardening_ratio"] = sigma_u / out["sigma_02"]

    # 11. Total effective global imperfection (non-negative magnitude) and its
    #     normalised form (Stage-2 beta predictor)
    out["w_total"] = _total_imperfection(out)
    out["w_total_norm"] = out["w_total"] / out["Le"]

    return out


def _section_props(row):
    fn = SECTION_CALCS.get(row["section_type"])
    if fn is None:
        raise ValueError(
            f"No section calc for {row['section_type']!r} "
            f"(ref_key={row.get('ref_key')})")
    return fn(row)


def _aspect_ratio(out):
    """max(h, b) / min(h, b); 1.0 for CHS (h is null) and inherently for SHS."""
    b = pd.to_numeric(out["b"], errors="coerce")
    h = pd.to_numeric(out["h"], errors="coerce")
    ar = np.maximum(b, h) / np.minimum(b, h)
    return pd.Series(np.where(h.isna(), 1.0, ar), index=out.index)


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

    # CHS biaxial imperfections: where the per-axis components are supplied, the
    # effective imperfection is the resultant of the two net (bow + eccentricity)
    # axis offsets, not the 1-D sum. Applied per-row so partial coverage is safe:
    # CHS rows with all four components use the resultant; everything else keeps
    # the planar |w_0 + w_e|.
    biax_cols = ["w_0_1", "w_e_1", "w_0_2", "w_e_2"]
    if set(biax_cols).issubset(out.columns):
        have_all = out[biax_cols].notna().all(axis=1)
        # Symmetric sections (SHS, CHS) can bend biaxially, so the effective
        # imperfection is the resultant of the two orthogonal net offsets.
        use_resultant = out["section_type"].isin(["SHS", "CHS"]) & have_all
        net1 = out["w_0_1"] + out["w_e_1"]
        net2 = out["w_0_2"] + out["w_e_2"]
        resultant = np.sqrt(net1**2 + net2**2)
        w_total = w_total.where(~use_resultant, resultant)

    return w_total
