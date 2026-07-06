"""EN 1993-1-4:2006 cross-section classification and failure-mode inference.

Split into two phases around the mechanics step in features.py, because the
effective area feeds lambda_bar and lambda_bar feeds the mode inference:

  classify_sections(df)    epsilon -> section_class -> lambda_0 -> A_eff/rho_eff
                           (requires gross geometry: run features.add_geometry first)
  infer_failure_modes(df)  inferred_failure_mode + anomalous_interactive_mode
                           + flexural_scope
                           (requires lambda_bar: run features.add_mechanics first)
"""
import numpy as np
import pandas as pd

from .sections import WELD_BASIS, effective_area

# --- Table 5.2 limits, parts in UNIFORM COMPRESSION (multiples of epsilon) ---
_INTERNAL_LIMITS = (25.7, 26.7, 30.7)          # internal parts: RHS/SHS, I-web
_OUTSTAND_LIMITS = {                           # outstand flanges: I-flange
    "cold":   (10.0, 10.4, 11.9),
    "welded": (9.0,  9.4,  11.0),
}
_TUBULAR_LIMITS = (50.0, 70.0, 90.0)           # CHS  -- NOTE: multiply epsilon**2

_CLASSIFIED = {"RHS", "SHS", "CHS", "I", "H"}   # section types handled here

# Reported failure-mode vocabulary is normalised before use so that source
# notation variants (and future sources) resolve to a controlled set.
_MODE_ALIASES = {
    "global_flexural": "global_flexural",
    "flexural":        "global_flexural",
    "global":          "global_flexural",
    "f":               "global_flexural",
    "fb":              "global_flexural",
    "local":           "local",
    "l":               "local",
    "interactive":     "interactive",
    "local_global":    "interactive",
    "local+global":    "interactive",
    "l+f":             "interactive",
    "yielding":        "yielding",
    "y":               "yielding",
}

# Modes outside the pure global flexural buckling formulation (KGW Eqs. 16-17):
# any torsional participation or distortional buckling excludes the specimen.
_EXCLUDED_MODES = {"torsional", "flexural_torsional", "distortional"}

# Modes eligible for the flexural training set. 'local' and 'interactive' are
# in scope ONLY for Class 4 sections, where the local reduction is carried by
# A_eff; on Class 1-3 sections they are anomalous (see anomalous flag).
_SCOPE_MODES = {"global_flexural", "yielding", "local", "interactive"}


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
        basis = WELD_BASIS.get(row.get("forming_route"), "cold")
        return [("web",    (h - 2*t_f) / t_w,        _INTERNAL_LIMITS,        eps),
                ("flange", ((b - t_w) / 2) / t_f,    _OUTSTAND_LIMITS[basis], eps)]

    return None


def cross_section_class(row, eps):
    """EN 1993-1-4 class plus the governing plate's normalised utilisation.

    Returns (section_class, cs_slenderness_norm).

    The governing plate is the one nearest to (or furthest past) its own limits,
    ranked by (class, utilisation) where utilisation = ratio / (class-3 limit).
    Because the web (internal) and flange (outstand) carry DIFFERENT EN limits,
    selecting by raw c/t alone can name the wrong plate; utilisation makes the
    plates directly comparable, and the normalised value (>1 == past the Class 3
    limit == Class 4) is a clean, cross-section-agnostic ML feature.

    Soft-fails to (pd.NA, nan) for unhandled sections (e.g. Angle) or where
    geometry is missing, keeping the master build intact.
    """
    elements = _plate_elements(row, eps)
    if not elements:
        return pd.NA, np.nan

    best_key, best = None, None
    for _name, ratio, limits, factor in elements:
        cls = _class_from_ratio(ratio, limits, factor)
        util = ratio / (limits[2] * factor)          # class-3 limit; >1 => Class 4
        key = (cls, util)
        if best_key is None or key > best_key:
            best_key, best = key, (cls, util)
    return best[0], best[1]


def limiting_slenderness(row):
    """lambda_0 for flexural buckling, EN 1993-1-4 Table 5.3."""
    stype = row.get("section_type")
    if stype in ("RHS", "SHS", "CHS"):
        return 0.40                                       # hollow sections
    if stype in ("I", "H"):
        basis = WELD_BASIS.get(row.get("forming_route"), "cold")
        return 0.20 if basis == "welded" else 0.40        # welded vs rolled/cold open
    return 0.40


def imperfection_factor(row):
    """alpha for flexural buckling, EN 1993-1-4:2006 Table 5.3.

    Cold formed open sections and hollow sections (welded and seamless):
    alpha = 0.49 (paired with lambda_0 = 0.40). Welded open sections:
    alpha = 0.49 about the major axis, 0.76 about the minor axis (paired with
    lambda_0 = 0.20). Grade does NOT select the curve in this standard - it
    enters only through f_y inside lambda_bar. Pairs with
    `limiting_slenderness` (lambda_0); keep the two in sync.
    """
    stype = row.get("section_type")
    if stype in ("I", "H"):
        basis = WELD_BASIS.get(row.get("forming_route"), "cold")
        if basis == "welded":
            # buckling_axis is always resolved for I/H (asymmetric sections);
            # anything other than an explicit 'major' is treated as minor,
            # which is the conservative branch.
            return 0.49 if row.get("buckling_axis") == "major" else 0.76
    return 0.49


def normalise_mode(raw):
    """Map a reported failure-mode string onto the controlled vocabulary.

    Torsional participation is detected by keyword so that source variants
    ('FT', 'flexural-torsional', 'torsional-flexural', ...) all resolve to the
    excluded families. Unrecognised strings are passed through lower-cased so
    they surface in audits rather than being silently coerced.
    """
    if pd.isna(raw):
        return pd.NA
    s = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
    if "distor" in s:
        return "distortional"
    if s in ("ft", "ftb", "tf", "tfb") or "torsion" in s:
        return "torsional" if s in ("t", "torsional") else "flexural_torsional"
    return _MODE_ALIASES.get(s, s)


def infer_mode(section_class, lambda_bar, lambda_0):
    """Failure-mode inference from EN class and member slenderness.

    Class 4, lambda_bar <= lambda_0 : 'local'        (cross-section governs)
    Class 4, lambda_bar >  lambda_0 : 'interactive'  (local-global flexural)
    Class 1-3, lambda_bar <= lambda_0 : 'yielding'
    Class 1-3, lambda_bar >  lambda_0 : 'global_flexural'

    lambda_bar is on the A_eff basis for Class 4 (KGW / EC3 definition).
    Returns 'unknown' when the class or slenderness could not be determined,
    so a label is never invented.
    """
    if pd.isna(section_class) or pd.isna(lambda_bar):
        return "unknown"
    if section_class == 4:
        return "local" if lambda_bar <= lambda_0 else "interactive"
    if lambda_bar <= lambda_0:
        return "yielding"
    return "global_flexural"


def _anomalous(section_class, mode_eff):
    """Local participation reported/inferred on a NON-slender section.

    A local or local-global interactive failure on a Class 1-3 cross-section
    contradicts the classification (the section should be fully effective) and
    may indicate premature local collapse due to experimental anomalies.
    Flagged for audit rather than silently retained or dropped.
    """
    if pd.isna(section_class) or pd.isna(mode_eff):
        return False
    return section_class in (1, 2, 3) and mode_eff in ("local", "interactive")


def _flexural_scope(section_class, mode_eff, anomalous):
    """Whether a row belongs to the global flexural buckling training set.

    In scope:  global_flexural and yielding (Class 1-3); local and interactive
               on Class 4 sections, where the local reduction is carried by
               A_eff (KGW: P_y = A_eff * f_y).
    Excluded:  any torsional/flexural-torsional/distortional participation,
               'unknown' modes, undetermined class, and anomalous rows
               (local participation on Class 1-3) pending audit.
    """
    if pd.isna(section_class) or pd.isna(mode_eff):
        return False
    if mode_eff in _EXCLUDED_MODES or mode_eff == "unknown":
        return False
    if anomalous:
        return False
    return mode_eff in _SCOPE_MODES


def classify_sections(df):
    """Phase 1: EN 1993-1-4 classification and effective area.

    Expects gross geometry (A) and material columns to be present, i.e. run
    features.add_geometry first. Adds: epsilon, section_class,
    cs_slenderness_norm, lambda_0, A_eff, rho_eff.
    """
    out = df.copy()
    out["epsilon"] = epsilon(out["sigma_02"], out["E0"])

    cls = out.apply(lambda r: cross_section_class(r, r["epsilon"]),
                    axis=1, result_type="expand")
    out["section_class"] = cls[0].astype("Int64")
    out["cs_slenderness_norm"] = cls[1]

    out["lambda_0"] = out.apply(limiting_slenderness, axis=1)

    out["A_eff"] = out.apply(
        lambda r: effective_area(r, r["A"], r["epsilon"], r["section_class"]),
        axis=1)
    out["rho_eff"] = out["A_eff"] / out["A"]
    return out


def _effective_mode(reported, inferred):
    """Resolve the per-row failure mode used for all scope/audit decisions.

    GROUND-TRUTH RULE: the source-reported mode (`reported_failure_mode`,
    normalised) is authoritative wherever present. The Eurocode-based
    `inferred_failure_mode` is a fallback ONLY for rows whose reported mode is
    missing/blank — inference never overrides an explicit report.
    """
    return reported.where(reported.notna(), inferred)


def infer_failure_modes(df):
    """Phase 2: failure-mode inference, audit flag and training-scope filter.

    Expects lambda_bar (A_eff basis) to be present, i.e. run
    features.add_mechanics first. Adds: inferred_failure_mode,
    anomalous_interactive_mode, flexural_scope.

    `flexural_scope` (the training-set eligibility boolean) is decided from
    the effective mode returned by `_effective_mode`: the reported
    `reported_failure_mode` column is the ground truth, and the computed
    `inferred_failure_mode` is consulted only where the report is blank.
    (The column `failure_mode` is accepted as a legacy alias of
    `reported_failure_mode` in extracted inputs.)
    """
    out = df.copy()

    if "reported_failure_mode" in out.columns:
        raw = out["reported_failure_mode"]
    elif "failure_mode" in out.columns:                      # legacy alias
        raw = out["failure_mode"]
    else:
        raw = pd.Series(pd.NA, index=out.index)
    reported = raw.map(normalise_mode)

    out["inferred_failure_mode"] = [
        infer_mode(sc, lb, l0)
        for sc, lb, l0 in zip(out["section_class"], out["lambda_bar"], out["lambda_0"])
    ]

    mode_eff = _effective_mode(reported, out["inferred_failure_mode"])

    out["anomalous_interactive_mode"] = [
        _anomalous(sc, m) for sc, m in zip(out["section_class"], mode_eff)
    ]
    out["flexural_scope"] = [
        _flexural_scope(sc, m, an)
        for sc, m, an in zip(out["section_class"], mode_eff,
                             out["anomalous_interactive_mode"])
    ]
    return out
