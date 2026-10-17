# YieldGuard: Semiconductor Process Excursion Monitoring and Failure-Driver Triage

YieldGuard is a reproducible semiconductor manufacturing analytics system built on the UCI SECOM dataset. It audits high-dimensional anonymized measurements and combines leakage-safe chronological evaluation, statistical process monitoring, multivariate monitoring, failure-driver association, risk ranking, and a capacity-constrained engineering-review queue.

The project supports yield, process integration, quality, and manufacturing analytics teams deciding which measurements can be trusted and which later production entities merit investigation. It distinguishes statistical alerts and associations from causal root-cause conclusions.

## Measured outcome and current verified scope

The system verifies 1,567 production entities, 590 anonymized measurements, 104 failures, and 440 quality-eligible measurements. On the 313-entity final block, the frozen model's PR-AUC is 0.0700 versus 0.1106 for the fixed monitoring baseline and 0.0543 for prevalence. At the frozen 10% budget, 32 reviews detect 2 of 17 failures (precision 0.0625; recall 0.1176). These sparse-failure estimates are directional.

The dashboard/reporting layer is reproducible and reconciled. Power BI Desktop itself was unavailable to automation, so no PBIX or Power BI screenshot is claimed; the exact build handoff is documented.

## Architecture

```text
UCI SECOM -> validated DuckDB warehouse -> reference-only SPC/PCA
          -> development associations/models -> frozen final evaluation/queue
          -> dashboard marts -> Power BI extracts + HTML statistical report
```

See `docs/architecture.md` and `docs/data_lineage.md` for the complete controls and refresh path.

## Setup and full reproduction

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
yieldguard acquire
yieldguard build-phase1
yieldguard build-phase2
yieldguard build-phase3
yieldguard phase4-calibrate
yieldguard phase4-develop
# Commit the frozen budget decision before the next command.
yieldguard phase4-final
yieldguard build-phase5
python -m pytest
python -m ruff check .
```

Raw source files, generated CSVs/HTML, and the local DuckDB database are intentionally excluded from Git. See `data/README.md` for provenance and acquisition details.

## Repository navigation

- `config/project.yaml` — thresholds, sources, seeds, and candidate allocations
- `src/yieldguard/` — acquisition, ingestion, monitoring, evaluation, and reporting logic
- `sql/` — warehouse transformations and stable presentation marts
- `tests/` — deterministic unit and integration checks
- `docs/PROJECT_PLAN.md` — approved source-of-truth specification
- `docs/PROJECT_STATUS.md` and `docs/DECISIONS.md` — resumable project memory
- `docs/PHASE4_REPORT.md` — frozen final evaluation and queue evidence
- `docs/PHASE5_REPORT.md` — Phase 5 evidence and explicit Power BI blocker
- `docs/dashboard_build_guide.md` — exact three-page Power BI model, interactions, DAX, and reconciliation
- `docs/ENGINEERING_DECISION_MEMO.md` — decision framing using the frozen policy
- `reports/statistical_report.qmd` — report entry point; the CLI renders mandatory HTML
- `docs/interview_guide.md` — concise interview-ready project explanation

## Methods, uncertainty, and limitations

All preprocessing and limits are learned before their evaluation period. Candidate search is bounded, baselines are explicit, the final review policy was committed before final evaluation, and uncertainty is reported with sparse-event caveats. Measurements are anonymous; alerts are not failures or specification breaches; associations are not causal; the review scenario is not staffing advice; and no savings or production-readiness claim is made. See `docs/methods_and_limitations.md` and `docs/metric_dictionary.md`.

## Dataset attribution

McCann, M. & Johnston, A. (2008). *SECOM* [Dataset]. UCI Machine Learning Repository. <https://doi.org/10.24432/C54305>. Licensed under CC BY 4.0.

Each source row is called a **production entity** because the public documentation does not establish a more specific physical unit. Measurements remain anonymous; YieldGuard does not invent sensor meanings, mechanisms, specification limits, production savings, or causal root causes.
