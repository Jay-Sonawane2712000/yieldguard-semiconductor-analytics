"""Reference-fitted Individuals, Moving Range, and EWMA monitoring."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def fit_imr_limits(reference_values: pd.Series, d2: float, d4: float) -> dict[str, float]:
    """Fit classical I-MR limits from adjacent, non-missing reference observations."""
    values = reference_values.astype(float)
    moving_ranges = values.diff().abs().where(values.notna() & values.shift(1).notna())
    observed = values.dropna()
    valid_ranges = moving_ranges.dropna()
    if len(observed) < 2 or valid_ranges.empty:
        raise ValueError(
            "I-MR fitting requires observations and at least one adjacent moving range"
        )
    center = float(observed.mean())
    mr_bar = float(valid_ranges.mean())
    sigma = mr_bar / d2
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("Reference moving ranges produced a non-positive sigma estimate")
    return {
        "individual_center": center,
        "individual_lcl": center - 3.0 * sigma,
        "individual_ucl": center + 3.0 * sigma,
        "moving_range_center": mr_bar,
        "moving_range_lcl": 0.0,
        "moving_range_ucl": d4 * mr_bar,
        "sigma": sigma,
        "reference_observation_count": int(len(observed)),
        "reference_moving_range_count": int(len(valid_ranges)),
    }


def ewma_sequence(
    values: pd.Series,
    center: float,
    sigma: float,
    smoothing: float,
    width: float,
) -> pd.DataFrame:
    """Calculate missing-aware EWMA statistics and time-varying control limits."""
    if not 0 < smoothing <= 1:
        raise ValueError("EWMA lambda must be in (0, 1]")
    if sigma <= 0 or not np.isfinite(sigma):
        raise ValueError("EWMA sigma must be finite and positive")
    state = center
    observed_sequence = 0
    records: list[dict[str, float | int]] = []
    for value in values.astype(float):
        if pd.isna(value):
            records.append(
                {
                    "statistic": np.nan,
                    "lower_control_limit": np.nan,
                    "upper_control_limit": np.nan,
                    "observation_sequence": observed_sequence,
                }
            )
            continue
        observed_sequence += 1
        state = smoothing * float(value) + (1.0 - smoothing) * state
        factor = np.sqrt(
            smoothing
            / (2.0 - smoothing)
            * (1.0 - (1.0 - smoothing) ** (2 * observed_sequence))
        )
        distance = width * sigma * factor
        records.append(
            {
                "statistic": state,
                "lower_control_limit": center - distance,
                "upper_control_limit": center + distance,
                "observation_sequence": observed_sequence,
            }
        )
    return pd.DataFrame(records, index=values.index)


def _signal_rows(
    sensor_id: str,
    values: pd.Series,
    entities: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    settings = config["monitoring"]
    reference_mask = entities["split"].eq("reference")
    limits = fit_imr_limits(
        values.loc[reference_mask],
        float(settings["imr_d2"]),
        float(settings["imr_d4"]),
    )
    base = entities[["entity_id", "event_timestamp", "split", "chronological_order"]].copy()
    base["sensor_id"] = sensor_id
    base["measurement_missing"] = values.isna().to_numpy()

    individuals = base.copy()
    individuals["method"] = "I"
    individuals["statistic"] = values.to_numpy()
    individuals["center_line"] = limits["individual_center"]
    individuals["lower_control_limit"] = limits["individual_lcl"]
    individuals["upper_control_limit"] = limits["individual_ucl"]
    individuals["observation_sequence"] = values.notna().cumsum().to_numpy()
    individuals["violation_indicator"] = (
        values.lt(limits["individual_lcl"]) | values.gt(limits["individual_ucl"])
    ).to_numpy()
    individuals["rule_identifier"] = "individual_outside_3sigma"
    individuals["limit_version"] = settings["imr_limit_version"]

    moving_range = values.diff().abs().where(values.notna() & values.shift(1).notna())
    ranges = base.copy()
    ranges["method"] = "MR"
    ranges["statistic"] = moving_range.to_numpy()
    ranges["center_line"] = limits["moving_range_center"]
    ranges["lower_control_limit"] = limits["moving_range_lcl"]
    ranges["upper_control_limit"] = limits["moving_range_ucl"]
    ranges["observation_sequence"] = moving_range.notna().cumsum().to_numpy()
    ranges["violation_indicator"] = moving_range.gt(limits["moving_range_ucl"]).to_numpy()
    ranges["rule_identifier"] = "moving_range_above_ucl"
    ranges["limit_version"] = settings["imr_limit_version"]

    ewma_values = ewma_sequence(
        values,
        limits["individual_center"],
        limits["sigma"],
        float(settings["ewma_lambda"]),
        float(settings["ewma_l"]),
    )
    ewma = base.copy()
    ewma["method"] = "EWMA"
    ewma["statistic"] = ewma_values["statistic"]
    ewma["center_line"] = limits["individual_center"]
    ewma["lower_control_limit"] = ewma_values["lower_control_limit"]
    ewma["upper_control_limit"] = ewma_values["upper_control_limit"]
    ewma["observation_sequence"] = ewma_values["observation_sequence"]
    ewma["violation_indicator"] = (
        ewma["statistic"].lt(ewma["lower_control_limit"])
        | ewma["statistic"].gt(ewma["upper_control_limit"])
    )
    ewma["rule_identifier"] = "ewma_outside_time_varying_3sigma"
    ewma["limit_version"] = settings["ewma_limit_version"]

    reference_pairs = pd.DataFrame(
        {"current": values.loc[reference_mask], "previous": values.loc[reference_mask].shift(1)}
    ).dropna()
    autocorrelation = (
        float(reference_pairs["current"].corr(reference_pairs["previous"]))
        if len(reference_pairs) >= 3
        else np.nan
    )
    correlation_record = {
        "sensor_id": sensor_id,
        "reference_lag1_pair_count": int(len(reference_pairs)),
        "reference_lag1_autocorrelation": autocorrelation,
    }
    limit_record = {"sensor_id": sensor_id, **limits}
    signal_frame = pd.concat([individuals, ranges, ewma], ignore_index=True)
    signal_frame.insert(
        0,
        "signal_id",
        signal_frame["entity_id"]
        + "|"
        + signal_frame["sensor_id"]
        + "|"
        + signal_frame["method"],
    )
    return signal_frame, limit_record, correlation_record


def build_univariate_signals(
    measurements: pd.DataFrame,
    entities: pd.DataFrame,
    selected_sensor_ids: list[str],
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build traceable I, MR, and EWMA records for all selected measurements."""
    order = entities.sort_values(
        ["event_timestamp", "source_row_number"], kind="mergesort"
    ).index
    ordered_entities = entities.loc[order].reset_index(drop=True)
    ordered_measurements = measurements.loc[order, selected_sensor_ids].reset_index(drop=True)
    signal_frames: list[pd.DataFrame] = []
    limits: list[dict[str, Any]] = []
    correlations: list[dict[str, Any]] = []
    for sensor_id in selected_sensor_ids:
        signals, limit_record, correlation_record = _signal_rows(
            sensor_id,
            ordered_measurements[sensor_id].reset_index(drop=True),
            ordered_entities,
            config,
        )
        signal_frames.append(signals)
        limits.append(limit_record)
        correlations.append(correlation_record)
    return (
        pd.concat(signal_frames, ignore_index=True),
        pd.DataFrame(limits),
        pd.DataFrame(correlations),
    )
