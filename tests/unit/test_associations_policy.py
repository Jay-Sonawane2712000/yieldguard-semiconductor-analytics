import numpy as np
import pandas as pd

from yieldguard.associations import _adjust_fdr, _cliffs_delta
from yieldguard.policy import evaluate_budgets


def test_cliffs_delta_direction_is_failure_higher_positive() -> None:
    assert _cliffs_delta(np.array([3.0, 4.0]), np.array([1.0, 2.0])) == 1.0
    assert _cliffs_delta(np.array([1.0, 2.0]), np.array([3.0, 4.0])) == -1.0


def test_fdr_adjustment_is_monotone_in_ranked_p_values() -> None:
    p_values = np.array([0.04, 0.001, 0.03, 0.2])
    adjusted = _adjust_fdr(p_values)
    ordered = adjusted[np.argsort(p_values)]

    assert (ordered[:-1] <= ordered[1:]).all()
    assert (adjusted >= p_values).all()


def test_budget_evaluation_reports_counts_and_approximate_intervals() -> None:
    ranked = pd.DataFrame(
        {
            "risk_rank": np.arange(1, 101),
            "raw_score": np.linspace(1.0, 0.0, 100),
            "failure_indicator": [1] * 5 + [0] * 90 + [1] * 5,
        }
    )
    config = {
        "project": {"random_seed": 7},
        "phase4": {
            "percentage_budgets": [0.10],
            "fixed_top_k_budgets": [5],
            "evaluation_bootstrap_replicates": 50,
        },
    }
    result = evaluate_budgets(
        ranked, config, "model", "config", "calibration", include_f2_diagnostic=True
    ).set_index("policy_scenario")

    assert result.loc["top_10_percent", "entities_reviewed"] == 10
    assert result.loc["top_10_percent", "failures_detected"] == 5
    assert result.loc["top_10_percent", "failures_missed"] == 5
    assert result.loc["top_10_percent", "precision"] == 0.5
    assert result.loc["top_10_percent", "recall"] == 0.5
    assert result.loc["top_10_percent", "bootstrap_usable_replicates"] == 50
