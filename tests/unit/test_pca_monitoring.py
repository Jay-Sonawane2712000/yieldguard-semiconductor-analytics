import numpy as np
import pandas as pd
import pytest

from yieldguard.pca_monitoring import fit_pca_monitor


def _config() -> dict:
    return {
        "pca": {
            "model_version": "pca-test-v1",
            "threshold_version": "threshold-test-v1",
            "explained_variance_target": 0.90,
            "threshold_quantile": 0.95,
            "pca_contribution_top_k": 10,
        }
    }


def _inputs() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    generator = np.random.default_rng(42)
    latent = generator.normal(size=(120, 3))
    loadings = generator.normal(size=(3, 12))
    values = latent @ loadings + generator.normal(scale=0.1, size=(120, 12))
    values[2, 3] = np.nan
    values[90, 8] = np.nan
    sensors = [f"measurement_{index:03d}" for index in range(12)]
    measurements = pd.DataFrame(values, columns=sensors)
    entities = pd.DataFrame(
        {
            "entity_id": [f"E{index:06d}" for index in range(1, 121)],
            "event_timestamp": pd.date_range("2024-01-01", periods=120, freq="h"),
            "split": ["reference"] * 80 + ["calibration"] * 20 + ["final_test"] * 20,
        }
    )
    return measurements, entities, sensors


def test_fit_is_unchanged_when_non_reference_measurements_change() -> None:
    measurements, entities, sensors = _inputs()
    first = fit_pca_monitor(measurements, entities, sensors, _config())
    changed = measurements.copy()
    changed.loc[entities["split"].ne("reference"), sensors] += 1_000_000
    second = fit_pca_monitor(changed, entities, sensors, _config())

    first_artifacts = first[3]
    second_artifacts = second[3]
    np.testing.assert_allclose(
        first_artifacts.imputation_values, second_artifacts.imputation_values
    )
    np.testing.assert_allclose(first_artifacts.scaling_means, second_artifacts.scaling_means)
    np.testing.assert_allclose(first_artifacts.scaling_scales, second_artifacts.scaling_scales)
    np.testing.assert_allclose(first_artifacts.components, second_artifacts.components)
    assert first_artifacts.t2_limit == pytest.approx(second_artifacts.t2_limit)
    assert first_artifacts.q_limit == pytest.approx(second_artifacts.q_limit)


def test_scores_contributions_and_model_metadata_reconcile() -> None:
    measurements, entities, sensors = _inputs()
    alerts, contributions, model, artifacts, diagnostics = fit_pca_monitor(
        measurements, entities, sensors, _config()
    )

    assert len(alerts) == 120
    assert alerts["entity_id"].is_unique
    assert (alerts[["t2_statistic", "q_statistic"]].to_numpy() >= -1e-12).all()
    assert len(contributions) == 120 * 2 * 10
    assert contributions["contribution_id"].is_unique
    counts = contributions.groupby(["entity_id", "statistic_type"]).size()
    assert counts.min() == counts.max() == 10
    assert set(contributions["statistic_type"]) == {"T2", "Q_SPE"}
    assert diagnostics["maximum_t2_reconciliation_error"] < 1e-10
    assert diagnostics["maximum_q_reconciliation_error"] < 1e-10
    assert diagnostics["maximum_t2_relative_reconciliation_error"] < 1e-12
    assert diagnostics["maximum_q_relative_reconciliation_error"] < 1e-12
    assert model.loc[0, "fit_split"] == "reference"
    assert model.loc[0, "reference_entity_count"] == 80
    assert model.loc[0, "explained_variance_retained"] >= 0.90
    assert artifacts.components.shape[1] == 12


def test_reference_empirical_limits_are_frozen_and_use_strict_alerts() -> None:
    measurements, entities, sensors = _inputs()
    alerts, _, _, artifacts, _ = fit_pca_monitor(
        measurements, entities, sensors, _config()
    )
    reference = alerts[alerts["split"].eq("reference")]

    assert artifacts.t2_limit == pytest.approx(
        np.quantile(reference["t2_statistic"], 0.95, method="higher")
    )
    assert artifacts.q_limit == pytest.approx(
        np.quantile(reference["q_statistic"], 0.95, method="higher")
    )
    assert (alerts["t2_alert"] == (alerts["t2_statistic"] > artifacts.t2_limit)).all()
    assert (alerts["q_alert"] == (alerts["q_statistic"] > artifacts.q_limit)).all()
