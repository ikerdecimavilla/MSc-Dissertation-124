# C.Buchanan 2018: Tests of cold-formed stainless steel CHS columns

- Date read (15/06/2026):

## 1. Summary: what was tested

- concentrically loaded cold-formed stainless steel CHS columns
- 37 pin-ended long columns and 10 stub columns spanning austenitic (Grades 1.4432, 1.4307/1.4301), duplex (Grade 1.4462), and ferritic (Grade 1.4512) stainless steels over a wide range of global slendernesses.
- Aim was to provide data to validate numerical models and demonstrate that provisions from EN 1993-1-4 are unconservative for CHS

## 2. Material properties

- Derived from both tensile coupons and full-section stub column tests in compression. Two tests were performed per batch.
- Full two-stage R-O parameters in Table 2
- Compressive properties in Table 4
- Secondary R0 parameters not reported


## 3. Ramberg-Osgood exponent n 

- n_source = measured
- Authors state in section 2.2 that "The Ramberg-Osgood and extended parameters were determined using weighted total least squares regression that is independent of the distribution of the data points."

## 4. Batch structure and study_id groupings

- There are 6 distinct physical material batches separated by cross-section size and tube origin (the 104×2 tubes were sourced from two different countries, SWE and FIN, with noticeably different strengths).

Chosen Batch groups:
- buchanan2018_A: CHS 106x3 (Austenitic)
- buchanan2018_B: CHS 104x2 FIN (Austenitic, Finland)
- buchanan2018_C: CHS 104x2 SWE (Austenitic, Sweden)
- buchanan2018_D: CHS 88.9x2.6 (Duplex)
- buchanan2018_E: CHS 80x1.5 (Ferritic)
- buchanan2018_F: CHS 101.6x1.5 (Ferritic)


## 5. Geometry and test setup

- Raw dimensions (D and t) in Tables 5-9, following the schema for CHS, D maps to b and h is left null.
- Boundary conditions: pin-pin
- Length L already includes the additional length from the knife edges so the reported L is the same as the effective buckling length Le

## 6. Initial geometric imperfections

- **Reporting:** The measured initial global mid-height bow is reported in Tables 5–9 as an L/ω0 ratio. 
- **Crucial Setup Note:** The authors artificially manipulated the test setup to introduce a loading eccentricity (e0), ensuring that the combined total imperfection (ω0+e0) equalled exactly L/1000. These combined values are also tabulated.

## 7. Failure modes and exclusions

- `n_specimens` (total in paper): 47 physical tests (37 long + 10 stub) + 450 FEA models.
- `n_included `(after filtering): 34 long columns.
- **Exclusions and reasons:** All 10 stub columns are strictly excluded as they failed by pure local buckling. The 450 FEA rows are excluded to prevent artificial dataset inflation. Additionally, 3 very short ferritic columns (80x1.5-300-P, 101.6x1.5-350-P, and 101.6x1.5-500-P) must be excluded; the authors explicitly state these "did not show an obvious global buckle at the peak load and instead developed 'elephant's foot' buckles" (local failure).

## 8. Data extraction notes

- Tensile properties in Table 2
- Compressive stub properties in Table 4
- Geometries and Nu are in Tables 5-9
- Imajor=Iminor (CHS) so `buckling_axis` left null

## 9. Judgement calls and flags

- **buckling_axis convention:** Assigned as - due to the perfectly symmetric nature of the CHS cross-sections.
- **Material Selection:** Prioritised the compressive flat material properties (Table 4) over tensile to align with column buckling physics. Missing parameters (σu and n0.2,1.0) were supplemented from the corresponding tensile batches in Table 2.
- **Failure Mode Filtering:** Excluded 3 very short pin-ended ferritic columns based on the authors' observation of premature local "elephant's foot" buckling before global buckling could govern.
- **Stage 2 Imperfection Flag**: Extracted the natural initial bow as w0 by reversing the L/ω0 ratios. However, the model predicting β must be flagged that these columns were actively forced to buckle with an effective combined imperfection of L/1000 due to artificially applied loading eccentricities.
​

