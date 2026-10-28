# Plan: loop-surgery implementation notes (draft)

1. **Walker.** Add `LoopBreakAnt` to `src/walkers.rs` implementing `Walker` like `PatchedAnt`. State: last 4 positions (ring), last 3 turn letters, a counter t.
   Loop-closing test uses the definition in `../2026-10-kappa-square-loop/README.md` ("loop step"): pos would equal pos[t-4] after the move and the four turns agree.
   Because the walker's `step` sees only `(cell, heading)`, position tracking needs the walker to integrate its own (dx, dy) from the heading; verify against the probe's coordinates.
   Hash-based flip: `mix64(seed ^ t ^ salt) < q * 2^64` (see `mix64` in `walkers.rs`). No thread_rng.
2. **Tests (AGENTS.md rule 4).** (a) `q = 0` equals `AntWalker` step-for-step (proptest, random rules/seeds). (b) A reference implementation (store whole path, decide by definition)
   agrees with `LoopBreakAnt` for q in {0.25, 1}. (c) Blank-board lead-k rule with `q = 1` never completes a lap (positions never repeat at lag 4 in the first 4k steps).
3. **Noise-matching.** Measure each cohort rule's S-arm flip rate per step in a short pilot (2^22 steps, 2 seeds), then set N and M arm flip probabilities to that rate for the same rule.
   Pilot is for the rate only; do not look at kappa from the pilot. Record rates in `results/rates.csv`.
4. **Probe front-end.** Extend `src/bin/probe.rs` spec syntax with `lbreak:` etc. **Caution**: that file has uncommitted edits from other sessions; coordinate or put the new spec in a new binary
   (`src/bin/surgery_probe.rs`) instead of touching it.
5. **Analysis** `scripts/analyse_surgery.py`: reuse `kcommon.per_rule`/`rule_means` (keep rule: >= 6 core-band runs, stationary |g_k| < 0.05), per-rule d_S, d_N, d_M, bootstrap over rules (seed 20261016, 2000).
   Report retention by arm and lead, escaped runs by arm, and the realised flip rate per arm.
6. **Cost.** 48 rules x 8 seeds x 4 arms-with-q (S at three q, N, M, matched) ~ 48 x 8 x 6 = 2304 runs at 2^27 steps: about one parent probe run (~22 min on 6 cores) plus overhead. Check `pgrep -af release/` first.
7. **Reality check before any claim**: the lead effect itself is concave and survivor-biased (parent L5). With only 8 rules per lead, S4 is a rough sign check, not an effect size.
