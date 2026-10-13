import numpy as np
import pandas as pd

from yieldguard.quality import audit_measurements


def test_audit_measurements_records_explicit_reference_only_exclusions() -> None:
    rows = 20
    entities = pd.DataFrame(
        {
            "event_timestamp": pd.date_range("2024-01-01", periods=rows, freq="h"),
            "source_row_number": range(1, rows + 1),
            "split": ["reference"] * 15 + ["final_test"] * 5,
        }
    )
    measurements = pd.DataFrame(
        {
            "measurement_000": np.arange(rows, dtype=float),
            "measurement_001": np.ones(rows),
            "measurement_002": [np.nan] * 15 + list(range(5)),
            "measurement_003": np.arange(rows, dtype=float) * 1e-8,
        }
    )
    config = {
        "quality": {
            "max_missing_fraction": 0.4,
            "min_non_null_count": 5,
            "near_constant_dominant_fraction": 0.995,
            "min_reference_variance": 1e-12,
            "temporal_bin_count": 5,
            "min_temporal_coverage_fraction": 0.8,
            "extreme_iqr_multiplier": 3.0,
        }
    }

    result = audit_measurements(measurements, entities, config).set_index("sensor_id")

    assert result.loc["measurement_000", "quality_status"] == "eligible"
    assert "constant_reference" in result.loc["measurement_001", "exclusion_reason"]
    assert "all_null_reference" in result.loc["measurement_002", "exclusion_reason"]
    assert result.loc["measurement_002", "overall_non_null_count"] == 5
    assert result.loc["measurement_002", "reference_non_null_count"] == 0
    assert "near_zero_variance_reference" in result.loc[
        "measurement_003", "exclusion_reason"
    ]
