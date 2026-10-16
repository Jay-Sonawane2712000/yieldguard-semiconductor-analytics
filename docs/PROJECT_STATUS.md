# Project status

- **Current phase:** Phase 4 — associations, risk ranking, and policy (complete; awaiting approval)
- **Objective:** Produce development-only association evidence, a bounded frozen risk model, baseline comparisons, a pre-final frozen review budget, directional final evaluation, and an auditable engineering-review queue.
- **Completed:** Phases 1–3 plus eight-configuration calibration selection, development associations for 440 measurements, BH/BY correction, frozen `hgb-01`, calibration and uncertainty evidence, frozen 10% policy, final baseline comparisons, and a 313-row review queue with reason codes.
- **Remaining:** Wait for explicit user approval before beginning Phase 5 dashboard, report, memo, screenshot, or other decision-product work.
- **Latest verified checkpoint:** Final PR-AUC is 0.069968 for `hgb-01`, 0.110591 for fixed monitoring, and 0.054313 for prevalence. The frozen 10% queue reviews 32 of 313 entities and detects 2 of 17 failures; all estimates are directional with approximate intervals.
- **Checks passed:** `python -m pytest` (22 passed); `python -m ruff check .`; frozen final pipeline twice with identical SHA-256 `2E7D0D08...A9462B7`; candidate-count, temporal-boundary, association, multiplicity, bootstrap, policy, model/evaluation, and queue reconciliations.
- **Unresolved failures/blockers:** None.
- **Relevant commits:** `43781a5` — frozen final evaluation; `ccfaf2f` — frozen review budget before final evaluation; `baf36a2` — frozen predictive champion; `11306c3` — frozen candidate design.
- **Exact next action:** Report Phase 4 evidence and wait for explicit Phase 5 approval.
- **Push status:** `main` through the Phase 4 documentation checkpoint is pushed to `origin/main`.
