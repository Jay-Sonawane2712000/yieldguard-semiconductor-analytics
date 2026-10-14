# Phase 3 completion report

Phase 3 is complete. It adds a frozen, label-blind PCA monitor over all 440 quality-eligible anonymous measurements. Reference-only preprocessing and PCA retained 121 components, explaining 90.1631% of reference variance. Empirical 99th-percentile reference limits are 551.588214 for Hotelling's T-squared and 111.311774 for Q/SPE.

## Evidence

| Split | Entities | Univariate-alert entities | T-squared alerts | Q/SPE alerts | Any multivariate alert | Uni/multivariate overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Reference | 940 | 679 | 9 | 9 | 18 | 10 |
| Calibration | 314 | 173 | 3 | 63 | 63 | 33 |
| Final test | 313 | 190 | 13 | 85 | 85 | 60 |

These are monitoring-volume comparisons only. No failure outcome was loaded, grouped, scored, or associated in Phase 3, including for the final-test period.

The build persists 1,567 entity-level score rows, 31,340 top-ten contribution rows, and 53,240 component-loading rows. Every entity has exactly ten T-squared and ten Q/SPE contributors. Full decompositions reconcile to scores before top-ten retention.

## Acceptance result

- Final-test data is absent from every fit; only frozen transformation and scoring are applied outside reference.
- Model and threshold versions, feature preprocessing values, and all loadings are persisted.
- Separate and joint T-squared/Q alerts are traceable at entity grain.
- Univariate and multivariate alerts are compared without outcome fields.
- Mathematical leakage, score, threshold, contribution, and retention tests pass.
- Optional Tier B simulation was not implemented; the core Phase 3 scope is complete and simulation remains separate.

Phase 4 has not begun and requires explicit approval.
