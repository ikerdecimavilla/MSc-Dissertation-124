import numpy as np
import pandas as pd

SECTION_CALCS = {}      # dictionary of cross-section types
                        # every time a new section is added, a new function should be added to this dictionary

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