# Behzadi 2021 : Fixed-ended equal-leg angle section compression members

## Metadata

- Date read (15/06/2026):

## 1. Summary: what was tested

Experimental and numerical study of fixed-ended equal-leg angle columns. Five physical tests conducted on hot-rolled austenitic stainless steel (Grade 1.4307), specifically 70x70x10 sections. FEA parametric study generated 1146 numerical results covering austenitic, duplex, and ferritic grades (hot-rolled and cold-formed) over a wide slenderness range.

## 2. Material properties

- **Experimental:** Derived from two tensile coupons cut from the legs of the 70x70x10 section.
  - R-O parameters are reported as averaged values per batch in Table 3.

- **FEA:** Used R-0 material properties from the literature of three stainless-steel families



## 3. Ramberg-Osgood exponent n (provenance flag)

n_source = measured

Authors directly derive n and secondary R-O strain hardening exponents from the stress-strain curves using optical extensometers and strain-gauges.

## 4. Batch structure and study_id groupings

There are 7 distinct batches --> 1 physical experiment batch and 6 FEA 'virtual' batches. The distinction between this is noted to prevent data leakage during CV.

`study_id` groupings:
- `behzadi2021_A`: Experimental, Angle 70x70x10, hot-rolled austenitic 1.4307
- `behzadi2021_B`: FEA, hot-rolled austenitic
- `behzadi2021_C`: FEA, cold-formed austenitic
- `behzadi2021_D`: FEA, hot-rolled ferritic
- `behzadi2021_E`: FEA, cold-formed ferritic
- `behzadi2021_F`: FEA, hot-rolled duplex
- `behzadi2021_G`: FEA, cold-formed duplex


## 5. Geometry and test setup

- **Geometry:** tabulated as raw dimensions (b,t,r1,r2,L) in Table 5
- **Boundary Conditions:** fixed-ended. Achieved by welding end plates to the specimens and clamping them to the testing machine base/top to prevent rotation about all axes.
- **Effective Length (Le)** Not directly tabulated. Must be derived using k=0.5 for fixed-fixed constraints Le=0.5*L

## 6. Initial geometric imperfections

- **Reporting:** Minor-axis bow (δv), major-axis bow (δu), and twist (θ) were all measured.
- **Format:** Reported in Table 4 as a ratio of member length (e.g., L/δv=−1427). This will require  conversion back to an absolute w0 value in mm during data entry.
- **FEA:** Assumed as a sinusoidal half-wave with amplitude L/1000 at midspan.

## 7. Failure modes and exclusions

Modes are explicitly distinguished between torsional-flexural (TF) and minor-axis flexural (F).

- `n_specimens` (total in paper): 5 experimental + 1,146 FEA = 1,151
- `n_included` (after filtering): 5 experimental + all FEA rows where Ncr,TF/Ncr,F,v > 1.0

**Exclusions and reasons:** Must exclude all FEA rows where Ncr,TF/Ncr,F,v ≤ 1.0 (torsional-flexural buckling), as they violate the pure global flexural buckling project constraint.

## 8. FEA details (delete if purely experimental)

- Validated against 127 total tests (5 present, 122 literature) with a mean Nu,FE​/Nu,Test ratio of 1.00 and a CoV of 0.08
- Elements: ABAQUS S4R shell elements
- Residual Stresses: Explicit bilinear 70 MPa distribution applied to hot-rolled members; inherently assumed in the stress-strain curve for cold-formed members.
  
## 9. Data extraction notes

- Geometries and ultimate loads are in Table 5
- Material properties in Table 3
- Experimental imperfections in Table 4
  
*Units:* 
- Modulus (E) and stresses in N/mm² (MPa)
- Loads in kN
- Dimensions in mm

No conversions needed other than calculating absolute w0 from the L/δv ratio.

## 10. Judgement calls and flags

- **Schema update:** Added `angle` to allowed `cross_section_type` in data dictionary
- **Filtering Judgement:** Used the N 
cr,TF/Ncr,F,v > 1.0 threshold to objectively filter the FEA dataset to pure global flexural buckling
- **Notation Mapping:** Mapped the paper's minor-axis bow imperfection δv to the master schema's global imperfection w0
- **Derived Le:** Must actively calculate Le=0.5⋅L based on the fixed-fixed physical test setup.
