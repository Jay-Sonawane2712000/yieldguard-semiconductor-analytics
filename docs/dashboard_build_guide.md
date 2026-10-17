# Power BI dashboard build guide

## Refresh and model

1. Run `yieldguard build-phase5` from the repository root.
2. In Power BI Desktop, Get Data > Folder and select `data/processed/phase5/powerbi`.
3. Load each CSV as a separate table, preserving the filename (without `.csv`) as its table name.
4. Set timestamps to Date/Time, indicators to True/False, counts/ranks to Whole Number, and estimates/limits/probabilities to Decimal Number.
5. Relate `mart_dashboard_monitoring_timeline[entity_id]` one-to-many to alert contributions and one-to-one to the review queue. Relate sensor quality one-to-many to contributions and failure drivers on `sensor_id`. Keep model, calibration, and budget tables disconnected because slicers use their explicit model/configuration/period columns.
6. Import `dashboard/yieldguard_theme.json`, create the measures in `dashboard/measures.dax`, build exactly the pages below, then refresh and run the reconciliation checklist.

Use single-direction filtering from timeline to contributions/queue and from sensor quality to sensor-grain facts. Do not create implicit many-to-many relationships. Hide raw keys and technical version fields from report view but retain them in the model.

## Page 1 — Data Trust

- KPI cards: Entity Count, Failure Count, Pass Count, Usable Measurements, Excluded Measurements, Monitoring Measurements.
- Date range card: minimum and maximum timestamp from `mart_dashboard_data_trust`.
- Stacked bar: pass/failure by split from the split summary.
- Split table: split, entity count, failure count/rate, timestamp and chronological boundaries.
- Sensor-quality table: sensor, missingness, temporal coverage, status, exclusion reason, monitoring status.
- Exclusion-reason bar chart with blank reason displayed as `Eligible / no exclusion`.
- Persistent limitations callout: anonymous measurements, sparse failures, retrospective analysis, no causal or specification claim.

Filters: split, quality status, exclusion reason, monitoring selection. Selecting a split filters split visuals but must not rewrite global dataset cards. Selecting a sensor-quality row cross-filters only sensor-level visuals. Empty state: “No measurements match the current quality filters.”

## Page 2 — Excursion Monitoring

- Slicers: split, timestamp range, entity ID, sensor ID, method/statistic type, failure outcome (clearly labeled retrospective).
- Timeline: entity chronological order on x; I/MR/EWMA alert count, T-squared statistic/limit, and Q/SPE statistic/limit in separate aligned visuals.
- Alert cards: univariate, T-squared, Q/SPE, and overlap entity counts.
- Entity drill-through table: all alert flags, failure outcome, and top contributions.
- Contribution bar: top ten absolute contributions by statistic type for the selected entity.
- Alert/failure matrix: alerts and failures remain separate fields; never label an alert as a failure.

Clicking a timeline point filters entity detail and contributions. Sensor selection filters univariate history/contributions only. Empty state: “No excursions match these filters; absence of an alert is not proof of process conformity.”

## Page 3 — Failure-Driver Triage

- Association table: rank, sensor, Cliff’s delta and interval, raw/BH/BY values, survival flags, data-quality context, PCA contribution count/share, model importance.
- Model comparison: PR-AUC, ROC-AUC, Brier score, ECE, intervals, and baselines.
- Calibration panel: mean prediction versus observed rate by bin; label the monitoring baseline as non-probabilistic.
- Budget table/curve: reviewed, detected, missed, precision, recall, alert rate, and intervals across scenarios.
- Frozen queue: rank, probability, headline flag, alert flags, missingness warning, reason codes, retrospective outcome.

Default filters: `evaluation_period = final_test`; headline callouts additionally use `model = hist_gradient_boosting`, `configuration_id = hgb-01`, `policy_scenario = top_10_percent`. Selecting a sensor filters associations; selecting a budget filters policy visuals, not the frozen queue. Empty state: “No candidates match the evidence filters; do not loosen multiplicity controls to create findings.”

## Reconciliation checklist

- Data Trust: 1,567 entities, 104 failures, 1,463 passes, 590 measurements, 440 usable, 150 excluded, 12 monitored.
- Split entity totals sum to 1,567 and failure totals sum to 104.
- Timeline has 1,567 distinct entity IDs.
- Failure-driver table has 440 rows; BH/BY survivor counts are 20/9.
- Queue has 313 distinct final entities; exactly 32 headline reviews and 17 retrospective failures.
- Headline policy: 32 reviewed, 2 detected, 15 missed, precision 0.0625, recall 0.117647.
- Model PR-AUC: frozen HGB 0.069968; monitoring baseline 0.110591; prevalence baseline 0.054313.

Run this checklist after every refresh. Store a dated screenshot of each principal page only after all values match. Phase 5 automation verified SQL/Python/CSV totals; Power BI visual totals and screenshots remain unverified until Desktop is available.
