# YieldGuard: Semiconductor Process Excursion Monitoring and Failure-Driver Triage

YieldGuard is a reproducible semiconductor manufacturing analytics system built on the UCI SECOM dataset. It audits high-dimensional anonymized measurements, establishes leakage-safe chronological evaluation, and will ultimately combine statistical process monitoring, multivariate monitoring, failure-driver association, risk ranking, and a capacity-constrained engineering-review queue.

The project supports yield, process integration, quality, and manufacturing analytics teams deciding which measurements can be trusted and which later production entities merit investigation. It distinguishes statistical alerts and associations from causal root-cause conclusions.

## Current verified scope

Phase 1 verified 1,567 production entities, 590 anonymized measurements, 104 failures, 440 quality-eligible measurements, and a retained final chronological block. Phase 2 freezes 12 label-blind monitoring measurements and builds traceable reference-fitted I-MR/EWMA signals over a reconciled wide/long DuckDB architecture. See `docs/PHASE1_REPORT.md` and `docs/PHASE2_REPORT.md`; later-phase results are intentionally not claimed yet.

## Setup and Phase 1 reproduction

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
yieldguard acquire
yieldguard build-phase1
yieldguard build-phase2
python -m pytest
python -m ruff check .
```

Raw source files, generated CSVs, and the local DuckDB database are intentionally excluded from Git. See `data/README.md` for provenance and acquisition details.

## Repository navigation

- `config/project.yaml` — thresholds, source configuration, seeds, and candidate allocations
- `src/yieldguard/` — reusable acquisition, ingestion, split, audit, and persistence logic
- `sql/` — documented SQL contracts and later transformations/marts
- `tests/` — deterministic unit and integration checks
- `docs/PROJECT_PLAN.md` — approved source-of-truth specification
- `docs/REQUIREMENTS_ROADMAP.md` — requirement-to-phase execution map
- `docs/PROJECT_STATUS.md` and `docs/DECISIONS.md` — resumable project memory
- `docs/univariate_monitoring.md` — frozen selection rule, formulas, alert volume, and limitations
- `docs/phase2_architecture.md` — SQL grains, keys, marts, and reconciliation controls

## Dataset attribution

McCann, M. & Johnston, A. (2008). *SECOM* [Dataset]. UCI Machine Learning Repository. <https://doi.org/10.24432/C54305>. Licensed under CC BY 4.0.

Each source row is called a **production entity** because the public documentation does not establish a more specific physical unit. Measurements remain anonymous; YieldGuard does not invent sensor meanings, mechanisms, specification limits, production savings, or causal root causes.
