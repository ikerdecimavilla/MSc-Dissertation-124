# Master Dataset — Data Dictionary

**Version:** 1.7  
**Date:** 06/07/2026  
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
| `reported_failure_mode` | Mandatory | categorical | — | Source-reported failure mode, stored as given by the source. **This column is the ground truth for all scope and audit decisions.** Preferred values: `global_flexural`, `local`, `interactive`, `yielding`, `torsional`, `flexural_torsional`, `distortional`. Source notation variants (e.g. `F`, `FT`, `local+global`, hyphenated forms) are normalised on the fly by `classify.normalise_mode` before use; the stored string is not rewritten. Left blank where the source does not report a mode — only then does the pipeline fall back to the computed `inferred_failure_mode` (see `classify._effective_mode`). Any torsional or distortional participation excludes the row from the flexural training set (see `flexural_scope`). (Renamed from `failure_mode` in v1.6; extracted input CSVs may still use the legacy header `failure_mode`, which `build.py` maps automatically.) |
 
---
 
### Computed Properties
 
These columns are derived from the mandatory raw inputs. They are never entered manually. They are populated by running the reusable functions in /src in the pipeline order `features.add_geometry` → `classify.classify_sections` → `features.add_mechanics` → `classify.infer_failure_modes` (orchestrated by `build.py`). The split is required because the Class 4 effective area feeds the squash load, which in turn feeds `lambda_bar`, which the failure-mode inference needs. The provenance flags `Le_source` and `buckling_axis_source` (listed above with their fields) are also generated here.
 

| Column | Tier | Type | Units | Formula | Description |
|---|---|---|---|---|---|
| `A` | Computed | float | mm^2 | See section formulae | Gross cross-sectional area. |
| `I_major` | Computed | float | mm^4 | See section formulae | Second moment of area about the major principal axis. Assigned by magnitude, so `I_major >= I_minor` always holds. |
| `I_minor` | Computed | float | mm^4 | See section formulae | Second moment of area about the minor principal axis. Assigned by magnitude, so `I_minor <= I_major` always holds. |
| `R` | Computed | float | mm | sqrt(I_crit / A) | Radius of gyration about the buckling axis (gross section). `I_crit` is `I_major` when `buckling_axis == major`, otherwise `I_minor` (so `minor` and the symmetric `-` both resolve to `I_minor`, which equals `I_major` for symmetric sections). |
| `N_cr` | Computed | float | kN | (pi^2 * E0 * I_crit) / Le^2 | Euler elastic critical buckling load. Always computed on gross section properties, including for Class 4 sections (EN 1993-1-1 6.3.1.3 convention). |
| `epsilon` | Computed | float | — | sqrt((235 / sigma_02) * (E0 / 210000)) | Material factor per EN 1993-1-4 Table 5.2. |
| `cs_slenderness_norm` | Computed | float | — | (c/t) / (class-3 limit) of the governing plate | Normalised plate utilisation of the governing plate, i.e. the plate ranked highest by (class, utilisation). `> 1` means the plate is past its Class 3 limit (Class 4). Cross-section-agnostic, so directly comparable across section types. (The raw `cs_slenderness` c/t column was removed in v1.5; the ratio is recoverable from the geometry columns.) |
| `section_class` | Computed | integer | — | See EN 1993-1-4 Table 5.2 | EN 1993-1-4:2006 cross-section class under uniform compression. Allowed values: `1`, `2`, `3`, `4`, or null. Null for `Angle` (excluded from classification) and where geometry needed for the check (e.g. `t`) is missing. |
| `lambda_0` | Computed | float | — | See EN 1993-1-4 Table 5.3 | Limiting slenderness for flexural buckling. `0.40` for hollow and rolled / cold-formed open sections; `0.20` for welded open sections (forming route `welded` or `laser_welded`). |
| `A_eff` | Computed | float | mm^2 | See Description | Effective cross-sectional area. Class 1–3: equals `A` (fully effective). Class 4 RHS/SHS/I/H: effective-width method of EN 1993-1-4:2006 clause 5.2.3 (stainless reduction factors, Eqs. 5.1–5.3; uniform compression, k_sigma = 4.0 internal / 0.43 outstand; welded vs cold outstand set selected by `forming_route`; flat widths consistent with classification, e.g. h−2t / b−2t for hollow sections). Class 4 CHS: EN 1993-1-4 has no effective-width rule for tubes, so the EN 1993-1-6:2007 meridional shell-buckling stress-design method (8.5.2 + Annex D.1.2) is used, expressed as `A_eff = chi_x * A`, with C_x = 1.0 (the long-cylinder correction embeds global column interaction, modelled separately here) and fabrication quality class B (Q = 25). Null where `section_class` is null. NB: a section a sliver past the Class 3 limit can be Class 4 yet fully effective (`A_eff = A`), because the rho = 1 point of Eq. 5.1 sits fractionally above the 30.7ε classification limit. |
| `rho_eff` | Computed | float | — | A_eff / A | Effective-area ratio; 1.0 for fully effective sections, < 1 for reduced Class 4 sections. Clean 0–1 local-slenderness ML feature. |
| `N_squash` | Computed | float | kN | A_eff * sigma_02 | Squash (cross-section) resistance on the effective-area basis, per Köllner, Gardner & Wadee (2023): P_y = A·f_y for Class 1–3 (where `A_eff = A`) and P_y = A_eff·f_y for Class 4. Replaces the gross-basis `N_y` of v1.4 (recoverable as `A * sigma_02`). |
| `lambda_bar` | Computed | float | — | sqrt(N_squash / N_cr); equivalently (Le / (pi * R)) * sqrt(sigma_02 / E0) * sqrt(A_eff / A) | Non-dimensional slenderness per Köllner, Gardner & Wadee (2023) / EN 1993-1-1 6.3.1.3, on the effective-area basis for Class 4 sections. The two formulae are asserted equal at build time as a unit-error guard. |
| `chi_exp` | Computed | float | — | N_u / N_squash | Experimental strength reduction factor on the effective-area basis (target variable for the KGW ML formulation). |
| `Delta` | Computed | float | — | sigma_02 / E0 | Material ratio Δ = f_y/E identified by KGW as governing the transition slenderness; direct model input alongside `n` and `lambda_bar`. |
| `aspect_ratio` | Computed | float | — | max(h, b) / min(h, b) | Cross-sectional aspect ratio. 1.0 for SHS (b = h) and CHS (by convention, h null). |
| `hardening_ratio` | Computed | float | — | sigma_u / sigma_02 | Strain-hardening capacity of the material. Null where `sigma_u` is not reported. |
| `chi_perfect` | Computed | float | — | KGW Eqs. 16–17, beta = 1 | KGW strength reduction factor for the perfect column, solved from chi + k·chi^n = 1/lambda_bar² (k = n·alpha_RO·E0/sigma_02) by `src/kgw.py` (verified against KGW Table 1 by `src/kgw_verification.py`). **Not capped at 1**: chi > 1 is genuine strain-hardening reserve for stocky columns. NaN where inputs are invalid or the solve failed (see `kgw_convergence_flag`). |
| `chi_kgw` | Computed | float | — | KGW Eqs. 16–17 + Eq. 19 | KGW factor with the imperfection correction beta(lambda_bar) applied inside the solve (m = beta·n) — never as a multiplier on chi. Not capped at 1. NaN on non-convergence. |
| `chi_eurocode` | Computed | float | — | EN 1993-1-4 6.3.1 | Eurocode flexural buckling curve chi = 1/(phi + sqrt(phi² − lambda_bar²)) ≤ 1, phi = 0.5(1 + alpha(lambda_bar − lambda_0) + lambda_bar²), with chi = 1 on the plateau. alpha per Table 5.3 via `classify.imperfection_factor` (0.49 everywhere except welded open sections about the minor axis: 0.76); lambda_0 reuses the validated `lambda_0` column. Grade does not select the curve — it enters only through sigma_02 inside lambda_bar. Capped at 1 per the code. |
| `N_perfect` | Computed | float | kN | chi_perfect * N_squash | Predicted perfect-column buckling load. On the A_eff basis for Class 4 automatically, via `N_squash`. |
| `N_kgw` | Computed | float | kN | chi_kgw * N_squash | Predicted KGW-corrected buckling load. |
| `N_eurocode` | Computed | float | kN | chi_eurocode * N_squash | Predicted EN 1993-1-4 design buckling resistance (characteristic, gamma_M1 = 1). |
| `kgw_convergence_flag` | Computed | boolean | — | From `kgw_batch._solve_row` | `True` where both KGW solves converged AND passed post-verification (equation residual < 1e-10, Euler bound, chi_kgw ≤ chi_perfect for lambda_bar ≥ 0.9). `False` rows carry NaN in `chi_perfect`/`chi_kgw`/`N_perfect`/`N_kgw` with the reason logged at build time; the batch never halts on individual failures. Does not gate `chi_eurocode` (closed-form). |
| `inferred_failure_mode` | Computed | categorical | — | From `section_class`, `lambda_bar` (A_eff basis) and `lambda_0` | Failure mode inferred for **every** row from Eurocode classification: Class 4 → `local` (lambda_bar ≤ lambda_0) or `interactive` (lambda_bar > lambda_0, i.e. local-global flexural); Class 1–3 → `yielding` (lambda_bar ≤ lambda_0) or `global_flexural`; `unknown` where the class or slenderness could not be determined. Scope decisions honour the reported `reported_failure_mode` (ground truth) where present and fall back to this column only where the report is missing/blank (`classify._effective_mode`). |
| `anomalous_interactive_mode` | Computed | boolean | — | From `section_class` and effective mode | `True` where a `local` or `interactive` (local-global) failure is reported/inferred for a **Class 1–3** section — the section should be fully effective, so local participation suggests premature local collapse due to experimental anomalies. Flagged for audit and excluded from `flexural_scope` pending review. |
| `flexural_scope` | Computed | boolean | — | From `section_class`, effective mode and `anomalous_interactive_mode` | `True` for rows belonging to the global flexural buckling training set: `global_flexural` and `yielding` rows, plus Class 4 `interactive` (local-global) and Class 4 `local` rows, whose local reduction is carried by `A_eff`. `False` for any torsional / flexural-torsional / distortional participation, `unknown` modes, undetermined class, and anomalous rows. Replaces the v1.4 `global_buckling_eligible` flag, which excluded all Class 4 sections; keeps `master.csv` complete rather than deleting rows. |
| `w_total` | Computed | float | mm | see Description | Total effective global imperfection, stored as a non-negative magnitude. **Planar sections** (single bending plane): `abs(w_0 + w_e)` — the magnitude of the net midspan offset (bow plus eccentricity, sign-aligned), which avoids the negative totals a raw signed sum produces when the two oppose. **Symmetric sections measured biaxially** (SHS/CHS with the four `w_*_1/2` components present): the resultant of the two orthogonal net offsets, `sqrt((w_0_1 + w_e_1)^2 + (w_0_2 + w_e_2)^2)`, matching the Rasmussen paper's `sqrt((v01-e01)^2 + (v02-e02)^2)`. Required for the Stage 2 ML model to predict β from the actual imperfection state. |
| `w_total_norm` | Computed | float | — | w_total / Le | Normalised total imperfection (dimensionless), the Stage-2 β predictor. Replaces the v1.4 `w_0_norm` / `w_e_norm` pair, which missed the biaxial-resultant case handled by `w_total`. |

---
 
## General Notes
 
**Units convention:** All stresses in MPa, all lengths and dimensions in mm, all loads in kN.
 
**Null handling:** Optional columns are left null where not reported. 

**Column extension:** New columns may be added as additional sources are integrated. Any new column is added to this dictionary before being added to the CSV. The tier (mandatory / optional / computed) is declared at the time of addition.
 
**Source log cross-reference:** Any judgement call made during data entry (inferred failure mode, imperfection notation interpretation, inferred stainless family, n flagged as derived) is to be recorded in `data/source_log.csv` with the relevant `source_id` and a brief note. Provenance for `Le` and `buckling_axis` is now captured automatically in the `Le_source` and `buckling_axis_source` columns rather than the source log; record only non-default overrides (e.g. a braced specimen forced onto its major axis) as a note.

---

## Changelog

**v1.7 — 06/07/2026**
- **Solver prediction columns** appended by the new batch stage `src/kgw_batch.py`, which runs as the final stage of `build.py` (so a rebuild always regenerates them — the dataset cannot fork): `chi_perfect`, `chi_kgw`, `chi_eurocode`, `N_perfect`, `N_kgw`, `N_eurocode`, `kgw_convergence_flag`.
- KGW chi values are intentionally **uncapped** (chi > 1 = strain-hardening reserve); the Eurocode curve is capped at 1 per the code. All N_* use `N_squash`, so Class 4 sections automatically run on the A_eff basis.
- Added `classify.imperfection_factor` (EN 1993-1-4:2006 Table 5.3 alpha mapping: 0.49 for hollow and cold-formed open sections; welded open sections 0.49 major / 0.76 minor axis), paired with the existing `lambda_0`.
- Numerical safety: three deterministic layers (input pre-validation, guarded per-row solve, post-verification of every root against the governing equation, the Euler bound and the beta-ordering rule). Failed rows carry NaN + `kgw_convergence_flag = False` and a logged reason; the batch never halts. Current build: 229/229 rows converged.
- New build guard (#10) validates the prediction columns on every rebuild.

**v1.6 — 06/07/2026**
- Renamed `failure_mode` → `reported_failure_mode` to make explicit that it is the source-reported ground truth. Extracted input CSVs may keep the legacy `failure_mode` header; `build.py` maps it automatically.
- Documented the eligibility ground-truth rule explicitly in code (`classify._effective_mode`): `flexural_scope` and `anomalous_interactive_mode` are decided from `reported_failure_mode` wherever it is populated; `inferred_failure_mode` is consulted **only** for rows whose reported mode is missing/blank. Inference never overrides an explicit report.

**v1.5 — 06/07/2026**
- **Effective area for Class 4 sections.** Added `A_eff` and `rho_eff`. Flat-element sections (RHS/SHS/I/H) use EN 1993-1-4:2006 clause 5.2.3 (stainless reduction factors, Eqs. 5.1–5.3); Class 4 CHS use the EN 1993-1-6:2007 meridional shell-buckling method (C_x = 1.0, quality class B, Q = 25), since Part 1-4 provides no tube rule. Class 1–3 sections carry `A_eff = A`.
- **Squash load basis.** `N_y` (gross) replaced by `N_squash = A_eff * sigma_02`, matching Köllner, Gardner & Wadee (2023): A·f_y for Class 1–3, A_eff·f_y for Class 4. `lambda_bar` and `chi_exp` redefined on the same basis; the build-time dual-formula guard gains the sqrt(A_eff/A) factor. `N_cr` remains on gross properties.
- **Failure-mode logic.** `inferred_failure_mode` now computed for every row (Class 4 splits into `local` / `interactive` at `lambda_0`; Class 1–3 into `yielding` / `global_flexural`). Reported `failure_mode` strings are normalised on the fly (`classify.normalise_mode`); torsional / flexural-torsional / distortional vocabulary recognised and excluded from scope.
- **New audit flags.** `anomalous_interactive_mode` (local participation on a Class 1–3 section, flagged for review) and `flexural_scope` (training-set filter: retains Class 4 local-global `interactive` and stocky Class 4 `local` rows on the A_eff basis; excludes torsional participation, `unknown`, and anomalous rows).
- **Removed columns:** `global_buckling_eligible` (excluded all Class 4 rows — superseded by `flexural_scope`), `failure_mode_conflict` (superseded by the universal inference + `anomalous_interactive_mode`), `N_y` (superseded by `N_squash`; recoverable as `A * sigma_02`), `lambda` (recoverable as `lambda_bar * pi * sqrt(E0/sigma_02) / sqrt(A_eff/A)`, collinear ML noise), `cs_slenderness` (raw c/t, superseded by `cs_slenderness_norm`), `w_0_norm` / `w_e_norm` (superseded by `w_total_norm`).
- **New ML features:** `Delta` (= sigma_02/E0, KGW transition-slenderness parameter), `aspect_ratio`, `hardening_ratio` (= sigma_u/sigma_02, nullable), `w_total_norm` (= w_total/Le, Stage-2 β predictor).
- **Pipeline restructure:** `/src` now runs `features.add_geometry` → `classify.classify_sections` → `features.add_mechanics` → `classify.infer_failure_modes` (A_eff feeds N_squash feeds lambda_bar feeds inference). `WELD_BASIS` moved to `sections.py` (shared by classification limits and effective-width reduction factors). Columns in `master.csv` are now emitted in a canonical order.
- **Known boundary quirk (documented):** EN 1993-1-4:2006 places the fully-effective point of Eq. 5.1 (lambda_p ≈ 0.5409) fractionally above the Class 3 internal limit 30.7ε (lambda_p ≈ 0.5405), so a marginally Class 4 section can be fully effective (`rho_eff = 1`), e.g. huang2013_08 at utilisation 1.0006.

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