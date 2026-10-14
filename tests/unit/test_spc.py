import numpy as np
import pandas as pd
import pytest

from yieldguard.spc import build_univariate_signals, ewma_sequence, fit_imr_limits


def _monitoring_config() -> dict:
    return {
        "monitoring": {
            "imr_d2": 1.128,
            "imr_d4": 3.267,
            "imr_limit_version": "imr-test-v1",
            "ewma_lambda": 0.2,
            "ewma_l": 3.0,
            "ewma_limit_version": "ewma-test-v1",
        }
    }


def test_fit_imr_limits_uses_only_adjacent_observed_ranges() -> None:
    values = pd.Series([10.0, 12.0, 11.0, np.nan, 13.0])

    result = fit_imr_limits(values, d2=1.128, d4=3.267)

    assert result["individual_center"] == pytest.approx(11.5)
    assert result["moving_range_center"] == pytest.approx(1.5)
    assert result["reference_moving_range_count"] == 2
    assert result["moving_range_ucl"] == pytest.approx(4.9005)


def test_ewma_recursion_skips_missing_observations_without_resetting_state() -> None:
    result = ewma_sequence(
        pd.Series([10.0, 12.0, np.nan, 14.0]),
        center=10.0,
        sigma=2.0,
        smoothing=0.2,
        width=3.0,
    )

    assert result["statistic"].tolist()[:2] == pytest.approx([10.0, 10.4])
    assert np.isnan(result.loc[2, "statistic"])
    assert result.loc[3, "statistic"] == pytest.approx(11.12)
    assert result["observation_sequence"].tolist() == [1, 2, 2, 3]
    expected_first_distance = 3.0 * 2.0 * np.sqrt(0.2 / 1.8 * (1 - 0.8**2))
    assert result.loc[0, "upper_control_limit"] == pytest.approx(
        10.0 + expected_first_distance
    )


def test_signal_build_preserves_missing_i_and_breaks_moving_range() -> None:
    measurements = pd.DataFrame({"measurement_000": [10.0, 12.0, np.nan, 13.0, 14.0]})
    entities = pd.DataFrame(
        {
            "entity_id": [f"E{index:06d}" for index in range(1, 6)],
            "source_row_number": range(1, 6),
            "event_timestamp": pd.date_range("2024-01-01", periods=5, freq="h"),
            "chronological_order": range(1, 6),
            "split": ["reference"] * 5,
        }
    )

    signals, limits, correlations = build_univariate_signals(
        measurements, entities, ["measurement_000"], _monitoring_config()
    )
    individual = signals[signals["method"].eq("I")].reset_index(drop=True)
    moving_range = signals[signals["method"].eq("MR")].reset_index(drop=True)

    assert np.isnan(individual.loc[2, "statistic"])
    assert np.isnan(moving_range.loc[2, "statistic"])
    assert np.isnan(moving_range.loc[3, "statistic"])
    assert moving_range.loc[4, "statistic"] == pytest.approx(1.0)
    assert len(limits) == 1
    assert correlations.loc[0, "reference_lag1_pair_count"] == 2
