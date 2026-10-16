# Phase 4 analytical architecture

## Separable execution gates

1. `yieldguard phase4-calibrate` fits the predeclared candidates on reference and evaluates them on calibration. It cannot query final entities.
2. The selected model is recorded and committed before `yieldguard phase4-develop` combines reference and calibration for associations.
3. `yieldguard phase4-develop` creates development associations and calibration budget evidence. It records zero final entities accessed.
4. The headline budget is recorded in `config/project.yaml` and `docs/DECISIONS.md` and committed.
5. Only then does `yieldguard phase4-final` query final outcomes, fit the frozen champion on development, score the final block, and build the queue.

Commit `ccfaf2f` freezes the 10% budget before the final-evaluation implementation and results.

## Persisted contracts

| Relation | Grain | Key or reconciliation | Purpose |
| --- | --- | --- | --- |
| `audit_phase4_candidate_metric` | model configuration × calibration period | 10 rows including baselines | Bounded candidate and baseline comparison |
| `fact_measurement_association` | eligible measurement | `sensor_id`, 440 rows | Development-only effects, intervals, tests, corrections, and evidence comparison |
| `fact_failure_risk` | model/baseline × final entity | `model, entity_id`, 939 rows | Scores, ranks, probabilities where applicable, and frozen-budget flags |
| `fact_model_evaluation` | model/baseline × final metric | model/configuration/metric | PR-AUC, ROC-AUC, calibration summaries, counts, and uncertainty |
| `fact_model_calibration` | probability model × final calibration bin | model/configuration/bin | Five-bin observed-versus-predicted calibration evidence |
| `fact_policy_evaluation` | model/baseline × period × policy | scenario grain | Workload, confusion counts, precision/recall/F2, and uncertainty |
| `fact_engineering_review_queue` | final production entity | `entity_id`, 313 rows | Frozen model rank, review status, alerts, contributions, quality warnings, outcome, and reason codes |

Stable views are defined in `sql/marts/030_phase4_marts.sql`.

## Leakage and reconciliation controls

- Candidate fitting uses 940 reference entities; selection uses 314 calibration entities.
- Associations use 1,254 development entities and explicitly query only reference/calibration splits.
- Final fitting uses development only, with preprocessing internal to the chosen estimator.
- Candidate searches contain four complete configurations per approved family, below the limit of six.
- The final score table contains `313 × 3 = 939` unique model/entity rows.
- The review queue contains 313 unique entities, exactly 32 marked for the ceiling-rounded 10% budget.
- Queue outcomes reconcile to 17 failures, including 2 among reviewed entities.
- Policy counts and queue totals agree.

Generated outputs and the DuckDB database remain excluded from Git.
