# Wall or memory: where does the ant's cube root live?

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
  porous territory (a 0.920, beta 0.909, `experiments/2026-10-19-kappa-walker-reference/`);
- the rotor and the ant both reach a ~ 2/3 with compact territories;
- turn noise applied on every step raises the ant's area exponent smoothly,
  0.70 at eps <= 0.01, 0.76 at 0.1, 0.89 at 0.5 (`experiments/2026-10-13-d3-noise/results/d3_stats.txt`).
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
Per run, exactly as `experiments/2026-10-19-kappa-walker-reference/scripts/analyse.py`:
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
  (`experiments/2026-10-13-probe-growth-census/results/probe_summary.csv`, window
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

A finite-window exponent (2^27 steps at most, early window ending at 2^23) is
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
  predicate `Pi(k)` (`experiments/2026-10-25-square-ring-fillers/scripts/ring.py`).
  `RRRLLLLR` has census a 0.592, c 0.197, the slowest of the six; it stays in, as drawn.
- Budget: one run of the 270 specs, `RAYON_NUM_THREADS` set to the cores
  available, expected well under an hour on 4 cores. No extension (longer runs,
  more rules, other Q or P) without a new dated registration here.

This experiment departs from the ordered sequence in `notes/ACTIVE.md`
(boundary-access discrimination first). It is a cheap ablation chosen by the
project owner; it does not replace that sequence.

## Reproduction

```sh
uv run --frozen experiments/2026-10-26-wall-vs-memory/scripts/select_rules.py
cargo test --release --locked --test hybrid_walker
sh experiments/2026-10-26-wall-vs-memory/scripts/run.sh
uv run --frozen experiments/2026-10-26-wall-vs-memory/scripts/analyse.py
```

`run.sh` builds `probe` into a fresh `CARGO_TARGET_DIR`, records the commit and
binary sha256, and writes `results/probe.csv`, `results/probe.log` and
`results/run.done`.

## Results, uncertainty and limitations

Not run yet.

## Pruning-index outcome and next question

Pending the run.

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
  **necessary** for the compact cube-root regime in all six rules.
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
- **Post hoc, descriptive:** the contrast between EF = 0.1 (little effect) and
  EF = 1 (porous in every rule) says the wall tolerates occasional leaks. With
  EF = 0.1 a fresh cell turns L only 5% of the time.

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
