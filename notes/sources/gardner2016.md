# Gardner et al. 2016 : Laser-welded stainless steel I-sections: Residual stress measurements and column buckling tests

## Metadata

* **Date read:** 18/06/2026

## 1. Summary: what was tested

This study investigated the structural response of newly introduced laser-welded austenitic stainless steel I-section members. The testing programme comprised 9 stub column tests and 22 long column flexural buckling tests (14 buckling about the minor axis and 8 about the major axis). The primary aim was to address the lack of test data for laser-welded profiles, measure their unique residual stress patterns, and evaluate whether current Eurocode 3 column buckling curves are appropriate for this high-precision fabrication method.

## 2. Material properties

* **Experimental:** The researchers conducted longitudinal tensile coupon tests in accordance with EN ISO 6892-1.
* **Reporting:** Full material properties ($E$, $f_y$, $f_{1.0}$, $f_u$, and Ramberg-Osgood parameters) are tabulated in Table 3. For sections with uniform plate thicknesses, a single coupon was tested, whereas sections with dissimilar thicknesses had coupons extracted from both the flange (F) and the web (W).
* **Selection Constraint:** As established for welded sections, the tensile flat properties provide the correct baseline, since fabrication impacts are driven by thermal residual stresses rather than mechanical cold-working enhancements.

## 3. Ramberg-Osgood exponent n (provenance flag)

n_source = measured

* **Reasoning:** The Ramberg-Osgood coefficients ($n$, $n_{0.2,1.0}$, and $n_{0.2,u}$) were physically measured and directly derived from the tensile coupon stress-strain curves.

## 4. Batch structure and study_id groupings

The specimens were fabricated across 9 distinct cross-section geometries. Each unique geometry maps directly to a specific material batch (and corresponding tensile coupon properties) in Table 3. Therefore, the `study_id` will be grouped by these geometries to prevent data leakage (e.g., `gardner2016_A` for I-50x50x4x4, `gardner2016_B` for I-102x68x5x5, etc.).

## 5. Geometry and test setup

* **Geometry:** Measured column dimensions ($h$, $b$, $t_w$, $t_f$) and lengths ($L$) are reported in Table 8 for minor axis tests and Table 10 for major axis tests. For the dataset, $b$ maps to $b$, $h$ maps to $h$, and the distinct thicknesses map to $t_f$ and $t_w$.
* **Boundary conditions:** Pin-ended (pin-pin). Knife edges were employed to achieve pinned end conditions for the target buckling axis, with lateral restraints provided during major axis tests to prevent minor axis deflection.
* **Effective length ($L_e$):** The tabulated length $L$ explicitly represents the "buckling length of the columns between the knife edges" (i.e., the physical column length plus the thickness of the two knife edges). Thus, $L_e$ equals $L$ directly.
* **Buckling Axis:** Explicitly recorded as `minor` for the 14 tests in Table 8 and `major` for the 8 tests in Table 10.

## 6. Initial geometric imperfections

* **Reporting:** The initial global geometric imperfection ($v_0$) was measured using a self-levelling laser. Additionally, an intentional load eccentricity ($e_0$) was applied by the researchers to achieve a target total eccentricity of approximately $L/1000$. The actual total applied eccentricity ($v_0 + e_0$) was calculated from strain gauge readings during the tests.
* **Mapping:**
* `w_0` maps perfectly to the measured global bow $v_0$.
* `w_total` maps to the total combined eccentricity ($v_0 + e_0$).
* `w_e` will be calculated mathematically as `w_total` - `w_0` ($e_0$).



## 7. Failure modes and exclusions

* `n_specimens` (total in paper): 31 (9 stub columns + 22 long columns).
* `n_included` (after filtering): 22
* **Exclusions and reasons:** All 9 stub column tests are strictly excluded because the authors explicitly note they "failed by inelastic local buckling". The 22 long columns are retained because all specimens explicitly failed by flexural buckling around the minor or major axis.
* **Failure Mode Note:** `failure_mode` will be logged directly as `global_flexural` for all 22 included rows.

## 8. FEA details

N/A (The paper relies exclusively on experimental data, though it notes numerical studies are underway).

## 9. Data extraction notes

* **Tables:** Tensile properties (Table 3). Minor axis geometries and imperfections (Table 8). Minor axis ultimate loads $N_u$ (Table 9). Major axis geometries and imperfections (Table 10). Major axis ultimate loads $N_u$ (Table 11).
* **Units:** Stresses and Modulus $E$ are in N/mm² (MPa). Dimensions and imperfections are in mm. Ultimate loads are in kN.
* **Section Type:** Recorded as `I`. The `forming_route` must be flagged as `laser_welded`.

## 10. Judgement calls and flags

* **Material Selection (Dissimilar Thicknesses):** For cross-sections built from dissimilar plate thicknesses (where both flange and web coupons are provided), the flange (F) properties should be extracted and applied to the columns. The flanges dominate the second moment of area and flexural stability, especially for minor-axis buckling.
* **Forming Route Identification:** Utilised the `laser_welded` forming route category, which is specifically accommodated in your data dictionary to track unique residual stress patterns.
* **Imperfection Mapping (`w_0`, `w_e`, `w_total`):** Mapped `w_0` to $v_0$ and `w_total` to the combined $v_0 + e_0$ eccentricity explicitly tracked by the authors via strain gauges.

## 11. General notes and useful for later

* **Residual Stresses & ML Generalisation:** The authors found that laser-welding inputs much less heat than conventional arc welding, resulting in significantly lower residual stresses. As a result, these laser-welded columns exhibited superior buckling performance compared to their conventionally welded counterparts. This provides an excellent test for the Stage 1 ML model—it will have to implicitly rely on the `forming_route` proxy (`laser_welded` vs `welded`) to recognise this physical difference and predict higher capacities accordingly.
