# Gardner & Nethercot 2004 : Experiments on stainless steel hollow sections (Parts 1 & 2)

## Metadata

* **Date read:** 18/06/2026

## 1. Summary: what was tested

This study investigated the material, cross-sectional, and structural member behaviour of cold-formed austenitic stainless steel (Grade 1.4301) Square and Rectangular Hollow Sections (SHS and RHS). Part 1 detailed the derivation of material properties through 54 tensile, 56 compressive, and 5 corner coupon tests, alongside 37 stub columns to investigate cross-sectional capacity. Part 2 presented the global buckling results for 22 pin-ended long columns (lengths ranging from 1.0 m to 2.0 m) and 9 beams. The primary aim was to provide full load-deformation histories to validate numerical models and to develop a continuous, slenderness-based design approach that outperforms the conservative Eurocode 3: Part 1.4 rules.

## 2. Material properties

* **Experimental:** Part 1 explicitly tabulates the material properties derived from compressive flat (CF), tensile flat (TF), and tensile corner (TC) coupons (Table 1).
* **Reporting:** For the compressive flat coupons, the initial elastic modulus ($E_0$), 0.2% proof stress ($\sigma_{0.2}$), 1.0% proof stress ($\sigma_{1.0}$), and the Ramberg-Osgood exponent ($n$) are comprehensively reported. Ultimate tensile strength ($\sigma_u$) is naturally null for the compressive tests because necking does not occur in compression.
* **Selection Constraint:** The compressive flat (CF) properties from Part 1, Table 1 are extracted. The authors themselves highlighted that compressive properties for stainless steel tend to be more rounded, with 0.2% proof stresses averaging 5% lower than their tensile equivalents.

## 3. Ramberg-Osgood exponent n (provenance flag)

n_source = measured

## 4. Batch structure and study_id groupings

There are exactly 15 distinct physical material batches for the long columns, logically separated by the 15 distinct cross-section dimensions. Part 1 proves that each unique tube geometry possessed its own specific set of averaged compressive flat (CF) coupon material properties.

* `gardner2004_A`: SHS 80x80x4
* `gardner2004_B`: SHS 100x100x2
* `gardner2004_C`: SHS 100x100x3 (and so on...)

## 5. Geometry and test setup

* **Geometry:** Measured column dimensions (depth $D$, breadth $B$, and thickness $t$) are fully tabulated in Part 2, Table 2. For the dataset, $B$ maps to $b$ and $D$ maps to $h$.
* **Boundary conditions:** Pin-ended (pin-pin). The ends of the columns were milled flat and bore against ground plates that were fixed to hardened steel knife edges, permitting free end rotation but no end translation.
* **Effective length ($L_e$):** The geometric lengths ($L$) are explicitly reported. Because the specimens were tested concentrically between knife edges, the effective buckling length $L_e$ directly equals the physical length $L$.
* **Buckling Axis:** Part 2, Table 2 explicitly denotes the buckling axis for each RHS column as either Major or Minor. For the completely symmetric SHS profiles, this will be recorded as `-`.

## 6. Initial geometric imperfections

* **Reporting:** The initial global geometric imperfections were physically measured using feeler gauges and a straight edge. They are tabulated in Part 2, Table 2 as $v_0$ (imperfection in the buckling direction) and $v_1$ (imperfection at 90 degrees) in mm.
* **Mapping:**
* `w_0` maps perfectly to $v_0$, the absolute measured bow in the buckling direction.
* `w_e` maps to 0.0. The authors explicitly stated that the specimens were aligned such that the geometric centrelines of the column ends acted directly on the centreline of the knife edges, intentionally preventing any functional applied eccentricity.
* `w_total` equals `w_0`.



## 7. Failure modes and exclusions

* `n_specimens` (total in paper): 68 (37 stub columns + 22 long columns + 9 beams).
* `n_included` (after filtering): 22
* **Exclusions and reasons:** Following the scope bounds, all 37 stub columns (pure local buckling) and all 9 three-point bending beams must be strictly excluded. Only the 22 pin-ended axially loaded long columns will be transferred to the master dataset.
* **Failure Mode Note:** The authors note that the "predominant mode of failure of the columns was overall flexural buckling, though there was clear evidence of interaction between local and global effects". Because they do not individually label the exact failure mode against each row in the load tables, the `failure_mode` field will be left blank for the `inferred_failure_mode` algorithm to automatically classify the specimens according to cross-section slenderness limits.

## 9. Data extraction notes

* **Tables:** Material properties (Part 1, Table 1). Column geometries and imperfections (Part 2, Table 2). Ultimate test loads $F_u$ (Part 2, Table 3).
* **Units:** Stresses ($E_0$, $\sigma_{0.2}$, $\sigma_{1.0}$) are reported in N/mm², which converts 1:1 to MPa. Dimensions and imperfections are in mm. Ultimate loads are in kN.
* **Section Type:** Recorded as `SHS` or `RHS` in the `section_type` column based on the specimen tags.

## 10. Judgement calls and flags

* **Cross-Referencing Sources:** The most crucial judgement call was bridging the gap between the two papers. Extracting $n$, $E_0$, $\sigma_{0.2}$, and $\sigma_{1.0}$ exclusively from the compressive flat (CF) rows in Part 1 (Table 1) and applying them to the corresponding column rows in Part 2 (Tables 2 & 3). Ultimate tensile strength ($\sigma_u$) is naturally left null as it does not exist for compression tests.
* **Failure Mode Handling:** Left `failure_mode` null since the authors broadly reported mixed failure modes but did not attribute them to specific specimens; the classifier will handle this automatically.
* **Imperfection Mapping (`w_0`, `w_e`, `w_total`):** Mapped `w_0` directly to $v_0$ (the geometric bow in the buckling direction). Assigned `w_e` = 0.0 as the columns were concentrically aligned on the knife edges, making `w_total` equal to `w_0`.

## 11. General notes and useful for later

* **Code Conservatism & Strain Hardening:** A major finding of the study was that for stocky (Class 1) and intermediate cross-sections, Eurocode 3 Part 1.4 substantially under-predicted capacities (by up to 30%) because its bi-linear assumption entirely ignores the profound post-yield strain-hardening capacity of stainless steel. This observation provides excellent physical justification for why the non-linear hardening parameter ($n$) in your Stage 1 Machine Learning model is vital to accurate strength prediction.
* **Corner Strength Enhancements:** Part 1 found that the 0.2% proof strength of the cold-worked corner material was typically around 50% higher than the equivalent flat material. This highlights how cold-forming permanently enhances the yield strength, which is why compressive stub/flat properties are the most representative baseline for the whole composite tube.