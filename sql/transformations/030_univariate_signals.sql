CREATE OR REPLACE TABLE fact_spc_signal AS
SELECT * FROM signal_frame;

CREATE UNIQUE INDEX ux_spc_signal
ON fact_spc_signal(signal_id);

CREATE OR REPLACE TABLE dim_spc_limit AS
SELECT * FROM limit_frame;

CREATE UNIQUE INDEX ux_spc_limit
ON dim_spc_limit(sensor_id);

CREATE OR REPLACE TABLE fact_sensor_autocorrelation AS
SELECT * FROM autocorrelation_frame;

CREATE UNIQUE INDEX ux_sensor_autocorrelation
ON fact_sensor_autocorrelation(sensor_id);
