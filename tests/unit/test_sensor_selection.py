import numpy as np
import pandas as pd

from yieldguard.sensor_selection import select_monitoring_sensors


def _config() -> dict:
    return {
        "monitoring": {
            "target_measurement_count": 3,
            "target_measurement_count_min": 2,
            "target_measurement_count_max": 4,
            "selection_rule_version": "test-v1",
            "ranking_percentile_tie_method": "average",
            "maximum_pairwise_absolute_correlation": 0.90,
        }
    }


def test_selection_is_deterministic_and_rejects_redundancy() -> None:
    rows = 20
    measurements = pd.DataFrame(
        {
            "measurement_000": np.arange(rows, dtype=float),
            "measurement_001": np.arange(rows, dtype=float) * 2,
            "measurement_002": np.tile([0.0, 1.0], rows // 2),
            "measurement_003": np.tile([0.0, 1.0, 2.0, 3.0], rows // 4),
        }
    )
    split = pd.Series(["reference"] * 15 + ["final_test"] * 5)
    audit = pd.DataFrame(
        {
            "sensor_id": measurements.columns,
            "quality_status": ["eligible"] * 4,
            "reference_temporal_coverage_fraction": [1.0] * 4,
        }
    )

    first = select_monitoring_sensors(measurements, split, audit, _config())
    second = select_monitoring_sensors(measurements, split, audit, _config())

    pd.testing.assert_frame_equal(first, second)
    assert first["is_selected"].sum() == 3
    correlated_pair = first.set_index("sensor_id").loc[
        ["measurement_000", "measurement_001"], "is_selected"
    ]
    assert correlated_pair.sum() == 1
    assert "not_selected_redundant" in set(first["selection_status"])


def test_selection_ignores_quality_excluded_measurements() -> None:
    measurements = pd.DataFrame(
        {
            "measurement_000": np.arange(20, dtype=float),
            "measurement_001": np.tile([0.0, 1.0], 10),
            "measurement_002": np.tile([0.0, 1.0, 2.0, 3.0], 5),
            "measurement_003": np.arange(20, dtype=float) * 5,
        }
    )
    split = pd.Series(["reference"] * 15 + ["calibration"] * 5)
    audit = pd.DataFrame(
        {
            "sensor_id": measurements.columns,
            "quality_status": ["eligible", "eligible", "eligible", "excluded"],
            "reference_temporal_coverage_fraction": [1.0] * 4,
        }
    )

    result = select_monitoring_sensors(measurements, split, audit, _config()).set_index(
        "sensor_id"
    )

    assert not bool(result.loc["measurement_003", "is_selected"])
    assert result.loc["measurement_003", "selection_status"] == (
        "not_selected_quality_excluded"
    )
