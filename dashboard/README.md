# Power BI delivery package

Phase 5 produces ten CSV extracts in `data/processed/phase5/powerbi/` with `yieldguard build-phase5`. Load the folder in Power BI Desktop, apply the relationships and measures in `docs/dashboard_build_guide.md`, and use `yieldguard_theme.json` as the report theme.

The intended artifact has exactly three principal pages: **Data Trust**, **Excursion Monitoring**, and **Failure-Driver Triage**. A `.pbix` is not checked into this repository because Power BI Desktop was unavailable to the automated Windows control surface during Phase 5. The repository therefore does not claim that a PBIX or Power BI screenshot was built or verified.
