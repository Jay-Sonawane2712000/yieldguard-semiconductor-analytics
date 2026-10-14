CREATE OR REPLACE TABLE dim_monitoring_sensor AS
SELECT * FROM selection_frame;

CREATE UNIQUE INDEX ux_monitoring_sensor
ON dim_monitoring_sensor(sensor_id);

CREATE OR REPLACE TABLE dim_sensor AS
SELECT
    sensor.* EXCLUDE (monitoring_selection_status, selection_rule_version),
    selection.selection_status AS monitoring_selection_status,
    selection.selection_rule_version
FROM dim_sensor AS sensor
JOIN dim_monitoring_sensor AS selection USING (sensor_id);

CREATE UNIQUE INDEX ux_sensor
ON dim_sensor(sensor_id);
