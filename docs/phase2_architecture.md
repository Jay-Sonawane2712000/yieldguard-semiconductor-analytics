# Phase 2 analytical architecture

## Persisted tables

| Relation | Grain and key | Purpose |
|---|---|---|
| `fact_production_entity` | One row per `entity_id` | Timestamp, stable chronology, normalized outcome, split, source version |
| `measurements_wide` | One row per `entity_id` | Efficient wide PCA/model operations in later phases |
| `fact_sensor_measurement` | One row per `entity_id, sensor_id` | Auditable long-form raw measurements, missingness, timestamps, and split |
| `dim_sensor` | One row per `sensor_id` | Quality evidence plus monitoring selection status/version |
| `dim_monitoring_sensor` | One row per `sensor_id` | Ranking components, reason codes, selected order, and correlation decision evidence |
| `dim_spc_limit` | One row per selected `sensor_id` | Reference-fitted I-MR parameters and sigma estimate |
| `fact_spc_signal` | One row per `entity_id, sensor_id, method` | Statistic, center, limits, signal flag, rule, and limit version |
| `fact_sensor_autocorrelation` | One row per selected `sensor_id` | Reference lag-1 pair count and correlation |

`fact_sensor_measurement` has 924,530 rows (1,567 entities × 590 measurements), 924,530 distinct compound keys, and 41,951 explicitly missing rows. `fact_spc_signal` has 56,412 rows (1,567 × 12 × 3 methods), 56,412 distinct `signal_id` values, and 366 unavailable statistics caused by first-range or missing-value behavior. No unavailable statistic is marked as a violation.

## Marts

- `mart_data_trust` — stable Phase 1/2 counts and timestamp coverage.
- `mart_univariate_alert_history` — dashboard-ready traceable I, MR, and EWMA history.
- `mart_spc_alert_summary` — period/measurement/method availability and alert rates.
- `mart_univariate_entity_summary` — one row per production entity with I-MR measurement count, EWMA measurement count, total signals, and any-signal flag. This supports the fixed label-blind monitoring baseline in Phase 4.

Power BI will connect to documented marts rather than intermediate Python objects. The rebuildable DuckDB file remains excluded from Git.

## SQL/Python reconciliation

The Phase 2 command fails if:

- long-table rows or compound keys differ from `entity_count × measurement_count`;
- long-table missing rows differ from the parsed pandas source;
- SPC rows or signal IDs differ from `entity_count × selected_count × 3`;
- SQL period/method signal and availability counts differ from Python groupings.

All four checks passed on the Phase 2 build.
