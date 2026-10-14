# Phase 2 completion report

## Outcome

**Complete — acceptance criteria passed.** The hybrid DuckDB/SQL architecture is complete for Phase 2, the 12-measurement label-blind selection is frozen, reference-only I-MR and EWMA monitoring is implemented, all signals are traceable and versioned, SQL/Python totals reconcile, and all tests pass. Phase 3 has not started.

## What changed and why it matters

- Added the complete long-form measurement fact while preserving the wide representation.
- Added a deterministic, reference-only selection module and auditable reason codes for all 590 measurements.
- Added classical Individuals/Moving Range and time-varying EWMA calculations with explicit missing and timestamp-gap behavior.
- Added reference-fitted limit, autocorrelation, alert-history, period-summary, and entity-workload relations.
- Added SQL transformations and four stable marts for later dashboard and policy work.
- Expanded automated coverage from 7 to 12 tests, including deterministic selection, redundancy, formulas, missingness, and end-to-end SQL grain checks.

This matters because later PCA, models, and review policies can reuse a versioned monitoring foundation without selecting measurements from failure outcomes or recomputing limits from future data.

## Acceptance criteria and evidence

| Criterion | Evidence |
|---|---|
| Selection is reproducible | Two real builds returned the same ordered 12-measurement set; deterministic tests pass |
| Labels are not used | Selection accepts measurements, split assignments, quality metadata, and config only; no outcome field is passed |
| Limits use reference data only | All 12 limit records use 940 reference observations and 939 adjacent reference ranges |
| Alerts are traceable | 56,412 unique signal IDs include entity, measurement, method, statistic, limits, rule, split, and version |
| SQL and Python reconcile | 924,530 long keys, 41,951 missing rows, signal keys, and period/method summaries match exactly |
| Missing behavior is explicit | No interpolation; missing I/EWMA statistics cannot signal; MR does not bridge missing values |
| Autocorrelation caveat is documented | Range -0.070 to 0.475; two measurements have absolute lag-1 correlation above 0.30 |
| Tests pass | `python -m pytest`: 12 passed; `python -m ruff check src tests`: passed |

## Key outputs

- Selected measurements: `104, 499, 500, 511, 082, 010, 009, 093, 077, 080, 092, 075` using their `measurement_NNN` identifiers.
- Maximum pairwise absolute correlation within the selected set: 0.234945.
- 924,530 long measurement rows and 56,412 SPC rows.
- 1,931 sensor-level statistical signals across all periods/methods.
- Any univariate method signaled 679 reference, 173 calibration, and 190 final-period entities.

The relatively high EWMA alert volume, especially in the reference period, is evidence of nonstationarity, distributional mismatch, serial dependence, or a combination—not proof of a confirmed process fault. Phase 2 does not call these false positives because it does not compare them with outcomes.

## Checks actually run

- `python -m pytest` — 12 passed in 2.46 seconds on the final run.
- `python -m ruff check src tests` — all checks passed.
- `yieldguard build-phase2` — completed and reran idempotently with the same selected set and counts.
- Read-only DuckDB checks — table/view presence; long and signal row/key counts; missing counts; selection reason totals; version counts; positive fitted sigma; signal summaries; no missing statistic marked as a violation.

## Files changed

Configuration, decisions, project status, CLI, sensor-selection and SPC modules, Phase 2 orchestration, three SQL transformation scripts, Phase 2 marts, unit/integration tests, README, and Phase 2 method/architecture/evidence documentation.

## Not verified or deferred

- Alert/failure overlap, false-positive counts, policy workload by observed outcome, and predictive comparisons are intentionally deferred until Phase 4.
- PCA, T-squared, Q/SPE, and contribution analysis belong to Phase 3 and were not started.
- Dashboard interaction and Power BI reconciliation belong to Phase 5.
- The classical control-limit assumptions are imperfect under observed autocorrelation and apparent reference nonstationarity; a statistical alert remains an investigation prompt.

## Material decisions and tradeoffs

- Twelve measurements balance interpretability with coverage.
- A 0.90 redundancy ceiling is permissive enough to reach the target, while the resulting set is substantially less correlated in practice.
- Time-varying EWMA limits preserve startup behavior but can generate clustered signals under serial dependence or shifts.
- Sequence-based charts do not duration-weight irregular timestamp gaps because no justified process cadence is available.

## Interview explanation

The key story is that selection is frozen without failure labels, and limits are learned only from earlier reference measurements. I-MR catches large individual changes and adjacent jumps; EWMA accumulates smaller sustained changes. Every statistical alert retains the exact statistic, limit, rule, measurement, entity, and version needed for engineering review.

## Repository status

Phase 2 commits and push are pending the final commit review. The next approved phase is Phase 3, but work must stop here until explicit user approval.
