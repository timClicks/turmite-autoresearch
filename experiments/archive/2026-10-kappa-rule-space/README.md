# What sets kappa? A rule-space and mechanism programme

Status (updated 2026-10-15): the W6 matched-area reanalysis of the pilot pairs has been run (M1 held, M2 failed: early letters change kappa at fixed area in both directions; see the Log, last entry). Stage 1, W3b, W4, W5, the W6 pilot and W3c have been run (W3c: primary P3c.1 held on the stationary cohort; W5: P5.1 FAILED, best bulk observable adds +0.04 held-out R^2 over ln A(22) against a 0.15 bar, P5.3 failed for the primary I_turn; see the Log). OPEN, not run: W3 proper, the area-matched mutation test and the 200-base W6 (deferred by scope; the 200-base W6 needs a registered addendum and ~8 CPU-hours). Original header: plan written 2026-10-14 (~18:45 +13:00), git HEAD `99de7c1` with a dirty working
tree. **Stage 1 (W0, W1, W2, W7) has been run; see the Log at the end. Stage 2 (W3 proper) and
Stage 3 had not at that time (W4, W5 and the W6 pilot have since; see the Log).** Every prediction in a "Pre-registered" block is fixed by the plan
timestamp; do not edit them after data arrive. Append results, revisions and deviations
under "Log" at the end, each with its own timestamp.

Supersedes nothing. It continues `notes/kappa-experiment-design.md` (Arms A, B, C),
`notes/excursion-tomography-2026-10-13.md` (T1, T1b; read its section 6 retraction first)
and `notes/research-frontier-2026-10-13-pm.md` section F.

## 1. Question

kappa = (B/S) / (P/A) is how much more often the walker starts a step on a boundary cell
than a uniform spread over the territory would put it there (B boundary steps, S steps,
P perimeter, A area; see `src/probe.rs`, `experiments/_lib/analyse_probe.py`).

**What property of an ant rule, or of the dynamics it generates, determines its
rule-mean kappa?**

Two framings keep the work honest:

- kappa is the growth prefactor in disguise. A^(3/2) = (3/2) c kappa g t with
  P = g sqrt(A), so at fixed t, kappa and area are tied. Anything that merely tracks
  size will "predict" kappa. T1 fell into this; every predictor here is tested **after**
  conditioning on ln A at the same window (section 4.4).
- "Explained" is a bar, not a feeling: held-out R^2 >= 0.3 on rule-mean ln kappa for
  rules not used to build the predictor (`notes/kappa-experiment-design.md`, "What would
  count as explaining kappa"). Anything less is a description.

## 2. What is already known, and what is out

Facts this plan stands on (sources are the existing files, not re-derived here):

| Fact | Source |
|---|---|
| Rotor kappa 2.00, c 0.498; memoryless persistent walker 1.3-1.45 | `experiments/archive/2026-10-a1-kappa/results/a1d_stats.txt`, T1 controls |
| ln kappa ICC across patched starts: 0.625 (b2 core band, 99 rules), 0.630 (item21, 58 rules); between-rule sd of ln kappa about 0.39-0.69 | `experiments/archive/2026-10-a1-kappa/results/a1b_icc.txt` |
| Rule-mean ln kappa sd 0.50 over 192 rules with >= 6 core-band runs (the armc/layers design pool says 152; **W0 pins down which**) | `experiments/archive/2026-10-a1-kappa/results/a1c_predict.txt` |
| Letters, substring counts, edge colour mix: LOO R^2 about -0.06..+0.04. Prefix-5 neighbour mean: +0.039 | `experiments/archive/2026-10-a1-kappa/results/a1c_predict.txt`, `a1_kappa_proxy.txt` |
| Edge dwell v_e is about 1.5 for 10 of 12 extreme rules whatever kappa (0.12 to 15); crust vs uniform classes; c pinned near 0.65 in crust class | Arm A, `experiments/archive/2026-10-layers-colours/results/layers_stats*.txt` |
| Matched pairs (equal n, q, c, kappa gap >= 0.5): crust depth does not separate them (13/26) | Arm C, `experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_stats.txt` |
| 83% of blob rules have |kappa drift exponent| < 0.05; the width-exponent outliers are drifting-kappa rules | `notes/summary-2026-10-13.md` |
| Noisy rotor: kappa rises to 3.5-6.7 during crossover, c stays 0.498 | Arm B |
| T1/T1b excursion statistics: null after audit; typical excursion is rule-independent; only extreme-tail partial r about -0.4 (does not survive Bonferroni) | excursion-tomography section 6 |
| Census canonical form keeps rules starting with R; mirror images are not separate rules | `src/rule.rs:41` |

Out, do not re-test: letter content, edge colour mix, dwell, crust depth, memoryless
persistence, whole-distribution excursion duration/depth/chord length.

## 3. Strategy: find out which kind of answer exists before searching for it

The programme is staged so that cheap existing-data checks decide whether the expensive
ones are worth doing.

- **Stage 1 (existing data, no new runs):** W0 harness and instrument check, W1 rule-space
  smoothness, W2 stationarity audit, W7 when kappa is set. About one to two working days.
- **Stage 2 (new tally code plus moderate runs):** W3 invariant rule features, W4
  colour-resolved decomposition, W5 bulk fingerprint.
- **Stage 3 (gated, design finalised at the gate):** W6 mutation scan, W8 strip geometry,
  W9 surrogate-field ladder, W10 theory (front matching). Not pre-registered in detail
  here; each gets a dated addendum, with predictions, before its first run.

Decision tree after Stage 1:

```
W1 rule-space r (ln kappa, Hamming-1 neighbours)
 |- r_obs >= 0.30 (smooth)       -> W3 gets priority, then W6; rule features are worth searching
 |- 0.15 < r_obs < 0.30 (mixed)  -> W3 and W5 both; run W6 pilot (50 bases) to sharpen
 `- r_obs <= 0.15 (rugged)       -> drop feature hunting in the rule string beyond the W3
                                    pre-registered list; prioritise W4, W5, W7, then W8-W10
W2 stationarity
 |- tail (kappa > 3) is mostly drifting rules -> restrict every later analysis to the stationary
 |                                              set and state the restriction in every table
 `- tail is stationary -> the heavy tail is a genuine property; W4(c) becomes the lead question
W7 emergence time
 |- rank order fixed by k <= 14 -> small-scale dynamics carry kappa; W5 can use short runs
 `- fixed only at k >= 20      -> self-organised; W5 must use matured fields (it does)
```

## 4. Common machinery (all workstreams)

### 4.1 Cohorts

| Name | What | File | Notes |
|---|---|---|---|
| census | 2630 blob-class rules, one blank-board run each, k = 20..26 fit; `kappa` is the last window, `g_k` is the log-log drift slope | `experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv` (`cls == blob`) | single run, so reliability about 0.6 on ln kappa; **8 more than the 2622 quoted in notes: W0 reconciles** |
| b2 | 99 rules x about 12 patched starts (`RULE@SEED`) | `experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv` | k = 9..26 windows; core band 0.25 < alpha_w < 0.42 |
| item21 | 98 further rules, patched starts | `experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv` | |
| pool | rules with >= 6 core-band runs from b2 + item21 (152 or 192) | `experiments/archive/2026-10-a1-kappa/scripts/a1c_predict.py` logic | the "held-out confirmation" set |
| armc | 44 rules in 26 matched pairs | `experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_pairs.txt`, `experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_specs.txt` | |
| controls | rotor, `pw:Q` memoryless walker, shuffled-label permutations | `src/walkers.rs` | |

### 4.2 Unit of inference and noise ceiling

- The unit is the **rule**. Pair-based tests (W1) resample rules by bootstrap because rules
  appear in many pairs; the 26 armc pairs are not 26 independent experiments.
- Noise ceiling: ln kappa reliability is about 0.6, so the best possible held-out R^2 on
  rule-mean ln kappa from perfectly known true kappa is about 0.6 for a single run and
  higher for 12-run means. Report every R^2 together with the ceiling and as a fraction of
  it. For pair correlations, the observed r is attenuated by about 0.6: r_obs = 0.3 means
  r_true about 0.5.

### 4.3 Held-out protocol

- **Discovery** on census minus pool (rule-disjoint), single-run kappa. **Confirmation** on
  pool rule means. Feature sets, models and thresholds are fixed in the pre-registration
  blocks before the confirmation split is touched.
- Cross-validation inside discovery is grouped by length-n and 5-prefix so near-duplicate
  rules do not straddle folds. Seeds: `numpy.random.default_rng(20261014)` for folds,
  permutations and bootstraps; the seed is printed in every output header.
- Power: with n = 152 and one degree of freedom, an R^2 of about 0.05 is the smallest
  detectable at 80% power (alpha = 0.05); held-out R^2 is more conservative. State this when
  reporting nulls. A **planted-signal check** is run first: synthesise ln kappa = beta * x +
  noise at reliability 0.6 on the real rule set and confirm the pipeline recovers the planted
  R^2 (a pipeline that cannot see a planted effect makes a null meaningless).

### 4.4 Controls applied to every predictor

1. **Size control.** Report the partial association given ln A at the same window; any
   result that vanishes given ln A is size contamination (T1 section 6).
2. **Drift control.** Repeat on the stationary subset (|g_k| < 0.05); report both.
3. **Class control.** Report crust vs uniform separately where the class is known.
4. **Negative control.** Permute kappa across rules of equal n (10^4 permutations) and report
   the null distribution of the statistic.
5. **Positive control.** The same pipeline on c (letters give R^2 about 0.66-0.78) must
   succeed; if it does not, the pipeline is broken and nothing it says about kappa counts.

### 4.5 Multiplicity

Primary tests are those in "Pre-registered" blocks (count them in section 8; Holm
correction over that family). Anything else is exploratory and labelled as such in the log.

### 4.6 Reproducibility rules specific to this folder

- Layout: `scripts/` (Python under `uv`, PEP 723 headers), `results/` (small, committed,
  with a header line giving command, git commit, seeds), `experiments/archive/2026-10-knockout-maps/dumps/` and `scratch/` (ignored).
- New Rust code: examples are prefixed with the slug (`examples/kappa_rs_*.rs`); a
  property test against `reference` lives in `tests/kappa_rs_*.rs`, **written and passing
  before the example is used for any result**. `cargo test --release` must pass.
- Sweeps are keyed by (rule, seed), written in input order, with `*.done` markers so a
  rerun reproduces identical bytes regardless of thread count.
- WSL wrapper for everything (see `AGENTS.md`):
  `wsl -e bash -lc "export UV_PROJECT_ENVIRONMENT=\$HOME/.venvs/turmite UV_LINK_MODE=copy && cd /mnt/f/Code/turmite && uv run experiments/archive/2026-10-kappa-rule-space/scripts/NAME.py"`.
- No existing file under `data/` or `notes/` is modified. Outputs land here; findings are
  promoted to `notes/` at the end (section 10).

## 5. Stage 1: existing data

### W0. Harness, reconciliation and instrument check

Goal: one tidy table everything else reads, plus proof that it reproduces known numbers.

- `scripts/w0_build.py` reads the cohorts above and writes `results/rules.csv` with one row
  per rule: rule, n, #R, #L, cohort flags, census kappa/c/g_k/alpha_w/area/perimeter at
  k = 26, pool rule means of ln kappa, c, g_k, ln A(k = 22), seed counts, within-rule sd.
- Reconcile the three counts (2630 / 2622 blob rules; 152 / 192 pool). Write the reason
  to `results/w0_reconcile.txt`. If unclear, use the stricter set and say so.
- **Instrument checks (all must pass before W1-W7 proceed):**
  1. Reproduce `experiments/archive/2026-10-a1-kappa/results/a1b_icc.txt` ICC for ln kappa within 0.01 (0.625 b2 core band).
  2. Reproduce the `a1c_predict` letter-by-position ridge LOO R^2 (about -0.04) with the
     new CV code. This is the **baseline** all W3 models are measured against.
  3. Planted-signal recovery (section 4.3).
  4. Positive control: letters predict c with held-out R^2 >= 0.5.
- Cost: minutes. Output: `results/rules.csv`, `results/w0_checks.txt`.

### W1. Is kappa smooth in rule space?

**Question.** Do rules one letter apart have correlated kappa? This decides whether any
rule-string feature can work.

**Method.**
- Neighbour definition: flip one letter at position j in an n-letter rule, then
  canonicalise by mirror (swap all L/R if the first letter became L). Flipping position 0
  therefore maps to the all-other-positions-flipped mirror; keep it, tagged `j = 0`.
  Secondary neighbours: delete or append the last letter (n +- 1). Tertiary: Hamming
  distance 2, 3, 4 for a variogram.
- Both members must be fitted census blob rules. Report the number of pairs per n before
  looking at any correlation; require >= 300 Hamming-1 pairs in total to conclude, else
  say the test is underpowered.
- Statistics: Pearson and Spearman of ln kappa across pairs; the same for c (positive
  control), ln A(22) (size), and alpha_w. Null: permute kappa among equal-n rules, 10^4
  times. Bootstrap CI: resample rules (not pairs), recompute pairs. Stratify by j.
- Attenuation: report r_obs and r_obs / 0.6.
- Compare with the pool's patched means for the subset of neighbour pairs that both lie in
  the pool (a cleaner, less noisy r on a small set).

**Pre-registered.**
- P1.1 (positive control): r(c) over Hamming-1 pairs >= 0.5. If not, the neighbour
  construction is wrong; stop and fix.
- P1.2: r_obs(ln kappa) <= 0.15, with the upper end of the 95% bootstrap CI below 0.30.
  Basis: letters and 5-prefix neighbours already give R^2 of 0.04 or less.
- P1.3: the effect of position is weak: r_obs for j >= 4 is not larger than for j <= 1 by
  more than 0.10.
- P1.4 (variogram): ln kappa correlation falls monotonically with Hamming distance, but
  is within 0.05 of the permutation null from distance 2 onward.

**Breaks the hypothesis (kappa is smooth):** r_obs >= 0.30. Then follow the decision tree.

Cost: minutes. Output: `results/w1_pairs.csv`, `results/w1_stats.txt`, one figure.

### W2. Stationarity audit of the heavy tail

**Question.** How much of kappa's dynamic range (0.08 to 184 across rules) and of its
unexplained rule-dependence is a drifting-kappa artefact?

**Method.**
- Rule-level drift = median across seeds of g_k (pool) or single-run g_k (census).
  Stationary: |g_k| < 0.05 (the criterion used in the summary). Sensitivity table at
  0.03 / 0.05 / 0.10.
- Compare rule-mean ln kappa distributions, ICC (reuse `a1b_icc.py` logic), and the W0
  letter baseline R^2 on stationary vs non-stationary rules. Check specifically the armc
  rules with kappa > 5 (T1 reports 0.24 to 183.9): what are their g_k, and do their
  kappa(k) curves flatten?
- Selecting on drift conditions on an outcome of the same dynamics; label this clearly
  as a descriptive restriction, and run the sensitivity table to show the restriction is
  not doing the work.

**Pre-registered.**
- P2.1: among rules with rule-mean kappa > 3, at least 50% are non-stationary.
- P2.2: sd of rule-mean ln kappa among stationary rules is <= 0.7 times the sd among all
  rules.
- P2.3: ICC of ln kappa among stationary pool rules is >= 0.45 (rule dependence survives
  removal of drifters).
- P2.4: letter-baseline held-out R^2 on the stationary subset stays <= 0.10 (drift
  contamination was not why letters failed).

**Interpretation.** P2.1-P2.2 true and P2.3 true: the tail was drift, the genuine target is a
narrower distribution. P2.3 false: most of the rule dependence was drift, and the
"rule-specific kappa" claim needs restating. P2.1 false: the tail is real.

Cost: minutes. Output: `results/w2_stationarity.txt`, one figure.

### W7. When is kappa determined?

**Question.** At which octave does a rule's kappa rank order settle? Uses the k = 9..26
windows already in `b2_probe.csv`.

**Method.** For each window k, Spearman between rule-mean kappa(k) (core-band seeds) and
kappa(26); ICC per k; also the share of variance of ln kappa(26) captured by kappa(k) after
ln A(k). Restrict to windows with >= 200 boundary steps per run (small k is count noise;
report the cutoff). Stationary subset and full set, as W2.

**Pre-registered.**
- P7.1: Spearman(kappa(k), kappa(26)) >= 0.8 for every k >= 16, and >= 0.6 already at k = 12.
  Basis: kappa is flat in time for most rules, so rank order should be an early fixture.
- P7.2: for the non-stationary rules the crossing point is later (k >= 20) than for the
  stationary rules by at least 4 octaves.

**Consequence.** P7.1 true: the information is small-scale, so exhaustive small-scale
analysis (W4, W5 on short runs) is legitimate. False: kappa is emergent at scale.

Cost: minutes. Output: `results/w7_emergence.txt`, one figure (rank correlation vs k).

## 6. Stage 2: features and tallies

### W3. Invariant and nonlinear rule features, with a discovery/confirmation split

**Question.** Did the letters-and-substrings analyses miss a structural feature of the rule
because the models were linear in letters?

**Feature families (fixed now, 14 in total; no others enter the primary family):**

| ID | Feature | Rationale |
|---|---|---|
| f1 | n | rule length |
| f2 | q = #R / n | known to matter for c |
| f3 | winding w = (#R - #L) mod 4, as a 4-level factor | net rotation per full colour cycle; w = 0 closes the cycle like the rotor |
| f4 | n mod 2 | lattice parity |
| f5 | (n, w) joint factor | |
| f6 | number of R-runs and longest run | texture of the rule |
| f7 | length of the leading run | first colours act on a fresh board |
| f8 | prefix-3 as a factor | |
| f9 | alternation count (RL or LR adjacencies) | |
| f10 | cyclic-rotation class of the rule (necklace id) as a factor; leave-class-out CV | tests dependence on the background colour only |
| f11 | partial sums of turns: the full walk S_j = sum_{i<=j} turn_i, summarised by min, max, and the number of returns to 0 | an arrow-path picture of the rule |
| f12 | q within the first half vs the second half | |
| f13 | the colour-occupancy vector pi_k from the colourstats snapshot (W4 output), entropy of pi | mixing, from dynamics rather than letters |
| f14 | c itself | known to be set by letters; tests whether kappa is a function of c |

**Models.** Group-mean encoding with shrinkage, ridge on one-hot features, and a depth-3
regression tree (own implementation in numpy; no new dependencies). All trained on the
discovery set, scored on the pool.

**Pre-registered.**
- P3.1: no feature family reaches held-out R^2 >= 0.10 on the pool, replicating the null
  (this is the expected outcome; the winding factor is the one with a mechanistic story).
- P3.2 (directional guess, low confidence): the median kappa of w = 0 rules is higher than of
  other w, with 0.02 <= eta^2 <= 0.15 and Kruskal-Wallis p < 0.01 on census; eta^2 >= 0.3
  would be a discovery and is **not** expected.
- P3.3: f14 (c alone) reaches R^2 <= 0.05 for ln kappa (kappa is not a function of c; the
  noisy rotor and the crust class already say so).
- P3.4: given ln A(22) as a covariate, no feature adds more than 0.03 held-out R^2.

**Break.** Any single feature or family with held-out R^2 >= 0.3, or >= 0.15 after the size
control with a CI excluding zero, passes the bar for follow-up; confirm with a fresh sample
of unseen rules from the length-12 sweep (new patched seeds, generated by `bin/probe`).

Cost: minutes (existing data); the confirmation sample if triggered: about 100 rules x 8
seeds at 2^26, order of an hour on 6 cores.

### W4. Colour-resolved decomposition of kappa

This is the one new mechanism idea with an exact algebraic core, so it gets a real tally.

**Algebra (to be verified by the tally, not assumed).** Let m_k be the fraction of steps that
start on a cell of colour k, f_k the fraction of those steps that start on a boundary cell,
and kappa_k = f_k / (P/A). Then exactly

    kappa = sum_k m_k kappa_k.

Conservation of cells across colours: each step moves one cell from colour k to k+1 (mod n),
and the cell count of every colour changes only through area growth (rate dA/dt about
t^(-1/3)) and slow drift of the colour mix. Hence m_k - m_{k-1} = O(dA/dt), and **for every
rule m_k -> 1/n at late times**, while the cell fraction pi_k need not be 1/n. If so,

    kappa -> (1/n) sum_k kappa_k,

so kappa is the *unweighted* mean of colour-resolved edge enhancements, and a heavy tail
means one colour is enormously over-represented on the edge. If in addition the walker's
per-cell visit rate depended only on colour (a "colour-class mean field"), then
f_k = (P/A) e_k / pi_k, where e_k is the colour mix of the boundary and pi_k that of the
territory, giving the parameter-free prediction

    kappa_hat = (1/n) sum_k e_k / pi_k.

The rotor gives kappa_hat = 1 against kappa = 2, so the mean-field closure is known to fail
there. The question is whether it explains the **rule-to-rule variation** among ants, and
what kappa / kappa_hat (the within-class inhomogeneity factor) looks like.

**Implementation.**
- `examples/kappa_rs_colourflux.rs`, same spec syntax as `bin/probe` (`RULE`, `RULE@SEED`,
  `rotor:SEED`, `pw:Q:SEED`). For each octave window k >= 18 write one row: rule, k, steps,
  steps_by_colour (n values), boundary_steps_by_colour, new_cells_by_colour, hist_all at
  window end, hist_boundary at window end, area, perimeter, plus the probe's own B and
  new_cells for cross-checking. Colour is the colour **before** the step.
- `tests/kappa_rs_colourflux.rs`: property test on small boards (random rules n = 2..8,
  random patched starts, 10^3-10^5 steps) that (i) sum of steps_by_colour equals steps,
  (ii) sum of boundary_steps_by_colour equals the probe's boundary_steps, (iii) all counts
  agree step-for-step with `reference`, (iv) hist_all and hist_boundary agree with
  `src/colours.rs`. Commit any `proptest-regressions/` files.
- Reuse the same boundary definition as the probe (visited cell with at least one
  never-visited 4-neighbour), so kappa from the tally matches `experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv`
  rows to numerical precision for the same seed.

**Runs.** Pool rules (152/192) x 6 patched seeds at 2^26 on a 8192 board (rule@seed
reproduces b2 seeds where available), plus 30 census blob rules not in the pool x 1 blank
run, plus controls (rotor x 6 seeds, `pw:0.5` x 6 seeds). Command (WSL):
`cargo run --release --example kappa_rs_colourflux -- 26 8192 < experiments/archive/2026-10-kappa-rule-space/results/w4_specs.txt > experiments/archive/2026-10-kappa-rule-space/dumps/w4_colourflux.csv`,
then `scripts/w4_stats.py` -> `results/w4_stats.txt`. Estimated 30-60 CPU-minutes, to be
confirmed by a timing run on 4 rules first.

**Analysis.**
1. Verify the conservation law: delta = max_k |n m_k - 1| per run and window; its decay with k.
2. Verify the identity kappa = sum m_k kappa_k and kappa(tally) = kappa(probe) within 1%.
3. Which colour carries kappa: rank-1 share = max_k m_k kappa_k / sum_k m_k kappa_k; is the
   leading colour 0 (fresh), 1 (freshly stepped), or a later one? Position in the rule?
4. Mean-field check: Spearman and R^2 of ln kappa_hat vs ln kappa across ants; the
   distribution of lambda = kappa / kappa_hat; the rotor and `pw` controls.
5. Variance decomposition: ln kappa = ln kappa_hat + ln lambda; which term carries the
   rule-to-rule variance?

**Pre-registered.**
- P4.1 (conservation): delta < 0.03 for at least 95% of blob-rule runs at k = 24..26, and
  delta falls with k with a log-log slope of -0.33 +- 0.15 where it is above the counting
  noise floor. Falsifies the derivation if delta is large and k-independent.
- P4.2 (identity): kappa = sum_k m_k kappa_k within 1% in every run (algebra; a code check).
- P4.3: among rules with kappa > 3, the leading colour supplies >= 60% of sum_k m_k kappa_k
  in at least 80% of those rules.
- P4.4: Spearman(ln kappa_hat, ln kappa) >= 0.4 on the pool. Moderate confidence only; the
  mean-field closure fails for the rotor and may fail for ants too. If Spearman < 0.2, report
  the closure as falsified and carry only P4.1-P4.3 forward.
- P4.5: lambda is not constant: CV(lambda) >= 0.3 across rules. (If lambda were constant,
  kappa would be a function of colour mix alone, a strong statement; that is not expected.)
- P4.6 (control): rotor kappa(tally) = 2.00 +- 0.01 and sum_k m_k kappa_k check passes;
  `pw:0.5` gives m_k = 1/n only trivially (n = 1 colour), so it controls the kappa
  algebra, not the conservation law.

**Why it matters.** If P4.1-P4.3 hold, the heavy tail and the unexplained rule dependence both
reduce to *which colour's edge enhancement is anomalous and why*, a much smaller question
than "kappa of the whole rule". If P4.4 also holds, part of kappa is already predicted from
two cheap histograms.

### W5. Bulk fingerprint on an area-matched mature field

**Question.** Does the interior dynamics of a rule, measured with no edge present, predict
its kappa? Rule letters did not; observables of the dynamics have not been tried.

**Design (the size confound is the main hazard, so the arena is matched on area, not time).**
- Run each rule from the blank board until the visited area first reaches A0 = 20 000 cells
  (about R = 80), then record the next T = 2^22 steps. Only steps taken while the walker
  is at least D0 = 20 layers inside the boundary (exact distance transform at snapshot
  intervals, reusing `examples/layers.rs` logic with a periodic refresh, or a conservative
  position-based bound: distance to the bounding box of the territory) are used. The
  territory grows over the recording window by a factor of at most (1 + T dA/dt / A0);
  report that factor and require it < 1.5 (else shorten T).
- Observables, per rule, by lag in absolute steps (never in units of R):
  - turn-sign autocorrelation C(m), m = 1..256, and I_turn = sum C(m);
  - mean-square displacement exponent and diffusion-like ratio MSD(L)/L for L = 2^6, 2^9, 2^12;
  - heading autocorrelation at lag 2^6;
  - first-return statistics to the 3x3 neighbourhood: P(return within 32 steps), tail slope;
  - fraction of steps on cells last visited within 64 steps (local reuse);
  - core colour mix pi_k and its entropy; mean colour of the cell under the walker.
- Rule-level kappa target: pool rule means of ln kappa at k = 25 (stationary subset flagged).

**Implementation.** `examples/kappa_rs_bulk.rs` with the same spec syntax; reference test
against `reference.rs` for the trajectory-derived tallies on small boards
(`tests/kappa_rs_bulk.rs`), and an end-to-end check that the territory reaches A0 at the
step `probe` reports for the same spec. Controls: rotor (known t^(1/3)), `rw`, `pw:0.5`.
Cost: 2^22 + roughly the time to reach A0 per run; about 200 rules x 4 seeds, minutes.

**Pre-registered.**
- P5.1: at least one pre-declared observable (the full list above is declared now; the
  primary three are I_turn, MSD(2^9)/2^9 and P(return within 32)) reaches held-out R^2
  >= 0.15 for ln kappa on the pool, **after** conditioning on ln A at k = 22. Prior probability
  I assign: about 25%.
- P5.2: bulk observables do not reach R^2 >= 0.3 (the explanation bar). Prior about 90% that
  they fall short; stated so a surprising pass is recognisable.
- P5.3: the fingerprints are themselves reproducible (ICC across seeds >= 0.7), otherwise they
  cannot explain a rule property.
- P5.4: rotor MSD/L scaling is consistent with the t^(1/3)-type subdiffusion (control reading
  only, no numerical bar).

**Interpretation.** A pass on P5.1 with a mechanistic reading (for example persistence or
local reuse) goes into the theory track W10. A fail with P5.3 true is a clean null for
"bulk transport sets kappa".

## 7. Stage 3: gated, with explicit entry criteria

Each of these gets a dated addendum **with predictions** before its first run. Entry criteria
and design sketches only, because the right design depends on Stage 1-2 outcomes.

### W6. Single-letter mutation scan (causal rule-space probe)

- Entry: W1 is mixed or smooth (r_obs >= 0.15), or a reviewer wants a low-noise confirmation
  of a rugged W1 (then run the 50-base pilot only).
- Design sketch: 200 stationary blob bases stratified by n (6..11); all single-letter
  mutants (canonicalised, deduplicated); 8 patched seeds each at 2^26 via `bin/probe`
  (`RULE@SEED` specs, `probe 26 8192`), roughly 1 800 rules x 8 seeds; time a pilot first.
  Analyse delta ln kappa against position and letter with a mixed model; the noise-adjusted
  effect threshold is delta > 3 * SE_diff.
- Question: do mutations at specific positions change kappa systematically, or is the landscape
  uncorrelated even with proper replication?

### W8. Strip (half-plane) front

- Entry: W4 or W5 leaves a mechanism unresolved and a geometry-free test is wanted.
- Sketch: a cylinder of width W with a reflecting far wall at height H; the front advances
  into fresh ground. Measure front speed versus H and W. If K_strip correlates with K_blob
  across rules (Spearman >= 0.8), curvature and shape are irrelevant and the cheap geometry
  can replace the blob. Needs a new walker/geometry in `src/` plus a property test against
  `reference`.

### W9. Surrogate-field ladder (interventional)

- Entry: W5 or W4 identifies a colour or fingerprint candidate worth intervening on.
- Sketch: at a fixed time, replace the bulk by surrogates preserving (a) the colour histogram,
  (b) nearest-neighbour colour pairs, (c) 3x3 statistics, (d) the exact field with one sector
  scrambled; keep the frontier and walker. Continue for 2^24 steps and compare boundary
  occupancy with seed-matched sham edits. The first rung at which kappa is restored measures
  the order of structure that carries it. Build on `examples/transplant.rs` and
  `examples/knock.rs` after reading them; this is the same family as F3 of the pm frontier note.

### W10. Theory track: front matching

- Always running, deliverable is a short derivation in `theory.md` here.
- Content: the cumulative visit density is the cone 3(1 - r/R) (zero at the edge) while the
  instantaneous edge occupancy is kappa times the mean (not zero). Write the flux balance of
  the comoving front with an unknown edge boundary coefficient, and state kappa as a
  functional of bulk quantities. Use W4's kappa_k decomposition (which colour is anomalous)
  and W5's fingerprints as the inputs the derivation must be able to produce.
- Success: one quantitative, falsifiable statement of the form "kappa = F(observable)" with a
  stated range of validity; otherwise a list of what was ruled out by the derivation.

## 8. Pre-registered test family (for Holm correction)

P1.1, P1.2, P1.3, P1.4, P2.1, P2.2, P2.3, P2.4, P3.1, P3.2, P3.3, P3.4, P4.1, P4.3, P4.4, P4.5,
P5.1, P5.2, P5.3, P7.1, P7.2. P4.2, P4.6, P5.4 are code and control checks and are not part of the
family. Everything else produced is exploratory.

## 9. Schedule, effort, order

| Order | Item | Dependency | Compute | Notes |
|---|---|---|---|---|
| 1 | W0 | none | minutes | gate for all |
| 2 | W1, W2, W7 | W0 | minutes each | independent, can run in parallel |
| 3 | decision-tree review; log entry | 2 | none | pick Stage 2 priority |
| 4 | W4 tally + test | W0 | tally code first, 30-60 CPU-min runs | independent of W1-W3 results |
| 5 | W3 | W0, W4 (for f13) | minutes | |
| 6 | W5 | W0 | tens of CPU-minutes | |
| 7 | Stage 3 gating review | 3-6 | none | write addenda with predictions |
| ongoing | W10 | W4, W5 | none | |

Total Stage 1-2 compute is under about 4 CPU-hours; the expensive items are the gated ones
(W6 about 8 CPU-hours, W9 more). Background long jobs with a log under `experiments/archive/2026-10-knockout-maps/dumps/`; do not block.

## 10. Deliverables and promotion

- `results/` holds every number cited; `scripts/` regenerates them from the committed data
  and the named binaries.
- Final write-up at the end of Stage 2 as a "Results" section appended here (not rewriting
  predictions), listing each pre-registered prediction as held / failed / not tested.
- Promotion: when Stage 2 closes, a concise summary goes into `notes/open-questions-hypotheses.md`
  (kappa entry) and `notes/kappa-experiment-design.md` (pointer), and the paper is touched only if
  a claim passed the explanation bar. Negative results are written up with the same weight; a
  confirmed null on rule-space smoothness is itself a result the paper can state.
- If W4's conservation law (P4.1) holds, check whether it is already in the literature or the
  notes before claiming novelty (rotor-walker and Eulerian-flow literature; the identity is an
  algebraic consequence of cell-count balance and may be known).

## 11. Risks and confounds, named in advance

| Risk | Mitigation |
|---|---|
| Size contamination (kappa tied to A at fixed t) | partial-on-ln A in every test; area-matched arena in W5 |
| Drift (non-stationary kappa) inflating the tail | stationary subset reported everywhere; W2 first |
| Single-run noise in the 2630-rule census (reliability about 0.6) | disattenuated and attenuated both reported; pool means for confirmation |
| Rule overlap across pairs / cohorts | bootstrap over rules; discovery and confirmation rule-disjoint |
| Multiple comparisons across many features | pre-registered family, Holm; features frozen before confirmation |
| Boundary definition mismatch between tallies | one shared definition, equality test against `probe` rows |
| Board-escape selection (late breakouts removed) | count and report escaped runs per cohort; do not impute |
| Selecting on outcomes (stationary restriction) | sensitivity table; report both full and restricted |
| Mirror symmetry / canonicalisation hiding near-duplicates | W1 mirror canonicalisation spelled out; grouped CV |
| Pipeline blind to real effects | planted-signal recovery before any null is believed |
| Textual claims outrunning data (T1 episode) | every claim in the log carries the command that produced it; registered tests are reported as registered even if a different test replaced them |

## 12. What would count as success, and as an honest failure

- **Success:** a feature or one-parameter prediction with held-out R^2 >= 0.3 on pool rule-mean
  ln kappa, and >= 0.15 after conditioning on ln A, confirmed on fresh rules.
- **Partial success:** a structural decomposition that reduces the question (for example
  P4.3: kappa is the mean of colour-resolved enhancements and one colour carries the
  tail), or a clean demonstration that kappa is rugged in rule space (P1.2) and that bulk
  dynamics does not carry it (P5.2).
- **Failure we will report plainly:** all of P1-P5 null, with W4's identity and conservation
  law as the only positive findings. kappa then stays listed as unexplained in `notes/`, with
  the sharper statement of which mechanisms and feature classes are excluded.

## Log

(Append dated entries here: what ran, command, git commit, seeds, which predictions held or
failed, deviations from this plan. Do not edit the sections above.)

### 2026-10-14 (evening): Stage 1 run, W0 / W1 / W2 / W7, plus two exploratory follow-ups

Commands (repo root, via the WSL wrapper in section 4.6), git HEAD `6ce3793` (the plan was
written at `99de7c1`; other commits landed in between, none touching `data/`), seed 20261014:
`uv run experiments/archive/2026-10-kappa-rule-space/scripts/{w0_build,w1_smooth,w2_stationarity,w7_emergence,x1_prefix_icc,x2_prefix_heldout}.py`.
Outputs: `results/w0_checks.txt`, `rules_pool.csv`, `rules_census.csv`, `w1_stats.txt`,
`w2_stationarity.txt`, `w7_emergence.txt`, `x1_prefix_icc.txt`, `x2_prefix_heldout.txt`.
No new simulation runs; everything reads committed `data/` files. Nothing here is committed to git yet.

**Deviations and decisions, stated up front.**
- *Cohorts reconciled (W0).* 2622 = 2630 fitted blob rules minus 8 bursty; the census cohort is the 2622 non-bursty rules
  (2622 with kappa > 0 and a k = 22 area). Pool-152 = b2 + item21 (arm C script); pool-192 adds `patched.csv` (a1c script).
  **Pool-192 is the primary pool** because it is the one for which the a1c baseline was published and reproduced.
  Four pool-192 rules are not in the census cohort.
- *"r_obs" in the decision tree was not defined as Pearson or Spearman.* I scored the registered P1 tests on the **Pearson** r
  (the form stated in the W1 method), and report Spearman next to it. They disagree materially (below), so the decision-tree
  branch depends on the choice. I flag it rather than pick the branch that suits a story.
- The four W0 instrument checks all passed (below), so W1-W7 proceeded.

**W0 instrument checks (all PASS).** ICC of ln kappa, b2 core band: 0.625 (reference 0.625). Letter-by-position ridge LOO R^2:
-0.061 / -0.046 / -0.036 for lam = 1 / 10 / 30, identical to a1c. Planted R^2 = 0.30 on one letter is recovered at +0.247 mean
(min +0.125, 20 draws; the pipeline is conservative, about 80% of the planted value, so nulls are not evidence of absence below
roughly R^2 0.1). Letters predict c at held-out R^2 +0.767 (positive control).

**W1 (rule-space smoothness; 9910 Hamming-1 pairs, 2622 rules; `results/w1_stats.txt`).**

| Pre-registered | Outcome |
|---|---|
| P1.1 r(c) >= 0.5 | **HELD**: r = +0.592 (CI +0.560..+0.621). Per position it is -0.57 for j <= 1, +0.52 for j in 2-3, +0.88 for j >= 4 (flipping an early letter changes c in a sign-reversed way, so pairs anticorrelate there) |
| P1.2 Pearson r(ln kappa) <= 0.15, CI upper < 0.30 | **HELD as written**: r = +0.075, 95% CI +0.022..+0.131, permutation null +0.005 +- 0.012 (p < 1e-4, so it is not zero). **But** Spearman = +0.271, and r = +0.222 after dropping pairs with a member beyond |z| > 3 (ln kappa runs from -6.1 to +3.4; sd 0.57). The Pearson number is dominated by tail rules |
| P1.3 r(j >= 4) - r(j <= 1) <= 0.10 | **HELD, barely**: +0.085 (r = +0.120 vs +0.035) |
| P1.4 monotone variogram, within 0.05 of null from d = 2 | **HELD, barely, on the stated tolerance**: r(ln kappa) = +0.081, +0.049, +0.015, +0.002 for d = 1..4 against null about +0.003. d = 2 exceeds the null by 0.046, which is about 9 null sd, so "within 0.05" was too loose to mean "indistinguishable from zero" |

Exploratory (not pre-registered, labelled so in the output): restricted to **stationary** pairs (both members |g_k| < 0.05;
7222 of 9910) the Pearson r(ln kappa) is **+0.272, CI +0.200..+0.340** (Spearman +0.351). By flipped position (stationary pairs):
j <= 1: +0.093; j = 2-3: +0.003; **j >= 4: +0.382**. Append-one-letter neighbours (rule R and R+x): r(ln kappa) = +0.369,
r(c) = +0.977 (the shared prefix drives the shared dynamics, so this is not independent of the prefix result below).
r(ln A(22)) over pairs is +0.305; the size-residualised ln kappa has pair r = +0.148.

Reading: kappa is **not a hash of the rule**. It is weakly smooth over all rules, and moderately smooth once drifting rules are
removed, with the smoothness living in late letters: changing an early letter (j <= 3) scrambles kappa, changing a late one
(j >= 4) mostly does not. Under the registered Pearson reading the decision tree says "rugged"; under Spearman or on the
stationary subset it says "mixed" (0.15 < r < 0.30 → W3 and W5 both, W6 pilot). I take the **mixed branch** because the
Pearson number is demonstrably outlier-driven.

**W2 (stationarity; `results/w2_stationarity.txt`).**

| Pre-registered (|g_k| < 0.05, pool-192) | Outcome |
|---|---|
| P2.1 >= 50% of kappa > 3 rules non-stationary | **HELD**: 4/5 in the pool (n is tiny); in the census (single runs) **43/44 = 98%** |
| P2.2 sd ln kappa ratio stationary/all <= 0.7 | **HELD**: 0.65 pool (0.504 -> 0.327); 0.61 census (0.572 -> 0.348) |
| P2.3 ICC(ln kappa) among stationary rules >= 0.45 | **HELD**: 0.851 (169 rules) |
| P2.4 letter LOO R^2 on stationary subset <= 0.10 | **HELD, barely**: +0.084 (but +0.119 at |g_k| < 0.03, which would have failed) |

Sensitivity (thr 0.03 / 0.05 / 0.10): stationary share 0.83 / 0.88 / 0.94; sd ratio 0.61 / 0.65 / 0.73; stationary ICC
0.856 / 0.851 / 0.558. The ICC is not stable in the threshold (the 0.10 set admits drifting rules with large within-rule
variance), so "ICC 0.85" is a statement about the |g_k| < 0.05 set, and part of its rise over 0.625 is selection on a quantity
that also lowers within-rule scatter. Among stationary census rules kappa is tight: 1/10/50/90/99 percentiles
0.36 / 0.59 / 0.90 / 1.28 / 1.91. The three pool rules with kappa > 5 are all drifting (|g_k| = 0.07-0.11).
Reading: **the heavy tail of kappa (0.1 to 180) is almost entirely drift**. For stationary rules kappa lives in roughly
0.4-1.9, rule-specific (ICC high), and letters already carry a little of it.

**W7 (when is kappa fixed; `results/w7_emergence.txt`; 2271 core-band runs, windows needing >= 200 boundary steps).**
P7.1 **HELD**: Spearman(kappa(k), kappa(26)) across the 192 pool rules is +0.728 at k = 12 and >= 0.844 for every k >= 16
(0.95-0.98 at k = 22-25). P7.2 **HELD** as scored (non-stationary rules reach 0.8 at k = 24 against k = 13 for stationary),
but the non-stationary subset is only 23 rules and drifting rules are drifting by definition, so this is the expected
reading, not independent evidence. Stationary rules have their rank order set by k = 13 (about 10^4 steps).
Caveat: the early-k rank correlation is also partly a size/c effect (partial Spearman given ln A(k) is 0.65 at k = 12,
0.71 at k = 16, 0.88 at k = 22) and the reference kappa(26) is computed from the same runs.
Reading: **for stationary rules kappa is already a rule property by about 10^4 steps**, so small-scale dynamics (W4/W5 on
short runs, exact analysis of the first few hundred colours' worth of dynamics) is legitimate; kappa is not a late emergent
collective property for them.

**Exploratory finding (x1, x2): the rule prefix predicts stationary-rule kappa out of sample.** Not pre-registered;
prompted by the position effect in W1. Census single-run ln kappa (stationary): the intraclass correlation of rules sharing
their first p letters is 0.008 / 0.140 / 0.322 / 0.456 for p = 3 / 4 / 5 / 6 (permutation null 0.000 +- 0.004; ICC(1) is
bias-corrected for group number, `results/x1_prefix_icc.txt`). Out of sample (`x2_prefix_heldout.py`): train prefix-group means on
the 2434 census rules **not** in pool-192, score on the pool's independent patched-start rule means. Held-out R^2:

| prefix length p | all rules | stationary rules |
|---|---|---|
| <= 4 | +0.054 | +0.120 |
| <= 5 | +0.131 | +0.311 |
| <= 6 | +0.161 | +0.368 |
| <= 8 | +0.275 | **+0.552** |

(fallback to the shorter prefix mean when a group has < 3 discovery rules; 44 / 42 prefix-6 groups). This is the first rule-string
feature in the project with held-out R^2 above the 0.3 explanation bar, and it contradicts the "no rule-string feature predicts
kappa" statement (a1c: letters-by-position ridge and prefix-5 neighbours, on 192 rules including drifters, R^2 about 0). Two reasons
the earlier null was a power and nonlinearity artefact: the earlier models were linear in letters, and the prefix-5 neighbour test
had about 6 rules per prefix against about 70 here.

**What it does not yet show, in the order I would doubt it:**
1. *Size and c.* Conditioning on ln A(22) alone gives held-out R^2 +0.595 (stationary), ln A(22) + c gives +0.854, because kappa and
   area are tied at fixed t. Adding the prefix-6 mean to ln A(22) gives +0.674 (+0.079, **below the 0.15 size-controlled bar** of
   section 12) and adding it to ln A(22) + c gives +0.854 (+0.000). So the prefix is informative about kappa, but I have not shown it
   carries anything beyond what ln A and c already carry; c alone is uninformative (R^2 -0.02).
2. *It is a lookup table, not a mechanism.* 2^(p-1) group means is description. What it does is localise the information: the
   first 5-8 colours of the rule carry most of what a rule's letters can tell us about kappa, consistently with W1 (late flips
   preserve kappa, early flips do not). The natural mechanism is that edge cells are young cells (colours 0, 1, 2, ...), so the edge
   dynamics sees the early colours first, but this is a story, not a test.
3. *Single-seed discovery, pool-192 confirmation, one split.* No repeated random splits, no fresh simulations. The pool rules are
   also census rules, so they share their blank-board runs' rule identity but not their runs.
4. *Selection on drift.* The stationary subset is defined by an outcome-related quantity (section 11).

**Consequences for the plan (decisions logged, no new predictions edited):**
- P3.1 ("no feature family reaches held-out R^2 >= 0.10") was registered with **prefix-3** as the prefix feature (f8), and that
  still holds (R^2 about -0.01); the exploratory prefix-p>=5 lookups would fail it. When W3 is run, the report will list prefix-p
  results as exploratory next to the registered prefix-3 test, and not claim P3.1 held without saying this.
- A pre-registered addendum for W3b (prefix lookup, fresh rules, size-controlled) must be written **before** any new run: fresh
  length-12 rules not in census or pool, 8 patched seeds at 2^26, predictions from the discovery table above. Not yet written.
- W4 gets a sharper question: if early letters carry kappa, the colour-resolved enhancements kappa_k (section 6, W4) should show
  the large kappa_k on **low-index colours**. That is a pre-existing registered analysis (item 3 of the W4 analysis), and it now has
  a directional prediction attached *as of this entry*: for stationary rules the leading colour (max m_k kappa_k) has index <= 2 in
  at least 60% of rules. Recorded here before W4 has run.
- W2's lesson applies to every later analysis: report the stationary subset separately; the full census mixes a tight rule-specific
  kappa (stationary) with a tail that is mostly drift.

**Status of the pre-registered family after Stage 1:** P1.1 held; P1.2 held (Pearson; fragile); P1.3 held (barely); P1.4 held
(barely; tolerance too loose); P2.1-P2.4 held (P2.4 barely and threshold-sensitive); P7.1 held; P7.2 held (low independent
information). P3-P5 not yet run. The one clear surprise is outside the registered family (the prefix lookup).

**Not done / open from this stage:** the W6 pilot that the "mixed" branch recommends; W1 on the pool patched means only has 48 pairs
(too few); the census cohort stationarity flag uses a single run's g_k, which is noisy; the sensitivity of the prefix result to the
fallback rule (`min_n = 3`) and to repeated random discovery/confirmation splits was not examined.

### 2026-10-14 (night): W3b addendum, registered BEFORE any fresh run

Status when written: git HEAD `6ce3793`; nothing of W3b has been simulated; the sampler
`scripts/w3b_sample.py` and its output `results/w3b_specs.txt` are produced after this entry is saved.
Motivation: the exploratory prefix lookup (x1/x2) reached held-out R^2 0.37 (p <= 6) and 0.55 (p <= 8) on
stationary pool rules, but it was found post hoc, tested on one split, and never on rules or runs not seen
during the search. This addendum fixes a confirmatory test.

**Fresh sample.** 150 rules, 75 each of length n = 13 and n = 14 (numpy `default_rng(20261014 + 11)`),
uniform over strings starting with R, rejecting all-R and non-primitive (periodic) strings (same
convention as `experiments/archive/2026-10-b3-long-rules/scripts/b3_sample.py`). Length 13-14 is chosen because every canonical rule of length <= 12 is already in the
census or the pool; "fresh length-12 rules" do not exist. **This makes W3b an extrapolation in rule length as well as a test on new runs.**
Failure therefore has two possible causes (the prefix effect is real but length-specific, or it is not real); the addendum says which
outcome I will conclude in each case. Runs: 8 patched starts per rule, seeds 201..208, `probe 27 8192`
(`RULE@SEED`), 1200 runs. Per-run kappa, c, g_k, alpha_w and ln A(22) as in W0/`analyse_probe.per_rule`.
Analysis cohort per rule: >= 6 core-band runs (0.25 < alpha_w < 0.42), as in the pool. Rule-level stationary flag: |median g_k| < 0.05.

**Predictor (frozen).** Group-mean lookup on the census (all 2622 non-bursty blob rules, **including** pool rules, n <= 12), exactly as
`scripts/x2_prefix_heldout.py`: mean ln kappa of census rules sharing the first p letters, falling back to the longest shorter prefix that
has >= 3 training rules; p in {3, 4, 5, 6, 7, 8}. For "all rules" the table uses all census rules; for "stationary" the table uses
census rules with |g_k| < 0.05. Size-controlled version: OLS of ln kappa on ln A(22) (and on ln A(22) plus the leave-one-out
prefix-6 mean), trained on the census, applied to the fresh rules. Held-out R^2 is computed two ways: **strict** against the training-set
mean (primary) and against the fresh-sample mean (as in x2; reported for comparability).

**Pre-registered predictions** (rule-level ln kappa means on the fresh rules):
- **P3b.1** Stationary fresh rules: strict held-out R^2 of the prefix-6 lookup >= 0.20, and of prefix-8 >= 0.25.
  (Pool values 0.37 / 0.55 shrunk for the length shift and the stricter baseline.) My confidence: about 50%.
- **P3b.2** All fresh core-band rules: prefix-6 strict held-out R^2 >= 0.08. About 55%.
- **P3b.3** Size-controlled: adding the prefix-6 mean to ln A(22) improves strict held-out R^2 by **less than 0.15** over ln A(22) alone
  (i.e. the registered size-controlled bar of section 12 is **not** cleared). About 75%. If it is cleared, prefix is a real predictor
  beyond size and the explanation question reopens strongly.
- **P3b.4** Control: permuting prefix labels among the training rules (200 permutations) gives strict held-out R^2 with a median <= +0.02
  and a 95th percentile <= +0.08 on the fresh stationary rules. (Checks the lookup pipeline, not kappa.)
- **P3b.5** At least 75% of fresh core-band rules (>= 6 runs) are stationary.
- **P3b.6** Direction check: the held-out R^2 rises with p between p = 4 and p = 8 for stationary rules (Spearman of R^2 vs p >= 0.8).

**Interpretation rules, fixed now.**
- P3b.1 true and P3b.3 true-as-predicted (not cleared): the prefix carries information about kappa that is entangled with size and c;
  proceed to W4 (does the colour-resolved decomposition locate it on early colours?). Do not call it an explanation.
- P3b.1 true and P3b.3 false (cleared): treat prefix as a genuine predictor and design the mechanism test around it.
- P3b.1 false and P3b.2 false: the pool result did not replicate; record the prefix lookup as a post-hoc artefact or a length-specific
  effect (cannot tell which without n <= 12 runs, which do not exist). Do not extrapolate it in the paper.
- P3b.1 false and P3b.2 true: weak/length-limited effect; report both numbers.

### 2026-10-14 (night): W4 implementation notes, registered before the full W4 run

Code: `src/colourflux.rs` (module `turmite::colourflux`), `tests/colourflux.rs`, `examples/kappa_rs_colourflux.rs`, specs from
`scripts/w4_specs.py` -> `results/w4_specs.txt` (pool-192 x 6 patched seeds 301..306, 30 census non-pool rules on a blank board,
rotor:1..6, pw:0.5:1..6; 1194 specs). Test status before any result was used: `cargo test --release --test colourflux` passes (6 tests:
HashMap oracle for any `Walker` on plain ant, patched ant, rotor, memoryless walker; `probe_walker` window equality; reference-ant colour counts).
A mutation check confirmed the oracle detects a wrong `new_by_colour` and a wrong boundary test (both made 4 of 6 tests fail); the regression
file those mutants produced was deleted, because it records failures of deliberately broken code, not of the real code.
Deviations from the W4 text above:
- `MAX_LOG2` is probe's convention: `... 18 27 8192` gives windows k = 18..26 (the README text said `26`).
- Windows k = 18..26 are recorded (hist_* at each window end), so the exact accounting identity below can be checked.

**Exact accounting identity (added; a code/algebra check, not part of the test family).** Each visit moves one cell from colour k to k+1.
For colours k >= 1 and consecutive windows, steps_by_colour[k] = steps_by_colour[k-1] - (hist_all[k](end) - hist_all[k](previous end)).
This holds exactly (cells of colour k change only through visits to k-1 and k). It is the algebra behind the conservation statement of P4.1
and will be reported as "exact in all runs" or as a bug.

**Peek disclosure.** To time the tally I ran `kappa_rs_colourflux 18 24 8192` on two specs (RLLLLLLLLRR@301, RLLLLLLLLRR@302, plus RLR and rotor:1;
only the first rows of two were read). What I saw before the full run: steps are spread nearly evenly over colours (about 1/n each, but with
colour 0 higher by roughly the new-cell rate: n*m_0 - 1 = 0.10 at k = 23, n = 11), and almost all boundary steps start on colours 0 and 1
(for RLLLLLLLLRR@301 k = 22: 42898 + 21513 of 65461 on colours 0 and 1; colours >= 2 carry under 1% each). Consequences, stated before the run:
1. **P4.1 as registered (delta < 0.03 for >= 95% of runs at k = 24..26) will probably fail.** Since steps on colour 0 exceed steps on colour n-1 by
   about the new-cell count, n*m_0 - 1 is about n*(dA/dt) per step, which is 0.1 at k = 23 for n = 11 and shrinks as t^(-1/3). Whether it is below 0.03
   at k = 24..26 depends on n; the 95% criterion will fail for long rules. The threshold was a guess; I am **not** changing it, and will report
   the failure with the measured distribution of delta by n and by k, and the slope of delta against k (the scaling part of P4.1 is unaffected).
2. **The leading-colour prediction recorded earlier ("max m_k kappa_k has colour index <= 2 in >= 60% of stationary rules") is close to trivial**:
   boundary steps are dominated by the young colours by construction (a fresh cell is entered on colour 0 and left on colour 1). It cannot
   support "early letters of the rule carry kappa". I will report it as scored, but the informative W4 quantities are the shares and ratios
   defined next. These are exploratory and labelled so:
   - e0 = boundary steps on colour 0 per new cell, e1 = boundary steps on colour 1 per new cell, e_rest = boundary steps on colours >= 2 per new cell
     (e0 + e1 + e_rest = B / new_cells = 1/c). Question: does the rule-to-rule variance of ln kappa live in e1 (re-visits of recently entered cells),
     in e_rest (deep boundary cells), or in c and the geometry?
   - Variance decomposition: ln kappa = ln(1/c) + ln(P/A)^-1 + ln(new_cells/steps) hence the identity; W4 will report which of these terms varies
     across stationary rules. This is bookkeeping, not mechanism, and will be described as bookkeeping.

### 2026-10-14 (night): W3b result (fresh length-13/14 rules)

Commands: `bash scripts/run_w3b.sh` (`probe 27 8192` on `results/w3b_specs.txt`, git `6ce3793`, 19:00-19:10 +13:00; log `results/w3b_probe.log`),
`uv run scripts/w3b_analyse.py` -> `results/w3b_stats.txt`; exploratory `scripts/x3_w3b_checks.py` -> `results/x3_w3b_checks.txt`.
Raw probe output is in `experiments/archive/2026-10-knockout-maps/dumps/w3b_probe.csv` (ignored by git).

**Sample outcome.** 150 rules x 8 seeds = 1200 runs. 229 runs (19%) left the 8192 board, all in 33 rules (a rule escaped either 0 or >= 5 of its
8 runs: 117 rules had no escapes). 931 runs were fitted, 726 in the core band. **89 rules** (46 of length 13, 43 of length 14) had >= 6 core-band runs; 87 of them are stationary.
The 61 excluded rules are the fast growers/escapers (33) and rules failing the core-band criterion (28), so the test is on rules that behave like the census blobs.
Selection check (exploratory): the prefix-6 predicted ln kappa of included rules (-0.208) is not very different from that of excluded rules (-0.118);
escapes per rule correlate only weakly with the prediction (Spearman +0.109).

| Pre-registered | Outcome |
|---|---|
| P3b.1 stationary, strict R^2 prefix-6 >= 0.20 and prefix-8 >= 0.25 | **HELD**: +0.578 and +0.742 (87 rules) |
| P3b.2 all rules, prefix-6 >= 0.08 | **HELD**: +0.461 (89 rules) |
| P3b.3 size-controlled gain of prefix-6 over ln A(22) alone < 0.15 | **HELD, by 0.005**: gain +0.145 (ln A(22) alone +0.569; with prefix-6 +0.714). Exploratory bootstrap over rules: 95% CI +0.069..+0.218, i.e. the bar is **not** clearly missed or met at p = 6 |
| P3b.4 shuffled-label control, median <= +0.02, 95th pct <= +0.08 | **HELD**: -0.010, +0.045 |
| P3b.5 stationary share >= 0.75 | **HELD**: 0.978 (conditional on inclusion, see above) |
| P3b.6 R^2 rises with p over 4..8 (Spearman >= 0.8) | **HELD**: +0.900 (R^2 by p = 3..8: +0.02, +0.21, +0.37, +0.58, +0.56, +0.74; p = 7 dips slightly) |

Exploratory, flagged as such: at **p = 8** the size-controlled gain is **+0.206 (95% CI +0.111..+0.300)**, above the 0.15 bar. p = 8 was not the registered
variant of P3b.3 (p = 6 was), and p = 8 was singled out by the same data, so this is a lead for the next confirmation, not a pass.

**Reading.**
- The prefix effect is **not a pool artefact**: on 87 unseen stationary rules of length 13-14, run on fresh patched seeds, the lookup trained only on the
  census (n <= 12) gets strict held-out R^2 0.58 (p = 6) and 0.74 (p = 8), above the pool values (0.37, 0.55), with a clean permutation control and a monotone
  rise with prefix length. All six registered predictions held. This is the first rule-string feature in the project that clears the 0.3 bar on data it was not found on.
- It is **not yet an explanation.** (1) It is a lookup table of 2^(p-1) group means; (2) most of what it predicts is also predicted by ln A(22) (strict R^2 0.57), because kappa
  and area are tied at fixed t, so what it adds beyond size is +0.145 (p = 6) to +0.206 (p = 8); (3) the effective sample is 87 rules, one family of lengths; (4) the stationary subset
  is defined by an outcome-related quantity; (5) the test does not say *why* early letters matter.
- Per the interpretation rules fixed in the addendum: P3b.1 true and P3b.3 true-as-predicted (not cleared at p = 6): "the prefix carries information about kappa that is entangled
  with size and c; proceed to W4." At p = 8 the size-controlled result leans the other way, so the plan now includes one more registered confirmation (W3c, below).

**Next registered step (W3c, to be written before running).** A direct test of the p = 8 size-controlled gain on a further fresh sample (e.g. length 13-14 rules, 150 more, new seeds) with the bar
(gain >= 0.15 with a bootstrap CI excluding 0) fixed in advance. Not yet written; no W3c run exists.

### 2026-10-14 (night): W4 result (colour-resolved tally)

Commands: `bash scripts/run_w4.sh` (`kappa_rs_colourflux 18 27 8192` on `results/w4_specs.txt`, 1194 specs, git `6ce3793`, 19:11-19:18 +13:00; log `results/w4_run.log`;
raw `experiments/archive/2026-10-knockout-maps/dumps/w4_colourflux.csv`, ignored), `uv run scripts/w4_stats.py` -> `results/w4_stats.txt`, per-rule table `results/w4_rules.csv`. Code: `src/colourflux.rs`,
`tests/colourflux.rs` (passes), `examples/kappa_rs_colourflux.rs`. Nine specs left the board (6 memoryless-walker controls, 3 ants). 187 pool rules had >= 4 usable seeds (167 stationary).
Analysis choices made before the run (header of `w4_stats.py`): runs with area log-log slope outside [0.55, 0.85] excluded from rule-level statistics; stationary flag from the pool's independent g_k.

| Check / prediction | Outcome |
|---|---|
| P4.2 kappa = sum_k m_k kappa_k within 1% (code check) | **HELD**: 0 violations in 10715 windows |
| Exact accounting identity V_j = V_(j-1) - dN_j (+ new cells for j = 0) | **HELD exactly**: 0 violations in 104087 colour-window pairs (patched and plain ants) |
| P4.1 delta = max_k abs(n m_k - 1) < 0.03 for >= 95% of blob-rule runs at k = 24..26 | **FAILED**: 0.875 of 3393 blob run-windows (0.850 over all ant runs). Median delta at k = 26 is 0.007 (n = 5) to 0.016 (n = 11); the share below 0.03 falls with length (1.00 at n <= 6, 0.93 at n = 12) |
| P4.1, scaling part: delta falls as t^(-0.33 +- 0.15) | **HELD**: median log-log slope -0.326 (IQR -0.343..-0.306); 96% of blob runs within -0.33 +- 0.15. Median delta / (n * dA/dt per step) = 0.46 |
| Leading boundary colour has index <= 2 in >= 60% of stationary rules (recorded earlier; near-trivial) | **HELD, trivially**: 100% (the leading colour is 0 in the cases checked) |
| P4.3 among rules with kappa > 3, the leading colour supplies >= 60% of boundary steps in >= 80% of them | **FAILED**: 2 of 4 rules (only four rules have kappa > 3 in this sample) |
| P4.4 Spearman(ln kappa_hat, ln kappa) >= 0.4 (pool) | **FAILED, barely**: +0.395 (all 187 rules); +0.233 on stationary rules |
| P4.5 lambda = kappa / kappa_hat has CV >= 0.3 | **HELD**: CV 0.50, mean lambda 0.97 |
| P4.6 rotor kappa 2.00 +- 0.01 | **FAILED as registered**: 1.978 +- 0.063 (sd over 6 seeds; SE 0.026, so consistent with 2.00; the band was set from the earlier long-window result 1.999 +- 0.002 and is too tight for 6 runs at one window). Rotor kappa_hat = 1.000 as expected |
| P4.6 pw:0.5 control | **not obtained**: all 6 memoryless runs left the 8192 board |

Deviation made after seeing the output: the first version of `w4_stats.py` scored P4.1 on all ant runs. The runs with huge delta (up to 5.0) are highway builders with dA/dt = 0.25 per step
(area about steps / 4). P4.1 is stated for blob-rule runs, so the script now also reports the blob-only share (0.875). Both are in `results/w4_stats.txt`; the verdict (failed) does not depend on the choice.

Exploratory bookkeeping (labelled as such in the output; it is the growth identity, not a mechanism):
- Share of var(ln kappa) carried by each term of ln kappa = ln(new cells per step) - ln c - ln(P/A), across **stationary** rules: **0.87** from new cells per step, 0.10 from c, 0.04 from P/A
  (all rules: 0.73 / 0.03 / 0.24). At a fixed window, the rule-to-rule spread of kappa among stationary rules is almost entirely the spread of the area growth rate per step.
- Boundary steps per new cell, mean over stationary rules: colour 0: 0.98, colour 1: 0.78, colours >= 2: 0.80 (sum 2.55 = 1/c on average). Colours >= 2 carry about 0.8 boundary steps per new cell,
  not the negligible fraction I inferred from the two rows I peeked at (those were unrepresentative). Correlations of ln kappa with ln e1, ln(1 + e_rest), -ln c are only +0.11..+0.12 on stationary rules.

**Reading.**
1. *Positive, mechanical:* the colour-flux law is exact as an accounting identity (zero violations), and its content is the rate: the deviation of the step distribution from 1/n shrinks as t^(-1/3)
   (median slope -0.326), with delta about half of n times the new-cell rate. So m_k tends to 1/n for every ant rule, as derived, but slowly enough that "close to 1/n" fails my 0.03 threshold for rules of
   length 11-12 at t = 2^26. The law is cell-count bookkeeping and is probably known in some form; I have not searched the literature and make no novelty claim.
2. *Negative, mechanism:* the colour-resolved decomposition does not locate kappa. The colour-class mean-field closure gives Spearman +0.395 against measured kappa (stationary +0.233): the colour mix at the edge and in the bulk
   carries a little of the rule-to-rule variation, nowhere near enough; the lambda factor (mean 0.97, CV 0.50) varies as much as kappa itself. The leading boundary colour is always 0 or 1, so the
   "early colours carry kappa" story is neither supported nor refuted by this tally. **W4 does not explain why the rule prefix predicts kappa (W3b).**
3. For stationary rules kappa's rule dependence is, at this window, the growth rate dA/dt per step, i.e. the same fact as "kappa is tied to area". The informative target remains what sets the growth
   prefactor, which W4 has not touched.

**Status after Stage 2 (W3b, W4).** Held: all six W3b predictions; P4.2, P4.1 scaling, P4.5. Failed: P4.1 threshold, P4.3, P4.4 (by 0.005), P4.6 rotor band as registered. Not obtained: pw control.
W3 proper and W5 (bulk fingerprint) not run. The strongest open lead is the prefix lookup (W3b: strict held-out R^2 0.58 at p = 6 and 0.74 at p = 8 on fresh rules; size-controlled gain +0.145 at p = 6,
+0.206 (CI +0.11..+0.30, exploratory) at p = 8).
Next steps recorded: (1) W3c registered confirmation of the p = 8 size-controlled gain on a further fresh sample; (2) W5 bulk fingerprint (area-matched), to test whether the prefix acts through bulk dynamics;
(3) W6 mutation scan at positions >= 4 vs <= 3 as a causal probe of the prefix effect, since W4's colour tally was uninformative about it.

### 2026-10-14 (night, session 3): W6 pilot addendum, registered BEFORE any mutant is simulated

Status when written: git HEAD `797704a`, working tree dirty (unrelated). No W6 sampler, spec or run exists yet. Motivation: the prefix lookup
(W3b) is correlational and entangled with size. A single-letter mutation is the cleanest intervention available: if early letters set kappa,
changing a letter at positions 1..3 should move ln kappa more than changing one at positions >= 4. This is the "50-base pilot" the W1 "mixed" branch asked for.

**Design.** 40 stationary pool bases (|g_k| < 0.05 in `rules_pool.csv`), n = 10, 11, 12 with 12 / 14 / 14 bases drawn with numpy `default_rng(20261014 + 21)`.
Mutants: flip the letter at 0-indexed position j = 1..n-1 (position 0 is excluded: it is R by canonical form, and flipping it is equivalent to flipping every other letter).
Canonicalise (mirror so it starts with R), drop non-primitive, all-R and duplicates (a mutant reached from two bases or positions is simulated once and credited to every pair).
Every base is re-run alongside its mutants. Runs: `RULE@SEED`, seeds 401..406 (same six for base and mutant, so the patch is shared), `probe 26 8192`.
Per-run kappa, alpha_w, g_k via `per_rule`; core band 0.25 < alpha_w < 0.42; a rule is usable with >= 4 core-band runs. Delta = mean ln kappa(mutant) - mean ln kappa(base).
Noise: SE_diff = sqrt(s_b^2/m_b + s_m^2/m_m), with s the between-seed sd of ln kappa. "Early" = j in {1,2,3}; "late" = j >= 4.
Selection hazard, stated up front: mutants that escape the board or leave the core band are dropped, and that may depend on j. The exclusion rate by j is reported and the main test is also run on pairs where both rules are usable.

**Pre-registered predictions (pair-level, usable pairs only; bases are the unit for CIs, bootstrapped over bases).**
- **P6.1** Median |Delta| over early mutants exceeds the median over late mutants by a ratio >= 1.3 (base-level paired: per base, median early |Delta| / median late |Delta|, median of ratios >= 1.3).
  Confidence about 50%: the prefix lookup says yes, but the whole-rule landscape in W1 was rugged and late flips may matter as much.
- **P6.2** Late mutations are not inert: median late |Delta| exceeds the replicate-noise null (median |Delta| between two disjoint 3-seed halves of the *same base*, matched pairing) by >= 1.5x. About 70%.
  If false, late letters really do not move kappa (a striking result, supporting a prefix-only mechanism).
- **P6.3** Share of mutants with |Delta| > 3 SE_diff is larger for early than for late (difference >= 0.10). About 55%.
- **P6.4** Signed: early mutants shift ln kappa more *negatively or positively* in a consistent direction by letter (L->R vs R->L): I make no directional prediction, only report it.
- **P6.5** Size control: the early/late contrast of |Delta ln A(22)| has the same sign as that of |Delta ln kappa| (kappa moves because area moves). If the ratio of the kappa contrast to the area contrast is below 1 the size confound explains it. Reported, no bar.
- **P6.6** Usable share of mutants is >= 70% overall and differs by less than 0.15 between early and late (selection check).

**Interpretation rules, fixed now.**
- P6.1 true and P6.2 true: early letters have *larger* effect but late letters matter too; the prefix is a weighting, not a switch. Next: dose-response over j (is there a smooth decay?).
- P6.1 true and P6.2 false: prefix-only mechanism; W3c becomes the confirmation and the theory track gets a hard constraint.
- P6.1 false: the prefix lookup is predictive but not causal in this sense (possible: early letters only correlate with composition/size). Record as a null for the causal reading.
- P6.6 false: the contrast is selection-contaminated; report but do not interpret P6.1-P6.3 without the both-usable restriction.
This is a pilot (40 bases); a pass is a reason to run the 200-base W6, not a result.

### 2026-10-14 (night, session 3): W6 pilot result

Commands: `uv run scripts/w6_sample.py` (40 bases, 398 mutant pairs, 405 distinct rules, 2430 runs), `bash scripts/run_w6.sh` (`probe 26 8192`, seeds 401..406, git `797704a`, 22:09-22:22 +13:00;
log `results/w6_probe.log`, raw `dumps/w6_probe.csv` ignored), `uv run scripts/w6_analyse.py` -> `results/w6_stats.txt`, `results/w6_pairs_scored.csv`. 232 of 2430 runs escaped the board; 39 of 40 bases usable; 277 of 398 pairs usable.

| Pre-registered | Outcome |
|---|---|
| P6.1 per-base median early/late \|d ln kappa\| >= 1.3 | **HELD**: median ratio 2.21 (bootstrap CI over 36 bases 1.59..3.10). Pooled medians: early 0.298 (n=72), late 0.132 (n=205) |
| P6.2 late median \|d\| >= 1.5x replicate-noise null | **HELD**: 5.2x the scaled null (0.025, 34 bases), 3.7x the raw 3-vs-3 null (0.036). Late letters are not inert |
| P6.3 share of \|d\| > 3 SE_diff, early minus late >= 0.10 | **HELD**: 0.750 vs 0.522 (+0.228) |
| P6.4 signed, no bar | early L->R +0.109, early R->L -0.032, late L->R -0.004, late R->L +0.048 |
| P6.5 size control, no bar | kappa contrast 2.27, area contrast 2.25 (ratio 1.01); Spearman(\|d ln kappa\|, \|d ln A(22)\|) = +0.69 |
| P6.6 usable share >= 0.70 and early-late gap < 0.15 | **HELD, barely**: 0.716 overall, early 0.626 vs late 0.754 (gap 0.128) |

Deviation: the first run of `w6_analyse.py` computed the P6.2 noise null over all 280 rules with 6 core-band runs, not over the bases as registered; fixed to bases only (34), result essentially unchanged (0.025 vs 0.024).
Exploratory: median \|d\| by position decays smoothly, 0.27-0.31 at j = 1..3, 0.23 (4), 0.21 (5), 0.16 (6), 0.15 (7), 0.12 (8), 0.08 (9), 0.06 (10); Spearman(j, median \|d\|) = -0.92. Spearman(j/n, \|d\|) = -0.36, Spearman(j, \|d\|) = -0.37 over pairs
(position, not relative position, is the better coordinate only marginally).

**Reading (pilot; per the interpretation rules).**
- P6.1 and P6.2 true: *early letters have larger effect but late letters matter too; the prefix is a weighting, not a switch.* The effect of a letter falls off smoothly with its position, an order of magnitude above noise even at j = 9-10 (|d| 0.06-0.08 vs noise 0.025).
  This is a causal (interventional) confirmation of the W3b direction, on rules unrelated to the census/pool fit.
- **Size is not separated from this.** The early/late contrast in kappa is the same as in ln A(22) (ratio of contrasts 1.01) and |d ln kappa| tracks |d ln A| (rho +0.69). That is expected at fixed t (kappa and A are tied), so
  the mutation result says "early letters change how fast the pattern grows", which is the growth-prefactor question W4 identified as the real target. It does not say anything beyond that yet.
- **Selection works against the finding, not for it.** Early mutants are dropped more often (62.6% usable vs 75.4%, mostly escapes), plausibly the biggest-effect ones, so the early/late contrast is probably understated. Not tested.
- Caveats: pilot only (40 bases, 36 with both early and late pairs; bases are the unit); position is confounded with which pairs of letters are adjacent and with the base's own prefix; 6 seeds; one window.
- Next: (1) the 200-base W6, now justified; (2) a mixed-effects fit of d on j and letter transition; (3) a mutation that holds area fixed (compare mutants matched on ln A) to see whether position matters beyond area; (4) W3c still unwritten.

**Corrections and exploratory checks after review of the W6 text above (`scripts/w6_checks.py` -> `results/w6_checks.txt`; not registered, run after seeing the result).**
- The sentence "on rules unrelated to the census/pool fit" is **wrong**: the bases are pool rules and every canonical rule of length <= 12 is in the census or pool, so all mutants are census rules too.
  What is new is the paired, interventional design and fresh runs (seeds 401..406), not fresh rules. W6 per-rule ln kappa agrees with the census value for 292 of 299 usable rules (Spearman +0.93).
- "Mostly escapes" is not supported: early mutants unusable 43 of 115 (19 escaped in >= 3 of 6 runs, 24 other, e.g. out of the core band), late 67 of 272 (22 escaped, 45 other). Early mutants escape about twice as often (17% vs 8%), but most of the
  unusable ones in both groups are not mass escapes.
- Stationary restriction (the W2 rule): 262 of 277 usable pairs have a stationary mutant (0.944 early, 0.946 late). Restricted P6.1 median ratio 2.10 (CI 1.68..3.24, 36 bases); P6.3 early 0.779 vs late 0.521. The registered verdicts do not change, and drift does not explain the contrast.
- Audit trail: the addendum and result entries carry nominal times; the actual runs were 22:09-22:22 +13:00 on 2026-10-14 (the notebook timestamps ~23:59 and ~00:30 were wrong; see the notebook correction). The runs used git 797704a; `w6_analyse.py` and `w6_checks.py` were run at HEAD `7eff085`, which is another experiment's commit (`2026-10-t1-excursion-tomography`) and did not touch this folder, which is still entirely untracked.

### 2026-10-15 (W3c): confirmation of the prefix size-controlled gain, registered 2026-10-15 20:55 (+13:00), BEFORE any W3c rule is sampled or simulated

Status when written: git HEAD `da88e61`, working tree dirty (unrelated experiments). No `w3c_*` file exists. Scope was set by the user on 2026-10-15
("run the cheap open steps"); the 200-base W6 and the area-matched mutation test are explicitly *not* part of this.

**Why.** W3b's registered P3b.3 (p = 6 gain < 0.15) held by 0.005 (gain +0.145, CI +0.069..+0.218). The p = 8 gain +0.206 (CI +0.111..+0.300) was found
post hoc in `x3_w3b_checks.py` after picking among p = 3..8 on the same 87 rules, so it is a lead. W3c tests it on rules and runs not used in W3b.

**Sample (frozen).** 300 rules, 150 each of length 13 and 14, from `numpy.default_rng(20261014 + 23)`, same generator as `w3b_sample.py` (uniform over
strings starting with R, rejecting all-R, non-primitive, duplicates) and additionally rejecting every string in `results/w3b_rules.txt`. Probe seeds 501..508
(not used by W3b 201..208, W4 301..306, W6 401..406), `probe 27 8192`, same as W3b: 2400 runs. Sizing: W3b kept 89 of 150 (59%) and its p = 8 CI was
about 0.19 wide; 300 rules should keep about 170 and narrow the interval to roughly 0.13. Instrument check: `src/probe.rs`, `src/fast.rs`, `src/rule.rs` unchanged
since W3b's commit `6ce3793`; `src/bin/probe.rs` gained only `cookie:`/`rcookie:`/`errw:` spec branches, which the `RULE@SEED` path does not touch.

**Estimator (frozen = `x3_w3b_checks.py`, copied verbatim into `scripts/w3c_analyse.py`).** Stationary cohort only (|median g_k| < 0.05, >= 6 core-band runs with
0.25 < alpha_w < 0.42 and kappa > 0). Training table = the census alone (stationary census rules, n <= 12); **W3b rules are not added**. Prefix-p lookup: mean ln kappa of
training rules sharing the first p letters, falling back to the longest shorter prefix with >= 3 rules, else the training mean. Size-controlled model: OLS of ln kappa on
ln A(22) plus the leave-one-out prefix-p mean (training side), fitted on the census, applied to fresh rules with the plain prefix-p lookup. Gain = strict held-out R^2
(against the training mean) of that model minus that of ln A(22) alone. Bootstrap: resample fresh rules with replacement, B = 2000, `default_rng(20261014 + 31)`, percentile 95%.
Also reported (no bar): all-rules cohort, p = 3..8 strict R^2, shuffled-label control (200 permutations, `rng(11)` as in W3b).

**Pre-registered predictions.**
- **P3c.1 (primary).** p = 8 size-controlled gain >= 0.15 **and** bootstrap lower bound > 0. Confidence about 45%: the W3b value was selected as the best of six p, so expect
  shrinkage toward the p = 6 value (+0.145), partly offset by the narrower interval.
- **P3c.2 (secondary).** Same bar at p = 6. Confidence about 35%: the W3b point estimate itself was below 0.15.
- **P3c.3.** Stationary strict held-out R^2 >= 0.40 at p = 8 and >= 0.30 at p = 6 (W3b: 0.74, 0.58; shrunk for selection). About 80%.
- **P3c.4.** ln A(22)-alone strict R^2 within +-0.15 of W3b's 0.569 (the sample is comparable). About 75%. If violated, report W3c as a different regime, not a replication.
- **P3c.5.** Shuffled-label control: median <= +0.02, 95th percentile <= +0.08 (pipeline check). About 90%.
- **P3c.6.** Stationary rules with >= 6 core-band runs: at least 120 of 300 (W3b kept 59%). About 85%. If fewer than 100 are kept, P3c.1/P3c.2 are reported but not judged.

**Decision rules (fixed now).**
- P3c.1 true: the prefix carries information about ln kappa beyond ln A(22) at p = 8 on lengths 13-14. Still not an explanation (a lookup table; extrapolation in length; stationary cohort
  defined by an outcome-related quantity). Next: W5 (area-matched bulk fingerprint), not run here.
- P3c.1 point estimate >= 0.15 but lower bound <= 0: inconclusive; no claim; the pooled W3b+W3c estimate may be reported as exploratory only.
- P3c.1 point estimate < 0.15: the p = 8 lead is attributed to selection among p; the prefix effect beyond size is at most about 0.15 and remains entangled with size.
- Holm: W3c is a single registered primary test (P3c.1); it is not added to the section-8 family. P3c.2-P3c.6 are secondary/checks and not corrected.
- Observational; no causal claim. Pooled W3b+W3c is exploratory regardless.

### 2026-10-15 (W3c): result (2026-10-15 21:19 +13:00, commit `da88e61`; registration above unchanged)

Commands: `uv run scripts/w3c_sample.py` (300 rules, 2400 runs, none shared with W3b), `bash scripts/run_w3c.sh` (`probe 27 8192`, seeds 501..508, 20:57-21:19 +13:00; log `results/w3c_probe.log`,
raw `dumps/w3c_probe.csv` gitignored; binary `target/release/probe` sha256 recorded in the log if the post-step ran), `uv run scripts/w3c_analyse.py` -> `results/w3c_stats.txt`.
Sample: 414 of 2400 runs escaped the board; 176 of 300 rules kept (>= 6 core-band runs; 90 of length 13, 86 of length 14); 162 stationary (92%).
Two restarts of the probe were needed before it ran (my first background launches were killed with the wrapper and one stale process wrote to a deleted file); the reported run is the last, clean one, and the CSV was produced by a single uninterrupted `probe` process.

| Pre-registered | Outcome |
|---|---|
| **P3c.1** p = 8 gain >= 0.15 and CI lower > 0 | **HELD**: +0.240, bootstrap 95% CI [+0.148, +0.347] (162 stationary rules; ln A(22) alone 0.497 -> 0.737 with prefix-8) |
| P3c.2 p = 6 same bar | **FAILED**: +0.117 [+0.049, +0.200] (point estimate below 0.15) |
| P3c.3 strict R^2 p=8 >= 0.40, p=6 >= 0.30 | **HELD**: 0.633, 0.364 |
| P3c.4 ln A(22)-alone R^2 within 0.15 of 0.569 | **HELD**: 0.497 |
| P3c.5 shuffled-label control | **HELD**: median -0.013, 95th percentile +0.048 |
| P3c.6 >= 120 of 300 rules kept | **HELD**: 176 |

Strict R^2 by prefix length (stationary): p = 3..8 -> 0.007, 0.132, 0.297, 0.364, 0.553, 0.633 (W3b: 0.02, 0.21, 0.37, 0.58, 0.56, 0.74), i.e. the same monotone rise with a uniformly lower level.

**Reading (registered decision rule: P3c.1 true).** The p = 8 prefix lookup carries information about ln kappa beyond ln A(22) on 162 further unseen stationary rules of length 13-14, and the W3b lead (+0.206) was not
selection noise (W3c +0.240, intervals overlap). Registered caveats stand: it is a lookup table of 2^7 group means, not an explanation; length 13-14 is an extrapolation; the p = 6 version of the claim does not meet the bar in either W3b (+0.145) or W3c (+0.117).
**Exploratory and weakening (not registered, same script, flagged as such):** in the **all-rules** cohort (176 rules, not restricted to stationary) the size-controlled gain is only +0.006 (p = 6) and +0.031 (p = 8, CI [-0.002, +0.065]),
and the strict R^2 of the prefix alone is 0.31 at p = 8. So the "beyond size" signal lives in the stationary subset, which is defined by a quantity (|median g_k| < 0.05) related to the outcome; whether it is a property of
stationary rules or a consequence of that definition is not separated here. The 14 non-stationary rules (8%) are few, so this is not a clean split either. Pooled W3b+W3c was not computed (registered as exploratory only).
Next (all unstarted): W5 area-matched bulk fingerprint to ask whether the prefix acts through bulk dynamics; a W6 mutation scan matched on ln A (and the 200-base W6, which needs a registered addendum and compute approval).

### 2026-10-15 (W3c): corrections after review (21:23 +13:00, commit `da88e61`)

1. **Provenance.** The result entry above says the probe binary hash was recorded "if the post-step ran". It did not run on the clean launch. The hash (sha256 5fa7fe42...6eb5ad1 for `target/release/probe`; file mtime 2026-10-14 22:02, before the run, not rebuilt since) was appended to `results/w3c_probe.log` after the run.
2. **The "tied to the stationarity filter" reading was wrong about where the filter acts.** The all-rules fresh cohort (176) contains the 162 stationary rules, so 14 extra test rules cannot explain a fall from +0.240 to +0.031. Exploratory cross check
   (`scripts/w3c_cross.py` -> `results/w3c_cross.txt`, unregistered, same estimator): p = 8 gain: train stationary / test stationary +0.240 [+0.148, +0.347]; train stationary / test all 176 +0.112 [-0.046, +0.250]; **train all / test stationary +0.042 [+0.009, +0.079]**; train all / test all +0.031 [-0.003, +0.062].
   So the loss comes from the **training side**: when the census table and the ln A(22) regression include the non-stationary census rules (sd of ln kappa 0.571 vs 0.348), the prefix adds almost nothing even on the stationary test rules. The registered primary (stationary training, stationary test) is unaffected.
   Reading: the prefix lookup works when trained on stationary rules; the non-stationary census rules degrade the lookup table and the area fit. Whether the prefix effect is "about" stationarity or the non-stationary tail is simply a different regime is not decided; the 14 non-stationary test rules add noise (the interval for train-stationary / test-all includes 0).

### 2026-10-15 (W5): implementation addendum, registered 2026-10-15 ~21:40 (+13:00), BEFORE any W5 code is run

Status when written: git HEAD `da88e61`, dirty tree. No `bulk` code, `w5_*` file or W5 run exists. P5.1-P5.4 above are **unchanged**; this entry fixes the details the text left open
and records the places where the registered text cannot be implemented as written. Scope set by the user: "work on W5"; nothing else (W6-200, mutation test) is started.

**Deviations from the W5 text (all fixed now, before data).**
1. **Seeds.** A blank-board ant is deterministic, so "4 seeds" would be copies. Pool rules run as `RULE@SEED` patched starts, seeds 601..606 (unused: W3b 201-208, W4 301-306, W6 401-406, W3c 501-508), 6 seeds so `icc_groups` (which drops groups < 6) works.
   Discovery rules (census minus pool-192) run once on the blank board, which is how their census kappa was made. A blank-board run of every pool rule is added as a patched-vs-blank check.
2. **Recording length.** Reaching A0 = 20 000 takes about 2^20 steps (A(2^22) is about e^10.7 = 44 000, A ~ t^(2/3)), so T = 2^22 would multiply the area by about 4. T is **2^18 for every rule** (uniform, not per rule),
   giving a growth factor of about 1.1-1.3; the factor is reported per run and runs with factor > 1.5 are flagged and excluded from the primary analysis. A run that has not reached A0 by 2^26 steps, or touches the board edge, is dropped (status column).
3. **Depth bound.** Distance to the territory bounding box is not conservative (indented edges, internal unvisited pockets). Instead, at the step A0 is first reached, a multi-source BFS gives each visited cell its 4-neighbour distance to the nearest
   unvisited cell (depth 0 = a probe boundary cell). Unvisited cells only disappear, so this depth is a **lower bound for the whole recording**; no refresh is needed. A step is *bulk* if depth(start cell) >= D0 = 20.
4. **Depth gate on lagged observables.** A lagged quantity at lag m uses the pair (j-m, j) only if **every** step j-m..j is bulk (running run length). The usable-pair count per observable is reported. If A0 = 20 000 (R about 80) leaves too few bulk
   pairs at lag 2^12, that observable is reported as unusable rather than changed.
5. **Size leak.** t* (steps to reach A0) is the growth prefactor in another form. It is recorded, never used as a fingerprint, and corr(observable, ln t*) is reported as a leak diagnostic in addition to the registered conditioning on ln A(22).
6. **Target.** `rules_pool.csv: lnk` is the mean over core-band runs of the **k = 26** window kappa (the end of `per_rule`'s 20..26 fit), not k = 25 as in the W5 text. I follow the text: the target is recomputed at **k = 25** from the same b2 / item21 / patched runs and the same core-band filter, and the k = 26 mean is reported as a sensitivity row.

**Definitions (frozen).** All lags are in absolute steps. Steps are indexed by the cell they start on; h = heading after the step; dh = (h_after - h_before) mod 4; turn sign s = +1 if dh = 1, -1 if dh = 3, 0 if dh in {0, 2} (straight or U-turn; rotor, pw, rw have those).
1. `I_turn` = sum_{m=1..256} C(m), C(m) = (<s_j s_{j-m}> over valid pairs - mean^2) / var, mean and var over all bulk steps.
2. `msd64`, `msd512`, `msd4096` = <|p_j - p_{j-L}|^2> / L over valid pairs, L = 2^6, 2^9, 2^12; `msd_exp` = log2(MSD(4096)/MSD(64))/6.
3. `head64` = <e(h_j) . e(h_{j-64})> over valid pairs (cosine of the heading difference).
4. `ret32` = P(first return to the **same cell** within 32 steps) = (# bulk steps i with i..i+32 all bulk whose next visit to that cell is at i+g, g <= 32) / (# bulk steps i with i..i+32 all bulk). **Deviation:** the W5 text said "return to the 3x3
   neighbourhood", which every step satisfies trivially at lag 1; the same-cell version is the non-trivial one. `ret_tail` = slope of ln(count/bin width) against ln(gap) of the first-return-gap histogram over log2 bins 6..11 (exploratory shape of the tail; right-censoring by leaving the bulk biases it, so only its rule-to-rule variation is read).
5. `reuse64` = fraction of bulk steps whose start cell was last visited (as a step start, any time since t = 0) within the previous 64 steps.
6. `ent_pi` = entropy of the colour mix pi_k of cells in the bulk mask at the end of recording, divided by ln n; `mean_col` = mean colour under the walker over bulk steps, divided by n - 1. For `rotor` the colour is the arrow (n = 4); for `pw` / `rw` colour is constant, so these two are undefined there.
7. Also recorded: bulk fraction of recorded steps, t*, area at A0 and at the end, bulk mask volume, dh histogram, U-turn fraction.
Declared list for P5.1: `I_turn`, `msd64`, `msd512`, `msd4096`, `msd_exp`, `head64`, `ret32`, `ret_tail`, `reuse64`, `ent_pi`, `mean_col` (11); **primary three** (as registered): `I_turn`, `msd512`, `ret32`.

**Estimator (frozen, W3c form).** Discovery = census (non-bursty, `rules_census.csv`) rules with `in_pool` False, blank-board fingerprint, target = their census ln kappa; confirmation = pool-192 rule means (6 patched seeds; fingerprints averaged over seeds, runs with growth factor
> 1.5 or no A0 dropped; >= 4 usable seeds required), target = pool rule-mean ln kappa(k = 25). Model: OLS of the target on [1, ln A(22), z(obs)], z-scored with the training mean/sd after clipping at the training 1st/99th percentiles. Gain = strict held-out R^2 (against the training mean)
of that model minus that of [1, ln A(22)] alone, both trained on the same discovery rules. **Primary cohort: stationary** (|g_k| < 0.05; discovery stationary rules train for stationary pool test, as in W3c); the all-rules cohort is reported beside it (W2 and W3c
showed the two behave differently, so neither is dropped). Bootstrap over pool rules, B = 2000, `default_rng(20261014 + 41)`, percentile 95%. Within-pool secondary: 5-fold CV grouped by (n, 5-prefix) on the pool alone.

**Multiplicity within P5.1.** Eleven declared observables could each pass, so "at least one reaches 0.15" has an inflated chance. P5.1 is judged as: **max gain over the 11 >= 0.15 AND permutation p <= 0.05** for that max, the null built by permuting
the pool targets within n (10^4 permutations, `rng(43)`; the whole 11-observable max is recomputed per permutation, with the model refit on the fixed discovery set). The primary-three max is reported separately. P5.1 enters the section-8 family as before (Holm over the family is applied by the reader; this
entry fixes that W5 contributes one p-value, the permutation p of the max).

**Controls and checks.**
- Planted signal (wording clarified at 21:50, still before any run): replace both the discovery and pool targets by y = ln A(22) coefficient part + s * (sqrt(0.3) z(obs) + sqrt(0.7) e), i.e. the target's residual after ln A(22) is a planted R^2 = 0.3 share of z(`I_turn`) plus noise e ~ N(0,1) (s = observed residual sd); the pipeline must recover a gain within 0.1 of 0.3 (a pipeline that cannot see a planted effect makes a null meaningless).
- Negative control: shuffled labels (permutation null above). Positive control: the same pipeline on c (`c` letters give R^2 0.66-0.78; bulk observables should predict c at least as well if they carry rule dynamics).
- Class and size: stationary vs all (above); corr(obs, ln t*) and corr(obs, ln A22) reported.
- P5.3 (reproducibility): ICC across the 6 patched seeds of each observable on the pool (`icc_groups`), plus patched-vs-blank agreement (Spearman) on the pool.
- P5.4: rotor `msd512`, `msd_exp` printed; no numerical bar. `rw:SEED` x 6 is the negative control (MSD/L about 1 per step, `msd_exp` about 1; ICC meaningless).
- Code checks before any result is used: `tests/kappa_rs_bulk.rs` (fingerprint vs a HashMap brute oracle on random trajectories; `run_bulk` positions and colours vs `reference::Ant`; first-hit-A0 step vs `probe`'s windowed area), passing in `--release`.

**Specs and runs.** `scripts/w5_specs.py` -> `results/w5_specs.txt`: pool-192 x seeds 601..606, pool-192 blank, census-minus-pool blank, rotor:1..6, pw:0.5:1..6, rw:1..6. Board 2048 (R about 100 fits; edge touch = dropped).
Binary `examples/kappa_rs_bulk.rs` (thin wrapper) over `src/bulk.rs`; `scripts/run_w5.sh` writes `dumps/w5_bulk.csv` with a `.done` marker, git hash and binary sha256 in `results/w5_run.log`; `scripts/w5_analyse.py` -> `results/w5_stats.txt`, `results/w5_rules.csv`.

**Predictions that stand (from the plan; not edited).** P5.1 about 25%, P5.2 about 90% (shortfall), P5.3 ICC >= 0.7, P5.4 control reading only. Additional, stated now: I expect `ret32`, `reuse64` and `msd_exp` to be the most reproducible across seeds and `ret_tail` the least;
and I expect any gain, if present, to shrink in the all-rules cohort (W3c pattern). Decision rules: P5.1 true -> carry the observable into W10 and design a bulk-matched mutation test; P5.1 false with P5.3 true -> clean null for "bulk transport sets kappa"; P5.3 false -> fingerprints cannot explain a rule property, report as instrument failure.
(The first write of this entry was cut off mid-sentence by the shell tool; the text from "Code checks" onward and the planted-signal wording were completed at 21:50, before any code existed.)
(Timestamp correction, 2026-10-15 21:40 by the clock: the W5 addendum above is stamped "~21:40" and its completion note "21:50", which were guesses. File mtimes show it was complete at 21:35, before `src/bulk.rs` (21:37) or any run (started 21:38:15). The content is unchanged since then.)

### 2026-10-15 (W5): result (21:48 +13:00, commit `da88e61`, dirty tree; addendum above unchanged)

Commands: `uv run scripts/w5_specs.py` (3796 specs); `cargo test --release --test kappa_rs_bulk` (5 tests, and the full `cargo test --release` passes; two deliberate source mutations, `>=` to `>` in the depth threshold and `>` to `>=` in the valid-gap test, were each caught by a test);
`bash scripts/run_w5.sh` (`kappa_rs_bulk 20000 262144 20 2048`, 21:38:15-21:40:40, one uninterrupted process; log `results/w5_run.log` with the binary sha256; raw `dumps/w5_bulk.csv` is gitignored, sha256 2af0d6c4d5616432...);
`uv run scripts/w5_analyse.py` -> `results/w5_stats.txt`, `results/w5_obs.csv` (per-run derived observables), `results/w5_rules.csv` (pool rule table).
Reproducibility checked: re-running the binary on a 300-spec subset with one thread gives byte-identical rows; two analysis runs give identical `w5_stats.txt`, `w5_obs.csv` and `w5_rules.csv`. (The first draft of the analysis was not deterministic: polars `group_by` order fed the seeded bootstrap. Rows are now sorted by rule before any seeded resampling. The numbers below are from the fixed script.)

Sample: 3796 specs, 3772 ant runs usable (6 blank rules never reached A0 in 2^26 steps). Growth factor area_end/area0: median 1.15, 90th percentile 1.30, 2.2% above the 1.5 bar. t* median 2^20.1. Bulk steps are a median 51% of the recorded steps (10th percentile 37%).
Pool: 187 of 192 rules have >= 4 usable patched seeds (168 stationary). Discovery: 2395 of 2434 census-minus-pool blank runs usable (2024 stationary).

| Pre-registered | Outcome |
|---|---|
| **P5.1** a declared observable reaches held-out gain >= 0.15 over ln A(22) (stationary cohort; permutation p <= 0.05 for the max of 11) | **FAILED**. Best gain **+0.040** (`msd64`, 95% CI [-0.009, +0.085]); best of the primary three `ret32` +0.039 [-0.007, +0.089]; `I_turn` +0.001. R2 with ln A(22) alone 0.581, at best 0.62 with an observable added |
| **P5.2** bulk observables do not reach the 0.3 explanation bar | **HELD**. Gain <= 0.04; exploratory joint model of 8 observables +0.028; any one observable alone has held-out R2 <= +0.03 on the stationary cohort |
| **P5.3** ICC across seeds >= 0.7 | **FAILED for the primary set**: `I_turn` 0.56 (`msd512` 0.94, `ret32` 0.998). Also reproducible: `msd64` 0.98, `reuse64` 0.997. Not reproducible: `msd4096` 0.09, `head64` 0.11, `msd_exp` 0.29, `mean_col` 0.35, `ent_pi` 0.38, `ret_tail` 0.44 |
| P5.4 (control reading only) | Rotor MSD/L = 0.59, 0.47, 0.21 at L = 64, 512, 4096, falling with L as subdiffusion should; rotor `msd_exp` 0.74; rotor bulk fraction 0.30; rotor growth factor 1.63 (above the bar; the rotor is not in the pool analysis) |

Planted-signal check (I_turn, residual R2 0.30 planted): recovered gain +0.117, which is 0.234 of the unexplained variance (criterion: within 0.1 of 0.30) -> **PASS**, with attenuation to about 78% of the planted strength.

Stated expectations that did not hold: I expected `msd_exp` to be among the most reproducible observables (ICC 0.29: no); `ret_tail` the least (0.44; `msd4096` 0.09 and `head64` 0.11 are lower); and any gain to shrink in the all-rules cohort (it does not: best +0.050, `msd64`; `msd_exp` +0.049).

**What the numbers say.**
- [RETRACTED in part, see 'Corrections after review' below: the gain is carried by five rules and its bootstrap CIs include 0.] The small gains are not noise. Under the registered null (pool targets permuted within n) the maximum over the 11 observables has p = 0.0005, and under a stricter exploratory null (observable permuted within n, size and target kept) p = 0.0006. They are small: R2 rises from 0.58 to about 0.62, i.e. the bulk observables account for roughly a tenth of what ln A(22) leaves unexplained.
  The three observables that carry it (`msd64`, `ret32`, `reuse64`) are one signal [the 0.95-0.99 patched-vs-blank figure measures reproducibility, not redundancy; the pairwise correlations are in the corrections below], and they point the same way (less displacement over 64 steps, more same-cell return within 32 steps, more reuse of cells visited in the last 64 steps all go with higher kappa; coefficient on `ret32` +0.081 in ln kappa per sd). A lead about how locally the walker reuses the interior, not a mechanism.
- Their raw correlation with ln kappa is large only in the all-rules pool (0.5 for `ret32`), and that is mostly the few non-stationary, high-kappa rules plus size; inside the stationary cohort it is 0.15 in the pool and 0.14 in the discovery set. Raw associations in the all-rules pool are a poor guide.
- [SUPERSEDED, see corrections: P5.3 failed on the registered primary set, so the frozen branch is 'instrument failure'; the following is my post-hoc split.] Registered decision rule: "P5.1 false with P5.3 true -> clean null for 'bulk transport sets kappa'". P5.3 is true for the observables that carry the signal (ICC >= 0.94) and false for the primary `I_turn`. So the null applies to local-displacement and reuse measures at lags <= 512, and the turn-sign sum is not a usable fingerprint here.
  **The lag-4096 observables are mostly unreproducible, not shown to be uninformative**: at A0 = 20 000 the bulk core is about 10 000 cells, lag-4096 pairs are confinement-limited (median 13 400 valid pairs; 4.4% of runs below 1000), and those are exactly the lags where subdiffusion would show.

**Caveats that can change the reading.**
1. *Selection.* The five pool rules without 4 usable seeds have mean ln kappa +0.86 against -0.10 for those kept: the fast-growing, high-kappa rules are the ones dropped. Removing the growth-factor exclusion changes the stationary-cohort gains by <= 0.001 (sensitivity table), so the exclusion is not what drives the null, but the extreme tail is under-represented in the test set.
2. *Training and test targets differ.* Discovery targets are single blank-board census runs at k = 26; pool targets are 6-12-run means at k = 25 (recomputed; correlation with the k = 26 mean 0.96; best gain on the k = 26 target +0.041). Fingerprints agree between patched and blank runs for `ret32`, `reuse64`, `msd64` (Spearman 0.95-0.99), not for `msd4096`, `head64`, `msd_exp` (0.00-0.23).
3. *The bulk -> c check failed (and the actual section-4.4 positive control, letters -> c, was run later and passes; see corrections).*  I wrote that bulk observables should predict c at least as well as kappa; they do not (best gain over ln A(22) on c is +0.024, `I_turn`, CI [+0.001, +0.044]). c is a boundary quantity, so this is not evidence that the pipeline works on bulk-driven targets. The only evidence that it can see a planted bulk effect is the planted-signal check (78% recovered).
4. *The negative walkers have no bulk.* `pw:0.5` and `rw` territories at A0 = 20 000 are porous (internal unvisited pockets are depth-0 cells), so n_bulk = 0 and they say nothing about the fingerprints. Only the rotor is a usable control (one `rw` run also touched the board edge).
5. *One A0 and one T.* The frozen depth >= 20 leaves a core of about half the territory. Rule length is not controlled beyond the pool/discovery split.

**Exploratory, run after seeing the table (labelled in `w5_stats.txt`).** Observable alone, the joint model, within-pool grouped CV (stationary gain +0.03 for `msd64`/`reuse64`/`ret32`; all-rules +0.07 to +0.11), the growth-exclusion and k = 26 sensitivity tables, the c positive control. The within-pool all-rules CV gives +0.10 and +0.11 for `msd64` and `msd512`, larger than the discovery-to-pool numbers; with 64 prefix groups and non-stationary rules in the mix I do not read that as a different finding.

**Next (all unstarted).** (1) The small `ret32`/`reuse64` association is a candidate for a W6-type intervention (mutants matched on that observable and on ln A); it needs its own registered addendum. (2) The null at the 0.15 bar redirects the programme to edge-side quantities (W4's ln(new cells per step) term, W8 strip geometry, W10 front matching). (3) A larger A0 (say 100 000 cells) would make the lag-4096 observables usable and is the one change that could overturn the "null for transport" reading; it costs about 5x the compute (still minutes) and needs a registered addendum.

### 2026-10-15 (W5): corrections after review (22:00 +13:00, commit `da88e61`, code untracked)

An advisor review of the result entry found four statements that the numbers do not support. Checks were run on the existing data (no new simulation); they are in `results/w5_stats.txt` under "added after review (exploratory)". The registered verdicts P5.1-P5.3 are unchanged.

1. **Redundancy.** I called `msd64`, `ret32` and `reuse64` "one signal" and cited the patched-vs-blank Spearman (0.95-0.99). That statistic measures reproducibility across start conditions, not redundancy. The right numbers are pairwise Spearman correlations across rules:
   pool stationary (168 rules) msd64-ret32 -0.92, msd64-reuse64 -0.96, ret32-reuse64 +0.98; discovery stationary (2024 rules) -0.90, -0.93, +0.99. So they are close to the same quantity (the claim stands, with these as the support).
2. **"The small gains are not noise" is withdrawn.** All three bootstrap CIs in the primary cohort include 0, and the per-rule decomposition shows why the permutation p (0.0005) and the CIs disagree: **five pool rules supply 89% (`msd64`), 97% (`ret32`) and 96% (`reuse64`) of the held-out gain, and without them the gain is +0.005, +0.001, +0.002.**
   The rules are near-all-R extremes of the observable (`RRRRRRLRRRRL`, `RRRRRRLRRRL`, `RRRRLRRRRRLL`, `RRRLR`, `RRLLLLLLLR`: `ret32` z of +1.9 to +3.0). The all-rules cohort looks the same: five rules (four low-kappa non-stationary ones with ln kappa -1.3 to -2.4, and `RRRRRRLRRRRL`) supply 84-90% of its +0.047..+0.050 gain, and without them it is +0.007..+0.012.
   What is supported: P5.1 failed; the held-out association of any bulk observable with kappa beyond area is, apart from a handful of extreme rules, zero to within +-0.01 on this test set. The permutation test rejecting zero says the alignment of those few rules is unlikely by chance, not that there is a general effect.
   (Also relevant: the registered target-permutation null has a positive median gain, +0.011 stationary and +0.014 all-rules, because it destroys the ln A-to-kappa relation and the added predictor can no longer be penalised the same way; so it is not zero-centred for "adds beyond ln A". The observable-permutation null, centred near +0.004, is the meaningful one. The two disagree in the all-rules cohort, p = 0.06 against 0.0001.)
3. **The section-4.4 positive control.** The control that is required is the one in the W0 gate: letters predict c. It was not run in the first pass (what I ran, bulk observables -> c, is a different check, and it failed: best gain +0.024). It is now run through the same strict-R2, census-minus-pool -> pool code:
   letters (one-hot of the first 12 positions, n, fraction R; ridge 10) give held-out R2 on **c = +0.768 (stationary) and +0.773 (all)**, against 0.767 from W0 CHECK4. **The pipeline control passes.** R2 of ln A(22) alone on ln kappa is 0.581 (stationary), in line with W3b 0.569 and W3c 0.497 from the same estimator family.
   Side result, not investigated: the same letters model gives held-out R2 on ln kappa of +0.171 (stationary) and +0.075 (all) when trained on the census, against about 0 for the W0 LOO on the pool; the protocols differ (census-trained, strict R2 against the training mean), so I do not read it as a contradiction of W1/W3.
4. **Decision-rule branch.** P5.3 was judged on the registered primary three and **failed** (`I_turn` ICC 0.56). The frozen decision rule maps "P5.3 false" to "fingerprints cannot explain a rule property, report as instrument failure", and that is the registered reading. The split I wrote (a null for the reproducible observables `msd64`, `msd512`, `ret32`, `reuse64`, an instrument failure only for `I_turn`) is my post-hoc interpretation, and I label it so.

Smaller corrections.
- The result entry said both source mutations were `>=` to `>`; the valid-gap mutation was `>` to `>=` (fixed above; the NOTEBOOK had it right).
- The exploratory list was too long. **Registered in the addendum** (not exploratory): the grouped within-pool CV, the c control (as the pipeline check), the planted-signal check, patched-vs-blank agreement and the leak diagnostics. **Exploratory, added after seeing the table**: observable-alone R2, the 8-observable joint model, the growth-exclusion and k = 26 sensitivity rows, the bulk -> c check, and everything in this correction (redundancy, concentration, dropped-rule reasons, letters control).
- Deviation from the addendum's wording: the permutation null draws a separate within-n permutation for each observable (seed varies with the observable), not one shared permutation per replicate, so the "max over 11" is the max of 11 independent nulls. That makes the max larger under the null, so it is conservative for P5.1 (which failed anyway).
- Why the five pool rules were dropped (stationary? lnk25; seeds with growth > 1.5 / n_bulk < 1000): `RLLRRRLRRRRR` (no, +1.29; 4/1 of 6), `RLLLRRRLRLRR` (no, +1.88; 6/0), `RLLRRRLLLLLL` (no, +0.06; 3/0), `RLLLLRR` (no, +1.21; 4/0), `RLRRRLLLRLLL` (yes, -0.13; 3/3). Four of five are non-stationary and failed the growth bar, so the exclusion bites in the all-rules cohort and not in the stationary one (the stationary test set is 168 with or without the exclusion).
  Without the growth exclusion the all-rules test set is 191 rules and the best gains are the same size (`msd_exp` +0.044, `reuse64` +0.038, `msd64` +0.040), so the exclusion is not what produces the all-rules numbers. My earlier sentence "the fast-growing high-kappa rules are the ones dropped" stands for the all-rules cohort only.
- P5.2 is judged on the gain over ln A(22) and on the observable-alone held-out R2 (both well below 0.3). Read literally, R2(ln A + observable) = 0.62 exceeds 0.3, but 0.58 of it is ln A(22), which is the size confound the plan says not to count.
- The depth comment in `src/bulk.rs` ("stored depth = 1 + distance") was wrong: the stored value is the distance (boundary cell 1); the behaviour matches the addendum and the test. Comment fixed after the run; no code change.
- Provenance: the code (`src/bulk.rs`, `tests/kappa_rs_bulk.rs`, `examples/kappa_rs_bulk.rs`, the three scripts) is untracked at git `da88e61`. Its sha256 values are appended to `results/w5_run.log`. Nothing is committed.
- Timestamps in NOTEBOOK.md: the entries stamped 21:38 and 21:48 were written at about 21:50 (the clock times of the run and of the first analysis are in the README entries). Corrections to the NOTEBOOK follow as new entries.

## Prefix audit addendum (2026-10-15 22:36 +13:00; git 275c2af; before analysis)

Continue the surviving W3c prefix-8 lead before another sweep. This is a new robustness analysis of already inspected data, not an independent confirmation. Freeze p=8, stationary census training and stationary W3c test; retain all-rules sensitivity. Compare the original leave-one-out lookup with deterministic five-fold cross-fitted lookup (seed 20261015), always fitting the final test lookup on all training rules. Folds split rules, not prefixes: the estimand is transfer to new suffixes of represented prefixes. Prefix groups with fewer than three training observations fall back to shorter prefixes.

Test both linear ln A(22) control and a continuous piecewise-linear control with training-area knots at the 10,25,50,75,90 percentiles. Training range extrapolates linearly. This asks whether a prefix merely repairs a nonlinear area relation. Fit OLS on area basis and lookup, without tuning on W3c. Report strict held-out R2, paired gain CI (2000 rule bootstraps), and the share of gain from the five largest positive individual contributions; also remove those five as a labelled influence diagnostic, not a new confirmatory test. Report prefix support and test-area extrapolation. Repeat both cohorts. No alternative prefix lengths are searched.

Expectations before this analysis: A1 cross-fitted stationary linear gain >=0.15 with lower CI >0; A2 flexible-area gain >= half the cross-fitted linear gain with lower CI >0. Failure of A2 weakens the beyond-size reading; failure of A1 weakens estimator robustness. Neither success supplies a mechanism. Historical W3c results stay unchanged. Save input and source hashes and exported per-rule predictions, and update the shareable notebook. Existing working-tree changes are preserved. No new sweep or commit.

### Prefix audit result (2026-10-15 22:40 +13:00; 275c2af, dirty tree)

Command: uv run experiments/archive/2026-10-kappa-rule-space/scripts/prefix_audit.py (WSL, required UV environment). Sources and input SHA256s: results/prefix_audit.json; per-rule predictions: results/prefix_audit_predictions.csv. Seed 20261015; 2000 paired rule bootstraps. This audit uses existing W3c trajectories, not fresh confirmation.

| Stationary cohort, 162 rules | Area-only R2 | With prefix R2 | Gain [95% CI] |
|---|---:|---:|---:|
| Historical LOO, linear area | 0.497 | 0.737 | +0.240 [0.153,0.344] |
| Five-fold encoding, linear area | 0.497 | 0.736 | +0.240 [0.156,0.342] |
| Five-fold encoding, flexible area | 0.528 | 0.729 | +0.201 [0.103,0.311] |

A1 and A2 held. Flexible control retains about 84% of the linear gain. Five largest positive contributors supply 40% of flexible-control gain; removing them leaves +0.150 (test-selected influence diagnostic). All test rules have direct prefix-8 support and no test areas lie outside the training range. All-rules training/testing gives flexible-control crossfit gain +0.041 [-0.018,0.103], and -0.003 after removing its five largest contributors. The stationary training restriction remains essential; do not generalise the result to all rules.

Interpretation: retain the stationary prefix lead. Cross-fitting and nonlinear area adjustment do not explain it away. This is not a mechanism: a noisy area snapshot cannot eliminate all growth-history confounding, test rules share prefixes, and test-only bootstrap omits training uncertainty. Existing W5 letters-to-c control passes; no permutation test or new noise-ceiling estimate is made in this audit. Calibration checks exact area-only and planted-signal recovery. The next causal experiment should compare mutations at matched area and measure early-colour exposure.

Shareable write-up: [notebooks/prefix-audit.ipynb](notebooks/prefix-audit.ipynb), generated with scripts/prefix_audit_notebook.py and executed with uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-kappa-rule-space/notebooks/prefix-audit.ipynb. New results await a user-requested commit.

Verification: cargo test --release passed (results/prefix_audit_release.log). Two independent analysis processes produced identical JSON and prediction-CSV hashes after rounding summary floats to 12 decimal places (initial differences were at about 1e-16). The shareable notebook executed successfully from a clean kernel. No dependencies changed and no commit was made.

## W6 matched-area reanalysis (2026-10-15 23:19 +13:00; git b3a0f76, dirty tree; registered BEFORE `w6m_analyse.py` exists or is run)

Scope: **no new simulation.** Reanalysis of the 277 usable W6 pilot pairs (`results/w6_pairs_scored.csv`, raw `dumps/w6_probe.csv`, seeds 401..406). It asks whether the early/late contrast in |d ln kappa| survives when
the mutant and base have matched area. What I have already seen: the pooled W6 contrast (ratio 2.21), the contrast in |d ln A(22)| (ratio of contrasts 1.01) and Spearman(|d ln kappa|, |dA|) = +0.69. I have **not** looked at d ln kappa within any
|dA| stratum; I have only counted pairs per caliper (early/late: 19/88 at |dA|<0.10, 24/122 at 0.15, 33/146 at 0.25). The per-position exposure measurement and new mutant runs are another folder's job
(`experiments/archive/2026-10-kappa-prefix-exposure`, in progress by another session); this entry does not touch it. dA = mean_seeds ln A(22, mutant) - mean_seeds ln A(22, base); d = mean_seeds ln kappa difference (as in W6).

**Tests.** Bases are the unit for every CI (bootstrap over bases, 2000 draws, `default_rng(20261014 + 31)`, rules sorted before resampling). Early = pos 1..3, late = pos >= 4 (W6 definition).
- **M1 (caliper contrast).** Among pairs with |dA| < 0.15: pooled median |d| early / late >= 1.3 with bootstrap lower bound > 1. Prior ~35%: kappa and A are tied at fixed t, so most of the W6 contrast should be area, but W3c left a stationary-cohort prefix gain beyond ln A of about +0.24, which argues for a surviving residual.
- **M2 (regression).** OLS d = beta * dA + gamma * early + eps on all usable pairs; **gamma != 0** (base-bootstrap 95% CI excludes 0) means position acts beyond area. Prior ~40%. Reported alongside: the same model with log(pos) in place of early (slope reported, no bar), and the residual contrast median|r| early / late.
- **M3 (late letters at fixed area).** Median |d| of late pairs with |dA| < 0.15 is >= 1.5x the replicate-noise null of W6 P6.2 (0.036, raw 3-vs-3). Prior ~50%. False means late mutations move kappa only through area.
- **Sensitivity (no bars):** calipers 0.10 and 0.25; M1 and M2 restricted to pairs with a stationary mutant; M2 with dA replaced by its estimate shrunk for seed noise (dA reliability from the between-seed sd of dA over 6 seeds, errors-in-variables attenuation of beta reported as a bound).

**Interpretation rules, fixed now.**
- M1 false and M2 gamma CI includes 0: the W6 position gradient is a **growth-prefactor (area) effect**; at matched area early letters do not matter more. The exposure instrument should then explain area change, not residual kappa, and this agrees with the W3c all-rules collapse.
- M2 gamma != 0 (or M1 true): position matters beyond a one-snapshot area, which is the live version of the exposure story. Caveat that stays attached to any such result: one noisy ln A(22) snapshot cannot absorb the whole growth history (same caveat as the prefix audit), so this would be motivation for the matched-area mutants, not a mechanism.
- Fewer than 20 early pairs in a caliper, or CI width of the ratio spanning 1.3 and 1: the result is **underpowered**, said as such, not read as a null.

### 2026-10-15 (W6 matched-area): result (23:35 +13:00; git b3a0f76, dirty tree; registration above unchanged)

Command: `uv run experiments/archive/2026-10-kappa-rule-space/scripts/w6m_analyse.py` -> `results/w6m_stats.txt` (reads ignored `dumps/w6_probe.csv`; two runs byte-identical). Same 277 usable pairs, 39 bases (asserted equal to W6's scored table).

| Registered | Outcome |
|---|---|
| **M1** caliper \|dA\|<0.15, pooled median \|d\| early/late >= 1.3, CI lower bound > 1 | **HELD**: early n=24 (22 bases), late n=122 (37 bases); medians 0.277 vs 0.065; ratio **4.26 [1.62, 5.40]** |
| **M2** gamma != 0 in d = b0 + beta dA + gamma early | **FAILED**: beta = 0.985 [0.883, 1.111], gamma = +0.034 [-0.030, +0.094] |
| **M3** late median \|d\| at caliper >= 1.5x raw null 0.036 | **HELD**: 0.065 = 1.81x |

Sensitivity (no bars): ratio 4.84 [1.71, 6.47] at 0.10 (early n=19, **flagged underpowered by the < 20 rule**) and 3.32 [1.37, 4.78] at 0.25 (n=33); stationary mutants only 4.54 [1.79, 5.58] and gamma +0.043 [-0.023, +0.106];
residual contrast median\|r\| early/late 2.71 [1.78, 4.46]; log(pos) slope -0.044 [-0.085, +0.002]; dA reliability 0.979, so errors-in-variables correction moves beta only to <= 1.006.

**Reading, per the frozen rules.** M1 true, M2 false is not one of the two clean branches; the rules said M1 true -> position matters beyond area, and that is what holds, but in a specific form:
- **Mean:** ln kappa moves one-for-one with ln A(22) (beta = 0.985, CI contains 1) and early letters add no systematic shift (gamma ~ 0).
- **Spread:** at matched area, early mutants still move ln kappa by a median 0.28 (signs mixed: 14 up, 10 down), late ones by 0.065. So early letters change kappa *at fixed area*, in either direction; the position effect is in the variance of the area-residual, not its mean.
  That is why a signed regression cannot see it and why a W3c-style linear prefix lookup (a mean-shift model) would capture only part of it.
- It is **not** an artifact of noisier area for early pairs (median paired seed SE of dA 0.028 early vs 0.026 late; 0.028 vs 0.025 inside the caliper).
- Late letters also move kappa at fixed area, 1.8x the replicate null (M3), but weakly.

**Exploratory, looked at after the result (not registered):** inside the caliper, median \|d\| by position is 0.32 (pos 1, n=5), 0.31 (pos 2, n=13), 0.07 (pos 3, n=6), then 0.10, 0.12, 0.07, 0.08, 0.06, 0.05, 0.05, 0.14 (pos 4..11). Position 3 behaves like a late letter, so the "early" class is really positions 1-2
(18 of the 24 pairs), and the W6 early = 1..3 definition dilutes it. Pilot-scale: positions 1 and 2 have 5 and 13 pairs.

**Caveats that stay attached.** (1) Pilot: 24 early pairs from 22 bases, one window (k = 26), 6 seeds; the 0.15 caliper was fixed before looking but is arbitrary (0.10 is flagged underpowered, 0.25 agrees). (2) Matching on a single ln A(22) snapshot does not match the growth history (the prefix-audit caveat applies unchanged); the
true test is the matched-area mutants with measured exposure in `experiments/archive/2026-10-kappa-prefix-exposure`, not this. (3) These mutants are census rules and their kappa is already in the W3 data; nothing here is fresh rules. (4) The "variance not mean" reading is mine, from the sign split plus residual contrast; no variance test was registered.
(5) w6m_peek.py in `scratch/` produced the exploratory numbers (seA split, per-position medians); it is not a committed result script.

**What this changes.** The pilot's "early letters matter more" is *not* only a growth-prefactor effect: with area matched the contrast is larger (4.3x vs 2.2x), because mutations that change area also change kappa one-for-one and dilute it. Positions 1-2 are the leading candidates for the exposure instrument's early class.
Next: the matched-area mutants with measured exposure belong to `2026-10-kappa-prefix-exposure` (it should treat the early class as positions 1-2, and expect sign-mixed effects, so its paired-direction P1 (>= 70% sign agreement) is the right test and a mean-shift model is the wrong one).
