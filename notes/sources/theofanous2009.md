# Behzadi 2021 : Fixed-ended equal-leg angle section compression members

## Metadata

- Date read: 15/06/2026

## 1. Summary: what was tested

into the compressive structural response of cold-rolled lean duplex stainless steel (Grade EN 1 4162) hollow sections. Included 8 stub column tests and 12 pin-ended flexural buckling column tests on square (SHS) and rectangular (RHS) sections. The primary aim was to assess the applicability of Eurocode 3: Part 1-4 provisions (Class 3 limits, effective width, and buckling curves) to this specific low-nickel grade.

## 2. Material properties

- **Experimental:** Derived from tensile flat, compressive flat, and tensile corner coupons.
- **Reporting:** Full two-stage R-O parameters are tabulated per section-size batch in Tables 2,3 and 4.
- **Selection**: Compressive flat material properties (Table 3) should be prioritised for global flexural buckling as done previously for afhsan2013.


## 3. Ramberg-Osgood exponent n (provenance flag)

n_source = measured


## 4. Batch structure and study_id groupings

Batches are cleanly separated by the four tested cross-section sizes, as each size shares a single unique set of coupon results.

- `theofanous2009_A`: SHS 100x100x4 (stub columns only, will be excluded)
- `theofanous2009_B`: SHS 80x80x4
- `theofanous2009_C`: SHS 60x60x3
- `theofanous2009_D:` RHS 80x40x4

FEA batches are ignored for now 

## 5. Geometry and test setup

- **Geometry:** raw dimensions and Area (A) tabulated in Table 7.
- **Boundary Conditions:** Stub columns compressed between flat parallel platens. Flexural buckling columns tested using knife-edges to simulate strictly pin-ended conditions.
- **Effective Length (Le)** Directly reported in Table 7 as the buckling length Lcr (total distance between knife edges)

## 6. Initial geometric imperfections

- **Reporting:** Both local (w0) and global (e0) measured prior to testing --> global bow (e0) mapped onto this study's schema's w0.
- **Format:** Reported in Table 7 as mm.
- **Crucial Setup Note:** The authors artificially enforced a minimum combined eccentricity. If the measured initial bow was small, they applied the load eccentrically so that the total initial imperfection (bow + loading eccentricity) equalled exactly L/1500.

## 7. Failure modes and exclusions

Modes are  distinguished between stub columns and long columns.

- `n_specimens` (total in paper): 20 physical tests (8 stub, 12 long) + extensive parametric FEA.
- `n_included` (after filtering): 12 long columns
**Exclusions and reasons:** FEA results are not included at this stage, stub columns excluded because they failed by local buckling.

## 8. FEA details (delete if purely experimental)

- Validated against 20 tests, mean ratio of numerical to experimental for flexural columns was 0.99 with a CoV of 0.05 when L/1500 imperfection assumed
- **Elements & Assumptions:** ABAQUS S4R shell elements. Implicitly included residual stresses via the coupon curves. Applied corner enhancements extending 2t into the flat faces
- **Parametric study:** Generated data covering aspect ratios 1.0 and 2.0 over a member slenderness range of 0.4 to 2.4. Used the Dawson and Walker predictive model for local imperfection amplitudes and L/1500 for global bow.
- **Recommendation**: Exclude FEA to prevent artificially inflating the model with near-duplicates.
  
## 9. Data extraction notes

- **Tables:** Material properties in Tables 2, 3, and 4. Long column geometries, effective lengths, and imperfections in Table 7. Long column ultimate loads (Fu) in Table 8.
- **Units**: Modulus (E) and stresses in N/mm² (MPa). Loads in kN. Dimensions in mm. No conversions needed.
- **Buckling Axis:** Table 7 explicitly specifies whether RHS specimens buckled about the major or minor axis.

## 10. Judgement calls and flags

**Material selection:** Extracted the flat compressive properties (Table 3) instead of tensile, aligning with the compressive nature of global column buckling.

**Imperfection threshold (Flag for Stage 2)**: While recording the raw measured global bow (e0 mapped to w0), it is critical to flag that the actual experimental imperfection was artificially bumped to L/1500 via load eccentricity