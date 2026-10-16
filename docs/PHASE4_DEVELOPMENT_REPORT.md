# Phase 4 development checkpoint

This checkpoint predates all final-test predictive and policy evaluation.

## Frozen model selection

Four logistic-regression and four HistGradientBoosting configurations were fitted on 940 reference entities and evaluated on 314 calibration entities. `hgb-01` won the predeclared predictive-model PR-AUC rule with PR-AUC 0.050925, ROC-AUC 0.620762, Brier score 0.053736, and expected calibration error 0.117081. Calibration contains only 11 failures, so these estimates are unstable. The fixed monitoring baseline achieved PR-AUC 0.143282 and the prevalence baseline 0.035032; the model is not claimed to outperform monitoring.

Raw probabilities are retained without post-hoc recalibration. This method, the 440-feature set, model configuration, and random seed were frozen before combined-development associations.

## Development associations

Association analysis uses exactly the 1,254 reference-plus-calibration entities (87 failures) and excludes the final test. Every eligible measurement includes outcome sample sizes, outcome-specific missingness, medians and quartiles, Cliff's delta with failure-higher defined as positive, a 250-replicate outcome-stratified approximate interval, two-sided Mann–Whitney U, raw p-value, BH adjustment, and BY dependence sensitivity.

- 20 of 440 measurements survive BH at 0.05.
- 9 survive BY at 0.05.
- 78 approximate effect intervals exclude zero.
- Every measurement produced all 250 usable bootstrap replicates.

Outcome-stratified intervals are descriptive and do not preserve temporal dependence. Mann–Whitney is not interpreted automatically as a median test because distribution shapes may differ. Candidate ranking considers correction status, absolute effect, interval width, usable sample size, and stable sensor ID—not p-value alone. PCA top-contribution frequency and frozen-model permutation evidence are stored beside association evidence; agreement does not establish causality.

## Frozen review budget

The selected model's predeclared 10% calibration scenario reviews 32 of 314 entities and detects 2 of 11 failures. Precision is 0.0625 and recall is 0.1818; approximate stratified intervals are 0–0.1538 and 0–0.4545. The 20% scenario detects no additional failure, so the headline budget is frozen at 10% before final evaluation. This is a dataset-period review scenario, not an invented operational staffing level.

The F2-maximizing threshold is retained only as a diagnostic and is not the recommendation.
