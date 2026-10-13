import pandas as pd

from yieldguard.splits import assert_split_integrity, chronological_candidate


def _entities() -> pd.DataFrame:
    timestamps = pd.to_datetime(
        [
            "2024-01-01",
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
            "2024-01-05",
            "2024-01-06",
            "2024-01-07",
            "2024-01-08",
            "2024-01-09",
        ]
    )
    return pd.DataFrame(
        {
            "entity_id": [f"E{index:06d}" for index in range(1, 11)],
            "source_row_number": range(1, 11),
            "event_timestamp": timestamps,
            "failure_indicator": [0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
        }
    )


def test_chronological_candidate_keeps_timestamp_ties_together() -> None:
    entities = _entities()
    candidate = chronological_candidate(entities, (0.6, 0.2, 0.2))
    assigned = entities.assign(split=candidate.assignments)

    assert assigned.groupby("event_timestamp")["split"].nunique().max() == 1
    assert_split_integrity(assigned)


def test_chronological_candidate_is_deterministic() -> None:
    entities = _entities()

    first = chronological_candidate(entities, (0.6, 0.2, 0.2)).assignments
    second = chronological_candidate(entities, (0.6, 0.2, 0.2)).assignments

    pd.testing.assert_series_equal(first, second)
