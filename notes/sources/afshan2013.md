# S.Afshan 2013: Experimental study of Cold-Formed Ferritic SHS

- Date read (13/06/2026):

## 1. Summary: what was tested

- Investigates performance of cold-formed ferritic (high percentage chromium, little to no nickel)stainless steel tubular elements to evaluate European and NA design codes.
- Focuses on SHS and RHS fabricated from N 1.4003 and EN 1.4509 (441) grades
- 15 pin-ended flexural buckling column tests with lengths ranging from 1.1m to 2.6m providing non dim slenderness from 0.31 to 2.33

## 2. Material properties

- E0 and sigma0.2 were obtained through 36 coupon tests (20 tensile and 16 compressive)
- Material properties are reported per batch (grouped by section size)
- Authors provide the flat weighted average tensile and compressive properties across constituent faces
- Reports two-stage Ramberg Osgood parameters


## 3. Ramberg-Osgood exponent n 

- Primary and secondary hardening exponents were measured directly from the stress-strain curves using the RO material model
- n_source = measured


## 4. Batch structure and study_id groupings

- There are four distinct batches in this paper, separated by section size and specific material grade
- All test coupons were extracted from the same lengths 
- Cross section size defines the batch grouping

Chosen Batch groups:
- afshan2013_A: RHS 120x80x3, ferritic EN 1.4003
- afshan2013_B: RHS 60x40x3, ferritic EN 1.4003
- afshan2013_C: SHS 80x80x3, ferritic EN 1.4003
- afshan2013_D: SHS 60x60x3, ferritic EN 1.4509


## 5. Geometry and test setup

Raw dimensions reported:
- length
- depth
- width
- thickness
- internal corner radius
- cross section area A

Boundary conditions:
- hardened steel knife edges at both ends
- fixed conditions about orthogonal axis

Le = L

## 6. Initial geometric imperfections

Global and local imperfections are reported separately

- **w0 = local** --> measured over a representative 800mm length for each section size 
  - *Measured deviation from a flat datum on all four faced of the tube and averaged to determine w0 for that batch*

- **v0 = global** --> measured in axis of buckling for each column specimen prior to testing

Both given as absolute values in mm 

## 7. Failure modes and exclusions

Failure modes for flexural buckling columns are grouped loosely. Authors state the failures *"involved overall flexural buckling and combined local and overall buckling"* 

Specimens excluded from the master and why:

- Stub columns (8 specimens): local failure
- Beams (8 specimens): flexural bending 
- Flexural buckling columns (interactive failures) --> apply cross-section slenderness filter check to exclude short slender profiles that are responsible for combined local and overall buckling

- n_specimens (total in paper): 31 (15 flex columns, 8 stub columns, 8 beams)
- n_included (after filtering): <=15 *tbc


## 9. Data extraction notes

- **Material properties**: Table 3 (individual coupon tests), Table 4 (weighted average tensile flat properties), Table 5 (weighted average compressive flat properties).
- **Flexural buckling geometries**: Table 10, which contains the cross-section dimensions, length, area, and measured global imperfection v0.
- **Flexural Buckling Results:** Table 11, which contains the ultimate load Nu and lateral deflection vu,

Units:
- standard conventions and units

Ambiguities and inconsistencies in the tables:
- Table 3, several specimens have missing values for 1% proof stress and secondary hardening exponent (due to the ultimate tensile stress occuring before the specimen reaches 1% proof strain)
- Omitted failure modes in results


## 10. Judgement calls and flags

- Failure modes need to be separated into local/global buckling --> apply cross-section slenderness filter
- Determine which set of material properties to use

## 11. General notes and useful for later

### Code Comparisons & Stage 2 Modifications

* **SEI/ASCE-8 Performance:** The North American design curves generally overpredict column strength, placing them on the unsafe side for most of the slenderness range.
* **EN 1993-1-4 (EC3) Performance:** The European curve provides a much better fit, though a few experimental points still fall unsafely below the codified line.
* **Proposed Correction ($\beta$ relevance):** To better approximate true buckling resistance, the authors recommend modifying the EC3 curve by either using a higher imperfection factor ($\alpha = 0.76$) with the current plateau ($\lambda_0 = 0.4$), or keeping the current imperfection factor ($\alpha = 0.49$) but shortening the plateau ($\lambda_0 = 0.2$).
* **Slenderness Limits:** The EC3 Class 3 cross-section limit is "rather conservative", whereas SEI/ASCE-8 allows for more efficient material exploitation.

### Imperfection & Eccentricity Handling

* **Enforced Threshold:** If a column's measured initial global imperfection ($v_0$) was less than $L/1500$, the authors artificially applied a loading eccentricity.
* **Combined Effect:** This ensured the combined effect of geometric imperfection plus loading eccentricity always equalled at least $L/1500$. Columns with natural imperfections $\geq L/1500$ were loaded concentrically.

### Post-Peak Behaviour

* **Extended Testing:** Tests were deliberately continued past the ultimate failure load to capture post-peak behaviour.
* **Captured Curves:** Full load-lateral displacement curves were recorded for all flexural buckling specimens, alongside full load-end shortening curves for the stub columns.

### Material Characteristics & Residual Stresses

* **Corner Strength Enhancement:** Due to the pronounced strain-hardening properties of stainless steel, the cold-worked corner regions exhibit higher strength than the flat faces.
* **Grade Equivalency:** The buckling performance of ferritic stainless steel largely overlaps with austenitic and duplex grades, although lean duplex achieves higher ultimate stresses due to its higher yield strength.
* **Residual Stresses:** Stub column lengths were specifically selected to be long enough to retain a "representative pattern" of the parent material's residual stresses and geometric imperfections. The EC3 design approach inherently accounts for these residual stresses through its constant parameters.