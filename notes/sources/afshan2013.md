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

Failure modes for flexural buckling columns are grouped loosel. Authors state the failures *"involved overall flexural buckling and combined local and overall buckling"* 

Specimens excluded from the master and why:

- Stub columns (8 specimens): local failure
- Beams (8 specimens): flexural bending 
- Flexural buckling columns (interactive failures) --> apply cross-section slenderness filter check to exclude short slender profiles that are responsible for combined local and overall buckling

- n_specimens (total in paper): 31 (15 flex columns, 8 stub columns, 8 beams)
- n_included (after filtering): <=15 *tbc


## 9. Data extraction notes

> Where are the data tables (table numbers and page)? What units does the paper use for each quantity, and what conversions did you apply on entry (for example E in GPa multiplied by 1000 to MPa, load already in kN so unchanged)? Note anything ambiguous or inconsistent in the tables themselves.

## 10. Judgement calls and flags

> Anything that required interpretation: a derived Le, an inferred failure mode, an inferred stainless family, an unusual n derivation, ambiguous notation. Every item recorded here must also be entered in the judgement_calls field of source_log.csv so the two stay in sync.

## 11. General notes and useful for later

> Anything beyond the raw data that could matter downstream: post-peak behaviour, imperfection-sensitivity comments, how the authors compared results to code predictions (EN 1993-1-4 and similar), residual stresses, or any observation that could inform the Stage 2 correction factor or the discussion chapter.