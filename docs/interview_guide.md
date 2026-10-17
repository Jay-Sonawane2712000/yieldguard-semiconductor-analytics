# Interview guide

1. **Problem:** prioritize investigation under sparse failures and many anonymous measurements.
2. **Stakeholders:** yield, process integration, quality, manufacturing analytics.
3. **Decision:** which final-period entities enter a constrained engineering-review queue.
4. **Entity terminology:** “production entity” avoids inventing wafer/lot semantics.
5. **Provenance:** UCI SECOM, DOI and CC BY 4.0 recorded.
6. **Data trust:** 1,567 entities, 590 measurements, 104 failures; 440 eligible.
7. **Chronology:** 940 reference, 314 calibration, 313 final.
8. **Leakage control:** reference fitting, calibration selection, frozen final policy.
9. **Univariate SPC:** I-MR and time-varying EWMA, reference-only limits.
10. **Multivariate monitoring:** PCA T-squared and Q/SPE at empirical reference q99.
11. **Sensor selection:** label-blind quality/completeness/variation/correlation rule.
12. **Contributions:** mathematical diagnostic attribution, not physical cause.
13. **Associations:** Mann–Whitney U and Cliff’s delta on development only.
14. **Multiplicity:** 20 BH and 9 BY survivors; BY handles dependence conservatively.
15. **Uncertainty:** stratified bootstrap; sparse events and temporal caveat.
16. **Candidates:** four logistic and four HGB configurations, fully specified.
17. **Champion:** `hgb-01`, selected on calibration PR-AUC.
18. **Baselines:** monitoring beats the champion on final PR-AUC; reported openly.
19. **Policy:** frozen top 10%, ceiling-rounded to 32 final entities.
20. **Headline result:** 2/17 failures found; 6.25% precision; 11.76% recall.
21. **Dashboard:** three pages separate trust, excursions, and failure triage.
22. **Architecture:** DuckDB facts/marts, Python computation, SQL contracts, Power BI presentation.
23. **Limits/next step:** no causality or production claim; prospective governed validation is required.

## Two-minute explanation

“YieldGuard is a leakage-safe semiconductor analytics prototype built on UCI SECOM. I first audited 590 anonymous measurements and created chronological reference, calibration, and final blocks. Reference-only I-MR/EWMA and PCA T-squared/Q provide outcome-blind monitoring. Development-only rank effects with BH and BY control identify investigation candidates. I then compared bounded logistic and gradient-boosting candidates with prevalence and monitoring baselines, froze `hgb-01` and a top-10% review budget, and opened the final block once. The model modestly exceeded prevalence but did not beat monitoring; at 32 reviews it found 2 of 17 failures. The important engineering result is the auditable pipeline and honest decision framing: alerts, associations, and reason codes prioritize investigation without pretending to prove root cause.”
