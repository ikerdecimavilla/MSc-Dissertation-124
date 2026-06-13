# [Author] ([Year]): [Short title]

> Reading-notes template. Copy to `notes/sources/[source_id].md`, rename, and replace the bracketed fields. The blockquote prompts are guidance, delete each one as you fill its section. The goal is to understand and appraise the source before any number goes into the standardised CSV.

## Metadata

- source_id (Zotero key):
- First author:
- Year:
- DOI:
- Data type (experimental / FEA / mixed):
- Date read (DD/MM/YYYY):

## 1. Summary: what was tested

> One short paragraph. Material grade(s), cross-section type(s), the range of lengths or slendernesses, the number of specimens, and the headline aim of the study.

## 2. Material properties

> How were E0 and sigma_0.2 obtained, and from how many coupon tests? Are properties reported per batch or per individual specimen? Note the two-stage Ramberg-Osgood parameters (sigma_1.0 and the second exponent n') if the paper reports them.

## 3. Ramberg-Osgood exponent n (provenance flag)

> The single most important question for data quality. Was n measured by fitting the coupon stress-strain curve, or back-calculated from two stress points? If derived, write down the exact formula used. This decision sets n_source = measured or derived for every row from this study.

## 4. Batch structure and study_id groupings

> A batch is a set of specimens that share the same steel coil and the same coupon results. How many distinct batches are in this paper, and what separates them (section size, grade, test-series label)? List the study_id values you will assign. This defines the grouping for cross-validation, so getting it right here prevents data leakage later.

Example:
- [source_id]_A: SHS 60x60x3, austenitic 1.4301, coupon batch 1
- [source_id]_B: ...

## 5. Geometry and test setup

> What dimensions are tabulated, raw (b, h, t) or derived (A, I)? What boundary conditions were used, described precisely rather than just labelled (knife-edge bearings, welded end plates, pinned fixture with some rotational stiffness)? Is the effective length Le reported directly, or must it be derived? If derived, record the factor k and the relation Le = k * L.

## 6. Initial geometric imperfections

> Is w0 reported? How was it measured or assumed? Is it a global bow, a local imperfection, or a loading eccentricity, and how is it notated in this paper? Given as an absolute value in mm, or as a ratio such as L/1000?

## 7. Failure modes and exclusions

> Are global flexural, local and interactive modes clearly distinguished per specimen, or grouped loosely? Which specimens are excluded from the master, and why (local or interactive failure, anomalous result, flagged by the authors)? Record both counts so the difference is traceable in the methodology chapter.

- n_specimens (total in paper):
- n_included (after filtering):
- Exclusions and reasons:

## 8. FEA details (delete if purely experimental)

> What was the FEA validated against, and how well? What material model and imperfection assumptions were used? Is the parametric range physically realistic, or are there near-duplicate parametric rows that would inflate apparent model performance?

## 9. Data extraction notes

> Where are the data tables (table numbers and page)? What units does the paper use for each quantity, and what conversions did you apply on entry (for example E in GPa multiplied by 1000 to MPa, load already in kN so unchanged)? Note anything ambiguous or inconsistent in the tables themselves.

## 10. Judgement calls and flags

> Anything that required interpretation: a derived Le, an inferred failure mode, an inferred stainless family, an unusual n derivation, ambiguous notation. Every item recorded here must also be entered in the judgement_calls field of source_log.csv so the two stay in sync.

## 11. General notes and useful for later

> Anything beyond the raw data that could matter downstream: post-peak behaviour, imperfection-sensitivity comments, how the authors compared results to code predictions (EN 1993-1-4 and similar), residual stresses, or any observation that could inform the Stage 2 correction factor or the discussion chapter.