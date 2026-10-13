# Material decisions

## D-001 — Preserve an untouched final directional block when feasible

- **Status:** Approved by the project plan; Phase 1 evidence pending.
- **Decision:** Prefer chronological training/reference, calibration, and untouched final-test periods. Use the approved rolling-origin fallback if a single holdout is too sparse, while retaining a latest directional block whenever statistically feasible.
- **Why:** This protects the project from temporal leakage and makes later retrospective claims auditable.
- **Alternatives:** Random splitting is prohibited. Dropping the final block requires Phase 1 evidence and explicit user approval.
- **Consequences:** Phase 1 may inspect only final-period counts, timestamps, schema, and structural quality; outcome-conditioned final-period analysis remains prohibited.

## D-002 — Use pandas as the primary dataframe library

- **Status:** Agent decision within approved scope.
- **Decision:** Use pandas for Phase 1 ingestion and audits, with DuckDB for persisted analytical tables.
- **Why:** pandas is already available, directly supports the SECOM text format, and keeps the approved stack small.
- **Alternatives:** Polars was allowed but would add another dependency without a Phase 1 benefit.
- **Consequences:** Wide operations must be written carefully to avoid unnecessary copies; later performance can be measured before any reconsideration.

## D-003 — Select the tie-safe 60/20/20 chronological holdout

- **Status:** Phase 1 agent decision under the plan’s approved evaluation gate.
- **Decision:** Use 940 reference, 314 calibration, and 313 final-test production entities, with 76, 11, and 17 failures respectively.
- **Why:** It is the first preconfigured candidate meeting the explicit minimum of 10 calibration and 10 final failures. No timestamp tie crosses a boundary.
- **Alternatives:** Three later-final-block candidates were evaluated; their final periods contain 9, 9, and 3 failures. Rolling-origin was approved as a fallback but was unnecessary because the preferred holdout is feasible.
- **Consequences:** Retain the final test untouched for Phase 4 frozen retrospective evaluation. Estimates based on 11 calibration or 17 final failures must remain directional and include uncertainty.
