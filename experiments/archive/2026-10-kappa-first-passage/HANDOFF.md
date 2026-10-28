# Implementation handoff

1. Read README and prior tail-budget failures before coding. Do not launch the
   older experiment or inspect any reserved outcomes from another investigation.
2. Review `src/field_age.rs`, `src/fixed_area.rs`, `examples/excursions.rs` and
   `examples/sectors.rs`. Reuse accounting conventions, not unverified estimates.
   Proposed Rust runner: `examples/kappa_first_passage_sampler.rs`; instrument
   module only if shared use warrants it. Neither exists in this scaffold.
3. Prototype exact evolving depth maintenance. Reference recomputes a BFS from
   boundary cells; fast version must agree after every step, including holes,
   boundary reclassification and geometry-induced milestone jumps.
4. Write oracle/property fixtures for empty/one-cell territory, no return,
   multiple contour changes, band endpoints, deep-cap censoring and checkpoints.
   Verify B+I=S and segment/fragments sum to exactly the observed time budget.
5. Implement synthetic calibration and fail the hidden-memory negative control
   honestly. In particular, do not reuse the failed truncated-tail estimator.
6. Freeze a pilot manifest, profile a few runs, then assess feasibility only.
   No ant-outcome model selection disguised as instrument calibration.
7. Resolve the statistical choices left open in README, freeze confirmation
   manifest, model, folds, stopping schedule and synthetic power results. Publish
   a dated deviation if the current thresholds or budgets need revision.
8. Build timed/published runs in a fresh CARGO_TARGET_DIR, preserve exit status
   and binary sha256. CPU only: this new statistic is not GPU-ported. Background
   long jobs with logs under results/; finish mid-trajectory resume first.
9. Write results and notebook as each stage completes, including failures.
   Update notes and blog only with provenance-linked findings.

The only implemented command is `scripts/preflight.py`. There is intentionally
no launcher or placeholder that could be mistaken for a working sampler.
