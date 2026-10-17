# Data lineage and refresh

```text
UCI SECOM archive
  -> validated raw measurements + labels + timestamps
  -> fact_production_entity / fact_sensor_measurement / dim_sensor
  -> reference-fitted I-MR/EWMA + PCA T²/Q facts
  -> development associations + calibration candidate evidence
  -> frozen final metrics, policy scenarios, and review queue
  -> mart_dashboard_* views
  -> deterministic CSV extracts
  -> Power BI three-page semantic model
  -> HTML statistical report
```

`yieldguard acquire` verifies and lands the public source. Phase commands are intentionally separate leakage gates. `yieldguard build-phase5` does not refit or rescore anything: it creates presentation views, exports them, reconciles them to frozen facts, and renders HTML. Refreshes are full and deterministic. Raw data, DuckDB, extracts, and rendered reports are rebuildable local artifacts excluded from Git.

The source-of-truth transformations are versioned SQL/Python. Power BI is a presentation layer and must not contain hidden outcome transformations or alternative thresholds. Any Power Query operation beyond type assignment and file loading requires a documented change to this lineage.
