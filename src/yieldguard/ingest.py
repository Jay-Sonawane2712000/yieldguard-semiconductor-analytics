"""Strict parsing and validation for SECOM source files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from yieldguard.config import project_path

LABEL_PATTERN = re.compile(r'^\s*(-?1)\s+"?([^"\r\n]+)"?\s*$')


def read_measurements(path: Path) -> pd.DataFrame:
    """Read the whitespace-delimited measurement matrix."""
    frame = pd.read_csv(path, sep=r"\s+", header=None, na_values=["NaN"], dtype=float)
    if frame.empty:
        raise ValueError("Measurement source is empty")
    frame.columns = [f"measurement_{index:03d}" for index in range(frame.shape[1])]
    return frame


def read_labels(path: Path, timestamp_format: str) -> pd.DataFrame:
    """Parse label/timestamp lines without relying on delimiter quoting behavior."""
    records: list[tuple[int, str]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            match = LABEL_PATTERN.match(line)
            if not match:
                raise ValueError(f"Invalid label row at line {line_number}: {line.rstrip()!r}")
            records.append((int(match.group(1)), match.group(2)))
    frame = pd.DataFrame(records, columns=["original_label", "timestamp_text"])
    frame["event_timestamp"] = pd.to_datetime(
        frame.pop("timestamp_text"), format=timestamp_format, errors="raise"
    )
    return frame


def load_source(config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load aligned measurements and entity metadata with strict invariants."""
    data_config = config["data"]
    measurements = read_measurements(project_path(data_config["measurement_file"]))
    labels = read_labels(
        project_path(data_config["label_file"]), data_config["timestamp_format"]
    )
    if len(measurements) != len(labels):
        raise ValueError(
            f"Row-count mismatch: {len(measurements)} measurement rows and "
            f"{len(labels)} label rows"
        )

    allowed_labels = {int(data_config["pass_label"]), int(data_config["failure_label"])}
    observed_labels = set(labels["original_label"].unique())
    if observed_labels != allowed_labels:
        raise ValueError(
            f"Expected exactly labels {sorted(allowed_labels)}, observed {sorted(observed_labels)}"
        )
    if labels["event_timestamp"].isna().any():
        raise ValueError("One or more timestamps could not be parsed")

    labels.insert(0, "source_row_number", np.arange(1, len(labels) + 1, dtype=int))
    labels.insert(0, "entity_id", [f"E{index:06d}" for index in range(1, len(labels) + 1)])
    labels["failure_indicator"] = (
        labels["original_label"] == int(data_config["failure_label"])
    ).astype("int8")
    labels["source_data_version"] = data_config["source_version"]
    labels["chronological_order"] = (
        labels.sort_values(["event_timestamp", "source_row_number"], kind="mergesort")
        .reset_index()
        .assign(order=lambda value: np.arange(1, len(value) + 1, dtype=int))
        .set_index("index")["order"]
        .reindex(labels.index)
        .astype(int)
    )
    return measurements, labels
