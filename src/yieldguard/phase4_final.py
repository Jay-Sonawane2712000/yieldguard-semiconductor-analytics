"""Frozen final-test evaluation and engineering-review queue construction."""

from __future__ import annotations

import json
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from yieldguard.config import PROJECT_ROOT, project_path
from yieldguard.ingest import read_measurements
from yieldguard.phase4_development import _selected_specification
from yieldguard.policy import evaluate_budgets
from yieldguard.risk import (
    build_model,
    calibration_summary,
    deterministic_rank,
    metric_intervals,
    monitoring_baseline,
    score_metrics,
)


def _evaluation_rows(
    outcomes: np.ndarray,
    scores: np.ndarray,
    model: str,
    configuration_id: str,
    config: dict[str, Any],
    probability_score: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    point = score_metrics(outcomes, scores, probability_score=probability_score)
    intervals = metric_intervals(
        outcomes,
        scores,
        int(config["phase4"]["evaluation_bootstrap_replicates"]),
        int(config["project"]["random_seed"]),
        probability_score,
    )
    records = []
    for metric in ("pr_auc", "roc_auc", "brier_score"):
        if metric == "brier_score" and not probability_score:
            continue
        records.append(
            {
                "model": model,
                "configuration_id": configuration_id,
                "evaluation_period": "final_test",
                "metric": metric,
                "estimate": point[metric],
                "interval_lower": intervals[f"{metric}_ci_lower"],
                "interval_upper": intervals[f"{metric}_ci_upper"],
                "entity_count": len(outcomes),
                "positive_count": int(outcomes.sum()),
                "negative_count": int((outcomes == 0).sum()),
                "uncertainty_method": intervals["uncertainty_method"],
                "bootstrap_usable_replicates": intervals[
                    "bootstrap_usable_replicates"
                ],
            }
        )
    bins = pd.DataFrame()
    if probability_score:
        bins, ece = calibration_summary(
            outcomes, scores, int(config["phase4"]["calibration_bins"])
        )
        records.append(
            {
                "model": model,
                "configuration_id": configuration_id,
                "evaluation_period": "final_test",
                "metric": "expected_calibration_error",
                "estimate": ece,
                "interval_lower": np.nan,
                "interval_upper": np.nan,
                "entity_count": len(outcomes),
                "positive_count": int(outcomes.sum()),
                "negative_count": int((outcomes == 0).sum()),
                "uncertainty_method": "descriptive_no_interval",
                "bootstrap_usable_replicates": 0,
            }
        )
        bins.insert(0, "configuration_id", configuration_id)
        bins.insert(0, "model", model)
        bins.insert(2, "evaluation_period", "final_test")
    return pd.DataFrame(records), bins


def _build_queue(
    connection: duckdb.DuckDBPyConnection,
    final_entities: pd.DataFrame,
    final_features: pd.DataFrame,
    selected_ranking: pd.DataFrame,
    headline_count: int,
) -> pd.DataFrame:
    queue = selected_ranking.copy()
    queue["headline_review_indicator"] = queue["risk_rank"] <= headline_count
    queue["retrospective_outcome"] = queue["entity_id"].map(
        final_entities.set_index("entity_id")["failure_indicator"]
    )
    monitoring = connection.execute(
        """
        SELECT entity_id, imr_signal_measurement_count, ewma_signal_measurement_count
        FROM mart_univariate_entity_summary WHERE split = 'final_test'
        """
    ).fetchdf()
    multivariate = connection.execute(
        """
        SELECT entity_id, t2_alert, q_alert
        FROM fact_multivariate_alert WHERE split = 'final_test'
        """
    ).fetchdf()
    contributors = connection.execute(
        """
        SELECT entity_id, statistic_type,
               string_agg(sensor_id, ', ' ORDER BY contribution_rank) AS top_measurements
        FROM fact_alert_contribution
        WHERE split = 'final_test' AND contribution_rank <= 3
        GROUP BY entity_id, statistic_type
        """
    ).fetchdf().pivot(index="entity_id", columns="statistic_type", values="top_measurements")
    contributors = contributors.rename(
        columns={"T2": "top_t2_measurements", "Q_SPE": "top_q_measurements"}
    ).reset_index()
    queue = queue.merge(monitoring, on="entity_id", how="left").merge(
        multivariate, on="entity_id", how="left"
    ).merge(contributors, on="entity_id", how="left")
    missing_count = pd.Series(
        final_features.isna().sum(axis=1).to_numpy(),
        index=final_entities["entity_id"],
    )
    queue["eligible_measurement_missing_count"] = queue["entity_id"].map(missing_count)
    queue["data_quality_warning"] = queue["eligible_measurement_missing_count"] > 0

    def reason_codes(row: pd.Series) -> str:
        reasons = []
        if row["headline_review_indicator"]:
            reasons.append("FROZEN_MODEL_TOP_10_PERCENT")
        if row["imr_signal_measurement_count"] > 0:
            reasons.append("IMR_EXCURSION")
        if row["ewma_signal_measurement_count"] > 0:
            reasons.append("EWMA_EXCURSION")
        if row["t2_alert"]:
            reasons.append("T2_EXCURSION")
        if row["q_alert"]:
            reasons.append("Q_SPE_EXCURSION")
        if row["data_quality_warning"]:
            reasons.append("MISSING_ELIGIBLE_MEASUREMENT")
        return ";".join(reasons) if reasons else "NO_FROZEN_REVIEW_REASON"

    queue["reason_codes"] = queue.apply(reason_codes, axis=1)
    return queue


def run_phase4_final(config: dict[str, Any]) -> dict[str, Any]:
    """Run the frozen final evaluation only after the budget decision is committed."""
    settings = config["phase4"]
    if settings.get("headline_budget_policy") != "top_10_percent":
        raise ValueError("A frozen supported headline budget is required")
    database_path = project_path(config["outputs"]["database"])
    measurements = read_measurements(project_path(config["data"]["measurement_file"]))
    with duckdb.connect(str(database_path)) as connection:
        sensor_ids = connection.execute(
            """
            SELECT sensor_id FROM dim_sensor
            WHERE quality_status = 'eligible' ORDER BY source_column
            """
        ).fetchdf()["sensor_id"].tolist()
        development_entities = connection.execute(
            """
            SELECT entity_id, source_row_number, event_timestamp, split, failure_indicator
            FROM fact_production_entity
            WHERE split IN ('reference', 'calibration') ORDER BY source_row_number
            """
        ).fetchdf()
        final_entities = connection.execute(
            """
            SELECT entity_id, source_row_number, event_timestamp, split, failure_indicator
            FROM fact_production_entity
            WHERE split = 'final_test' ORDER BY source_row_number
            """
        ).fetchdf()
        development_positions = development_entities["source_row_number"].to_numpy(int) - 1
        final_positions = final_entities["source_row_number"].to_numpy(int) - 1
        development_features = measurements.iloc[development_positions].loc[:, sensor_ids]
        final_features = measurements.iloc[final_positions].loc[:, sensor_ids].reset_index(
            drop=True
        )
        development_outcomes = development_entities["failure_indicator"].to_numpy(int)
        final_outcomes = final_entities["failure_indicator"].to_numpy(int)

        specification = _selected_specification(settings)
        specification.pop("id")
        specification["feature_names"] = sensor_ids
        model = build_model(
            settings["selected_model"],
            specification,
            int(config["project"]["random_seed"]),
        )
        model.fit(development_features, development_outcomes)
        probabilities = model.predict_proba(final_features)[:, 1]
        selected = deterministic_rank(final_entities, probabilities)
        selected["failure_indicator"] = selected["entity_id"].map(
            final_entities.set_index("entity_id")["failure_indicator"]
        )
        selected["model"] = settings["selected_model"]
        selected["configuration_id"] = settings["selected_configuration_id"]
        selected["calibrated_probability"] = selected["raw_score"]

        prevalence = float(development_outcomes.mean())
        prevalence_scores = np.full(len(final_outcomes), prevalence)
        prevalence_ranked = deterministic_rank(final_entities, prevalence_scores)
        prevalence_ranked["failure_indicator"] = prevalence_ranked["entity_id"].map(
            final_entities.set_index("entity_id")["failure_indicator"]
        )
        prevalence_ranked["model"] = "prevalence_baseline"
        prevalence_ranked["configuration_id"] = "prevalence-development-v1"
        prevalence_ranked["calibrated_probability"] = prevalence_ranked["raw_score"]

        monitoring = monitoring_baseline(connection, "final_test")
        monitoring["failure_indicator"] = monitoring["entity_id"].map(
            final_entities.set_index("entity_id")["failure_indicator"]
        )
        monitoring["model"] = "monitoring_baseline"
        monitoring["configuration_id"] = "fixed-monitoring-v1"
        monitoring["calibrated_probability"] = np.nan

        evaluation_frames = []
        calibration_frames = []
        for ranked, model_name, configuration_id, is_probability in (
            (
                selected,
                settings["selected_model"],
                settings["selected_configuration_id"],
                True,
            ),
            (prevalence_ranked, "prevalence_baseline", "prevalence-development-v1", True),
            (monitoring, "monitoring_baseline", "fixed-monitoring-v1", False),
        ):
            ranked_by_entity = ranked.sort_values("entity_id")
            scores = ranked_by_entity["raw_score"].to_numpy(float)
            if model_name == "monitoring_baseline":
                scores = scores + ranked_by_entity["tie_breaker"].to_numpy(float) * 1e-12
            outcome_lookup = final_entities.set_index("entity_id")["failure_indicator"]
            outcomes = ranked_by_entity["entity_id"].map(outcome_lookup).to_numpy(int)
            evaluation, bins = _evaluation_rows(
                outcomes, scores, model_name, configuration_id, config, is_probability
            )
            evaluation_frames.append(evaluation)
            if not bins.empty:
                calibration_frames.append(bins)
        evaluations = pd.concat(evaluation_frames, ignore_index=True)
        final_calibration = pd.concat(calibration_frames, ignore_index=True)

        policy_frames = []
        for ranked, model_name, configuration_id in (
            (selected, settings["selected_model"], settings["selected_configuration_id"]),
            (prevalence_ranked, "prevalence_baseline", "prevalence-development-v1"),
            (monitoring, "monitoring_baseline", "fixed-monitoring-v1"),
        ):
            policy_frames.append(
                evaluate_budgets(
                    ranked,
                    config,
                    model_name,
                    configuration_id,
                    "final_test",
                    include_f2_diagnostic=False,
                )
            )
        final_policies = pd.concat(policy_frames, ignore_index=True)
        calibration_policies = connection.execute(
            "SELECT * FROM fact_policy_evaluation WHERE evaluation_period = 'calibration'"
        ).fetchdf()
        all_policies = pd.concat([calibration_policies, final_policies], ignore_index=True)

        headline_count = int(np.ceil(settings["headline_budget_fraction"] * len(final_entities)))
        queue = _build_queue(
            connection, final_entities, final_features, selected, headline_count
        )
        risk_scores = pd.concat(
            [selected, prevalence_ranked, monitoring], ignore_index=True, sort=False
        )
        risk_scores["headline_review_indicator"] = (
            risk_scores["risk_rank"] <= headline_count
        )

        connection.register("risk_score_frame", risk_scores)
        connection.register("model_evaluation_frame", evaluations)
        connection.register("final_calibration_frame", final_calibration)
        connection.register("all_policy_frame", all_policies)
        connection.register("review_queue_frame", queue)
        connection.execute(
            "CREATE OR REPLACE TABLE fact_failure_risk AS SELECT * FROM risk_score_frame"
        )
        connection.execute(
            "CREATE OR REPLACE TABLE fact_model_evaluation AS "
            "SELECT * FROM model_evaluation_frame"
        )
        connection.execute(
            "CREATE OR REPLACE TABLE fact_model_calibration AS "
            "SELECT * FROM final_calibration_frame"
        )
        connection.execute(
            "CREATE OR REPLACE TABLE fact_policy_evaluation AS SELECT * FROM all_policy_frame"
        )
        connection.execute(
            "CREATE OR REPLACE TABLE fact_engineering_review_queue AS "
            "SELECT * FROM review_queue_frame"
        )
        connection.execute(
            "CREATE UNIQUE INDEX ux_review_queue "
            "ON fact_engineering_review_queue(entity_id)"
        )
        connection.execute(
            "CREATE UNIQUE INDEX ux_failure_risk ON fact_failure_risk(model, entity_id)"
        )
        connection.execute(
            (PROJECT_ROOT / "sql/marts/030_phase4_marts.sql").read_text(encoding="utf-8")
        )

    if len(queue) != len(final_entities) or not queue["entity_id"].is_unique:
        raise AssertionError("Review queue grain does not reconcile")
    if int(queue["headline_review_indicator"].sum()) != headline_count:
        raise AssertionError("Frozen review budget count does not reconcile")
    headline = final_policies.loc[
        final_policies["model"].eq(settings["selected_model"])
        & final_policies["policy_scenario"].eq(settings["headline_budget_policy"])
    ].iloc[0]
    if int(headline["entities_reviewed"]) != headline_count:
        raise AssertionError("Queue and policy review counts disagree")

    output_directory = project_path("data/processed/phase4")
    evaluations.to_csv(output_directory / "final_model_evaluation.csv", index=False)
    final_calibration.to_csv(output_directory / "final_calibration_bins.csv", index=False)
    all_policies.to_csv(output_directory / "all_policy_evaluation.csv", index=False)
    queue.to_csv(output_directory / "engineering_review_queue.csv", index=False)
    result = {
        "frozen_budget_commit_precedes_evaluation": True,
        "development_entity_count": len(development_entities),
        "final_entity_count": len(final_entities),
        "final_failure_count": int(final_outcomes.sum()),
        "selected_model": settings["selected_model"],
        "selected_configuration_id": settings["selected_configuration_id"],
        "headline_budget_policy": settings["headline_budget_policy"],
        "headline_result": headline.to_dict(),
        "model_evaluation": evaluations.to_dict(orient="records"),
        "queue_row_count": len(queue),
        "queue_review_count": int(queue["headline_review_indicator"].sum()),
        "queue_failure_count": int(queue["retrospective_outcome"].sum()),
    }
    (output_directory / "final_evaluation_summary.json").write_text(
        json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"
    )
    return result
