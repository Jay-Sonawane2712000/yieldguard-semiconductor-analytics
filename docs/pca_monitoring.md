# PCA multivariate monitoring method

## Leakage boundary and fitted population

Phase 3 reads raw measurement values and only these persisted entity fields: identifier, source row, timestamp, chronological order, and split. It never selects or loads the outcome fields. Median imputation, standard scaling, PCA, and both thresholds are fitted on the 940-entity **reference period** only. Calibration and final-test measurements are transformed with those frozen artifacts; their outcomes remain untouched for Phase 4.

All 440 measurements marked `quality_status = 'eligible'` in Phase 1 enter PCA. Each missing value is replaced by that measurement's reference median. The imputed reference mean and population standard deviation then define standardization for every split.

## Component and limit rules

PCA uses a full deterministic singular-value decomposition. It retains the fewest components whose cumulative reference explained-variance ratio reaches 90%. The fitted model retains 121 components and 90.163054% of reference variance.

For standardized row vector `x`, retained loading matrix `P`, score vector `t = xP'`, and retained eigenvalues `lambda`:

- Hotelling's T-squared is `sum(t_j^2 / lambda_j)`.
- Q/SPE is `sum((x - tP)^2)`.

Separate limits are empirical 99th percentiles of the 940 reference scores, using NumPy's `higher` quantile rule. They are not theoretical specification limits and do not establish that the reference period is known to be in control. The frozen limits are 551.588214 for T-squared and 111.311774 for Q/SPE. A score must be strictly greater than its limit to alert.

## Contributions

Full T-squared contributions use `x * ((t / lambda)P)` by measurement. They are signed and sum to the T-squared score; absolute magnitude determines rank and share because positive and negative terms can offset. Q/SPE contributions are squared residuals, are nonnegative, and sum to Q/SPE. The pipeline verifies those full decompositions before persisting the ten greatest absolute contributions per entity and statistic. Stored shares use the total absolute contribution across all 440 measurements as denominator.

This yields exactly 10 T-squared and 10 Q/SPE rows for each of 1,567 entities, or 31,340 contribution rows. A top-ten subset is intentionally an explanation view and need not itself sum to the full score.

## Interpretation limits

An alert means a measurement profile is unusual relative to the empirical reference distribution. It is not a failure prediction, causal diagnosis, specification breach, or proof of a physical mechanism. Anonymous measurement identifiers must not be assigned invented meanings. Phase 3 alert counts are descriptive only and contain no outcome comparison.
