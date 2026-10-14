"""Reference-fitted PCA monitoring with traceable T-squared and Q contributions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class PCAArtifacts:
    """Frozen numerical artifacts needed to audit a fitted PCA monitor."""

    sensor_ids: tuple[str, ...]
    imputation_values: np.ndarray
    scaling_means: np.ndarray
    scaling_scales: np.ndarray
    components: np.ndarray
    explained_variance: np.ndarray
    explained_variance_ratio: np.ndarray
    t2_limit: float
    q_limit: float


def _top_contributions(
    values: np.ndarray,
    entities: pd.DataFrame,
    sensor_ids: list[str],
    statistic_type: str,
    top_k: int,
    model_version: str,
) -> pd.DataFrame:
    absolute = np.abs(values)
    selected = np.argsort(-absolute, axis=1, kind="stable")[:, :top_k]
    rows: list[dict[str, Any]] = []
    for entity_position, sensor_positions in enumerate(selected):
        denominator = float(absolute[entity_position].sum())
        entity = entities.iloc[entity_position]
        for rank, sensor_position in enumerate(sensor_positions, start=1):
            contribution = float(values[entity_position, sensor_position])
            rows.append(
                {
                    "contribution_id": (
                        f"{entity.entity_id}|{statistic_type}|{rank:02d}"
                    ),
                    "entity_id": entity.entity_id,
                    "event_timestamp": entity.event_timestamp,
                    "split": entity.split,
                    "statistic_type": statistic_type,
                    "sensor_id": sensor_ids[sensor_position],
                    "contribution": contribution,
                    "absolute_contribution": abs(contribution),
                    "contribution_rank": rank,
                    "contribution_share": (
                        abs(contribution) / denominator if denominator else 0.0
                    ),
                    "model_version": model_version,
                }
            )
    return pd.DataFrame(rows)


def fit_pca_monitor(
    measurements: pd.DataFrame,
    entities: pd.DataFrame,
    sensor_ids: list[str],
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, PCAArtifacts, dict[str, float]]:
    """Fit on reference measurements and score every entity without using outcomes."""
    if len(measurements) != len(entities):
        raise ValueError("Measurements and entities must have the same row count")
    if not sensor_ids:
        raise ValueError("At least one eligible sensor is required")

    settings = config["pca"]
    reference_mask = entities["split"].eq("reference").to_numpy()
    if not reference_mask.any():
        raise ValueError("A non-empty reference split is required")
    matrix = measurements.loc[:, sensor_ids].to_numpy(dtype=float)
    reference_matrix = matrix[reference_mask]

    imputer = SimpleImputer(strategy="median")
    reference_imputed = imputer.fit_transform(reference_matrix)
    all_imputed = imputer.transform(matrix)
    scaler = StandardScaler()
    reference_scaled = scaler.fit_transform(reference_imputed)
    all_scaled = scaler.transform(all_imputed)

    full_pca = PCA(svd_solver="full")
    full_pca.fit(reference_scaled)
    cumulative_variance = np.cumsum(full_pca.explained_variance_ratio_)
    component_count = int(
        np.searchsorted(cumulative_variance, settings["explained_variance_target"]) + 1
    )
    components = full_pca.components_[:component_count]
    explained_variance = full_pca.explained_variance_[:component_count]
    explained_variance_ratio = full_pca.explained_variance_ratio_[:component_count]

    scores = all_scaled @ components.T
    reconstruction = scores @ components
    residuals = all_scaled - reconstruction
    t2 = np.sum(scores**2 / explained_variance, axis=1)
    q = np.sum(residuals**2, axis=1)
    t2_contributions = all_scaled * ((scores / explained_variance) @ components)
    q_contributions = residuals**2

    quantile = float(settings["threshold_quantile"])
    t2_limit = float(np.quantile(t2[reference_mask], quantile, method="higher"))
    q_limit = float(np.quantile(q[reference_mask], quantile, method="higher"))
    alerts = entities.loc[:, ["entity_id", "event_timestamp", "split"]].copy()
    alerts["t2_statistic"] = t2
    alerts["t2_limit"] = t2_limit
    alerts["t2_alert"] = t2 > t2_limit
    alerts["q_statistic"] = q
    alerts["q_limit"] = q_limit
    alerts["q_alert"] = q > q_limit
    alerts["any_multivariate_alert"] = alerts["t2_alert"] | alerts["q_alert"]
    alerts["model_version"] = settings["model_version"]
    alerts["threshold_version"] = settings["threshold_version"]

    top_k = min(int(settings["pca_contribution_top_k"]), len(sensor_ids))
    contribution_frames = [
        _top_contributions(
            t2_contributions,
            entities,
            sensor_ids,
            "T2",
            top_k,
            settings["model_version"],
        ),
        _top_contributions(
            q_contributions,
            entities,
            sensor_ids,
            "Q_SPE",
            top_k,
            settings["model_version"],
        ),
    ]
    contributions = pd.concat(contribution_frames, ignore_index=True)
    model = pd.DataFrame(
        [
            {
                "model_version": settings["model_version"],
                "threshold_version": settings["threshold_version"],
                "fit_split": "reference",
                "reference_entity_count": int(reference_mask.sum()),
                "feature_count": len(sensor_ids),
                "component_count": component_count,
                "explained_variance_target": float(
                    settings["explained_variance_target"]
                ),
                "explained_variance_retained": float(explained_variance_ratio.sum()),
                "imputation_method": "reference_median",
                "scaling_method": "reference_standard_scaler",
                "threshold_method": "reference_empirical_quantile_higher",
                "threshold_quantile": quantile,
                "t2_limit": t2_limit,
                "q_limit": q_limit,
                "contribution_top_k": top_k,
            }
        ]
    )
    artifacts = PCAArtifacts(
        sensor_ids=tuple(sensor_ids),
        imputation_values=imputer.statistics_.copy(),
        scaling_means=scaler.mean_.copy(),
        scaling_scales=scaler.scale_.copy(),
        components=components.copy(),
        explained_variance=explained_variance.copy(),
        explained_variance_ratio=explained_variance_ratio.copy(),
        t2_limit=t2_limit,
        q_limit=q_limit,
    )
    t2_reconciliation_error = np.abs(t2_contributions.sum(axis=1) - t2)
    q_reconciliation_error = np.abs(q_contributions.sum(axis=1) - q)
    diagnostics = {
        "maximum_t2_reconciliation_error": float(
            np.max(t2_reconciliation_error)
        ),
        "maximum_q_reconciliation_error": float(
            np.max(q_reconciliation_error)
        ),
        "maximum_t2_relative_reconciliation_error": float(
            np.max(t2_reconciliation_error / np.maximum(np.abs(t2), 1.0))
        ),
        "maximum_q_relative_reconciliation_error": float(
            np.max(q_reconciliation_error / np.maximum(np.abs(q), 1.0))
        ),
    }
    return alerts, contributions, model, artifacts, diagnostics
