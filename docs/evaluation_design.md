# Phase 1 evaluation design

## Selected design

YieldGuard uses a tie-safe chronological 60%/20%/20% holdout:

| Period | Production entities | Failures | Start | End | Approved use |
|---|---:|---:|---|---|---|
| Reference | 940 | 76 | 2008-07-19 11:55 | 2008-09-20 05:34 | Training/reference fitting and reference-only quality rules |
| Calibration | 314 | 11 | 2008-09-20 06:08 | 2008-10-02 20:54 | Approved development choices and later policy calibration |
| Final test | 313 | 17 | 2008-10-02 21:32 | 2008-10-17 06:07 | Untouched frozen retrospective evaluation in Phase 4 |

This was the first configured candidate with at least 10 failures in both calibration and final-test periods. The split uses stable chronological ordering and moves boundaries to timestamp-group ends, so no timestamp tie crosses a period boundary.

## Candidate evidence

| Allocation | Reference entities/failures | Calibration entities/failures | Final entities/failures | Feasibility result |
|---|---:|---:|---:|---|
| 60/20/20 | 940 / 76 | 314 / 11 | 313 / 17 | Selected; both later periods meet configured minimum |
| 65/20/15 | 1,019 / 76 | 313 / 19 | 235 / 9 | Final period below minimum |
| 70/15/15 | 1,097 / 78 | 235 / 17 | 235 / 9 | Final period below minimum |
| 70/20/10 | 1,097 / 78 | 313 / 23 | 157 / 3 | Final period below minimum |

The choice follows the preconfigured candidate order and feasibility thresholds, not model performance. Rolling-origin evaluation was not triggered because the preferred holdout is feasible. The development period for later allowed development analyses is the combined reference and calibration periods (1,254 entities, 87 failures), but the project plan’s required freezing order still applies before using calibration outcomes in association analysis.

## Timestamp evidence and leakage controls

- All 1,567 timestamps parsed with the documented day-first format.
- Coverage is 2008-07-19 11:55 through 2008-10-17 06:07.
- There are 1,534 unique timestamps; 32 timestamp values are duplicated, involving 65 entities, with a maximum tie size of 3.
- There are no timestamp reversals in original source order, no reversals after stable chronological sorting, and no split-boundary tie violations.
- The median positive gap is 2,280 seconds; the maximum observed gap is 175,080 seconds.
- Phase 1 accessed final outcomes only to count the 17 failures required for feasibility. It did not compute final-test associations, outcome-conditioned measurement statistics, predictive metrics, policy results, or model comparisons.

Final-test estimates will be directional and accompanied by uncertainty intervals because only 17 failures occur in the final period.
