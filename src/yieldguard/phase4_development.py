"""Development associations and calibration-period policy analysis."""

from __future__ import annotations

import json
from typing import Any

import duckdb
import pandas as pd
from sklearn.inspection import permutation_importance

from yieldguard.associations import analyze_associations
from yieldguard.config import project_path
from yieldguard.ingest import read_measurements
from yieldguard.phase4_calibration import _period_data
from yieldguard.policy import evaluate_budgets
from yieldguard.risk import build_model


def _selected_specification(settings: dict[str, Any]) -> dict[str, Any]:
    selected_id = settings["selected_configuration_id"]
    key = (
        "logistic_configurations"
        if settings["selected_model"] == "logistic_regression"
        else "hist_gradient_boosting_configurations"
    )
    matches = [item for item in settings[key] if item["id"] == selected_id]
    if len(matches) != 1:
        raise ValueError("Selected configuration does not resolve uniquely")
    return dict(matches[0])


def run_phase4_development(config: dict[str, Any]) -> dict[str, Any]:
    """Run combined-development associations after the predictive design is frozen."""
    settings = config["phase4"]
    output_directory = project_path("data/processed/phase4")
    selection_path = output_directory / "calibration_selection.json"
    if not selection_path.exists():
        raise FileNotFoundError("Run phase4-calibrate before phase4-develop")
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if selection["selected_model"] != settings["selected_model"] or selection[
        "selected_configuration_id"
    ] != settings["selected_configuration_id"]:
        raise AssertionError("Frozen model does not match calibration selection")

    database_path = project_path(config["outputs"]["database"])
    measurements = read_measurements(project_path(config["data"]["measurement_file"]))
    with duckdb.connect(str(database_path)) as connection:
        sensor_ids = connection.execute(
            """
            SELECT sensor_id FROM dim_sensor
            WHERE quality_status = 'eligible'
            ORDER BY source_column
            """
        ).fetchdf()["sensor_id"].tolist()
        development_entities = connection.execute(
            """
            SELECT entity_id, source_row_number, event_timestamp, split, failure_indicator
            FROM fact_production_entity
            WHERE split IN ('reference', 'calibration')
            ORDER BY source_row_number
            """
        ).fetchdf()
        positions = development_entities["source_row_number"].to_numpy(dtype=int) - 1
        development_features = measurements.iloc[positions].loc[:, sensor_ids].reset_index(
            drop=True
        )
        development_outcomes = development_entities["failure_indicator"].to_numpy(dtype=int)
        associations = analyze_associations(
            development_features, development_outcomes, sensor_ids, config
        )

        _, train_features, train_outcomes = _period_data(
            connection, measurements, "reference", sensor_ids
        )
        _, calibration_features, calibration_outcomes = _period_data(
            connection, measurements, "calibration", sensor_ids
        )
        specification = _selected_specification(settings)
        specification.pop("id")
        specification["feature_names"] = sensor_ids
        model = build_model(
            settings["selected_model"],
            specification,
            int(config["project"]["random_seed"]),
        )
        model.fit(train_features, train_outcomes)
        importance = permutation_importance(
            model,
            calibration_features,
            calibration_outcomes,
            scoring="average_precision",
            n_repeats=1,
            random_state=int(config["project"]["random_seed"]),
        )
        model_evidence = pd.DataFrame(
            {
                "sensor_id": sensor_ids,
                "model_permutation_importance": importance.importances_mean,
            }
        )
        pca_evidence = connection.execute(
            """
            SELECT sensor_id,
                   COUNT(*) AS pca_top_contribution_count,
                   SUM(contribution_share) AS pca_contribution_share_sum
            FROM fact_alert_contribution
            WHERE split IN ('reference', 'calibration')
            GROUP BY sensor_id
            """
        ).fetchdf()
        associations = associations.merge(pca_evidence, on="sensor_id", how="left").merge(
            model_evidence, on="sensor_id", how="left"
        )
        associations[["pca_top_contribution_count", "pca_contribution_share_sum"]] = (
            associations[
                ["pca_top_contribution_count", "pca_contribution_share_sum"]
            ].fillna(0)
        )

        calibration_scores = connection.execute(
            "SELECT * FROM fact_phase4_calibration_score"
        ).fetchdf()
        policy_frames: list[pd.DataFrame] = []
        requested = [
            (settings["selected_model"], settings["selected_configuration_id"], True),
            ("prevalence_baseline", "prevalence-reference-v1", False),
            ("monitoring_baseline", "fixed-monitoring-v1", False),
        ]
        for model_name, configuration_id, include_f2 in requested:
            ranked = calibration_scores.loc[
                calibration_scores["configuration_id"].eq(configuration_id)
            ].copy()
            policy_frames.append(
                evaluate_budgets(
                    ranked,
                    config,
                    model_name,
                    configuration_id,
                    "calibration",
                    include_f2_diagnostic=include_f2,
                )
            )
        policies = pd.concat(policy_frames, ignore_index=True)

        connection.register("association_frame", associations)
        connection.register("calibration_policy_frame", policies)
        connection.execute(
            "CREATE OR REPLACE TABLE fact_measurement_association AS "
            "SELECT * FROM association_frame"
        )
        connection.execute(
            "CREATE OR REPLACE TABLE fact_policy_evaluation AS "
            "SELECT * FROM calibration_policy_frame"
        )
        connection.execute(
            "CREATE UNIQUE INDEX ux_measurement_association "
            "ON fact_measurement_association(sensor_id)"
        )

    associations.to_csv(output_directory / "development_associations.csv", index=False)
    policies.to_csv(output_directory / "calibration_policy_evaluation.csv", index=False)
    result = {
        "development_entity_count": len(development_entities),
        "development_failure_count": int(development_outcomes.sum()),
        "final_test_entity_count_accessed": 0,
        "final_test_outcomes_accessed": False,
        "association_measurement_count": len(associations),
        "bh_supported_count": int(associations["survives_bh"].sum()),
        "by_supported_count": int(associations["survives_by"].sum()),
        "interval_excludes_zero_count": int(
            associations["interval_excludes_zero"].sum()
        ),
        "association_bootstrap_usable_replicates_minimum": int(
            associations["bootstrap_usable_replicates"].min()
        ),
        "selected_model": settings["selected_model"],
        "selected_configuration_id": settings["selected_configuration_id"],
        "calibration_policy_results": policies.to_dict(orient="records"),
    }
    (output_directory / "development_summary.json").write_text(
        json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
    )
    return result
