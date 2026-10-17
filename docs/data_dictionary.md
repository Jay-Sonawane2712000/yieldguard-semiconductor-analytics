# Analytical data dictionary

| Relation | Grain | Primary identifiers | Purpose |
| --- | --- | --- | --- |
| `fact_production_entity` | production entity | `entity_id` | Timestamp, chronological order, split, mapped outcome. |
| `dim_sensor` | anonymous measurement | `sensor_id` | Quality evidence, eligibility, exclusion, selection status. |
| `fact_sensor_measurement` | entity × measurement | `entity_id`, `sensor_id` | Long-form observed value and missingness. |
| `fact_spc_signal` | entity × selected sensor × method | `signal_id` | I, MR, and EWMA statistics, limits, rules, alerts. |
| `fact_multivariate_alert` | entity | `entity_id` | T-squared/Q statistics, thresholds, alert flags. |
| `fact_alert_contribution` | entity × statistic × ranked sensor | `contribution_id` | Top mathematical contributions and shares. |
| `fact_measurement_association` | eligible sensor | `sensor_id` | Development-only effects, intervals, tests, adjustments, evidence comparison. |
| `fact_model_evaluation` | model × final metric | model/configuration/metric | Held-out estimates and uncertainty. |
| `fact_model_calibration` | model × final calibration bin | model/configuration/bin | Observed versus predicted failure rates. |
| `fact_policy_evaluation` | model × period × policy | model/configuration/period/policy | Workload, detected/missed counts, precision/recall and intervals. |
| `fact_engineering_review_queue` | final entity | `entity_id` | Frozen rank, review flag, alerts, contributors, quality warning, outcome, reasons. |

The ten `mart_dashboard_*` relations are presentation contracts defined in `sql/marts/040_phase5_dashboard_marts.sql`. Column types are discoverable with DuckDB `DESCRIBE`; all visible metric semantics are defined in `docs/metric_dictionary.md`.
