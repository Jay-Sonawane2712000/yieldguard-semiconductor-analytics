# Phase 1 completion report

## Outcome

**Complete — stop/go gate passed.** Parsing is reproducible, labels and timestamps are understood, the preferred chronological holdout is feasible, 440 measurements remain eligible after reference-only trust rules, the untouched final directional block is retained, initial DuckDB tables reconcile, and focused tests pass. Phase 2 has not started.

## Startup audit

The supplied GitHub repository was verified as empty and cloned into the internships-projects workspace. It had an unborn `main` branch, configured `origin`, no commits, files, dependencies, lock files, entry points, tests, README, `.gitignore`, dataset, environment configuration, secrets, large untracked files, generated outputs, caches, or unrelated local changes. No applicable ancestor `AGENTS.md` existed. Git identity was configured. Python 3.13.5 was available; pandas, NumPy, DuckDB, PyYAML, and pytest existed in the base environment, while Ruff was installed in the new ignored `.venv`. Quarto and a DuckDB CLI were not found; neither is required to pass Phase 1.

## What was built and why it matters

- Persistent project memory, the verbatim approved plan, requirement roadmap, package configuration, ignore rules, and reproducibility commands.
- Idempotent official UCI archive acquisition with expected-member validation, safe extraction, file sizes, and SHA-256 checksums.
- Strict 590-column measurement parsing, strict label-row parsing, `-1` pass / `1` fail normalization, stable production-entity IDs, and deterministic chronological order.
- Tie-safe candidate split comparison and configured feasibility selection.
- Reference-only measurement trust profiling covering missingness, counts, distinctness, variance, dominant values, temporal coverage, extreme-value counts, and correlation redundancy evidence.
- Machine-readable exclusion reasons; no measurement is silently removed.
- Rebuildable DuckDB tables with unique indexes for production entities, wide measurements, and sensor metadata.
- Unit tests for parsing, invalid rows, naming, explicit exclusions, deterministic splitting, and tied timestamps, plus an end-to-end synthetic smoke test.

## Verified source and trust findings

- 1,567 production entities and 590 anonymized measurements.
- 1,463 passes and 104 failures (6.64% observed failure prevalence).
- 41,951 missing cells out of 924,530 measurement cells (4.54% overall); missingness is highly uneven by measurement.
- No all-null measurement across the full source; no duplicate measurement rows or duplicate complete label/timestamp/measurement rows.
- 440 eligible measurements and 150 excluded using reference-period evidence only.
- Excluded combinations: 122 constant; 8 excessive missingness only; 4 excessive missingness plus insufficient non-null count; 16 excessive missingness plus insufficient non-null count and insufficient temporal coverage.
- Atomic reason totals overlap by design: 122 constant, 28 excessive missingness, 20 insufficient non-null count, and 16 insufficient temporal coverage.
- Thresholds are configuration-controlled: maximum 40% reference missingness, minimum 100 reference non-null observations, 99.5% dominant-value near-constant threshold, variance below `1e-12` as a conservative near-zero flag, and coverage in at least 80% of ten chronological reference bins.

Detailed reproducible outputs are generated under ignored `data/processed/phase1/`: `phase1_summary.json`, `sensor_quality.csv`, `sensor_exclusion_log.csv`, `missingness_by_entity.csv`, `split_comparison.csv`, and `selected_split_counts.csv`.

## Evaluation design and uncertainty

The selected 60/20/20 chronological design has 940/314/313 entities and 76/11/17 failures in reference/calibration/final test. All configured boundaries were compared, and no timestamp tie crosses a split. See `evaluation_design.md` for exact ranges and alternatives.

The calibration and final periods meet the configured minimum of 10 failures, but 11 and 17 failures remain sparse. Downstream calibration and final estimates must therefore be described as directional and include uncertainty. Phase 1 accessed final outcomes only for the permitted failure count.

## Initial DuckDB reconciliation

| Table | Grain | Rows | Distinct key evidence |
|---|---|---:|---:|
| `fact_production_entity` | One row per `entity_id` | 1,567 | 1,567 distinct IDs |
| `measurements_wide` | One row per `entity_id` | 1,567 | 1,567 distinct IDs |
| `dim_sensor` | One row per `sensor_id` | 590 | 590 distinct IDs |
| `audit_split_candidate` | One row per configured allocation | 4 | Four candidates |

Database split totals exactly match Python outputs; the SQL tie-violation count is zero.

## Checks actually run

- `yieldguard acquire` — passed; official archive and all three expected members downloaded and checksummed.
- `yieldguard build-phase1` — passed; audits, CSV outputs, and DuckDB database built.
- `python -m pytest` — passed: 7 tests in 0.73 seconds after repairing pandas 3 read-only/all-null correlation handling.
- `python -m ruff check src tests` — passed with no issues.
- Read-only DuckDB reconciliation queries — passed for table presence, row counts, unique keys, quality counts, split counts/ranges, and zero boundary-tie violations.
- Secret-pattern scan of commit candidates — no matches; raw/generated paths and the virtual environment are ignored.

## Not verified or deferred

- Quarto HTML rendering, Power BI, monitoring, PCA, associations, models, review policies, and dashboard/report outputs belong to later phases and were not attempted.
- Raw-file reacquisition from a second independent network was not tested; deterministic checksums make future comparison possible.
- Physical measurement meanings and causal mechanisms are unavailable and must not be inferred.

## Material decisions and tradeoffs

- pandas is the primary dataframe library; DuckDB is the persisted analytical layer.
- The first feasible preconfigured allocation (60/20/20) was selected; no outcome-performance optimization occurred.
- Generated data and the rebuildable database are excluded from Git. Small committed documentation records provenance and findings; machine-readable evidence is recreated by the CLI.
- The overall data has no all-null measurement, but exclusions are deliberately based on the earlier reference period to prevent future structural information from changing selection eligibility.

## Interview explanation

Phase 1 demonstrates that a trustworthy analytical system starts with semantics, temporal boundaries, and measurement quality—not a classifier. The crucial design choice is to learn all later transformations from earlier data, preserve a final time block, and make every excluded anonymous measurement traceable to an explicit rule.

## Residual risks

The 104 total failures are imbalanced and later periods are sparse. Timestamps identify test points but not confirmed process chronology, excursion intervals, equipment, recipes, or specification limits. High correlation among anonymous measurements will require explicit redundancy control in Phase 2. These limitations do not invalidate the project, but they constrain downstream interpretation.
