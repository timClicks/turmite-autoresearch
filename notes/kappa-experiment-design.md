# What sets kappa? Experiment design (written 2026-10-13, before any run)

Status: DESIGN ONLY. No arm below has been run. Predictions are fixed here and must
not be edited after data arrive; append results and revisions underneath.

## Where we are

- kappa = (B/S) / (P/A): how much more (or less) often the walker stands on an edge
  cell than a uniform spread over the territory would put it there.
- Measured: rotor 2.0; ants median 0.9, rule-specific (ICC 0.58, `experiments/archive/2026-10-a1-kappa/results/a1b_icc.txt`)
  but not predicted by letters, q, edge colour mix, prefixes or substrings
  (`experiments/archive/2026-10-a1-kappa/results/a1_kappa_proxy.txt`, `a1c_predict.txt`, `a1_edge_q.txt`); memoryless
  persistent walker 1.3-1.45 with area exponent 0.95 (A1d, `experiments/archive/2026-10-a1-kappa/results/a1d_stats.txt`).
- Bookkeeping that frames the design (algebra, from the paper's definitions):
  kappa * c = (dA/dt) * (A/P). With R^3 = K t and P = p R this makes kappa*c a
  function of the growth prefactor K and the edge roughness p. So "why kappa" is the
  same question as "what sets K, given c and p". c is already predicted by the
  letters (R^2 0.78); kappa is the leftover.
- The A3 note says kappa changes only a thin edge layer, not the bulk integral.
  Nobody has measured how thin, or what the layer looks like.

## Question

Is kappa (a) a *local* property of the first cell layer, set by what an edge cell does
to a walker that lands on it (stickiness), or (b) a *graded* boundary-layer property,
a depletion/enhancement of walker density over many cells set by an extrapolation
length, as for a partially absorbing wall in a diffusion problem?

These predict different, cheap-to-measure things, and different ways kappa varies
between rules.

## Arm A: edge-layer anatomy (observational, the discriminating arm)

Measure the instantaneous visit density as a function of distance d from the edge,
where d is the Manhattan distance to the nearest never-visited cell (d = 0 is the
current "edge"), for d = 0..6, in octave windows k = 22..26.

- rho(d) = (visits to cells at layer d in the window / cells at layer d) divided by
  (S / A). rho(0) is kappa by construction (check: must reproduce the probe's kappa
  within 2%). This check is the instrument calibration.
- Also per window: the mean number of visits an edge cell receives during its edge
  phase, v_e (the identity c = 1/v_e for steady growth is a second check), and the
  edge-phase lifetime.
- Walkers: the 12 rules of the `item4` stratified set, six chosen to be low-kappa and
  six high-kappa from `experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv` rule means (selection rule: lowest/highest
  six rule-mean kappa among rules with >= 6 core-band runs, stated before the run);
  the rotor, 12 seeds; the memoryless walker at Q = 0.5, 6 seeds. Ants run from the
  blank board, 3 patched starts each for within-rule noise.
- Implementation: extend `src/probe.rs` with an optional layer tally (neighbourhood
  scan of radius 6 on first reaching a cell is too costly per step; instead keep a
  per-cell "distance to nearest unvisited" lower bound refreshed when a neighbour is
  first visited, capped at 6). Property-test the tally against a brute-force layer
  count on small boards for fast/reference parity, as AGENTS.md requires.

Predictions, fixed now:

- A1 (local, "thin layer"): rho(d) is within 10% of 1 for d >= 2 for every ant rule and
  the rotor; all of the kappa difference between rules lives in d = 0 and d = 1.
- A2: in the rotor rho(0) = 2.0 +- 0.1 and rho(1) is between 1.1 and 1.5 (the rotor's
  Eulerian rule keeps it at the edge until the unvisited neighbours are used up).
- A3: for ants, rho(0) tracks 1/c across rules: Spearman(rho(0), v_e) >= 0.5 over the
  12 rules. If instead rho(0) is uncorrelated with v_e, the "stickiness is dwell time"
  idea fails even though kappa*c = Adot*A/P holds algebraically.
- A4 (memoryless walker): rho(d) rises smoothly over >= 4 layers (graded, a diffusive
  boundary layer), unlike A1. This is the contrast case.

Decision rule: A1 and A3 both hold -> kappa is a local stickiness property, go to Arm
B. A1 fails with a graded profile whose length ell correlates with kappa across rules
-> boundary-layer picture, go to Arm C. A1 fails and A3 fails -> neither picture; report as
unexplained and stop.

## Arm B: noisy rotor, a handle on memory (interventional)

Rotor variant with probability eps of replacing the usual quarter-turn by a uniform
random arrow at each visit (eps = 0 is the rotor; eps = 1 is a memoryless walker).
Run eps in {0, 0.001, 0.003, 0.01, 0.03, 0.1, 1}, 8 seeds each, to 2^28 on a 32768
board, standard windows (k = 20..26, and k = 22..28 to see the crossover).

Predictions, fixed now:

- B1: for any eps > 0 the area exponent drifts from 2/3 toward 1 with a crossover time
  t*(eps) that falls as eps rises; for eps <= 0.003 the k = 20..26 window sits below
  the crossover and still reads 0.66-0.70.
- B2: within the window below crossover, kappa(eps) declines monotonically from 2.0 as
  eps rises (Spearman with eps <= -0.9 over the five smallest eps), reaching
  about 1.4 at eps = 1. If kappa stays near 2.0 while the exponent has already
  crossed over, kappa is not what the memory controls.
- B3: kappa*c vs (dA/dt)*(A/P) holds at every eps (algebra; a check on the code).

Decision: B2 supported -> kappa is controlled by how much of the rotor's deterministic
exit structure survives, and Arm A's v_e should fall with eps in step with kappa.
Report the eps at which kappa has lost half its excess over 1.4.

## Arm C: rule family with matched letters (only if A1 fails)

Take pairs of rules with equal n and q and equal c (within 0.02) but kappa differing by
>= 0.5 (search `experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv`; report how many pairs exist; if fewer than
10, the arm is dropped). For each pair, measure rho(d) and compare the length ell of
the profile. Prediction: ell differs between members of a pair in the direction of
kappa (longer depletion layer, lower kappa). This is the only arm that targets the
rule-specificity (ICC 0.58) directly.

## Controls and sample sizes

- Positive control: c from the same layer tally reproduces the probe's c; the c
  letter model (R^2 0.78) already shows the instrument can see rule dependence.
- Negative control: the memoryless walker has no rule or memory dependence, so
  between-seed ICC of rho(0) must be < 0.2.
- Seeds and rules fixed in the spec files; all randomness seeded; results keyed by
  (walker, seed) so thread count cannot change them. Arm A about 2 CPU-hours at 2^26
  with the tally; Arm B about 4 CPU-hours at 2^28.

## What would count as explaining kappa

A closed-form or one-parameter prediction of rule-mean kappa that has held-out
R^2 >= 0.3 on the 192 rules with >= 6 core-band runs, using only quantities measured
in Arm A (for example v_e and ell). Anything less is a description of the edge layer,
not an explanation, and the paper should say so.

## Not covered

The asymptotic edge exponent and the ants' wider edge (surface width exponent 0.22-0.25
against 0.12 for the rotor) are not tested by this design. If rho(d) differs between
ant and rotor beyond d = 1, Arm A gives a first quantitative handle on the width
difference; otherwise those items stay open.

## Arm A results, extreme-kappa ants (done 2026-10-13)
Commands: `uv run experiments/archive/2026-10-layers-colours/scripts/layers_select.py` (6 lowest + 6 highest rule-mean kappa of 152 rules with >= 6 core-band runs; blank board) -> `experiments/archive/2026-10-layers-colours/results/layers_specs.txt`; `layers 26 8192 < experiments/archive/2026-10-layers-colours/results/layers_specs.txt > experiments/archive/2026-10-layers-colours/results/layers.csv` (`examples/layers.rs`); `uv run experiments/archive/2026-10-layers-colours/scripts/layers_stats.py > experiments/archive/2026-10-layers-colours/results/layers_stats.txt`. Windows k = 22..25 (the run stops at 2^26, so the planned k = 26 window is missing). Deviations from the design: no patched starts for the ants (blank board only, so no within-rule noise estimate); 1 of 6 memoryless seeds escaped the 8192 board and the others have 1-2 windows; layer census is exact (distance transform), step layers by ball scan; the property test against brute force was not written (instead the census layer 0 equals the probe perimeter in every row, asserted in the stats script).
Instrument checks: rho(0) matches the probe's kappa within 10% (rotor 1.83 with the mean-census normalisation, 2.00 with the probe's end-of-window normalisation).
- A2 (rotor rho0 2.0 +- 0.1, rho1 in 1.1-1.5): rho1 = 1.11 holds; rho0 = 1.83 in the layer normalisation, 2.00 in the probe's: half-held, the 8% gap is the normalisation.
- A1 (thin layer, |rho(d)-1| < 0.1 for d >= 2) **FAILS for the 12 selected ants**: median max deviation 0.93. Their profile is: rho0 and rho1 far from 1 (0.12-0.46 for low-kappa rules, 3-15 for high), rho2-4 near 0 (0.01-0.6), bulk (d >= 5) near 1. It holds for the rotor (median 0.09) and approximately for the memoryless walker (0.16, graded, falling 1.4 -> 0.8).
- A3 (rho0 tracks dwell v_e) **FAILS**: Spearman(rho0, v_e) = -0.26 (p = 0.42); v_e = 1.5 for 10 of 12 ants whatever their kappa (0.12 to 15). kappa is not a dwell-time effect. Spearman(rho0, rho1) = 0.99: the two outer layers move together.
- A4 holds weakly (graded profile for the memoryless walker; 5 walkers, few windows).
Caveat that changes the reading: selecting the six lowest and six highest of a heavy-tailed distribution picked atypical rules (kappa 0.08 to 11), whose territories have a thin active shell separated from the bulk by a nearly unvisited crust, not a mixed blob. The thin-layer question for *typical* ants (kappa near the median 0.9) is therefore untested; the follow-up below targets it.

### A1-typical follow-up (exploratory, added after seeing the above; prediction written before the run)
The 12 rules with rule-mean kappa closest to 0.9 (same pool). Prediction P-typ: |rho(d) - 1| < 0.15 for d = 2..4 for at least 9 of 12, and Spearman(rho0, v_e) >= 0.5 over the 12 (kappa varies little there, so a weak test). If P-typ holds, the extreme-kappa rules are a separate regime (shell plus crust) and the typical ant's kappa is a local edge effect; if it fails, the crust is generic.

### A1-typical result and exploratory classes (done 2026-10-13)
Commands: `layers 26 8192 < experiments/archive/2026-10-layers-colours/results/layers_specs_typical.txt > experiments/archive/2026-10-layers-colours/results/layers_typical.csv`; `uv run experiments/archive/2026-10-layers-colours/scripts/layers_stats_typical.py` -> `experiments/archive/2026-10-layers-colours/results/layers_stats_typical.txt`; exploratory (not pre-registered) `experiments/archive/2026-10-layers-colours/scripts/layers_classes.py` -> `experiments/archive/2026-10-layers-colours/results/layers_classes.txt`, `experiments/archive/2026-10-layers-colours/scripts/layers_census_c.py` -> `experiments/archive/2026-10-layers-colours/results/layers_census_c.txt`.
- P-typ **FAILS**: only 6 of 12 typical-kappa rules have |rho(d)-1| < 0.15 for d = 2..4 (needed >= 9). Spearman(rho0, v_e) = -0.59 (p = 0.04), the opposite sign to the prediction (>= +0.5).
- Exploratory finding, labelled as such: the 24 ants split into two classes by the shape of the edge layers. *Crust* (15 of 24): layers 2-4 are almost unvisited (rho 0.01-0.6) and the walker is concentrated in layers 0-1; they have c = 0.64-0.66 and edge dwell v_e = 1.5 almost exactly (with two exceptions at c 0.44-0.48), yet kappa from 0.13 to 18.3. *Uniform* (9 of 24): rho(d) within 0.3 of 1, c = 0.27-0.48, v_e = 2.1-3.7, kappa 0.82-0.96. The uniform class's kappa range is truncated by the selection (the typical set was chosen near 0.9), so the tightness is not evidence of a law; within it Spearman(kappa, v_e) = 0.02 (n = 9).
- The crust class is not rare in the census: 319 of 2622 blob rules (12%) have c >= 0.6, with a spike of 263 in [0.65, 0.70) (`experiments/archive/2026-10-layers-colours/results/layers_census_c.txt`), and the median kappa of that group (0.80, IQR 0.57-1.17) is close to the rest (0.91): the extremes tested above are tails of a class whose typical kappa is ordinary.
Reading against the design's decision rule: A1 fails and A3 fails, so neither "thin local stickiness" nor "dwell time" explains kappa. What Arm A does give is a structural classification (crust vs uniform) that c tracks (c is pinned near 0.65 for the crust class), and the fact that within the crust class c and v_e are constant while kappa varies by two orders of magnitude, so kappa is set by something other than the edge-entry statistics: the ratio of occupation of layers 0-1 to the bulk. That is the one-sentence form of "emergent property of each rule's dynamics". kappa is still not predicted; Arms B and C were not run.
Not done: Arm B (noisy rotor), Arm C (matched pairs), the property test of the layer tally against brute force, patched starts, the 2^26 window. All predictions above, including the failures, stand as written.

## Arm B results, noisy rotor (done 2026-10-13)
Commands: `probe 27 16384 < experiments/archive/2026-10-arm-kappa-depletion-arms/results/armb_specs.txt > experiments/archive/2026-10-arm-kappa-depletion-arms/results/armb_probe.csv` (`nrotor:EPS:SEED`, `NoisyRotor` in `src/walkers.rs`; eps in {0, .001, .003, .01, .03, .1} x 8 seeds; eps = 1 is the memoryless walker of A1d), `uv run experiments/archive/2026-10-arm-kappa-depletion-arms/scripts/armb_stats.py > experiments/archive/2026-10-arm-kappa-depletion-arms/results/armb_stats.txt`. Windows k = 20..26 (design said 22..28; the run stops at 2^27). 38 of 48 runs fitted: 10 left the 16384 board or lacked a window (eps .01: 7 of 8 fitted, .03: 6, .1: 1), so the eps = 0.1 row is a single run.
Code check: eps = 0 reproduces the rotor (area exponent 0.688, kappa 2.00, c 0.498).
- B1 **FAILS in its detail**: the area exponent leaves 2/3 at every eps tested, including 0.001 (0.76), 0.003 (0.85), 0.01 (0.91), 0.03 (0.94). I had predicted eps <= 0.003 would still read 0.66-0.70 in this window; the crossover is earlier than that. The direction (towards 1, crossover earlier for larger eps) holds.
- B2 **FAILS**: kappa does not fall from 2.0 towards 1.4; it rises to 3.55, 5.83, 6.65 (eps .001, .003, .01), then falls (3.76 at .03, 2.63 at .1, one run). Spearman(kappa, eps) over eps <= 0.03 = +0.70 (p = 0.19), the opposite sign to the prediction. The drift exponent of kappa is positive (0.12-0.19), so these runs are not stationary: kappa is read in the middle of the crossover from t^(1/3) to diffusive growth, and the large values are transient.
- B3 holds (the identity kappa*c = (dA/dt)(A/P) is satisfied exactly, as expected: it is algebra).
- Unplanned observation: c stays at 0.498-0.499 for every eps from 0 to 0.1 while kappa varies between 2.0 and 6.7. So c is set by the local rule at the edge (an arrow update), and kappa is not a function of c; the same decoupling appeared in the crust class of the ants.
Reading: a small amount of memory noise raises kappa by up to a factor 3 and destroys the cube root, so the rotor's kappa = 2 is a property of exact Eulerian memory, not of generic persistent motion; the ants' kappa behaves like an emergent property of memory too. This is consistent with A1d and A1b-c but is not a prediction of kappa. Arm C (matched pairs) was not run.

## Arm C (feasibility and pre-registration, 2026-10-13, before the run)
`experiments/archive/2026-10-arm-kappa-depletion-arms/scripts/armc_pairs.py` -> `experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_pairs.txt`: among the 152 rules with >= 6 core-band runs there are 26 pairs with equal n, equal number of R, rule-mean c within 0.02 and rule-mean kappa differing by >= 0.5. (Rule-mean kappa has within-rule sd ~0.37, so some pairs are selected partly on noise.)
Statistic fixed now: depletion D = mean over d = 2..4 of (1 - rho(d)) from the layer tally on the blank board (windows k = 22..25, as Arm A). Prediction: the lower-kappa member of a pair has the larger D in at least 18 of the 26 pairs (one-sided sign test p < 0.05). If it holds, the depth of the depleted crust is what separates equal-letter, equal-c rules, and a model of the crust depth is the next target; if not, the crust class does not explain kappa either. Pairs where either member escapes the 8192 board are dropped and counted.

### Arm C result (done 2026-10-13)
`layers 26 8192 < experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_specs.txt > experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_layers.csv` (44 rules from 26 pairs), `uv run experiments/archive/2026-10-arm-kappa-depletion-arms/scripts/armc_stats.py > experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_stats.txt`. All 26 pairs usable.
- Prediction **FAILS**: the lower-kappa member has the larger depletion D in 13 of 26 pairs (needed >= 18; one-sided sign test p = 0.58). Crust depth does not separate rules with equal letters-count, equal length and equal c.
- Side result: the blank-board kappa from this independent run type orders the pair the same way as the patched-start rule means in 25 of 26 pairs. The rule dependence of kappa is therefore robust across run type, not a selection artefact, which strengthens the A1b ICC (0.58) result.
Overall for the A1 programme: five mechanisms/predictors tested (letters, edge colour mix, memoryless persistent walk, edge-layer shape and dwell, crust depth in matched pairs) and the noisy-rotor intervention; none predicts kappa. The rule-specific part of kappa is real and unexplained.
