# Y.Huang 2013: Tests of pin-ended cold-formed lean duplex stainless steel columns

- Date read (15/06/2026):

## 1. Summary: what was tested

- Experimental study investigating behaviour of cold-formed lean duplex (50% ferrite 50% austenite)stainless steel (EN 1.4162) columns under axial compression.
- Consists of 32 concentrically loaded pin-ended long columns and 6 stub columns covering 2 SHS and 4 RHS
- Primary aim was to assess applicability of existing American, Australian, New Zealand and European design specs for high-strength lean duplex grade

## 2. Material properties

- Derived from both flat tensile coupon tests (Table 7) and complete cross-section stub column tests (Table 8).
- Properties are reported as averaged values per batch
- Secondary R0 parameters not reported
- Tensile coupon tests must be prioritised for extraction (Table 7) rather than stub columns (which failed by local buckling)


## 3. Ramberg-Osgood exponent n 

- n_source = derived 
- Authors used n = ln(0.01/0.2)/ln(sigma_0.01/sigma_0.2) 

## 4. Batch structure and study_id groupings

- There are 6 distinct batches corresponding to 6 cross-section profiles tested

Chosen Batch groups:
- huang2013_A: RHS 50x30x2.5 (corresponds to series C1)
- huang2013_B: SHS 50x50x1.5 (corresponds to series C2)
- huang2013_C: SHS 50x50x2.5 (corresponds to series C3)
- huang2013_D: RHS 70x50x2.5 (corresponds to series C4)
- huang2013_E: RHS 100x50x2.5 (corresponds to series C5)
- huang2013_F: RHS 150x50x2.5 (corresponds to series C6)


## 5. Geometry and test setup

Raw section dimensions and areas fully tabulated for each specimen in Tables 1-6

Boundary conditions:
- Pinned-pinned
- Supported by wedge plates and pit plates allowing free rotation about the minor axis only

Effective length is directly tabulated for each specimen in tables 10-15, explicitly derived by authors as the specimen length L + thickness of the two end plates (40mm) and wedge plates (70mm)

## 6. Initial geometric imperfections

**Reporting:** Overall geometric imperfections (δ) at mid-length were measured and tabulated as a ratio of the specimen length (e.g., L/1575) in Table 9.

**Crucial Setup Note:** While the authors aimed for zero load eccentricity, they actively measured the final total eccentricity + imperfection (e+δ) resulting from the test setup. These total effective values are reported in Tables 10–15.

## 7. Failure modes and exclusions

Failure modes are explicitly documented per specimen as Yielding (Y), Local buckling (L),Flexural buckling (F), or an interaction (L+F)

- **n_specimens** (total in paper): 38 (32 long columns + 6 stub columns)
- **n_included**(after filtering): 16 long columns.
- **Exclusions and reasons:** All 6 stub columns and 16 long columns must be strictly excluded because they failed by local buckling, material yielding, or an interactive local-global mode. Only the 16 specimens with an explicitly assigned pure flexural buckling mode ("F") in Tables 10–15 are retained.

## 8. Data extraction notes

- Dimensions in Tables 1–6
- Coupon material properties in Table 7
- Imperfections in Table 9
- Effective lengths, ultimate loads, and failure modes in Tables 10–15

**Units: **Modulus (E0) reported in GPa. Loads in kN. Dimensions in mm.

**Buckling Axis:** Columns were oriented to buckle about the minor axis. Therefore, the "Width (B)" from the tables maps to b, and "Depth (D)" maps to h.

## 9. Judgement calls and flags

- n_source flagged as derived
- Opted to extract from the flat tensile coupons (Table 7) rather than the stub columns (Table 8) to avoid geometric instability (local buckling) contaminating the raw material parameters
- While w0 is extracted purely from the natural measured bow (δ in Table 9), the ML model predicting β in Stage 2 should note that an additional setup eccentricity (e) was present, making the total experimental imperfection (e+δ) somewhat larger than w0.
​
## 11. General notes and useful for later

