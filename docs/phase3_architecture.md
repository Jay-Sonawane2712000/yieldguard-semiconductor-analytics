# Phase 3 analytical architecture

## Persisted contracts

| Relation | Grain | Key | Purpose |
| --- | --- | --- | --- |
| `dim_pca_model` | one fitted model | `model_version` | Fitting population, methods, component rule, versions, and frozen limits |
| `dim_pca_feature` | model × eligible measurement | `model_version, sensor_id` | Reference median, imputed mean, and scale |
| `fact_pca_loading` | model × component × measurement | all three fields | Auditable loadings and component variance |
| `fact_multivariate_alert` | production entity | `entity_id` | T-squared/Q scores, limits, flags, split, and versions |
| `fact_alert_contribution` | entity × statistic × retained rank | `contribution_id` | Ten stored measurement contributions for each score type |
| `mart_multivariate_alert_history` | production entity | inherited entity key | Stable multivariate alert history contract |
| `mart_alert_overlap` | production entity | inherited entity key | Label-free univariate/multivariate comparison |
| `mart_alert_method_summary` | split | `split` | Counts by monitoring method without outcomes |

`sql/transformations/040_pca_monitoring.sql` materializes versioned artifacts, scores, and contributions. `sql/marts/020_phase3_marts.sql` exposes stable downstream views.

## Reconciliation controls

- 1,567 score rows equal 1,567 distinct production entities.
- 31,340 contribution rows equal `1,567 × 2 × 10`, with ranks 1 through 10 for every entity/statistic pair.
- 53,240 loading rows equal `440 × 121`.
- Full T-squared contribution sums have maximum relative error `7.39e-16`; Q/SPE sums reconcile exactly in the observed build.
- SQL and Python split-level score-alert counts agree.
- The model record declares `fit_split = reference` and `reference_entity_count = 940`.

Generated artifacts live under `data/processed/phase3/` and remain excluded from Git. The DuckDB database is also generated locally.
