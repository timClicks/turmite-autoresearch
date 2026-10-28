# Handoff (written 2026-10-16 ~20:55 +13:00)

1. Read `AGENTS.md`, `experiments/README.md`, this README, PLAN.md, SCHEMA.md, then `../2026-10-kappa-leadrun-fresh/{README,NOTEBOOK}.md`.
2. `git status` first. The workspace is dirty with other sessions' edits (`src/bin/probe.rs`, `src/gpu/mod.rs`, `Cargo.toml`, paper
   supplementary files). Do not revert them or build on them casually, and do not edit `src/probe.rs` for this work.
3. The parent's mutant run finished 20:53 and was scored (`../2026-10-kappa-leadrun-fresh/results/mutants_analysis.txt`, README "Part B results").
   M1 and M2 FAILED as registered (arm E mean d -0.062, because extending the lead also lowers ln A22 by 0.29; E-C -0.056 [-0.159, +0.040]); M3 HELD
   (shortening the lead: d -0.198 [-0.290, -0.110] at unchanged area). Area-matched pairs and the paired regression (b = +0.158) go the predicted way, but
   ln A22 is post-treatment and ln kappa tracks it with coefficient ~1. So the causal question is open, not closed: the loop instrument is still worth building,
   but read the parent's "Reading" paragraph first, and note that P3 here must be run at fixed area in the same sense (spline of ln A22) with that caveat.
4. Append an `intent` entry to NOTEBOOK.md. Implement the sampler, identity test and calibration (PLAN.md section 1) before any scientific run.
5. Freeze the **[choose]** items as `decision` entries, run the cohort once, analyse once. Variants go in new entries, never over the first.
6. Fill `notebook.ipynb` from committed `results/` only; execute it with the command in `experiments/README.md`.
7. At the end add a summary to `notes/open-questions-hypotheses.md` and link it from `notes/kappa-mechanisms-2026-10-15.md`.

State: P1 run and passed. Everything else is unwritten. Do not cite this folder as evidence for H-loop.

**Update 2026-10-16 ~22:55:** done. Instrument, tests, cohort + mutant runs and the single analysis exist; P2 FAILED, so H-loop is dead at this scale and `../2026-10-kappa-loop-surgery/` was not started. See README Results. Open: other loop shapes (period 6/8, mixed turns), what carries the lead effect.
