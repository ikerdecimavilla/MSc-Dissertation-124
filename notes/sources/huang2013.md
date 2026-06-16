# Huang & Young 2013 : Tests of pin-ended cold-formed lean duplex stainless steel columns

## Metadata

* **Date read:** 16/06/2026

## 1. Summary: what was tested

This experimental study investigated the flexural buckling behaviour of cold-formed lean duplex stainless steel (grade EN 1.4162) columns. The programme tested a total of 38 specimens, comprising 6 compressive stub columns and 32 pin-ended long columns across 6 cross-section geometries (2 Square Hollow Sections and 4 Rectangular Hollow Sections). Specimen lengths ranged from 200 mm to 1550 mm. The primary aim was to assess whether current American, Australian/New Zealand, and European design specifications are applicable to this relatively new lean duplex grade, as it was not yet covered by the codes.

## 2. Material properties

* **Experimental:** The authors performed both flat tensile coupon tests and full-section compressive stub column tests.
* **Reporting:** The primary properties ($E_0$, $\sigma_{0.2}$, $\sigma_u$, $n$) are explicitly tabulated for both the tensile coupons (Table 7) and stub columns (Table 8). The secondary two-stage Ramberg-Osgood parameters ($\sigma_{1.0}$, $n^\prime$) were not reported.
* **Selection Constraint:** Crucially, several of the stub columns (SC2L150, SC5L300, SC6L450) suffered from premature local buckling before yielding. Therefore,  the tensile coupon properties (Table 7) are used.

## 3. Ramberg-Osgood exponent n (provenance flag)

n_source = measured

* **Reasoning:** The authors state they derived $n$ directly from their measured physical stress-strain curves using the standard formula $n = \ln(0.01/0.2) / \ln(\sigma_{0.01}/\sigma_{0.2})$ based on their own measured 0.01% and 0.2% proof stresses.

## 4. Batch structure and study_id groupings

There are 6 distinct physical material batches, separated cleanly by cross-section type and their corresponding unique tensile coupon test. These map directly to the authors' series C1 through C6.

* `huang2013_A`: RHS 50x30x2.5 (corresponds to series C1)
* `huang2013_B`: SHS 50x50x1.5 (corresponds to series C2)
* `huang2013_C`: SHS 50x50x2.5 (corresponds to series C3)
* `huang2013_D`: RHS 70x50x2.5 (corresponds to series C4)
* `huang2013_E`: RHS 100x50x2.5 (corresponds to series C5)
* `huang2013_F`: RHS 150x50x2.5 (corresponds to series C6)

## 5. Geometry and test setup

* **Geometry:** Measured dimensions (depth $D$, width $B$, thickness $t$) are fully tabulated in Tables 1-6. $D$ maps to $h$, and $B$ maps to $b$.
* **Boundary conditions:** Pin-ended (pin-pin). The columns were supported by knife-edges seated in V-shaped pits.
* **Effective length ($L_e$):** The authors report both the cut specimen length ($L$) and the effective buckling length ($L_e$). The effective length explicitly adds 110 mm to account for the combined 40 mm thickness of the end plates and the 70 mm height of the wedge plates. $L_e$ is extracted directly from the authors' tables.

## 6. Initial geometric imperfections

* **Reporting:** The maximum natural global bow at mid-length ($\delta$) is reported as a $\delta/L$ ratio in Table 9.
* **Crucial Setup Note:** The researchers aimed to test the columns concentrically (zero eccentricity). However, a small functional setup eccentricity remained. They explicitly tracked and reported the total combined imperfection $(e + \delta)$ for every specimen in Tables 10-15.
* **Mapping:** The natural bow ($\delta$) maps to $w_0$. The explicitly reported combined $(e + \delta)$ metric maps directly to $w_{total}$. The applied setup eccentricity ($w_e$) is mathematically reversed as $w_{total} - w_0$. Because the setup eccentricity often inadvertently counteracted the natural bow, $w_e$ is occasionally a negative value.

## 7. Failure modes and exclusions

* `n_specimens` (total in paper): 38 (32 long columns + 6 stub columns).
* `n_included` (after filtering): 21
* **Exclusions and reasons:** 17 specimens were excluded. This includes all 6 stub columns (strictly local/material tests), 8 long columns that failed strictly by pure local buckling (L), and 3 highly short long columns that failed by simple material yielding/squashing (Y). The 21 included specimens comprise 16 that failed by pure global flexural buckling (F) and 5 that failed by interactive modes (L+F), which have been logged accordingly.

## 9. Data extraction notes

* **Tables:** Dimensions (Tables 1-6). Material properties (Table 7). Imperfections (Table 9). Ultimate loads, combined imperfections, and effective lengths (Tables 10-15).
* **Units:** $E_0$ is reported in GPa (needs multiplying by 1000). Stresses are in MPa. Loads ($N_u$) are in kN. Lengths are in mm.

## 10. Judgement calls and flags

* **Material Selection:** Extracted properties exclusively from the flat tensile coupons (Table 7) rather than compressive stub columns
* **Failure Mode Filtering:** Included global_flexural and interactive failures, but strictly excluded local and yielding failures to maintain ML training integrity.
* **Buckling Axis:** All specimens were constrained to buckle about the minor axis, so `buckling_axis` is populated as `minor`.
* **Stage 2 Imperfection Flag:** Extracted the natural bow ($\delta$) as $w_0$ (by multiplying the reported $\delta/L$ ratio by $L$). Mapped the authors' actively tracked combined imperfection metric $(e + \delta)$ directly to $w_{total}$. Calculated $w_e$ programmatically as $w_{total} - w_0$, intentionally retaining negative values where the rig configuration opposed the geometric bow.

## 11. General notes and useful for later

* **Code Performance:** The authors concluded that using the full cross-sectional area alongside stub column properties provides a more accurate and less scattered prediction of column capacity than current design codes (ASCE, AS/NZS, EC3).
* **Interactive Modes Context:** The interactive buckling (L+F) modes predominantly occurred in the wider RHS specimens (Series C5 and C6) where the plate slenderness $b/t$ was highest. .