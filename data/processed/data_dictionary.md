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
| `study_id` | Mandatory | string | — | Identifier for the experimental campaign or FEA batch. Specimens sharing the same steel batch and test setup share a `study_id`. This is the grouping key for grouped cross-validation — specimens within one `study_id` must never be split across train and test sets. Where a paper reports a single batch, `study_id` equals `source_id`. Where a paper reports multiple clearly distinct batches or series, append a letter: e.g. `afshan2013_A`, `afshan2013_B`. |
| `data_type` | Mandatory | categorical | — | Provenance of the row. Allowed values: `experimental`, `FEA`. For studies that report both, assign per row.|

---

### Material Properties

All material properties are per batch from coupon tests unless otherwise noted. Values are duplicated to every specimen row belonging to that batch.

| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `material_grade` | Mandatory | string | — | Steel grade or alloy designation as reported by the source, e.g. `1.4301`, `6061-T6`, `S690`. |
| `material_type` | Mandatory | categorical | — | Material family. Allowed values: `stainless_steel`, `aluminium`, `cold_formed_steel`. |
| `E0` | Mandatory | float | MPa | Initial (elastic) Young's modulus from coupon tests. |
| `sigma_02` | Mandatory | float | MPa | 0.2% proof stress from coupon tests. Notation variants in sources: `f₀.₂`, `σ₀.₂`, `fy`. |
| `n` | Mandatory | float | — | Ramberg–Osgood strain hardening exponent. See `n_source` for provenance flag. |
| `n_source` | Mandatory | categorical | — | Provenance of `n`. Allowed values: `measured` (fitted directly from coupon stress–strain data), `derived` (back-calculated from two stress points, e.g. via `n = ln2 / ln(σ₀.₂/σ₀.₁)`)- derived values introduce a fabricated algebraic dependency and must be distinguishable from measured values at all modelling stages. |
| `sigma_u` | Optional | float | MPa | Ultimate tensile strength from coupon tests. Notation variants: `fu`, `σu`. |
| `sigma_10` | Optional | float | MPa | 1.0% proof stress. Present in stainless steel sources only. Used in two-stage Ramberg–Osgood models. |
| `n_prime` | Optional | float | — | Secondary Ramberg–Osgood hardening exponent for two-stage model. Present in stainless steel sources only. Notation variants: `n'`, `m`, `mu`. |

---

### Geometric Properties

Raw cross-section dimensions are stored per specimen. Derived section properties (A, I, r) are computed programmatically — see Computed section.

| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `cross_section_type` | Mandatory | categorical | — | Cross-section shape. |
| `b` | Mandatory | float | mm | External width of the cross-section. For CHS, store the outer diameter here and leave `h` null. |
| `h` | Mandatory | float | mm | External height of the cross-section. Null for CHS. |
| `t` | Mandatory | float | mm | Wall thickness. For sections with distinct flange and web thicknesses, store the governing (minimum) thickness here and note the variant in the source log. |
| `L` | Mandatory | float | mm | Physical member length as reported by the source. |
| `boundary_condition` | Mandatory | categorical | — | End condition of the column. Allowed values: `pin-pin`, `fixed-fixed`, `fixed-pin`, `fixed-free`. |
| `Le` | Optional | float | mm | Effective buckling length. Populate directly where reported by the source. Where not reported, derived from `L` using the standard effective length factor for the given `boundary_condition` (k = 1.0 pin-pin, k = 0.5 fixed-fixed, k = 0.7 fixed-pin, k = 2.0 fixed-free) and documented derivation in `source_log.csv`. |
| `w0` | Optional | float | mm | Initial global geometric imperfection amplitude (maximum bow). Notation is highly variable across sources: `w₀`, `ωg`, `δv`, `Δmid`, `e₀`. |

---

### Test Outputs

| Column | Tier | Type | Units | Description |
|---|---|---|---|---|
| `N_u` | Mandatory | float | kN | Ultimate axial load at failure. Notation variants: `Pu`, `Nu`, `FEXP`, `Nu,EXP`. Convert to kN if reported in N (÷1000). |
| `failure_mode` | Mandatory | categorical | — | Observed or reported failure mode. Allowed values: `global_flexural`, `local`, `interactive`. Where the source does not distinguish modes explicitly, infer from slenderness ratio and note as `inferred` in the source log. Rows where failure mode cannot be reliably determined should be flagged and excluded from modelling. |

---

### Computed Properties

These columns are derived programmatically from the mandatory raw inputs. They are never entered manually. Populate them by running the computation notebook after raw data entry is complete.

Assumed cross-section formulae (thin-walled approximation, valid for typical hollow sections):
- **SHS / RHS:** `A = 2t(b + h) − 4t²` ; `I = (bh³ − (b−2t)(h−2t)³) / 12` about weak axis
- **CHS:** `A = π/4 × (b² − (b−2t)²)` ; `I = π/64 × (b⁴ − (b−2t)⁴)`

| Column | Tier | Type | Units | Formula | Description |
|---|---|---|---|---|---|
| `A` | Computed | float | mm² | See above | Cross-sectional area. |
| `I` | Computed | float | mm⁴ | See above | Second moment of area about the weak axis. |
| `r` | Computed | float | mm | `√(I / A)` | Radius of gyration. |
| `lambda_bar` | Computed | float | — | `(Le / (π × r)) × √(σ₀.₂ / E₀)` | Non-dimensional slenderness per Köllner, Gardner & Wadee (2023). Requires `Le` — use derived `Le` where not reported directly. |

---

## General Notes

**Units convention:** All stresses in MPa, all lengths and dimensions in mm, all loads in kN. Convert at point of entry — do not store mixed units.

**Null handling:** Optional columns are left null (empty cell in CSV) where not reported. Do not substitute zeroes for nulls.

**Column extension:** New columns may be added as additional sources are integrated. Any new column must be added to this dictionary before being added to the CSV. The tier (mandatory / optional / computed) must be declared at the time of addition.

**Source log cross-reference:** Any judgement call made during data entry (inferred failure mode, derived Le, imperfection notation interpretation, n flagged as derived) must be recorded in `data/source_log.csv` with the relevant `source_id` and a brief note.