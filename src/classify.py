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
# Both 'laser_welded' and the generic 'welded' select the welded limit set.
_WELD_BASIS = {
    "cold_formed":  "cold",
    "press_braked": "cold",
    "hot_rolled":   "cold",
    "hot_finished": "cold",
    "laser_welded": "welded",
    "welded":       "welded",
}

_CLASSIFIED = {"RHS", "SHS", "CHS", "I", "H"}   # section types handled here

# inferred_failure_mode values that indicate local-buckling contamination and
# therefore disqualify a row from the global flexural buckling training set.
_LOCAL_CONTAMINATED = {"local", "interactive", "unknown"}


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


def _plate_elements(row, eps):
    """Compression plate elements of the section as (name, ratio, limits, factor).

    Each section type contributes the plates that can buckle locally under pure
    compression, each with its OWN EN limit set and epsilon power. Returns None
    when the section type is unhandled (e.g. Angle) or geometry is missing.
    """
    stype = row.get("section_type")
    t = row.get("t")
    if stype not in _CLASSIFIED or pd.isna(eps) or pd.isna(t) or t == 0:
        return None

    if stype in ("RHS", "SHS"):
        b, h = row.get("b"), row.get("h")
        if pd.isna(b) or pd.isna(h):
            return None
        return [("side_h", (h - 2*t) / t, _INTERNAL_LIMITS, eps),
                ("side_b", (b - 2*t) / t, _INTERNAL_LIMITS, eps)]

    if stype == "CHS":
        d = row.get("b")                                 # outer diameter stored under 'b'
        if pd.isna(d):
            return None
        return [("shell", d / t, _TUBULAR_LIMITS, eps**2)]   # NB epsilon^2

    if stype in ("I", "H"):
        b, h = row.get("b"), row.get("h")
        if pd.isna(b) or pd.isna(h):
            return None
        t_f = row.get("t_f", t); t_w = row.get("t_w", t)
        if pd.isna(t_f): t_f = t
        if pd.isna(t_w): t_w = t
        basis = _WELD_BASIS.get(row.get("forming_route"), "cold")
        return [("web",    (h - 2*t_f) / t_w,        _INTERNAL_LIMITS,        eps),
                ("flange", ((b - t_w) / 2) / t_f,    _OUTSTAND_LIMITS[basis], eps)]

    return None


def cross_section_class(row, eps):
    """EN 1993-1-4 class plus the GOVERNING plate slenderness and its utilisation.

    Returns (section_class, cs_slenderness, cs_slenderness_norm).

    The governing plate is the one nearest to (or furthest past) its own limits,
    ranked by (class, utilisation) where utilisation = ratio / (class-3 limit).
    Because the web (internal) and flange (outstand) carry DIFFERENT EN limits,
    selecting by raw c/t alone can name the wrong plate (e.g. an I-section whose
    web has the larger c/t but whose flange is the element actually driving the
    Class 4 failure). Utilisation makes the plates directly comparable, so
    cs_slenderness always reports the plate that governs the class, and the
    normalised value (>1 == past the Class 3 limit == Class 4) is a clean,
    cross-section-agnostic ML feature.

    Soft-fails to (pd.NA, nan, nan) for unhandled sections (e.g. Angle) or where
    geometry is missing, keeping the master build intact.
    """
    elements = _plate_elements(row, eps)
    if not elements:
        return pd.NA, np.nan, np.nan

    best_key, best = None, None
    for _name, ratio, limits, factor in elements:
        cls = _class_from_ratio(ratio, limits, factor)
        util = ratio / (limits[2] * factor)          # class-3 limit; >1 => Class 4
        key = (cls, util)
        if best_key is None or key > best_key:
            best_key, best = key, (cls, ratio, util)
    return best[0], best[1], best[2]


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
        return "local" if lambda_bar <= lambda_0 else "interactive"
    if lambda_bar <= lambda_0:                            # Class 1-3, stocky
        return "yielding"                                 # cross-section governs
    return "global_flexural"                              # Class 1-3, slender


def global_buckling_eligible(section_class, inferred_mode):
    """Whether a row is a clean global flexural buckling data point.

    Excludes any local-buckling-contaminated specimen (Class 4, or an inferred
    mode of local / interactive / unknown), enforcing the project's strict
    global-flexural scope systematically rather than by manual row deletion.
    Stocky 'yielding' points (Class 1-3 below the plateau) are retained, since
    they are valid low-slenderness points on the buckling curve.
    """
    if pd.isna(section_class) or section_class == 4:
        return False
    return inferred_mode not in _LOCAL_CONTAMINATED


def failure_mode_conflict(reported_mode, inferred_mode):
    """Flag clear scope-creep mislabels: a row the source reports as global
    flexural buckling that the computed classification finds to be PURE local
    buckling (stocky Class 4, no global component) -- e.g. the stocky
    buchanan2018 Class 4 CHS. Class-4 'interactive' rows are not flagged here,
    since a global component genuinely participates; they are still removed from
    the training set by `global_buckling_eligible`, which excludes all Class 4.
    """
    return reported_mode == "global_flexural" and inferred_mode == "local"


def classify(df):
    """Add EN 1993-1-4 classification columns to a feature-enriched frame.

    Expects `lambda_bar`, `sigma_02`, `E0` and the geometry columns to be present
    (i.e. run features.add_features first).
    """
    out = df.copy()
    out["epsilon"] = epsilon(out["sigma_02"], out["E0"])

    cls = out.apply(lambda r: cross_section_class(r, r["epsilon"]),
                    axis=1, result_type="expand")
    out[["section_class", "cs_slenderness", "cs_slenderness_norm"]] = cls
    out["section_class"] = out["section_class"].astype("Int64")

    out["lambda_0"] = out.apply(limiting_slenderness, axis=1)

    reported = out["failure_mode"] if "failure_mode" in out.columns \
        else pd.Series(pd.NA, index=out.index)

    out["inferred_failure_mode"] = [
        failure_mode(sc, lb, l0)
        for sc, lb, l0 in zip(out["section_class"], out["lambda_bar"], out["lambda_0"])
    ]
    out["global_buckling_eligible"] = [
        global_buckling_eligible(sc, fm)
        for sc, fm in zip(out["section_class"], out["inferred_failure_mode"])
    ]
    out["failure_mode_conflict"] = [
        failure_mode_conflict(rep, inf)
        for rep, inf in zip(reported, out["inferred_failure_mode"])
    ]
    return out