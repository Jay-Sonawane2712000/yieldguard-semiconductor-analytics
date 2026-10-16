CREATE OR REPLACE VIEW mart_model_performance AS
SELECT * FROM fact_model_evaluation;

CREATE OR REPLACE VIEW mart_review_budget AS
SELECT * FROM fact_policy_evaluation;

CREATE OR REPLACE VIEW mart_failure_association AS
SELECT * FROM fact_measurement_association;

CREATE OR REPLACE VIEW mart_engineering_review_queue AS
SELECT * FROM fact_engineering_review_queue;
