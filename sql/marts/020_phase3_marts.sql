CREATE OR REPLACE VIEW mart_multivariate_alert_history AS
SELECT
    entity_id,
    event_timestamp,
    split,
    t2_statistic,
    t2_limit,
    t2_alert,
    q_statistic,
    q_limit,
    q_alert,
    any_multivariate_alert,
    model_version,
    threshold_version
FROM fact_multivariate_alert;

CREATE OR REPLACE VIEW mart_alert_overlap AS
SELECT
    multivariate.entity_id,
    multivariate.event_timestamp,
    multivariate.split,
    univariate.any_univariate_signal,
    multivariate.t2_alert,
    multivariate.q_alert,
    multivariate.any_multivariate_alert,
    univariate.any_univariate_signal AND multivariate.any_multivariate_alert
        AS both_univariate_and_multivariate,
    univariate.total_univariate_signal_count
FROM fact_multivariate_alert AS multivariate
JOIN mart_univariate_entity_summary AS univariate USING (entity_id);

CREATE OR REPLACE VIEW mart_alert_method_summary AS
SELECT
    split,
    COUNT(*) AS entity_count,
    COUNT(*) FILTER (WHERE any_univariate_signal) AS univariate_alert_entity_count,
    COUNT(*) FILTER (WHERE t2_alert) AS t2_alert_entity_count,
    COUNT(*) FILTER (WHERE q_alert) AS q_alert_entity_count,
    COUNT(*) FILTER (WHERE any_multivariate_alert) AS multivariate_alert_entity_count,
    COUNT(*) FILTER (WHERE both_univariate_and_multivariate) AS overlap_entity_count
FROM mart_alert_overlap
GROUP BY split;
