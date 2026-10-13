# Data provenance

## Source

- **Dataset:** SECOM, UCI Machine Learning Repository dataset 179
- **Creators:** Michael McCann and Adrian Johnston
- **Donated:** 2008-11-18
- **Landing page:** <https://archive.ics.uci.edu/dataset/179/secom>
- **DOI:** <https://doi.org/10.24432/C54305>
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Official archive:** <https://archive.ics.uci.edu/static/public/179/secom.zip>
- **Acquired:** 2026-10-13 04:29:25 UTC by `yieldguard acquire`

UCI describes examples as single production entities with anonymous measured features, pass/fail labels, and timestamps. It reports 1,567 examples and 591 features on the landing page; the downloaded measurement matrix contains 590 numeric measurement columns, while labels and timestamps are stored in the separate label file. YieldGuard reports these components separately rather than silently treating the label as a measurement.

## Verified checksums

| File | Bytes | SHA-256 |
|---|---:|---|
| `secom.zip` | 1,964,989 | `eea568baf3c2229096d7d294cf0b096b5502bd96d92c0b80a65b84714059be8e` |
| `secom.data` | 5,389,983 | `20f0e7ee434f7dcbae0eea9ffff009a2b57f42d6b0dc9a5bd4f00782c0a3374c` |
| `secom_labels.data` | 40,638 | `126884cf453705c9e61a903fe906f0665a3b45ce3639e621edc5c93c89627e03` |
| `secom.names` | 4,223 | `6d91b0b46cdee03064ee3e3112f937c1b3f7fcd9933575794ec07974e6f1ea59` |

Raw files and the generated `source_manifest.json` remain under ignored `data/raw/`. They are reproducibly reacquired rather than committed.

## Attribution and semantic limits

McCann, M. & Johnston, A. (2008). *SECOM* [Dataset]. UCI Machine Learning Repository. <https://doi.org/10.24432/C54305>.

Each row is called a **production entity**. The source does not establish a wafer, die, lot, batch, tool run, chamber event, process step, equipment identity, physical measurement meaning, failure mechanism, or engineering specification limit.
