# Engineering decision memo: frozen review policy

**To:** Yield, process-integration, quality, and manufacturing analytics stakeholders  
**Decision:** Retain the frozen top-10% review scenario as an auditable retrospective benchmark, but do not recommend production deployment from this dataset alone.

## Why this decision is supportable

YieldGuard was designed around a real decision constraint: investigation capacity is limited, while process measurements are high-dimensional and failures are sparse. The system therefore separates monitoring from outcome modeling and translates each ranking into a transparent workload scenario. Data trust, model selection, and final evaluation were gated chronologically. The final block was not used to choose the champion or the budget.

The frozen `hgb-01` model achieved final PR-AUC 0.069968 versus a 0.054313 prevalence baseline, but it did not beat the fixed monitoring baseline at 0.110591. Its ROC-AUC was 0.5982 and its probability calibration was weak relative to prevalence (Brier 0.0823; ECE 0.1390). These figures support only modest retrospective enrichment. They do not justify replacing established monitoring with the predictive model.

At the precommitted top-10% policy, 32 of 313 final entities enter review. Two of 17 failures are detected, 15 are missed, and 30 reviewed entities are nonfailures. Precision is 0.0625 and recall is 0.117647. Approximate intervals are wide: precision 0–0.1563 and recall 0–0.2941. The fixed monitoring baseline produces the same headline counts in this block, while prevalence detects one failure. The practical conclusion is that the model can organize evidence, but its incremental value over monitoring is not established.

## Recommended use

Use the queue as a reproducible investigation aid. Each row preserves rank, I-MR/EWMA and T-squared/Q flags, leading mathematical contributions, missingness warnings, retrospective outcome, and reason codes. Engineers can compare monitoring and outcome-based evidence without conflating them. On the Failure-Driver Triage page, association effects and intervals should guide questions about anonymous measurements; BY-supported findings deserve greater priority than raw p-values, but none should be called a root cause.

Keep the top-10% setting as a benchmark because it was frozen before final evaluation and creates a clear, repeatable 32-entity workload for this dataset period. Do not describe it as an operational staffing recommendation. Real capacity, review time, false-positive cost, miss cost, and production cadence are not available in SECOM.

## Conditions before operational use

Before any deployment decision, map anonymous measurements to governed process definitions; confirm the physical production entity and timestamp semantics; run prospective validation on newer data; quantify review capacity and asymmetric costs; assess latency, drift, missingness, and alert stability; define disposition authority and audit retention; and compare against the actual incumbent workflow. Recalibration or threshold changes must occur in a new development cycle with another untouched holdout.

## Claims explicitly rejected

This work does not establish causal root causes, equipment mechanisms, specification violations, production savings, reduced scrap, deployable alarm thresholds, or autonomous disposition. No simulation is included because the source lacks defensible economic and operating parameters. The evidence supports an interview-ready analytical prototype and a disciplined evaluation method—not a production-control claim.
