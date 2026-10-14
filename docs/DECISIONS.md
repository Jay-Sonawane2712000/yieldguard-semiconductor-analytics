# Material decisions

## D-001 — Preserve an untouched final directional block when feasible

- **Status:** Approved by the project plan; Phase 1 evidence pending.
- **Decision:** Prefer chronological training/reference, calibration, and untouched final-test periods. Use the approved rolling-origin fallback if a single holdout is too sparse, while retaining a latest directional block whenever statistically feasible.
- **Why:** This protects the project from temporal leakage and makes later retrospective claims auditable.
- **Alternatives:** Random splitting is prohibited. Dropping the final block requires Phase 1 evidence and explicit user approval.
- **Consequences:** Phase 1 may inspect only final-period counts, timestamps, schema, and structural quality; outcome-conditioned final-period analysis remains prohibited.

## D-002 — Use pandas as the primary dataframe library

- **Status:** Agent decision within approved scope.
- **Decision:** Use pandas for Phase 1 ingestion and audits, with DuckDB for persisted analytical tables.
- **Why:** pandas is already available, directly supports the SECOM text format, and keeps the approved stack small.
- **Alternatives:** Polars was allowed but would add another dependency without a Phase 1 benefit.
- **Consequences:** Wide operations must be written carefully to avoid unnecessary copies; later performance can be measured before any reconsideration.

## D-003 — Select the tie-safe 60/20/20 chronological holdout

- **Status:** Phase 1 agent decision under the plan’s approved evaluation gate.
- **Decision:** Use 940 reference, 314 calibration, and 313 final-test production entities, with 76, 11, and 17 failures respectively.
- **Why:** It is the first preconfigured candidate meeting the explicit minimum of 10 calibration and 10 final failures. No timestamp tie crosses a boundary.
- **Alternatives:** Three later-final-block candidates were evaluated; their final periods contain 9, 9, and 3 failures. Rolling-origin was approved as a fallback but was unnecessary because the preferred holdout is feasible.
- **Consequences:** Retain the final test untouched for Phase 4 frozen retrospective evaluation. Estimates based on 11 calibration or 17 final failures must remain directional and include uncertainty.

## D-004 — Freeze the Phase 2 monitoring-selection rule

- **Status:** Agent decision within the approved Phase 2 scope; frozen before failure association or final-test evaluation.
- **Decision:** Select 12 measurements from Phase 1 quality-eligible measurements using reference data only. Rank deterministically by the equal-weight mean of completeness percentile, temporal-coverage percentile, and a dimensionless robust-variation percentile, using average ranks for ties. Traverse that ranking by score then sensor ID and reject a candidate when its absolute reference correlation with any already selected measurement is at least 0.90.
- **Why:** Twelve is inside the approved 8–15 range and is small enough for interpretable I-MR/EWMA review. The rule rewards reliable sequential availability and variation while limiting redundant charts.
- **Alternatives:** Selecting by failure association is prohibited. Selecting every eligible measurement would be uninterpretable. A lower correlation ceiling could prevent reaching the approved range; a higher ceiling would preserve redundant signals.
- **Consequences:** Version `monitoring-selection-v1` is label-blind and frozen. Later outcome analysis must not revise the selected set.

## D-005 — Use reference-fitted classical I-MR and time-varying EWMA limits

- **Status:** Agent decision within the approved Phase 2 scope.
- **Decision:** Estimate the center and short-term sigma from reference-period adjacent moving ranges (`d2 = 1.128`). Use three-sigma Individuals limits, `D4 = 3.267` for Moving Range, and observation-indexed EWMA limits with lambda 0.20 and L 3.0.
- **Why:** These are transparent, standard formulas that can be audited and tested. Time-varying EWMA limits match the approved configuration and reflect startup behavior.
- **Alternatives:** Steady-state EWMA limits were approved but would ignore startup narrowing. Supplementary run rules remain optional and are not added in Phase 2.
- **Consequences:** Limits use reference measurements only. Missing observations are not interpolated, do not update EWMA state, and break Moving Range adjacency. Autocorrelation can inflate nominal false-alarm rates and must be reported.

## D-006 — Freeze reference-only empirical PCA monitoring

- **Status:** Agent decision within the approved Phase 3 scope; frozen before outcome association or final-test evaluation.
- **Decision:** Fit median imputation, standard scaling, and PCA on the 940-entity reference period using all 440 Phase 1 quality-eligible measurements. Retain the fewest components reaching at least 90% reference explained variance. Set separate T-squared and Q/SPE limits to the reference empirical 99th percentile using the conservative `higher` sample quantile.
- **Why:** The rule is deterministic, label-blind, robust to missing measurement cells, and makes no distributional assumption that the sparse, anonymous public dataset cannot support.
- **Alternatives:** Parametric T-squared/Jackson Q limits and bootstrap limits were allowed, but empirical limits are simpler to audit and align directly with the observed reference distribution. Fitting on calibration or final data is prohibited.
- **Consequences:** Model `pca-reference-v1` retains 121 components and 90.1631% reference variance. Threshold version `pca-empirical-reference-q99-v1` is frozen at T-squared 551.588214 and Q/SPE 111.311774. Later outcome analysis must not revise preprocessing, component count, or limits.
