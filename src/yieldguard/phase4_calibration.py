"""Phase 4 calibration-only model and baseline comparison."""

from __future__ import annotations

import json
from typing import Any

import duckdb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from yieldguard.config import project_path
from yieldguard.ingest import read_measurements
from yieldguard.risk import (
    build_model,
    calibration_summary,
    deterministic_rank,
    monitoring_baseline,
    score_metrics,
)


def _period_data(
    connection: duckdb.DuckDBPyConnection,
    measurements: pd.DataFrame,
    split: str,
    sensor_ids: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    entities = connection.execute(
        """
        SELECT entity_id, source_row_number, event_timestamp, split, failure_indicator
        FROM fact_production_entity
        WHERE split = ?
        ORDER BY source_row_number
        """,
        [split],
    ).fetchdf()
    positions = entities["source_row_number"].to_numpy(dtype=int) - 1
    features = measurements.iloc[positions].loc[:, sensor_ids].reset_index(drop=True)
    outcomes = entities["failure_indicator"].to_numpy(dtype=int)
    return entities, features, outcomes


def run_phase4_calibration(config: dict[str, Any]) -> dict[str, Any]:
    """Evaluate only the predeclared candidates on the calibration period."""
    settings = config["phase4"]
    if len(settings["logistic_configurations"]) > 6:
        raise ValueError("Logistic-regression configuration limit exceeded")
    if len(settings["hist_gradient_boosting_configurations"]) > 6:
        raise ValueError("HistGradientBoosting configuration limit exceeded")

    database_path = project_path(config["outputs"]["database"])
    measurements = read_measurements(project_path(config["data"]["measurement_file"]))
    seed = int(config["project"]["random_seed"])
    metric_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    calibration_frames: list[pd.DataFrame] = []

    with duckdb.connect(str(database_path)) as connection:
        sensor_ids = connection.execute(
            """
            SELECT sensor_id FROM dim_sensor
            WHERE quality_status = 'eligible'
            ORDER BY source_column
            """
        ).fetchdf()["sensor_id"].tolist()
        train_entities, train_features, train_outcomes = _period_data(
            connection, measurements, "reference", sensor_ids
        )
        calibration_entities, calibration_features, calibration_outcomes = _period_data(
            connection, measurements, "calibration", sensor_ids
        )

        families = (
            ("logistic_regression", settings["logistic_configurations"]),
            (
                "hist_gradient_boosting",
                settings["hist_gradient_boosting_configurations"],
            ),
        )
        for family, configurations in families:
            for specification in configurations:
                parameters = dict(specification)
                configuration_id = parameters.pop("id")
                parameters["feature_names"] = sensor_ids
                model = build_model(family, parameters, seed)
                model.fit(train_features, train_outcomes)
                probabilities = model.predict_proba(calibration_features)[:, 1]
                metrics = score_metrics(calibration_outcomes, probabilities)
                bins, ece = calibration_summary(
                    calibration_outcomes,
                    probabilities,
                    int(settings["calibration_bins"]),
                )
                metric_rows.append(
                    {
                        "model": family,
                        "configuration_id": configuration_id,
                        "split": "calibration",
                        **metrics,
                        "expected_calibration_error": ece,
                    }
                )
                ranked = deterministic_rank(calibration_entities, probabilities)
                ranked["model"] = family
                ranked["configuration_id"] = configuration_id
                ranked["failure_indicator"] = ranked["entity_id"].map(
                    calibration_entities.set_index("entity_id")["failure_indicator"]
                )
                prediction_frames.append(ranked)
                bins.insert(0, "configuration_id", configuration_id)
                bins.insert(0, "model", family)
                calibration_frames.append(bins)

        prevalence = float(train_outcomes.mean())
        prevalence_scores = np.full(len(calibration_outcomes), prevalence)
        prevalence_metrics = score_metrics(calibration_outcomes, prevalence_scores)
        prevalence_bins, prevalence_ece = calibration_summary(
            calibration_outcomes,
            prevalence_scores,
            int(settings["calibration_bins"]),
        )
        metric_rows.append(
            {
                "model": "prevalence_baseline",
                "configuration_id": "prevalence-reference-v1",
                "split": "calibration",
                **prevalence_metrics,
                "expected_calibration_error": prevalence_ece,
            }
        )
        prevalence_ranked = deterministic_rank(calibration_entities, prevalence_scores)
        prevalence_ranked["model"] = "prevalence_baseline"
        prevalence_ranked["configuration_id"] = "prevalence-reference-v1"
        prevalence_ranked["failure_indicator"] = prevalence_ranked["entity_id"].map(
            calibration_entities.set_index("entity_id")["failure_indicator"]
        )
        prediction_frames.append(prevalence_ranked)
        prevalence_bins.insert(0, "configuration_id", "prevalence-reference-v1")
        prevalence_bins.insert(0, "model", "prevalence_baseline")
        calibration_frames.append(prevalence_bins)

        monitoring = monitoring_baseline(connection, "calibration")
        monitoring_outcomes = monitoring["entity_id"].map(
            calibration_entities.set_index("entity_id")["failure_indicator"]
        ).to_numpy(dtype=int)
        monitoring_metrics = {
            "pr_auc": float(
                average_precision_score(
                    monitoring_outcomes,
                    monitoring["raw_score"] + monitoring["tie_breaker"] * 1e-12,
                )
            ),
            "roc_auc": float(
                roc_auc_score(
                    monitoring_outcomes,
                    monitoring["raw_score"] + monitoring["tie_breaker"] * 1e-12,
                )
            ),
        }
        metric_rows.append(
            {
                "model": "monitoring_baseline",
                "configuration_id": "fixed-monitoring-v1",
                "split": "calibration",
                **monitoring_metrics,
                "brier_score": np.nan,
                "positive_prevalence": float(calibration_outcomes.mean()),
                "expected_calibration_error": np.nan,
            }
        )
        monitoring["model"] = "monitoring_baseline"
        monitoring["configuration_id"] = "fixed-monitoring-v1"
        monitoring["failure_indicator"] = monitoring["entity_id"].map(
            calibration_entities.set_index("entity_id")["failure_indicator"]
        )
        prediction_frames.append(monitoring)

        metrics_frame = pd.DataFrame(metric_rows)
        candidate_metrics = metrics_frame[metrics_frame["model"].isin(
            ["logistic_regression", "hist_gradient_boosting"]
        )].copy()
        winner = candidate_metrics.sort_values(
            ["pr_auc", "brier_score", "configuration_id"],
            ascending=[False, True, True],
            kind="mergesort",
        ).iloc[0]

        predictions = pd.concat(prediction_frames, ignore_index=True, sort=False)
        calibration_bins = pd.concat(calibration_frames, ignore_index=True)
        connection.register("phase4_candidate_metric_frame", metrics_frame)
        connection.register("phase4_calibration_score_frame", predictions)
        connection.register("phase4_calibration_bin_frame", calibration_bins)
        connection.execute(
            "CREATE OR REPLACE TABLE audit_phase4_candidate_metric AS "
            "SELECT * FROM phase4_candidate_metric_frame"
        )
        connection.execute(
            "CREATE OR REPLACE TABLE fact_phase4_calibration_score AS "
            "SELECT * FROM phase4_calibration_score_frame"
        )
        connection.execute(
            "CREATE OR REPLACE TABLE audit_phase4_calibration_bin AS "
            "SELECT * FROM phase4_calibration_bin_frame"
        )

    output_directory = project_path("data/processed/phase4")
    output_directory.mkdir(parents=True, exist_ok=True)
    metrics_frame.to_csv(output_directory / "candidate_metrics.csv", index=False)
    predictions.to_csv(output_directory / "calibration_scores.csv", index=False)
    calibration_bins.to_csv(output_directory / "calibration_bins.csv", index=False)
    result = {
        "design_version": settings["design_version"],
        "reference_entity_count": len(train_entities),
        "reference_failure_count": int(train_outcomes.sum()),
        "calibration_entity_count": len(calibration_entities),
        "calibration_failure_count": int(calibration_outcomes.sum()),
        "feature_count": len(sensor_ids),
        "evaluated_configuration_counts": {
            "logistic_regression": len(settings["logistic_configurations"]),
            "hist_gradient_boosting": len(
                settings["hist_gradient_boosting_configurations"]
            ),
        },
        "selected_model": winner["model"],
        "selected_configuration_id": winner["configuration_id"],
        "selection_metric": settings["selection_metric"],
        "candidate_metrics": metrics_frame.to_dict(orient="records"),
        "final_test_outcomes_accessed": False,
    }
    (output_directory / "calibration_selection.json").write_text(
        json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
    )
    return result
