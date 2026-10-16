"""Development-only measurement association analysis."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu


def _adjust_fdr(p_values: np.ndarray, dependency_factor: float = 1.0) -> np.ndarray:
    """Benjamini-Hochberg adjustment, with BY obtained via harmonic factor."""
    count = len(p_values)
    order = np.argsort(p_values, kind="stable")
    ranked = p_values[order]
    adjusted_ranked = ranked * count * dependency_factor / np.arange(1, count + 1)
    adjusted_ranked = np.minimum.accumulate(adjusted_ranked[::-1])[::-1]
    adjusted = np.empty(count, dtype=float)
    adjusted[order] = np.clip(adjusted_ranked, 0.0, 1.0)
    return adjusted


def _cliffs_delta(failure_values: np.ndarray, nonfailure_values: np.ndarray) -> float:
    if not len(failure_values) or not len(nonfailure_values):
        return np.nan
    statistic = mannwhitneyu(
        failure_values, nonfailure_values, alternative="two-sided", method="asymptotic"
    ).statistic
    return float(2.0 * statistic / (len(failure_values) * len(nonfailure_values)) - 1.0)


def _bootstrap_delta(
    failure_values: np.ndarray,
    nonfailure_values: np.ndarray,
    replicates: int,
    seed: int,
) -> tuple[float, float, int]:
    """Outcome-stratified approximate bootstrap interval for Cliff's delta."""
    generator = np.random.default_rng(seed)
    estimates = np.empty(replicates, dtype=float)
    for replicate in range(replicates):
        failure_sample = generator.choice(failure_values, len(failure_values), replace=True)
        nonfailure_sample = generator.choice(
            nonfailure_values, len(nonfailure_values), replace=True
        )
        estimates[replicate] = _cliffs_delta(failure_sample, nonfailure_sample)
    usable = estimates[np.isfinite(estimates)]
    if not len(usable):
        return np.nan, np.nan, 0
    return (
        float(np.quantile(usable, 0.025)),
        float(np.quantile(usable, 0.975)),
        len(usable),
    )


def analyze_associations(
    measurements: pd.DataFrame,
    outcomes: np.ndarray,
    sensor_ids: list[str],
    config: dict[str, Any],
) -> pd.DataFrame:
    """Calculate robust, multiplicity-aware associations on development data."""
    settings = config["phase4"]
    alpha = float(settings["significance_alpha"])
    replicates = int(settings["association_bootstrap_replicates"])
    seed = int(config["project"]["random_seed"])
    failure_mask = outcomes.astype(bool)
    records: list[dict[str, Any]] = []
    for index, sensor_id in enumerate(sensor_ids):
        values = measurements[sensor_id].to_numpy(dtype=float)
        failure_values = values[failure_mask & np.isfinite(values)]
        nonfailure_values = values[~failure_mask & np.isfinite(values)]
        delta = _cliffs_delta(failure_values, nonfailure_values)
        ci_low, ci_high, usable = _bootstrap_delta(
            failure_values,
            nonfailure_values,
            replicates,
            seed + index,
        )
        test = mannwhitneyu(
            failure_values,
            nonfailure_values,
            alternative="two-sided",
            method="asymptotic",
        )
        records.append(
            {
                "sensor_id": sensor_id,
                "failure_entity_count": int(failure_mask.sum()),
                "nonfailure_entity_count": int((~failure_mask).sum()),
                "failure_nonmissing_count": len(failure_values),
                "nonfailure_nonmissing_count": len(nonfailure_values),
                "failure_missing_fraction": float(
                    np.mean(~np.isfinite(values[failure_mask]))
                ),
                "nonfailure_missing_fraction": float(
                    np.mean(~np.isfinite(values[~failure_mask]))
                ),
                "failure_median": float(np.median(failure_values)),
                "failure_q1": float(np.quantile(failure_values, 0.25)),
                "failure_q3": float(np.quantile(failure_values, 0.75)),
                "nonfailure_median": float(np.median(nonfailure_values)),
                "nonfailure_q1": float(np.quantile(nonfailure_values, 0.25)),
                "nonfailure_q3": float(np.quantile(nonfailure_values, 0.75)),
                "cliffs_delta": delta,
                "cliffs_delta_direction": "failure_higher_positive",
                "cliffs_delta_ci_lower": ci_low,
                "cliffs_delta_ci_upper": ci_high,
                "bootstrap_method": "outcome_stratified_approximate",
                "bootstrap_usable_replicates": usable,
                "mann_whitney_u": float(test.statistic),
                "raw_p_value": float(test.pvalue),
                "method_version": settings["association_method_version"],
            }
        )
    result = pd.DataFrame(records)
    p_values = result["raw_p_value"].to_numpy()
    result["bh_adjusted_p_value"] = _adjust_fdr(p_values)
    harmonic = float(np.sum(1.0 / np.arange(1, len(result) + 1)))
    result["by_adjusted_p_value"] = _adjust_fdr(p_values, harmonic)
    result["survives_bh"] = result["bh_adjusted_p_value"] <= alpha
    result["survives_by"] = result["by_adjusted_p_value"] <= alpha
    result["interval_excludes_zero"] = (
        (result["cliffs_delta_ci_lower"] > 0)
        | (result["cliffs_delta_ci_upper"] < 0)
    )
    result["investigation_status"] = np.select(
        [
            result["survives_by"] & result["interval_excludes_zero"],
            result["survives_bh"] & result["interval_excludes_zero"],
            result["interval_excludes_zero"],
        ],
        ["BY-supported candidate", "BH-supported candidate", "effect-only candidate"],
        default="not prioritized",
    )
    result["association_rank"] = (
        result.assign(
            status_order=np.select(
                [result["survives_by"], result["survives_bh"]], [0, 1], default=2
            ),
            absolute_effect=result["cliffs_delta"].abs(),
            interval_width=(
                result["cliffs_delta_ci_upper"] - result["cliffs_delta_ci_lower"]
            ),
            total_nonmissing=(
                result["failure_nonmissing_count"]
                + result["nonfailure_nonmissing_count"]
            ),
        )
        .sort_values(
            [
                "status_order",
                "absolute_effect",
                "interval_width",
                "total_nonmissing",
                "sensor_id",
            ],
            ascending=[True, False, True, False, True],
            kind="mergesort",
        )
        .reset_index()
        .assign(rank=lambda frame: np.arange(1, len(frame) + 1))
        .set_index("index")["rank"]
        .reindex(result.index)
        .astype(int)
    )
    return result
