# G1 follow-up: what is the 4-steps-per-cell builder of RLRLLL? (2026-10-14)

Hypotheses written 2026-10-14 before any new measurement. Data in hand: `data/g1_ribbon.csv`, `data/g1_stats.txt`
(window statistics only: after t = 1.2677e10 the ant makes 4.02 steps per new cell, x drifts -2190 -> -16384
at ~4.8e-5 cells/step, y extent of new cells per 1e6-step window grows 478 -> 9939).

**H-sweep.** The ant is a boustrophedon sweeper: its y(t) is a near-triangular wave between two moving turning
points, each sweep leaves a one-cell-wide column strip, and x advances by ~1 per sweep. 4.8e-5 cells/step
= 1 column per ~21,000 steps, i.e. sweep length ~5,000 cells at 4 steps per cell, matching the y extent.

Predictions (trajectory dump of 4e5 steps at t0 = 1.28e10 and at t0 = 1.29e10):
- P1. |dy| per step is mostly +-1 or 0 in long runs (> 1000 steps) with a few (< 50 per 4e5 steps) turnarounds.
- P2. The number of distinct x values visited by the ant in the window is small (< 40) while the y-range covered is > 1000.
- P3. The y range of the sweep increases between t0 = 1.28e10 and 1.29e10 by about (0.67 x Delta|x|).
- P4. The colour wake behind the ant (x larger than the ant) is locally periodic in x with a short period (<= 16)
  once the y-structure is factored out (column-to-column colour patterns repeat).

Refutation: if the trajectory is instead many short zig-zags (turnaround every < 100 steps), the "ribbon" is a
diffusive/thick front and H-sweep is wrong.

## Results (appended 2026-10-14; predictions above not edited)
Commands (worktree `g1-builder-structure`, base commit dd0e234 + uncommitted `examples/builder_dump.rs`; blank 32768 board, deterministic, one trajectory):
`bash data/g1_builder_run.sh` (= `builder_dump RLRLLL T0 400000 dumps/g1_T0` for T0 = 12800000000 and 12900000000; `dumps/` is gitignored),
`uv run data/g1_builder_analysis.py 12800000000 12900000000`, `uv run data/g1_builder_sweeps.py 12800000000 12900000000`,
`uv run data/g1_builder_scaling.py` (outputs were read from the terminal, not saved to files; rerun to regenerate).

- **P1 (long straight y-runs, < 50 turnarounds): falsified at step scale, true at sweep scale.** At step scale dy is 0 half the time and +-1 otherwise, y reverses every ~4 steps (100,802 and 99,338 reversals in 4e5 steps; median run 2). Smoothed over 40 steps there are only 34 and 26 reversals: the ant makes slow full-height sweeps.
- **P2: confirmed.** 36 and 30 distinct x values in 4e5 steps; y range 6,399 (T0 = 1.28e10) and 8,609 (1.29e10).
- **P3: confirmed.** The y range grew by 2,210; 0.67 x Delta|x| = 0.67 x 3,320 = 2,220 (|x| = 11,060 -> 14,380). Sweep length L ~ 0.67|x| - 960 from these two points only.
- **P4: confirmed (and sharper than predicted).** The wake is exactly periodic in x with period 3: column agreement at lag 3, 6, 12, 24 is 0.993-0.995, at lags not divisible by 3 it is <= 0.003. Colours 3, 4, 5 each cover 1/3 of the wake; colours 0, 1, 2 are < 0.3%. The wake spans the full sweep height at every column (6,400 rows at the first dump).
- **Mechanism (post hoc, read off the dumps; not pre-registered).** One cycle = a slow traverse of L rows at 10.02-10.03 steps per row (63,880 and 86,000 steps) plus a fast return at ~2 steps per row (12,880 and 17,320 steps), total ~12 L, adding 3 columns (one colour period) = 3 L new cells: 76,760 / (3 x 6,400) = 4.00 steps per new cell, the measured 4.02. The 40-step-smoothed segment list also shows short repeated reversals (40-120 steps) at the bottom turn that are not part of the cycle count.
- **Quantitative check, using only sweep lengths (post hoc model, but the comparison is to independently measured x(t)).** dx/dt = -3/(12 L) = -1/(4 L). Predicted d|x|^2/dt = 0.864 and 0.835 at the two dump positions; measured from the 1e6-step windows 0.862 and 0.833 (window +-2e7). Fit over the whole steady phase (298 windows): |x|^2 = 0.8634 t - 1.093e10, residual 0.7% of the range, i.e. **|x| grows as t^(1/2) in the steady phase, not linearly**: the builder decelerates because the sweep gets longer as it moves out. The only two L values used came from this same trajectory, so this does not test the L ~ |x| law at any third point.
- **Reading.** The breakout is a *period-3, boustrophedon column builder* whose cycle time is proportional to its own height. It is neither a perimeter crawl (interpretation (a) of the TODO) nor an unstructured new regime. Still open: (i) what sets the 10 vs 2 steps-per-row asymmetry and the ~0.67 slope of L against |x| (a cone of half-angle ~34 degrees?), (ii) what triggers the switch at 1.2677e10, (iii) why the colour pattern has period 3 given a rule of length 6, (iv) whether a finite local rule (a "highway of highways") is behind the traverse, (v) whether the other board escapes are the same. One rule, one trajectory, two 4e5-step windows.
- Heading period: heading autocorrelation at lags 4-48 is 0.41-0.59, so the local 10-step-per-row traverse is not a simple short-period cycle; no claim is made about it.

## 2026-10-20: the builder is a checked macro-transition (appended)
`experiments/archive/2026-10-rlrlll-macro-transition/` (predictions P1-P5 registered at `4bc029a` before the run).
Over all 4,729 cycles of the blank-board run, each cycle adds 3 columns and exactly 2 rows of height, and takes
exactly `12 m + b_q` steps with `b = (934, 1058, 898)` cycling in period 3 (`m` = bulk rows). A separate checker shows
the three-phase family `C(m, q)` is closed for every even m >= 2 (shift lemmas over the bulk, every step by
`reference::Ant`), and the run is in `C(434, 0)` at step 12,677,007,177. Consequences: the sweeper never stops,
`|x|^2/t -> 3/4` (the 0.8634 fit above is a finite-size value), and the "10 vs 2 steps per row" are exact (20 steps per
2 rows down, 4 per 2 rows up). Still open from (i)-(v) above: the trigger (ii), the colour period 3 (iii), and whether
the other escapes are the same (v). (iv) is answered: the traverse is a translation-periodic "highway along a column".
