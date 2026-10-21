# What does a highway need from the grid? Causal seeds of highway onset across rules

Created 2026-10-21 20:05 +13:00, base `3fcfce8`. Status: **REGISTERED, nothing measured yet.** Predictions below are
fixed before any instrument code is written or run.

## Question

Every analysis of highways so far has used either the trajectory (onset time, period, drift: `highway_stats.txt`) or
the rule string (rule-statistics classifier, CV AUC 0.70: weak). The rule alone cannot be the whole story: the same rule
runs chaotically for 10^4 to 10^10 steps and then builds a highway, so whatever changes at onset is in the **grid**.
The question here is what the grid has to look like for a highway to start, and whether different rules share that
precondition when it is written in a rule-independent way.

## The object: the dependency set and the seed

Let `S_tau` be the state after `tau` steps from a blank board. Define

    D(tau) = { cells x : colour of x in S_tau is nonzero, and the ant reads x at some step t > tau }.

`D(tau)` is exactly the information in `S_tau` that the future uses: putting the colours of `D(tau)` on an otherwise
blank board, with the ant at its `S_tau` position and heading, reproduces the whole future trajectory step for step
(cells that are zero at `tau`, visited or not, are indistinguishable from blank; cells written after `tau` are produced
by the dynamics). For a highway rule the future eventually leaves the old territory for ever, so `D(tau)` is finite and
computable from one run. `|D(0)| = 0` (blank board); during chaos `|D(tau)|` is of order the territory area, since the
ant will revisit most of it; inside the highway it is the highway's own self-overlap (cells of recent periods that the
next periods re-read), call its range over one period `[h_min, h_max]`.

**Seed.** In the window `tau in [t_on - W, t_on + 20p)` (`t_on` the census onset, `p` the period,
`W = min(t_on, max(100p, 50000))`), let `tau*` be the **earliest** `tau` attaining the minimum of `|D|`. The seed is
`D(tau*)` together with the ant's position and heading at `tau*`. It is the smallest causal precondition of the highway
near onset: the grid state, read in conjunction with the rule, that is necessary and sufficient for everything after.

**Rule-independent encoding (the point of the exercise).** Colours mean different things in different rules, but the
ant only ever sees turns. Each seed cell is encoded by its *turn word*: the sequence of turns (L/R) the ant takes on
each of its reads of that cell after `tau*`. Coordinates are relative to the ant and rotated so the ant heads north at
`tau*`. The **seed key** is the sorted list of (dx, dy, word). The **highway key** is the turn word of one steady period
(lexicographically least rotation), which identifies "the same highway" across rules regardless of orientation.

Independent events: rules that share a prefix have identical trajectories while the extra colours are unused (seen in
the onset clusters of `notes/frontier-results.md`). An event is identified by the colours actually reached in the run:
if the largest colour ever read is `m < n - 1` the trajectory depends only on `rule[0..=m]` (no wraparound), so all
rules with that prefix and no wraparound are one event. Statistics below are over independent events unless stated.

## Inputs

All confirmed highways of the census with onset <= 1e9: `experiments/2026-10-13-census-sweeps/results/confirmed_v2.csv`
(rows with `confirmed == true`, 571 rules, lengths 2-12, onset <= 1e8) and `confirmed_1B.csv` (12 rules, onset 1e8-1e9),
primitive rules only. Blank board, ant at the origin heading north, `DIRS` and update order of `src/reference.rs`.
Deterministic: no randomness anywhere in the instrument.

The 54 late highways (onsets 1e9 to 8e10) are a later stage if this one is informative.

## Predictions (registered before any code for this experiment exists)

- **P1 (collapse).** For every event with `t_on >= 1e4`, `|D(tau*)| <= 0.1 x` the chaotic level (median `|D|` over 32
  log-spaced `tau` in `[t_on / 2, t_on - W)`; events where that interval is empty are excluded and counted). Expected
  for >= 95% of such events; median ratio <= 0.02. Fails if fewer than 95% satisfy it.
- **P2 (the seed is a highway fragment plus a few cells).** The excess `|D(tau*)| - h_min` is <= 10 cells for the median
  event. Confidence about 50%; the alternative is that onset needs a sizeable piece of specific old structure.
- **P3 (frontier, outward).** At `tau*` the ant is at the edge of its territory and the highway points away from it: the
  cosine between the drift `(dx, dy)` and the vector from the centroid of cells visited by `tau*` to the ant is > 0 for
  >= 95% of events, and the ant leaves the bounding box of cells visited by `tau*` within 50 periods for >= 90%.
- **P4 (shared preconditions across rules: the hypothesis this experiment was set up to test).** Group events by
  highway key. In highway classes with >= 3 independent events, the modal seed key covers >= 50% of the class's events
  in at least half of those classes. The null alternative is that preconditions are idiosyncratic: almost every event has
  its own seed key even when the highway is shared. Confidence about 40%.
- **P5 (precondition size and onset time).** Across independent events with `t_on >= 1e3`, Spearman correlation between
  the seed excess `|D(tau*)| - h_min` and `log10 t_on` is >= 0.3. Mechanism: a bigger specific precondition is rarer, so
  the chaotic phase takes longer to stumble on it. Confidence about 35%.

## Controls (must pass before P1-P5 are scored)

- **C1 (oracle).** `|D(tau)|` from the instrument's interval method equals a brute-force count with `reference::Ant`
  (snapshot at `tau`, run forward, collect nonzero cells read) on random rules of length 2-8 and random `tau`, in a
  proptest (`tests/seed.rs`). The instrument's stepping is also compared with `reference::Ant` there.
- **C2 (sufficiency transplant).** For every event, the seed alone on a blank board, ant at its `tau*` position and
  heading, reproduces the original trajectory exactly from `tau*` to `T_end + 200p`, where `T_end` is the end of the
  window used to collect reads. Required to hold for 100% of events (it also checks that no old cell is read after
  `T_end`).
- **C3 (onset recomputed).** The instrument's own onset, computed with the census definition, equals the census `onset`
  for every rule.
- **C4 (chaotic baseline for P1).** For 20 non-highway rules (the first 20 primitive `budget` rows of `sweep_v2.csv` in
  file order), the minimum of the truncated count `D_Delta(tau)` (reads within `Delta = 20000` steps of `tau`) over
  `tau in [1e6, 1e6 + 50000)` is >= 10x the median `D_Delta(tau*)` of the highway events. Fails otherwise, in which case
  P1's collapse would not be specific to highways.

## Commands

(To be filled in when run.)

## Results

(Appended below; the registration above is not edited.)

### Deviation 1 (2026-10-21 20:50 +13:00, after a 3-rule pilot, before any full run or scoring)

Pilot (`RL`, `RRL`, `RRRRLR`; scratch only) showed a definitional bug: when `t_on <= 50000` the window starts at
`tau = 0`, where the board is blank and `|D| = 0` trivially, so `tau* = 0` and the "seed" is empty (RL, RRL). Fix:
the window's lower end is `lo = max(t_on - W, ceil(t_on / 2))`. The chaotic level keeps its registered definition
(32 log-spaced `tau` in `[t_on/2, lo)`) where that interval is non-empty, and otherwise uses `[t_on/4, t_on/2)`.
P1-P5 are otherwise unchanged.

Also seen in the pilot, and the reason for two added (unregistered, descriptive) columns: in RRRRLR the earliest
minimum of `|D|` lies 1.1 periods *after* onset and equals `h_min`, i.e. the "seed" is a fragment of the running
highway. Then P2 is met trivially and P4 partly tautologically (the same highway has the same self-overlap). To keep
the question about *preconditions* honest, the scan also reports the **pre-onset seed**: `tau_pre` = earliest argmin
of `|D|` over `[lo, t_on]`, its size, its excess over `h_min`, and its seed key. These are exploratory; no prediction
is attached to them, and P2/P4 are scored as registered (on `tau*`) with this caveat stated next to the score.
