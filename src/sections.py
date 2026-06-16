import numpy as np
SECTION_CALCS = {}      # dictionary of cross-section types
                        # every time a new section is added, a new function should be added to this dictionary

def register(section_type):
    def deco(fn):
        SECTION_CALCS[cross_section_type] = fn
        return fn
    return deco

@register("RHS")
def rhs(row):
    b, h, t = row["b"], row["h"], row["t"]
    A = b*h - (b-2*t)*(h-2*t)
    I_major = (b*h**3 - (b-2*t)*(h-2*t)**3) / 12
    I_minor = (h*b**3 - (h-2*t)*(b-2*t)**3) / 12
    return A, I_major, I_minor

@register("SHS")
def shs(row):
    return rhs(row)            # square = RHS with b = h

@register("CHS")
def chs(row):
    D, t = row["b"], row["t"]; d = D - 2*t          # D is written under b for CHS (see data schema)
    A = np.pi/4*(D**2 - d**2)
    I = np.pi/64*(D**4 - d**4)
    return A, I, I           # symmetric

@register("Angle")
def angle(row):
    b, h, t, r1, r2 = row["b"], row["h"], row["t"], row["r1"], row["r2"]
    
    # 1. Area (Exact formulation including root and toe radii)
    A_rect = (b + h - t) * t
    A_root = (1 - np.pi/4) * r1**2
    A_toe = 2 * (1 - np.pi/4) * r2**2
    A = A_rect + A_root - A_toe
    
    # 2. Centroid (Using rectangular approximation for inertia performance)
    # Leg 1: Vertical (h x t), Leg 2: Horizontal ((b-t) x t)
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
    
    I_major = I_avg + R
    I_minor = I_avg - R
    
    return A, I_major, I_minor

