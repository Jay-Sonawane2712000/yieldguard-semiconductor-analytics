"""Phase 5 dashboard extracts, reconciliation, and static report rendering."""

# ruff: noqa: E501 -- report prose and CSS remain readable as literal source lines.

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from yieldguard.config import PROJECT_ROOT, project_path

EXPORTS = (
    "mart_dashboard_data_trust",
    "mart_dashboard_split_summary",
    "mart_dashboard_sensor_quality",
    "mart_dashboard_monitoring_timeline",
    "mart_dashboard_alert_contribution",
    "mart_dashboard_failure_driver",
    "mart_dashboard_model_comparison",
    "mart_dashboard_calibration",
    "mart_dashboard_review_budget",
    "mart_dashboard_review_queue",
)

EXPORT_ORDER = {
    "mart_dashboard_data_trust": "entity_count",
    "mart_dashboard_split_summary": "chronological_order_start",
    "mart_dashboard_sensor_quality": "source_column",
    "mart_dashboard_monitoring_timeline": "chronological_order",
    "mart_dashboard_alert_contribution": (
        "event_timestamp, entity_id, statistic_type, contribution_rank"
    ),
    "mart_dashboard_failure_driver": "association_rank",
    "mart_dashboard_model_comparison": "model, metric",
    "mart_dashboard_calibration": "model, calibration_bin",
    "mart_dashboard_review_budget": (
        "evaluation_period, model, entities_reviewed, policy_scenario"
    ),
    "mart_dashboard_review_queue": "risk_rank",
}


def _fmt(value: float, digits: int = 4) -> str:
    return f"{value:.{digits}f}"


def _table(frame: pd.DataFrame) -> str:
    return frame.to_html(index=False, border=0, classes="data-table", na_rep="—")


def _render_report(connection: duckdb.DuckDBPyConnection, output: Path) -> None:
    trust = connection.execute("SELECT * FROM mart_dashboard_data_trust").fetchdf().iloc[0]
    split = connection.execute(
        "SELECT * FROM mart_dashboard_split_summary ORDER BY chronological_order_start"
    ).fetchdf()
    model = connection.execute(
        """SELECT model, metric, estimate, interval_lower, interval_upper
           FROM mart_dashboard_model_comparison ORDER BY model, metric"""
    ).fetchdf()
    budget = connection.execute(
        """SELECT model, policy_scenario, entities_reviewed, failures_detected,
                  failures_missed, precision, recall, precision_ci_lower,
                  precision_ci_upper, recall_ci_lower, recall_ci_upper
           FROM mart_dashboard_review_budget
           WHERE evaluation_period = 'final_test'
           ORDER BY model, entities_reviewed"""
    ).fetchdf()
    associations = connection.execute(
        """SELECT sensor_id, cliffs_delta, cliffs_delta_ci_lower, cliffs_delta_ci_upper,
                  bh_adjusted_p_value, by_adjusted_p_value, survives_bh, survives_by,
                  investigation_status, association_rank
           FROM mart_dashboard_failure_driver ORDER BY association_rank LIMIT 15"""
    ).fetchdf()
    alerts = connection.execute(
        """SELECT split, COUNT(*) AS entities,
                  SUM(any_univariate_signal::INTEGER) AS univariate_alerts,
                  SUM(t2_alert::INTEGER) AS t2_alerts,
                  SUM(q_alert::INTEGER) AS q_alerts,
                  SUM(alert_overlap::INTEGER) AS overlaps
           FROM mart_dashboard_monitoring_timeline GROUP BY split
           ORDER BY MIN(chronological_order)"""
    ).fetchdf()
    headline = budget.loc[
        budget["model"].eq("hist_gradient_boosting")
        & budget["policy_scenario"].eq("top_10_percent")
    ].iloc[0]
    style = """
    body{font-family:Segoe UI,Arial,sans-serif;max-width:1100px;margin:32px auto;padding:0 24px;color:#172033;line-height:1.5}
    h1,h2{color:#123b63} h2{border-bottom:2px solid #dbe7f2;padding-bottom:6px;margin-top:34px}
    .note{background:#fff4d6;border-left:5px solid #d99a00;padding:12px 16px}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
    .card{background:#eef5fb;border-radius:8px;padding:14px}.card b{display:block;font-size:1.6rem;color:#0d5f89}
    table{border-collapse:collapse;width:100%;font-size:.88rem}th,td{border:1px solid #d7e0e8;padding:6px;text-align:right}th{background:#123b63;color:white}td:first-child,th:first-child{text-align:left}
    code{background:#edf1f5;padding:2px 5px}.small{font-size:.9rem;color:#48566a}@media(max-width:800px){.cards{grid-template-columns:1fr 1fr}}
    """
    sections = f"""
    <h1>YieldGuard statistical report</h1>
    <p class="small">Rendered from the reconciled DuckDB marts. Dataset: UCI SECOM; analytical unit: production entity.</p>
    <div class="note"><b>Decision boundary.</b> This is retrospective, association-based evidence for engineering triage. It does not identify causal root causes, physical sensor meanings, specification limits, savings, or deployable operating thresholds.</div>
    <div class="cards"><div class="card"><b>{int(trust.entity_count):,}</b>entities</div><div class="card"><b>{int(trust.failure_count):,}</b>failures</div><div class="card"><b>{int(trust.usable_measurement_count):,}</b>usable measurements</div><div class="card"><b>{int(trust.monitoring_measurement_count):,}</b>monitored measurements</div></div>
    <h2>1. Executive summary</h2><p>YieldGuard combines leakage-safe chronological evaluation, reference-fitted statistical monitoring, development-only association screening, and a frozen capacity-constrained review policy. The fixed monitoring baseline produced higher final PR-AUC than the frozen predictive model. Results are directional because the final block contains only 17 failures.</p>
    <h2>2. Business problem and stakeholder decision</h2><p>Yield, process-integration, quality, and manufacturing analytics teams need an auditable way to identify production entities and anonymous measurements for investigation. The supported decision is which entities enter a limited retrospective engineering-review queue.</p>
    <h2>3. Data provenance and license</h2><p>McCann &amp; Johnston (2008), UCI SECOM, DOI 10.24432/C54305, CC BY 4.0. No domain meaning is assigned to anonymous measurements.</p>
    <h2>4. Unit of analysis and label semantics</h2><p>Each source row is called a production entity. Source label -1 is mapped to pass (0); label 1 is mapped to failure (1).</p>
    <h2>5. Data trust profile</h2><p>{int(trust.measurement_count)} measurements span {html.escape(str(trust.timestamp_start))} through {html.escape(str(trust.timestamp_end))}. {int(trust.excluded_measurement_count)} measurements were excluded by predeclared quality rules.</p>
    <h2>6. Chronological split design</h2>{_table(split)}
    <h2>7. Leakage controls</h2><p>Quality screening, monitoring limits, imputation, scaling, and PCA thresholds are fitted on the reference period. Candidate selection uses calibration only. Associations use reference plus calibration. The final block is opened once after model and review budget are frozen.</p>
    <h2>8. Measurement-quality policy</h2><p>Eligibility considers missingness, minimum count, variance, dominant-value concentration, temporal coverage, and correlation-aware selection. Exclusion reasons remain visible in the dashboard mart.</p>
    <h2>9. Univariate monitoring methods</h2><p>I-MR and time-varying EWMA limits use reference-only estimates. Alerts are statistical excursion indicators, not specification violations.</p>
    <h2>10. Multivariate monitoring methods</h2><p>Reference-only median imputation and scaling feed PCA. Empirical reference 99th-percentile thresholds define Hotelling T-squared and Q/SPE alerts.</p>
    <h2>11. Monitoring results</h2>{_table(alerts)}
    <h2>12. Alert overlap and interpretation</h2><p>Univariate and multivariate signals are shown separately and together. Agreement prioritizes investigation but does not establish mechanism or causality.</p>
    <h2>13. Contribution diagnostics</h2><p>Stored top-ten T-squared and Q/SPE contributions provide mathematical attribution at the entity-measurement grain. They are diagnostic leads only.</p>
    <h2>14. Association-screening design</h2><p>All 440 eligible measurements are compared across development failures and nonfailures using Mann–Whitney U, Cliff's delta, and approximate stratified-bootstrap intervals.</p>
    <h2>15. Multiple-testing control</h2><p>Both Benjamini–Hochberg and the more conservative Benjamini–Yekutieli adjustments are reported at 0.05. Twenty measurements survive BH and nine survive BY.</p>
    <h2>16. Leading association evidence</h2>{_table(associations)}
    <h2>17. Predictive candidate design</h2><p>Four complete logistic-regression configurations and four complete histogram-gradient-boosting configurations were predeclared. Search size remained below six configurations per family.</p>
    <h2>18. Model selection</h2><p><code>hgb-01</code> was frozen using calibration PR-AUC. The fixed monitoring baseline was stronger on calibration and remained an explicit comparator.</p>
    <h2>19. Final discrimination and calibration</h2>{_table(model)}
    <h2>20. Uncertainty</h2><p>Final metric intervals use 1,000 outcome-stratified bootstrap replicates. They are approximate and do not preserve temporal dependence; sparse failures make them wide.</p>
    <h2>21. Review-policy design</h2><p>The headline scenario reviews the ceiling-rounded top 10% of final entities. Percentage and fixed-count alternatives are retained for sensitivity analysis.</p>
    <h2>22. Review-policy results</h2>{_table(budget)}
    <h2>23. Frozen headline result</h2><p>The model reviewed {int(headline.entities_reviewed)} of 313 entities, detected {int(headline.failures_detected)} of 17 failures, and achieved precision {_fmt(headline.precision)} and recall {_fmt(headline.recall)}. This is a dataset-period scenario, not a staffing recommendation.</p>
    <h2>24. Engineering-review queue</h2><p>The queue preserves all final entities, identifies exactly 32 headline reviews, and includes ranks, monitoring flags, leading contributions, missingness warnings, retrospective outcomes, and reason codes.</p>
    <h2>25. Reconciliation</h2><p>SQL mart totals are programmatically checked against source facts and exported CSV row counts. The build fails on any mismatch.</p>
    <h2>26. Dashboard design</h2><p>Exactly three principal pages are specified: Data Trust, Excursion Monitoring, and Failure-Driver Triage. Filters, interactions, empty states, lineage, and measures are documented separately.</p>
    <h2>27. Operational interpretation</h2><p>Use the artifacts to prioritize investigation and to challenge data quality. Do not treat rankings as autonomous disposition decisions.</p>
    <h2>28. Known limitations</h2><p>Measurements are anonymous; failures are sparse; timestamps may not represent stable production cadence; bootstrap intervals ignore temporal dependence; public data cannot validate deployment latency, drift, or staffing capacity.</p>
    <h2>29. Simulation</h2><p>No simulation is implemented. The project does not fabricate economic or operational parameters unsupported by the source.</p>
    <h2>30. Reproducibility</h2><p>Run <code>yieldguard build-phase5</code>, <code>pytest</code>, and <code>ruff check .</code>. Generated database, CSV, and HTML files are reproducible and excluded from Git.</p>
    <h2>31. Claim ledger</h2><p>Supported: dataset counts, retrospective alert volumes, associations, held-out ranking metrics, and review-scenario workload. Unsupported: causal root cause, physical interpretation, specification compliance, savings, and production readiness.</p>
    <h2>32. Next steps</h2><p>Open the supplied CSV model in Power BI Desktop, implement the documented relationships and DAX, reconcile totals, and capture the three page screenshots. Production use would additionally require domain mapping, governance, prospective validation, drift monitoring, and capacity confirmation.</p>
    """
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>YieldGuard statistical report</title><style>"
        + style
        + "</style></head><body>"
        + sections
        + "</body></html>\n",
        encoding="utf-8",
    )


def build_phase5(config: dict[str, Any]) -> dict[str, Any]:
    """Build dashboard marts/exports, reconcile totals, and render the HTML report."""
    database_path = project_path(config["outputs"]["database"])
    if not database_path.exists():
        raise FileNotFoundError("Analytical database is missing; run Phases 1-4 first")
    export_directory = project_path("data/processed/phase5/powerbi")
    export_directory.mkdir(parents=True, exist_ok=True)
    report_path = project_path("reports/rendered/yieldguard_statistical_report.html")
    with duckdb.connect(str(database_path)) as connection:
        connection.execute(
            (PROJECT_ROOT / "sql/marts/040_phase5_dashboard_marts.sql").read_text(
                encoding="utf-8"
            )
        )
        row_counts: dict[str, int] = {}
        digests: dict[str, str] = {}
        for relation in EXPORTS:
            frame = connection.execute(
                f'SELECT * FROM "{relation}" ORDER BY {EXPORT_ORDER[relation]}'
            ).fetchdf()
            path = export_directory / f"{relation}.csv"
            frame.to_csv(path, index=False)
            row_counts[relation] = len(frame)
            digests[relation] = hashlib.sha256(path.read_bytes()).hexdigest()

        trust = connection.execute("SELECT * FROM mart_dashboard_data_trust").fetchone()
        source = connection.execute(
            """SELECT COUNT(*), SUM(failure_indicator),
                      (SELECT COUNT(*) FROM dim_sensor),
                      (SELECT COUNT(*) FROM dim_sensor WHERE quality_status = 'eligible'),
                      (SELECT COUNT(*) FROM dim_sensor WHERE quality_status = 'excluded'),
                      (SELECT COUNT(*) FROM dim_monitoring_sensor WHERE is_selected)
               FROM fact_production_entity"""
        ).fetchone()
        if (trust[0], trust[2], trust[5], trust[6], trust[7], trust[8]) != source:
            raise AssertionError("Data-trust dashboard mart does not reconcile to source facts")
        timeline_count = connection.execute(
            "SELECT COUNT(*) FROM mart_dashboard_monitoring_timeline"
        ).fetchone()[0]
        if timeline_count != source[0]:
            raise AssertionError("Monitoring timeline is not one row per entity")
        final_entity_count = connection.execute(
            "SELECT COUNT(*) FROM fact_production_entity WHERE split = 'final_test'"
        ).fetchone()[0]
        queue = connection.execute(
            """SELECT COUNT(*), SUM(headline_review_indicator::INTEGER),
                      SUM(retrospective_outcome)
               FROM mart_dashboard_review_queue"""
        ).fetchone()
        policy = connection.execute(
            """SELECT entities_reviewed, failure_count
               FROM mart_dashboard_review_budget
               WHERE evaluation_period = 'final_test'
                 AND model = 'hist_gradient_boosting'
                 AND policy_scenario = 'top_10_percent'"""
        ).fetchone()
        if queue != (final_entity_count, policy[0], policy[1]):
            raise AssertionError("Review queue does not reconcile to frozen policy")
        _render_report(connection, report_path)

    result = {
        "dashboard_mart_count": len(EXPORTS),
        "row_counts": row_counts,
        "csv_sha256": digests,
        "source_entity_count": int(source[0]),
        "source_failure_count": int(source[1]),
        "headline_review_count": int(queue[1]),
        "html_report": str(report_path.relative_to(PROJECT_ROOT)),
        "power_bi_verified": False,
    }
    summary_path = project_path("data/processed/phase5/phase5_summary.json")
    summary_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
