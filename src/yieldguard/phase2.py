"""Phase 2 SQL architecture, sensor selection, and univariate monitoring."""

from __future__ import annotations

import json
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from yieldguard.config import PROJECT_ROOT, project_path
from yieldguard.ingest import load_source
from yieldguard.sensor_selection import select_monitoring_sensors
from yieldguard.spc import build_univariate_signals


def _json_default(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(value).isoformat()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if pd.isna(value):
        return None
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def _execute_sql_file(connection: duckdb.DuckDBPyConnection, relative_path: str) -> None:
    sql_path = PROJECT_ROOT / relative_path
    connection.execute(sql_path.read_text(encoding="utf-8"))


def _phase1_entities(connection: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return connection.execute(
        """
        SELECT
            entity_id,
            source_row_number,
            event_timestamp,
            chronological_order,
            split
        FROM fact_production_entity
        ORDER BY source_row_number
        """
    ).fetchdf()


def build_phase2(config: dict[str, Any]) -> dict[str, Any]:
    """Build the Phase 2 analytical architecture and frozen monitoring outputs."""
    database_path = project_path(config["outputs"]["database"])
    if not database_path.exists():
        raise FileNotFoundError("Phase 1 database is missing; run yieldguard build-phase1 first")
    measurements, source_entities = load_source(config)

    with duckdb.connect(str(database_path)) as connection:
        entities = _phase1_entities(connection)
        if not entities["entity_id"].equals(source_entities["entity_id"]):
            raise AssertionError("Source entity IDs do not match the Phase 1 database")
        sensor_audit = connection.execute(
            "SELECT * FROM dim_sensor ORDER BY source_column"
        ).fetchdf()

        selection = select_monitoring_sensors(
            measurements,
            entities["split"],
            sensor_audit,
            config,
        )
        selected = (
            selection.loc[selection["is_selected"]]
            .sort_values("selected_order")["sensor_id"]
            .tolist()
        )
        signals, limits, autocorrelation = build_univariate_signals(
            measurements,
            entities,
            selected,
            config,
        )

        connection.register("selection_frame", selection)
        connection.register("signal_frame", signals)
        connection.register("limit_frame", limits)
        connection.register("autocorrelation_frame", autocorrelation)
        _execute_sql_file(connection, "sql/transformations/010_measurements_long.sql")
        _execute_sql_file(connection, "sql/transformations/020_monitoring_selection.sql")
        _execute_sql_file(connection, "sql/transformations/030_univariate_signals.sql")
        _execute_sql_file(connection, "sql/marts/010_phase2_marts.sql")

        long_evidence = connection.execute(
            """
            SELECT
                COUNT(*) AS row_count,
                COUNT(DISTINCT entity_id || '|' || sensor_id) AS distinct_key_count,
                COUNT(*) FILTER (WHERE missing_indicator) AS missing_count
            FROM fact_sensor_measurement
            """
        ).fetchone()
        signal_evidence = connection.execute(
            """
            SELECT
                COUNT(*) AS row_count,
                COUNT(DISTINCT signal_id) AS distinct_key_count,
                COUNT(*) FILTER (WHERE violation_indicator) AS signal_count
            FROM fact_spc_signal
            """
        ).fetchone()
        sql_summary = connection.execute(
            """
            SELECT split, method, SUM(signal_count)::BIGINT AS signal_count,
                   SUM(available_statistic_count)::BIGINT AS available_statistic_count
            FROM mart_spc_alert_summary
            GROUP BY split, method
            ORDER BY split, method
            """
        ).fetchdf()

    expected_long_rows = len(entities) * measurements.shape[1]
    expected_signal_rows = len(entities) * len(selected) * 3
    expected_missing = int(measurements.isna().sum().sum())
    if long_evidence != (expected_long_rows, expected_long_rows, expected_missing):
        raise AssertionError(
            f"Long-table reconciliation failed: observed {long_evidence}, expected "
            f"{(expected_long_rows, expected_long_rows, expected_missing)}"
        )
    if signal_evidence[0] != expected_signal_rows or signal_evidence[1] != expected_signal_rows:
        raise AssertionError(
            f"SPC-signal reconciliation failed: observed {signal_evidence[:2]}, expected "
            f"{expected_signal_rows}"
        )
    python_summary = (
        signals.groupby(["split", "method"], sort=True)
        .agg(
            signal_count=("violation_indicator", "sum"),
            available_statistic_count=("statistic", "count"),
        )
        .reset_index()
    )
    pd.testing.assert_frame_equal(
        sql_summary.reset_index(drop=True),
        python_summary.reset_index(drop=True),
        check_dtype=False,
    )

    output_directory = project_path("data/processed/phase2")
    output_directory.mkdir(parents=True, exist_ok=True)
    selection.to_csv(output_directory / "monitoring_sensor_selection.csv", index=False)
    limits.to_csv(output_directory / "spc_limits.csv", index=False)
    autocorrelation.to_csv(output_directory / "sensor_autocorrelation.csv", index=False)
    sql_summary.to_csv(output_directory / "spc_signal_summary.csv", index=False)
    selected_selection = selection.loc[selection["is_selected"]].sort_values("selected_order")
    result = {
        "selection": {
            "rule_version": config["monitoring"]["selection_rule_version"],
            "selected_count": len(selected),
            "selected_sensor_ids": selected,
            "correlation_threshold": config["monitoring"][
                "maximum_pairwise_absolute_correlation"
            ],
            "maximum_selected_pairwise_absolute_correlation": float(
                measurements.loc[entities["split"].eq("reference"), selected]
                .corr()
                .abs()
                .where(~np.eye(len(selected), dtype=bool))
                .max()
                .max()
            ),
            "ranking": selected_selection[
                ["selected_order", "sensor_id", "ranking_score"]
            ].to_dict(orient="records"),
        },
        "architecture": {
            "fact_sensor_measurement_rows": int(long_evidence[0]),
            "fact_sensor_measurement_missing_rows": int(long_evidence[2]),
            "fact_spc_signal_rows": int(signal_evidence[0]),
            "fact_spc_signal_count": int(signal_evidence[2]),
        },
        "monitoring": {
            "imr_limit_version": config["monitoring"]["imr_limit_version"],
            "ewma_limit_version": config["monitoring"]["ewma_limit_version"],
            "ewma_lambda": config["monitoring"]["ewma_lambda"],
            "ewma_l": config["monitoring"]["ewma_l"],
            "signal_summary": sql_summary.to_dict(orient="records"),
            "autocorrelation": autocorrelation.to_dict(orient="records"),
        },
    }
    (output_directory / "phase2_summary.json").write_text(
        json.dumps(result, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    return result
