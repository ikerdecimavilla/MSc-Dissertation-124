# Master Dataset — Data Dictionary

**Version:** 1.2  
**Date:** 17/06/2026  
**Description:** Column definitions for the master dataset of Ramberg–Osgood material column buckling experiments and FEA parametric studies.

---

## Overview

The master dataset is organised in three tiers:

- **Mandatory:** must be present for every row; a row is incomplete without these
- **Optional:** populated where reported by the source; null otherwise
- **Computed:** derived programmatically from raw inputs; never entered manually

Material properties are reported per batch in most sources and are duplicated down to every specimen row. The `study_id` field captures the batch grouping for cross-validation purposes.

---

## Column Definitions
 
### Provenance
 
| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `specimen_id` | Mandatory | string | — | Unique row identifier. Format: `[first_author][year]_[number]`, e.g. `afshan2013_01`. Numbers are zero-padded to two digits within each source. |
| `source_id` | Mandatory | string | — | Zotero citation key for the source paper, e.g. `afshan2013`. Must match the key in `references/library.bib` exactly. |
| `study_id` | Mandatory | string | — | Identifier for the experimental campaign or FEA batch. Where a paper reports a single batch, `study_id` equals `source_id`. Where a paper reports multiple clearly distinct batches or series, append a letter: e.g. `afshan2013_A`, `afshan2013_B`. |
| `data_type` | Mandatory | categorical | — | Provenance of the row. Allowed values: `experimental`, `FEA`. For studies that report both, assign per row. |
 
---
 
### Material Properties
 
All material properties are from the reported coupon tests.
 
| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `material_grade` | Mandatory | string | — | Stainless steel grade designation as reported by the source, e.g. `1.4301`, `1.4404`, `1.4571`, `1.4462`, `1.4003`. |
| `material_type` | Mandatory | categorical | — | Stainless steel family. Allowed values: `austenitic`, `ferritic`, `duplex`, `lean_duplex`. |
| `forming_route` | Mandatory | categorical | — | Manufacturing route of the section, recorded as reported by the source. Allowed values: `cold_formed`, `hot_rolled`, `hot_finished`, `press_braked`, `laser_welded`. Used by the classifier as the residual-stress proxy that selects the outstand limit set (welded vs non-welded) for open sections. |
| `E0` | Mandatory | float | MPa | Initial (elastic) Young's modulus. |
| `sigma_02` | Mandatory | float | MPa | 0.2% proof stress from coupon tests. Notation variants in sources: f0.2, sigma_0.2, fy. |
| `n` | Mandatory | float | — | First-stage Ramberg–Osgood strain hardening exponent (governs response up to sigma_0.2). See `n_source` for provenance flag. |
| `n_source` | Mandatory | categorical | — | Provenance of `n`. Allowed values: `measured` `derived`. For stainless steel, `n` is usually fitted directly, so a `derived` flag should be rare. |
| `sigma_10` | Optional | float | MPa | 1.0% proof stress. Part of the two-stage Ramberg–Osgood model for stainless steel. Notation variants: sigma_1.0, f1.0. |
| `n_prime` | Optional | float | — | Second-stage Ramberg–Osgood hardening exponent (governs response between sigma_0.2 and sigma_1.0 / sigma_u). Part of the two-stage model. Notation variants: n', n'0.2-1.0, m, mu. |
| `sigma_u` | Optional | float | MPa | Ultimate tensile strength from coupon tests. Notation variants: fu, sigma_u. |
 
---
 
### Geometric Properties
 
Raw cross-section dimensions are stored per specimen. Derived section properties (A, I, R) are computed after.
 
| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `cross_section_type` | Mandatory | categorical | — | Cross-section shape. Allowed values: `SHS`, `RHS`, `CHS`, `I`, `H`, `Angle`... |
| `b` | Mandatory | float | mm | External width of the cross-section. For CHS, store the outer diameter here and leave `h` null. For `I` / `H` sections, this is the flange width. |
| `h` | Mandatory | float | mm | External height of the cross-section. Null for CHS. For `I` / `H` sections, this is the overall depth. |
| `t` | Mandatory | float | mm | Wall thickness. For sections with distinct flange and web thicknesses, the governing (minimum) thickness is stored and noted in the source log; for `I` / `H` sections the distinct thicknesses may instead be given in `t_f` / `t_w`. |
| `t_f` | Optional | float | mm | Flange thickness, for `I` / `H` sections with distinct flange and web thicknesses. Where absent, the section calculator falls back to `t`. |
| `t_w` | Optional | float | mm | Web thickness, for `I` / `H` sections with distinct flange and web thicknesses. Where absent, the section calculator falls back to `t`. |
| `L` | Mandatory | float | mm | Physical member length as reported by the source. |
| `boundary_condition` | Mandatory | categorical | — | End condition of the column. Allowed values: `pin-pin`, `fixed-fixed`, `fixed-pin`, `fixed-free`. |
| `Le` | Optional | float | mm | Effective buckling length. Where not reported, derived from `L` using the standard effective length factor for the given `boundary_condition` (k = 1.0 pin-pin, k = 0.5 fixed-fixed, k = 0.7 fixed-pin, k = 2.0 fixed-free).|
| `buckling_axis` | Mandatory | categorical | — | The principal axis about which the member underwent flexural buckling, read from the source's test description. Allowed values: `minor`, `major`. |
| `w_0` | Optional | float | mm | Initial global geometric imperfection amplitude (maximum bow). Notation changes across sources: w0, omega_g, delta_v, delta_mid, e0. |
| `w_e` | Optional | float | mm | Artificially applied initial loading eccentricity introduced by researchers during testing to achieve a specific target imperfection (e.g., L/1000). Where researchers tested concentrically or did not actively apply an eccentricity, this is populated as 0.0. |

 
---
 
### Test Outputs
 
| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `N_u` | Mandatory | float | kN | Ultimate axial load at failure. Notation variants: Pu, Nu, FEXP, Nu,EXP. |
| `failure_mode` | Mandatory | categorical | — | Reported failure mode. Allowed values: `global_flexural`, `local`, `interactive`. Where the source does not report a mode explicitly, it is taken from the computed `inferred_failure_mode` and the judgement is noted in the source log. |
 
---
 
### Computed Properties
 
These columns are derived from the mandatory raw inputs. They are never entered manually. They are populated by running the reusable functions in /src (`features.add_features` then `classify.classify`).
 

| Column | Tier | Type | Units | Formula | Description |
|---|---|---|---|---|---|
| `A` | Computed | float | mm^2 | See section formulae | Cross-sectional area. |
| `I_major` | Computed | float | mm^4 | See section formulae | Second moment of area about the major principal axis. |
| `I_minor` | Computed | float | mm^4 | See section formulae | Second moment of area about the minor principal axis. |
| `R` | Computed | float | mm | sqrt(I_crit / A) | Radius of gyration about the buckling axis. `I_crit` is `I_major` or `I_minor` selected by `buckling_axis`. |
| `lambda` | Computed | float | — | Le / R | Standard (dimensional) slenderness ratio. |
| `N_cr` | Computed | float | N | (pi^2 * E0 * I_crit) / Le^2 | Euler elastic critical buckling load. |
| `N_y` | Computed | float | N | A * sigma_02 | Squash (yield) load of the gross cross-section. |
| `lambda_bar` | Computed | float | — | sqrt(N_y / N_cr); equivalently (Le / (pi * R)) * sqrt(sigma_02 / E0) | Non-dimensional slenderness per Köllner, Gardner & Wadee (2023). |
| `chi` | Computed | float | — | N_u / N_y | Experimental strength reduction factor. |
| `epsilon` | Computed | float | — | sqrt((235 / sigma_02) * (E0 / 210000)) | Material factor per EN 1993-1-4 Table 5.2. |
| `cs_slenderness` | Computed | float | — | See EN 1993-1-4 Table 5.2 | Governing plate slenderness used for the cross-section class: c/t for SHS/RHS/I, d/t for CHS. |
| `section_class` | Computed | integer | — | See EN 1993-1-4 Table 5.2 | EN 1993-1-4 cross-section class under uniform compression. Allowed values: `1`, `2`, `3`, `4`, or null. Null for `Angle` (excluded from classification) and where geometry needed for the check (e.g. `t`) is missing. |
| `lambda_0` | Computed | float | — | See EN 1993-1-4 Table 5.3 | Limiting slenderness for flexural buckling. `0.40` for hollow and rolled / cold-formed open sections; `0.20` for welded open sections. |
| `inferred_failure_mode` | Computed | categorical | — | From `section_class` and `lambda_bar` | Failure mode inferred where `failure_mode` is not reported. Allowed values: `global_flexural`, `yielding`, `local`, `local_global_interaction`, `unknown`. `local_global_interaction` corresponds to the reported `interactive` category; `unknown` is used for excluded angles or where `section_class` could not be determined. |
| `w_total` | Computed | float | mm | (w_0 + w_e) | Total effective global imperfection experienced by the column during testing. This is the sum of the natural measured bow and any artificially applied setup eccentricity. This combined metric is strictly required for the Stage 2 ML model to accurately predict the β correction factor based on the actual imperfection state the column experienced. |
---
 
## General Notes
 
**Units convention:** All stresses in MPa, all lengths and dimensions in mm, all loads in kN.
 
**Null handling:** Optional columns are left null where not reported. 

**Column extension:** New columns may be added as additional sources are integrated. Any new column is added to this dictionary before being added to the CSV. The tier (mandatory / optional / computed) is declared at the time of addition.
 
**Source log cross-reference:** Any judgement call made during data entry (inferred failure mode, derived Le, imperfection notation interpretation, inferred stainless family, n flagged as derived) is to be recorded in `data/source_log.csv` with the relevant `source_id` and a brief note.