# SECOM data acquisition

YieldGuard uses only the UCI SECOM dataset (dataset 179) as factual manufacturing data.

- Landing page: <https://archive.ics.uci.edu/dataset/179/secom>
- DOI: <https://doi.org/10.24432/C54305>
- License: CC BY 4.0
- Creators: Michael McCann and Adrian Johnston (2008)

Source files and rebuildable outputs are intentionally ignored by Git. After installing the project, run:

```powershell
yieldguard acquire
yieldguard build-phase1
```

`acquire` downloads the official UCI archive, validates its expected members, extracts them under `data/raw/`, and writes SHA-256 metadata. `build-phase1` validates the source, performs the Phase 1 audits, and builds the local DuckDB database and machine-readable artifacts under `data/processed/`.

Each row is described only as a **production entity**. The public metadata does not establish that a row is a wafer, die, lot, batch, tool run, chamber event, or process step.
