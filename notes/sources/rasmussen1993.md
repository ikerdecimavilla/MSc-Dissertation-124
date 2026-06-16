# Rasmussen & Hancock 1993 : Design of cold-formed stainless steel tubular members. I: Columns

## Metadata

* Date read: 16/06/2026

## 1. Summary: what was tested

This foundational experimental study investigated the compressive strength and global flexural buckling of cold-formed austenitic stainless steel (Type 304L) tubular members. The testing programme consisted of 20 physical tests across two cross-section profiles (Square Hollow Sections 80×3.0 mm and Circular Hollow Sections 101.6×2.85 mm), comprising 4 stub columns and 16 pin-ended long columns. The primary aim was to quantify the considerable strength enhancement produced by the cold-rolling and welding fabrication process and to propose a design method that exploits these enhanced properties rather than relying on conservative annealed material data.

## 2. Material properties

* **Experimental:** The authors performed extensive tension and compression testing on flat/curved coupons cut from the tubes, but crucially, they also tested full-section stub columns in compression to capture the complete cross-section's behaviour.
* **Reporting:** The initial Young's modulus ($E_0$), 0.2% proof stress ($\sigma_{0.2}$), and hardening exponent ($n$) are explicitly reported for the full stub columns in Table 3.
* **Selection:** Because column buckling is a compressive instability and the cold-forming process introduces significant cross-sectional variations (especially in the SHS corners), the compressive stub column properties (Table 3) must be prioritised for data extraction over the individual tensile coupons. $E_0$ is 191 GPa for SHS and 201 GPa for CHS. The secondary two-stage Ramberg-Osgood parameters ($\sigma_{1.0}$, $n^\prime$) were not reported.

## 3. Ramberg-Osgood exponent n (provenance flag)

n_source = measured

* **Reasoning:** curves were "fitted through the measured stress-strain curves" obtained from the stub column tests. The exponent $n$ was derived directly from the physical nonlinear curves (resulting in $n=3.0$ for SHS and $n=6.0$ for CHS)

## 4. Batch structure and study_id groupings

There are 2 distinct physical material batches, separated cleanly by cross-section type. All long columns of a given profile were cut from the same parent coil as their corresponding stub columns, meaning they share virtually identical material properties.

* `rasmussen1993_A`: SHS 80×3.0 (Austenitic 304L)
* `rasmussen1993_B`: CHS 101.6×2.85 (Austenitic 304L)

## 5. Geometry and test setup

* **Geometry:** The measured dimensions (outer width $B$, diameter $d_0$, and thickness $t$) are fully tabulated in Tables 1 and 2. Following the dataset schema, $B$ and $d_0$ map to $b$. For the CHS, $h$ must be left null.
* **Boundary conditions:** Pin-ended (pin-pin). The columns were tested in a horizontal reaction frame using rigid end platens mounted on bearings that were free to rotate about both principal axes.
* **Effective length ($L_e$):** The authors report the specimen physical cut length ($L$). They explicitly state that the pinned end bearings added 225 mm to each end. Therefore, the effective pin-ended column length ($L_t$ in the paper) must be derived as $L_e = L + 450$ mm.

## 6. Initial geometric imperfections

* **Reporting:** The authors rigorously measured the natural mid-length bow ($v_{01}$ and $v_{02}$) in both principal planes in absolute millimetres. These map directly to $w_0$.
* **Crucial Setup Note:** For half of the long columns (labeled with an 'E'), the authors actively induced a nominal initial loading eccentricity of a thousandth of the pinned column length ($L_t/1000$). They tabulated these applied eccentricities ($e_{01}$, $e_{02}$) alongside the natural bow. The combined total initial distance from the line of action to the geometric centroid is given as $|v_{01} - e_{01}|$ and $|v_{02} - e_{02}|$. Therefore, $w_e$ corresponds to $-e_0$, and $w_{total}$ is the combined value.

## 7. Failure modes and exclusions

* `n_specimens` (total in paper): 20 (4 stub columns + 16 long columns).
* `n_included` (after filtering): 16 long columns.
* **Exclusions and reasons:** The 4 stub columns (S1SC1, S1SC2, C1SC1, C1SC2) are strictly excluded as they are purely material/local characterisation tests. All 16 long columns are safe to include. The authors confirm that "Local buckling... was not observed in the SHS and CHS long column tests" prior to failure; it only occurred in two short specimens (S1L1000) as an inelastic buckle during the advanced postultimate stages of loading. Therefore, the peak loads ($P_u$) reported in Tables 1 & 2 represent pure global flexural buckling.

## 8. Data extraction notes

* **Tables:** Geometries, imperfections, eccentricities, and ultimate loads ($P_u$) for the long columns are in Table 1 (SHS) and Table 2 (CHS). Material properties are in Table 3.
* **Units:** Modulus $E_0$ is reported in GPa and must be multiplied by 1000 for MPa. Stresses are in MPa. Loads are in kN. Lengths and imperfections are in mm.
* **Buckling Axis:** Because this dataset consists solely of perfectly symmetric Square Hollow Sections (SHS) and Circular Hollow Sections (CHS), moments of inertia are identical about all lateral axes. Therefore, the buckling_axis must be populated uniformly as `-` for all rows.

## 9. Judgement calls and flags

* **Material Selection:** Prioritised the compressive stub column parameters (Table 3) over individual flat/corner tension coupons to properly capture the composite cross-sectional stiffness inherent to column buckling.
* **buckling_axis convention:** Assigned as `-` due to the geometrically symmetric nature of both SHS and CHS profiles.
* **Lengths:** Computed the effective length programmatically ($L_e = L + 450$ mm) based on the authors' description of the test bearings.
* **Stage 2 Imperfection Flag:** Carefully mapped the natural bow $v_0$ to $w_0$, the applied eccentricity $e_0$ to $w_e$, and the combined baseline $|v_0 - e_0|$ to $w_{total}$. The authors explicitly tested identical lengths both concentrically (label 'C', aiming for $w_e = 0$) and eccentrically (label 'E', aiming for $w_{total} = L_e/1000$). This creates an incredibly valuable contrast for training your Stage 2 $\beta$ prediction model.

## 10. General notes and useful for later

* **Cold-work impact:** The study heavily emphasizes that standard design codes (like the ASCE specification) are overly conservative for low-slenderness tubes because they rely on annealed material properties. Cold-working drastically increases strength (and introduces severe bending residual stresses). 
* **Residual Stresses:** Interestingly, while longitudinal membrane residual stresses were negligible, through-thickness bending residual stresses were very large (up to $3119 \mu\epsilon$ in the SHS flats), causing earlier yielding/nonlinearity in the SHS compared to the CHS. This is excellent physical context for why $n$ values differ so sharply between the two profiles ($n=3.0$ for SHS vs $n=6.0$ for CHS) despite originating from similar baseline steel.