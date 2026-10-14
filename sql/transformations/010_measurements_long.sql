CREATE OR REPLACE TABLE fact_sensor_measurement AS
SELECT
    unpivoted.entity_id,
    entity.event_timestamp,
    entity.split,
    entity.chronological_order,
    unpivoted.sensor_id,
    unpivoted.raw_value,
    unpivoted.raw_value IS NULL AS missing_indicator
FROM (
    FROM measurements_wide
    UNPIVOT INCLUDE NULLS (
        raw_value FOR sensor_id IN (COLUMNS(* EXCLUDE (entity_id)))
    )
) AS unpivoted
JOIN fact_production_entity AS entity USING (entity_id);

CREATE UNIQUE INDEX ux_sensor_measurement
ON fact_sensor_measurement(entity_id, sensor_id);
