# Young & Liu 2003 : Experimental Investigation of Cold-Formed Stainless Steel Columns

## Metadata

* **Date read:** 18/06/2026

## 1. Summary: what was tested

This experimental study investigated the compressive strength of fixed-ended cold-formed austenitic stainless steel (Type 304) Rectangular Hollow Section (RHS) columns. The programme covered 4 different cross-section geometries (nominal depth 120 mm, varying widths of 40/80 mm and thicknesses of 2–6 mm) tested over lengths ranging from 360 mm to 3600 mm. A total of 24 specimens were tested (including 8 stub columns and 16 long columns). The study aimed to provide fixed-ended buckling data and evaluate the reliability of the ASCE, Australian/New Zealand, and Eurocode 3 design rules.

## 2. Material properties

* **Experimental:** The authors conducted both longitudinal flat tensile coupon tests (Table 5) and compressive stub column tests (Table 6).
* **Reporting:** Full primary properties ($E_0$, $\sigma_{0.2}$, $n$) are explicitly tabulated for both. The secondary parameters ($\sigma_{0.5}$, $\sigma_u$) were only reported for the tensile coupons.
* **Selection Constraint:** compressive stub column properties (Table 6) are used for data extraction. These properties natively capture the substantial yield strength enhancement induced by the cold-forming process across the full cross-section.

## 3. Ramberg-Osgood exponent n (provenance flag)

n_source = measured

* **Reasoning:** The authors state that $n$ was obtained from the "measured 0.01% ($\sigma_{0.01}$) and 0.2% ($\sigma_{0.2}$) proof stresses using $n = \ln(0.01/0.2) / \ln(\sigma_{0.01}/\sigma_{0.2})$." Because this algebraic formula is applied directly to the stress points measured during their physical stub column tests (rather than a theoretical proxy), it is classed as a measured value.

## 4. Batch structure and study_id groupings

There are 4 distinct physical material batches, separated perfectly by the four cross-section series (R1, R2, R3, R4). Each series shares a unique set of averaged stub column material properties.

* `young2003_A`: RHS 120x40x2.0 (Series R1)
* `young2003_B`: RHS 120x40x5.3 (Series R2)
* `young2003_C`: RHS 120x80x2.8 (Series R3)
* `young2003_D`: RHS 120x80x6.0 (Series R4)

## 5. Geometry and test setup

* **Geometry:** Measured dimensions (overall depth $D$, width $B$, and thickness $t$) are fully tabulated for all specimens in Tables 1-4. For the dataset, $B$ maps to $b$ and $D$ maps to $h$.
* **Boundary conditions:** Fixed-ended (fixed-fixed). Specimens were bolted to rigid flat bearing plates, which were locked to prevent minor and major axis rotations, twisting, and warping.
* **Effective length ($L_e$):** The actual cut length ($L$) is reported. The authors explicitly assumed an effective length of one-half the column length due to the fully restrained setup. Therefore, $L_e$ will be derived programmatically as $L \times 0.5$.

## 6. Initial geometric imperfections

* **Reporting:** The initial overall minor axis geometric imperfections at mid-length were measured using a theodolite and reported as a $\delta/L$ ratio in Table 7.
* **Mapping:**
* `w_0` maps to the actual mid-length bow, calculated programmatically by multiplying the tabulated $\delta/L$ ratio by the actual specimen length $L$.
* `w_e` maps to 0.0. The researchers applied a minimal 2 kN seating load to establish full contact before rigidly locking the spherical bearing into a fixed position. They did not intentionally induce any functional loading eccentricity.
* `w_total` equals `w_0`.



## 7. Failure modes and exclusions

* `n_specimens` (total in paper): 24 (16 long columns + 8 stub columns).
* `n_included` (after filtering): 16
* **Exclusions and reasons:** The 8 stub columns (specimens with $L=360$, e.g., R1L0360, R1L0360R) were explicitly designed to comply with SSRC guidelines to determine purely local, cross-sectional yielding capacity.
* **Failure Mode Note:** The text broadly notes that the failure modes "involved local buckling, overall flexural buckling, and combined local and overall flexural buckling," but does not explicitly assign these labels to individual rows in the load tables. Therefore, `failure_mode` will be left blank (null) for the `inferred_failure_mode` script to categorise them using Eurocode 3 limits.

## 9. Data extraction notes

* **Tables:** Geometries (Tables 1-4). Compressive material properties (Table 6). Imperfections (Table 7). Ultimate test loads $P_{Exp}$ (Tables 8-11).
* **Units:** Initial modulus $E_0$ is in GPa (multiply by 1000 to get MPa). Stresses are in MPa. Loads are in kN. Lengths are in mm.
* **Section Type:** Recorded as `RHS` in the `section_type` column.
* **Buckling Axis:** Because these are rectangular tubes, flexural buckling naturally occurred about the weaker axis. The authors explicitly note "Minor axis flexural imperfections were recorded", confirming that `buckling_axis` must be populated as `minor`.

## 10. Judgement calls and flags

* **Material Selection:** Prioritised the compressive stub column parameters (Table 6) over the flat tensile coupons to appropriately reflect the full-section cold-worked compressive stiffness. Ultimate tensile strength ($\sigma_u$) is thus left null, as it was only tested in tension.
* **Failure Mode Handling:** Left `failure_mode` null since the authors did not provide specimen-specific labels; the classifier algorithm will identify `global_flexural` vs `interactive` behavior automatically.
* **Derived Lengths:** Derived $L_e$ programmatically as $L \times 0.5$ based on the explicit fixed-fixed bearing setup.
* **Imperfection Mapping (`w_0`, `w_e`, `w_total`):** Calculated `w_0` by extracting the $\delta/L$ ratio from Table 7 and multiplying by $L$. Assigned `w_e` = 0.0 as bearings were locked concentrically, meaning `w_total` equals `w_0`.
* **Buckling Axis:** Populated as `minor` based on the measured minor axis curvature and theoretical expectations for RHS sections.

## 11. General notes and useful for later

* **Post-Yield Behavior:** Similar to Liu & Young (2003), the authors observed that the stub columns and highly compact sections effectively reached the ultimate tensile strength of the material, significantly outperforming the 0.2% proof stress baseline that standard design codes rely on. This is excellent evidence for the necessity of properly modelling the non-linear hardening exponent $n$ to accurately predict capacity.
* **Design Code Conservatism:** Eurocode 3 and ASCE specifications were broadly conservative for the tested long columns, but the Australian/New Zealand rules were the most reliable.