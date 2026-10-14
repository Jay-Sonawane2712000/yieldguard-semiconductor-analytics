"""Deterministic, label-blind monitoring-measurement selection."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _robust_variation(frame: pd.DataFrame) -> pd.Series:
    first = frame.quantile(0.25)
    third = frame.quantile(0.75)
    spread = third - first
    median_magnitude = frame.median().abs()
    denominator = median_magnitude + spread
    return spread.div(denominator.where(denominator > 0)).fillna(0.0)


def select_monitoring_sensors(
    measurements: pd.DataFrame,
    split_assignments: pd.Series,
    sensor_audit: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    """Select monitoring measurements without accepting or using outcome labels."""
    settings = config["monitoring"]
    target = int(settings["target_measurement_count"])
    minimum = int(settings["target_measurement_count_min"])
    maximum = int(settings["target_measurement_count_max"])
    if not minimum <= target <= maximum:
        raise ValueError(
            f"Monitoring target {target} is outside approved range {minimum}–{maximum}"
        )

    reference_mask = split_assignments.eq("reference")
    if not reference_mask.any():
        raise ValueError("Sensor selection requires a non-empty reference period")
    reference = measurements.loc[reference_mask]
    audit = sensor_audit.set_index("sensor_id", drop=False).copy()
    eligible_ids = audit.loc[audit["quality_status"].eq("eligible"), "sensor_id"].tolist()
    if len(eligible_ids) < target:
        raise ValueError(
            f"Only {len(eligible_ids)} quality-eligible measurements for target {target}"
        )

    eligible = reference[eligible_ids]
    components = pd.DataFrame(index=eligible_ids)
    components["completeness"] = 1.0 - eligible.isna().mean()
    components["temporal_coverage"] = audit.loc[
        eligible_ids, "reference_temporal_coverage_fraction"
    ].astype(float)
    components["robust_variation"] = _robust_variation(eligible)
    tie_method = str(settings["ranking_percentile_tie_method"])
    for component in ("completeness", "temporal_coverage", "robust_variation"):
        components[f"{component}_percentile"] = components[component].rank(
            method=tie_method, pct=True
        )
    components["ranking_score"] = components[
        [
            "completeness_percentile",
            "temporal_coverage_percentile",
            "robust_variation_percentile",
        ]
    ].mean(axis=1)
    ranked_ids = sorted(
        eligible_ids,
        key=lambda sensor: (-float(components.loc[sensor, "ranking_score"]), sensor),
    )
    components["candidate_rank"] = pd.Series(
        {sensor: rank for rank, sensor in enumerate(ranked_ids, start=1)}
    )

    correlations = eligible.corr(min_periods=max(3, min(100, len(eligible) // 5))).abs()
    threshold = float(settings["maximum_pairwise_absolute_correlation"])
    selected: list[str] = []
    decision: dict[str, tuple[str, float | None, str | None, int | None]] = {}
    for sensor in ranked_ids:
        if selected:
            candidate_correlations = correlations.loc[sensor, selected].dropna()
            if len(candidate_correlations):
                most_correlated = str(candidate_correlations.idxmax())
                maximum_correlation = float(candidate_correlations.max())
            else:
                most_correlated = None
                maximum_correlation = 0.0
        else:
            most_correlated = None
            maximum_correlation = 0.0
        if maximum_correlation >= threshold:
            decision[sensor] = (
                "not_selected_redundant",
                maximum_correlation,
                most_correlated,
                None,
            )
            continue
        if len(selected) >= target:
            decision[sensor] = (
                "not_selected_below_target_rank",
                maximum_correlation,
                most_correlated,
                None,
            )
            continue
        selected.append(sensor)
        decision[sensor] = (
            "selected",
            maximum_correlation,
            most_correlated,
            len(selected),
        )

    if len(selected) < minimum:
        raise RuntimeError(
            f"Correlation control selected only {len(selected)} measurements; "
            f"approved minimum is {minimum}"
        )

    records: list[dict[str, Any]] = []
    for row in audit.itertuples(index=False):
        sensor = row.sensor_id
        base: dict[str, Any] = {
            "sensor_id": sensor,
            "quality_status": row.quality_status,
            "selection_rule_version": settings["selection_rule_version"],
            "ranking_percentile_tie_method": tie_method,
            "correlation_threshold": threshold,
        }
        if sensor not in components.index:
            base.update(
                {
                    "selection_status": "not_selected_quality_excluded",
                    "candidate_rank": pd.NA,
                    "selected_order": pd.NA,
                    "ranking_score": np.nan,
                    "completeness": np.nan,
                    "temporal_coverage": np.nan,
                    "robust_variation": np.nan,
                    "completeness_percentile": np.nan,
                    "temporal_coverage_percentile": np.nan,
                    "robust_variation_percentile": np.nan,
                    "maximum_correlation_at_decision": np.nan,
                    "most_correlated_selected_sensor": pd.NA,
                }
            )
        else:
            status, maximum_correlation, correlated_sensor, selected_order = decision[sensor]
            base.update(components.loc[sensor].to_dict())
            base.update(
                {
                    "selection_status": status,
                    "selected_order": selected_order,
                    "maximum_correlation_at_decision": maximum_correlation,
                    "most_correlated_selected_sensor": correlated_sensor,
                }
            )
        records.append(base)
    result = pd.DataFrame(records)
    result["is_selected"] = result["selection_status"].eq("selected")
    return result.sort_values("sensor_id").reset_index(drop=True)
