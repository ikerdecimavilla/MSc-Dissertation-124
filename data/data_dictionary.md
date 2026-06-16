# Master Dataset — Data Dictionary

**Version:** 1.1  
**Date:** 15/06/2026  
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
| `forming_route` | Mandatory | categorical | — | Manufacturing route of the section, recorded as reported by the source. Allowed values: `cold_formed`, `hot_rolled`, `hot_finished`. 
| `E0` | Mandatory | float | MPa | Initial (elastic) Young's modulus. |
| `sigma_02` | Mandatory | float | MPa | 0.2% proof stress from coupon tests. Notation variants in sources: f0.2, sigma_0.2, fy. |
| `n` | Mandatory | float | — | First-stage Ramberg–Osgood strain hardening exponent (governs response up to sigma_0.2). See `n_source` for provenance flag. |
| `n_source` | Mandatory | categorical | — | Provenance of `n`. Allowed values: `measured` `derived`. For stainless steel, `n` is usually fitted directly, so a `derived` flag should be rare. |
| `sigma_10` | Optional | float | MPa | 1.0% proof stress. Part of the two-stage Ramberg–Osgood model for stainless steel. Notation variants: sigma_1.0, f1.0. |
| `n_prime` | Optional | float | — | Second-stage Ramberg–Osgood hardening exponent (governs response between sigma_0.2 and sigma_1.0 / sigma_u). Part of the two-stage model. Notation variants: n', n'0.2-1.0, m, mu. |
| `sigma_u` | Optional | float | MPa | Ultimate tensile strength from coupon tests. Notation variants: fu, sigma_u. |
 
---
 
### Geometric Properties
 
Raw cross-section dimensions are stored per specimen. Derived section properties (A, I, r) are computed after.
 
| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `cross_section_type` | Mandatory | categorical | — | Cross-section shape. Allowed values: `SHS`, `RHS`, `CHS`, `Angle`... |
| `b` | Mandatory | float | mm | External width of the cross-section. For CHS, store the outer diameter here and leave `h` null. |
| `h` | Mandatory | float | mm | External height of the cross-section. Null for CHS. |
| `t` | Mandatory | float | mm | Wall thickness. For sections with distinct flange and web thicknesses, the governing (minimum) thickness is stored and noted in the source log. |
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
| `failure_mode` | Mandatory | categorical | — | Reported failure mode. Allowed values: `global_flexural`, `local`, `interactive`. Where the source does not distinguish modes explicitly, infered from slenderness ratio and noted in the source log. |
 
---
 
### Computed Properties
 
These columns are derived from the mandatory raw inputs. They are never entered manually. They are populated by running the reusable function in /src.
 

| Column | Tier | Type | Units | Formula | Description |
|---|---|---|---|---|---|
| `A` | Computed | float | mm^2 | See above | Cross-sectional area. |
| `I` | Computed | float | mm^4 | See above | Second moment of area about the weak axis. |
| `r` | Computed | float | mm | sqrt(I / A) | Radius of gyration. |
| `lambda_bar` | Computed | float | — | (Le / (pi * r)) * sqrt(sigma_0.2 / E0) | Non-dimensional slenderness per Köllner, Gardner & Wadee (2023). |
 | `w_total` | Computed | float | mm | (w_0 + w_e) | Total effective global imperfection experienced by the column during testing. This is the sum of the natural measured bow and any artificially applied setup eccentricity. This combined metric is strictly required for the Stage 2 ML model to accurately predict the β correction factor based on the actual imperfection state the column experienced. |
---
 
## General Notes
 
**Units convention:** All stresses in MPa, all lengths and dimensions in mm, all loads in kN.
 
**Null handling:** Optional columns are left null where not reported. 

**Column extension:** New columns may be added as additional sources are integrated. Any new column is added to this dictionary before being added to the CSV. The tier (mandatory / optional / computed) is declared at the time of addition.
 
**Source log cross-reference:** Any judgement call made during data entry (inferred failure mode, derived Le, imperfection notation interpretation, inferred stainless family, n flagged as derived) is to be recorded in `data/source_log.csv` with the relevant `source_id` and a brief note.