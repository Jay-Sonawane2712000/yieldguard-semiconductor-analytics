CREATE OR REPLACE TABLE dim_pca_model AS
SELECT * FROM pca_model_frame;

CREATE UNIQUE INDEX ux_pca_model
ON dim_pca_model(model_version);

CREATE OR REPLACE TABLE dim_pca_feature AS
SELECT * FROM pca_feature_frame;

CREATE UNIQUE INDEX ux_pca_feature
ON dim_pca_feature(model_version, sensor_id);

CREATE OR REPLACE TABLE fact_pca_loading AS
SELECT * FROM pca_loading_frame;

CREATE UNIQUE INDEX ux_pca_loading
ON fact_pca_loading(model_version, component_number, sensor_id);

CREATE OR REPLACE TABLE fact_multivariate_alert AS
SELECT * FROM multivariate_alert_frame;

CREATE UNIQUE INDEX ux_multivariate_alert
ON fact_multivariate_alert(entity_id);

CREATE OR REPLACE TABLE fact_alert_contribution AS
SELECT * FROM contribution_frame;

CREATE UNIQUE INDEX ux_alert_contribution
ON fact_alert_contribution(contribution_id);
