# APPROVED PROJECT PLAN — YIELDGUARD

Use this document as the separate project plan alongside my **Codex Project-Building Workflow**.

The workflow document defines how you must inspect, implement, verify, document, commit, stop at phase boundaries, and communicate. This project plan defines exactly what must be built.

Treat this plan as the approved source of truth. Do not replace the project, silently change its objective, expand its scope, substitute another dataset, or alter the approved architecture, evaluation strategy, models, dashboard, or deliverables without my explicit approval.

# YieldGuard: Semiconductor Process Excursion Monitoring and Failure-Driver Triage

## 1. Assignment

Build a portfolio-quality, reproducible semiconductor manufacturing analytics project named:

> **YieldGuard: Semiconductor Process Excursion Monitoring and Failure-Driver Triage**

This must be a serious end-to-end analytical decision system—not a generic classification notebook, a collection of disconnected notebooks, or a basic dashboard.

The system must:

1. Audit the reliability of high-dimensional manufacturing measurements.
2. Identify measurements unsuitable for analysis because of missingness, insufficient coverage, constant values, near-zero variance, or other quality problems.
3. Select a small group of measurements for sequential monitoring using a written, label-blind, training-only rule.
4. Monitor those measurements using I-MR and EWMA control charts.
5. Detect multivariate excursions using PCA-based T-squared and Q/SPE monitoring.
6. Calculate measurement-level contributions for every production entity.
7. Identify measurements associated with failed production entities while controlling false discoveries.
8. Build interpretable failure-risk rankings for later production entities.
9. Compare predictive models with simple, label-blind monitoring baselines.
10. Convert analytical outputs into an auditable engineering-review queue.
11. Evaluate review policies under fixed capacity constraints.
12. Quantify failures found, failures missed, false alerts, workload, calibration, and uncertainty.
13. Communicate findings through:
    - Python;
    - DuckDB and SQL;
    - a reproducible statistical report;
    - a functional three-page Power BI dashboard;
    - a concise engineering decision memo;
    - professional GitHub documentation.
14. Clearly distinguish:
    - monitoring;
    - statistical association;
    - prediction;
    - causal root cause.

Do not replace this with another semiconductor project.

Do not expand it into a streaming platform, digital twin, deep-learning project, cloud architecture exercise, production API, or web application.

---

## 2. Why this project was selected

My portfolio already demonstrates areas including:

- ecommerce funnel and retention analysis;
- batch and streaming data engineering;
- A/B testing and experimentation;
- fraud classification and anomaly explanation;
- transit monitoring;
- operational control towers;
- financial-reporting and data-quality analysis.

Another generic classifier, predictive-maintenance notebook, Kafka pipeline, supply-chain dashboard, or anomaly dashboard would duplicate existing evidence.

YieldGuard adds a distinct portfolio story:

- semiconductor manufacturing analytics;
- statistical process control;
- multivariate process monitoring;
- measurement-system and data-quality auditing;
- high-dimensional statistical analysis;
- false-discovery-rate control;
- time-aware evaluation;
- calibrated risk ranking;
- engineering review-budget decisions;
- SQL analytical modeling;
- Power BI decision support;
- honest separation of association from causation.

The project should demonstrate that I can do more than train a model. It must show that I can:

- frame a real operational decision;
- validate imperfect data;
- prevent temporal leakage;
- implement statistical monitoring correctly;
- quantify uncertainty;
- design a usable analytical data model;
- translate scores into a review policy;
- communicate limitations;
- create a polished stakeholder-facing product.

The project is best positioned for roles such as:

- manufacturing data analyst;
- semiconductor analytics analyst;
- yield-data analyst;
- quality-data analyst;
- factory BI or reporting analyst;
- manufacturing programming specialist;
- junior manufacturing data scientist;
- analytics roles supporting process, yield, equipment, or quality engineers.

Do not imply that this project replaces any electrical-engineering, materials-science, physics, chemical-engineering, or direct fabrication experience required by a particular job.

### Public-claims restriction

This section is private project-selection rationale.

Do not copy claims about employer requirements, hiring demand, or particular companies into the public README, report, dashboard, portfolio, or resume unless a separate current-market review verifies them using dated, directly cited job postings.

The project must stand on its technical and business merits without unsupported labor-market claims.

---

## 3. Portfolio pitch

Use the following as the core description unless measured results later justify a more specific version:

> YieldGuard is a reproducible semiconductor manufacturing analytics system that audits high-dimensional process measurements, detects univariate and multivariate excursions, ranks failure-associated measurements, and produces a statistically defensible engineering-review queue. It combines Python, SQL, DuckDB, Power BI, and a reproducible statistical report. Because the public dataset does not provide confirmed excursion intervals or causal interventions, the project clearly separates observed associations from causal conclusions and, if the simulation extension is completed, uses a small controlled simulation to validate monitoring behavior.

---

## 4. Business framing

### Primary stakeholders

- Yield engineering team
- Process integration team
- Quality engineering team
- Manufacturing analytics or factory BI team

### Business problem

Semiconductor manufacturing can produce hundreds of measurements for each production entity.

Engineers need to determine:

- which measurements are trustworthy;
- whether the process is showing unusual behavior;
- which entities require investigation;
- which measurements contributed to an alert;
- which measurements are associated with failures;
- how many entities can realistically be reviewed;
- how many failures may be detected or missed under that review policy.

### Decisions the project must support

1. Which measurements have sufficient quality for analysis?
2. Which measurements are suitable for sequential monitoring?
3. Which entities show univariate excursion signals?
4. Which entities show multivariate excursion signals?
5. Which measurements contributed most to T-squared and Q/SPE scores?
6. Which measurements are associated with failure strongly enough to prioritize investigation?
7. Which later entities should enter the engineering-review queue?
8. What review workload does each alert policy create?
9. How many failures are found or missed under each policy?
10. How uncertain and temporally stable are the results?

### Intended user workflow

An analyst or engineer should be able to:

1. Open the **Data Trust** dashboard page.
2. Understand which measurements were retained or excluded and why.
3. Open the **Excursion Monitoring** page.
4. Inspect I-MR, EWMA, T-squared, and Q/SPE alerts.
5. Select an entity and inspect its leading measurement contributions.
6. Open the **Failure-Driver Triage** page.
7. Examine failure-associated measurements.
8. Review the ranked engineering queue.
9. Compare fixed review-budget scenarios.
10. Understand the resulting workload and missed-failure tradeoff.
11. Consult the statistical report for methods, assumptions, uncertainty, and limitations.

---

## 5. Dataset

Use the **UCI SECOM dataset** as the core and only factual manufacturing dataset.

Source:

`https://archive.ics.uci.edu/dataset/179/secom`

Expected characteristics that must be verified during Phase 1:

- approximately 1,567 rows;
- approximately 590 anonymized process-measurement columns;
- timestamps;
- pass/fail labels;
- extensive missingness;
- severe class imbalance.

The source files are commonly distributed as `secom.data` and `secom_labels.data`, but inspect the acquired source rather than assuming filenames or structure.

Before reporting anything as fact, verify:

- exact row count;
- exact measurement count;
- label encoding;
- pass count;
- failure count;
- timestamp format;
- timestamp range;
- duplicate behavior;
- missingness;
- metadata;
- license;
- checksum where practical.

### Data-semantics rule

Call each row a **production entity**.

Do not automatically call it a:

- wafer;
- die;
- lot;
- batch;
- tool run;
- chamber event;
- process step.

The public documentation does not establish those meanings.

### Data-integrity rules

Do not fabricate:

- equipment IDs;
- tool IDs;
- chamber IDs;
- recipes;
- named process steps;
- product families;
- physical sensor meanings;
- engineering specification limits;
- failure mechanisms;
- corrective actions;
- production costs;
- operational savings;
- production volumes;
- real review staffing levels.

Do not map anonymized measurements to named physical parameters.

If simulation is implemented:

- store it separately;
- clearly label it as simulated;
- never mix it with SECOM;
- never present it as factual manufacturing evidence.

Prefer reproducible acquisition.

Do not commit source data if the license, repository policy, or file size makes that inappropriate. Document acquisition in `data/README.md`, use appropriate `.gitignore` rules, and record checksums where practical.

---

## 6. Required analytical questions

The completed project must answer:

1. What is the observed pass/fail distribution?
2. How does observed failure frequency vary over time?
3. Are timestamps usable for chronological evaluation?
4. Which measurements are unusable because of data-quality problems?
5. Which measurements qualify for univariate monitoring under a label-blind, training-only rule?
6. Do selected measurements show I-MR or EWMA signals when limits are learned without future data?
7. Can PCA T-squared and Q/SPE detect multivariate excursions?
8. Which measurements contribute most to every entity’s T-squared and Q/SPE scores?
9. Which measurements differ between passed and failed entities?
10. How large and uncertain are those differences?
11. Which associations survive false-discovery-rate correction?
12. How sensitive are findings to correlated measurements?
13. How well do logistic regression and HistGradientBoosting rank later failures?
14. How do those models compare with prevalence and monitoring-based baselines?
15. Under fixed review budgets, how many failures are found?
16. How many failures are missed?
17. How many non-failures require review?
18. How well calibrated are the predicted risks?
19. How uncertain are the estimates?
20. Are results reasonably stable across time windows?

---

## 7. Definition of analytical success

Success does not mean obtaining an arbitrary model score.

The project succeeds when:

- the pipeline is reproducible;
- data-quality decisions are auditable;
- future data is protected from leakage;
- every alert traces to an entity, method, statistic, limit, and version;
- T-squared and Q/SPE scores have measurement-level contributions;
- association results contain effect sizes and multiplicity correction;
- prediction uses metrics suitable for class imbalance;
- alert policies quantify workload and missed failures;
- uncertainty is reported;
- small-sample limitations are explicit;
- the dashboard supports a real decision workflow;
- the report explains methods and assumptions;
- tests protect important calculations and boundaries;
- the repository is professional and interview-ready.

Do not define success as classification accuracy.

A negative result is acceptable. If a complex model does not improve meaningfully over a simple baseline, preserve that result and recommend the simpler policy.

Do not manipulate the split, metric, features, thresholds, or narrative to manufacture success.

---

## 8. Scope tiers

### Tier A — required core deliverables

1. Feasibility and data-quality audit.
2. Reproducible data acquisition or documented manual acquisition.
3. Hybrid DuckDB analytical architecture.
4. Meaningful SQL tables, views, and marts.
5. Measurement-quality audit.
6. Machine-readable sensor-exclusion log.
7. Chronological or rolling-origin evaluation.
8. Label-blind, training-only monitoring-sensor selection.
9. I-MR monitoring.
10. EWMA monitoring.
11. PCA T-squared monitoring.
12. PCA Q/SPE monitoring.
13. Contribution analysis for every entity.
14. Cliff’s delta.
15. Approximate bootstrap intervals.
16. Two-sided Mann–Whitney U comparisons.
17. Benjamini–Hochberg FDR correction.
18. Dependence sensitivity using Benjamini–Yekutieli or a justified limited permutation method.
19. Regularized logistic regression.
20. `HistGradientBoostingClassifier`.
21. Prevalence baseline.
22. Fixed label-blind monitoring baseline.
23. PR-AUC evaluation.
24. Calibration evaluation.
25. Fixed review-budget evaluation.
26. Uncertainty reporting.
27. Frozen headline budget selected before final-test evaluation.
28. Functional three-page Power BI dashboard.
29. Reproducible statistical report with HTML output.
30. Engineering decision memo.
31. Focused automated tests.
32. Repository documentation.
33. Architecture and data-flow explanation.
34. Data dictionary.
35. Metric dictionary.
36. Methods documentation.
37. Limitations documentation.
38. Dashboard screenshots.
39. Reproducibility instructions.
40. Interview guide.

### Tier B — quality-preserving extensions

Implement only after the related Tier A work is complete:

1. Small, separately labeled injected-shift simulation.
2. Minimal continuous integration.
3. Limited sensitivity analyses for imputation, scaling, monitoring limits, or temporal windows.

### Tier C — optional extensions

Only consider after the core project works:

- Two or three supplementary Western Electric or Nelson-style rules.
- JMP corroboration appendix if JMP is legally available.
- Excel review-queue export.
- Excel reconciliation sheet.
- Advanced Power BI themes, bookmarks, and custom tooltips.

### Cut policy

Do not silently remove requirements.

If schedule risk appears, raise it at the current phase boundary.

Preferred cut order:

1. Advanced dashboard polish, never the dashboard itself.
2. Elaborate simulation scenarios.
3. CI beyond a basic test workflow.
4. Broad sensitivity analysis.
5. Supplementary run rules.
6. JMP appendix.
7. Excel exports.

Never cut:

- leakage prevention;
- contribution analysis;
- uncertainty reporting;
- core tests;
- the statistical report;
- the functional dashboard;
- the decision memo.

---

## 9. Explicit exclusions

Do not add the following without explicit approval:

- Kafka;
- Spark;
- Airflow;
- dbt;
- Snowflake;
- Databricks;
- Kubernetes;
- cloud infrastructure;
- streaming ingestion;
- real-time deployment claims;
- deep learning;
- neural networks;
- a digital twin;
- a production API;
- a web application;
- causal root-cause claims;
- Cp, Cpk, Pp, or Ppk without real specification limits;
- SPC charts for every measurement;
- CUSUM;
- complicated imbalance methods before class weighting;
- SHAP as a required component;
- fabricated savings;
- fabricated ROI;
- accuracy as the headline metric;
- random train/test splitting as the primary evaluation;
- claims that this reproduces operations at any semiconductor company.

Do not add R, Java, C, or C++ merely to increase the number of languages.

The project’s depth must come from analytical correctness and decision quality, not unnecessary technologies.

---

## 10. Approved technology stack

Use the smallest professional stack that implements the plan:

- **Python**
- **DuckDB**
- **SQL**
- **pandas or Polars**, choosing one primary dataframe library
- **NumPy**
- **SciPy**
- **statsmodels**, where required
- **scikit-learn**
- **Matplotlib, Seaborn, or Plotly**, using a coherent visual stack
- **Quarto**, if available
- **Power BI Desktop**
- **pytest**
- **Ruff**, or an existing equivalent
- **GitHub Actions**, when feasible

Use Python for:

- acquisition;
- validation;
- transformations;
- SPC;
- PCA;
- contribution analysis;
- statistical comparisons;
- modeling;
- evaluation;
- exports;
- report generation.

Use DuckDB and SQL for:

- persisted analytical tables;
- views;
- marts;
- quality summaries;
- alert history;
- review queues;
- dashboard-ready outputs.

Guarantee a rendered HTML report.

Treat PDF as optional if the required rendering toolchain is unavailable.

Keep notebooks thin and exploratory. Reusable calculations and transformations must live in tested modules. Hidden notebook state must not be the production pipeline.

---

## 11. Proposed repository structure

Adapt names only when existing repository conventions require it.

```text
yieldguard-semiconductor-analytics/
|-- README.md
|-- AGENTS.md
|-- pyproject.toml
|-- .gitignore
|-- .env.example
|-- config/
|   `-- project.yaml
|-- data/
|   |-- README.md
|   |-- raw/
|   |-- interim/
|   |-- processed/
|   `-- sample/
|-- src/
|   `-- yieldguard/
|       |-- __init__.py
|       |-- cli.py
|       |-- config.py
|       |-- acquire.py
|       |-- ingest.py
|       |-- validation.py
|       |-- splits.py
|       |-- quality.py
|       |-- sensor_selection.py
|       |-- spc.py
|       |-- pca_monitoring.py
|       |-- contributions.py
|       |-- associations.py
|       |-- modeling.py
|       |-- evaluation.py
|       |-- simulation.py
|       `-- export.py
|-- sql/
|   |-- ddl/
|   |-- transformations/
|   `-- marts/
|-- notebooks/
|   `-- exploratory/
|-- reports/
|   |-- yieldguard_analysis.qmd
|   |-- rendered/
|   |-- figures/
|   `-- decision_memo.md
|-- powerbi/
|   |-- YieldGuard.pbix
|   |-- README.md
|   |-- dax_measures.md
|   |-- data_dictionary.md
|   `-- screenshots/
|-- docs/
|   |-- PROJECT_PLAN.md
|   |-- PROJECT_STATUS.md
|   |-- DECISIONS.md
|   |-- architecture.md
|   |-- data_dictionary.md
|   |-- metric_dictionary.md
|   |-- validation_design.md
|   |-- statistical_methods.md
|   |-- limitations.md
|   `-- interview_guide.md
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- fixtures/
`-- .github/
    `-- workflows/
        `-- ci.yml
```

`.env.example` should exist only if variables are genuinely required.

Do not commit:

- secrets;
- credentials;
- caches;
- temporary files;
- Power BI lock files;
- rebuildable local databases;
- restricted raw data;
- unnecessarily large generated files.

---

## 12. Data architecture

Use a hybrid wide/long architecture.

Do not make a fully long table the only representation for every analytical operation.

### `fact_production_entity`

One row per production entity:

- `entity_id`
- `event_timestamp`
- original label
- normalized failure indicator
- chronological order
- split or fold assignment
- source-data version

### `measurements_wide`

One row per entity and one column per measurement.

Use for:

- PCA;
- modeling;
- efficient wide statistical operations.

### `fact_sensor_measurement`

Long representation for:

- auditability;
- SQL analysis;
- dashboard filtering;
- measurement drilldowns.

Fields:

- `entity_id`
- `sensor_id`
- raw value
- missing indicator
- explicitly named transformed or imputed value, if stored
- timestamp or documented timestamp join path

### `dim_sensor`

One row per measurement:

- `sensor_id`
- source column
- missingness
- temporal coverage
- non-null count
- distinct count
- variance or robust spread
- quality status
- inclusion status
- exclusion reason
- monitoring-selection status
- selection-rule version

### `fact_spc_signal`

Fields:

- entity
- timestamp
- measurement
- method: `I`, `MR`, or `EWMA`
- statistic
- center line
- lower control limit
- upper control limit
- violation indicator
- rule identifier
- limit version

### `fact_multivariate_alert`

Fields:

- entity
- timestamp
- T-squared score
- T-squared limit
- T-squared alert
- Q/SPE score
- Q/SPE limit
- Q/SPE alert
- combined alert status
- model version
- threshold version

### `fact_alert_contribution`

For every entity and for each statistic:

- entity
- statistic type
- measurement
- contribution
- contribution rank
- contribution share

Persist the top ten measurements per entity per statistic.

### `fact_sensor_association`

Fields:

- measurement
- development-period group counts
- missingness by outcome
- descriptive statistics by outcome
- Cliff’s delta
- lower and upper approximate interval
- Mann–Whitney statistic
- raw p-value
- BH-adjusted p-value
- BY-adjusted p-value or approved sensitivity result
- investigation status
- method version

### `fact_failure_risk`

Fields:

- entity
- timestamp
- split or fold
- model
- model version
- raw score
- calibrated probability, if available
- risk rank
- review-budget flags

### `fact_model_evaluation`

Fields:

- model or baseline
- split or fold
- metric
- estimate
- interval bounds
- threshold or review budget
- positive count
- negative count
- model version

### `mart_engineering_review_queue`

Include:

- entity;
- timestamp;
- risk score;
- risk rank;
- review-budget status;
- I-MR status;
- EWMA status;
- T-squared status;
- Q/SPE status;
- top contributions;
- data-quality warnings;
- retrospective outcome;
- reason codes explaining why the entity was queued.

### Dashboard marts

Create stable, documented marts for each dashboard page.

Do not connect Power BI directly to fragile intermediate dataframes.

### SQL expectations

SQL must provide meaningful evidence, including:

- label normalization;
- production-entity construction;
- sensor-quality summaries;
- alert history;
- contribution outputs;
- association outputs;
- risk outputs;
- review queue;
- alert-budget results;
- dashboard facts and dimensions.

Document:

- grain;
- keys;
- joins;
- metric definitions;
- null behavior.

Test important:

- row counts;
- uniqueness;
- join cardinality;
- reconciliations.

---

## 13. Evaluation-design gate

Do not finalize the evaluation design before inspecting timestamp and failure distributions.

### Preferred design

Use chronological partitions:

- earlier period: training and reference fitting;
- later period: calibration and policy selection;
- latest period: untouched final test.

A candidate starting allocation is approximately 60/20/20, but it is not mandatory.

Choose boundaries based on:

- timestamp integrity;
- chronological coverage;
- tied timestamps;
- failure counts;
- usable period sizes.

Do not select boundaries based on whichever split produces better performance.

### Required Phase 1 checks

Report:

- total entities;
- total failures;
- entities per candidate period;
- failures per candidate period;
- duplicate timestamps;
- tied timestamps;
- timestamp gaps;
- ordering anomalies;
- temporal coverage;
- whether the final holdout has enough failures for interpretable estimates.

### Rolling-origin fallback

If a single holdout has too few failures, switch to a documented rolling-origin or expanding-window design.

This switch is already approved when supported by Phase 1 evidence. Do not stop merely to ask permission to use rolling-origin evaluation.

Retain the latest suitable period as an untouched final directional block whenever statistically feasible.

Under rolling-origin evaluation:

- define the development period as all observations before the final directional block;
- use only that development period for association analysis and development choices;
- preserve chronological order;
- report fold-level and aggregated results;
- report uncertainty.

### Dropping the final directional block

Dropping the final block is allowed only when Phase 1 evidence shows that retaining it is statistically impractical.

If that occurs:

1. Record the evidence in `docs/DECISIONS.md`.
2. Explain the consequences.
3. Define the proposed no-holdout design.
4. Obtain my approval before proceeding without an untouched block.
5. If approved, state that no untouched final evaluation exists.
6. Label rolling-origin results as development-period estimates.
7. Do not call anything final-test performance.

Do not switch to random cross-validation merely to obtain attractive metrics.

### Small-sample language

Verify the failure count.

If failures are sparse, state:

> Holdout performance estimates are directional and are accompanied by uncertainty intervals because the number of observed failures is limited.

Do not claim operational reliability from a small holdout.

---

## 14. Leakage and final-test policy

Leakage prevention is non-negotiable.

- Split chronologically before fitting preprocessing, PCA, models, or thresholds.
- Fit all preprocessing on training/reference data only.
- Use calibration data only for approved development decisions.
- Do not inspect final-test outcomes while choosing sensors, models, hyperparameters, thresholds, policies, or narratives.
- Select monitoring measurements without using failure labels.
- Put preprocessing inside reproducible pipelines.
- Add assertions or tests for temporal boundaries.
- Record random seeds and versions.

### Permitted Phase 1 final-period access

During Phase 1, Codex may inspect:

- final-period entity count;
- final-period failure count;
- timestamps;
- schema validity;
- structural data-quality conditions.

These checks are permitted because they are required to determine evaluation feasibility.

Before Phase 4, do not calculate:

- final-test failure associations;
- final-test outcome-conditioned measurement statistics;
- final-test predictive metrics;
- final-test alert-policy results;
- final-test model comparisons.

All quality thresholds and measurement-selection rules remain training-only.

### Association-analysis boundary

Run the primary failure-driver association analysis on the combined training and calibration periods only. Call this the **development period**.

Never include final-test entities or outcomes in:

- Cliff’s delta;
- Mann–Whitney tests;
- association bootstrap intervals;
- multiplicity correction;
- candidate rankings;
- association narratives.

Before using calibration outcomes in the combined association analysis, freeze:

- monitoring design;
- sensor-selection rule;
- predictive features;
- model choices;
- hyperparameters;
- calibration method;
- alert policies.

Association findings must not be used afterward to revise those frozen choices.

Reserve final-test outcomes for evaluation of the frozen monitoring, ranking, and alert policy.

Do not mine the final test for new findings.

---

## 15. Measurement trust audit

Profile and report:

- source shape;
- source schema;
- label encoding;
- class balance;
- timestamp validity;
- timestamp range;
- duplicate entities;
- duplicate source rows;
- missingness by measurement;
- missingness by entity;
- all-null columns;
- distinct counts;
- constant columns;
- near-constant columns;
- variance or robust spread;
- extreme values;
- parsing problems;
- temporal coverage;
- candidate split counts;
- redundancy and correlations relevant to selection;
- exclusion reasons.

Create a machine-readable exclusion log.

Never silently remove a measurement.

Put quality thresholds in configuration.

Document every threshold and rationale.

If a material threshold changes after Phase 1, record the decision.

---

## 16. Monitoring-measurement selection

Select approximately 8–15 measurements for I-MR and EWMA monitoring.

The exact number may change only for documented feasibility reasons.

The rule must be:

- written;
- deterministic;
- label-blind;
- training-only;
- frozen before failure association or final-test evaluation.

Base eligibility on:

- acceptable missingness;
- sufficient non-null count;
- meaningful spread;
- temporal coverage;
- sequential-monitoring suitability;
- redundancy control.

Do not select measurements based on pass/fail association.

If eligible measurements must be ranked, use a deterministic combination of:

- coverage;
- completeness;
- variation;
- temporal availability;
- redundancy.

Store:

- rule definition;
- threshold values;
- ranking components;
- selected measurements;
- exclusion reasons;
- selection-rule version.

---

## 17. Univariate monitoring

Implement:

1. Individuals charts.
2. Moving Range charts.
3. EWMA charts.

Requirements:

- Estimate centers and limits from the training/reference period only.
- Distinguish control limits from engineering specification limits.
- Document formulas and constants.
- Define missing-observation behavior.
- Define timestamp-gap behavior.
- Do not silently interpolate missing values.
- Report signal counts and signal rates by period.
- Inspect serial correlation.
- Explain autocorrelation’s effect on false-alarm assumptions.
- Trace every signal to its entity and measurement.
- Compare signals with failures only retrospectively.
- Do not call alert/failure overlap causal evidence.
- Quantify workload and false alerts.

Supplementary run rules are optional.

If included:

- use at most two or three;
- document their assumptions;
- quantify added alert volume;
- avoid producing an uninterpretable alert explosion.

### EWMA limits

Choose either:

- exact time-varying limits; or
- steady-state limits.

Record the selected form in `config/project.yaml`.

Use the same limits in:

- chart display;
- alert logic;
- baseline severity calculation.

---

## 18. PCA multivariate monitoring

Implement:

- Hotelling’s T-squared;
- Q/SPE residual monitoring.

Requirements:

- Fit imputation on training/reference data only.
- Fit scaling on training/reference data only.
- Document the imputation method.
- Choose component count using a documented training-only rule.
- Fit PCA on the reference period.
- Use “reference period,” not “known in-control period,” unless justified.
- Calibrate limits without final-test labels.
- State whether limits are theoretical, empirical, or bootstrap-based.
- Report T-squared and Q/SPE separately and jointly.
- Compare multivariate and univariate alerts.
- Version models and thresholds.
- Test score and limit calculations.

### Mandatory contribution analysis

Calculate contributions for every production entity for:

- T-squared;
- Q/SPE.

For each entity and each statistic, retain the ten highest-contributing measurements.

Set:

```yaml
pca_contribution_top_k: 10
```

in `config/project.yaml`.

Do not leave this value to session-level judgment.

At approximately 1,567 entities, two statistics, and ten retained measurements, expect approximately 31,000 contribution rows, subject to the verified entity count.

The report and dashboard must display the stored contributors for a selected entity and statistic.

Contribution rankings identify measurements associated with a score or alert. They do not prove physical root cause.

---

## 19. Failure-driver association analysis

The objective is to prioritize investigation candidates, not prove root causes.

Use the development period only.

Exclude the final test completely.

For every eligible measurement:

1. Report sample size by outcome.
2. Report missingness by outcome.
3. Report robust descriptive statistics.
4. Calculate **Cliff’s delta**.
5. Define its direction consistently.
6. Calculate an approximate bootstrap interval.
7. Run a two-sided **Mann–Whitney U test**.
8. Explain that Mann–Whitney is not automatically a median test when group shapes differ.
9. Report raw p-values.
10. Apply **Benjamini–Hochberg FDR**.
11. Acknowledge correlated measurements.
12. Apply **Benjamini–Yekutieli** or a justified dependence-sensitive alternative.
13. Show which findings survive each correction.
14. Compare association evidence with PCA contributions and model evidence.
15. Do not treat agreement as causality.

Do not rank measurements by p-value alone.

Consider:

- effect magnitude;
- interval width;
- data quality;
- sample size;
- adjusted evidence;
- stability;
- consistency.

### Association bootstrap

Prefer moving-block or another time-respecting bootstrap when feasible.

If rare failures make that unstable:

- use outcome-stratified resampling;
- label intervals approximate;
- disclose that temporal dependence is not preserved;
- report usable replicate count;
- treat intervals as descriptive.

If permutation testing is used, preserve temporal or dependence structure. Do not use a simplistic invalid permutation.

---

## 20. Failure-risk ranking

This is a secondary module, not the project’s identity.

### Model 1 — regularized logistic regression

Use a training-fitted pipeline with:

- eligible-column filtering;
- median imputation;
- optional missingness indicators if Phase 1 justifies them;
- scaling;
- regularized logistic regression.

Do not preprocess outside the training pipeline.

### Model 2 — HistGradientBoosting

Use scikit-learn’s:

`HistGradientBoostingClassifier`

This is the only tree-based model.

For this model:

- retain native missing-value handling;
- do not impute merely to mirror logistic regression;
- do not scale inputs;
- use the same training-only unusable-column filter;
- use `class_weight` when supported;
- otherwise use equivalent training-only sample weights.

Do not add:

- XGBoost;
- LightGBM;
- CatBoost;
- random forest;
- other boosting libraries.

Do not turn the project into a model tournament.

### Hyperparameter limit

Define complete candidate configurations in `config/project.yaml` before evaluation.

Evaluate no more than:

- six complete logistic-regression configurations;
- six complete HistGradientBoosting configurations.

A configuration means a complete set of parameter values, not six values for every parameter.

Keep the search within the approved temporal development design.

Do not expand or alter the search after viewing final-test performance.

### Baselines

Required baselines:

1. Prevalence or constant-score baseline.
2. Fixed, label-blind monitoring baseline.

### Monitoring baseline

For each entity:

```text
monitoring_signal_count =
    number of selected measurements with an I-MR signal
  + number of selected measurements with an EWMA signal
  + indicator(T-squared exceeds its frozen limit)
  + indicator(Q/SPE exceeds its frozen limit)
```

Rank first by `monitoring_signal_count`.

Resolve ties using the following severity rules:

```yaml
For I and EWMA:
    if statistic >= center_line:
        severity = (statistic - center_line) / (UCL - center_line)
    else:
        severity = (center_line - statistic) / (center_line - LCL)

For Moving Range:
    severity = statistic / UCL

For T-squared:
    severity = score / T2_limit

For Q/SPE:
    severity = score / Q_limit

entity_tie_breaker = maximum severity across all available
                     monitoring statistics for that entity
```

Interpretation:

- severity `1.0` means exactly at the applicable limit;
- severity above `1.0` means outside the limit.

Additional rules:

- Validate every denominator as finite and strictly positive.
- Fail clearly on invalid limits.
- A missing measurement contributes no severity.
- Do not impute missing severity to zero.
- If an entity has no available monitoring statistics, assign `entity_tie_breaker = 0`.
- Use the same EWMA limit form as the chart at that observation.
- Severities are only tie-breakers.
- Do not claim they are comparable effect sizes across chart types.

Final deterministic ranking:

1. Descending `monitoring_signal_count`
2. Descending `entity_tie_breaker`
3. Timestamp
4. Entity ID

Do not learn baseline weights, combinations, thresholds, or tie-breaking rules from labels.

### Modeling rules

- Use chronological or approved rolling evaluation.
- Fit all preprocessing inside training.
- Use class weighting before complex resampling.
- Keep tuning bounded.
- Do not tune against the final test.
- Calibrate using permitted development data only.
- Preserve feature provenance.
- Report instability honestly.

### Required evaluation

Report:

- positive prevalence;
- PR-AUC;
- ROC-AUC as supplementary context;
- calibration curve;
- calibration summary;
- precision;
- recall;
- confusion counts;
- fixed-budget precision and recall;
- entities reviewed;
- failures detected;
- failures missed;
- non-failures reviewed;
- uncertainty intervals;
- performance by fold or period;
- comparisons with both baselines.

Do not headline accuracy.

Use language such as:

> The model produces a prioritized investigation queue whose retrospective enrichment is measured under a constrained review budget.

### Evaluation uncertainty

Prefer a moving-block, stationary, or time-respecting bootstrap.

Report:

- block definition;
- usable replicate count;
- entity count;
- failure count.

If sparse failures make that impractical, use an outcome-stratified bootstrap only as an approximate descriptive interval.

Disclose that it does not preserve temporal dependence.

---

## 21. Alert-policy analysis

Evaluate:

- top 1%;
- top 5%;
- top 10%;
- top 20%;
- one or more fixed top-k counts;
- F2-maximizing calibration threshold as a diagnostic comparison.

For every policy, report:

- entities reviewed;
- failures detected;
- failures missed;
- non-failures reviewed;
- precision;
- recall;
- alert rate;
- uncertainty;
- evaluation period.

Do not invent daily or weekly staffing levels when the data does not support them.

Use **dataset-period review scenario** where appropriate.

### Frozen headline budget

Choose the recommended fixed-percentage or fixed-count budget using:

- calibration-period results;
- explicit capacity reasoning;
- uncertainty;
- interpretability.

Before running or examining final-test evaluation metrics:

1. Record the selected budget in `docs/DECISIONS.md`.
2. Record the reasoning and alternatives.
3. Commit that decision.
4. Confirm the commit succeeded.
5. Only then run final-test evaluation.

The Git history must make the order auditable.

After the decision commit:

- freeze the headline budget;
- do not change it because of final-test performance;
- label any post-test alternative exploratory;
- do not replace the frozen headline recommendation.

### F2 restriction

The F2-maximizing threshold is diagnostic only.

It may be unstable when calibration failures are sparse.

The decision memo must recommend the frozen fixed budget—not the F2 threshold.

---

## 22. Controlled simulation

This is Tier B.

Keep it small and separate.

### Purpose

Test whether the monitoring implementation reacts sensibly to known injected:

- mean shifts;
- variance shifts;
- correlated multivariate changes.

Compare:

- detection rate;
- false-positive rate;
- detection delay

for:

- I-MR;
- EWMA;
- T-squared;
- Q/SPE.

### Rules

- Separate Python module.
- Separate output directory.
- Separate report section.
- Clearly label outputs as simulated.
- Use fixed random seeds.
- Never mix simulated data with SECOM.
- Do not tune real-data limits using simulation outcomes.
- Keep scenarios limited.
- Do not let simulation become a second project.

---

## 23. Power BI dashboard

A functional dashboard is required.

Advanced polish is optional. The dashboard itself is not.

Build exactly three principal pages.

### Page 1 — Data Trust

Show:

- entity count;
- measurement count;
- pass/fail balance;
- timestamp coverage;
- missingness distribution;
- usable measurements;
- excluded measurements;
- monitoring measurements;
- exclusion reasons;
- split or fold boundaries;
- entity and failure counts by period;
- prominent limitations.

### Page 2 — Excursion Monitoring

Support:

- alert timeline;
- time filters;
- measurement filters;
- method filters;
- alert-type filters;
- I-MR charts;
- EWMA charts;
- T-squared scores and limits;
- Q/SPE scores and limits;
- alert overlap;
- selected-entity drillthrough;
- leading T-squared contributions;
- leading Q/SPE contributions;
- clear separation of statistical alerts and observed failures.

### Page 3 — Failure-Driver Triage

Support:

- ranked measurement associations;
- Cliff’s delta;
- approximate intervals;
- BH-adjusted results;
- dependence sensitivity;
- quality warnings;
- model and baseline comparison;
- calibration summary;
- alert-budget scenarios;
- review workload;
- failures detected;
- failures missed;
- non-failures reviewed;
- engineering-review queue;
- queue reason codes.

### Dashboard requirements

- Use metric-dictionary definitions.
- Avoid misleading red/green semantics.
- Document data lineage.
- Document refresh steps.
- Document important DAX.
- Capture readable screenshots.
- Test filters.
- Test interactions.
- Test empty states.
- Reconcile totals against SQL and Python.
- Do not fabricate dashboard outputs.

### Power BI execution boundary

If Codex cannot operate Power BI Desktop:

1. Build and verify the marts.
2. Define model relationships.
3. Write DAX measures.
4. Create page wireframes.
5. Create reconciliation queries.
6. Document exact manual construction steps.
7. Report the `.pbix` as not built or not verified.
8. Request the smallest necessary user action.

Do not claim a working `.pbix` exists when it has not been inspected.

Expect final desktop assembly and screenshot capture to require one or two user-assisted days.

That does not permit weaker data preparation or validation.

---

## 24. Statistical report

The report is the methodological source of truth.

Prefer Quarto.

Successful HTML rendering is mandatory.

PDF is optional if the toolchain is unavailable.

Required sections:

1. Executive summary
2. Business problem
3. Stakeholders and decisions
4. Dataset provenance
5. Dataset semantics
6. Feasibility findings
7. Measurement trust audit
8. Evaluation design
9. Leakage controls
10. Sensor-selection rule
11. I-MR methodology and findings
12. EWMA methodology and findings
13. PCA methodology
14. T-squared findings
15. Q/SPE findings
16. Contribution analysis
17. Association methodology
18. Cliff’s delta
19. Mann–Whitney results
20. BH-FDR
21. Dependence sensitivity
22. Risk-ranking models
23. Baselines
24. Calibration
25. Review-budget evaluation
26. Uncertainty
27. Simulation, if completed
28. Temporal stability
29. Limitations
30. Prohibited interpretations
31. Recommendations
32. Next steps

Show formulas or precise definitions where they improve auditability.

Keep the report understandable to both data analysts and engineering stakeholders.

---

## 25. Engineering decision memo

Create an approximately two-page memo for a yield, process, or quality manager.

Answer:

- What data was analyzed?
- Which quality issues limit trust?
- Which measurements were excluded?
- What did monitoring identify?
- Which measurements are investigation candidates?
- Which frozen review budget is recommended?
- Why was it chosen?
- What workload does it create?
- How many failures were detected retrospectively?
- How many were missed?
- How many non-failures were reviewed?
- How uncertain are the estimates?
- What should an engineer investigate next?
- What cannot be concluded?

The recommendation must use the budget frozen and committed before final-test evaluation.

The memo may discuss F2 for comparison but must explain its instability.

Do not claim:

- causal root causes;
- confirmed physical mechanisms;
- financial savings;
- production deployment;
- guaranteed future detection.

---

## 26. Testing requirements

At minimum, test or deterministically verify:

- source parsing;
- label normalization;
- schema;
- timestamps;
- split boundaries;
- tied-timestamp handling;
- train-only transformations;
- sensor exclusions;
- label-blind sensor selection;
- I-MR calculations;
- EWMA recursion;
- EWMA limits;
- severity calculations;
- missing-severity behavior;
- zero severity for entities without statistics;
- PCA score shapes;
- PCA thresholds;
- contribution shapes;
- top-ten contribution retention;
- absence of final-test rows from fitting;
- absence of final-test rows from association analysis;
- BH correction;
- BY or approved sensitivity method;
- monitoring-signal count;
- tie-breaker ordering;
- alert-budget calculations;
- frozen-budget configuration;
- review-queue reason codes;
- SQL grain and key expectations;
- SQL/Python reconciliations;
- deterministic seeds.

Add a small end-to-end smoke test.

Do not add hundreds of low-value tests.

Never claim a check passed unless it actually ran successfully.

---

## 27. Reproducibility

Provide documented commands or a CLI for:

```text
acquire or locate data
validate source data
build DuckDB tables
build SQL marts
run measurement audit
run sensor selection
run SPC
run PCA
run contributions
run associations
train models
select and freeze budget
evaluate final test
build review queue
export dashboard marts
render report
run tests
```

The budget-selection and final-evaluation commands must be separable so the decision can be committed first.

Requirements:

- project-relative paths;
- no personal absolute paths;
- configuration separate from logic;
- deterministic seeds;
- idempotent outputs where practical;
- documented environment;
- managed dependencies;
- no secrets.

### README requirements

Include:

- title;
- business problem;
- stakeholder;
- decision;
- measured results;
- architecture diagram;
- dataset provenance;
- license;
- acquisition instructions;
- setup;
- commands;
- dashboard screenshots;
- methods;
- metrics with uncertainty;
- limitations;
- repository navigation;
- interview-ready explanation.

Do not publish placeholders as results.

Do not publish unsupported hiring-market claims.

---

## 28. Terminology rules

Use:

- **production entity**, not wafer, die, lot, or tool run;
- **measurement** or **anonymized sensor**, not a named parameter;
- **control limit**, not specification limit;
- **excursion signal** or **statistical alert**, not confirmed fault;
- **failure-associated measurement** or **investigation candidate**, not root cause;
- **retrospective ranking performance**, not guaranteed prediction;
- **reference period**, not known in-control period unless justified;
- **development period** for allowed training and calibration analysis;
- **final test** only for frozen retrospective evaluation;
- **frozen decision**, not preregistered decision.

---

## 29. AGENTS.md requirements

Create a concise `AGENTS.md`.

It must preserve across sessions:

1. Section 9 exclusions.
2. Section 14 leakage rules.
3. Final-test access restrictions.
4. Section 28 terminology.
5. Frozen-budget rule.
6. Maximum six configurations per model.
7. Required validation commands.
8. Prohibited secret, raw, cache, generated, and lock files.
9. Requirement to inspect project status and Git state before resuming.
10. Requirement to stop after each approved phase.

Do not copy the entire project plan into `AGENTS.md`.

---

## 30. Interview guide

Create `docs/interview_guide.md` explaining:

1. Why the project was selected.
2. What business decision it supports.
3. Why rows are called production entities.
4. Why chronological evaluation matters.
5. Why accuracy is misleading.
6. How I-MR works.
7. How EWMA differs from I-MR.
8. How PCA is used for monitoring.
9. How T-squared differs from Q/SPE.
10. How contribution analysis works.
11. Why selection must be label-blind.
12. Why Cliff’s delta is used.
13. What Mann–Whitney does and does not prove.
14. Why FDR correction is needed.
15. How correlation affects multiplicity.
16. Why association is not causation.
17. Why the design uses wide and long tables.
18. Why the two models handle missingness differently.
19. How alert budgets convert scores into decisions.
20. Why the budget is frozen before final evaluation.
21. Why F2 can be unstable.
22. What limitations remain.
23. What real fabrication data would add.

---

## 31. Implementation phases

Follow the separate workflow.

Stop after every phase and wait for approval.

### Phase 1 — Feasibility, foundation, and data trust

#### Objectives

- Perform the repository startup audit.
- Initialize or align the repository.
- Acquire or locate SECOM.
- Verify provenance and license.
- Build deterministic ingestion.
- Normalize labels and timestamps.
- Perform the feasibility audit.
- Perform the measurement-quality audit.
- Evaluate chronological partitions.
- Count failures in each candidate period.
- Choose chronological holdout or automatically switch to approved rolling-origin evaluation when supported.
- Retain a final directional block whenever feasible.
- Create initial DuckDB tables.
- Create persistent project memory.
- Create the requirements roadmap.

#### Outputs

- Provenance record.
- Checksum where practical.
- Source-validation report.
- Label and timestamp summary.
- Missingness report.
- Sensor-quality report.
- Exclusion log.
- Split comparison.
- Evaluation design with exact counts.
- Development-period definition.
- Final-directional-block definition where applicable.
- Initial DuckDB schema.
- Ingestion and split tests.
- Updated documentation.

#### Stop/go gate

Continue only if:

- parsing is reproducible;
- labels are understood;
- timestamps support a defensible design;
- enough measurements remain;
- failure counts are explicit;
- uncertainty limitations are explicit;
- temporal evaluation is documented;
- final-period label access has been limited to permitted counts;
- no data-semantics issue invalidates the project.

If holdout failures are too sparse, switch to rolling-origin without stopping merely to request approval.

If the final block must be dropped entirely, document the evidence and stop for approval.

Stop after Phase 1.

---

### Phase 2 — SQL architecture and univariate monitoring

#### Objectives

- Complete the wide/long DuckDB architecture.
- Implement SQL transformations.
- Build initial marts.
- Freeze sensor-selection rules.
- Select the monitoring subset.
- Implement I-MR.
- Implement EWMA.
- Generate traceable signals.
- Document missingness and autocorrelation.
- Add focused tests.

#### Acceptance criteria

- Selection is reproducible.
- Labels are not used for selection.
- Limits use reference data only.
- Alerts trace to entities and versions.
- SQL and Python reconcile.
- Missing-data behavior is explicit.
- Autocorrelation caveats are documented.
- Tests pass.

Stop after Phase 2.

---

### Phase 3 — PCA and contributions

#### Objectives

- Build training-only preprocessing.
- Fit PCA.
- Implement T-squared.
- Implement Q/SPE.
- Calibrate limits without final outcomes.
- Calculate contributions for every entity.
- Persist the top ten measurements per statistic and entity.
- Compare univariate and multivariate alerts.
- Add tests.
- Optionally implement the Tier B simulation.

#### Acceptance criteria

- Final-test data is absent from fitting.
- Limits are frozen correctly.
- Alerts are traceable.
- Ten T-squared contributions exist per eligible entity.
- Ten Q/SPE contributions exist per eligible entity.
- Contribution outputs reconcile with scores.
- Mathematical tests pass.
- Simulation remains separate if implemented.

Stop after Phase 3.

---

### Phase 4 — Associations, risk ranking, and policy

#### Objectives

- Freeze modeling and monitoring choices.
- Build development-period associations.
- Calculate Cliff’s delta.
- Calculate approximate intervals.
- Run Mann–Whitney comparisons.
- Apply BH-FDR.
- Apply dependence sensitivity.
- Train logistic regression.
- Train HistGradientBoosting.
- Enforce six configurations per model.
- Evaluate prevalence and monitoring baselines.
- Evaluate calibration.
- Evaluate 1%, 5%, 10%, 20%, and fixed top-k budgets.
- Report F2 as diagnostic only.
- Select the headline budget from calibration.
- Record the choice in `DECISIONS.md`.
- Commit the frozen decision.
- Only then run final-test evaluation.
- Build the review queue.

#### Acceptance criteria

- Final test is excluded from associations.
- Association outputs include sample sizes, effects, intervals, corrections, and caveats.
- Preprocessing remains training-only.
- Searches stay within six configurations per model.
- The frozen-budget commit precedes final evaluation in Git history.
- PR-AUC is reported.
- Calibration is reported.
- Budget results include counts and uncertainty.
- Baselines are included.
- Queue reason codes are interpretable.
- Queue totals reconcile.
- Sparse-failure conclusions remain directional.

Do not require models to beat baselines.

Do not alter the evaluation after disappointing results.

Stop after Phase 4.

---

### Phase 5 — Decision products

#### Objectives

- Complete dashboard marts.
- Build the Power BI dashboard.
- Reconcile Power BI totals.
- Render the statistical report.
- Write the decision memo.
- Complete architecture documentation.
- Complete dictionaries.
- Complete methods and limitations.
- Complete interview documentation.
- Capture screenshots.

#### Acceptance criteria

- All dashboard pages support their intended decisions.
- Totals reconcile across Power BI, SQL, and Python.
- HTML report renders.
- Screenshots are current.
- Memo uses the frozen policy.
- Memo is concise and non-causal.
- A reviewer can understand the problem, method, result, tradeoff, and limitations in about five minutes.

If user-assisted Power BI work is required, report exactly what remains.

Stop after Phase 5.

---

### Phase 6 — Final audit and release

Verify:

- every Tier A requirement;
- no prohibited claims;
- no secrets;
- no restricted raw data;
- no caches;
- no lock files;
- no unnecessary large files;
- clean reproduction;
- README accuracy;
- screenshot accuracy;
- architecture accuracy;
- Git history quality;
- measured resume bullets;
- explicit limitations;
- explicit unverified items.

Do not add new features during the audit without approval.

---

## 32. Definition of done

The project is complete only when:

- Tier A is complete or an approved exception exists;
- every phase passes its gate;
- required tests actually ran;
- reconciliations actually ran;
- no known final-test leakage exists;
- the frozen budget predates final evaluation;
- HTML report renders;
- the Power BI dashboard has been inspected;
- Power BI reconciles with SQL and Python;
- the decision memo is complete;
- the repository is reproducible;
- terminology is honest;
- metrics include counts and uncertainty;
- simulation is clearly separated;
- source and generated data are separated;
- Git status is understood;
- Git history is meaningful;
- no unresolved core-quality gap remains.

---

## 33. Resume bullets after completion

Do not publish placeholders as results.

Replace brackets only with verified evidence.

Potential bullets:

- Built a semiconductor process-monitoring system over **[verified entity count] production entities and [verified measurement count] anonymized process measurements**, combining DuckDB/SQL data-quality controls, I-MR/EWMA monitoring, and PCA T-squared/Q analysis to generate an auditable engineering-review queue.

- Applied Cliff’s delta, Mann–Whitney comparisons, approximate bootstrap intervals, and false-discovery-rate correction across **[N] eligible measurements**, identifying **[N] failure-associated investigation candidates** while separating statistical association from causal root cause.

- Developed time-aware risk-ranking benchmarks and a three-page Power BI decision dashboard, retrospectively capturing **[X]% of failures at a frozen [Y]% review budget**, with **[Z] non-failures reviewed** and **[uncertainty statement]** on the untouched evaluation period.

If no model provides a defensible improvement, write an honest bullet about the monitoring and evaluation system instead of inventing success.

---

## 34. First required action

Follow the separate workflow prompt.

After receiving this plan:

1. Read the workflow completely.
2. Read this plan completely.
3. Inspect all applicable `AGENTS.md` files.
4. Inspect the repository.
5. Inspect Git status and history.
6. Perform the startup audit.
7. Restate the approved scope.
8. Identify only material ambiguities.
9. Save this plan as `docs/PROJECT_PLAN.md`.
10. Create or update:
    - `AGENTS.md`;
    - `docs/PROJECT_STATUS.md`;
    - `docs/DECISIONS.md`.
11. Ensure `AGENTS.md` contains the persistent rules from Section 29.
12. Map every requirement to a phase.
13. Define exact Phase 1 implementation units.
14. Define Phase 1 acceptance checks.
15. If no material issue blocks execution, begin Phase 1 immediately.
16. Execute, verify, critique, repair, document, and commit according to the workflow.
17. Stop after Phase 1 with an evidence-based completion or blocker report.
18. Wait for my approval before Phase 2.

Do not respond only with instructions telling me how to do the work.

Use the available tools and execute the approved Phase 1 work directly.
