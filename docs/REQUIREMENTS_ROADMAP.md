# Requirements-to-phase roadmap

The approved specification is canonical in `PROJECT_PLAN.md`. This roadmap makes execution and phase boundaries auditable without replacing it.

| Phase | Objective and included scope | Key acceptance evidence | Excluded until later | Likely commit boundaries |
|---|---|---|---|---|
| 1 | Repository foundation; UCI provenance/license; deterministic acquisition and parsing; label/timestamp normalization; feasibility and measurement-trust audits; chronological split comparison; evaluation-design choice; initial DuckDB entity, wide-measurement, and sensor tables; project memory and roadmap | Checksums and source manifest; exact counts; machine-readable quality/exclusion outputs; split counts and boundaries; leakage assertions; DuckDB grain checks; ingestion/split tests | Monitoring rules/signals, PCA, associations, models, policies, dashboard, final report | Foundation and memory; ingestion/audit implementation; evidence/docs |
| 2 | Complete hybrid wide/long SQL architecture and marts; freeze label-blind training-only measurement selection; implement I-MR and EWMA; traceable signals and reconciliation | Reproducible selection; reference-only limits; signal traceability; missingness/autocorrelation notes; SQL/Python reconciliation; focused tests | PCA, outcome associations, predictive models, final policy | SQL architecture; sensor selection; univariate monitoring |
| 3 | Training-only PCA preprocessing; T-squared and Q/SPE; frozen limits; top-ten contributions for each statistic/entity; alert comparison; optional separate Tier B simulation | No final-test fitting; score/limit math; contribution shapes, ranks, and reconciliations; separate simulation evidence if used | Associations, models, final-test policy evaluation | PCA monitoring; contributions; optional simulation |
| 4 | Freeze development choices; development-only associations with effect sizes, approximate intervals, BH and dependence sensitivity; logistic and HistGradientBoosting ranking; baselines; calibration; budget analysis; frozen-budget decision commit before final evaluation; review queue | Leakage assertions; <=6 configurations/model; PR-AUC/calibration/counts/uncertainty; auditable decision-before-test Git order; queue reconciliation | Dashboard/report/memo production | Frozen design; associations; models/baselines; budget decision; final evaluation/queue |
| 5 | Dashboard marts and exactly three Power BI pages; reconciliations; HTML statistical report; engineering memo; dictionaries, methods, limitations, architecture, screenshots, interview guide | Inspected dashboard or explicit user-assisted gap; cross-system totals; rendered HTML; memo tied to frozen policy; current screenshots and docs | New analytical features | Decision marts; report/memo; dashboard/docs |
| 6 | Final Tier A, leakage, security, reproducibility, documentation, screenshot, architecture, Git-history, and release audit | Clean reproduction; no restricted/generated artifacts or secrets; accurate README and evidence-based resume bullets; explicit limitations/unverified items | Any new feature without approval | Audit repairs; release documentation |

## Phase 1 implementation units

1. Initialize project memory, configuration, packaging, ignore rules, README/data documentation, and provenance record.
2. Implement idempotent UCI archive acquisition with checksums and safe extraction.
3. Implement strict source parsing, label normalization, timestamp validation, and source-level validation.
4. Implement training-period measurement-quality profiling and machine-readable exclusion reasons without silently dropping measurements.
5. Compare tie-safe chronological candidate allocations, count failures, and select holdout or the approved rolling fallback using configured feasibility thresholds.
6. Persist initial DuckDB tables and generated Phase 1 audit artifacts outside Git.
7. Add synthetic unit/integration coverage, run lint/tests/pipeline, inspect outputs, and document the verified checkpoint.

## Phase 1 acceptance checks

- Acquisition is repeatable and the downloaded archive/raw files have SHA-256 checksums.
- Source parsing yields one aligned label/timestamp row per measurement row; only documented labels are accepted.
- Timestamps parse completely, chronological ordering is deterministic, and ties are never split across periods.
- Exact class, duplicate, missingness, quality, temporal coverage, and candidate-period counts are recorded.
- Every measurement has a quality record; every excluded measurement has one or more explicit reasons; exclusion decisions use the reference/training period only.
- The chosen evaluation design follows configured feasibility criteria, retains a final directional block unless evidence requires escalation, and documents sparse-failure uncertainty.
- Initial DuckDB grains/keys/row counts reconcile with Python outputs.
- Targeted tests, full pytest, Ruff, and a clean Phase 1 rebuild pass in the current environment.
