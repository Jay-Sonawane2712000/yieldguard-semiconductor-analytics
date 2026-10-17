CREATE OR REPLACE VIEW mart_dashboard_data_trust AS
SELECT
    COUNT(*) AS entity_count,
    COUNT(*) FILTER (WHERE failure_indicator = 0) AS pass_count,
    COUNT(*) FILTER (WHERE failure_indicator = 1) AS failure_count,
    MIN(event_timestamp) AS timestamp_start,
    MAX(event_timestamp) AS timestamp_end,
    (SELECT COUNT(*) FROM dim_sensor) AS measurement_count,
    (SELECT COUNT(*) FROM dim_sensor WHERE quality_status = 'eligible') AS usable_measurement_count,
    (SELECT COUNT(*) FROM dim_sensor WHERE quality_status = 'excluded') AS excluded_measurement_count,
    (SELECT COUNT(*) FROM dim_monitoring_sensor WHERE is_selected) AS monitoring_measurement_count,
    (SELECT SUM(measurement_missing::INTEGER) FROM fact_spc_signal WHERE method = 'I')
        AS selected_measurement_missing_count
FROM fact_production_entity;

CREATE OR REPLACE VIEW mart_dashboard_split_summary AS
SELECT
    split,
    COUNT(*) AS entity_count,
    COUNT(*) FILTER (WHERE failure_indicator = 1) AS failure_count,
    COUNT(*) FILTER (WHERE failure_indicator = 0) AS pass_count,
    AVG(failure_indicator) AS failure_rate,
    MIN(event_timestamp) AS timestamp_start,
    MAX(event_timestamp) AS timestamp_end,
    MIN(chronological_order) AS chronological_order_start,
    MAX(chronological_order) AS chronological_order_end
FROM fact_production_entity
GROUP BY split;

CREATE OR REPLACE VIEW mart_dashboard_sensor_quality AS
SELECT
    sensor_id,
    source_column,
    quality_status,
    inclusion_status,
    monitoring_selection_status,
    exclusion_reason,
    overall_missing_fraction,
    reference_missing_fraction,
    reference_temporal_coverage_fraction,
    reference_variance,
    reference_dominant_fraction,
    reference_extreme_count
FROM dim_sensor;

CREATE OR REPLACE VIEW mart_dashboard_monitoring_timeline AS
SELECT
    entity.entity_id,
    entity.event_timestamp,
    entity.chronological_order,
    entity.split,
    entity.failure_indicator,
    univariate.imr_signal_measurement_count,
    univariate.ewma_signal_measurement_count,
    univariate.total_univariate_signal_count,
    univariate.any_univariate_signal,
    multivariate.t2_statistic,
    multivariate.t2_limit,
    multivariate.t2_alert,
    multivariate.q_statistic,
    multivariate.q_limit,
    multivariate.q_alert,
    multivariate.any_multivariate_alert,
    univariate.any_univariate_signal AND multivariate.any_multivariate_alert
        AS alert_overlap
FROM fact_production_entity AS entity
JOIN mart_univariate_entity_summary AS univariate USING (entity_id)
JOIN fact_multivariate_alert AS multivariate USING (entity_id);

CREATE OR REPLACE VIEW mart_dashboard_alert_contribution AS
SELECT
    contribution.entity_id,
    contribution.event_timestamp,
    contribution.split,
    contribution.statistic_type,
    contribution.sensor_id,
    contribution.contribution,
    contribution.absolute_contribution,
    contribution.contribution_rank,
    contribution.contribution_share
FROM fact_alert_contribution AS contribution
WHERE contribution_rank <= 10;

CREATE OR REPLACE VIEW mart_dashboard_failure_driver AS
SELECT
    association.*,
    sensor.overall_missing_fraction,
    sensor.reference_missing_fraction,
    sensor.reference_temporal_coverage_fraction,
    sensor.monitoring_selection_status
FROM fact_measurement_association AS association
JOIN dim_sensor AS sensor USING (sensor_id);

CREATE OR REPLACE VIEW mart_dashboard_model_comparison AS
SELECT * FROM fact_model_evaluation;

CREATE OR REPLACE VIEW mart_dashboard_calibration AS
SELECT * FROM fact_model_calibration;

CREATE OR REPLACE VIEW mart_dashboard_review_budget AS
SELECT * FROM fact_policy_evaluation;

CREATE OR REPLACE VIEW mart_dashboard_review_queue AS
SELECT * FROM fact_engineering_review_queue;
