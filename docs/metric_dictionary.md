# Dashboard metric dictionary

| Metric | Definition | Grain/filter | Interpretation guardrail |
| --- | --- | --- | --- |
| Entity count | Distinct `entity_id` | Dataset or selected split | Source rows are called production entities; physical unit is unknown. |
| Failure count/rate | Sum/mean of mapped `failure_indicator` | Entity | Retrospective source label, not a forecast. |
| Usable measurement count | Sensors with `quality_status = eligible` | Sensor | Eligibility means analytically usable under frozen rules. |
| Excluded measurement count | Sensors with `quality_status = excluded` | Sensor | Reasons are data-quality rules, not process judgment. |
| Monitoring measurement count | Sensors with `is_selected` | Sensor | Correlation-aware label-blind selection; 12 sensors. |
| Univariate alert entity | Any I/MR/EWMA violation for an entity | Entity | Statistical signal, not failure/specification breach. |
| T-squared alert | T-squared exceeds reference empirical q99 | Entity | Monitors modeled multivariate variation. |
| Q/SPE alert | Q residual exceeds reference empirical q99 | Entity | Monitors residual variation. |
| Alert overlap | Any univariate and any multivariate alert | Entity | Agreement prioritizes review; it is not causality. |
| Cliff’s delta | Probability-scale rank effect, failure minus nonfailure | Development sensor | Positive means higher values among failures. |
| BH/BY adjusted p-value | Multiplicity-adjusted Mann–Whitney p-value | Development sensor | BY is more conservative under dependence. |
| PR-AUC | Area under precision-recall curve | Model × final block | Preferred discrimination metric for sparse failures. |
| ROC-AUC | Pairwise ranking discrimination | Model × final block | Can appear optimistic under imbalance; report with PR-AUC. |
| Brier score | Mean squared probability error | Probabilistic model × final block | Lower is better; prevalence is a required baseline. |
| ECE | Weighted bin gap between predicted and observed rates | Probabilistic model × final block | Descriptive; no interval is claimed. |
| Reviewed entities | Ceiling-rounded/fixed count selected by rank | Model × policy × period | Dataset-period workload, not staffing advice. |
| Review precision | Detected failures / reviewed entities | Policy | Sparse-event uncertainty interval must accompany it. |
| Review recall | Detected / all failures | Policy | Sparse-event uncertainty interval must accompany it. |
| Reason codes | Semicolon list of frozen model, alert, and quality reasons | Queue entity | Explanation of recorded evidence, not a causal explanation. |
