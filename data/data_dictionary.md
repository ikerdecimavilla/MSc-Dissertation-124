# Master Dataset — Data Dictionary

**Version:** 1.0  
**Date:** 13/06/2026  
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
| `n_source` | Mandatory | categorical | — | Provenance of `n`. Allowed values: `measured` (fitted directly from coupon stress–strain data), `derived` (back-calculated from two stress points, e.g. via n = ln2 / ln(sigma_0.2 / sigma_0.1)). For stainless steel, `n` is usually fitted directly, so a `derived` flag should be rare. |
| `sigma_10` | Optional | float | MPa | 1.0% proof stress. Part of the standard two-stage Ramberg–Osgood model for stainless steel (Mirambell–Real / Rasmussen). Expected to be well populated across stainless sources. Notation variants: sigma_1.0, f1.0. |
| `n_prime` | Optional | float | — | Second-stage Ramberg–Osgood hardening exponent (governs response between sigma_0.2 and sigma_1.0 / sigma_u). Part of the two-stage stainless steel model. Notation variants: n', n'0.2-1.0, m, mu. |
| `sigma_u` | Optional | float | MPa | Ultimate tensile strength from coupon tests. Notation variants: fu, sigma_u. |
 
---
 
### Geometric Properties
 
Raw cross-section dimensions are stored per specimen. Derived section properties (A, I, r) are computed after.
 
| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `cross_section_type` | Mandatory | categorical | — | Cross-section shape. Allowed values: `SHS`, `RHS`, `CHS`, `Angle`... |
| `b` | Mandatory | float | mm | External width of the cross-section. For CHS, store the outer diameter here and leave `h` null. |
| `h` | Mandatory | float | mm | External height of the cross-section. Null for CHS. |
| `t` | Mandatory | float | mm | Wall thickness. For sections with distinct flange and web thicknesses, store the governing (minimum) thickness here and note the variant in the source log. |
| `L` | Mandatory | float | mm | Physical member length as reported by the source. |
| `boundary_condition` | Mandatory | categorical | — | End condition of the column. Allowed values: `pin-pin`, `fixed-fixed`, `fixed-pin`, `fixed-free`. |
| `Le` | Optional | float | mm | Effective buckling length. Populate directly where reported by the source. Where not reported, derived from `L` using the standard effective length factor for the given `boundary_condition` (k = 1.0 pin-pin, k = 0.5 fixed-fixed, k = 0.7 fixed-pin, k = 2.0 fixed-free).|
| `buckling_axis` | Mandatory | categorical | — | The principal axis about which the member underwent flexural buckling, read from the source's test description. Allowed values: `minor`, `major`. |
| `w0` | Optional | float | mm | Initial global geometric imperfection amplitude (maximum bow). Notation is highly variable across sources: w0, omega_g, delta_v, delta_mid, e0. |

 
---
 
### Test Outputs
 
| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `N_u` | Mandatory | float | kN | Ultimate axial load at failure. Notation variants: Pu, Nu, FEXP, Nu,EXP. |
| `failure_mode` | Mandatory | categorical | — | Observed or reported failure mode. Allowed values: `global_flexural`, `local`, `interactive`. Where the source does not distinguish modes explicitly, infer from slenderness ratio and note as inferred in the source log. Rows where failure mode cannot be reliably determined should be flagged and excluded from modelling. |
 
---
 
### Computed Properties
 
These columns are derived programmatically from the mandatory raw inputs. They are never entered manually. Populate them by running the computation notebook after raw data entry is complete.
 

| Column | Tier | Type | Units | Formula | Description |
|---|---|---|---|---|---|
| `A` | Computed | float | mm^2 | See above | Cross-sectional area. |
| `I` | Computed | float | mm^4 | See above | Second moment of area about the weak axis. |
| `r` | Computed | float | mm | sqrt(I / A) | Radius of gyration. |
| `lambda_bar` | Computed | float | — | (Le / (pi * r)) * sqrt(sigma_0.2 / E0) | Non-dimensional slenderness per Köllner, Gardner & Wadee (2023). Requires `Le` — use derived `Le` where not reported directly. |
 
---
 
## General Notes
 
**Units convention:** All stresses in MPa, all lengths and dimensions in mm, all loads in kN. Convert at point of entry — do not store mixed units.
 
**Null handling:** Optional columns are left null (empty cell in CSV) where not reported. Do not substitute zeroes for nulls.
 
**Column extension:** New columns may be added as additional sources are integrated. Any new column must be added to this dictionary before being added to the CSV. The tier (mandatory / optional / computed) must be declared at the time of addition.
 
**Source log cross-reference:** Any judgement call made during data entry (inferred failure mode, derived Le, imperfection notation interpretation, inferred stainless family, n flagged as derived) must be recorded in `data/source_log.csv` with the relevant `source_id` and a brief note.