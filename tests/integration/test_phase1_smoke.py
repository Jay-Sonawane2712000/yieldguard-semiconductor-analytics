import json
import zipfile
from pathlib import Path

import duckdb

from yieldguard.pipeline import build_phase1


def test_phase1_pipeline_builds_reconciled_duckdb(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    raw.mkdir()
    rows = 30
    measurement_lines = []
    label_lines = []
    for index in range(rows):
        variable = index / 10
        measurement_lines.append(f"{variable} 1 NaN {index % 3} {index + 5}\n")
        label = 1 if index % 5 == 0 else -1
        label_lines.append(f'{label} "{index + 1:02d}/01/2024 00:00:00"\n')
    (raw / "secom.data").write_text("".join(measurement_lines), encoding="utf-8")
    (raw / "secom_labels.data").write_text("".join(label_lines), encoding="utf-8")
    (raw / "secom.names").write_text("synthetic fixture", encoding="utf-8")
    with zipfile.ZipFile(raw / "secom.zip", "w") as archive:
        archive.write(raw / "secom.data", "secom.data")
    (raw / "source_manifest.json").write_text(
        json.dumps({"dataset": "synthetic-test-fixture"}), encoding="utf-8"
    )

    config = {
        "data": {
            "landing_archive": str(raw / "secom.zip"),
            "measurement_file": str(raw / "secom.data"),
            "label_file": str(raw / "secom_labels.data"),
            "timestamp_format": "%d/%m/%Y %H:%M:%S",
            "pass_label": -1,
            "failure_label": 1,
            "source_version": "synthetic-test-fixture",
        },
        "quality": {
            "max_missing_fraction": 0.4,
            "min_non_null_count": 5,
            "near_constant_dominant_fraction": 0.995,
            "min_reference_variance": 1e-12,
            "temporal_bin_count": 5,
            "min_temporal_coverage_fraction": 0.8,
            "extreme_iqr_multiplier": 3.0,
        },
        "evaluation": {
            "minimum_calibration_failures": 1,
            "minimum_final_failures": 1,
            "candidate_allocations": [[0.6, 0.2, 0.2]],
        },
        "outputs": {
            "database": str(processed / "yieldguard.duckdb"),
            "phase1_directory": str(processed / "phase1"),
        },
    }

    result = build_phase1(config)

    assert result["source"]["entity_count"] == rows
    assert result["database"]["table_counts"]["fact_production_entity"] == rows
    assert result["database"]["table_counts"]["measurements_wide"] == rows
    with duckdb.connect(str(processed / "yieldguard.duckdb"), read_only=True) as connection:
        assert connection.execute(
            "SELECT COUNT(DISTINCT entity_id) FROM fact_production_entity"
        ).fetchone()[0] == rows
