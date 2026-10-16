"""Fixed-budget retrospective review-policy evaluation."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve


def _policy_counts(outcomes: np.ndarray, reviewed: np.ndarray) -> dict[str, float | int]:
    failures_detected = int(np.sum((outcomes == 1) & reviewed))
    failures_missed = int(np.sum((outcomes == 1) & ~reviewed))
    nonfailures_reviewed = int(np.sum((outcomes == 0) & reviewed))
    entities_reviewed = int(reviewed.sum())
    precision = failures_detected / entities_reviewed if entities_reviewed else 0.0
    recall = failures_detected / int(outcomes.sum()) if outcomes.sum() else 0.0
    f2 = 5 * precision * recall / (4 * precision + recall) if precision + recall else 0.0
    return {
        "entities_reviewed": entities_reviewed,
        "failures_detected": failures_detected,
        "failures_missed": failures_missed,
        "nonfailures_reviewed": nonfailures_reviewed,
        "precision": precision,
        "recall": recall,
        "f2": f2,
        "alert_rate": entities_reviewed / len(outcomes),
    }


def _stratified_interval(
    outcomes: np.ndarray,
    reviewed: np.ndarray,
    replicates: int,
    seed: int,
) -> tuple[float, float, float, float, int]:
    generator = np.random.default_rng(seed)
    failure_positions = np.flatnonzero(outcomes == 1)
    nonfailure_positions = np.flatnonzero(outcomes == 0)
    precision_values = np.empty(replicates)
    recall_values = np.empty(replicates)
    for index in range(replicates):
        positions = np.concatenate(
            [
                generator.choice(failure_positions, len(failure_positions), replace=True),
                generator.choice(
                    nonfailure_positions, len(nonfailure_positions), replace=True
                ),
            ]
        )
        counts = _policy_counts(outcomes[positions], reviewed[positions])
        precision_values[index] = counts["precision"]
        recall_values[index] = counts["recall"]
    return (
        float(np.quantile(precision_values, 0.025)),
        float(np.quantile(precision_values, 0.975)),
        float(np.quantile(recall_values, 0.025)),
        float(np.quantile(recall_values, 0.975)),
        replicates,
    )


def evaluate_budgets(
    ranked_scores: pd.DataFrame,
    config: dict[str, Any],
    model: str,
    configuration_id: str,
    evaluation_period: str,
    include_f2_diagnostic: bool = False,
) -> pd.DataFrame:
    """Evaluate predeclared dataset-period budgets on a ranked score table."""
    settings = config["phase4"]
    ordered = ranked_scores.sort_values("risk_rank").reset_index(drop=True)
    outcomes = ordered["failure_indicator"].to_numpy(dtype=int)
    scenarios: list[tuple[str, int, float | None]] = []
    for percentage in settings["percentage_budgets"]:
        review_count = int(np.ceil(float(percentage) * len(ordered)))
        scenarios.append((f"top_{int(percentage * 100)}_percent", review_count, None))
    for review_count in settings["fixed_top_k_budgets"]:
        scenarios.append((f"top_{int(review_count)}", min(int(review_count), len(ordered)), None))
    if include_f2_diagnostic:
        precision, recall, thresholds = precision_recall_curve(
            outcomes, ordered["raw_score"].to_numpy(dtype=float)
        )
        f2_values = np.divide(
            5 * precision * recall,
            4 * precision + recall,
            out=np.zeros_like(precision),
            where=(4 * precision + recall) > 0,
        )
        best = int(np.argmax(f2_values[:-1])) if len(thresholds) else 0
        threshold = float(thresholds[best]) if len(thresholds) else np.inf
        review_count = int((ordered["raw_score"] >= threshold).sum())
        scenarios.append(("f2_max_diagnostic", review_count, threshold))

    records: list[dict[str, Any]] = []
    for scenario_index, (scenario, review_count, threshold) in enumerate(scenarios):
        reviewed = np.arange(len(ordered)) < review_count
        counts = _policy_counts(outcomes, reviewed)
        intervals = _stratified_interval(
            outcomes,
            reviewed,
            int(settings["evaluation_bootstrap_replicates"]),
            int(config["project"]["random_seed"]) + scenario_index,
        )
        records.append(
            {
                "model": model,
                "configuration_id": configuration_id,
                "evaluation_period": evaluation_period,
                "policy_scenario": scenario,
                "score_threshold": threshold,
                **counts,
                "entity_count": len(outcomes),
                "failure_count": int(outcomes.sum()),
                "precision_ci_lower": intervals[0],
                "precision_ci_upper": intervals[1],
                "recall_ci_lower": intervals[2],
                "recall_ci_upper": intervals[3],
                "uncertainty_method": "outcome_stratified_approximate",
                "bootstrap_usable_replicates": intervals[4],
            }
        )
    return pd.DataFrame(records)
