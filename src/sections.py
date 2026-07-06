import numpy as np
import pandas as pd

SECTION_CALCS = {}      # dictionary of cross-section types
                        # every time a new section is added, a new function should be added to this dictionary

# forming_route -> outstand limit family (only affects open sections, i.e. I).
# hot_rolled / hot_finished are non-welded and have no dedicated EN row; they are
# mapped to the (more generous) cold-formed limits. Documented assumption.
# Both 'laser_welded' and the generic 'welded' select the welded limit set.
# Lives here (not classify.py) because the effective-width reduction factors of
# EN 1993-1-4 5.2.3 also branch on the same welded/cold basis.
WELD_BASIS = {
    "cold_formed":  "cold",
    "press_braked": "cold",
    "hot_rolled":   "cold",
    "hot_finished": "cold",
    "laser_welded": "welded",
    "welded":       "welded",
}

def register(section_type):
    def deco(fn):
        SECTION_CALCS[section_type] = fn
        return fn
    return deco

@register("RHS")
def rhs(row):
    """Rectangular hollow section (sharp corners).

    I_major / I_minor are assigned BY MAGNITUDE, not by a fixed geometric axis.
    The previous version always labelled (b*h^3)/12 as 'major', which is only
    correct when h >= b; for wide RHS (b > h) it silently swapped the labels and
    corrupted axis selection downstream (e.g. theofanous2009 RHS).
    """
    b, h, t = row["b"], row["h"], row["t"]
    A = b*h - (b-2*t)*(h-2*t)
    I_bh = (b*h**3 - (b-2*t)*(h-2*t)**3) / 12     # bending about axis with depth h
    I_hb = (h*b**3 - (h-2*t)*(b-2*t)**3) / 12     # bending about axis with depth b
    return A, max(I_bh, I_hb), min(I_bh, I_hb)

@register("SHS")
def shs(row):
    return rhs(row)            # square = RHS with b = h

@register("CHS")
def chs(row):
    D, t = row["b"], row["t"]; d = D - 2*t          # D is written under b for CHS (see data schema)
    A = np.pi/4*(D**2 - d**2)
    I = np.pi/64*(D**4 - d**4)
    return A, I, I           # symmetric

@register("I")
def i_section(row):
    """Doubly-symmetric I / H section.

    Sharp corners (root radii neglected -> conservative for classification).
    Uses separate flange/web thicknesses t_f, t_w when the columns are present,
    otherwise falls back to the single 't' (e.g. equal-thickness welded I).

    I_major / I_minor are assigned by magnitude (max/min) for the same robustness
    reason as rhs(): a standard I has h > b so the strong axis is (b*h^3)/12, but
    the max/min guard removes any reliance on that holding for every future row.
    """
    b, h, t = row["b"], row["h"], row["t"]
    t_f = row.get("t_f", t); t_w = row.get("t_w", t)
    if pd.isna(t_f): t_f = t
    if pd.isna(t_w): t_w = t

    A = 2*b*t_f + (h - 2*t_f)*t_w
    I_strong = (b*h**3 - (b - t_w)*(h - 2*t_f)**3) / 12     # about axis with depth h (y-y)
    I_weak   = (2*t_f*b**3 + (h - 2*t_f)*t_w**3) / 12       # about axis with depth b (z-z)
    return A, max(I_strong, I_weak), min(I_strong, I_weak)

@register("H")
def h_section(row):
    return i_section(row)      # 'H' label -> same doubly-symmetric formulae

@register("Angle")
def angle(row):
    b, h, t, r1, r2 = row["b"], row["h"], row["t"], row["r1"], row["r2"]

    # 1. Area (Exact formulation including root and toe radii)
    A_rect = (b + h - t) * t
    A_root = (1 - np.pi/4) * r1**2
    A_toe = 2 * (1 - np.pi/4) * r2**2
    A = A_rect + A_root - A_toe

    # 2. Centroid (Using rectangular approximation for inertia performance)
    A1, y1, z1 = h * t, t / 2, h / 2
    A2, y2, z2 = (b - t) * t, t + (b - t) / 2, t / 2
    A_simp = A1 + A2
    yc = (A1 * y1 + A2 * y2) / A_simp
    zc = (A1 * z1 + A2 * z2) / A_simp

    # 3. Second Moments of Area (Iy, Iz) via Parallel Axis Theorem
    Iy1 = (t * h**3) / 12 + A1 * (z1 - zc)**2
    Iy2 = ((b - t) * t**3) / 12 + A2 * (z2 - zc)**2
    Iy = Iy1 + Iy2
    Iz1 = (h * t**3) / 12 + A1 * (y1 - yc)**2
    Iz2 = (t * (b - t)**3) / 12 + A2 * (y2 - yc)**2
    Iz = Iz1 + Iz2

    # 4. Product of Inertia (Iyz)
    Iyz = A1 * (y1 - yc) * (z1 - zc) + A2 * (y2 - yc) * (z2 - zc)

    # 5. Principal Axes (I_major, I_minor) via Mohr's Circle rotation
    I_avg = (Iy + Iz) / 2
    R = np.sqrt(((Iy - Iz) / 2)**2 + Iyz**2)
    return A, I_avg + R, I_avg - R


# ---------------------------------------------------------------------------
# Effective area of Class 4 cross-sections
#
# Flat-element sections (RHS/SHS/I/H): EN 1993-1-4:2006 clause 5.2.3, which
# adopts the effective-width method of EN 1993-1-5 4.4 with stainless-specific
# reduction factors rho (Eqs. 5.1-5.3). Uniform compression (psi = 1) is
# assumed throughout, consistent with concentrically loaded column tests:
#   k_sigma = 4.0 (internal elements), 0.43 (outstand elements)
#   lambda_p = (b_bar/t) / (28.4 * eps * sqrt(k_sigma))
#
# CHS: EN 1993-1-4 gives no effective-width rule (Table 5.2 refers d/t > 90
# eps^2 to EN 1993-1-6), so the meridional shell-buckling stress-design method
# of EN 1993-1-6:2007 (8.5.2 + Annex D.1.2) is used and expressed as an
# effective area A_eff = chi_x * A.
# ---------------------------------------------------------------------------

EFFECTIVE_AREA_CALCS = {}     # section_type -> effective-area function

# EN 1993-1-6 fabrication quality class B (Q = 25): documented assumption for
# cold-formed structural CHS.
_CHS_QUALITY_Q = 25.0


def register_eff(section_type):
    def deco(fn):
        EFFECTIVE_AREA_CALCS[section_type] = fn
        return fn
    return deco


def _lambda_p(b_bar, t, eps, k_sigma):
    """Plate slenderness, EN 1993-1-5 4.4(2) as adopted by EN 1993-1-4 5.2.3."""
    return (b_bar / t) / (28.4 * eps * np.sqrt(k_sigma))


def _rho_flat(lam_p, family):
    """Stainless steel reduction factor rho, EN 1993-1-4:2006 Eqs. 5.1-5.3.

    family: 'internal' (cold formed or welded), 'outstand_cold', 'outstand_welded'.
    Capped at 1.0 (fully effective plate).
    """
    if lam_p <= 0:
        return 1.0
    if family == "internal":
        rho = 0.772 / lam_p - 0.125 / lam_p**2          # Eq. 5.1
    elif family == "outstand_cold":
        rho = 1.0 / lam_p - 0.231 / lam_p**2            # Eq. 5.2
    elif family == "outstand_welded":
        rho = 1.0 / lam_p - 0.242 / lam_p**2            # Eq. 5.3
    else:
        raise ValueError(f"unknown plate family {family!r}")
    return min(rho, 1.0)


@register_eff("RHS")
def rhs_eff(row, A, eps):
    """A_eff of an RHS/SHS: both wall pairs are internal elements in uniform
    compression; flat widths taken as (h-2t) and (b-2t), consistent with the
    conservative 'c' used in classification (EN 1993-1-4 5.2.3 NOTE)."""
    b, h, t = row["b"], row["h"], row["t"]
    A_eff = A
    for width in (h - 2*t, b - 2*t):
        rho = _rho_flat(_lambda_p(width, t, eps, 4.0), "internal")
        A_eff -= 2.0 * (1.0 - rho) * width * t          # two walls per direction
    return A_eff


@register_eff("SHS")
def shs_eff(row, A, eps):
    return rhs_eff(row, A, eps)


@register_eff("I")
def i_eff(row, A, eps):
    """A_eff of a doubly-symmetric I/H: internal web + four outstand half-flanges.
    The outstand rho branches on the welded/cold basis via WELD_BASIS, matching
    the limit set used in classification."""
    b, h, t = row["b"], row["h"], row["t"]
    t_f = row.get("t_f", t); t_w = row.get("t_w", t)
    if pd.isna(t_f): t_f = t
    if pd.isna(t_w): t_w = t
    basis = WELD_BASIS.get(row.get("forming_route"), "cold")

    web = h - 2*t_f
    rho_w = _rho_flat(_lambda_p(web, t_w, eps, 4.0), "internal")

    outstand = (b - t_w) / 2.0
    rho_f = _rho_flat(_lambda_p(outstand, t_f, eps, 0.43),
                      "outstand_welded" if basis == "welded" else "outstand_cold")

    return A - (1.0 - rho_w) * web * t_w - 4.0 * (1.0 - rho_f) * outstand * t_f


@register_eff("H")
def h_eff(row, A, eps):
    return i_eff(row, A, eps)


@register_eff("CHS")
def chs_eff(row, A, eps):
    """A_eff of a Class 4 CHS via EN 1993-1-6:2007 meridional buckling.

    Stress design (8.5.2) with Annex D.1.2 parameters, expressed as
    A_eff = chi_x * A:
      sigma_x,Rcr = 0.605 * C_x * E * t / r      (r = mid-surface radius)
      lambda_x    = sqrt(f_y / sigma_x,Rcr)
      alpha_x     = 0.62 / (1 + 1.91 * (dw_k/t)^1.44),  dw_k = (t/Q) sqrt(r/t)
      chi_x       = 1                                     lambda_x <= 0.20
                    1 - 0.60 (lambda_x-0.20)/(lambda_p-0.20)   plastic range
                    alpha_x / lambda_x^2                  lambda_x >= lambda_p
      lambda_p    = sqrt(alpha_x / 0.40)

    C_x is taken as 1.0 (medium-length cylinder). The Annex D long-cylinder
    reduction of C_x embeds global column interaction of the tube, which this
    pipeline models separately through the flexural buckling formulation;
    applying it here would double-count length effects. Fabrication quality
    class B (Q = 25) is assumed for cold-formed structural CHS.
    """
    D, t = row["b"], row["t"]                     # D stored under 'b' (schema)
    E0, fy = row["E0"], row["sigma_02"]
    r = (D - t) / 2.0

    sigma_cr = 0.605 * E0 * t / r                 # C_x = 1.0, see docstring
    lam_x = np.sqrt(fy / sigma_cr)

    dwk_over_t = (1.0 / _CHS_QUALITY_Q) * np.sqrt(r / t)
    alpha = 0.62 / (1.0 + 1.91 * dwk_over_t**1.44)

    lam_0, beta, eta = 0.20, 0.60, 1.0
    lam_p = np.sqrt(alpha / (1.0 - beta))
    if lam_x <= lam_0:
        chi = 1.0
    elif lam_x < lam_p:
        chi = 1.0 - beta * ((lam_x - lam_0) / (lam_p - lam_0))**eta
    else:
        chi = alpha / lam_x**2
    return chi * A


def effective_area(row, A, eps, section_class):
    """Effective cross-sectional area A_eff.

    Class 1-3 sections are fully effective (A_eff = A). Class 4 sections are
    reduced by the registered per-type calculator. Returns NaN when the class
    is undetermined or the section type has no calculator (e.g. Angle), so an
    area is never invented.
    """
    if pd.isna(section_class) or pd.isna(A):
        return np.nan
    if section_class != 4:
        return float(A)
    fn = EFFECTIVE_AREA_CALCS.get(row.get("section_type"))
    if fn is None:
        return np.nan
    return float(fn(row, A, eps))