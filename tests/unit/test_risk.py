import duckdb
import numpy as np
import pandas as pd
import pytest

from yieldguard.risk import (
    calibration_summary,
    deterministic_rank,
    metric_intervals,
    monitoring_baseline,
)


def test_deterministic_rank_uses_scores_then_time_and_id() -> None:
    entities = pd.DataFrame(
        {
            "entity_id": ["E2", "E1", "E3"],
            "event_timestamp": pd.to_datetime(
                ["2024-01-01 02:00", "2024-01-01 01:00", "2024-01-01 01:00"]
            ),
            "split": ["calibration"] * 3,
        }
    )
    ranked = deterministic_rank(entities, [1.0, 1.0, 0.0], [0.5, 0.5, 9.0])

    assert ranked["entity_id"].tolist() == ["E1", "E2", "E3"]
    assert ranked["risk_rank"].tolist() == [1, 2, 3]


def test_calibration_summary_reconciles_bin_counts() -> None:
    bins, ece = calibration_summary(
        np.array([0, 0, 1, 0, 1, 0]),
        np.array([0.1, 0.2, 0.8, 0.3, 0.7, 0.4]),
        3,
    )

    assert bins["entity_count"].sum() == 6
    assert len(bins) == 3
    assert 0 <= ece <= 1


def test_metric_intervals_are_reproducible_and_report_requested_replicates() -> None:
    outcomes = np.array([0, 0, 0, 1, 1, 1])
    scores = np.array([0.1, 0.2, 0.6, 0.4, 0.8, 0.9])

    first = metric_intervals(outcomes, scores, 25, 9, probability_score=True)
    second = metric_intervals(outcomes, scores, 25, 9, probability_score=True)

    assert first == second
    assert first["bootstrap_usable_replicates"] == 25
    assert first["pr_auc_ci_lower"] <= first["pr_auc_ci_upper"]


def test_monitoring_baseline_counts_imr_measurement_once_and_uses_max_severity() -> None:
    signals = pd.DataFrame(
        [
            ["E1", "measurement_001", "I", 12.0, 10.0, 6.0, 14.0, True],
            ["E1", "measurement_001", "MR", 3.0, 0.0, 0.0, 4.0, True],
            ["E1", "measurement_002", "EWMA", 14.0, 10.0, 6.0, 14.0, True],
            ["E2", "measurement_001", "I", 10.0, 10.0, 6.0, 14.0, False],
        ],
        columns=[
            "entity_id",
            "sensor_id",
            "method",
            "statistic",
            "center_line",
            "lower_control_limit",
            "upper_control_limit",
            "violation_indicator",
        ],
    )
    signals["event_timestamp"] = pd.to_datetime(
        signals["entity_id"].map({"E1": "2024-01-01", "E2": "2024-01-02"})
    )
    signals["split"] = "calibration"
    multivariate = pd.DataFrame(
        {
            "entity_id": ["E1", "E2"],
            "event_timestamp": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "split": ["calibration", "calibration"],
            "t2_statistic": [20.0, 1.0],
            "t2_limit": [10.0, 10.0],
            "t2_alert": [True, False],
            "q_statistic": [5.0, 1.0],
            "q_limit": [10.0, 10.0],
            "q_alert": [False, False],
        }
    )
    connection = duckdb.connect()
    connection.register("signals", signals)
    connection.register("multivariate", multivariate)
    connection.execute("CREATE TABLE fact_spc_signal AS SELECT * FROM signals")
    connection.execute("CREATE TABLE fact_multivariate_alert AS SELECT * FROM multivariate")

    result = monitoring_baseline(connection, "calibration").set_index("entity_id")

    assert result.loc["E1", "raw_score"] == 3
    assert result.loc["E1", "tie_breaker"] == pytest.approx(2.0)
    assert result.loc["E1", "risk_rank"] == 1
