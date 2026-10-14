# Phase 2 univariate monitoring design

## Frozen monitoring-measurement selection

Rule version `monitoring-selection-v1` uses only the 940-entity reference period and never accepts failure labels as an input.

1. Start with the 440 measurements that passed the Phase 1 reference-only quality audit.
2. Calculate reference completeness, temporal coverage, and dimensionless robust variation: `IQR / (abs(median) + IQR)`.
3. Convert each component to a percentile using average ranks for ties and average the three percentiles equally.
4. Sort by descending score and then sensor ID.
5. Traverse the ranking greedily, rejecting a candidate if its absolute pairwise reference correlation with any already selected measurement is at least 0.90.
6. Stop after 12 selected measurements, within the approved range of 8–15.

The frozen set is:

| Order | Measurement | Ranking score | Maximum correlation at decision |
|---:|---|---:|---:|
| 1 | `measurement_104` | 0.768561 | 0.000000 |
| 2 | `measurement_499` | 0.768561 | 0.019503 |
| 3 | `measurement_500` | 0.768561 | 0.017541 |
| 4 | `measurement_511` | 0.768561 | 0.019374 |
| 5 | `measurement_082` | 0.762121 | 0.044854 |
| 6 | `measurement_010` | 0.760606 | 0.054361 |
| 7 | `measurement_009` | 0.759091 | 0.063741 |
| 8 | `measurement_093` | 0.758333 | 0.047452 |
| 9 | `measurement_077` | 0.757576 | 0.087774 |
| 10 | `measurement_080` | 0.756061 | 0.234945 |
| 11 | `measurement_092` | 0.754545 | 0.097807 |
| 12 | `measurement_075` | 0.753788 | 0.142716 |

The maximum absolute correlation anywhere within the selected set is 0.234945. Across all 590 measurements, selection statuses are 12 selected, 3 rejected as redundant, 425 below the target rank, and 150 excluded by Phase 1 quality rules.

## Individuals and Moving Range

For each selected measurement, reference observations estimate:

```text
center = mean(reference observations)
MR_t = abs(x_t - x_(t-1)) only when both adjacent entities are observed
MR_bar = mean(reference MR_t)
sigma_hat = MR_bar / 1.128
I limits = center +/- 3 * sigma_hat
MR LCL = 0
MR UCL = 3.267 * MR_bar
```

Limits are frozen as `imr-reference-v1`. They are control limits, not engineering specification limits.

## EWMA

EWMA version `ewma-reference-time-varying-v1` uses lambda 0.20, L 3.0, the same reference center and short-term sigma estimate, and starts at the reference center:

```text
z_t = lambda * x_t + (1 - lambda) * z_(t-1)

limit distance_t = L * sigma_hat * sqrt(
    lambda / (2 - lambda) * (1 - (1 - lambda)^(2t))
)
```

The chart display and alert logic use the same time-varying limits.

## Missing values and timestamp gaps

- No measurement is interpolated.
- A missing value produces no I or EWMA statistic and cannot signal.
- A missing value does not update or reset the EWMA state; the next observed value continues from the prior observed state.
- Moving ranges require adjacent production entities with observed values. A missing value breaks adjacency, so the chart never bridges over missingness.
- Limits are indexed by observed production-entity sequence, not elapsed clock time. Irregular timestamp gaps do not reset or duration-weight a chart because the public data provides no justified process cadence. This limits interpretation when long gaps correspond to unobserved operating changes.

Selected measurements have no missing reference observations, 12 missing calibration values out of 3,768 sensor-entity cells, and 100 missing final-period values out of 3,756. These are structural monitoring counts only; no outcome-conditioned final-period analysis was performed.

## Autocorrelation and alert volume

Reference lag-1 correlations range from -0.070 to 0.475. `measurement_080` is 0.475 and `measurement_075` is 0.386; the other ten are below 0.30 in absolute value. Serial correlation and nonstationarity can increase or cluster nominal false alarms, so signals are investigation prompts rather than confirmed faults.

| Period | Method | Available statistics | Signals | Signal rate | Distinct entities signaled |
|---|---|---:|---:|---:|---:|
| Reference | I | 11,280 | 203 | 1.80% | 179 |
| Reference | MR | 11,268 | 207 | 1.84% | 188 |
| Reference | EWMA | 11,280 | 900 | 7.98% | 618 |
| Calibration | I | 3,756 | 69 | 1.84% | 55 |
| Calibration | MR | 3,744 | 95 | 2.54% | 73 |
| Calibration | EWMA | 3,756 | 176 | 4.69% | 142 |
| Final period | I | 3,656 | 25 | 0.68% | 23 |
| Final period | MR | 3,650 | 41 | 1.12% | 37 |
| Final period | EWMA | 3,656 | 215 | 5.88% | 165 |

Any univariate method signaled 679 reference, 173 calibration, and 190 final-period production entities. These are alert-volume counts—not false-positive counts—because Phase 2 does not compare alerts with outcomes. Outcome overlap, workload tradeoffs, and non-failures reviewed belong to the frozen retrospective policy evaluation in Phase 4.
