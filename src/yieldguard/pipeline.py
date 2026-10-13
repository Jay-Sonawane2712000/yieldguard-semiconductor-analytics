"""Phase 1 orchestration and persisted audit outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from yieldguard.acquire import sha256_file
from yieldguard.config import project_path
from yieldguard.ingest import load_source
from yieldguard.quality import audit_measurements, missingness_by_entity
from yieldguard.splits import assert_split_integrity, choose_evaluation_design


def _json_default(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(value).isoformat()
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if pd.isna(value):
        return None
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )


def _source_summary(measurements: pd.DataFrame, entities: pd.DataFrame) -> dict[str, Any]:
    ordered = entities.sort_values(["event_timestamp", "source_row_number"])
    gaps = ordered["event_timestamp"].diff().dropna().dt.total_seconds()
    source_order_gaps = (
        entities.sort_values("source_row_number")["event_timestamp"]
        .diff()
        .dropna()
        .dt.total_seconds()
    )
    duplicate_measurement_rows = int(measurements.duplicated(keep=False).sum())
    duplicate_complete_rows = int(
        pd.concat(
            [entities[["original_label", "event_timestamp"]], measurements], axis=1
        ).duplicated(keep=False).sum()
    )
    timestamp_counts = entities["event_timestamp"].value_counts()
    return {
        "entity_count": int(len(entities)),
        "measurement_count": int(measurements.shape[1]),
        "pass_count": int((entities["failure_indicator"] == 0).sum()),
        "failure_count": int(entities["failure_indicator"].sum()),
        "original_label_counts": {
            str(key): int(value)
            for key, value in entities["original_label"].value_counts().sort_index().items()
        },
        "timestamp_min": entities["event_timestamp"].min(),
        "timestamp_max": entities["event_timestamp"].max(),
        "timestamp_null_count": int(entities["event_timestamp"].isna().sum()),
        "unique_timestamp_count": int(entities["event_timestamp"].nunique()),
        "duplicate_timestamp_value_count": int((timestamp_counts > 1).sum()),
        "entities_in_timestamp_ties": int(timestamp_counts[timestamp_counts > 1].sum()),
        "maximum_timestamp_tie_size": int(timestamp_counts.max()),
        "source_order_timestamp_reversal_count": int((source_order_gaps < 0).sum()),
        "source_order_zero_gap_count": int((source_order_gaps == 0).sum()),
        "negative_gap_count_after_chronological_sort": int((gaps < 0).sum()),
        "zero_chronological_gap_count": int((gaps == 0).sum()),
        "median_positive_gap_seconds": float(gaps[gaps > 0].median()),
        "maximum_gap_seconds": float(gaps.max()),
        "duplicate_measurement_row_count_including_all_copies": duplicate_measurement_rows,
        "duplicate_complete_source_row_count_including_all_copies": duplicate_complete_rows,
        "overall_missing_cell_count": int(measurements.isna().sum().sum()),
        "overall_missing_cell_fraction": float(measurements.isna().to_numpy().mean()),
        "all_null_measurement_count_overall": int(measurements.isna().all().sum()),
    }


def _persist_database(
    database_path: Path,
    entities: pd.DataFrame,
    measurements: pd.DataFrame,
    sensor_audit: pd.DataFrame,
    split_comparison: pd.DataFrame,
) -> dict[str, int]:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    database_path.unlink(missing_ok=True)
    wide = pd.concat([entities[["entity_id"]], measurements], axis=1)
    with duckdb.connect(str(database_path)) as connection:
        connection.register("entities_frame", entities)
        connection.register("wide_frame", wide)
        connection.register("sensor_frame", sensor_audit)
        connection.register("split_frame", split_comparison)
        connection.execute("CREATE TABLE fact_production_entity AS SELECT * FROM entities_frame")
        connection.execute("CREATE TABLE measurements_wide AS SELECT * FROM wide_frame")
        connection.execute("CREATE TABLE dim_sensor AS SELECT * FROM sensor_frame")
        connection.execute("CREATE TABLE audit_split_candidate AS SELECT * FROM split_frame")
        connection.execute(
            "CREATE UNIQUE INDEX ux_entity ON fact_production_entity(entity_id)"
        )
        connection.execute("CREATE UNIQUE INDEX ux_wide_entity ON measurements_wide(entity_id)")
        connection.execute("CREATE UNIQUE INDEX ux_sensor ON dim_sensor(sensor_id)")
        tables = [
            "fact_production_entity",
            "measurements_wide",
            "dim_sensor",
            "audit_split_candidate",
        ]
        return {
            table: int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
            for table in tables
        }


def build_phase1(config: dict[str, Any]) -> dict[str, Any]:
    """Run the complete, idempotent Phase 1 validation and persistence pipeline."""
    measurements, entities = load_source(config)
    assignments, split_comparison, design = choose_evaluation_design(entities, config)
    entities = entities.assign(split=assignments)
    assert_split_integrity(entities)

    sensor_audit = audit_measurements(measurements, entities, config)
    entity_missingness = missingness_by_entity(measurements, entities)
    source_summary = _source_summary(measurements, entities)
    split_counts = (
        entities.groupby("split", sort=False)
        .agg(
            entity_count=("entity_id", "size"),
            failure_count=("failure_indicator", "sum"),
            start_timestamp=("event_timestamp", "min"),
            end_timestamp=("event_timestamp", "max"),
        )
        .reset_index()
    )

    output_directory = project_path(config["outputs"]["phase1_directory"])
    output_directory.mkdir(parents=True, exist_ok=True)
    sensor_audit.to_csv(output_directory / "sensor_quality.csv", index=False)
    sensor_audit.loc[
        sensor_audit["quality_status"] == "excluded",
        ["sensor_id", "source_column", "exclusion_reason"],
    ].to_csv(output_directory / "sensor_exclusion_log.csv", index=False)
    entity_missingness.to_csv(output_directory / "missingness_by_entity.csv", index=False)
    split_comparison.to_csv(output_directory / "split_comparison.csv", index=False)
    split_counts.to_csv(output_directory / "selected_split_counts.csv", index=False)

    database_path = project_path(config["outputs"]["database"])
    table_counts = _persist_database(
        database_path, entities, measurements, sensor_audit, split_comparison
    )
    manifest_path = project_path(config["data"]["landing_archive"]).parent / "source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    result = {
        "source": source_summary,
        "evaluation_design": design,
        "selected_split_counts": split_counts.to_dict(orient="records"),
        "quality": {
            "eligible_measurement_count": int(
                (sensor_audit["quality_status"] == "eligible").sum()
            ),
            "excluded_measurement_count": int(
                (sensor_audit["quality_status"] == "excluded").sum()
            ),
            "exclusion_reason_counts": {
                reason: int(count)
                for reason, count in (
                    sensor_audit.loc[
                        sensor_audit["exclusion_reason"].ne(""), "exclusion_reason"
                    ]
                    .str.split(";")
                    .explode()
                    .value_counts()
                    .items()
                )
            },
        },
        "source_manifest": manifest,
        "database": {
            "relative_path": str(Path(config["outputs"]["database"]).as_posix()),
            "sha256": sha256_file(database_path),
            "table_counts": table_counts,
        },
    }
    _write_json(output_directory / "phase1_summary.json", result)
    return result
