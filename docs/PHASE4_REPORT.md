# Phase 4 completion report

Phase 4 is complete. The model, calibration approach, monitoring baseline, policy scenarios, and 10% headline budget were frozen before final-test evaluation. Git commit `ccfaf2f` contains the budget decision and precedes all final metrics in repository history.

## Development evidence

- Eight complete model configurations were evaluated: four logistic and four HistGradientBoosting.
- `hgb-01` was selected by the predeclared predictive-model calibration PR-AUC rule.
- The fixed monitoring baseline was stronger than every predictive model on calibration; this is reported rather than hidden.
- All 440 eligible measurements received development-only association outputs.
- 20 associations survive BH and 9 survive BY at 0.05.
- Intervals use 250 outcome-stratified replicates and are explicitly approximate because temporal dependence is not preserved.

The leading BY-supported investigation candidate is `measurement_059`, with Cliff's delta 0.4550 and approximate interval 0.3337–0.5499. Positive delta consistently means higher observed values among failures. This is association evidence, not causal root cause or a physical interpretation.

## Frozen final evaluation

The final block contains 313 entities and 17 failures. Estimates are directional because failures are sparse.

| Ranking | PR-AUC | ROC-AUC | Calibration summary |
| --- | ---: | ---: | ---: |
| Frozen `hgb-01` | 0.0700 (0.0560–0.1209) | 0.5982 (0.4847–0.7210) | Brier 0.0823; ECE 0.1390 |
| Fixed monitoring baseline | 0.1106 (0.0442–0.2391) | 0.4714 (0.3440–0.5948) | Not a probability model |
| Development-prevalence baseline | 0.0543 | 0.5000 | Brier 0.0516; ECE 0.0515 |

Intervals are 1,000-replicate outcome-stratified approximate intervals and do not preserve temporal dependence. The model provides modest retrospective enrichment over prevalence but does not beat the monitoring baseline on PR-AUC and has worse probability calibration than the constant prevalence baseline.

## Frozen 10% review scenario

| Ranking | Reviewed | Failures detected | Failures missed | Non-failures reviewed | Precision | Recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen `hgb-01` | 32 | 2 | 15 | 30 | 0.0625 | 0.1176 |
| Fixed monitoring baseline | 32 | 2 | 15 | 30 | 0.0625 | 0.1176 |
| Prevalence baseline | 32 | 1 | 16 | 31 | 0.0313 | 0.0588 |

For the headline model queue, the approximate precision interval is 0–0.1563 and recall interval is 0–0.2941. The policy is a constrained **dataset-period review scenario**, not an operational staffing recommendation.

## Queue and interpretation

The queue contains all 313 final entities and marks exactly 32 for review. Each row includes frozen model score/rank, I-MR and EWMA status, T-squared and Q/SPE status, leading stored contributions, eligible-measurement missingness, retrospective outcome, and semicolon-delimited reason codes. Totals reconcile exactly.

No causal root-cause, specification-limit, savings, capacity, or operational-reliability claim is made. Phase 5 has not begun.
