# Master Dataset — Data Dictionary

**Version:** 1.4  
**Date:** 24/06/2026  
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
| `forming_route` | Mandatory | categorical | — | Manufacturing route of the section, recorded as reported by the source. Allowed values: `cold_formed`, `hot_rolled`, `hot_finished`, `press_braked`, `laser_welded`, `welded`. Used by the classifier as the residual-stress proxy that selects the outstand limit set (welded vs non-welded) for open sections. Both `laser_welded` and the generic `welded` select the welded limit set and the `0.20` flexural plateau. |
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
| `section_type` | Mandatory | categorical | — | Cross-section shape. Allowed values: `SHS`, `RHS`, `CHS`, `I`, `H`, `Angle`. (This column is named `section_type` in the dataset and in `/src`; earlier drafts referred to it as `cross_section_type`.) |
| `b` | Mandatory | float | mm | External width of the cross-section. For CHS, store the outer diameter here and leave `h` null. For `I` / `H` sections, this is the flange width. |
| `h` | Mandatory | float | mm | External height of the cross-section. Null for CHS. For `I` / `H` sections, this is the overall depth. |
| `t` | Mandatory | float | mm | Wall thickness. For sections with distinct flange and web thicknesses, the governing (minimum) thickness is stored and noted in the source log; for `I` / `H` sections the distinct thicknesses may instead be given in `t_f` / `t_w`. |
| `t_f` | Optional | float | mm | Flange thickness, for `I` / `H` sections with distinct flange and web thicknesses. Where absent, the section calculator falls back to `t`. |
| `t_w` | Optional | float | mm | Web thickness, for `I` / `H` sections with distinct flange and web thicknesses. Where absent, the section calculator falls back to `t`. |
| `L` | Mandatory | float | mm | Physical member length as reported by the source. |
| `boundary_condition` | Mandatory | categorical | — | End condition of the column. Allowed values: `pin-pin`, `fixed-fixed`, `fixed-pin`, `fixed-free`. Required to derive `Le` when an effective length is not reported. |
| `Le` | Optional | float | mm | Effective buckling length. Where not reported, derived automatically by `features.add_features` as `Le = k · L` using the standard effective length factor for the given `boundary_condition` (k = 1.0 pin-pin, k = 0.5 fixed-fixed, k = 0.7 fixed-pin, k = 2.0 fixed-free). Always populated in the master; see `Le_source`. |
| `Le_source` | Computed | categorical | — | Provenance of `Le`. Allowed values: `reported` (taken directly from the source), `derived` (computed as `k · L`). |
| `buckling_axis` | Mandatory | categorical | — | The principal axis about which the member underwent flexural buckling. Allowed values: `minor`, `major`, `-`. Populated for every master row by `features.add_features`: a source-reported axis is honoured; perfectly symmetric sections (SHS/CHS) carry no weaker axis and are recorded as `-`; asymmetric sections (RHS/I/H) with no reported axis default to `minor`, valid for a standard pin-ended test with no intermediate lateral bracing (the minor axis gives the smallest `r`, the highest `lambda_bar` and the lowest `N_cr`). May be left blank in the extracted input where it is to be derived; set it explicitly (e.g. `major`) only where the rig braced or loaded the member to force a non-default axis. Provenance recorded in `buckling_axis_source`. |
| `buckling_axis_source` | Computed | categorical | — | Provenance of `buckling_axis`. Allowed values: `reported` (stated by the source), `symmetric` (SHS/CHS, recorded as `-`), `derived` (asymmetric default to minor axis). |
| `w_0` | Optional | float | mm | Initial global geometric imperfection amplitude (maximum bow). Signed where the source reports a direction. Notation changes across sources: w0, omega_g, delta_v, delta_mid, e0. |
| `w_e` | Optional | float | mm | Artificially applied initial loading eccentricity introduced by researchers during testing to achieve a specific target imperfection (e.g., L/1000). Signed where the source reports a direction. Where researchers tested concentrically or did not actively apply an eccentricity, this is populated as 0.0. |
| `w_0_1` | Optional | float | mm | First-plane geometric bow for sections measured biaxially (SHS/CHS). Stored with the source's sign. Component of the biaxial imperfection resultant. |
| `w_e_1` | Optional | float | mm | First-plane eccentricity contribution, sign-aligned so that `w_0_1 + w_e_1` is the net first-plane offset. For Rasmussen, whose paper defines the net as `|v0 - e0|`, this equals `-e0`. |
| `w_0_2` | Optional | float | mm | Second-plane (orthogonal) geometric bow for biaxially measured sections. |
| `w_e_2` | Optional | float | mm | Second-plane eccentricity contribution, sign-aligned so that `w_0_2 + w_e_2` is the net second-plane offset. |

 
---
 
### Test Outputs
 
| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `N_u` | Mandatory | float | kN | Ultimate axial load at failure. Notation variants: Pu, Nu, FEXP, Nu,EXP. |
| `failure_mode` | Mandatory | categorical | — | Reported failure mode. Allowed values: `global_flexural`, `local`, `interactive`. Where the source does not report a mode explicitly, it is taken from the computed `inferred_failure_mode` and the judgement is noted in the source log. |
 
---
 
### Computed Properties
 
These columns are derived from the mandatory raw inputs. They are never entered manually. They are populated by running the reusable functions in /src (`features.add_features` then `classify.classify`). The provenance flags `Le_source` and `buckling_axis_source` (listed above with their fields) are also generated here.
 

| Column | Tier | Type | Units | Formula | Description |
|---|---|---|---|---|---|
| `A` | Computed | float | mm^2 | See section formulae | Cross-sectional area. |
| `I_major` | Computed | float | mm^4 | See section formulae | Second moment of area about the major principal axis. Assigned by magnitude, so `I_major >= I_minor` always holds. |
| `I_minor` | Computed | float | mm^4 | See section formulae | Second moment of area about the minor principal axis. Assigned by magnitude, so `I_minor <= I_major` always holds. |
| `R` | Computed | float | mm | sqrt(I_crit / A) | Radius of gyration about the buckling axis. `I_crit` is `I_major` when `buckling_axis == major`, otherwise `I_minor` (so `minor` and the symmetric `-` both resolve to `I_minor`, which equals `I_major` for symmetric sections). |
| `lambda` | Computed | float | — | Le / R | Standard (dimensional) slenderness ratio. |
| `N_cr` | Computed | float | kN | (pi^2 * E0 * I_crit) / Le^2 | Euler elastic critical buckling load. |
| `N_y` | Computed | float | kN | A * sigma_02 | Squash (yield) load of the gross cross-section. |
| `lambda_bar` | Computed | float | — | sqrt(N_y / N_cr); equivalently (Le / (pi * R)) * sqrt(sigma_02 / E0) | Non-dimensional slenderness per Köllner, Gardner & Wadee (2023). The two formulae are asserted equal at build time as a unit-error guard. |
| `chi` | Computed | float | — | N_u / N_y | Experimental strength reduction factor. |
| `epsilon` | Computed | float | — | sqrt((235 / sigma_02) * (E0 / 210000)) | Material factor per EN 1993-1-4 Table 5.2. |
| `cs_slenderness` | Computed | float | — | See EN 1993-1-4 Table 5.2 | Slenderness (c/t for SHS/RHS/I, d/t for CHS) of the **governing** plate, i.e. the plate ranked highest by (class, utilisation). Because the web and flange of an I-section carry different EN limits, the governing plate is selected by utilisation rather than by the largest raw ratio. |
| `cs_slenderness_norm` | Computed | float | — | (c/t) / (class-3 limit) of the governing plate | Normalised plate utilisation of the governing plate. `> 1` means the plate is past its Class 3 limit (Class 4). Cross-section-agnostic, so directly comparable across section types; preferred over raw `cs_slenderness` as an ML feature. |
| `section_class` | Computed | integer | — | See EN 1993-1-4 Table 5.2 | EN 1993-1-4 cross-section class under uniform compression. Allowed values: `1`, `2`, `3`, `4`, or null. Null for `Angle` (excluded from classification) and where geometry needed for the check (e.g. `t`) is missing. |
| `lambda_0` | Computed | float | — | See EN 1993-1-4 Table 5.3 | Limiting slenderness for flexural buckling. `0.40` for hollow and rolled / cold-formed open sections; `0.20` for welded open sections (forming route `welded` or `laser_welded`). |
| `inferred_failure_mode` | Computed | categorical | — | From `section_class` and `lambda_bar` | Failure mode inferred where `failure_mode` is not reported. Allowed values: `global_flexural`, `yielding`, `local`, `interactive`, `unknown`. `interactive` corresponds to the reported `interactive` category; `unknown` is used for excluded angles or where `section_class` could not be determined. |
| `global_buckling_eligible` | Computed | boolean | — | From `section_class` and `inferred_failure_mode` | `True` for a clean global flexural buckling data point. `False` for any Class 4 section or any row whose inferred mode is `local`, `interactive`, or `unknown`. Use this to filter the Stage 1 / Stage 2 training set, keeping `master.csv` complete rather than deleting rows. Stocky `yielding` (Class 1-3) points are retained. |
| `failure_mode_conflict` | Computed | boolean | — | From `failure_mode` and `inferred_failure_mode` | `True` where a row reported as `global_flexural` is computed to be pure `local` buckling (stocky Class 4). Flags likely manual-extraction scope-creep mislabels for review. |
| `w_total` | Computed | float | mm | see Description | Total effective global imperfection, stored as a non-negative magnitude. **Planar sections** (single bending plane): `abs(w_0 + w_e)` — the magnitude of the net midspan offset (bow plus eccentricity, sign-aligned), which avoids the negative totals a raw signed sum produces when the two oppose. **Symmetric sections measured biaxially** (SHS/CHS with the four `w_*_1/2` components present): the resultant of the two orthogonal net offsets, `sqrt((w_0_1 + w_e_1)^2 + (w_0_2 + w_e_2)^2)`, matching the Rasmussen paper's `sqrt((v01-e01)^2 + (v02-e02)^2)`. Required for the Stage 2 ML model to predict β from the actual imperfection state. |
---
 
## General Notes
 
**Units convention:** All stresses in MPa, all lengths and dimensions in mm, all loads in kN.
 
**Null handling:** Optional columns are left null where not reported. 

**Column extension:** New columns may be added as additional sources are integrated. Any new column is added to this dictionary before being added to the CSV. The tier (mandatory / optional / computed) is declared at the time of addition.
 
**Source log cross-reference:** Any judgement call made during data entry (inferred failure mode, imperfection notation interpretation, inferred stainless family, n flagged as derived) is to be recorded in `data/source_log.csv` with the relevant `source_id` and a brief note. Provenance for `Le` and `buckling_axis` is now captured automatically in the `Le_source` and `buckling_axis_source` columns rather than the source log; record only non-default overrides (e.g. a braced specimen forced onto its major axis) as a note.

---

## Changelog

**v1.4 — 24/06/2026**
- Added biaxial imperfection components `w_0_1`, `w_e_1`, `w_0_2`, `w_e_2` for SHS/CHS sections measured in two principal planes (Rasmussen). `w_total` now uses the resultant of the two orthogonal net offsets for these sections.
- `cs_slenderness`: redefined as the slenderness of the **governing** plate, selected by (class, utilisation) so that the web/flange limit difference for I-sections is handled correctly (previously took the largest raw ratio).
- Added `cs_slenderness_norm` (governing-plate utilisation; `>1` == Class 4).
- Added `global_buckling_eligible` (scope filter excluding Class 4 / local / interactive / unknown) and `failure_mode_conflict` (reported-global vs inferred-pure-local mislabel flag).
- Sign convention for `w_e` / `w_e_1` / `w_e_2`: stored so that `w_0 + w_e` reproduces the source's net imperfection. For Rasmussen the paper defines the net as `|v0 - e0|`, so the eccentricity is stored as `-e0`.

**v1.3 — 24/06/2026**
- `forming_route`: added `welded` to the allowed vocabulary (generic welded open section); it selects the welded outstand limits and the `0.20` flexural plateau, fixing welded I-sections previously defaulting to `0.40`.
- `buckling_axis`: added `-` to the allowed values for perfectly symmetric sections (SHS/CHS); documented the reported → symmetric → derived-minor resolution now performed by `features.add_features`.
- Added `buckling_axis_source` (computed provenance: `reported` / `symmetric` / `derived`).
- `Le`: derivation `Le = k · L` from `boundary_condition` is now performed automatically in the pipeline; added `Le_source` (computed provenance: `reported` / `derived`).
- `w_total`: formula changed from `(w_0 + w_e)` to `abs(w_0 + w_e)` (non-negative magnitude); added the CHS biaxial-resultant rule.
- `I_major` / `I_minor`: clarified that labels are assigned by magnitude so `I_major >= I_minor` always holds.
- Renamed dictionary entry `cross_section_type` → `section_type` to match the dataset and `/src`.
- `lambda_bar`: noted the build-time dual-formula equality guard.