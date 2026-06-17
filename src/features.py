import numpy as np
from .sections import SECTION_CALCS

def add_features(df):
    out = df.copy()
    
    # 1. Base Geometry
    geom = out.apply(_section_props, axis=1, result_type="expand")
    out[["A", "I_major", "I_minor"]] = geom

    # 2. Critical Inertia
    I_crit = np.where(out["buckling_axis"] == "major",
                      out["I_major"], out["I_minor"])
                      
    # 3. Radius of Gyration (Capital R)
    out["R"] = np.sqrt(I_crit / out["A"])
    
    # 4. Standard Slenderness (lambda)
    out["lambda"] = out["Le"] / out["R"]
    
    # 5. Euler Elastic Buckling Load
    out["N_cr"] = np.pi**2 * out["E"] * I_crit / out["Le"]**2
    
    # 6. Yield Load (using 0.2% proof stress)
    out["N_y"] = out["A"] * out["sigma_02"]
    
    # 7. Non-dimensional Slenderness
    out["lambda_bar"] = np.sqrt(out["N_y"] / out["N_cr"])
    
    # 8. Strength Reduction Factor
    out["chi"] = out["N_u"] / out["N_y"]
    
    # 9. Material factor (for comparison with Eurocode)
    out["epsilon"] = np.sqrt((235 / out["sigma_02"]) * (out["E0"] / 210000)) #Table 5.2 EN 1993-1-4
    
    return out

def _section_props(row):
    fn = SECTION_CALCS.get(row["section_type"])
    if fn is None:
        raise ValueError(
            f"No section calc for {row['section_type']!r} "
            f"(ref_key={row.get('ref_key')})")
    return fn(row)