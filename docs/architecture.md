# YieldGuard architecture

```text
Acquire + validate
       |
Entity/sensor warehouse ---- data-quality audit
       |                         |
       +---- chronological split + sensor eligibility
       |                         |
Reference-only SPC -------- reference-only PCA
       |                         |
       +------ alert facts + contributions
                         |
Development associations + bounded model calibration
                         |
Frozen model + frozen 10% policy
                         |
One-time final evaluation + review queue
                         |
Dashboard marts -- CSV/Power BI contract -- HTML report
```

DuckDB is the analytical system of record. Pandas/scikit-learn/SciPy perform deterministic computation; SQL defines stable dashboard contracts; Power BI is restricted to presentation and measures. The architecture separates fitting, selection, development inference, and final evaluation to make leakage visible and testable.

Controls include unique keys, source/row reconciliation, frozen random seed, reference-only limits, bounded candidate families, explicit baseline comparisons, precommitted final policy, and a failing Phase 5 reconciliation build.
