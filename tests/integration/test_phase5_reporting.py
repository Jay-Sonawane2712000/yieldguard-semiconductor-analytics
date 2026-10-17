"""Integration coverage for Phase 5 marts, exports, and report."""

from __future__ import annotations

import duckdb

from yieldguard.config import load_config, project_path
from yieldguard.phase5 import EXPORTS, build_phase5


def test_phase5_build_reconciles_and_renders() -> None:
    result = build_phase5(load_config())
    repeated = build_phase5(load_config())
    assert result["dashboard_mart_count"] == 10
    assert result["source_entity_count"] == 1567
    assert result["source_failure_count"] == 104
    assert result["headline_review_count"] == 32
    assert result["power_bi_verified"] is False
    assert result["csv_sha256"] == repeated["csv_sha256"]
    report = project_path(result["html_report"])
    rendered = report.read_text(encoding="utf-8")
    assert "YieldGuard statistical report" in rendered
    assert "32. Next steps" in rendered
    with duckdb.connect(str(project_path("data/processed/yieldguard.duckdb"))) as connection:
        tables = {row[0] for row in connection.execute("SHOW TABLES").fetchall()}
    assert set(EXPORTS).issubset(tables)
