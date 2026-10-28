# Frontier results (append-only log)

Conventions: each item section has **Hypothesis** (timestamped before the run),
**Result**, **Reproduce**. Environment: WSL, `CARGO_TARGET_DIR=~/turmite-target-frontier`,
`RAYON_NUM_THREADS=3`, uncommitted tree on HEAD bbaa8c8.

## Item 23: rule equivalences

**Hypothesis** (2026-10-12, before running). Mirror (L<->R) is the only
symmetry used (`is_canonical` = starts with R) and it is exact (x-reflected
trajectory). Cyclic rotation of colours is not a symmetry (the blank colour is
0). Prediction: no two canonical rules give identical trajectories, EXCEPT
repeated rules u^k, which should be identical to u (colour matters only mod
|u|). Falsifier: any other collision within 2e4 steps is a bug or an
unreached-colour effect. Not excluded by `is_canonical`, so the census may
double count.

**Result.** Mirror: 0 mismatches over all 502 canonical non-trivial rules of
length 2..9 (2e4 steps, `examples/equiv.rs`). Repeats u^k collide exactly with u
(RL=RLRL=RLRLRL..., RLL=RLLRLL, ...). Other collisions at 2e4 steps (e.g. RRL
= RRLRRLL = RRLRRLR ...) are all highway builders whose cells never reach the
extra colours; these are prefix-equivalent only for a finite horizon (confirm
by running longer: they diverge iff some cell reaches colour |u|... see
below). Census (`experiments/archive/2026-10-census-sweeps/results/census.csv`, 3512 rules): 52 are exact repeats (39
blob, 2 builder, 11 log), 1.5%; dropping them moves the blob median
exponent 0.3322 -> 0.3321 (no effect), and the repeats' alpha equals their
root's bitwise. Added `Rule::root`/`is_primitive` and `tests/equiv.rs`
(proptest, repeat == root step-for-step).

**Reproduce.** `cargo run --release --example equiv -- 2 9 20000`;
`uv run experiments/archive/2026-10-census-sweeps/scripts/equiv_census.py`; `cargo test --release --test equiv`.

## Items 18, 19, 20 (and the data side of 17): highway onset, catalogue, chaos vs highway

**Hypotheses** (2026-10-12, written before analysing `sweep_v2.csv`,
`sweep_1B.csv`, `confirmed_v2.csv`; I have only looked at row counts and
column names). Data: rules of length 2..12, budget 1e8 steps (v2); the 854
rules of length <=10 still unresolved were rerun to 1e9 (`sweep_1B`).

- H18. Onset time T of highway builders is heavy tailed: the number of rules
  with onset in each decade of T does not decay quickly. Prediction: among
  length<=10 rules the count per decade of onset between 1e4 and 1e9 declines
  by less than a factor 2 per decade (tail P(T>t) ~ t^-g with g < 0.3).
  Falsifier: counts fall by >= 3x per decade (thin tail; the unresolved set is
  then almost all genuinely chaotic). Consequence to compute: expected number
  of the remaining unresolved rules that are late highways.
- H19. Highway displacement is constrained. Predictions: |dx|=|dy| (diagonal)
  for most highways; period correlates positively with rule length (Spearman
  > 0.3); (period, |d|) pairs cluster on few values; period even.
- H20. Chaos vs highway is only weakly predicted by simple rule statistics
  (#R, longest run, palindromic symmetry): cross-validated AUC < 0.75.
  Falsifier: AUC > 0.9.

### Results (items 18-20) -- `uv run experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/scripts/highway_stats.py` > `experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/highway_stats.txt`

Population: primitive rules (repeats of shorter rules removed, item 23).
Caution found on the way: of the 28 `escaped` rows in `sweep_1B.csv`, 16 have
no period/onset and widths ~16380: they are *chaotic blobs that hit the
16384 grid* around 5.4e8 steps (fast growers), not highways. Only rows with an
onset are counted as highways below.

- **H18 supported (heavy tail).** Highway onsets for length<=10 (v2 + 1B),
  counts per decade 1e3..1e9: 17, 14, 17, 26, 11, 11 (log10 slope -0.011 per
  decade, i.e. no decay detectable). 12 of the 854 survivors at 1e8 became
  highways in 1e8..1e9 (1.4%); latest onset 9.0e8. So the unresolved set is
  not "almost all chaotic": ~1% of survivors convert per decade, and a thin tail
  would have predicted a fall by >=3x per decade. Caveats: small counts
  (Poisson sd ~ 3-5 per decade, so a factor-1.5 decay per decade is not
  excluded); the 1e8..1e9 decade covers length<=10 only. Onset is "start of the
  final periodic tail", measured retrospectively. Item 17 extends this one
  more decade (below).
- **H19 mixed.** 555 confirmed primitive highways: diagonal
  (|dx|=|dy|) 95.7% (predicted majority: yes); period always even (100%;
  forced: net heading change must be 0 mod 4, which needs an even number of
  turns) and dx+dy always even (parity of steps); period mod 4 is 0 (349) or 2
  (206). The prediction "period grows with n" is FALSIFIED: Spearman(period, n)
  = -0.013 and period quantiles (10/50/90%) are the same for every n
  (e.g. 18/112/484 at n=8, 18/132/580 at n=12). Period 18 (displacement
  (1,1); the RRL family) is 22.5% of all highways; 171 distinct periods and 188
  distinct (period,|d|) classes among 555 rules, so not "few values" beyond the
  period-18 spike. Speed |d|max/period: median 0.015, max 0.056 (= 1/18 ).
- **H20 held.** CV AUC of a logistic model on length, #R, fraction R,
  longest run, flips, (anti)palindrome, R's in first positions: 0.698
  (single-feature best 0.64: R in positions 1-2). So simple rule statistics
  carry only weak information; more R means more chaos-to-highway, not less.
  Not fitted beyond logistic; a richer model could do better (limit stated).
  Rules the model finds least plausible as highways (but are): RLLLLRLLLRLL,
  RRLRRLLLLLLL, RLRLLLLLRLLR; chaotic rules it finds most highway-like:
  RRRRLRRLRRRR, RRRLRRR, RRRLLRRR. These are candidates for hand study.

### Item 17 pilot design

`experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e10.sh` reruns the primitive survivors at 1e9 to 1e10 steps (grid
32768, resumable chunks in `experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/`). Prediction (H17, written
2026-10-12 before it finishes): if the onset tail is flat as H18 says,
about 1% of survivors (around 6-10 of ~800) become highways in 1e9..1e10; a
thin tail would give <= 3. Results to be appended below when finished.

## Item 8: edge exponent beta = 0.52

**Hypothesis** (2026-10-12, before running `experiments/archive/2026-10-edge-statistics/scripts/edge_exponent.py`). Calibration
says 0.52 is finite time for both rotor and ants. Prediction: local slope of
log P vs log A (octaves k..k+4) drifts down monotonically toward 0.5 for the
six rules run to 2^32 and is within 0.01 of 0.5 at k>=26; a model
P = c1 sqrt(A) + c0 fits all octaves k>=17 better than a free exponent
(residual of the offset model <= free-exponent residual). Falsifier: local
slope plateaus above 0.51 or the offset model is clearly worse.

**Result** (`experiments/archive/2026-10-edge-statistics/results/edge_exponent.txt`, six long ants + 64 rotors). Partly
supported, not decisive. Mean local slope (4-octave windows) across the six
ants: 0.544 (k14), 0.545 (k18), 0.527 (k20), 0.547 (k22), 0.523 (k24),
0.510 (k26), 0.522 (k28): a downward drift toward 0.5, but with per-window
scatter ~0.03 per rule (individual rules go 0.51 -> 0.53 -> 0.51). The
rotor drifts smoothly 0.63 (k10) -> 0.55 (k16-18) -> 0.52 (k22), the same
pattern. The stated falsifier (plateau above 0.51 or offset model clearly
worse) is not triggered, but "within 0.01 of 0.5 at k>=26" fails (0.510 and
0.522 means; per-rule up to 0.534). The offset model P = c1 sqrt(A) + c0
fits better than a free exponent for 3 of 6 ants and worse for 3 (rms
log-residuals 0.018-0.035, dominated by octave-to-octave perimeter
fluctuations, not by the trend); it cannot discriminate. RLR (a rule with a
low-fill, odd-shaped territory) is the exception: free beta = 0.57 over
k>=17 and 0.548 at k28, so it has not converged by 2^32. Conclusion to carry
into claims: "0.52 is consistent with a finite-time approach to 0.5 and the
rotor does the same" is supported; "converges to exactly 0.5" is not
established. Decisive data would need many more octaves or an ensemble average
over patched starts (item 4 provides such an ensemble).
Reproduce: `uv run experiments/archive/2026-10-edge-statistics/scripts/edge_exponent.py`.

## Item 4: is the exponent exactly 1/3 for every chaotic rule?

**Hypothesis** (2026-10-12, before the run). H4: all chaotic (blob) rules share
one asymptotic area exponent 2/3 (width 1/3); the residual between-rule spread
in fitted exponents (sd 0.004-0.014 true, Part C) is a convergence-rate effect.
Design: 11 primitive core rules (stratified by length 3..12 and by census
width exponent; `experiments/archive/2026-10-item4-exponent-rotor-calibrated/scripts/item4_select.py`), 24 random 5x5 starting patches each
(seeds 1..24, `RULE@SEED`), 2^30 steps, octave probe output
(`experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_probe.csv`). Per rule, ensemble-average the local area exponent
a(k) = d log A / d log t over 3-octave windows and fit
a(k) = a_inf + b * 2^(-k/3) (correction ~ 1/width, delta fixed 1/3; also
delta free as a check). Predictions: (i) a_inf within 2 SE of 2/3 for >= 9 of
11 rules; (ii) between-rule sd of a_inf, after subtracting SEs, < 0.01;
(iii) |b| differs between rules, correlating with the 2^27-window exponent
deviation (a - 2/3), i.e. fast and slow looking rules are early-time
transients. Falsifier: two or more rules with a_inf differing from 2/3 by
> 0.02 and > 4 SE, or a(k) flat at a value != 2/3 over k=22..29 for some
rule. Caveat to report regardless: the correction form is an assumption;
a_inf estimates are model-dependent, so also report raw a(k) at k=27..29.

## Items 5 and 7: limit shape and boundary width of ant territories

**Hypotheses** (2026-10-12, before running `examples/shape.rs`; area `A`
cross-checked against `probe` for RLR at 2^14..2^22: identical). Statistics
per checkpoint t=2^k (k=12,14,...): anisotropy of the visited set, angular
harmonics h2/h4/h8 of the outermost-visited-radius profile (128 bins, about the
centroid), K&D boundary width `Wsurf` (sd of surface-cell radius about the
centroid), and at the last checkpoint the radial visit-density profile in
units t/A and shell width 0.075 R_eq. Rotor = calibration (40 seeds, 2^26);
ants = 11 core rules from `experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_rules.txt` x 8 patched seeds, 2^28.
- P5a. Rotor shape converges to a disc: median h2, h4, aniso fall with k.
  Ants: median aniso at 2^28 below 0.1 and h4 below 0.05 for most rules
  (a chaotic territory is statistically round, lattice anisotropy washes out).
- P5b. Seed-to-seed CV of A/t^(2/3) falls from 2^16 to 2^28 by a factor >= 2
  for >= 9 of 11 rules (a deterministic coefficient, like the rotor's 8.9% ->
  1.8% in 1e4 -> 1e7).
- P5c. After scaling radius by R_eq, the visit-density profile collapses across
  rules (relative sd across rules < 0.2 at 0.5 R_eq) but differs from the
  rotor's (centre value ~2.7 t/A for the rotor).
- P7. Ant boundary width scales as W ~ A^(delta/..): local exponent of W vs t
  between 0.1 and 0.2 for ants (same ballpark as the rotor's drift
  0.19 -> 0.13 to K&D's 0.136), i.e. a sub-linear, slowly growing width. Falsifier: local
  exponent > 0.25 (width proportional to R: a fuzzy, non-self-averaging edge)
  or < 0.05 consistently for k in 20..28.

## Items 29 and 28 (literature part)

**Hypothesis** (2026-10-12). The frontier note's rotor exponent in d
dimensions, radius ~ t^(1/(d+1)) (range ~ t^(d/(d+1))), is correct as a
rigorous *lower* bound for Eulerian walks; the exponent for ants is not
implied by it.

**Checked (WebSearch/WebFetch 2026-10-12; abstracts only, I did not read the proofs).**
- Bou-Rabee & Peres, arXiv:2608.23545 (24 Aug 2026), "Eulerian walkers on
  Z^2 have range exponent 2/3": proves the PDDK 1996 conjecture (radius of
  order t^(1/3) for i.i.d. uniform initial arrows), that every site is visited
  infinitely often, and that the region rescaled by t^(1/3) converges to a
  **convex body**. They do not claim a disc: that is Kapri & Dhar's
  numerical statement (arXiv:0906.5506, who also give boundary-width exponent
  alpha/3 with alpha = 0.40 +- 0.06, i.e. delta ~ 0.13).
- Lower bound range >= c t^(d/(d+1)) for Eulerian graphs periodically
  embedded in R^d: "The range of a rotor walk" (arXiv:1408.5533).
  Hence radius t^(1/(d+1)): the frontier note's formula is confirmed as a
  lower bound; whether it is tight for d>=3 I did not find. For d=3 the
  prediction is radius t^(1/4), area-analogue t^(3/4).
- Correction to my earlier reading of the calibration note: B-R&P prove
  convexity, not isotropy; our measurement (below) of aniso/h4 tests the
  disc claim numerically.

**What a proof for ants could and could not reuse.** (i) The rotor walk is a
function of the *site* state only: the outgoing direction depends on the
arrow, not on the incoming heading. The ant turns relative to its heading,
so it is reversible (`Ant::unstep`) and the rotor router's monotone/abelian
structure (the machinery for Eulerian lower bounds) does not apply directly.
(ii) In a rotor interior every site is 4-periodic (visit counts are multiples
of 4 in each completed sweep: measured 89% exactly 4 in the last 4S steps);
for ants the colour cycle has length n but the heading-dependent exit means a
cell's n visits do not return the ant to a fixed pattern: the analogous
statistic is measured in item 6. (iii) The ant's edge-entry and edge-occupancy
factors c, kappa (paper) correspond to the rotor's, but the rotor's constants
(c ~ 0.50, kappa ~ 2) are tied to the exact 4-periodicity. Left open: no proof
of any t^(1/3) result for a non-Eulerian reversible walker is known to me.

## Item 6: can a chaotic ant be reduced to a rotor-like walker? (pilot)

**Hypothesis** (2026-10-12, before `examples/lastvisits.rs` runs). The rotor
interior is 4-periodic: 89% of interior sites get exactly 4 visits in a window
of 4A steps. If an ant could be mapped onto a rotor with an effective
n-fold cycle, the ant analogue would show a *peaked* distribution of window
visits at m = n (window n*A) with fraction > 0.5. Competing: the ant's
heading-dependent exit means visits are not locked to n, giving a broad
(Poisson-like) distribution with exact-m fraction < 0.25. Prediction: the
rotor reproduces ~0.89 (calibration); for ants the exact-m fraction is below
0.4 for every tested rule (no exact reduction in this sense). Falsifier: any
chaotic ant with exact-n fraction > 0.5, which would be a lead for a reduction.
Limit: this tests one observable; failure to find a peak does not rule out a
different coupling, so this is a pilot, not a negative theorem.

**Result** (`experiments/archive/2026-10-misc-instruments/results/lastvisits.txt`; `cargo run --release --example lastvisits -- 22 rotor:1 ... RLR RLL ...`;
T = 2^22 then consecutive windows of m*A steps, interior = cell and its 4
neighbours visited before the window). Rotor: exactly-4 fraction 0.918-0.932
(4 runs; K&D-style definition gave 0.893, mine counts interior only),
the calibration passes. Ants (7 rules, windows m=4 and m=n): exactly-m
fraction 0.025-0.072, i.e. no peak at n; the distribution is broad and has a
large mass at **zero** visits: 32%-69% of interior cells are not visited at
all in a window of 4A steps (Poisson with mean 4 would give 1.8%). So the ant is
far from uniformly sweeping its interior on the timescale of 4A steps
(overdispersed, intermittent: the same cells are revisited in bursts).
Prediction (exact-m fraction < 0.4 for all tested rules) held; no lead for
an exact rotor reduction of this kind. Side finding to follow up: this
overdispersion contrasts with the well-mixed assumption of the cup picture, which
only needs mixing on the timescale of growth (R^2/D << t; paper Mixing
paragraph, ratio ~ 0.002), so the two are not in contradiction, but the
distribution of window visits (a clustering, not a sweep) is a statistic the
cup picture does not predict. Limits: 7 rules, 1 age, one observable.

## Item 3 (P2.1): letters that set c

**Hypothesis** (2026-10-12, before `experiments/archive/2026-10-probe-growth-census/scripts/c_letters.py`). c depends on rule[1],
rule[2] much more than later letters (H2). Prediction: among core blob rules
(n>=8, primitive) a linear model on letters 1-2 alone has R^2 >= 2/3 of the
R^2 of letters 1-5, and letters 3-5 alone have R^2 < 0.05. Falsifier: letters 3-5
alone explain > 0.1.

**Result** (`experiments/archive/2026-10-probe-growth-census/results/c_letters.txt`, 2515 rules). P2.1 supported strongly. Letters 1-2
alone: R^2 = 0.747 (CV 0.747); letters 1-5: 0.789; letters 3-5 alone: 0.026;
letter 1 alone 0.578. Effect of R instead of L on c: -0.185 (letter 1), -0.104
(letter 2), -0.05 (letter 3), ~0 beyond. Fraction of R alone: R^2 = 0.159. So
the edge-entry probability is set almost entirely by how the ant turns on its
first two colours (young cells), as H2 says: R on young cells curls it back.
Direction matches the prediction that low colours turning like colour 0 (R)
lower c. Combined with the paper's held-out edge model (R^2 in the paper),
the answer to "why does c vary" is: first two letters. "Why c ~ 0.44 on average" remains the
mean of this letter distribution (not verified here: the census mean is about 0.44; I did not check whether letters 1-2 being
random reproduces it), so not a universal
constant, and the random walk's 0.44 is coincidence.
Items 1 (P1-P4: measured, paper) and 3 are closed with these additions; P5 is an
identity (paper table), the independent mechanism test is P2.1/P2.3 above and
the null of gamma drift.

## Items 24, 25, 26, 27, 28: extensions (hypotheses, written 2026-10-12 before any extension run)

Code: `src/ext.rs` (SqSim: multi-state turmite, many ants, turn noise, random
background; HexSim; CubeSim), driver `src/bin/ext.rs`, oracle tests
`tests/ext.rs` (HashMap versions; SqSim == `reference::Ant` step for step for
L/R rules; all pass). Sanity: RLR via the new simulator gives area 83628 at
2^22, identical to `probe`. The cup picture (A grows by c*kappa*P/A with P ~
A^((d-1)/d)) predicts for any lattice in d dimensions
V ~ t^(d/(d+1)), i.e. radius t^(1/(d+1)): d=2: area t^(2/3); d=3: volume
t^(3/4), radius t^(1/4). This matches the rotor's rigorous lower bound
(item 28 literature check).

- H24 (hex lattice). Chaotic hex ants (non-highway, non-bounded) have area
  exponent 2/3 within the rotor-calibrated window bias (0.667..0.70 over
  k=16..27); medians over rules in [0.65, 0.70]. Falsifier: median outside
  [0.62, 0.75].
- H28 (3D). Among cubic-lattice ants with 4 letters that neither build a
  highway nor stay bounded, the volume exponent is 3/4 (accept 0.72..0.80
  incl. window bias); radius exponent 1/4. Competing: 2/3 or 1 (ballistic).
- H25 (turmites). Among 2-state 2-colour turmites that grow at 2^22 without a
  highway (area exponent between 0.5 and 0.9 on k=16..22, extent growing),
  the exponent distribution clusters at 2/3 (>50% within 0.1) -- the cube root
  is not special to single-state LR ants. A second parameter is needed only if
  a distinct cluster appears (e.g. near 1/2 or near 1).
- H26a (random background). With i.i.d. uniform initial colours, the blank-cell
  wall is gone: radius exponent 0.5 +- 0.07, not 1/3 (so determinism alone
  does not give the cube root; the repelling blank ground does). Already seen
  in the smoke test: RLR with random background reaches extent 2189 at 2^22
  versus 361 for the blank board.
- H26b (turn noise eps). Two competing predictions. H_A: class changes: for t
  beyond t*(eps) ~ eps^-3 (radius sqrt(eps t) exceeds t^(1/3)) growth
  becomes diffusive (local exponent -> 1/2 radius); H_B: noise only adds an outward rate, the
  exponent stays 2/3 with a larger coefficient. Discriminator: local area
  exponent at k=24..28 for eps in {1e-4,1e-3,1e-2,1e-1}; H_A predicts exponent
  rising above 0.8 with onset k*(eps) shifting by 3 per decade/ (3.3 octaves per decade of eps...),
  H_B predicts a flat 0.67-0.70 for all eps.
- H27 (many ants). m ants sharing the board (RLR, RLL and 2 longer rules,
  m = 1, 2, 4, 8) keep area exponent 2/3 and collapse onto the one-ant curve in
  *total* steps: A_m(t) / A_1(m t) ~ constant between 0.5 and 2 for t over 6
  octaves. Falsifier: exponent differing by > 0.05, or the ratio drifting by
  more than a factor 1.5 over those octaves (interaction changes the class).

### Results: items 26 and 27 (`bash experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_specs_26_27.sh`; `uv run experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_stats.py` > `experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_stats.txt`)

- **H27 supported.** RLR, RLL, RLRLRRRLLR, RRRLR with m = 1, 2, 4, 8 ants
  (start 2 cells apart, deterministic): area exponent (k=18..26, per tick)
  0.67-0.74 for every (rule, m), i.e. unchanged within the single-ant
  spread; and A_m(t) / A_1(m t) stays within 0.87-1.23 over k=16..26 with no
  trend (last-octave ratios 0.93-1.06). So m ants on one board are, for area
  growth, one ant running m times faster: the territory is shared and
  the cube root is not disturbed by interaction. Limit: 4 rules, one start geometry.
- **H26a supported.** Random i.i.d. background: area exponent 0.924 (sd 0.013),
  extent (width) exponent 0.466 (sd 0.031) over k=16..24, 9 runs
  (RLR, RLL, RLRLRRRLLR, RRRLR; 4 seeds each; 7 of 16 escaped the 8192 board by 2^23
  and are excluded, which biases toward slower runs). Prediction 0.5 +- 0.07
  held; the cube root needs the blank repelling ground. Not 1/3 at all.
- **H26b: H_A (class change at t* ~ eps^-3) FALSIFIED for small noise; H_B
  holds.** eps = 1e-4, 1e-3, 1e-2: area exponent 0.68-0.69 at k=24-27,
  coefficient A/t^(2/3) = 2.7, 2.7, 2.9 (noise-free 2.7); eps = 0.1 (about 5% of steps
  with a wrong-or-same turn, since the replacement is uniform L/R): exponent
  0.71-0.76, coefficient 6.4 (x2.4), width exponent 0.31-0.38 (still cube root).
  Larger noise does change the class: eps = 0.3: area 0.81-0.83; eps = 0.6:
  0.90-0.92, width 0.50 (diffusive); eps = 1 (random walk) escapes the board.
  So the cube root is robust to a few percent turn noise (a *threshold*, not
  a crossover time that diverges like a power of 1/eps); the transition lies
  between 0.1 and 0.6 in eps. Not located more finely (limit: 3 rules,
  3 seeds, k<=27; eps=0.3/0.6 runs partly escaped so are biased).

## Items 11-16, 22: the tether ("home") questions -- hypotheses written 2026-10-13 before any run

Tool: `examples/tetherlab.rs` (own code, own grids; does not read or write
`experiments/archive/2026-10-knockout-maps/knock/`, `experiments/archive/2026-10-knockout-maps/dumps/`, the knockout files). Calibration done before the
hypotheses: `tetherlab dose RRRRRLLLLLL 16777216 4194304 2 real shuffle keep:0.9`
gives spread 14.1 (real), 38.6 (shuffle), 24.8 (keep 0.9) vs the published
14.4, 39.3, 22.6 at trial length 2^26 (mine 2^22; the notes say spread is flat
from 2^22). Hard rules: RRRRRLLLLLL, RLLLLRRRRLR. Easy: RRRLLRLLR,
RLLRRRRRLRLR, RRRLLLLRRRLL. "Spread" = RMS distance from the last quarter's
mean position; "tethered" = spread < 25 in the last quarter.

- H15 (how many hard rules). Screen = all log-class (tethered) primitive
  rules in `census.csv` (n <= 12): grow 2^24, then a fresh ant on (a) real and (b)
  shuffled field, 2^24 steps. Hard := tethered on real (spread_real < 25) and
  spread_shuf >= 30. Predictions: hard rules are a minority (< 40% of the
  tethered rules); hardness increases with territory area (Spearman(area,
  spread_shuf/spread_real) > 0.2) and with rule length; it is not predicted
  by #R/n (|rho| < 0.15). Falsifier: > 60% hard, or no relation to area
  and length (|rho| < 0.1 for both).
- H13 (age). For the two hard rules at ages 2^20, 2^24, 2^28, with keep:F
  F in {0.8, 0.85, 0.9, 0.93, 0.95, 0.97, 0.99}, 8 seeds: define f50 as the F at
  which mean spread is halfway between real and fully shuffled. Two
  competing hypotheses, pre-registered. H13a (fixed core): the number of
  corrupted cells at f50, N50 = (1 - f50) * area, is age independent (within
  30%) while the fraction is not. H13b: the corrupted *fraction* is age
  independent. I predict H13a (the hold needs a bounded set of cells; area
  grows only logarithmically, so the two differ by little: the area ratio
  2^28 vs 2^20 is what discriminates; measured area will be reported first). If area changes
  by < 25% between ages the test cannot discriminate and I will say so.
- H16 (graded or sharp). keep:F with F from 0.5 to 1 in steps of 0.025, 8
  seeds, both hard rules, age 2^24. Predictions: mean spread vs F crosses
  halfway at f50 = 0.92 +- 0.04; the 10-90% width of the transition is >= 0.05 (a crossover, not a
  jump); per-realization outcomes near f50 are NOT bimodal (fewer than 30% of
  realizations in a band close to either end); i.e. the state is graded, as the notes' finding 1.
- H14 (carrier). Knock out whole classes: colour class k (every cell of colour k
  swapped with a random cell of another colour) for each k, and parity
  classes (shuffle among cells with (x+y) even / odd), each compared with a
  matched-corruption random control (shuffle of m random cells, m chosen so
  that the expected number of changed cells is equal). Prediction: no class is
  special: spread(class) within 20% of its control, i.e. the carrier is spatial,
  not a colour or parity class. Falsifier: some class with spread > 1.5x or
  < 0.67x of its control (a class-specific carrier).
- H11 (bound state). Clone the grown state *including the running ant* at age
  2^24, flip NFLIP random visited cells (colour +1) in the clone, run both
  2^25 more steps. Predictions: (i) damage spreading: the number of differing cells
  reaches >= 30% of area by 1e6 steps after first contact (the dynamics is
  chaotic: positive Lyapunov-like growth); (ii) nevertheless the home survives: P(lose
  tether | 1 flip) <= 5% for hard rules (an attractor with a finite basin,
  maintained by the running ant, versus a fresh ant that cannot re-form it);
  (iii) P(lose tether | 700 flips ~ 10% of area) >= 50%. Falsifier of (ii): a single
  flip kills the tether in > 20% of trials (a repeller, knife-edge).
- H12 (formation). Patched-start ants (5x5 random patch, seeds 1..48), 2^26
  steps, windows of 2^15: onset = last window index at which RMS distance from
  the start exceeds 1.5 x its final median. Predictions for the five known
  tethered rules: the onset is a rare-event-like random variable with wide spread
  (sd of log2 onset across seeds > 1.5 octaves); median onset between 2^16 and 2^24;
  the territory extent at onset is much less variable than onset itself (CV of extent < 0.4 vs CV of
  onset > 1), i.e. formation is triggered by reaching a size, not a clock.
  (Extent is only observed at the end of the run in my implementation, so I
  compare final extent, a weaker test; stated now.)
- H22 (tether drift). From the 2^26 trajectories of the five known tethered rules
  (own dumps in `experiments/archive/2026-10-tether-rules/dumps_f/`): radial drift v and diffusion D at lag tau from
  `experiments/_lib/tether.py`; P1.5 predicts D/v (outward) equals the decay length of the
  occupancy profile within 30% for the easy rules, and fails (ratio far from 1,
  or no inward drift at all) for the hard rules because their hold is not a
  smooth potential. Falsifier: D/v matches for the hard rules too.

### Results: items 24 and 28 (screens: `python3 experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_screens.py hex|cube 6 | ext 12 24 ...`;
### `uv run experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_lattice_stats.py experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_hex.csv`; `experiments/archive/2026-10-probe-growth-census/scripts/cube_fill.py`; `experiments/archive/2026-10-probe-growth-census/scripts/sq_baseline_window.py`)

- **Item 24 (hexagonal lattice), H24 mostly held, with a small offset.** 2718
  mirror-canonical hex rules of length 2..6 over {r,l (60 deg), R,L (120 deg)}
  (repeats of shorter rules NOT removed here), 2^24 steps: 2041 blob-like, 637
  escaped the board (highway or ballistic), 24 slow, 16 fast (a >= 0.9). For the
  blobs, area exponent over k=16..24: quantiles 10/25/50/75/90% =
  0.681/0.694/0.712/0.737/0.768, extent exponent median 0.346 (IQR 0.331-0.366), flat in
  rule length (median a 0.711-0.736 for n = 2..6). Same window for the square-lattice core rules
  (`experiments/archive/2026-10-probe-growth-census/results/sq_baseline_window.txt`): 0.682 median (0.667-0.697 IQR), so hex is higher by
  about 0.03 in area exponent; extent exponents agree (0.346 vs ~0.34). My
  acceptance interval for the median was [0.65, 0.70]; 0.712 misses it, but is
  inside the wider falsifier [0.62, 0.75]. Reading: cube root class on the
  hex lattice, with a slightly larger finite-window offset (fill of the
  territory is still rising; 2 x extent exponent = 0.69 is nearer 2/3). Not tested: the
  rotor on the hex lattice (not implemented), so the window bias is
  uncalibrated here: this is the weak point. Triangular-cell lattice (3 neighbours) not done.
- **Item 28 (cubic lattice), H28 partly held.** 1416 cubic-lattice rules of
  length 2..6 over {L,R,U,D} (two mirror reductions), 2^24 steps (box 320^3): 578
  escaped (highway/ballistic), 400 blob-like, 114 bounded, 22 slow, 22 fast. For
  blobs the extent exponent drifts 0.279 (k14-18) -> 0.262 -> 0.254 (k20-24):
  consistent with 1/4. Volume exponent 0.847 -> 0.830 -> 0.816 (k20-24 IQR
  0.797-0.836) with V/E^3 rising 0.17 -> 0.23: falling toward the predicted 3/4 but
  not inside my acceptance band [0.72, 0.80] yet (the prediction is therefore
  unconfirmed, not refuted; the drift is the same sign as the rotor's finite-window
  bias in 2D). Window 2^24 only; need 2^30+ at radius ~ 100 for a decisive test.
  **Correction to the frontier note / my literature check:** the control walker
  does not behave as t^(3/4). The 3D rotor-router with i.i.d. uniform
  arrows (`Rotor3`, 12 seeds, property-tested) leaves a 512^3 box by 2^17 steps and
  has area/t = 0.69 at 2^15: its range is linear in t (transient walk), so the
  bound c t^(d/(d+1)) is far from tight in d = 3 and gives no calibration for
  the 3D ant's exponent. (For d = 2 the bound is tight, which is the
  Bou-Rabee-Peres theorem.) I rely on the extent exponent matching 1/4 and
  the downward drift of the volume exponent only.

### Result: item 22 (`experiments/_lib/tether.py` on `experiments/archive/2026-10-tether-rules/dumps_f/` = own 2^26 dumps; `experiments/archive/2026-10-tether-rules/results/tether_drift.txt`)

Zero-flux drift-diffusion check: v/D (outward displacement over lag tau divided
by MSD/4tau, averaged with weights) against the observed exponential slope
d ln(time per cell)/dr.

| rule | class | observed slope | v/D (tau=2,4,8) | ratio at tau=4 |
|---|---|---|---|---|
| RRRRRLLLLLL | hard | -0.172 | -0.202, -0.195, -0.187 | 1.13 |
| RLLLLRRRRLR | hard | -0.172 | -0.203, -0.196, -0.188 | 1.14 |
| RRRLLRLLR | easy | -0.549 | -0.636, -0.561, -0.511 | 1.02 |
| RLLRRRRRLRLR | easy | -0.338 | -0.408, -0.377, -0.361 | 1.12 |
| RRRLLLLRRRLL | easy | -0.338 | -0.406, -0.377, -0.350 | 1.12 |

H22 / P1.5 **supported for all five** (D/v within 15% of the decay length at
tau = 4 and 8, within 20-25% at tau=2): tethered ants feel a
constant inward drift (v/D flat in r beyond ~5 cells), the stationary occupancy
is the matching exponential. My pre-registered falsifier ("D/v matches for the
hard rules too") **triggered**: the hard/easy split is not a difference in the
stationary radial law; it must lie in what holds the drift in place (item 14/16).
**Unexplained coincidence found here** (not part of the pre-registered tests): the two hard rules
have radial occupancy statistics equal to ~0.3% with different trajectories
(mean r 11.576 vs 11.545, 10/50/90% quantiles 2.24/9.22/23.85 vs 2.24/9.22/23.6; observed slope
and v/D(r) agree to 2-3 digits), and the same for two of the easy rules (mean r 5.541 vs 5.531,
slope -0.338 in both). Trajectories are not related by a symmetry (position match < 3% for
all 8 dihedral maps), and the rule strings are not rotations/mirrors of each other. So pairs of
different rules share a radial law to high precision: add to open questions (hidden
equivalence of the bound state? coincidence of two rules' typical drift?).

## Item 31: faster ant

**Hypothesis** (2026-10-13). `fast::run` is slowed by per-step bookkeeping (x/y,
escape test, 4 min/max, 8-byte trail write), not by the ant's own memory
traffic. Predicted speedup of a loop containing only read/turn/write/move: >=1.3x.
Then, shortening the dependent-load chain (one fused (heading, cell) -> (new heading,
index delta) lookup instead of two sequential lookups) another >=1.2x.

**Implementation** `src/lean.rs`: sentinel ring for escape, touched flag in bit 7
for the extent, trail rebuilt by running the (reversible) dynamics backwards
and then forward again, fused transition table. `run_lean` returns the same
`RunResult` as `fast::run`; `tests/lean.rs` (proptest, 4000 cases: random rule,
grid 24-200, 60k steps, history 100-30000) checks every field including
highway detection; `sweep_lean` output is byte-identical to `sweep` on test rules.

**Result** (`experiments/archive/2026-10-misc-instruments/results/leanbench.txt`, 5e8 steps, 8192 grid, machine under load from
other jobs): fast 139-141 Msteps/s; lean (without fusion) 207-211 (1.5x);
lean (fused) 285-303 Msteps/s: **2.05-2.16x** on RLL, RLRLLRRLL, RLLRLLRLRRRL.
Both predictions held. Limits: no block/compression algorithm (the interior is
chaotic, so a Hashlife-style macro-step has nothing to cache); the speedup
is constant-factor, bounded by the dependent-load chain (~3.3 ns/step). `highway_onset`
(HashMap re-run) is unchanged and is the new bottleneck for runs that end in a highway.
Used for item 17 (`experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e10.sh`, `sweep_lean`).

### Results: item 15 (`tetherlab screen 16777216 8388608 1 < experiments/archive/2026-10-log-growers/results/log_rules.txt`; `uv run experiments/archive/2026-10-tether-rules/scripts/tether_screen_stats.py` > `experiments/archive/2026-10-tether-rules/results/tether_screen.txt`)

Population: the 560 primitive census rules of class `log` (n = 5..12). Grown 2^24, then a
fresh ant on the real and on a shuffled copy of the field, 2^23 steps each, spread over
the last quarter (1 shuffled trial left the board: counted as lost). Check on the
known rules (all in the screen except RRRRRLLLLLL, which census.csv classes `blob`, alpha 0.150,
at the edge of the class boundary): RLLLLRRRRLR real 14.7 / shuffled 45.6 (hard, as published), RRRLLRLLR 4.2 / 6.1,
RRRLLLLRRRLL 7.0 / 18.0, RLLRRRRRLRLR 7.0 / 11.7 (easy, as published). Calibration passes.
- 556 of 560 are tethered on the real field (spread < 25). **184 (33.1%) are hard**
  (shuffled spread >= 30), 108 intermediate (15-30), 264 lose nothing (< 15). So hard
  rules are common (a third, not "two of five"): H15 first prediction (< 40%) held.
- Hardness is almost a function of the territory area: AUC of area alone 0.987; hard
  fraction 1% / 5% / 94% in area terciles (< 1486, 1486-5278, > 5278). Rank
  correlation of the shuffled spread with area: 0.95. Interpretation (inference, not
  tested): area is an *outcome* -- a rule that tethers strongly even in random surroundings forms
  its home early and stays small; rules that can only tether in a particular arrangement
  wander (and grow) until they stumble into it. So the area correlation does not mean
  that size causes hardness. The 'hardness grows with area' prediction held, trivially.
- Rule length: no smooth trend (Spearman(hard, n) = -0.007), but the
  fractions are n = 5-7: 0%, n = 8: 14%, 9: 0%, 10: 4%, **11: 68%**, 12: 20% (198 and 228
  rules at n = 11, 12). Predicted no length relation; the n = 11 spike is not
  explained (could be a census sampling artefact: I did not check how the census chose its n = 11 and
  12 rules). #R/n: Spearman(hard, fracR) = -0.17 (prediction |rho| < 0.15 narrowly missed).
  Run structure is more informative: AUC 0.735 for the number of runs (more alternation, harder),
  0.337 for the longest run (long runs, easier).
- Limit: one shuffle per rule; threshold 30 taken from the two known hard rules; the
  `log` class excludes tethered rules classed `blob` (28 blob rules have alpha < 0.25, including
  RRRRRLLLLLL).

### Results: items 13 and 16 (`tetherlab dose RULE AGE 8388608 12 real keep:0.5 ... keep:0.99 shuffle`;
### ages 2^20, 2^24, 2^28; 12 shuffle seeds per point; `uv run experiments/archive/2026-10-dose-corruption-dose/scripts/dose_stats.py` > `experiments/archive/2026-10-dose-corruption-dose/results/dose_stats.txt`)

Territory area by age (from `experiments/archive/2026-10-dose-corruption-dose/results/dose.log`): RRRRRLLLLLL 2907 / 7264 / 14239 (x4.9 over 2^20 -> 2^28),
RLLLLRRRRLR 5336 / 11144 / 20712 (x3.9). So the age comparison does discriminate
fixed-count from fixed-fraction. Calibration: spreads at 2^24 reproduce the earlier values
(real 14.3, shuffled 38.8, F=0.9: 24.2).
- **H13 (age): H13a (fixed core, N50 constant) FALSIFIED; fixed fraction fits better.**
  N50 = (1 - f50) * area grows 7.4x (RRRRRLLLLLL) and 4.5x (RLLLLRRRRLR) from 2^20 to 2^28,
  tracking the area (x4.9, x3.9), while (1 - f50) changes only x1.5 and x1.16. At a fixed
  corrupted fraction the spread hardly moves with age: at F = 0.9 the mean spread is
  20.6 / 24.2 / 25.2 (RRRRRLLLLLL) and 20.5 / 21.6 / 23.6 (RLLLLRRRRLR) at 2^20 / 2^24 / 2^28, F = 0.96:
  16.6 / 17.3 / 17.9 and 16.6 / 17.1 / 17.6, although the number of corrupted cells grows ~4-5x. So the
  hold degrades with the corrupted *fraction*, not the number of cells: the home is a
  property of the whole territory, not of a bounded core (consistent with the earlier
  "knockout map" motivation, but it says the critical cells are spread over the territory).
  What does grow with age is the fully-shuffled spread (27.6 -> 51.6; 34.4 -> 61.2): the cup gets wider
  while the home stays 14.
- **H16 (graded vs sharp): graded, but my f50 prediction was wrong.** Mean spread vs F is
  smooth with no jump from F = 0.5 to 1; spread across 12 seeds at a given F is tight
  (sd about 1, e.g. F = 0.94: 18.5-21.5; none bimodal: the share of realisations in the
  middle half between real and shuffled is 0.97-1.0 near f50), so each corrupted field has its own
  intermediate stationary spread -- a graded home, as the pattern-field notes found. Predicted
  f50 = 0.92 +- 0.04: measured f50 = 0.82 / 0.80 / 0.80 (RLLLLRRRRLR) and 0.90 / 0.88 / 0.84
  (RRRRRLLLLLL), so f50 depends on rule and age (it moves with the cup size, since I define it
  halfway to the shuffled value). 10-90% width 0.44-0.51 and 0.24-0.32: a crossover far wider than the
  predicted >= 0.05; no percolation-like threshold is visible. Caveat: `keep:F` moves each cell
  independently with probability 1 - F and then shuffles the moved cells, so the actually changed
  fraction is slightly less than 1 - F (10 colours: ~ 0.9(1-F)... exact factor not computed); f50 values
  are therefore nominal.

### Results: item 4 (`probe 30 < experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_walkers.txt`; `uv run experiments/archive/2026-10-item4-exponent-rotor-calibrated/scripts/item4_stats.py` > `experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_stats.txt`)

11 rules x 24 patched seeds to 2^30 steps (251 of 264 runs kept: 13 runs left the 8192
board, 3 rules affected -- RLRR 7, RLRLLL 5, RRLLLLLLR 1 -- so those rules' ensembles are biased toward
the slower seeds). Local area exponent a(k) from 3-octave windows, ensemble mean over seeds.
- **Prediction (i) FAILED.** a_inf (delta = 1/3) within 2 SE of 2/3 for only 2 of 11 rules (z = 4.9, 12.1, 1.4,
  10.7, 6.6, 8.5, 5.0, 2.9, 8.1, 7.3, -1.7; SEs ~0.002). Most rules sit at a(k) 0.675-0.70 over k = 24-30
  (RLL 0.676/0.676/0.676 at k = 24, 28, 30; RLR 0.748 -> 0.695 -> 0.699; RLLLRRLRRRLR 0.659 -> 0.666 -> 0.659).
  Mean of the last six local exponents across rules: 0.6825 (sd 0.0135, range 0.660-0.709). Changing the
  correction exponent (delta 1/6, 1/3, 1/2) moves a_inf by only ~0.01-0.02 and chi2/dof stays 0.3-5.6, so the
  conclusion does not hinge on the correction form: nothing here converges to exactly
  0.667 by 2^30; the same holds for the rotor (0.687 at 2^20-2^26, calibration Part A).
- **Prediction (ii) FAILED narrowly:** between-rule true sd of a_inf = 0.0125 (> 0.01), driven by
  RLR/RRRLR (0.696-0.698, correction amplitude b = 2.5), RRLLLLLLR (0.707), versus RLLLRRLRRRLR (0.660), RLL (0.676).
  Differences of 0.02-0.04 between such rules are many SEs, so rules *do* differ in effective exponent
  over 2^22-2^30; whether this is different asymptotes or different slow convergence is NOT decided by
  this data. (iii) qualitatively yes: the two highest-b rules (RLR, RRRLR) are the ones with the high
  early exponents; they come down by about 0.03-0.05 from k = 16-24 to k = 28-30, so a slow downward drift
  exists for them, but the final values are still above 2/3.
- **Self-averaging (P5b) held for 10 of 11.** CV across seeds of A / t^(2/3) falls from
  0.05-0.12 at 2^16 to 0.009-0.032 at 2^30 (factor 2.9-9; all but one rule above the predicted factor 2). The coefficient therefore
  looks deterministic, as for the rotor (8.9% -> 1.8%). **Exception: RRLLLLLLR**: CV 0.12 -> 0.26 -> 0.38 -> 0.39
  (rising), i.e. the seeds do not converge: some patches lead to much faster growth (3 further seeds had
  already left the board). A genuinely non-self-averaging chaotic rule; add to open questions
  (is its growth rate multi-valued, with a few different "phases" selected by the initial patch?).
- Verdict on item 4: "exactly 1/3 for every chaotic rule" is neither confirmed nor refuted.
  What is established: (a) run-to-run noise is small for ordinary rules at 2^30 (CV ~1-3% of A), (b)
  the area exponent is 0.66-0.70 across rules even at 2^28-2^30, with systematic rule differences far
  above their SEs, and (c) at least one rule is not self-averaging.

## Item 21: are the non-1/3 outliers (alpha 0.15-0.6) real?

**Hypothesis** (2026-10-13, before the run). Selection: all blob rules in
`probe_summary.csv` with alpha_w > 0.40 (36 rules, "high") or < 0.27 (32 rules,
"low"), plus 30 random core rules as control (0.30 < alpha_w < 0.37). Each re-run
from 12 random 5x5 patches (seeds 1..12), 2^27 steps, same fit window as the census
(octave windows k = 20..26, width = max(width, height)). Part C says most of the
spread is run-to-run noise, so predictions: (i) regression to the mean: for >= 70% of the
high outliers the 12-seed mean alpha_w falls below 0.37 and for >= 70% of the low outliers it
rises above 0.30; (ii) the persistent minority (< 30%) is real: consistent in sign in >= 10/12
seeds; (iii) persistent high rules show kappa drift (g_k > 0.1 in the original
census), persistent low rules g_k < 0 (the paper's claim that the outliers are the rules whose edge
occupation drifts). (iv) controls: 12-seed mean within 0.30-0.37 for >= 90%.
Falsifier of the 'noise' reading: fewer than 50% regress.

### Results: item 14 (`tetherlab dose ... class:K ctrlclass:K parity:P ctrl:M recolour:K recolourctrl:K core:R`; age 2^24, 12 seeds;
### `experiments/archive/2026-10-knockout-maps/results/classko_stats.txt`, `experiments/archive/2026-10-recolour/results/recolour_stats.txt`, `experiments/archive/2026-10-colourstats/results/describe_colours.csv`)

**H14 FALSIFIED: a colour class is special.** The carrier of the hold is not diffuse.
- Colour counts in the grown field are far from uniform: for RRRRRLLLLLL colours 6, 8, 10 have 222, 188,
  190 cells (about 3% each) against 760-890 for the others; for RLLLLRRRRLR colours 0, 6, 8 have 185, 176, 177
  (about 1.7%) against 950-3076 (colour 2 is very abundant at 3076). These rare colours are spread over the whole
  territory (mean radius 33-36, only 5-9% within 10 cells of home), not concentrated at the centre.
- *Swap* test (every cell of colour K swapped with a random other-colour cell; control: shuffle a random subset
  of the same expected number of changed cells). Rare classes: spread 37.3-37.7 for RRRRRLLLLLL (colours 6, 8, 10),
  38.5-40.3 for RLLLLRRRRLR (colours 0, 6, 8) -- as bad as the full shuffle (38.8 / 46.2) -- while the matched random controls give
  19.3-20.3 and 16.7. Ratio 1.9-2.4. Abundant classes behave the other way: class spread 26-29 against control
  35-36 (ratio 0.76-0.81), i.e. the abundant-colour cells are *less* critical than random cells.
- *Recolour* test (cells of colour K set to a random other colour; control: same number of random cells): rare classes
  25-26 vs 19-20 (ratio 1.28-1.32) and 24-25 vs 17.4-17.9 (ratio 1.37-1.40); abundant classes 0.95-1.04. So
  just erasing the rare-colour cells costs about +6-7 spread units over a random equal-sized corruption,
  and moving them to wrong places is far worse (the misplaced rare cells act as defects).
- Parity classes ((x+y) even / odd shuffled): 38.6 / 38.4 (RRRRRLLLLLL) and 43.3 / 43.7 (RLLLLRRRRLR), equal to a
  random subset of the same size (38.5, 42.9): no parity structure, as predicted.
- Spatial core shuffles (cells within R of home): R = 10: 16.4-16.7; 20: 21.0-21.4; 30: 27.1; 40: 33.9 for both
  rules: the core carries little; the damage tracks the number of shuffled cells.
Reading (inference): the critical cells are a small set (about 2-3% of the territory per rare colour) identified by
colour and scattered across the territory; the 'present at wrong places' effect suggests the home is a
configuration in which the rare-colour cells sit at specific positions (maybe a skeleton of return paths, the
idea in `pattern-fields-results.md`). Not explained: why exactly those colours are rare (6, 8, 10 for the first
rule, 0, 6, 8 for the second). Immediate follow-up for the other agent's knockout map: its hot tiles should be
rich in rare-colour cells; a cheap check is the rare-colour density of hot versus cold tiles.

### Results: item 11 (`tetherlab flip RULE 16777216 33554432 16 NFLIP 7`; `experiments/archive/2026-10-flip-damage/results/flip_stats.txt`)

Clone the grown state *with the running ant*, flip NFLIP random visited cells (colour +1) in the clone,
run both 3.4e7 steps in lockstep, 16 perturbations per setting, both hard rules.
- (ii) **held**: P(lose tether | 1 flip) = 0/16 for both rules (spread 14.5 / 14.6 against base 14.4 / 14.9). Also 0/16 for 10
  flips and for 100 flips (spread 18.1 / 16.8: slightly wider, still home), whereas 700 flips (9.6% / 6.3% of the area)
  lose it in 16/16 (spread 36.6 / 33.2). So the running home is an attractor with a finite basin, robust to ~1% of
  cells flipped, lost somewhere between 100 and 700 flips (not located).
- (i) **partly held**: damage spreads (number of cells differing between the perturbed and base states), but slowly for a
  single flip. Median damage after first contact: 35 / 49 / 758 cells at lags 1e4 / 1e5 / 1e6 (RRRRRLLLLLL; area 7264) and
  36 / 40 / 6070 (RLLLLRRRRLR; area 11144); only 44% and 60% of single-flip runs have reached 30% of the area by
  lag 1e6 (my prediction was >= 80%); with 10 or more flips it is 100% and the damage covers almost the whole area (5758 and
  6701 cells at 1e6 for 10 flips). First contact takes a median 7e5 and 1.9e5 steps for one flip (the ant has to reach the cell).
  So trajectories decorrelate completely in the territory while the ant stays at home: the home is
  a statistical attractor of the (ant, field) dynamics, not a periodic orbit or a fixed configuration. Together with the fresh-ant
  results: a running ant repairs/re-randomises 1-1.4% damage without losing the home, but a fresh ant on a field
  with only 3% damage in the rare-colour cells (item 14) loses it, so 'formation' needs more than 'maintenance'.
  Limits: 16 perturbations per setting; flip = colour +1; the threshold between 100 and 700 flips is not resolved;
  return map / Lyapunov exponent proper not computed (damage grows ~14x per decade of lag from 1e5 to 1e6 for one flip;
  between 1e4 and 1e5 it barely grows, so it is not exponential in lag).

### Results: item 12 (`tetherlab formage RULE 24 7 24 524288`; `uv run experiments/archive/2026-10-formage-age/scripts/formage_stats.py` > `experiments/archive/2026-10-formage-age/results/formage_stats.txt`)

Method change (stated honestly): my pre-registered operationalisation (windowed RMS distance from the start in a
single long run; `tetherlab form`) was uninformative (the ant is within 1.5x of its home radius in nearly every
window from the first, and "onset" was dominated by rare excursions), so I replaced it by a direct test:
for each of 24 patched starts + the blank start, at every age 2^k (k = 7..24) take the field, run a fresh ant at home
on the real and on a shuffled copy for 2^19 steps, and report the spread.
- **H12 FALSIFIED: there is no formation event.** For all five tethered rules the spread of a fresh ant on the real
  field is already at its late value at the earliest age tested, 2^7 = 128 steps (area ~ 40-55 cells): RRRRRLLLLLL 11.8
  at 2^7 vs 14.4 at 2^24; RLLLLRRRRLR 13.2 vs 15.4; RRRLLRLLR 4.7 vs 4.9; RLLRRRRRLRLR 7.3 vs 7.5; RRRLLLLRRRLL 7.2 vs 7.6;
  sd across the 25 starts is 0.2-1.6 (the home is not a rare-event outcome of the initial patch). No start ever exceeds
  1.5 x its rule's median late spread. What changes with age is the *cup*: shuffled spread grows from 12 to 35 (RRRRRLLLLLL),
  while the home stays ~12-15. For the hard rules the real-field home is slightly worse
  than the shuffled one at the smallest sizes (13.2 vs 12.9), and becomes distinguishable only once the cup exceeds
  the home (2^14 or later). So 'hard' means: the home value (set at birth) stays while the cup grows around it; the
  required arrangement is built together with the territory, not found later. The earlier statement that the home
  'is not re-formed from degraded fields' stands, but 'formation' in a normal run is not an event.
- Slow drift of the home itself: spread 11.8 -> 14.4 (RRRRRLLLLLL) and 13.2 -> 15.4 (RLLLLRRRRLR) from 2^7 to
  2^24, i.e. +20%/+17% over 17 octaves (the same trend as the logarithmic territory growth); the easy rules do not drift
  (4.7 -> 4.9).
- Limits: spread < ~14 at ages < 2^12 cannot be distinguished from a small cup (shuffled 12-13); five rules; 2^19-step trials.

### Results: items 5 and 7 (`shape 26 2048 < experiments/archive/2026-10-shape-limit/results/shape_rotor_specs.txt`; `shape 28 4096 < experiments/archive/2026-10-shape-limit/results/shape_ant_specs.txt`;
### `uv run experiments/archive/2026-10-shape-limit/scripts/shape_stats.py experiments/archive/2026-10-shape-limit/results/shape_rotor.csv experiments/archive/2026-10-shape-limit/results/shape_ants.csv` > `experiments/archive/2026-10-shape-limit/results/shape_stats.txt`)

Rotor calibration: 40 seeds, 2^26. Ants: 11 rules x 8 patched seeds, 2^28 (85 of 88 runs reach 2^28; three left the 4096 board).
Instrument checks: rotor boundary-width local exponents 0.24, 0.19, 0.13, 0.17, 0.16, 0.17, 0.13 for k = 12..26 (K&D 0.136 ->
passes: fitted 0.158 over k >= 18, last pair 0.126); the rotor's visit profile is the linear cone of K&D; the rotor's CV of
S/t^(2/3) falls 10% -> 1.3% over 14 octaves (K&D/Bou-Rabee-Peres: deterministic coefficient). All consistent with the calibration notes.
- **P5a held (round shape).** Ant territories at 2^28: median anisotropy (l1-l2)/(l1+l2) = 0.071 (rotor 0.054 at 2^26), median
  4th-harmonic amplitude of the contour 0.044 (rotor 0.013, 0.028 for h2), fill A/(pi rbar^2) 0.98 (rotor 0.96). Per rule the anisotropy
  at 2^28 is 0.01-0.13 (RLR 0.131 highest, RRLLLLLLR and RLLLRRLRRRLR ~0.01-0.02): a nearly round but not perfectly isotropic
  limit; h4 > h2 residuals (rule-dependent 4-fold deviation) are small but not zero: not tested whether they vanish as t -> infinity.
- **P5b held (deterministic coefficient) for 9 of 11 rules** (the predicted minimum was 9): CV of A/t^(2/3) across 8
  seeds falls from 0.06-0.12 at 2^16 to 0.007-0.046 at 2^28. The two exceptions are RRLLLLLLR (CV rises 0.12 -> 0.37, the same
  non-self-averaging rule as in item 4) and RLRR (n = 5 surviving runs, CV 0.78 at 2^16 due to one outlying start, 0.02 at 2^28).
- **P5c: collapse held, "differs from the rotor" FALSIFIED -- striking.** Mean visits per cell in 20 shells of width
  0.075 R_eq (R_eq = sqrt(A/pi)), in units of t/A, averaged over runs:
  ants 2.99 2.78 2.53 2.27 2.02 1.77 1.53 1.29 1.05 0.82 0.59 0.37 0.18 0.06 0.02 0 ...;
  rotor 2.87 2.66 2.42 2.19 1.96 1.74 1.51 1.29 1.07 0.85 0.63 0.41 0.20 0.05 0.00 ...
  Both are the same cone 3 (1 - r/R_eq) (mean over the disc = 1, as required if all of the time is spent inside R_eq: values
  1.54 at shell 6 and 0.19 at shell 12). The across-rule relative sd of the ant profile is 3-14% over the first 12 shells
  (4% at shell 6), and ants vs rotor differ by 1-4% (central shells) .. 10% (shells 10-11). So the occupation density is
  universal across rules and across the ant/rotor divide to a few per cent. The cube-root theorem for the rotor
  (K&D nbar(r) = a N^(1/3) (1 - r/(b N^(1/3)))) therefore describes the ant's time density as well; this is the best
  quantitative evidence so far for a common mechanism, and a sharper target than the exponent for any derivation.
- **P7 (boundary width): prediction (0.1-0.2) not met; ants are wider than the rotor.** Wsurf local exponent against t for the ant ensemble:
  0.34, 0.35, 0.34, 0.31, 0.28, 0.31, (0.14 -- sample change, three runs dropped), 0.27 for k = 12..28; fitted 0.258 for k >= 18
  (per-rule median 0.250, range 0.128-0.362). Same estimator and window on the rotor: 0.158 (last pair 0.126). The ants' exponent is
  falling but is 0.25-0.27 at the end, between the rotor's ~0.13 and the territory radius' 1/3. At comparable size (A ~ 9e5)
  W/R_eq = 0.076 for ants against 0.049 for the rotor, so the ant edge is ~1.5x broader. Verdict: not shown to be a different
  universality class (the exponent drifts down, as the rotor's does; 2^28 is too short), but not the same value at equal t either.
  Wsurf includes interior holes (as K&D's does); unclear how much of the ant's width comes from holes (not separated).

## Item 30: heavier statistics, loud failure

**Hypothesis** (2026-10-13). Between-seed sd of the per-rule headline numbers is of the same size as the Part C
within-rule sd (alpha_w 0.016, alpha_rg 0.011, a 0.020) and is much larger than the fit standard errors; c has
essentially no seed noise (it is set by the rule's letters, cf. item 3). 
**Result** (`research-outputs/scholarly-articles/cube-root-growth/seed_uncertainty.py`, `experiments/archive/2026-10-probe-growth-census/results/seed_uncertainty.txt`, `research-outputs/scholarly-articles/cube-root-growth/seed_uncertainty.json`; 11 rules x 24 patched
starts, census windows k = 20..26): median between-seed sd across the 11 rules: alpha_w 0.0165, alpha_rg 0.0096, area exponent
0.0126, beta (edge) 0.0128, **c 0.0006**, kappa 0.041. Both predictions held (Part C: 0.016 / 0.011 / 0.020). c is
deterministic to 3 digits across starts (0.0000-0.0030 per rule), kappa is not (0.017-0.061). The exception again is
RRLLLLLLR: alpha_w 0.379 +- 0.065, a 0.763 +- 0.137, kappa 2.2 +- 1.1 (non-self-averaging).
`research-outputs/scholarly-articles/cube-root-growth/compute_numbers.py` now exits with an error before computing anything if any data file named in the
script is missing or empty (tested by hiding `experiments/archive/2026-10-census-sweeps/results/census.csv`), and reproduces `research-outputs/scholarly-articles/cube-root-growth/numbers.json` bit for bit
(`cmp` against the committed copy). `main.typ` was not changed; the new sd numbers live in `research-outputs/scholarly-articles/cube-root-growth/seed_uncertainty.json`
for a later edit of the manuscript.

### Correction to the H18 result above (2026-10-13)

The decade counts quoted for H18 ("17, 14, 17, 26, 11, 11 for 1e3..1e9", slope -0.011) were mislabelled by one
decade, and the slope fit dropped a zero-count bin incorrectly. Correct values (`experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/highway_stats.txt`, last block;
primitive rules of length <= 10, v2 + 1B rerun): onsets per decade (1e3,1e4] ... (1e8,1e9] = **13, 17, 14, 17, 26, 11**.
Poisson log-linear fit: slope **+0.015 +- 0.026 log10 per decade** (counts x1.04 per decade); the last decade (11) against the mean of
the previous five (17.4): Poisson P(X <= 11) = 0.071. The H18 verdict stands ("not decaying by 3x per decade; flat within
noise; tail heavy") but the last decade is mildly low, which is what the web page reports as its failed prediction
(it expected >= 15 and found 10, plus 1 older). 11 vs 10 differ only in whether the borderline onset 9.86e7 is counted.
The 1e9-1e10 decade from item 17 (running) is the next data point.

## Item 32: web demo of the cup picture

**Hypothesis** (2026-10-13). The page's simulator can show the mechanism live: with the visited set tracked from step 0, the
overlay's c, kappa, P/A should reproduce the offline probe (RLR at 2^22: A = 83628, P = 2066) and the identity
c * kappa * P/A = observed new cells per step.
**Done.** `web/sim.js` `Ant(rule, size, track)` keeps the `src/probe.rs` bookkeeping (fresh-neighbour counts, A, P, per-octave
c and kappa, area exponent over the last two doublings); `web/page.js` highlights edge cells (visited cells with a fresh
neighbour) and shows a live readout; `web/template.html` has the checkbox "show the cup" (toggling restarts the run because
the visited set must be tracked from step 0). **Checks:** `node` run of `sim.js` for RLR to 2^22 gives A = 83628, P = 2066,
c = 0.451, kappa = 1.40: identical to the Rust probe's area and perimeter; jsdom smoke tests (`web/smoke.js`,
new `web/smoke_mech.js`) show no errors and the readout "c*kappa*P/A = 0.0156 against 0.0156 new cells per step actually seen,
area exponent 0.71" at 6.4M steps. Built with `uv run web/build.py web/dist/explorer.html` (output dir `web/dist/`, not
committed). Limit: only a headless check; the visual appearance of the overlay (highlight density at large zoom, where
a pixel samples one cell) was not inspected by eye.

### Cross-check with the knockout map (read-only use of `experiments/archive/2026-10-knockout-maps/knock/*/tiles.csv` and `experiments/archive/2026-10-knockout-maps/dumps/*.grid`; `experiments/archive/2026-10-hot-tiles/scripts/hot_rare.py` > `experiments/archive/2026-10-hot-tiles/results/hot_rare.txt`)

Hypothesis written before looking (2026-10-13): if the rare colours found in item 14 carry the hold, then the other agent's
independently measured 5x5-tile knockout loss should correlate with the number of rare-colour cells in the tile, and the hot tiles should
be enriched in them, even after controlling for visited cells, distance and occupancy. Falsifier: partial Spearman < 0.1 or hot-tile
enrichment p > 0.05. (Their field is the same 2^24 field: colour counts identical to mine.)
**Result: supported for both hard rules.** Rare colours: 6, 8, 10 for RRRRRLLLLLL (8.3% of cells), 0, 6, 8 for RLLLLRRRRLR (4.8%).
Spearman(tile loss, rare cells) = 0.46 and 0.49 (vs 0.20 and 0.32 for the number of visited cells); hot tiles contain 4.3 and 3.7 rare cells
against 1.9 and 1.1 for all tiles (permutation p = 0.003 and < 0.0002; 11 and 17 hot tiles); partial Spearman controlling for visited cells, distance and
occupancy 0.48 and 0.41. Their own summary gives partial rho with route density 0.03 (CI -0.11..0.20), so rare-colour
density explains hot tiles where route density does not. Two independent methods (class knockouts here, tile knockouts there) agree on
where the hold lives. I did not touch their files or take over their protocol.

## Item 10 (refinement to 1x1 cells): status

Owned by the knockout agent: `experiments/archive/2026-10-knockout-maps/knock/RULE/refine5.csv`, `refine3.csv`, `fresh3.csv`, `fresh5.csv` exist and are growing, so the
protocol is running there. Not duplicated here. What this work adds for it: a concrete candidate for the minimal set (the ~200 cells of each
rare colour; for the first rule colours 6, 8, 10) that the 1x1 refinement can test directly, e.g. by recolouring only the rare-colour
cells inside a hot tile versus the same number of other cells in that tile.

### Item 10 complement: is the rare-colour set the minimal set inside the hot tiles?

Hypothesis (2026-10-13, before the run): if the rare-colour cells are the critical cells, recolouring only the rare-colour cells inside the
knockout agent's hot tiles (47 cells for RRRRRLLLLLL, 62 for RLLLLRRRRLR, from `experiments/archive/2026-10-knockout-maps/knock/RULE/hot.csv`) should damage the hold at least as much as
recolouring the same number of other cells from the same tiles (prediction: rare effect >= 1.5x control effect).
Result (`experiments/archive/2026-10-hot-tiles/results/hot_recolour_stats.txt`, 12 random recolourings per list, 6 control lists, `tetherlab dose ... recolourlist:FILE`, spread of
a fresh ant, age 2^24): intact 14.3 / 14.7. Rare cells: +2.67 / +1.73. Equal-sized controls from the same tiles: +2.10 / +2.59 (the second rule goes the
wrong way). All cells of the hot tiles: +4.59 / +5.76. **Prediction false: within a hot tile the rare cells are not special.** So the rare colours
mark where the hot tiles are (item 14 and the tile enrichment above) without being the minimal set themselves; in a hot tile the damage seems to
spread over its cells (47-62 cells of a ~275-425 cell tile give about half the damage of the whole tile). A true 1x1 minimal set is not found by
this; the knockout agent's `refine*` protocol is the right tool. Limit: recolouring (random colour) rather than swapping; one age; two rules.

### Item 24 (triangular cells): hypothesis written 2026-10-13 before the screen

`TriSim` in `src/ext.rs` (ant on the triangles of the triangular tiling, 3 neighbours, L/R = exit through the next edge
counter-/clockwise; property-tested against an independent Cartesian-geometry reference: `tests/ext.rs::tri_matches_geometric_reference`).
Prediction: chaotic (non-highway, non-bounded) triangular ants also have area exponent 2/3: median over rules in [0.64, 0.72] for
the k = 16..24 window (square 0.682, hex 0.712 in the same window). Falsifier: median outside [0.60, 0.76]. Screen: all
canonical (first letter R) non-trivial L/R rules of length 2..12 (4083 rules, same list as the square census), 2^24 steps.

### Correction/calibration for item 4 (added 2026-10-13 after review; `experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_rotor_stats.txt`)

AGENTS rule 5: the a(k)/a_inf estimator of `experiments/archive/2026-10-item4-exponent-rotor-calibrated/scripts/item4_stats.py` had not been run on the rotor. Done now: 24 rotor seeds, `probe 30`, same
script (argument `experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_rotor_probe.csv`). The rotor (true exponent 2/3, proved) gives a(k) = 0.737 (k=16), 0.712 (20), 0.682 (24), 0.674 (28), 0.673 (k = 29-30);
a_inf = 0.656 / 0.670 / 0.674 (delta = 1/6, 1/3, 1/2; chi2/dof 1.2, 2.4, 6.0, SE 0.001); mean of the last six local exponents 0.677.
So the estimator at 2^30 is biased by +0.004 to +0.010 (and an SE-based "within 2 SE of 2/3" criterion is meaningless: the rotor itself is 4.7 SE
above 2/3). The earlier "prediction (i) FAILED" used that flawed criterion and should be read as: "relative to the rotor benchmark (last-six mean 0.677)":
RLL 0.677, RLRLLL 0.676, RLRR 0.673, RRRLRLLL 0.675, RLRLLRRLRL 0.678 are indistinguishable from the rotor (5 of 11, consistent with exponent 2/3 under the same bias);
RRRLRLRRRRL 0.683 and RLRLRRL 0.685 are +0.006-0.008 above; RLR 0.696 and RRRLR 0.696 are +0.02 above (their b amplitudes are the
largest, 2.5, and their local exponents still fell 0.03-0.05 between k = 24 and 28: consistent with slow convergence, not shown to converge to 2/3);
RLLLRRLRRRLR 0.660 is 0.017 below; RRLLLLLLR (0.709, not self-averaging) is excluded. The broader statement stands: rules differ by up to 0.03
in effective exponent at 2^28-2^30 and this data cannot separate different asymptotes from different convergence rates; but the claim in the
earlier paragraph that "nothing converges to 2/3 by 2^30" is withdrawn: the rotor does not either, by this estimator. The rotor CV of A/t^(2/3) falls 0.056 -> 0.006 (x9), the
same as the best ant rules. Decisive statement in one line: 6 of 11 rules match the rotor within 0.006, 5 do not.

## Corrections after review (2026-10-13)

**Item 15 -- hardness cutoff was confounded with territory size.** `spread_shuf >= 30` is an absolute cutoff, so small territories
cannot be 'hard'. Size-free reanalysis (`experiments/archive/2026-10-tether-rules/scripts/tether_screen_stats.py`, last block; q = spread_shuf / cup_rms with cup_rms = sqrt(A/pi)/sqrt2):
q is bimodal over the 556 tethered rules (histogram per 0.1 from 0: 0, 54, 112, 28, 21, 21, 28, 31, 25, 21, 77, 112, 11, 8, 1): 194 rules
(35%) keep the home on a shuffled field (q < 0.4), 209 (38%) are cup-wide (q >= 1.0), 153 (27%) in between. The headline "33% hard" was an
artefact of the cutoff; with q >= 0.5 the share is 61% (65% for 0.4, 58% for 0.6); the honest statement is "hardness is graded; about a third
each: keep, lose, partial". Spearman(q, area) = 0.84 and Spearman(q, spread_real) = 0.84, AUC of area for q >= 0.5 is 0.947, so the size
relationship survives normalisation (a larger home is more fragile), but causation is not shown. Rule length: share with q >= 0.5 by n =
5: 0.20, 6: 0.17, 7: 0.00, 8: 0.64, 9: 0.33, 10: 0.21, 11: 0.72, 12: 0.69 -- the n = 11/12 excess remains, n = 10 is low. Run structure
(AUC 0.805 for the number of runs; 0.355 for the longest run; 0.64 for n) is still the best simple predictor. The known easy rules are not at q ~ 0:
RRRLLRLLR q = 0.37, RLLRRRRRLRLR 0.44, RRRLLLLRRRLL 0.77; RLLLLRRRRLR 1.08.

**Item 22 -- an identity, not a test.** For any stationary radially confined trajectory the drift/diffusion ratio estimated from that same trajectory must
reproduce the log-slope of its own occupancy, so the agreement in the table above shows only that the estimators are mutually consistent.
The pre-registered 'falsifier triggered' statement is withdrawn: nothing here discriminates hard from easy rules. A real test would predict a rule's occupancy
profile from the drift/diffusion measured in a different field (e.g. real-field motion applied to a shuffled field).

**Item 12 -- wording.** At 2^7 steps the real and shuffled spreads are equal (11.8 vs 11.9), so a home cannot be distinguished from the cup at that
age. What the data support: no detectable formation event; the real-field spread is flat (11.8 -> 14.4) while the cup grows from 12 to 35.
The status line 'present at 128 steps' is replaced by that.

**NEW, unexplained finding (found while checking identical spreads; `experiments/archive/2026-10-spread-home/results/spread_dups.txt`, `experiments/archive/2026-10-spread-home/results/spread_clusters.txt`, `experiments/archive/2026-10-spread-home/results/spread_groups.txt`,
`examples/orbit.rs`).** The 556 tethered rules take only 203 distinct spread values at 0.01 resolution, and when clustered at 2% relative gap there are 28 clusters of which 16
hold >= 5 rules and 530 rules (95%): e.g. spread 7.0: 165 rules (n = 8 and 12, 4-7 runs, territories 2530-18807 cells); 14.5: 114 rules (all n = 11, includes the two
'hard' rules); 2.66: 53 rules (n = 11); 2.32: 43 rules. So the radial law of the bound state (exponential occupancy, decay length l = spread / sqrt6, v/D = 1/l) takes
a small number of discrete values, shared by rules with very different territories and different letters. Not periodic: `orbit` finds no exact period for any of 13 rules (2^21-step tails
cover 650-8400 distinct cells, bounding boxes 29x30 to 106x102) and the occupancy-weighted RMS agrees to 0.3% between rules in a cluster (e.g. 2.65-2.68 for five rules whose bounding boxes
range 29-44 cells). Structure: blocky rules (<= 3 runs) have spread x n ~ 14.9 (n = 7..12: 1.92, 1.66, 1.53, 2.39, 2.66, 1.77); grouping by (n, #R) explains 51% of the variance of log spread,
n alone 25%; spread is symmetric under #R <-> #L (n = 12: #R = 2 and 10 both ~2.3; #R = 4, 6, 8 all ~6.9-7.0). The home is therefore not a property of a single rule's cell
configuration but of a coarse rule class: this is presumably also why different rules' homes respond in the same way (item 22's 'identical v/D'). Unexplained; added to open questions.
Consequence for items 11 and 14: the 'rare colour' structure may be a signature of the class (the hard rules' class has spread 14.5), but the check across the 114 rules of
that class was not done.

### Results: item 21 (`probe 27 < experiments/archive/2026-10-item21-slow-outliers/results/item21_walkers.txt` -- 98 rules x 12 patched seeds; `uv run experiments/archive/2026-10-item21-slow-outliers/scripts/item21_stats.py` > `experiments/archive/2026-10-item21-slow-outliers/results/item21_stats.txt`)

All 98 rules re-measured (36 high-alpha outliers, 32 low, 30 core controls). Window k = 20..26 as in the census.
- **Prediction (i) FAILED, the 'noise' reading is falsified for most outliers.** Only 17% of the high outliers (6 of 36) have a 12-seed mean below 0.37
  (prediction >= 70%) and 34% of the low ones (11 of 32) a mean above 0.30. The 12-seed means track the census values: median 0.437 -> 0.439 (high),
  0.210 -> 0.207 (low), Spearman 0.84 and regression slope 0.81 of re-measurement on the census value over the 68 outliers (slope 1 = no regression to the mean).
  Between-seed sd is small compared with the offsets: 0.017 (low), 0.016 (core), 0.053 (high; the high group is noisier).
- (ii) 19 of 36 high and 20 of 32 low rules are persistent (>= 10/12 seeds on the same side). Example persistent high rules: RLLRRRRRRRRL (census 0.424, re-measured 0.596 +- 0.158),
  RLLLLLLRLRL (0.565), RLLLLLRRRRL (0.549 +- 0.038), RRLRLLLLLRRL (0.544); persistent low: RLLRRRRLRLRR (0.109 +- 0.034), RRRLRLLLRRR (0.129), RLLRRRRLLLL (0.132).
- (iii) held: persistent high rules have median g_k +0.39 (regressed ones +0.29) and persistent low -0.45 (regressed -0.31); Spearman(g_k, mean alpha) = 0.82 over the outliers.
  This is the paper's identity, not an independent confirmation: it says outliers are rules whose edge occupation drifts, which still lacks a cause.
- (iv) controls: 93% of the 30 core rules stay in 0.30-0.37 (prediction >= 90%): the instrument is stable.
- Reading: most of the 68 outliers are real rule properties over 2^20-2^27, not noise or patch artefacts. Whether they are different asymptotic exponents or very slow
  transients is untestable at this length (compare item 4: even core rules differ by up to 0.03 at 2^30); the 'real but not necessarily asymptotic' wording is the safe claim.

**Result (triangular cells; `ext 12 24 4096 64 < experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/tri_specs.txt`, `uv run experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_lattice_stats.py experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_tri.csv 16 24`).** Prediction held, with the
best agreement of the three lattices. 4083 rules (length 2..12): 4039 blob-like (99%), 24 escaped (highway or ballistic), 20 fast; none bounded, none slow.
Area exponent over k = 16..24: quantiles 10/25/50/75/90% = 0.652/0.665/0.676/0.687/0.700; extent exponent median 0.331 (IQR 0.322-0.340); median by rule length
0.676-0.690 (n = 3..12), 0.676 at n = 12. The same window gave 0.682 (square) and 0.712 (hex). No tethered/bounded behaviour exists in this screen (on the square lattice
17% of rules were log-growing or bounded). So the cube-root class is common to the square, hexagonal and triangular lattices; the triangular ant has 99% chaotic rules,
and the rotor-calibrated window bias (+0.01 to +0.02 at 2^20-2^26, item 4) is of the size of the offsets between lattices, so I do not claim they differ.
Not done: rotor walkers on the hex and triangular lattices (the windows are uncalibrated there).

### Generalising item 14 (hypothesis written 2026-10-13 before `experiments/archive/2026-10-hot-tiles/scripts/rare_class_test.py`)

Does the 'rare colours are critical' result belong to the two named hard rules or to their class? For 12 random rules with home spread 13.7-15.6
(the 114-rule cluster that contains both hard rules) and 12 random rules with spread 6.8-7.3 (165-rule cluster), take the 3 rarest and the 3 most abundant colours
of the 2^24 field and run the swap test against the matched random control. Predictions: in the ~14.5 cluster the class/control ratio for rare colours has median >= 1.5 and
>= 60% of rare colours exceed 1.3, while abundant colours have median < 0.9; in the ~7.0 cluster (different home type) the rare-colour effect is weaker (median ratio < 1.3).
Falsifier: median rare ratio < 1.2 in the 14.5 cluster (the effect is specific to the two rules, or an artefact of the swap construction).

**Result (`experiments/archive/2026-10-hot-tiles/scripts/rare_class_test.py` > `experiments/archive/2026-10-hot-tiles/results/rare_class_test.txt`; 24 rules, 3 rarest and 3 most abundant colours each, 6 seeds, trial 2^22).** The rare-colour effect is
general, not specific to the two named rules, and it is NOT confined to the 14.5 cluster. Home ~14.5 (12 rules): class/control ratio for the rare colours median 2.06
(92% above 1.3); abundant colours median 0.80 (81% below 0.9). Home ~7.0 (12 rules): rare median 1.84 (100% above 1.3), abundant median 0.71 (100% below 0.9). The prediction that the
~7.0 cluster would show a weaker effect (< 1.3) is FALSIFIED; the prediction for the 14.5 cluster (median >= 1.5, >= 60% above 1.3, abundant < 0.9) held. Exceptions: RLLLLRRLLRR (rare colours
702-2255 cells, i.e. not really rare, ratios 0.94-1.3) and RRLRRRRLLLL (one abundant colour at 0.18). Caveat on interpretation: the swap construction both removes the class from its places and
injects it at random places, which the matched random control does not do in the same way; the plain recolour test (items above, two rules only) gives the smaller but same-sign
effect (1.3-1.4), so I trust the sign and the generality and not the factor 2. Mechanism for rarity: not examined (colours that the ant passes quickly or avoids; the colour census of the visited
field is flat apart from those few colours).

### Item 28 follow-up (hypothesis written 2026-10-13): 3D at 2^28

24 random blob-like cubic rules (numpy-free shuffle, seed 20261013, ) run to 2^28 steps (box 384^3). Prediction: local
volume exponent over k = 24..28 is within 0.72-0.80 (the earlier window k = 20..24 gave a median 0.816 and falling) and extent exponent within 0.23-0.27.
Falsifier: volume exponent still > 0.80 at k = 24..28 or no downward trend from the k = 20..24 value. Rotor bias in 3D is uncalibrated (the 3D rotor is transient), so a
miss would not distinguish a different exponent from slow convergence.

### Results: item 25 (turmites; `python3 experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_screens.py tm | ext 12 20 2048 64`, then `ext 16 26 8192 64 < experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/tm_candidates.txt`; `experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_tm_screen.txt`, `experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_tm_long.txt`)

Pre-registered (2026-10-13, before the screen): among 2-state 2-colour turmites (all 65536 tables, square lattice, decoded as in `Turmite::from_id`: write colour, turn N/R/U/L, next state)
that grow without a highway, the area exponent clusters at 2/3 (> 50% within 0.1); a second parameter would be needed if a distinct cluster appeared.
**Result: held, with one extra cluster.** Screen to 2^20 (47863 tables with output; the other 17673 left the 2048 board before 2^12, i.e. immediate highway/ballistic):
bounded 37068 (77%), escaped 3970, blob-like (0.5 <= a < 0.9) 3934, slow 2089 (a < 0.5), fast 802.
Blob-like tables split into two clusters: **1560 with area exponent exactly 0.500 and extent exponent 0.500** (area x8.04 over six octaves: a square-builder / growing-frame
class, as the one-state 'builder' rules; a distinct class, not cube-root) and **2290 in 0.55-0.85**. These 2290 rerun to 2^26: 2114 stay in the 8192 box; area exponent
quantiles 10/25/50/75/90 = 0.667/0.678/0.701/0.726/0.771 over k = 22..26 (median 0.708 at k = 20..24 and 0.720 at k = 16..20: falling), extent exponent 0.340; 85% within 0.1 of 2/3
(65% within 0.05). So multi-state chaotic turmites obey the same cube-root class with the same finite-window offset as one-state ants (0.68-0.70 here); no second
parameter is needed for the bulk; the separate sqrt(t) cluster is the exception. Limits: one family (2 states x 2 colours), the 0.55-0.85 selection was made from the 2^20
screen, no calibration of window bias for turmites (rotor-like bias assumed similar), duplicates under symmetry (mirror, state relabelling) not removed -- counts are tables, not distinct ants.

### Result: item 28 follow-up (`ext 20 28 64 384 < experiments/archive/2026-10-probe-growth-census/results/cube_long_specs.txt`; `experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_cube_long.txt`)

16 of the 24 chosen cubic blob rules stay in the 384^3 box to 2^28 (the other 8 left it: faster growers; selection bias toward slower growth). Volume exponent median 0.801 at k = 20..24 and
**0.788 at k = 24..28** (IQR 0.776-0.796); extent exponent 0.246 and 0.245. Pre-registered band [0.72, 0.80] for the volume exponent and [0.23, 0.27] for the extent: both held
(the volume value is close to the upper edge and still falling). Consistent with volume ~ t^(3/4), radius ~ t^(1/4) as the cup picture predicts for d = 3; not proven (no calibrated
walker in 3D; the 3D rotor is transient).

## Item 17 (partial result, 2026-10-13; run still going)

Pre-registered: ~1% of survivors (6-10 of 807) become highways in (1e9, 1e10] if the onset tail is flat; <= 3 if it is thin.
`experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e10.sh` (lean ant, 32768 board, 1e10 steps, fixed-seed shuffled chunks of 12 rules; `experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/scripts/h1e10_stats.py`, `experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10_stats.txt`).
After 12 of 68 chunks (144 rules, 17.8% unbiased sample): **7 highways** (RRRRRLRLLR onset 1.69e9, RRRRRRRRLR 2.13e9, RLRRRLLR 4.29e9, RRLRRRRRLR 6.44e9,
RLLRLRLRL 7.91e9, RRRLR 8.82e9, RLLLRLLR 9.53e9; periods 1772, 508, 16, 24, 212, 332, 564), 6 blobs reaching the board edge, 131 still unresolved. That is 4.9%
of survivors (about 39 scaled to all 807), well above the predicted ~1% and far from the thin-tail alternative: the tail is heavy, perhaps rising, so the unresolved set is NOT
mostly chaotic-forever. Caveats: 7 events (Poisson uncertainty ~ +-2.6 of 7), onsets near the budget are unconfirmed on a second board size, the last census decade was low (11). Even a 5-colour rule
(RRRLR) builds its highway only at 8.8e9 steps. The remaining chunks keep running; rerun `bash experiments/archive/2026-10-census-sweeps/scripts/regen_frontier_stats.sh` when they finish.

## Item 17 (FINAL, 2026-10-13): all 68 chunks, 807 of 807 rules to 1e10 steps

Command: `bash experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e10.sh` (sweep_lean, 32768 board); summary `experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10_stats.txt` (`uv run experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/scripts/h1e10_stats.py`).
Prediction (pre-registered, ~1% of survivors, 6-10 rules): **falsified**. Result: 38 new highways (4.7% of 807) with onset in (1e9, 1e10] **[Corrected 2026-10-21: 22 of the 38 (1e9,1e10] and 4+ of the 16 (1e10,1e11] "highways" are board artefacts; genuine yields 1.98% and 0.68-1.64% (1.64% if the 7 pending rechecks confirm); see `experiments/archive/2026-10-late-highway-board-check/README.md`.]**
(periods mostly 16/24/32 plus long ones to 1772), 37 blob grid escapes (no highway), 732 still unresolved at 1e10.
The decade yield is therefore ~2x the earlier decades (11-26 per decade), not flat or falling: the onset tail is heavy and the unresolved
set shrinks by only ~5% per decade. The earlier 12-chunk partial (7 of 144) understated it.
Caveat/oddity: 28 of 38 onsets fall in tight clusters (about 4.2932-4.2942e9 for 16 RLRRRR..-family rules, 6.4395-6.4410e9 for 9 RRLRRRR..-family
rules, 8.5875-8.5881e9 for 2). These are near 2^32, 1.5*2^32, 2*2^32 but not at them; step counters are 64-bit (checked `highway_onset_flat`,
`sweep_lean`), so I read this as related rules sharing one trajectory until a late colour is reached (shared prefix), i.e. the 38 are
~10 independent events, not 38. Not verified by a trajectory comparison; open question. Counts above are of rules, not independent mechanisms.
`cargo test --release` passes; regen_frontier_stats.sh ran clean.

## Item 10 (own investigation; the knockout agent's 5x5/3x3 refine data are the starting point)
Hypotheses, written 2026-10-13 before any single-cell run (my tool: `examples/cell1.rs`, reads `experiments/archive/2026-10-knockout-maps/dumps/RULE.grid`, same protocol as knock: fresh ant at home,
2^26 steps, near_home over the last quarter; baseline 0.4737 for RRRRRLLLLLL; I do not edit any knockout file):
- H10a: the loss of the best 3x3 windows (0.07-0.09) is carried by a few cells: some single-cell recolourings inside the window lose >= 0.02
  (the single-cell null p95 from 200 random visited cells, same recolouring rule, will be measured and reported; I expect ~0.005).
- H10b: the loss is not additive; a short list of the top single cells (<= 5) recoloured together reaches the 3x3 patch loss (>= 80% of it).
  Falsified if the top 9 cells together reach < 50% of it (hold = diffuse, no minimal set).
- H10c: the sensitive cells are not a closed cycle/object: the top cells are not connected in the ant's own trajectory loop (descriptive; I look at their colours and positions only).

### Item 10 result (2026-10-13)
Command: `cell1 experiments/archive/2026-10-knockout-maps/dumps/RULE.grid RULE 67108864 experiments/archive/2026-10-cell1/results/RULE <three 3x3 window corners>` (windows = the three lowest-near_home 3x3 windows in `experiments/archive/2026-10-knockout-maps/knock/RULE/refine3.csv`:
RRRRRLLLLLL -7,-10 -7,-11 -5,-15; RLLLLRRRRLR -1,7 1,6 -2,8), `examples/cell1.rs`; stats `uv run experiments/archive/2026-10-cell1/scripts/cell1_stats.py` -> `experiments/archive/2026-10-cell1/results/cell1_stats.txt`. Each run is a deterministic fresh ant, 2^26 steps.
Scan: every visited cell within 1 of those windows (52 / 47 cells) x every other colour (10 alternatives) = 520 / 470 single-cell recolourings; null = 200 random visited cells anywhere, random other colour.
- **H10a supported.** Single-cell null: mean loss 0.002 / 0.004, p95 0.0065 / 0.0088, p99 0.011 / 0.016, max 0.025 / 0.036. In the scan the worst recolouring of a single cell loses
  0.039 / 0.046 (8-9% of the tether); all 52 / 46 of 47 cells exceed the null p95, 29 / 20 exceed the null max. A single cell can matter, but the typical recolouring costs only 0.01.
- **H10b supported in the weak form.** Top-k cells each at their worst colour, recoloured together: k=3 gives 0.081 / 0.136 (the 3x3 patch loss is 0.07-0.09), and the
  curve saturates at ~0.13-0.16 (the 5x5 patch loss, 25-30% of the tether), non-monotone (k=4 for RLLLLRRRRLR is lower than k=3). Not additive: 3 cells = 2.1x/3.0x the best single.
  So a handful (3) of cells reproduces the 3x3 effect, but no handful removes the tether.
- **Second-cell scan:** with the top cell already recoloured, 210 of 510 / 229 of 460 further recolourings exceed the top cell alone (max 0.084 / 0.105): many partners, no unique pair.
- **H10c (descriptive): no closed cycle or small object found.** The sensitive cells (~50, all above null p95) form a patch about 5 cells across, not a few special cells;
  their old colours vary (0,2,3,5,9,10 ...) and the worst new colours are mostly the high/rare ones (6, 8, 10). The hold is "diffuse locally": a region where almost any cell matters at the 1-4% level
  and a few at 4-5%, rather than a minimal return path. Consistent with items 11 and 14 (the carrier is a statistical, rare-colour-rich neighbourhood).
Caveats: windows were chosen as the worst of the knockout map (winner's curse; the random-cell null is not location-matched, so the comparison overstates specificity - only the ratio
top-cell loss / typical-cell-in-window loss (4x) is location-free); one field per rule at 2^24, one deterministic outcome per recolouring; the scan covers about 50 cells around three windows only.

### Verification notes (2026-10-13)
`bash experiments/archive/2026-10-census-sweeps/scripts/regen_frontier_stats.sh` run twice (txt and b suffix), all outputs byte-identical (including the new cell1_stats). `cargo test --release` all suites pass.
The web cup overlay was NOT inspected by eye: the Chrome extension was not connected in this session. It is covered by the Rust cross-check and jsdom smoke tests only.
