"""Leakage-safe risk ranking, monitoring baselines, and evaluation helpers."""

from __future__ import annotations

from typing import Any

import duckdb
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_model(model_family: str, parameters: dict[str, Any], seed: int) -> Any:
    """Build one complete approved model configuration."""
    if model_family == "logistic_regression":
        if parameters["penalty"] != "l2":
            raise ValueError("Only the frozen L2 logistic penalty is supported")
        preprocessing = ColumnTransformer(
            [
                (
                    "measurements",
                    Pipeline(
                        [
                            ("imputer", SimpleImputer(strategy="median")),
                            ("scaler", StandardScaler()),
                        ]
                    ),
                    list(parameters["feature_names"]),
                )
            ],
            remainder="drop",
        )
        classifier = LogisticRegression(
            C=float(parameters["c"]),
            l1_ratio=0.0,
            solver="liblinear",
            class_weight="balanced",
            max_iter=2000,
            random_state=seed,
        )
        return Pipeline([("preprocessing", preprocessing), ("classifier", classifier)])
    if model_family == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(
            learning_rate=float(parameters["learning_rate"]),
            max_iter=int(parameters["max_iter"]),
            max_leaf_nodes=int(parameters["max_leaf_nodes"]),
            min_samples_leaf=int(parameters["min_samples_leaf"]),
            l2_regularization=float(parameters["l2_regularization"]),
            class_weight="balanced",
            random_state=seed,
        )
    raise ValueError(f"Unsupported model family: {model_family}")


def calibration_summary(
    outcomes: np.ndarray, probabilities: np.ndarray, bin_count: int
) -> tuple[pd.DataFrame, float]:
    """Return deterministic equal-frequency calibration bins and weighted ECE."""
    frame = pd.DataFrame({"outcome": outcomes, "probability": probabilities})
    frame["calibration_bin"] = pd.qcut(
        frame["probability"].rank(method="first"), bin_count, labels=False
    )
    bins = (
        frame.groupby("calibration_bin", sort=True)
        .agg(
            entity_count=("outcome", "size"),
            observed_failure_rate=("outcome", "mean"),
            mean_predicted_probability=("probability", "mean"),
            minimum_probability=("probability", "min"),
            maximum_probability=("probability", "max"),
        )
        .reset_index()
    )
    ece = float(
        (
            bins["entity_count"]
            * np.abs(
                bins["observed_failure_rate"] - bins["mean_predicted_probability"]
            )
        ).sum()
        / len(frame)
    )
    return bins, ece


def score_metrics(outcomes: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    """Calculate ranking and raw-probability metrics."""
    return {
        "pr_auc": float(average_precision_score(outcomes, scores)),
        "roc_auc": float(roc_auc_score(outcomes, scores)),
        "brier_score": float(brier_score_loss(outcomes, scores)),
        "positive_prevalence": float(np.mean(outcomes)),
    }


def deterministic_rank(
    entities: pd.DataFrame,
    primary_score: np.ndarray | pd.Series,
    secondary_score: np.ndarray | pd.Series | None = None,
) -> pd.DataFrame:
    """Rank descending scores, then timestamp and entity ID."""
    ranked = entities.loc[:, ["entity_id", "event_timestamp", "split"]].copy()
    ranked["raw_score"] = np.asarray(primary_score, dtype=float)
    ranked["tie_breaker"] = (
        np.asarray(secondary_score, dtype=float) if secondary_score is not None else 0.0
    )
    ranked = ranked.sort_values(
        ["raw_score", "tie_breaker", "event_timestamp", "entity_id"],
        ascending=[False, False, True, True],
        kind="mergesort",
    ).reset_index(drop=True)
    ranked["risk_rank"] = np.arange(1, len(ranked) + 1)
    return ranked


def monitoring_baseline(
    connection: duckdb.DuckDBPyConnection, split: str
) -> pd.DataFrame:
    """Build the fixed label-blind monitoring count/severity ranking."""
    signals = connection.execute(
        """
        SELECT entity_id, event_timestamp, split, sensor_id, method, statistic,
               center_line, lower_control_limit, upper_control_limit,
               violation_indicator
        FROM fact_spc_signal
        WHERE split = ?
        """,
        [split],
    ).fetchdf()
    multivariate = connection.execute(
        """
        SELECT entity_id, event_timestamp, split, t2_statistic, t2_limit, t2_alert,
               q_statistic, q_limit, q_alert
        FROM fact_multivariate_alert
        WHERE split = ?
        """,
        [split],
    ).fetchdf()
    available = signals["statistic"].notna()
    individual = signals["method"].isin(["I", "EWMA"]) & available
    upper_side = signals["statistic"] >= signals["center_line"]
    denominator = np.where(
        upper_side,
        signals["upper_control_limit"] - signals["center_line"],
        signals["center_line"] - signals["lower_control_limit"],
    )
    mr = signals["method"].eq("MR") & available
    invalid_individual = individual & (~np.isfinite(denominator) | (denominator <= 0))
    invalid_mr = mr & (
        ~np.isfinite(signals["upper_control_limit"])
        | (signals["upper_control_limit"] <= 0)
    )
    if invalid_individual.any() or invalid_mr.any():
        raise ValueError("Monitoring severity contains a non-finite or non-positive denominator")
    signals["severity"] = np.nan
    signals.loc[individual, "severity"] = (
        np.abs(
            signals.loc[individual, "statistic"]
            - signals.loc[individual, "center_line"]
        )
        / denominator[individual]
    )
    signals.loc[mr, "severity"] = (
        signals.loc[mr, "statistic"] / signals.loc[mr, "upper_control_limit"]
    )
    imr = (
        signals.loc[signals["method"].isin(["I", "MR"]) & signals["violation_indicator"]]
        .groupby("entity_id")["sensor_id"]
        .nunique()
        .rename("imr_signal_count")
    )
    ewma = (
        signals.loc[signals["method"].eq("EWMA") & signals["violation_indicator"]]
        .groupby("entity_id")["sensor_id"]
        .nunique()
        .rename("ewma_signal_count")
    )
    maximum_univariate_severity = signals.groupby("entity_id")["severity"].max()
    multivariate_limits = multivariate[["t2_limit", "q_limit"]].to_numpy()
    if ((~np.isfinite(multivariate_limits)) | (multivariate_limits <= 0)).any():
        raise ValueError("Multivariate severity contains an invalid limit")
    multivariate["t2_severity"] = multivariate["t2_statistic"] / multivariate["t2_limit"]
    multivariate["q_severity"] = multivariate["q_statistic"] / multivariate["q_limit"]
    result = multivariate.merge(imr, on="entity_id", how="left").merge(
        ewma, on="entity_id", how="left"
    )
    result[["imr_signal_count", "ewma_signal_count"]] = result[
        ["imr_signal_count", "ewma_signal_count"]
    ].fillna(0)
    result["monitoring_signal_count"] = (
        result["imr_signal_count"]
        + result["ewma_signal_count"]
        + result["t2_alert"].astype(int)
        + result["q_alert"].astype(int)
    )
    result["entity_tie_breaker"] = np.nanmax(
        np.column_stack(
            [
                result["entity_id"].map(maximum_univariate_severity).to_numpy(),
                result["t2_severity"].to_numpy(),
                result["q_severity"].to_numpy(),
            ]
        ),
        axis=1,
    )
    result["entity_tie_breaker"] = result["entity_tie_breaker"].fillna(0.0)
    ranked = deterministic_rank(
        result, result["monitoring_signal_count"], result["entity_tie_breaker"]
    )
    return ranked.merge(
        result[
            [
                "entity_id",
                "imr_signal_count",
                "ewma_signal_count",
                "t2_alert",
                "q_alert",
                "t2_severity",
                "q_severity",
            ]
        ],
        on="entity_id",
        how="left",
    )
