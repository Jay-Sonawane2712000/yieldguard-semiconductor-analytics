"""Phase 3 orchestration for reference-only multivariate monitoring."""

from __future__ import annotations

import json
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from yieldguard.config import PROJECT_ROOT, project_path
from yieldguard.ingest import read_measurements
from yieldguard.pca_monitoring import PCAArtifacts, fit_pca_monitor


def _execute_sql_file(connection: duckdb.DuckDBPyConnection, relative_path: str) -> None:
    connection.execute((PROJECT_ROOT / relative_path).read_text(encoding="utf-8"))


def _artifact_frames(
    artifacts: PCAArtifacts, model_version: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    features = pd.DataFrame(
        {
            "model_version": model_version,
            "sensor_id": artifacts.sensor_ids,
            "reference_median": artifacts.imputation_values,
            "reference_mean_after_imputation": artifacts.scaling_means,
            "reference_scale": artifacts.scaling_scales,
        }
    )
    component_count, feature_count = artifacts.components.shape
    loadings = pd.DataFrame(
        {
            "model_version": model_version,
            "component_number": np.repeat(np.arange(1, component_count + 1), feature_count),
            "sensor_id": np.tile(np.asarray(artifacts.sensor_ids), component_count),
            "loading": artifacts.components.reshape(-1),
            "explained_variance": np.repeat(
                artifacts.explained_variance, feature_count
            ),
            "explained_variance_ratio": np.repeat(
                artifacts.explained_variance_ratio, feature_count
            ),
        }
    )
    return features, loadings


def build_phase3(config: dict[str, Any]) -> dict[str, Any]:
    """Fit and persist PCA monitoring while keeping all outcome fields out of memory."""
    database_path = project_path(config["outputs"]["database"])
    if not database_path.exists():
        raise FileNotFoundError("Phase 1 database is missing; run earlier phases first")
    measurements = read_measurements(project_path(config["data"]["measurement_file"]))

    with duckdb.connect(str(database_path)) as connection:
        entities = connection.execute(
            """
            SELECT entity_id, source_row_number, event_timestamp, chronological_order, split
            FROM fact_production_entity
            ORDER BY source_row_number
            """
        ).fetchdf()
        sensor_ids = connection.execute(
            """
            SELECT sensor_id
            FROM dim_sensor
            WHERE quality_status = 'eligible'
            ORDER BY source_column
            """
        ).fetchdf()["sensor_id"].tolist()
        if len(measurements) != len(entities):
            raise AssertionError("Raw measurements do not align with persisted entities")

        alerts, contributions, model, artifacts, diagnostics = fit_pca_monitor(
            measurements, entities, sensor_ids, config
        )
        features, loadings = _artifact_frames(artifacts, config["pca"]["model_version"])
        connection.register("pca_model_frame", model)
        connection.register("pca_feature_frame", features)
        connection.register("pca_loading_frame", loadings)
        connection.register("multivariate_alert_frame", alerts)
        connection.register("contribution_frame", contributions)
        _execute_sql_file(connection, "sql/transformations/040_pca_monitoring.sql")
        _execute_sql_file(connection, "sql/marts/020_phase3_marts.sql")

        table_evidence = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM fact_multivariate_alert),
                (SELECT COUNT(DISTINCT entity_id) FROM fact_multivariate_alert),
                (SELECT COUNT(*) FROM fact_alert_contribution),
                (SELECT COUNT(DISTINCT contribution_id) FROM fact_alert_contribution),
                (SELECT COUNT(*) FROM fact_pca_loading)
            """
        ).fetchone()
        rank_evidence = connection.execute(
            """
            SELECT MIN(contribution_count), MAX(contribution_count)
            FROM (
                SELECT entity_id, statistic_type, COUNT(*) AS contribution_count
                FROM fact_alert_contribution
                GROUP BY entity_id, statistic_type
            )
            """
        ).fetchone()
        sql_summary = connection.execute(
            "SELECT * FROM mart_alert_method_summary ORDER BY split"
        ).fetchdf()

    top_k = min(config["pca"]["pca_contribution_top_k"], len(sensor_ids))
    expected_contributions = len(entities) * 2 * top_k
    expected_loadings = len(sensor_ids) * artifacts.components.shape[0]
    expected = (
        len(entities),
        len(entities),
        expected_contributions,
        expected_contributions,
        expected_loadings,
    )
    if table_evidence != expected:
        raise AssertionError(f"Phase 3 table reconciliation failed: {table_evidence} != {expected}")
    if rank_evidence != (top_k, top_k):
        raise AssertionError(f"Contribution rank reconciliation failed: {rank_evidence}")
    if diagnostics["maximum_t2_relative_reconciliation_error"] > 1e-10:
        raise AssertionError("T-squared contributions do not reconcile with scores")
    if diagnostics["maximum_q_relative_reconciliation_error"] > 1e-10:
        raise AssertionError("Q contributions do not reconcile with scores")

    python_summary = (
        alerts.groupby("split", sort=True)
        .agg(
            entity_count=("entity_id", "size"),
            t2_alert_entity_count=("t2_alert", "sum"),
            q_alert_entity_count=("q_alert", "sum"),
            multivariate_alert_entity_count=("any_multivariate_alert", "sum"),
        )
        .reset_index()
    )
    pd.testing.assert_series_equal(
        sql_summary.set_index("split")["entity_count"],
        python_summary.set_index("split")["entity_count"],
        check_names=False,
        check_dtype=False,
    )
    for column in (
        "t2_alert_entity_count",
        "q_alert_entity_count",
        "multivariate_alert_entity_count",
    ):
        pd.testing.assert_series_equal(
            sql_summary.set_index("split")[column],
            python_summary.set_index("split")[column],
            check_names=False,
            check_dtype=False,
        )

    output_directory = project_path("data/processed/phase3")
    output_directory.mkdir(parents=True, exist_ok=True)
    model.to_csv(output_directory / "pca_model.csv", index=False)
    features.to_csv(output_directory / "pca_feature_preprocessing.csv", index=False)
    loadings.to_csv(output_directory / "pca_loadings.csv", index=False)
    sql_summary.to_csv(output_directory / "alert_method_summary.csv", index=False)
    result = {
        "model": model.iloc[0].to_dict(),
        "architecture": {
            "multivariate_alert_rows": int(table_evidence[0]),
            "contribution_rows": int(table_evidence[2]),
            "loading_rows": int(table_evidence[4]),
        },
        "score_reconciliation": diagnostics,
        "alert_method_summary": sql_summary.to_dict(orient="records"),
        "outcome_fields_accessed": False,
    }
    (output_directory / "phase3_summary.json").write_text(
        json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
    )
    return result
