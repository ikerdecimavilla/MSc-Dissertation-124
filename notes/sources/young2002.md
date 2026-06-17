# Young & Hartono 2002 : Compression Tests of Stainless Steel Tubular Members

## Metadata

* **Date read:** 17/06/2026

## 1. Summary: what was tested

This experimental study investigated the compressive strength of cold-formed austenitic stainless steel (Type 304) Circular Hollow Section (CHS) columns. The testing programme comprised 16 fixed-ended specimens across 3 different cross-section geometries ($D/t$ ratios ranging from 32.0 to 74.7) with lengths ranging from 550 mm to 3000 mm. The primary aim was to provide rare experimental data on fixed-ended stainless steel columns and evaluate the reliability of current design specifications (ASCE, AS/NZS, Eurocode) alongside alternative rules proposed by Rasmussen & Hancock and Rasmussen & Rondal.

## 2. Material properties

* **Experimental:** The authors conducted both longitudinal flat tensile coupon tests (Table 4) and full-section compressive stub column tests (Table 5).
* **Reporting:** The primary properties ($E_0$, $\sigma_{0.2}$, and $n$) are explicitly tabulated for both types of tests. The secondary two-stage Ramberg-Osgood parameters ($\sigma_{1.0}$, $n^\prime$) were not reported.
* **Selection Constraint:** Consistent with our methodology for cold-formed tubular sections, the compressive stub column properties (Table 5) must be used for data extraction. They accurately capture the composite compressive stiffness and cold-worked state of the cross-sections. The authors themselves highlight that the tensile 0.2% proof stresses were consistently higher than the compressive stub column values, reinforcing the need to use the compressive baseline for column buckling.

## 3. Ramberg-Osgood exponent n (provenance flag)

n_source = measured

* **Reasoning:** The authors state they determined $n$ directly from their measured physical stress-strain curves using the standard two-point formula: $n = \ln(0.01/0.2) / \ln(\sigma_{0.01}/\sigma_{0.2})$. While this is an algebraic formula, it is applied directly to their own physically measured 0.01% and 0.2% proof stresses from the stub columns, not derived via a generic proxy.

## 4. Batch structure and study_id groupings

There are 3 distinct physical material batches, cleanly separated by the three cross-section series (C1, C2, C3). Each series shares its own unique set of stub column material properties.

* `young2002_A`: CHS 89.0x2.78 (Series C1)
* `young2002_B`: CHS 168.7x3.34 (Series C2)
* `young2002_C`: CHS 322.8x4.32 (Series C3)

## 5. Geometry and test setup

* **Geometry:** Measured dimensions (outer diameter $D$ and thickness $t$) are fully tabulated for all specimens in Tables 1, 2, and 3. In the dataset, $D$ maps to $b$, and $h$ will be left null.
* **Boundary conditions:** Fixed-ended (fixed-fixed). The specimens were welded to thick end plates and bolted to flat bearing plates that were rigidly restrained against major/minor axis rotations, twist, and warping.
* **Effective length ($L_e$):** The authors report the actual specimen length ($L$). They explicitly state that the effective length was taken as one-half of the column length. Therefore, $L_e$ must be derived as $L_e = 0.5L$.

## 6. Initial geometric imperfections

* **Reporting:** The authors measured the initial overall geometric imperfection at mid-length ($\delta$) and tabulated it as a $\delta/L$ ratio in Table 6. This maps perfectly to the dataset's $w_0$ (calculated as the ratio multiplied by $L$).
* **Loading Eccentricity:** The researchers aimed for full contact, locking the spherical bearings into a fixed state before loading. They did not actively apply any intentional loading eccentricity. Therefore, $w_e$ is 0.0, and $w_{total}$ equals $w_0$.

## 7. Failure modes and exclusions

* `n_specimens` (total in paper): 16 (12 long columns + 4 stub columns).
* `n_included` (after filtering): 12
* **Exclusions and reasons:** The authors explicitly note that 4 specimens (C1L0550, C2L0550, C2L0550R, and C3L1000) were tested strictly to comply with the SSRC guidelines for stub columns. The remaining 12 long columns are safely included.
* **Failure Mode Note:** The authors note that failures involved "overall flexural buckling, and combined local and overall flexural buckling," but they do not explicitly tabulate which of the 12 long columns failed interactively versus purely flexurally. This will require the Eurocode-based `inferred_failure_mode` script to reliably assign `global_flexural` or `interactive` to the rows based on their cross-section class.

## 9. Data extraction notes

* **Tables:** Dimensions (Tables 1-3). Compressive material properties (Table 5). Imperfections (Table 6). Ultimate loads $P_{Exp}$ (Tables 7-9).
* **Units:** Modulus $E_0$ is in GPa (requires multiplying by 1000 to MPa). Stresses are in MPa. Loads are in kN. Lengths are in mm.
* **Buckling Axis:** Because all specimens are Circular Hollow Sections (CHS), moments of inertia are identical about all lateral axes. Therefore, `buckling_axis` must be populated as `-`.

## 10. Judgement calls and flags

* **Material Selection:** Prioritised the compressive stub column parameters (Table 5) over the tensile coupons to accurately capture the composite compressive stiffness of the tubes.
* **Failure Mode Handling:** Because the authors did not tag individual long columns with their exact failure mode in the tables, the `failure_mode` column should be left null or flagged for the `inferred_failure_mode` algorithm to classify them based on EN 1993-1-4 Class 3 limits.
* **buckling_axis convention:** Assigned as `-` due to the symmetric nature of CHS profiles.
* **Derived Lengths:** Derived $L_e$ mathematically as $L \times 0.5$ based on the authors' explicit fixed-fixed boundary condition assumptions.

## 11. General notes and useful for later

* **Code Performance:** The authors found that current specifications (ASCE, AS/NZS, Eurocode) were generally unconservative for predicting fixed-ended column strengths. In contrast, the design rules proposed by Rasmussen & Rondal (1997)—which use the Perry curve but specify the imperfection parameter explicitly in terms of the Ramberg-Osgood $n$ value—were conservative and far more reliable. This perfectly underscores the entire premise of your dissertation: properly integrating the non-linear $n$ parameter into the flexural buckling calculation significantly outperforms standard calibrated code curves.