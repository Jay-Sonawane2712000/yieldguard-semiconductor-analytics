from pathlib import Path

import pytest

from yieldguard.ingest import read_labels, read_measurements


def test_read_labels_normalizes_quoted_timestamps(tmp_path: Path) -> None:
    source = tmp_path / "labels.data"
    source.write_text(
        '-1 "19/07/2008 11:55:00"\n1 "20/07/2008 12:01:02"\n', encoding="utf-8"
    )

    result = read_labels(source, "%d/%m/%Y %H:%M:%S")

    assert result["original_label"].tolist() == [-1, 1]
    assert result["event_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist() == [
        "2008-07-19 11:55:00",
        "2008-07-20 12:01:02",
    ]


def test_read_labels_rejects_malformed_rows(tmp_path: Path) -> None:
    source = tmp_path / "labels.data"
    source.write_text("0 invalid\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid label row"):
        read_labels(source, "%d/%m/%Y %H:%M:%S")


def test_read_measurements_assigns_stable_anonymous_names(tmp_path: Path) -> None:
    source = tmp_path / "measurements.data"
    source.write_text("1 NaN 3\n4 5 6\n", encoding="utf-8")

    result = read_measurements(source)

    assert result.columns.tolist() == [
        "measurement_000",
        "measurement_001",
        "measurement_002",
    ]
    assert result.shape == (2, 3)
    assert result.iloc[0, 1] != result.iloc[0, 1]
