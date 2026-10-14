CREATE OR REPLACE VIEW mart_data_trust AS
SELECT
    (SELECT COUNT(*) FROM fact_production_entity) AS entity_count,
    (SELECT COUNT(*) FROM dim_sensor) AS measurement_count,
    (SELECT COUNT(*) FROM dim_sensor WHERE quality_status = 'eligible') AS eligible_measurement_count,
    (SELECT COUNT(*) FROM dim_sensor WHERE quality_status = 'excluded') AS excluded_measurement_count,
    (SELECT COUNT(*) FROM dim_monitoring_sensor WHERE is_selected) AS monitoring_measurement_count,
    (SELECT MIN(event_timestamp) FROM fact_production_entity) AS timestamp_start,
    (SELECT MAX(event_timestamp) FROM fact_production_entity) AS timestamp_end;

CREATE OR REPLACE VIEW mart_univariate_alert_history AS
SELECT
    signal.signal_id,
    signal.entity_id,
    signal.event_timestamp,
    signal.split,
    signal.sensor_id,
    signal.method,
    signal.statistic,
    signal.center_line,
    signal.lower_control_limit,
    signal.upper_control_limit,
    signal.violation_indicator,
    signal.measurement_missing,
    signal.rule_identifier,
    signal.limit_version
FROM fact_spc_signal AS signal;

CREATE OR REPLACE VIEW mart_spc_alert_summary AS
SELECT
    split,
    sensor_id,
    method,
    COUNT(*) AS entity_count,
    COUNT(statistic) AS available_statistic_count,
    COUNT(*) FILTER (WHERE violation_indicator) AS signal_count,
    COUNT(*) FILTER (WHERE violation_indicator)::DOUBLE
        / NULLIF(COUNT(statistic), 0) AS signal_rate_among_available
FROM fact_spc_signal
GROUP BY split, sensor_id, method;

CREATE OR REPLACE VIEW mart_univariate_entity_summary AS
SELECT
    entity_id,
    event_timestamp,
    split,
    COUNT(DISTINCT sensor_id) FILTER (
        WHERE method IN ('I', 'MR') AND violation_indicator
    ) AS imr_signal_measurement_count,
    COUNT(DISTINCT sensor_id) FILTER (
        WHERE method = 'EWMA' AND violation_indicator
    ) AS ewma_signal_measurement_count,
    COUNT(*) FILTER (WHERE violation_indicator) AS total_univariate_signal_count,
    BOOL_OR(violation_indicator) AS any_univariate_signal
FROM fact_spc_signal
GROUP BY entity_id, event_timestamp, split;
