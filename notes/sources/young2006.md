# Young & Lui 2006 : Tests of cold-formed high strength stainless steel compression members

## Metadata

* **Date read:** 18/06/2026

## 1. Summary: what was tested

This study investigated the compressive strength of cold-formed high-strength duplex stainless steel hollow section columns. The testing programme consisted of two Square Hollow Section (SHS) series and two Rectangular Hollow Section (RHS) series, tested across fixed-ended lengths ranging from 300 mm to 3000 mm. A total of 24 specimens were tested (6 stub columns and 18 long columns). The headline aim was to examine the strength of high-strength duplex steel columns and to evaluate whether the current design rules derived from normal-strength austenitic steel remain applicable to duplex grades with yield stresses up to 750 MPa.

## 2. Material properties

* **Experimental:** The researchers obtained material properties from both flat longitudinal tensile coupons (Table 5) and compressive stub columns (Table 6).
* **Reporting:** Full primary properties ($E_0$, $\sigma_{0.2}$, $n$) are provided for both test types.
* **Selection Constraint (Critical Issue):** Usually for cold-formed sections, the stub column properties are used to capture the enhanced yield strength from corner cold-working. However, the authors explicitly note that for test series SHS2, RHS1, and RHS2, the compressive 0.2% proof stresses were anomalously lower than the tensile properties because "local buckling occurred in the stub column tests". Therefore, using the stub column properties for these specific series would artificially penalise the intrinsic material strength. As a result, the compressive stub properties (Table 6) are used for Series SHS1 (where local buckling did not compromise the test) but revert to the flat tensile coupon properties (Table 5) for Series SHS2, RHS1, and RHS2.

## 3. Ramberg-Osgood exponent n (provenance flag)

n_source = measured


## 4. Batch structure and study_id groupings

The four batches:

* `young2006_A`: SHS 40x40x2 (Series SHS1)
* `young2006_B`: SHS 50x50x1.5 (Series SHS2)
* `young2006_C`: RHS 140x80x3 (Series RHS1)
* `young2006_D`: RHS 160x80x3 (Series RHS2)

## 5. Geometry and test setup

* **Geometry:** Measured raw dimensions (overall depth $D$, overall width $B$, and thickness $t$) are fully tabulated for all specimens in Tables 1 to 4. $B$ maps to $b$ and $D$ maps to $h$.
* **Boundary conditions:** Fixed-ended (fixed-fixed). End plates were bolted to rigid flat bearings that were mechanically locked to restrain minor/major axis rotations, twist, and warping.
* **Effective length ($L_e$):** The geometric length $L$ is provided. The researchers explicitly state the effective length $l_e$ was assumed to be $L/2$ due to the rigid restraint. $L_e$ is thus derived programmatically as $L \times 0.5$.
* **Buckling Axis:** Because RHS sections natively buckle about the weaker axis, and the authors state "minor axis flexural imperfections were recorded for all specimens", `buckling_axis` must be populated as `minor` for RHS series and `-` for the perfectly symmetric SHS profiles.

## 6. Initial geometric imperfections

* **Reporting:** The initial overall minor axis geometric imperfections at mid-length were measured using a theodolite and are reported as $\delta/L$ ratios for both the x-axis and y-axis in Table 7.
* **Mapping:**
* `w_0` maps to the maximum initial geometric bow. It should be calculated programmatically by taking the larger of the $\delta_x/L$ and $\delta_y/L$ ratios from Table 7 and multiplying by the actual column length $L$.
* `w_e` maps to 0.0. The test setup involved a minimal 2 kN seating load to establish full concentric contact before the end bearings were mechanically locked into place, intentionally preventing functional loading eccentricity.
* `w_total` perfectly matches `w_0`.



## 7. Failure modes and exclusions

* `n_specimens` (total in paper): 24.
* `n_included` (after filtering): 14
* **Exclusions and reasons:** You are explicitly keeping overall flexural (F) and interactive local-overall (LCF) modes, while excluding pure yielding (Y) and pure local buckling (L).
* **Excluded (10 specimens):** All 6 stub columns (Y or L), plus 4 long columns that failed strictly by pure local buckling (SHS2L650, SHS2L1000, RHS1L1400, RHS2L1400).
* **Included (14 specimens):** The 9 pure flexural failures (F) across SHS1 and SHS2, plus the 5 interactive buckling failures (LCF) across SHS2, RHS1, and RHS2.



## 9. Data extraction notes

* **Tables:** Dimensions (Tables 1-4). Tensile material properties (Table 5). Stub column material properties (Table 6). Imperfections (Table 7). Ultimate loads (Tables 8-11).
* **Units:** Modulus $E_0$ in GPa (requires multiplying by 1000 to MPa). Stresses in MPa. Loads in kN.
* **Section Type:** Recorded as `SHS` or `RHS` in the `section_type` column based on the series designation.

## 10. Judgement calls and flags

* **Inclusion of Interactive Buckling:** Per your instruction, 5 columns failing by local-overall interaction (LCF) are now kept. The `failure_mode` field will be directly populated as `global_flexural` for 'F' failures and `interactive` for 'LCF' failures, relying directly on the authors' explicit tags in Tables 8–11 rather than the inference script.
* **Material Selection Hybrid:** Due to the severe local buckling observed during the actual compressive stub column testing, Table 6 properties were strictly used for Series SHS1, but flat tensile properties from Table 5 had to be used for Series SHS2, RHS1, and RHS2 to prevent inputting an artificially low yield stress into the ML model.
* **Imperfections (`w_0`, `w_e`, `w_total`):** `w_0` computed using the maximum of the two orthogonal $\delta/L$ ratios from Table 7. `w_e` set to 0.0 due to the concentrically locked bearings.

## 11. General notes and useful for later

* **Slenderness Impact:** This paper vividly illustrates the danger of using highly slender cross-sections (large $b/t$ ratios) when working with ultra-high-strength materials. The duplex steel ($f_y \approx 750$ MPa) pushed the cross-sections deep into Class 4 territory, causing massive interaction with local buckling even at long column lengths (e.g., $L=1500$ mm). 