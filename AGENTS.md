# YieldGuard repository instructions

Before resuming, read `docs/PROJECT_PLAN.md`, `docs/PROJECT_STATUS.md`, and `docs/DECISIONS.md`; then verify them against Git status, history, files, and current checks. Stop after each user-approved phase and wait for approval.

## Stack and validation

- Use Python, pandas, NumPy, SciPy, statsmodels where needed, scikit-learn, DuckDB/SQL, pytest, Ruff, Quarto, and Power BI only as approved by the plan.
- Keep reusable logic in `src/yieldguard`; notebooks must remain thin.
- Run `python -m pytest`, `python -m ruff check .`, and the narrow CLI validation relevant to changed pipeline stages. Never report a check as passed unless it ran successfully.
- Use project-relative paths, deterministic seeds, configuration separate from logic, and idempotent outputs where practical.

## Data, security, and repository hygiene

- Never commit secrets, credentials, real `.env` values, restricted/raw data, caches, rebuildable databases, generated extracts, Power BI lock files, or dependency lock files.
- Preserve source/generated separation. SECOM is the only factual manufacturing dataset; simulated data, if later approved, must remain separate and explicitly labeled.
- Do not fabricate identifiers, physical meanings, specification limits, mechanisms, actions, costs, savings, volumes, or staffing.

## Analytical guardrails

- Split chronologically before fitting. Fit preprocessing, sensor rules, PCA, thresholds, and models on the permitted training/reference data only.
- Sensor selection must be deterministic, label-blind, and training-only. Final-test outcomes may not influence features, models, hyperparameters, thresholds, policies, or narratives.
- Phase 1 final-period access is limited to entity/failure counts, timestamps, schema validity, and structural quality. Before Phase 4, do not calculate final-test associations, outcome-conditioned measurement statistics, predictive metrics, policy results, or model comparisons.
- Association analysis uses the development period only and never final-test entities. Freeze monitoring, selection, predictive features, models, hyperparameters, calibration, and alert policies before combining training and calibration outcomes for associations.
- Evaluate at most six complete configurations per approved model.
- Record and commit the fixed review budget in `docs/DECISIONS.md` before final-test evaluation. Never revise the frozen headline budget in response to final-test performance.

## Scope exclusions

Do not add Kafka, Spark, Airflow, dbt, Snowflake, Databricks, Kubernetes, cloud infrastructure, streaming, deep learning, neural networks, digital twins, a production API, a web app, CUSUM, unapproved model libraries, causal root-cause claims, capability indices without real specification limits, or fabricated business claims. Do not use random splitting as the primary evaluation or accuracy as the headline metric.

## Required terminology

Use **production entity**, **measurement/anonymized sensor**, **control limit**, **excursion signal/statistical alert**, **failure-associated measurement/investigation candidate**, **retrospective ranking performance**, **reference period**, **development period**, **final test** only for frozen retrospective evaluation, and **frozen decision**. Do not substitute the prohibited physical or causal interpretations listed in the project plan.
