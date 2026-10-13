"""Tie-safe chronological evaluation design."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SplitCandidate:
    """One candidate chronological allocation and its evidence."""

    allocation: tuple[float, float, float]
    assignments: pd.Series
    summary: dict[str, Any]


def _nearest_group_end(group_ends: np.ndarray, target: float, minimum: int) -> int:
    valid = group_ends[group_ends > minimum]
    if not len(valid):
        raise ValueError("Not enough unique timestamp groups for chronological partitions")
    return int(valid[np.argmin(np.abs(valid - target))])


def chronological_candidate(
    entities: pd.DataFrame, allocation: tuple[float, float, float]
) -> SplitCandidate:
    """Create train/calibration/final partitions without splitting timestamp ties."""
    if not np.isclose(sum(allocation), 1.0):
        raise ValueError(f"Allocation must sum to 1.0: {allocation}")
    ordered = entities.sort_values(["event_timestamp", "source_row_number"], kind="mergesort")
    group_sizes = ordered.groupby("event_timestamp", sort=True).size().to_numpy()
    group_ends = np.cumsum(group_sizes)
    total = len(ordered)
    train_end = _nearest_group_end(group_ends[:-1], total * allocation[0], 0)
    calibration_end = _nearest_group_end(
        group_ends[:-1], total * (allocation[0] + allocation[1]), train_end
    )
    if calibration_end >= total:
        raise ValueError("Chronological allocation left no final-test rows")

    ordered_assignments = pd.Series("final_test", index=ordered.index, dtype="string")
    ordered_assignments.iloc[:train_end] = "reference"
    ordered_assignments.iloc[train_end:calibration_end] = "calibration"
    assignments = ordered_assignments.reindex(entities.index)
    candidate_entities = entities.assign(split=assignments)

    summary: dict[str, Any] = {"allocation": "/".join(f"{value:.0%}" for value in allocation)}
    for split in ("reference", "calibration", "final_test"):
        rows = candidate_entities[candidate_entities["split"] == split]
        summary[f"{split}_entities"] = int(len(rows))
        summary[f"{split}_failures"] = int(rows["failure_indicator"].sum())
        summary[f"{split}_start"] = rows["event_timestamp"].min()
        summary[f"{split}_end"] = rows["event_timestamp"].max()
    return SplitCandidate(allocation=allocation, assignments=assignments, summary=summary)


def choose_evaluation_design(
    entities: pd.DataFrame, config: dict[str, Any]
) -> tuple[pd.Series, pd.DataFrame, dict[str, Any]]:
    """Compare configured candidates and select holdout or rolling fallback."""
    evaluation = config["evaluation"]
    candidates = [
        chronological_candidate(entities, tuple(float(value) for value in allocation))
        for allocation in evaluation["candidate_allocations"]
    ]
    summaries = pd.DataFrame([candidate.summary for candidate in candidates])
    minimum_calibration = int(evaluation["minimum_calibration_failures"])
    minimum_final = int(evaluation["minimum_final_failures"])
    feasible = [
        candidate
        for candidate in candidates
        if candidate.summary["calibration_failures"] >= minimum_calibration
        and candidate.summary["final_test_failures"] >= minimum_final
    ]

    if feasible:
        selected = feasible[0]
        design = {
            "design": "chronological_holdout",
            "allocation": selected.summary["allocation"],
            "reason": (
                "First configured candidate meeting minimum calibration and final-test "
                "failure-count thresholds."
            ),
            "minimum_calibration_failures": minimum_calibration,
            "minimum_final_failures": minimum_final,
        }
        return selected.assignments, summaries, design

    final_feasible = [
        candidate
        for candidate in candidates
        if candidate.summary["final_test_failures"] >= minimum_final
    ]
    if not final_feasible:
        raise RuntimeError(
            "No configured allocation retains the minimum final failures. Dropping the final "
            "directional block requires explicit approval."
        )

    selected = final_feasible[0]
    assignments = selected.assignments.replace({"calibration": "development"})
    design = {
        "design": "rolling_origin_with_final_directional_block",
        "allocation": selected.summary["allocation"],
        "reason": (
            "No single calibration holdout met the configured sparse-failure threshold; "
            "use expanding development folds while preserving the selected final block."
        ),
        "minimum_calibration_failures": minimum_calibration,
        "minimum_final_failures": minimum_final,
    }
    return assignments, summaries, design


def assert_split_integrity(entities: pd.DataFrame) -> None:
    """Reject overlap, temporal reversal, or split timestamp ties."""
    if entities["split"].isna().any():
        raise AssertionError("Every entity must have a split assignment")
    if (entities.groupby("event_timestamp")["split"].nunique() > 1).any():
        raise AssertionError("Entities sharing a timestamp cannot cross split boundaries")

    observed = entities.groupby("split")["event_timestamp"].agg(["min", "max"])
    ordered_names = [
        name
        for name in ("reference", "calibration", "development", "final_test")
        if name in observed.index
    ]
    for earlier, later in zip(ordered_names, ordered_names[1:], strict=False):
        if observed.loc[earlier, "max"] >= observed.loc[later, "min"]:
            raise AssertionError(f"Temporal boundary overlaps between {earlier} and {later}")
