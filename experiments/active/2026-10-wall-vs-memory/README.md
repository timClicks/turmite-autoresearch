# Wall or memory: where does the ant's cube root live?

> **Scope after review (2026-10-27, see "Addendum: PR 19 review" at the end).** What this
> experiment supports is an *intervention* result: randomising the turn on first departure from
> a cell disrupts compact growth in six sampled core-class rules, over finite windows ending at
> 2^22 (Stage 1 early fit) to 2^31 (Stage 2). It does **not** establish reflection as the
> mechanism, and it does not establish a separate asymptotic exponent for V1. Where the text
> below says the wall or fresh-ground rule is "necessary", read "necessary under this
> particular intervention and these windows".

## Question and registered prediction

Registered 2026-10-26 23:05 NZDT (+1300), base commit
`5b96f680ba25ff898fc5ed91d2c33a43d6713233`, **before any code for the walker
and before any run**. Requested by the project owner after a discussion of how
to get closer to the cube-root mechanism.

### Why this test

The original mechanism (`notes/cube-root-hypothesis.md`, 2026-10-10) has two
ingredients: (1) *blank cells repel*: every canonical rule turns R on colour 0,
so an ant entering fresh ground curls back; (2) *the interior is well mixed*.
The controls so far pull in different directions:

- the memoryless persistent walker `pw:0.5` matches the ant's interior turn
  statistics (`notes/mixing-random-sample.md`), yet grows as t^0.92 with a
  porous territory (a 0.920, beta 0.909, `experiments/archive/2026-10-kappa-walker-reference/`);
- the rotor and the ant both reach a ~ 2/3 with compact territories;
- turn noise applied on every step raises the ant's area exponent smoothly,
  0.70 at eps <= 0.01, 0.76 at 0.1, 0.89 at 0.5 (`experiments/archive/2026-10-d3-noise/results/d3_stats.txt`).
  That noise breaks both ingredients at once: it randomises the turn on fresh
  cells (the wall) and on revisited cells (the memory).

No walker so far separates the two. This experiment does, with a 2x2 factorial
on one walker family.

### The walker `hy:RULE:EV:EF:SEED`

The ant `RULE` with turn noise applied separately by cell type. Each step
draws one SplitMix64 value `r` from the walker's own stream (seeded by `SEED`).
If the current cell has **never been departed from** (fresh) the noise rate is
`EF`, otherwise `EV`. A noisy step replaces the rule's turn by R or L with
probability 1/2 each; the colour still advances as in the ant. The cell's
"departed" flag is separate from its colour (a revisited cell back at colour 0
is not fresh). The probe's visited set and the walker's fresh flag agree on
every cell except the start cell before its first departure.

Corners (canonical rules turn R on colour 0):

| | EF = 0: wall kept (fresh cell -> R) | EF = 1: wall removed (fresh cell -> random) |
|---|---|---|
| **EV = 0: memory kept** | the ant `RULE` (deterministic) | **F1**: ant memory, no wall |
| **EV = 1: memory removed** | **V1**: the *hybrid wall walker*, memoryless +/-90 deg turns inside, forced R on fresh ground | memoryless persistent walk, exactly `pw:0.5` |

Exact identities that the implementation must satisfy (oracle tests, run
before any measurement): `hy:RULE:0:0:S` equals the ant `RULE` step for step
and window for window; `hy:RULE:1:0:S` is the same trajectory for every rule
(V1 is rule-free); `hy:RULE:1:1:S` equals `pw:0.5:S` step for step.

### Two explanations

- **H-wall.** The cube root comes from the reflecting edge: forced R on a fresh
  cell bounds penetration into fresh ground, so the walker deposits a few cells
  and returns; any diffusive interior then spends a fraction ~P/A of its time on
  the boundary, giving dA/dt ~ A^(-1/2).
- **H-memory (local-time balancing).** The cube root needs the interior's
  deterministic memory, which keeps neighbouring cells' visit counts close (as
  the rotor router's bounded discrepancy does), so the frontier advances only
  when the interior has been visited enough. The fresh-ground rule is not what
  sets the exponent.

### Instrument and classification (frozen)

`probe 27 16384` (board 16384, windows up to k = 27, probe CSV `t` = window end).
Per run, exactly as `experiments/archive/2026-10-kappa-walker-reference/scripts/analyse.py`:
a = slope of ln area vs ln t; beta = slope of ln perimeter vs ln area;
kappa = mean over windows of (boundary_steps / (t/2)) / (perimeter / area);
g_k = slope of ln kappa vs ln t. Two window sets: **early** k = 12..22 (complete
for every walker that does not escape by 2^22) and **late** k = 20..26 (the census
window). A run contributes to a window set only if all its windows are present.
Condition values are means over runs, with between-run sd.

A condition is
- **compact** if early a <= 0.78 and early beta <= 0.65, and, when at least
  6 of its runs complete the late window, late a <= 0.74;
- **porous** if early a >= 0.85 and early beta >= 0.80;
- **intermediate** otherwise (reported, not forced into a class).

### Predictions

Calibration gates (if one fails, the factorial is reported but not scored):

- G1. Rotor (8 seeds): early a in [0.68, 0.77], beta in [0.53, 0.62]; late a in
  [0.66, 0.71] (prior run: 0.730 / 0.575 early, 0.685 late).
- G2. `hy:R:1:1` reproduces `pw:0.5` (early a 0.92 +/- 0.03, beta 0.91 +/- 0.04);
  trajectory identity is also tested exactly in Rust.
- G3. Each deterministic `hy:RULE:0:0:0` reproduces its census row's a and beta
  (`experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv`, window
  20..26) to within 0.005, and is compact.

Discriminating corners:

| | H-wall predicts | H-memory predicts |
|---|---|---|
| V1 (`hy:R:1:0`, 8 seeds) | compact | porous |
| F1 (`hy:RULE:0:1`, 6 rules x 8 seeds) | porous, or early a at least 0.05 above the rule's deterministic run in >= 5 of 6 rules | compact, early a within 0.03 of the deterministic run in >= 5 of 6 rules |

Dose arms (6 rules x 8 seeds each): `(EV, EF)` = (0.01, 0), (0.1, 0), (0, 0.1)
and (0.1, 0.1). Let Delta_V and Delta_F be the early-a shifts of (0.1, 0) and
(0, 0.1) above each rule's deterministic run. H-memory predicts
Delta_V - Delta_F >= 0.03 in >= 5 of 6 rules; H-wall predicts Delta_F - Delta_V
>= 0.03 in >= 5 of 6 rules. (0.1, 0.1) should rise as in D3 (0.76 median, a
replication check of D3's semantics; noise streams differ, so not exact).
(0.01, 0) is expected to stay within 0.02 of the deterministic run (D3: 0.698
at eps = 0.01); this probes whether a small memory corruption already matters.

Reading of the corners:

- V1 porous and F1 compact: **H-memory supported**; the wall is neither needed
  nor sufficient.
- V1 compact and F1 porous: **H-wall supported**.
- Both compact: either ingredient suffices; the cube root is redundant.
- Both porous: neither suffices alone; the ingredients interact.
- F1 split across rules (fewer than 5 of 6 agree): rule-dependent, reported as such.

**My prior, stated before running:** H-memory, about 70%. With a memoryless
interior, a forced-R step on a fresh cell makes a loop of at most four steps
back to the entry cell, after which the walker leaves at random, so chains of
such loops can still march outward; nothing in the interior suppresses
visit-count fluctuations, and the random-cookie walker (a first-departure bias,
no lasting memory) stayed at a ~ 0.92 (`notes/walker-comparisons-2026-10-13.md`).
Against this: deposition at a roughly reflecting edge could act like Eden growth
and stay compact. F1 is the arm I am least sure of: removing the wall lets the
ant wander onto fresh ground, and how far depends on the rule's low colours.

### What this cannot show

A finite-window exponent (2^27 steps at most, early window ending at 2^22: the probe's `k`
is log2 of the window's *end* t, so the registered `k = 12..22` fit ends at 2^22) is
not an asymptotic class: D3's smooth rise shows crossovers can be slow. A
"compact" verdict for V1 or F1 says the ingredient keeps the walker compact
over these windows, not that a = 2/3 exactly. Six rules from one class are a
sample, not the census. Nothing here derives the exponent.

## Pruning-index preflight

- Index revision `5b96f680ba25ff898fc5ed91d2c33a43d6713233`. Commands:
  `rg --files notes/pruning-index/entries`; `rg -n -i -e walker -e wall -e repel -e hybrid -e persistent -e blank -e "pw:" notes/pruning-index/entries`;
  `rg -n -i -e fresh -e noise -e memory -e wall -e hybrid -e "local.time" notes/pruning-index/entries`.
- Candidates: the three entries (`NR-20261022-additive-laws-order-blind`,
  `NR-20261025-crawler-window-single-letter`, `NR-20261025-kappa-exposure-classes-exposed-edge`).
  Hits were incidental words ("blank background", "noise gate", "fresh target").
- Scope comparison: none concerns growth exponents, turn noise, or walkers with
  a modified fresh-ground rule. Membership predicates are exact cohorts of
  other observables; this run's specs are not members.
- Decision: **run**. The rotor and `pw:0.5` corners are deliberate replications
  (calibration controls), justified above.
- Run spec: `results/specs.txt` (270 lines), produced by `scripts/select_rules.py`;
  no exclusions. Rule draw: 6 rules, numpy `default_rng(20261026)` from the core
  class (cls blob, 0.30 < alpha_w < 0.37, not bursty; 2404 rules), giving
  `RLRLLRRLRLR`, `RLRLLRRRRRRR`, `RRLLLRLRRRLL`, `RRLLRLLRLR`, `RRRLLLLR`,
  `RRRRLLLLLLLR` (`results/rules.txt`). None satisfies the square-ring filler
  predicate `Pi(k)` (`experiments/archive/2026-10-square-ring-fillers/scripts/ring.py`).
  `RRRLLLLR` has census a 0.592, c 0.197, the slowest of the six; it stays in, as drawn.
- Budget: one run of the 270 specs, `RAYON_NUM_THREADS` set to the cores
  available, expected well under an hour on 4 cores. No extension (longer runs,
  more rules, other Q or P) without a new dated registration here.

This experiment departs from the ordered sequence in `notes/ACTIVE.md`
(boundary-access discrimination first). It is a cheap ablation chosen by the
project owner; it does not replace that sequence.

## Reproduction

```sh
uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/select_rules.py
cargo test --release --locked --test hybrid_walker
sh experiments/active/2026-10-wall-vs-memory/scripts/run.sh
uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/analyse.py
```

`run.sh` builds `probe` into a fresh `CARGO_TARGET_DIR`, records the commit and
binary sha256, and writes `probe.csv`, `probe.log` and `run.done` into its output
directory. The committed `results/` already holds `run.done`, so the bare commands above
skip the simulation. To actually re-simulate, give a fresh directory and verify it
(added after review; see the addendum):

```sh
OUT=experiments/active/2026-10-wall-vs-memory/scratch/rerun   # gitignored
sh experiments/active/2026-10-wall-vs-memory/scripts/run.sh $OUT
sh experiments/active/2026-10-wall-vs-memory/scripts/run_stage2.sh $OUT
uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/verify.py $OUT --against experiments/active/2026-10-wall-vs-memory/results
uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/analyse.py $OUT
uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage2.py $OUT
```

`verify.py` checks the specs hash, the CSV hash against provenance, that exactly the
registered specs are present with complete windows, and (with `--against`) byte identity
with the committed CSV.

## Results, uncertainty and limitations

See "Stage 1 results" and "Stage 2 results" below (appended in order, after
their registrations). Summary at the end of the file.

## Pruning-index outcome and next question

See "Outcome" at the end of the file.

## Addenda (append only)

### 2026-10-26 23:40 NZDT: labels and threshold, before any run

- Deviation (label only): `Rule` needs at least two colours, so the rule-free
  corners are run as `hy:RL:1:0:SEED` (V1) and `hy:RL:1:1:SEED` (the `pw:0.5`
  corner) instead of the `hy:R:...` written above. Every canonical rule gives
  the same trajectory in these corners (tested), so nothing else changes; the
  analysis groups them as `hy:*:1:0` and `hy:*:1:1`.
- Precision of the semantics: a step is noisy iff the low 32 bits of the draw
  are below `floor(eps * 2^32)`, and a noisy turn is R iff the high 32 bits are
  below 2^31 (the `PersistentWalk` test at q = 0.5). The sparse reference in
  `tests/hybrid_walker.rs` compares in floating point, which differs only when
  the low bits equal that floor exactly (probability 2^-32 per step).
- Oracle tests (`cargo test --release --locked --test hybrid_walker`, 5 tests)
  pass at the commit that adds the walker: sparse reference for random rules
  of length 2..12 and noise rates; no-noise equals `reference::Ant` and the
  ant probe; full noise equals `PersistentWalk(seed, 0.5)` window for window;
  revisit-only noise is rule-free, and removing the wall changes it.
- `scripts/analyse.py` is committed before the run and implements the
  classification and readings above; any later change to it is recorded here.

### 2026-10-26 23:15 NZDT: timestamp correction (append only)

The times written by hand above ("Registered ... 23:05", the "23:40" addendum)
were estimates, not clock readings, and some lie after the run. The git commit
times are authoritative: registration `086c1ac` at 22:55:21 NZDT, walker, tests
and frozen `analyse.py` `f1bd2c8` at 23:02:13, Stage 1 run 23:02:30 to 23:05:33
(`results/provenance.txt`, UTC). The order registration -> code -> run holds.
From here on every timestamp is read from the clock.

## Stage 1 results (run 2026-10-26, commit `f1bd2c8`)

Command: `RAYON_NUM_THREADS=4 sh scripts/run.sh` then `uv run --frozen scripts/analyse.py`.
Provenance (commit, binary and input sha256, start/end) in `results/provenance.txt`;
per-run fits `results/runs.csv`, per-condition `results/conditions.csv`, scored
output `results/analysis.txt`. 270 runs, 18 with an escape on the 16384 board
(all in porous conditions: 8 of 8 `hy:*:1:1`, 10 in F1), none before the early window.

**Gates: G1, G2, G3 all pass.** Rotor early a 0.722 (sd 0.018), beta 0.562, late
a 0.687; the `pw:0.5` corner early a 0.929, beta 0.921; every deterministic run
reproduces its census a and beta exactly (difference 0.0000).

**Corners (scored):**

| condition | early a | early beta | late a (n) | class |
|---|---|---|---|---|
| ant, deterministic (6 rules) | 0.591-0.705 | 0.50-0.55 | 0.592-0.702 (6) | compact (6/6) |
| F1, memory kept, wall removed | 0.861-0.906 per rule | 0.84-0.89 | 0.866-0.923 | **porous (6/6)**; a up by +0.19 to +0.29 |
| V1, hybrid: wall kept, memory removed | 0.801 (sd 0.023) | 0.695 (0.025) | 0.759 (0.061) (8) | **intermediate** |
| memoryless, no wall (`pw:0.5`) | 0.929 (0.033) | 0.921 | 0.930 (4) | porous |
| rotor | 0.722 (0.018) | 0.562 | 0.687 (8) | compact |

- **F1: the H-wall criterion is met in 6/6 rules and the H-memory criterion in 0/6.**
  My registered prior (H-memory, about 70%) is wrong for this arm: with the
  ant's memory intact, randomising only the turn on fresh cells makes every
  rule porous, close to the memoryless walker. The fresh-ground rule is
  **necessary** for the compact cube-root regime in all six rules *under this
  intervention* (randomising it; the review narrows this, see the addendum).
- **V1 is intermediate**, so no registered corner reading applies. The wall
  alone takes the walker from a 0.93 / beta 0.92 (`pw:0.5`) most of the way
  towards the rotor and the ant (0.80 / 0.70 early, 0.76 / 0.63 late), with
  fill 0.50-0.62 at 2^27 (rotor 0.68-0.75). Sufficiency is not shown within
  these windows; necessity is.
- **Dose arms:** neither registered dose prediction holds (Delta_V - Delta_F >= 0.03
  in 2/6 rules, the reverse in 0/6). At a 10% rate, revisit noise moves the
  exponent more than fresh noise on average (mean Delta_V +0.047, mean Delta_F
  +0.028; Delta_V <= 0.04 in 2/6 rules, Delta_F <= 0.04 in 5/6), but not by
  the registered margin rule by rule. `RRRLLLLR`, the slowest rule, moves most
  under every noise. (0.01, 0) stays
  within 0.02 in 4/6 rules (the two exceptions are `RRRLLLLR` +0.063 and
  `RRRRLLLLLLLR` +0.028). (0.1, 0.1) median early a 0.717 against D3's 0.761 at
  eps 0.1 (different rules, stream and window).
- **Post hoc, descriptive:** EF = 0.1 shifts early a by +0.028 on average without
  changing the compact classification, while EF = 1 makes every condition mean porous.
  With EF = 0.1 a fresh cell turns L only 5% of the time.

Interpretation (mine, not a registered test): the cube root in these ants
needs the repelling fresh-ground rule; interior memory does not substitute for
it, but the wall alone, with a memoryless interior, has not reached the ant's
exponent by 2^27. Either the hybrid converges slowly to 2/3, or it has its own
exponent near 0.75 and memory supplies the rest. Stage 2 asks which.
Limits: six rules from one class; finite windows; V1's late-window sd (0.061)
is three times the rotor's.

## Stage 2: does the wall alone reach the cube root? (registered 2026-10-26 23:15 NZDT, before running)

Base commit `f1bd2c8`; Stage 1 results in hand (this prediction is informed by
them and says so). Stage 1 local per-octave area exponents for V1 (mean over 8
seeds, from `results/probe.csv`, computed ad hoc): about 0.82 at k = 17-20 and
0.73-0.77 at k = 24-27; the rotor's are 0.67-0.69 at k = 24-27.

Design: `hy:RL:1:0:SEED` for seeds 2026102601..16 (the 8 Stage 1 seeds, whose
first 2^27 steps repeat exactly, plus 8 new), and `rotor:SEED` for seeds
2026102601..08 as the control; `probe 31 16384` (windows to k = 31). Spec file
`results/stage2_specs.txt`, output `results/stage2_probe.csv`, scored by
`scripts/analyse_stage2.py` (committed before the run). Per run: a and beta over
k = 24..30 (fit as Stage 1), local area exponent per octave, and the slope of
local a against k over k = 22..31. Uncertainty: between-seed sd and a seed
bootstrap (10,000 resamples, numpy seed 20261026) of the mean slope.

Gate S0: rotor a(24..30) in [0.65, 0.70].

Readings (V1, 16 seeds):
- **Converging (wall suffices in the long run):** mean a(24..30) <= 0.72 and the
  bootstrap 95% interval of the local-a slope lies entirely below 0.
- **Separate exponent (memory needed for the rest):** mean a(24..30) >= 0.73 and
  the slope interval contains 0.
- Anything else: unresolved at this horizon.

Prior: converging, about 55%; the Stage 1 trend (roughly -0.01 per octave)
extrapolates to about 0.71 by k = 30, but four octaves of an sd-0.06 walker can
easily look flat. Runs that escape the board are counted and fitted only on
complete windows. Budget: 24 runs of up to 2^31 steps, minutes on 4 cores; no
further extension without a new registration.

## Stage 2 results (run 2026-10-26 23:14-23:18 NZDT, commit `428a083`)

Command: `RAYON_NUM_THREADS=4 sh scripts/run_stage2.sh`, then
`uv run --frozen scripts/analyse_stage2.py`. Provenance in
`results/stage2_provenance.txt`; per-run fits `results/stage2_runs.csv`; scored
output `results/stage2_analysis.txt`. 24 runs to 2^31 steps, no escapes.
Determinism check (ad hoc, shell `md5sum` over CSV rows): the 8 V1 and 8 rotor
runs that share seeds with Stage 1 reproduce its rows exactly for k <= 27.

| walker | a(24..30) | beta(24..30) | local-a slope per octave, 95% bootstrap | mean local a, k = 28..31 |
|---|---|---|---|---|
| rotor (8) | 0.677 (sd 0.003) | 0.521 (0.019) | -0.0024 [-0.0037, -0.0009] | 0.674, 0.676, 0.674, 0.669 |
| V1 hybrid (16) | 0.732 (sd 0.021) | 0.585 (0.047) | -0.0045 [-0.0124, +0.0031] | 0.724, 0.705, 0.717, 0.728 |

- **S0 passes** (rotor 0.677).
- **V1 reading under the frozen rule: "separate exponent".** But it is
  borderline: the mean a(24..30) of 0.732 clears the 0.73 threshold by 0.002,
  less than a tenth of the between-seed sd. The slope interval contains 0
  and also reaches -0.012 per octave, so slow convergence is not excluded.
  The fair summary is that at 2^31 steps the hybrid sits about 0.05 above the
  rotor in a and 0.06 in beta, with no resolved trend in either direction.
- My registered prior (converging, about 55%) did not get its reading; I do
  not count this as strong evidence for a separate exponent either.

## Outcome

1. **The wall is necessary (Stage 1, F1, scored).** In all six drawn core-class
   rules, keeping the ant's memory but randomising its turn on fresh cells gives
   a porous territory (early a 0.86-0.91, beta 0.84-0.89), close to the
   memoryless walker. My registered H-memory prior predicted the opposite.
2. **The wall alone gets most of the way, not all (Stages 1-2).** The hybrid
   (forced R on fresh cells, memoryless +/-90 deg turns elsewhere) moves from the
   memoryless walker's a 0.93 / beta 0.92 to 0.73 / 0.59 at k = 24..30, against
   the rotor's 0.68 / 0.52 and the six ants' 0.59-0.70 / 0.51-0.55 (k = 20..26).
   Whether it converges to 2/3 is unresolved at 2^31.
3. **Low-rate noise shifts the exponent a little but did not change the registered
   classification.** At 10%, neither cell type dominates rule by rule; mean early-a
   shifts are +0.047 (revisit noise) and +0.028 (fresh-cell noise), and 10% fresh-cell
   noise left all six conditions compact. The registered dose predictions failed in
   both directions. (Reworded after review: classification stability is narrower than
   "negligible effect".)

What this does not show: that the ant's cube root *is* the hybrid's mechanism
(the ant's interior is not memoryless); anything beyond six rules of one class;
asymptotic exponents. Nothing here derives 2/3.

Pruning index: `NR-20261026-wall-vs-memory-no-wall-porous` records the F1
result (empirical, exactly the 48 tested F1 specs). It permits deferring an
exact repeat on these rules, seeds and instrument. It does not exclude memory as
a contributor; point 2 suggests memory supplies the remainder. No signature is
written for V1 (unresolved) or the dose arms (failed predictions of a contrast,
not a dead end).

Next questions (none registered):
- *How does the response to fresh-cell noise grow with EF?* EF = 0.1 moves early a by
  +0.028 on average (no change of class) but EF = 1 makes every condition mean porous. A dose curve in EF between 0.1
  and 1 would locate the threshold and test whether it is a sharp transition (a
  percolation-like loss of the reflecting edge) or a smooth crossover. Prediction
  to be derived before registering.
- *What does the memory add on top of the wall?* Compare the hybrid's and the
  ant's interior visit-count fluctuations (neighbour discrepancy of local times),
  the quantity the rotor router controls. If the ant's are rotor-like and the
  hybrid's diffusive, that is the remaining 0.05 in a.
- *Does V1 converge?* Only a longer run or a mechanism-level argument can say;
  2^35 steps on a larger board is feasible with the tiled grid (`TURMITE_GRID=tiled`
  covers `sweep_lean` only, so the probe would need porting first).

### Write-up reproduction (appended)

```sh
uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/figure.py         # results/fig_local_exponents.png
uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/build_notebook.py  # then execute as in its docstring
```

## Addendum: PR 19 review (2026-10-27 20:45 NZDT, append only)

An external review of head `15d41a9` recomputed the main fits (they reproduce) and asked
for narrower claims. Registered scores and frozen fits above are **unchanged**; the
following corrections and limits are appended. Review-time numbers come from
`scripts/posthoc_review.py` -> `results/posthoc_review.txt` and are post hoc, descriptive.

1. **What the factorial supports.** It separates two intervention policies: randomising the
   first-departure turn (EF) and randomising later turns (EV). Supported: (a) EF = 1
   changes growth in all six sampled rules and every F1 condition mean meets the registered
   porous criterion; (b) from fully random, forcing R on first departure substantially
   lowers the finite-window exponent; (c) ant -> V1 shows the interior turn policy matters,
   i.e. removing interior colour-dependent turns does not preserve the ant's behaviour.
   Under the registered table neither explanation wins (V1 intermediate).

2. **"Wall removed" is not "reflection removed".** Randomising first departures also breaks
   coherent first-visit chirality, short-loop geometry and the correlations between
   heading and the evolving colour field, and F1's colour memory then develops along a
   different trajectory. This experiment identifies a consequential first-departure
   policy, not why it matters. Likewise V1 keeps historical information in the `departed`
   flag, so "interior colour-dependent turns removed" is more accurate than "memory
   removed", and randomising the interior does not test whether the interior is well
   mixed. "Necessary" throughout means: under this intervention, over these windows.
   Not shown: that deterministic R is the only first-departure policy compatible with
   compact growth (forced L is untested; see item 9).

3. **Conditions are not individual runs.** The registered classification applies to
   condition means (F1: 6/6 porous). Applying the same early thresholds (a >= 0.85 and
   beta >= 0.80) to individual runs, **39 of 48 F1 runs** meet both (per rule 7, 6, 6, 8, 7,
   5 of 8; lowest run a = 0.824). Seeds are shared across rules, so the 48 trajectories
   are not 48 independent rule-level replications; the independent units are the six
   selected rules, drawn from an already compact core class.

4. **Time-window correction.** `csv_rows` emits `k = log2(t_end)` for the window
   (2^(k-1), 2^k], so the CSV's `k = 12..22` early fit ends at **2^22**, not 2^23 (the
   earlier text, the notebook and the pruning entry said 2^23); late `k = 20..26` ends at
   2^26, Stage 2 `k = 24..30` at 2^30 with `k = 31` the last window. The frozen fits are
   unchanged. `verify.py` checks `k = 9..27` / `9..31` contiguity. Late-window escape
   censoring (18 of 270 stage 1 runs escaped) warrants caution for late fits; it does not
   affect the complete early-window result.

5. **Stage 2 cannot establish a separate exponent.** The registered rule read V1 as
   "separate exponent" because a(24..30) = 0.732 >= 0.73 and the trend interval
   [-0.012, +0.003] contains zero. An interval containing zero is failure to resolve a
   trend, not evidence of a plateau, and a significantly negative trend would not by
   itself identify 2/3 as the limit. Post hoc: V1 a(24..30) = 0.7320 (seed-level
   bootstrap 95% of the mean [0.722, 0.742], n = 16); refitting over `k = 27..31` gives
   **0.7170** ([0.699, 0.736]); the per-seed shift between windows is -0.015 (sd 0.034).
   Rotor: 0.6767 -> 0.6735. The score stands as registered (borderline "separate
   exponent", cleared by 0.002) but the scientific conclusion is **unresolved**: the
   finite-window separation of V1 from the rotor is real, its asymptote is not determined.
   Use "finite-window separation", not an asymptotic verdict.

6. **Low noise is not negligible.** Mean early-a shifts at 10% are +0.047 (revisit-only)
   and +0.028 (fresh-only); both registered dose predictions failed. The supported
   statement is "10% fresh-cell noise did not change the registered compact
   classification in any of six rules" (revisit-only 10% left 5 of 6 compact). Replaces
   "low-rate leaks don't matter" / "tolerates occasional leaks" everywhere.

7. **Oracle discrepancy resolved.** The sparse reference in `tests/hybrid_walker.rs` compared
   `low32 / 2^32 < eps` in floating point while production compared `low32 < floor(eps *
   2^32)`; they differ exactly when `low32 == floor(eps * 2^32)` for non-dyadic eps. The
   specified semantics are now the integer ones (`walkers::noise_threshold32`, doc-comment
   on `HybridWalker`): noisy iff `low32 < floor(eps * 2^32)`; eps = 1 always noisy, eps = 0
   never. The reference restates this independently, and
   `noise_threshold_boundary_is_strict_integer_comparison` aims the first draw (by
   inverting SplitMix64's `mix64`) at threshold - 1, threshold and threshold + 1 for
   several eps. Production behaviour is unchanged, so every committed result stands; the
   fresh rerun below re-checks that byte for byte.

8. **Reproduction now re-simulates.** `run.sh` / `run_stage2.sh` take an optional output
   directory (the committed one still skips because it holds the `.done` markers), the
   analysis scripts take a results directory, and `verify.py` validates specs, completeness
   and hashes (and byte identity with `--against`). Outcome of the fresh rerun (both stages, 4 threads, new
   binary built after the change in item 7): `verify.py --against` passes; `probe.csv` and
   `stage2_probe.csv` are byte-identical to the committed files and the analysis outputs are
   identical. Recorded in `NOTEBOOK.md`.

9. **Follow-up tests, registered here before any measurement (not run).** Each is
   independent of the merge criterion.
   - **F-a. Deterministic first-departure L.** Same cohort, seeds and windows; revisited
     cells unchanged; compare forced R, forced L and fair R/L on first departure.
     Prediction (mine, ~60%): forced L is also compact (it is the mirror image on fresh
     ground, so its loops are also coherent), a within 0.05 of forced R in >= 5/6 rules and
     both far from fair R/L. If so, "R is necessary" is wrong and the operative property is
     *coherent chirality on first departure*; if forced L is porous, the colour-0 R policy
     itself matters (rule asymmetry with the interior's R/L colours).
   - **F-b. Mediator measurement.** Record per fresh excursion: length, maximum
     penetration into fresh ground, new cells deposited before the first return to previously
     departed territory, and return probability, for ant, F1, V1 and forced-L. Prediction:
     these statistics rank the conditions in the same order as their early a (Spearman
     >= 0.8 over the 6 rules x 4 conditions), and fresh excursion length is longer and heavier
     tailed in F1. If they do not predict growth, the reflecting-edge explanation fails.
   - **F-c. Convergence extension.** V1 and rotor at two longer horizons (2^33, 2^35) with
     new seeds, board large enough to avoid escape, equal-width late windows frozen before
     running (5 octaves each), reporting window sensitivity and seed-level uncertainty.
     Prediction: V1 a(window) keeps decreasing with horizon (-0.015 to -0.03 per window
     shift); a ~0.70 at the later window. The verdict word is "finite-window separation".
     Needs the tiled grid ported to the probe (not done).
   - **F-d. Fresh versus colour-zero noise.** Compare noise on first departure with noise
     on every colour-zero read (including revisits). Prediction: colour-zero noise at the
     same rate shifts a more than fresh-only noise (it also hits revisits), so "blank cells
     repel" is not the same intervention as "fresh ground repels".
   A denser EF dose curve follows these controls; a steep finite-time curve alone would not
   separate a transition from a noise-dependent crossover.

## Stage 3: what about the fresh-ground turn matters? (registered 2026-10-28 18:35 NZDT, before any code or run)

Base commit `4fd558bf93177bfeb5461e2a2ae7e3206450fdf9`. Supersedes nothing above; it runs
F-a from item 9 of the review addendum unchanged in substance, adds one arm, and defers F-b
for a reason found while designing it.

### An exact fact that reshapes F-b

Call a *fresh run* a maximal sequence of consecutive steps taken from fresh (never departed)
cells. Under any deterministic quarter-turn policy on fresh cells (forced R, as in the ant and
V1, or forced L), the fresh cells of one run are visited around a 2x2 block: after four equal
quarter turns the walker re-enters the first cell of the run, which is now departed. So **a
fresh run has at most 4 cells** under forced R or forced L, whatever the interior does, and
under a forced U-turn (below) at most 2 (2 only at the start cell). Under F1's fair R/L the
run is an unbounded random path into fresh ground. This is a property of the construction,
not a measurement; the oracle test below checks it on simulated trajectories.

Consequence: F-b's "fresh excursion length" and "new cells deposited before the first return"
are bounded by 4 for every deterministic arm and can only separate F1 from the rest, which
Stage 1 already did. Its registered Spearman criterion (>= 0.8 over 24 conditions) would be
met or missed mainly by that one split. **F-b is deferred**, not run; a mediator worth
measuring has to vary among bounded policies.

### Explanations and arms

Three explanations of why the fresh-ground turn matters (Stage 1: randomising it makes all six
rules porous):

- **H-bound.** What matters is that excursions into fresh ground are *bounded*: the walker
  deposits O(1) cells and returns to departed territory. Any bounded policy keeps growth compact.
- **H-chiral.** What matters is *coherent chirality* on fresh ground: a consistent loop sense
  (R or L), not boundedness alone. (This is the reading behind the registered F-a prediction.)
- **H-match.** What matters is that the fresh turn *matches the rule's colour-0 turn* (every
  canonical rule turns R on colour 0), so fresh ground behaves like the interior's colour-0 cells.

New walker `ft:RULE:T` (deterministic, no seed): the ant `RULE`, except that on a cell it stands
on for the first time it turns by `T` instead of `rule[0]`: `R` (+1 quarter turn), `L` (-1) or
`U` (half turn, a reversal: the walker steps straight back to the cell it came from). The colour
advances as in the ant; freshness is the never-departed flag, as in `hy:` (a revisited cell at
colour 0 is not fresh).

| arm | H-bound | H-chiral | H-match |
|---|---|---|---|
| `ft:RULE:L` (F-a, forced L) | compact | compact | not compact |
| `ft:RULE:U` (new, reversal) | compact | not compact | not compact |

`ft:RULE:R` is the ant itself for these rules (all six turn R on colour 0) and is the identity
gate. A straight-ahead policy is not run: from the start cell it walks a ray of fresh cells
and never returns, which is trivially non-compact and tells us nothing.

### Instrument, classes, cohort (frozen)

The Stage 1 instrument unchanged: `probe 27 16384`, early `k = 12..22`, late `k = 20..26`,
fits as `scripts/analyse.py`. Classes as Stage 1 (compact / porous / intermediate), plus one
added before any run because a reflecting policy might trap the walker in a cycle that never
touches fresh ground again, which the compact thresholds would mislabel: **stalled** if early
a < 0.45 or if the final window's area equals the previous window's. Stalled is not compact.
"Not compact" in the table means porous, intermediate or stalled.

Cohort: the six Stage 1 rules (`results/rules.txt`). The walker is deterministic, so the eight
seeds of F-a's wording would give eight identical runs; there is **one run per (rule, arm)**,
18 runs in all (3 arms x 6 rules), and the independent units are the six rules. There is no
between-seed sd; the spread over rules is reported instead.

Gates (if one fails, nothing is scored):
- T0. `cargo test --release --locked --test fresh_turn` passes: `ft:RULE:R` equals
  `reference::Ant` step for step (cells, heading, position) for rules starting with R; `ft:`
  equals an independent sparse reference for all three policies; the fresh-run bound (<= 4 for
  R/L, <= 2 for U) holds on every simulated step.
- T1. Each `ft:RULE:R` probe row equals the committed deterministic `hy:RULE:0:0:0` row in
  `results/probe.csv` field for field except the label.

Reading (per arm, an arm is "compact" or "not compact" when at least 5 of 6 rules agree; else
"split, rule-dependent"):
- L compact and U compact: **H-bound** favoured.
- L compact, U not compact: **H-chiral** favoured.
- L not compact, U not compact: **H-match** favoured.
- L not compact, U compact: none of the three; reported as unexplained.
- Any split arm: no reading for that arm.

Quantitative side predictions (scored, not part of the reading): F-a as registered, forced L
early a within 0.05 of the ant in >= 5 of 6 rules. For U, if compact, early a within 0.05 of
the ant in >= 4 of 6 rules.

**My priors, stated before running:** H-bound 40%, H-chiral 30%, H-match 20%, other 10%. On
F-a I keep the registered ~60% for "forced L compact". The reason for leaning towards H-bound:
V1 (bounded fresh runs, no interior colour memory) was already much more compact than `pw:0.5`,
which suggests the bound does most of the work. Against it: reversal deposits one cell per
contact, which is Eden-like deposition and could be compact for a different reason, or
could let the ant's interior sweep along the edge without growing.

What this cannot show: a finite-window class, six rules of one class, and nothing about why
the bound gives a cube root. A reading favours an explanation among these three; it does not
establish it.

### Pruning-index preflight (Stage 3)

- Index revision `4fd558bf93177bfeb5461e2a2ae7e3206450fdf9`; `rg --files notes/pruning-index/entries`
  (4 entries); `rg -n -i -c -e forced -e u-turn -e uturn -e reverse -e first.departure -e fresh
  -e chiral -e "hy:" -e "ft:"` (hits in 3 entries); `rg -l -F RULE` for each of the six rules
  (hit only `NR-20261026-wall-vs-memory-no-wall-porous`).
- Membership: `NR-20261026` covers exactly the 48 `hy:RULE:0:1:SEED` specs (EF = 1 random fresh
  turns); `ft:` specs are deterministic fresh-turn policies and are not members. The
  kappa-exposure and crawler hits are incidental ("forced first departures" as an observable of
  the plain ant, "fresh" target directories). The additive-law entry concerns conservation laws.
- Decision: **run**. `ft:RULE:R` deliberately replicates the deterministic ants (gate T1).
- Budget: 18 runs of 2^27 steps on 4 cores (minutes). No extension without a new registration.

Clarification (2026-10-28 18:55 NZDT, still before any run): Stage 1's `classify()` applies the
late-window test only to conditions with >= 6 runs, so the single-run deterministic ants were
classed on the early window alone. Stage 3 conditions are single runs and use the same function
unchanged; the late a (when the run completes `k = 20..26`) is reported beside the class and
scored separately as "late a <= 0.74", not folded into the class. Specs:
`results/stage3_specs.txt` (18 lines, `ft:RULE:T` for T = R, L, U); scorer `scripts/analyse_stage3.py`,
committed before the run.

## Stage 3 results (run 2026-10-28 18:25 NZDT, commit `3164e1a`)

Command: `RAYON_NUM_THREADS=3 sh experiments/active/2026-10-wall-vs-memory/scripts/run_stage3.sh`, then
`uv run --frozen python experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3.py`. Provenance
(clean tree, probe sha256 `92aacf01...`, CSV sha256 `c5978b24...`) in `results/stage3_provenance.txt`;
per-run fits `results/stage3_runs.csv`; scored output `results/stage3_analysis.txt`. 18 runs, 10 s.

**Gates: T0 and T1 pass** (T1: every `ft:RULE:R` row equals the Stage 1 `hy:RULE:0:0:0` row in all fields).

| rule | ant (R) early / late a | forced L early / late a | reversal U early / late a |
|---|---|---|---|
| `RLRLLRRLRLR` | 0.690 / 0.678 | **highway**, escaped by 2^17 | 0.699 / 0.678 |
| `RLRLLRRRRRRR` | 0.675 / 0.662 | **highway**, escaped by 2^17 (same trajectory as the row above) | 0.649 / 0.681 |
| `RRLLLRLRRRLL` | 0.670 / 0.694 | 0.691 / 0.695 | 0.700 / 0.698 |
| `RRLLRLLRLR` | 0.705 / 0.665 | 0.717 / 0.679 | 0.704 / 0.703 |
| `RRRLLLLR` | 0.591 / 0.592 | 0.611 / 0.566 | 0.698 / 0.700 |
| `RRRRLLLLLLLR` | 0.646 / 0.702 | 0.777 / 0.664 | **highway** (3 cells wide), escaped by 2^15 |

Every run with a complete early window is compact (early beta 0.51-0.57), and every complete late
window has late a <= 0.74.

- **Arm L: split** (compact 4/6; 2 escaped). **Arm U: compact** (5/6; 1 escaped).
- **Registered reading: none** (arm L is split). F-a's side prediction (forced L within 0.05 of the
  ant in >= 5/6) **failed**: 3/6, partly because two runs never reached the window. U's side
  prediction (>= 4/6 within 0.05) held at exactly 4/6.
- **Escapes were not a named class.** The registration anticipated cycles that stall but not
  early highways. Each escaped run has area linear in t, constant width (U) or w = h (L)
  from k <= 12, and leaves the 16384 board by 2^15-2^17 steps. The scorer committed before the run
  counts "no early fit" as not compact, which is the right call for a highway, but I note that
  the class was not registered. The two forced-L highways are byte-identical rows: presumably
  neither ant read a colour past their shared prefix `RLRLLRR` before locking in (inferred, not checked).

Post hoc, descriptive (not registered):
- The six rules were drawn from the core class *under their own fresh turn R* (blob, not
  bursty, no highway), so the R arm cannot build a highway by selection, while L and U are new
  dynamics with no such filter. Base rate: 7% of canonical rules of length 8-12 have a highway
  onset before 4096 steps (`experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv`, 268 of 3963). Three early
  highways in 12 non-identity runs, two of them one trajectory, is not out of line with that.
- Among the runs that stayed bounded, reversal's late a clusters tightly: 0.692 (sd 0.012, n = 5)
  against the six ants' 0.665 (sd 0.039). The slowest ant, `RRRLLLLR` (0.592), moves to 0.700
  under U.

Interpretation (mine; post hoc where it goes beyond the registered table). Taken one arm at a time,
the U result contradicts the U predictions of H-chiral and H-match in 5 of 6 rules: a walker
that never curls on fresh ground, and whose fresh turn matches neither the rule's colour-0 turn
nor any chirality, still grows compactly with a ~ 0.70 whenever it does not lock into a highway.
But H-bound as registered ("any bounded policy keeps growth compact") is contradicted too, by
3 escapes in 12 runs. What survives: **bounded fresh excursions are compatible with compact
growth in every non-highway run here, and need neither chirality nor a match with colour 0;
boundedness does not prevent highways**, which compete as they do for ordinary rules. This
narrows Stage 1's "the fresh turn matters": what F1 destroys is plausibly the bound on fresh
runs, not the R. It is six rules, one class, finite windows; Stage 3b tests it on new rules.

## Stage 3b: fresh-turn policies on a new cohort (registered 2026-10-28 19:05 NZDT, before any run)

Base commit `ad29f506`. **Informed by Stage 3 and says so**: the predictions below were written
after seeing six rules. This stage asks whether Stage 3's surviving statement holds with power on
rules that played no part in forming it.

Cohort: 100 rules drawn uniformly without replacement (numpy `default_rng(20261028)`, from the
core class sorted by rule string, with the six Stage 1 rules removed first; core class as Stage 1:
cls blob, 0.30 < alpha_w < 0.37, not bursty, 2404 rules, all turning R on colour 0). Arms R, L, U
of `ft:RULE:T`, one deterministic run each: 300 specs in `results/stage3b_specs.txt`, made by
`scripts/select_stage3b.py`. Instrument, windows and fits as Stage 1 and 3 (`probe 27 16384`).

Classes per run (named before running):
- **escape**: the run leaves the board before completing the early window (`k = 12..22`);
- **stalled**: as Stage 3;
- otherwise Stage 1's `classify()` on the early window: compact / intermediate / porous.

Gate T2 (instrument and selection, not a hypothesis): no R-arm run escapes, and >= 90 of 100 R
runs are compact. If it fails, the arms are reported but not scored.

Primary measure per arm (L and U): f = compact / (runs that are not escapes), with a Wilson 95%
interval; escape rates reported separately with Wilson intervals.

Reading:
- f_L >= 0.90 and f_U >= 0.90: **bounded fresh runs suffice whenever no highway forms** (the
  weak H-bound of Stage 3) survives on a new cohort.
- f_L >= 0.90 and f_U <= 0.50: H-chiral.
- f_L <= 0.50 and f_U <= 0.50: H-match.
- anything else: unresolved or rule-dependent, reported as such.

Predictions (mine, after Stage 3): weak H-bound, about 70%. Escape rate per arm between 2% and 20%
(census base rate of highway onsets before 4096 steps is 7%; this horizon is longer). Second,
from the Stage 3 post hoc observation (registered now, so this is its first test): among rules
where both the R and U runs complete the late window, the between-rule sd of late a is smaller
under U than under R, with a rule-bootstrap (10,000 resamples, seed 20261028, rules sorted
before resampling) 95% interval of sd_U / sd_R entirely below 1; about 60%. And mean late a under
U in [0.67, 0.72].

Scorer `scripts/analyse_stage3b.py` and runner `scripts/run_stage3b.sh`, committed before the run.
Pruning preflight: same index revision content as Stage 3 (no entries added since `4fd558b`);
the new rules are not members of any entry (`NR-20261026` covers only `hy:RULE:0:1:SEED`
specs); decision **run**. Budget: 300 runs of 2^27 steps, a few minutes on 4 cores. No
extension without a new registration.

## Stage 3b results (run 2026-10-28 18:29-18:32 NZDT, commit `383fe4c`)

Command: `RAYON_NUM_THREADS=3 sh experiments/active/2026-10-wall-vs-memory/scripts/run_stage3b.sh`, then
`uv run --frozen python experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3b.py`. Clean tree; probe sha256
`92aacf01...` (same binary as Stage 3); CSV sha256 `d2c77b0f...`; `results/stage3b_provenance.txt`,
`results/stage3b_runs.csv`, `results/stage3b_analysis.txt`. 300 runs in 3 min 16 s.

**Gate T2 passes** (R arm: 0 escapes, 99/100 compact; the one intermediate, `RRLRLLLLRLL`, has early
a 0.814 but late a 0.671, a slow transient).

| arm | compact | intermediate | escape | porous | f = compact / non-escape (Wilson 95%) | escape rate (Wilson 95%) |
|---|---|---|---|---|---|---|
| R (the ants) | 99 | 1 | 0 | 0 | 0.990 | 0 |
| L (forced L) | 78 | 13 | 9 | 0 | **0.857 [0.771, 0.915]** | 0.09 [0.05, 0.16] |
| U (reversal) | 63 | 0 | 37 | 0 | **1.000 [0.943, 1.000]** | **0.37 [0.28, 0.47]** |

- **Registered reading: unresolved** (f_L = 0.857 falls between the 0.50 and 0.90 bands).
- **H-chiral and H-match are rejected by the U arm**: both predicted f_U <= 0.50; observed 63/63 compact,
  interval [0.94, 1.00]. A walker whose fresh-ground turn has no handedness and does not match colour 0
  grows compactly in every run that stays on the board.
- Escape-rate prediction (2-20% per arm): held for L (9%), **failed for U (37%)**. Reversal makes
  early highways far more common than the census base rate.
- Late-a spread (registered from the Stage 3 post hoc observation): sd_U / sd_R = 0.725, rule bootstrap
  95% [0.556, 0.958], **held** (n = 60 rules with both late windows); U mean late a 0.687, in [0.67, 0.72],
  **held**. The effect is weaker than the six-rule hint (0.31 there), as one would expect of a pattern
  noticed in a small sample.
- Distinct trajectories: R 99, L 98, U 86 of 100 (rules sharing a prefix can coincide when an ordered
  structure forms before longer colours are read).

Post hoc, descriptive (not registered): **the 13 "intermediate" L runs are ordered fillers, not
porous walks.** Early a 0.94-1.15, beta 0.50-0.57; late a ~1; area grows at a constant rate with A/t
settling to 1/10, 1/8, 1/6 (five rules), 1/4 (three rules), and two non-rational-looking values (0.150, 0.083), the
territory a solid square in 10 of 13 (w/h = 1.00, perimeter = 2(w + h)), a 2:1 rectangle in one and
an octagon-like shape (perimeter / 2(w + h) = 0.76) in two that share a trajectory. These are the
square-ring / square-spiral fillers known from the census (`notes/proof-track-2026-10-20.md`,
`experiments/archive/2026-10-square-ring-fillers/`), here produced by the forced-L policy. Treating fillers like
highways (ordered structures, not growth regimes) would give f_L = 78/78, but that class was not
registered, so it does not change the score.

Interpretation (mine; it goes beyond the registered table and is labelled as such). Across 300
deterministic bounded-fresh-run walkers, **no run is porous**. Every run either locks into an ordered
structure (a highway or a filler) or grows compactly with early a ~ 0.69-0.70 and beta ~ 0.55. That is
a dichotomy: *bounded fresh runs + no crystallisation => compact growth near the cube root*. The fresh
turn's handedness and its match with colour 0 decide only which ordered structures are likely (U:
highways; L: highways and fillers; R: neither, by the selection of this cohort). This reading predicts
something Stage 1 could not separate: F1 (random R/L on fresh cells) was porous because its fresh
runs are *unbounded*, not because they are random. Stage 3c tests exactly that.

## Stage 3c: random but bounded fresh turns (registered 2026-10-28 19:30 NZDT, before any code or run)

Base commit `9f8a06aa`. Informed by Stages 3 and 3b, and says so. Question: was F1 porous because its
fresh turns were **random** or because its fresh runs were **unbounded**? Stage 1 could not tell:
random R/L does both.

Walker `fs:RULE:SET:SEED`: the ant `RULE`, except that on a fresh (never departed) cell the turn is
drawn uniformly from `SET` (letters from R, L, U; U a reversal). One SplitMix64 draw per step,
seeded by SEED, consumed on every step as in `hy:`; on a fresh cell the high 32 bits pick
`SET[(high32 * |SET|) >> 32]`. With `SET = RL` this is exactly F1, `hy:RULE:0:1:SEED`, step for step
(gate T3).

Exact properties (by construction; checked by the oracle test):
- `RU`, `LU`: **bounded**. A U steps straight back onto the cell just departed; a run of equal quarter
  turns closes a 2x2 block within 4 cells. So a fresh run has at most 4 cells (5 for the run that
  starts at the origin, whose U has no departed predecessor), whatever the draws.
- `RL`, `RLU`: **unbounded**. Alternating R and L draws make a staircase into fresh ground, with
  probability > 0 for every length.

Explanations:
- **H-bound (the Stage 3b dichotomy).** Bounded fresh runs and no crystallisation give compact growth;
  randomness on fresh ground is harmless if runs stay bounded. Predicts: `RU` and `LU` compact;
  `RLU` porous like F1.
- **H-random.** Randomising the fresh turn breaks the compact regime by itself (for example by
  breaking first-visit correlations with the colour field), whatever the bound. Predicts: `RU` and
  `LU` not compact.

Cohorts and specs (`results/stage3c_specs.txt`, made by `scripts/select_stage3c.py`):
- **A**: the six Stage 1 rules x the eight Stage 1 seeds 2026102601..08, arms `RU`, `LU`, `RLU`
  (144 runs), directly comparable with F1 (`hy:RULE:0:1:SEED`, committed in `results/probe.csv`).
- **B**: the 100 Stage 3b rules x one seed 2026102801, arms `RU` and `RLU` (200 runs).
- Gate T3 specs: `fs:RULE:RL:2026102601` for the six Stage 1 rules (6 runs), compared field for field
  with the committed `hy:RULE:0:1:2026102601` rows.

Classes per run (all named before running): escape, stalled (as Stage 3b), **filler** (added now from
the Stage 3b post hoc finding: early a >= 0.90, early beta <= 0.62, and A/t over the last three
windows within 3% of their mean), then Stage 1's `classify()`.

Primary measure per (cohort, arm): f = compact / (runs that are neither escape nor filler), Wilson 95%;
and p = porous / (same denominator).

Reading (each cohort scored separately; A by runs, with rules as the independent units noted):
- `RU` (and in A also `LU`) f >= 0.90 and `RLU` p >= 0.50: **H-bound** supported.
- `RU` (and `LU`) f <= 0.50: **H-random** supported.
- Anything else, or the cohorts disagree: unresolved.

Side predictions (mine): in A, condition-mean early a for `RU` <= 0.78 in >= 5 of 6 rules; escape rate
under `RU` below 5% in both cohorts (random fresh turns should rarely sustain a highway's leading
edge); `RLU` porous fraction p >= 0.7 in both cohorts (F1 run-level porous was 39/48 = 0.81).

**Priors:** H-bound about 65%, H-random about 25%, unresolved 10%. Against H-bound: random fresh
turns add noise exactly where the ant's trajectory first meets new ground, which Stage 1 showed is
where the regime is decided; for example the colour pattern laid at the edge may matter, not just
how far the walker goes.

Gates: T0' (`cargo test --release --locked --test fresh_set` passes: sparse reference, the bound for
`RU`/`LU`, an unbounded run observed for `RLU`), T3 (above). Pruning preflight: no entries added since
`4fd558b`; `NR-20261026` covers exactly the `hy:RULE:0:1:SEED` specs (F1); the `fs:` arms other than
the T3 gate are not members, and the T3 gate is a deliberate replication of six F1 specs as an
identity check. Decision **run**. Budget: 350 runs of 2^27 steps on 3-4 cores (minutes). No extension
without a new registration.

## Stage 3c results (run 2026-10-28 18:37-18:41 NZDT, commit `3d13c18`)

Command: `RAYON_NUM_THREADS=3 sh experiments/active/2026-10-wall-vs-memory/scripts/run_stage3c.sh`, then
`uv run --frozen python experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3c.py`. Probe sha256 `a0615a05...`,
CSV sha256 `29fa44d8...` (`results/stage3c_provenance.txt`). The provenance records 2 dirty tracked files:
uncommitted fixes to two Python scripts in *other* experiments (`a7_census.py`, `a5_home_types.py`), which
the probe binary does not read; the Rust sources were committed (`3d13c18`). 350 runs in 4 min 16 s.

**Gates T0' and T3 pass** (T3: all six `fs:RULE:RL:2026102601` rows equal F1's `hy:RULE:0:1:2026102601`).

| cohort, set | fresh runs | compact | intermediate | porous | f (Wilson 95%) | p (Wilson 95%) | mean early a / beta |
|---|---|---|---|---|---|---|---|
| A, `RU` (48) | bounded, random | 47 | 1 | 0 | 0.979 [0.891, 0.996] | 0 | 0.721 / 0.60 |
| A, `LU` (48) | bounded, random | 42 | 6 | 0 | 0.875 [0.753, 0.941] | 0 | 0.736 / 0.61 |
| A, `RLU` (48) | unbounded, random | 1 | 29 | 18 | 0.021 | 0.375 [0.252, 0.516] | 0.851 / 0.79 |
| B, `RU` (100) | bounded, random | 86 | 13 | 1 | 0.860 [0.779, 0.915] | 0.010 | 0.737 / 0.61 |
| B, `RLU` (100) | unbounded, random | 1 | 44 | 55 | 0.010 | 0.550 [0.452, 0.644] | 0.858 / 0.81 |

No run escaped and none was a filler or stalled. Cohort A condition means (early a; ant / F1 / RU / LU / RLU):
`RLRLLRRLRLR` 0.690 / 0.883 / 0.729 / 0.783 / 0.889; `RLRLLRRRRRRR` 0.675 / 0.861 / 0.683 / 0.739 / 0.834;
`RRLLLRLRRRLL` 0.670 / 0.869 / 0.721 / 0.737 / 0.860; `RRLLRLLRLR` 0.705 / 0.906 / 0.732 / 0.744 / 0.864;
`RRRLLLLR` 0.591 / 0.877 / 0.745 / 0.719 / 0.841; `RRRRLLLLLLLR` 0.646 / 0.867 / 0.719 / 0.696 / 0.816.

- **Registered reading: unresolved in both cohorts.** A: `RU` 0.979 and `LU` 0.875 (below 0.90), `RLU` p
  0.375 (below 0.50). B: `RU` f 0.860 (below 0.90). Each cohort misses an H-bound threshold.
- **H-random is rejected**: it predicted f <= 0.50 for the bounded sets; observed 0.86-0.98, every
  interval's lower end at or above 0.75.
- Side predictions: `RU` condition-mean early a <= 0.78 in 6/6 rules, **held**; `RU` escape rate < 5% in
  both cohorts (0/48, 0/100), **held**; `RLU` p >= 0.7, **failed** in both (0.375, 0.550).

What the misses are. The non-compact bounded runs are mostly *intermediate, near the compact edge*
(early a 0.77-0.86, beta about 0.66-0.69, late a about 0.74), not porous: 1 porous run in 196. `RLU` is
less porous than F1 (A: 18/48 against F1's 39/48 run-level) and most of its non-porous runs are
intermediate with early a 0.78-0.89 (U draws cut a third of the staircase steps short, so its fresh
runs are unbounded but shorter than F1's).

Post hoc, descriptive: bounded randomness is not free. In cohort B, `RU` early a exceeds the same rule's
deterministic ant by 0.056 on average (sd 0.040, n = 100), with beta 0.60-0.61 against the ants' 0.55;
late a about 0.71 against 0.68. That is the size of V1's finite-window offset from the rotor in Stage 2
(+0.05), which also keeps a bound (forced R) and randomises elsewhere.

Interpretation (mine; beyond the registered reading). Stages 3-3c together:

| fresh-ground policy | fresh runs | compact | porous |
|---|---|---|---|
| deterministic R / L / U (3, 3b) | bounded | every non-ordered run (1 slow transient) | 0 of 318 |
| random from {R, U} or {L, U} (3c) | bounded | 175 of 196 | 1 of 196 |
| random from {R, L, U} (3c) | unbounded | 2 of 148 | 73 of 148 |
| random from {R, L} (F1, Stage 1) | unbounded | 0 of 48 condition-level | 39 of 48 runs |

The bound on fresh runs separates compact from porous growth far more sharply than chirality,
the match with colour 0, or randomness. Randomness and the particular turn tune the exponent by a
few hundredths and decide which ordered structures appear. This is the mechanism H-wall named in
Stage 1 ("forced R on a fresh cell bounds penetration into fresh ground"), now tested against
alternatives that Stage 1 could not separate. It is still a finite-window, core-class result: it
does not say why the bounded regime's exponent is near 2/3 rather than 0.70-0.74, and the
registered thresholds were not met cleanly.
