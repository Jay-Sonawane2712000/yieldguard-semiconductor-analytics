"""Measurement trust audit using reference-period data for exclusions."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _temporal_coverage(
    reference_measurements: pd.DataFrame,
    reference_entities: pd.DataFrame,
    bin_count: int,
) -> pd.Series:
    ordered_index = reference_entities.sort_values(
        ["event_timestamp", "source_row_number"], kind="mergesort"
    ).index
    ordered = reference_measurements.loc[ordered_index]
    bins = pd.qcut(
        pd.Series(np.arange(len(ordered)), index=ordered.index),
        q=min(bin_count, len(ordered)),
        labels=False,
        duplicates="drop",
    )
    observed_bins = ordered.notna().groupby(bins).any().sum(axis=0)
    actual_bins = int(bins.nunique())
    return observed_bins / actual_bins


def _dominant_fraction(frame: pd.DataFrame) -> pd.Series:
    values: dict[str, float] = {}
    for column in frame.columns:
        counts = frame[column].value_counts(dropna=True)
        values[column] = float(counts.iloc[0] / counts.sum()) if len(counts) else np.nan
    return pd.Series(values)


def _extreme_counts(frame: pd.DataFrame, multiplier: float) -> pd.Series:
    first = frame.quantile(0.25)
    third = frame.quantile(0.75)
    spread = third - first
    lower = first - multiplier * spread
    upper = third + multiplier * spread
    return ((frame.lt(lower)) | (frame.gt(upper))).sum(axis=0)


def _correlation_summary(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    correlation = frame.corr(min_periods=max(3, min(100, len(frame) // 5))).abs()
    correlation_array = correlation.to_numpy(copy=True)
    np.fill_diagonal(correlation_array, np.nan)
    correlation = pd.DataFrame(
        correlation_array, index=correlation.index, columns=correlation.columns
    )
    correlated_with = correlation.apply(
        lambda row: row.idxmax() if row.notna().any() else pd.NA, axis=1
    )
    return correlation.max(axis=1), correlated_with


def audit_measurements(
    measurements: pd.DataFrame,
    entities: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    """Profile every measurement and assign explicit reference-only exclusions."""
    reference_mask = entities["split"] == "reference"
    if not reference_mask.any():
        raise ValueError("Measurement audit requires a non-empty reference period")
    reference = measurements.loc[reference_mask]
    reference_entities = entities.loc[reference_mask]
    thresholds = config["quality"]

    non_null = reference.notna().sum()
    distinct = reference.nunique(dropna=True)
    variance = reference.var(ddof=1)
    dominant = _dominant_fraction(reference)
    temporal_coverage = _temporal_coverage(
        reference,
        reference_entities,
        int(thresholds["temporal_bin_count"]),
    )
    max_correlation, correlated_with = _correlation_summary(reference)
    extreme_counts = _extreme_counts(reference, float(thresholds["extreme_iqr_multiplier"]))

    audit = pd.DataFrame(
        {
            "sensor_id": measurements.columns,
            "source_column": np.arange(measurements.shape[1], dtype=int),
            "overall_non_null_count": measurements.notna().sum().to_numpy(),
            "overall_missing_fraction": measurements.isna().mean().to_numpy(),
            "reference_non_null_count": non_null.to_numpy(),
            "reference_missing_fraction": reference.isna().mean().to_numpy(),
            "reference_distinct_count": distinct.to_numpy(),
            "reference_variance": variance.to_numpy(),
            "reference_dominant_fraction": dominant.to_numpy(),
            "reference_temporal_coverage_fraction": temporal_coverage.to_numpy(),
            "reference_extreme_count": extreme_counts.to_numpy(),
            "reference_max_abs_correlation": max_correlation.to_numpy(),
            "reference_most_correlated_sensor": correlated_with.to_numpy(),
        }
    )

    reasons: list[str] = []
    for row in audit.itertuples(index=False):
        sensor_reasons: list[str] = []
        if row.reference_non_null_count == 0:
            sensor_reasons.append("all_null_reference")
        if row.reference_missing_fraction > float(thresholds["max_missing_fraction"]):
            sensor_reasons.append("excessive_reference_missingness")
        if row.reference_non_null_count < int(thresholds["min_non_null_count"]):
            sensor_reasons.append("insufficient_reference_non_null_count")
        if row.reference_distinct_count <= 1 and row.reference_non_null_count > 0:
            sensor_reasons.append("constant_reference")
        elif (
            pd.notna(row.reference_dominant_fraction)
            and row.reference_dominant_fraction
            >= float(thresholds["near_constant_dominant_fraction"])
        ):
            sensor_reasons.append("near_constant_reference")
        if (
            row.reference_distinct_count > 1
            and np.isfinite(row.reference_variance)
            and row.reference_variance < float(thresholds["min_reference_variance"])
        ):
            sensor_reasons.append("near_zero_variance_reference")
        if (
            row.reference_temporal_coverage_fraction
            < float(thresholds["min_temporal_coverage_fraction"])
        ):
            sensor_reasons.append("insufficient_reference_temporal_coverage")
        if row.reference_distinct_count > 1 and not np.isfinite(row.reference_variance):
            sensor_reasons.append("non_finite_reference_variance")
        reasons.append(";".join(sensor_reasons))

    audit["exclusion_reason"] = reasons
    audit["quality_status"] = np.where(audit["exclusion_reason"].eq(""), "eligible", "excluded")
    audit["inclusion_status"] = audit["quality_status"]
    audit["monitoring_selection_status"] = "not_evaluated_phase1"
    audit["selection_rule_version"] = pd.NA
    return audit.sort_values("source_column").reset_index(drop=True)


def missingness_by_entity(
    measurements: pd.DataFrame, entities: pd.DataFrame
) -> pd.DataFrame:
    """Return structural missingness by production entity without outcome conditioning."""
    missing_count = measurements.isna().sum(axis=1)
    return pd.DataFrame(
        {
            "entity_id": entities["entity_id"],
            "event_timestamp": entities["event_timestamp"],
            "split": entities["split"],
            "missing_measurement_count": missing_count,
            "missing_measurement_fraction": missing_count / measurements.shape[1],
        }
    )
