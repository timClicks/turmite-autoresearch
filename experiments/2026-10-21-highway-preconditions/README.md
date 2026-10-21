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

From the repo root (cloud container, 4 cores, cargo 1.97; total 6 min):

```bash
E=experiments/2026-10-21-highway-preconditions
cargo test --release --test seed                                   # C1
uv run --frozen $E/scripts/make_specs.py                           # results/highway_specs.txt, control_specs.txt
bash $E/scripts/run_scan.sh                                        # events.csv, seeds.tsv, curves.csv, control.csv; run.log
uv run --frozen $E/scripts/analyse.py  > $E/results/analysis.txt   # controls and P1-P5 as registered
uv run --frozen $E/scripts/followup.py > $E/results/followup.txt   # post hoc checks (no registered predictions)
```

`run.log` holds the commit (`f099f5e`), binary sha256, command lines, timings and output sha256. Fully deterministic:
no randomness; rayon output is in spec order (`events.csv` per rule; columns documented in the example's header).

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

### Results (appended 2026-10-21 20:25 +13:00; the registration above is not edited)

566 primitive highway rules, all on board (<= 16384); **406 independent events** (rules sharing the colours reached
are one trajectory; all 160 duplicates have identical `tau*` and seed key, checked).

| Item | Outcome | Numbers (`results/analysis.txt`) |
|---|---|---|
| C1 oracle | **Passed** | 5 tests, proptest vs `reference::Ant` brute force |
| C2 transplant | **Passed** | 566/566 exact from `tau*` to `T_end + 200p`; seed size = `|D(tau*)|` 566/566 |
| C3 onset | **Passed** | 566/566 equal census |
| C4 chaotic baseline | **Passed** | control minima 233-3297 vs highway median `D_delta(tau*)` = 20 (all >= 10x) |
| P1 collapse | **Held** | 257/265 = 97.0% have ratio <= 0.1; median ratio 0.0023 (max 0.34) |
| P2 small excess | **Held, trivially** | median excess 0: `tau*` falls in the highway phase for 82% of events (caveat registered in Deviation 1) |
| P3 frontier, outward | **Held** | cos > 0 for 402/406 (99.0%); leaves the old box within 50 periods for 400/406 (median 3.0 periods) |
| P4 shared seeds | **Held as registered, but it is a prefix-family effect** | 7/8 classes have modal share >= 0.5; every class is one prefix family (below) |
| P5 excess vs onset | **Failed** | Spearman -0.063 (p 0.25, n 329) |

**What the seed is.** The dependency of the whole future on the grid collapses from thousands of cells to the size of
the highway's own trail, and it does so late and fast: `|D|` first drops to the highway level (`launch`) a median 0.11
periods before the census onset (p10 0.75 periods; one event 40). The **pre-onset seed** (exploratory; Deviation 1) is
the highway's own minimum overlap plus a median of **3 cells** (p75 6, p90 10.5; 73% within 5 cells); median size 25
cells against a chaotic level of ~10^3-10^5. At that moment the ant is at the territory's edge pointing out (P3). So
the precondition of a highway, in every one of the 406 events, is *a short fragment of that highway plus a handful of
cells, at the edge, facing blank ground*. Nothing deep in the old pattern is needed.

**P4 is not evidence of shared preconditions across unrelated rules** (`results/followup.txt`, post hoc): every one of
the 8 classes is a family with a long common prefix (`RLRLRLRR...` 16 events, `RRLLRLR...` 8, `RL...` 6, ...). Across
rules that differ within their first 4 letters, **0** seed keys and **0** pre-onset keys are shared, and the 406 events
build 343 distinct highways. At `tau*` the shared key is close to tautological (82% of seeds are the running highway's
own trail, so same highway, same seed). Before onset, families mostly do **not** share seeds (pre-onset modal share
>= 0.5 in 4/8 classes; 10 distinct pre-onset seeds among 16 events of the period-88 family): different chaotic histories
reach the same highway through different last few cells. The highway is an attractor; the grid route into it is not
a common template.

**What does predict onset time (post hoc, not registered).** Not the excess (P5) but the size of the highway itself:
Spearman with log10 onset is 0.45 for `h_min` (highway self-overlap), 0.46 for period, -0.54 for speed (displacement
per step). `h_min` and period are largely one factor (partial correlation of `h_min` given period 0.16, of period given
`h_min` 0.20). Median log10 onset by `h_min` bin: 3.8 (<10 cells, n 6), 4.4 (10-20, n 110), 5.8 (20-40, n 122), 6.7
(40-80, n 67), 6.6 (>= 80, n 24). OLS: about 0.018 decades of waiting per extra overlap cell. Rule length does not
carry it (Spearman with n: -0.12).

Interpretation (confidence moderate; alternatives not excluded): a highway starts when the ant happens to lay down a
fragment of it on the edge. If the fragment's cells had to come out of an unstructured random search, each extra cell
would cost a factor of about n (0.3-1 decades); the observed cost is 0.018 decades per cell, about 50 times flatter. So
the chaotic phase is not a random search over colours. It already produces highway-like pieces, and the bigger and
slower the highway, the longer the ant takes to produce enough of one at the right place. Alternatives not excluded:
(i) the dependence on highway size is a census selection effect (slow, long-period highways may also be harder to
detect early); (ii) `h_min` is a proxy for the highway's "basin" in some other sense, e.g. how many different edges it
can grow from; (iii) the 0.018 slope is dominated by between-family differences (406 events are not 406 independent
mechanisms when families are large).

Not done: `notebook.ipynb` (the shareable notebook required by the conventions) has not been written; the 54 late
highways (onset 1e9-8e10) are not scanned; no intervention tests (does removing one of the "+3" cells abort the launch?).

## Part 2: knock-out of the pre-onset seed (registered 2026-10-21 21:40 +13:00, before any code for it)

Question (Q18 in `notes/open-questions-hypotheses.md`): is the pre-onset seed a fine-tuned trigger, or is the highway
an attractor that a damaged fragment still reaches? The seed holds a median of 25 cells, 3 more than the highway's own
self-overlap.

Intervention, per independent event (406): rebuild the full board at `tau_pre`, set **one** pre-onset seed cell to 0
(blank), run the full dynamics for `B = (t_on - tau_pre) + 200p` steps, and score **launch survives** if the last `20p`
positions satisfy `pos[t] - pos[t-p] = (dx, dy)` with the original period and drift. Every seed cell is knocked out in
turn (10,155 knock-outs). Deterministic.

Controls: **K1**, knocking out up to 3 nonzero cells *not* in the seed (the first 3 in board scan order) leaves the
trajectory identical over `B` (must hold for 100%, else `D` is wrong); **K2**, the unmodified board launches (100%).

Predictions:
- **Q1 (fragile).** The median event's survival fraction (knock-outs that still launch, divided by seed size) is <= 0.3.
  Alternative (attractor): >= 0.5. Confidence about 55% for fragile: a defect in a highway fragment usually sends the
  ant back into chaos, and 200 periods is short.
- **Q2 (no single trigger).** In fewer than 25% of events is there exactly one essential cell (a cell whose knock-out
  alone stops the launch) with all others surviving. Exploratory reading: if Q1 fails high (robust) and Q2 fails, the
  precondition really is one specific cell, i.e. a trigger.
- **Q3 (where the essential cells are).** Essential cells are closer to the ant at `tau_pre` than surviving ones: median
  Chebyshev distance smaller, in >= 70% of events with both kinds present.

Instrument: `examples/highway_preconditions_knockout.rs`. Output `results/knockout.csv` (one row per knock-out).

Correction to the Part 2 registration (2026-10-21 21:50 +13:00, before the full run): the pre-onset seeds hold 15,339
cells in total, not 10,155 (an arithmetic slip; the procedure is unchanged). Added before the full run, exploratory and
unscored: column `any_direction`, launch with the same period and drift rotated or reflected.
