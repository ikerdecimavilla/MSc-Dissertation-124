"""EN 1993-1-4:2006 cross-section classification and failure-mode inference."""
import numpy as np
import pandas as pd

# --- Table 5.2 limits, parts in UNIFORM COMPRESSION (multiples of epsilon) ---
_INTERNAL_LIMITS = (25.7, 26.7, 30.7)          # internal parts: RHS/SHS, I-web
_OUTSTAND_LIMITS = {                           # outstand flanges: I-flange
    "cold":   (10.0, 10.4, 11.9),
    "welded": (9.0,  9.4,  11.0),
}
_TUBULAR_LIMITS = (50.0, 70.0, 90.0)           # CHS  -- NOTE: multiply epsilon**2

# forming_route -> outstand limit family (only affects open sections, i.e. I).
# hot_rolled / hot_finished are non-welded and have no dedicated EN row; they are
# mapped to the (more generous) cold-formed limits. Documented assumption.
_WELD_BASIS = {
    "cold_formed":  "cold",
    "press_braked": "cold",
    "hot_rolled":   "cold",
    "hot_finished": "cold",
    "laser_welded": "welded",
}

_CLASSIFIED = {"RHS", "SHS", "CHS", "I", "H"}   # section types handled here


def epsilon(sigma_02, E0):
    """Material factor, EN 1993-1-4 Table 5.2:  sqrt[(235/f_y)(E/210000)]."""
    return np.sqrt((235.0 / sigma_02) * (E0 / 210000.0))


def _class_from_ratio(ratio, limits, factor):
    """Return 1/2/3/4 by comparing `ratio` with (c1, c2, c3) * factor."""
    c1, c2, c3 = limits
    if ratio <= c1 * factor:
        return 1
    if ratio <= c2 * factor:
        return 2
    if ratio <= c3 * factor:
        return 3
    return 4


def cross_section_class(row, eps):
    """EN 1993-1-4 class (1-4) and governing plate slenderness for a column.

    Soft-fails to (pd.NA, np.nan) when geometry is missing or the section type
    is not handled (e.g. Angle), keeping the master build intact.
    """
    stype = row.get("section_type")
    t = row.get("t")
    if stype not in _CLASSIFIED or pd.isna(eps) or pd.isna(t) or t == 0:
        return pd.NA, np.nan

    if stype in ("RHS", "SHS"):
        b, h = row.get("b"), row.get("h")
        if pd.isna(b) or pd.isna(h):
            return pd.NA, np.nan
        gov = max((h - 2*t) / t, (b - 2*t) / t)          # c = h-2t / b-2t (sheet-1 note)
        return _class_from_ratio(gov, _INTERNAL_LIMITS, eps), gov

    if stype == "CHS":
        d = row.get("b")                                 # outer diameter stored under 'b'
        if pd.isna(d):
            return pd.NA, np.nan
        ratio = d / t
        return _class_from_ratio(ratio, _TUBULAR_LIMITS, eps**2), ratio   # NB epsilon^2

    if stype in ("I", "H"):
        b, h = row.get("b"), row.get("h")
        if pd.isna(b) or pd.isna(h):
            return pd.NA, np.nan
        t_f = row.get("t_f", t); t_w = row.get("t_w", t)
        if pd.isna(t_f): t_f = t
        if pd.isna(t_w): t_w = t
        web = (h - 2*t_f) / t_w                           # internal compression part
        flange = ((b - t_w) / 2) / t_f                    # outstand half-flange
        basis = _WELD_BASIS.get(row.get("forming_route"), "cold")
        cls = max(_class_from_ratio(web, _INTERNAL_LIMITS, eps),
                  _class_from_ratio(flange, _OUTSTAND_LIMITS[basis], eps))
        return cls, max(web, flange)

    return pd.NA, np.nan


def limiting_slenderness(row):
    """lambda_0 for flexural buckling, EN 1993-1-4 Table 5.3."""
    stype = row.get("section_type")
    if stype in ("RHS", "SHS", "CHS"):
        return 0.40                                       # hollow sections
    if stype in ("I", "H"):
        basis = _WELD_BASIS.get(row.get("forming_route"), "cold")
        return 0.20 if basis == "welded" else 0.40        # welded vs rolled/cold open
    return 0.40


def failure_mode(section_class, lambda_bar, lambda_0):
    """Combine local susceptibility (class) with global slenderness (lambda_bar).

    Returns 'unknown' when the class could not be determined, so a label is
    never invented (e.g. thickness absent, or an excluded angle).
    """
    if pd.isna(section_class) or pd.isna(lambda_bar):
        return "unknown"
    if section_class == 4:                                # local-susceptible
        return "local" if lambda_bar <= lambda_0 else "local_global_interaction"
    if lambda_bar <= lambda_0:                            # Class 1-3, stocky
        return "yielding"                                 # cross-section governs
    return "global_flexural"                              # Class 1-3, slender


def classify(df):
    """Add EN 1993-1-4 classification columns to a feature-enriched frame.

    Expects `lambda_bar`, `sigma_02`, `E` and the geometry columns to be present
    (i.e. run features.add_features first).
    """
    out = df.copy()
    out["epsilon"] = epsilon(out["sigma_02"], out["E0"])

    cls = out.apply(lambda r: cross_section_class(r, r["epsilon"]),
                    axis=1, result_type="expand")
    out[["section_class", "cs_slenderness"]] = cls
    out["section_class"] = out["section_class"].astype("Int64")

    out["lambda_0"] = out.apply(limiting_slenderness, axis=1)
    out["inferred_failure_mode"] = [
        failure_mode(sc, lb, l0)
        for sc, lb, l0 in zip(out["section_class"], out["lambda_bar"], out["lambda_0"])
    ]
    return out