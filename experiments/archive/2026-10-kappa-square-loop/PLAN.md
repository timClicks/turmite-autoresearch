# Plan: loop instrument and analysis (draft; freeze before the confirmatory run)

Nothing below is implemented. Choices marked **[choose]** are open for the implementer. Record each as a `decision`
entry in `NOTEBOOK.md` before running anything that produces outcomes.

## 1. Instrument: `examples/kappa_square_loop_sampler.rs`

- Do NOT edit `src/probe.rs` or `src/bin/probe.rs`: the workspace has uncommitted changes from other sessions in `src/bin/probe.rs`,
  `src/gpu/mod.rs` and `Cargo.toml`. Copy the `probe_walker` stepping loop into the example with the same board (8192),
  `PatchedAnt::new(rule, seed, 2)`, octave windows, escape rule (|x| or |y| >= c-2) and boundary-step definition, and add counters.
  Use a repo-root `Walker` implementation only through its public API.
- Per window k in 20..=26 and per (rule, seed) accumulate: steps; boundary steps; loop steps (lead-colour / other, each split
  boundary / interior); loop entries (same split); histogram of lead-colour loop-run lengths in laps (1..8, >8).
- Per-step state: ring of the last 4 cell indices, the last 4 turn letters and the colours read at those steps. Turn letter = `rule[colour_before]`,
  recomputed from the colour; do not modify `AntWalker`.
- **Identity test (required, in `tests/`)**: the example's window fields (area, perimeter, new_cells, boundary_steps) equal `probe_walker`
  for >= 200 random (rule, seed, short horizon) `proptest` cases, and the loop counters equal an obviously-correct reference
  (store the whole path, count by definition) on the same cases. Commit `proptest-regressions/`.
- **Calibration** (AGENTS.md rule 5) before trusting it: (a) blank-board lead-k rules give exactly 4k opening loop steps (the P1 result);
  (b) negative controls: `PersistentWalk` q=0.5 and the rotor walker. For q=0.5 the loop-step fraction has an analytic value
  (four equal turns in a row, probability 1/8, then the path closes). **[choose]** derive it exactly, including overlap of consecutive
  loop steps, and compare with the measurement. Do not trust this sentence as the derivation.
- Determinism: results keyed by (rule, seed); rayon reduction in input order; identical bytes at 1 and 6 threads (test it).

## 2. Cohort and cost

- Cohort: the 300 fresh lead-stratified rules x seeds 601..608 (`../2026-10-kappa-leadrun-fresh/results/specs.txt`), as in the parent.
  Analyse the 176 stationary rules (`fresh_rules.csv`); also output the dropouts so selection can be checked.
- Cost is about that of the parent probe (2400 runs to 2^27 steps, ~22 min on 6 cores) plus counter overhead. Run in the background,
  log under `results/`, write a `.done` marker. Check `pgrep -af release/` first so timings are not distorted.
- Mutants (C3): the 3336 specs in the parent's `results/mutant_specs.txt`, after the parent's M1-M4 analysis is done.

## 3. Analysis (`scripts/analyse_loops.py`, polars, seed 20261016, 2000 bootstraps over rules)

Per rule: average over the 8 seeds, with the parent's keep rule (>= 6 core-band runs, stationary |g_k| < 0.05). Join to `fresh_rules.csv`
(lnk, lnA22, lead). Reuse the parent's `analyse.py` spline basis (`prefix_audit.basis`, knots at 10/25/50/75/90% quantiles of the census ln A22).

- **P2**: mean loop-step fraction per lead 1..6 (report each step, monotone or not); Spearman within ln A22 tertiles with bootstrap CI.
- **P3**: fit ln kappa ~ spline(ln A22) + b*min(lead,6) giving b0, then add g*loop_frac giving b1. Report b1/b0 with bootstrap CI over rules.
  Proposed pass: b1/b0 <= 0.5 with CI upper bound < 0.8 **[choose and freeze]**. Also use log loop fraction and a rank version
  to show the verdict is not a scale artefact.
- **C1**: the same with lead-colour and other loops separately and jointly.
- **C2**: the same with interior-only loop steps and with loop-entry rate.
- **P4**: ratio of per-step loop probability on boundary vs interior steps, per rule then pooled (median with CI over rules).
- **C3**: join `mutant_pairs.csv`; Spearman of d_loop with d.
- **Reliability**: between-seed sd of the loop fraction and an ICC across seeds (see `_lib/mixing.py`, `kcommon.icc_groups`). If ICC < 0.5 the
  mediation test is uninformative, not a null. Say which.

## 4. Threats to examine before announcing anything

- Opening-transient loops (first 4k steps) are irrelevant to windows 20-26. Confirm no loop mass comes from transients.
- High loop fraction might just mean the ant is on a periodic/highway-like structure. The stationary filter helps; also look at period-4 mass in non-lead-colour loops.
- Reverse causation: high boundary occupancy could itself create more fresh-cell loops. P3 cannot exclude it; the surgery experiment is the causal test.
- Concavity of the lead effect (saturating near 5): P2 should show the same shape if loops carry it. Compare shapes, not only signs.
- Dropouts (parent L5): lead >= 5 rules are the most selected. Repeat P3 on leads 1-4 only.
- Same-turn 4-loops are the only shape tested. Period-6/8 loops with mixed turns exist; do not dismiss "loops" if P2 is weak without checking them (NOTEBOOK question 20:59).
