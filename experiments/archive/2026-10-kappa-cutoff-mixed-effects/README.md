# kappa-cutoff-mixed-effects: does the kappa residual predict the excursion cutoff ratio, rule by rule, across seed halves?

Registered 2026-10-16 00:10 NZDT, base commit `997c9b2` (dirty tree), **before any model was fitted** and before
`scripts/mixed.py`, `scripts/calibrate.py` or `scripts/fit.py` was run. This is the open, previously unregistered
follow-up of `experiments/archive/2026-10-kappa-matched-area/` (noise-floor section, last sentence).

**No new simulation.** Only input: `experiments/archive/2026-10-t1-excursion-tomography/results/t1b_cutoff_seeds.csv`
(committed; sha256[:16] `e813c6f21f63421c`; patched-start windows k = 22 and 25, 44 rules, 6-8 seeds each, escaped
windows excluded as in the parent experiment). Columns used: `rule, seed, k, area, lnkappa, ln_ratio`
(`ln_ratio` = ln(L_99.9/R_eq), the excursion cutoff ratio). `ln A := ln area`.

## Question

Matched-area pairs (parent experiment) showed the higher-kappa rule has the smaller cutoff ratio in ~80% of pairs, but
that needed matching on noisy ln A, used only 62-67 non-independent pairs, and shared trajectories between the kappa and
ln_ratio sides unless split by parity (N3). Is there a **rule-level** association between the kappa residual (kappa at
given ln A) and ln_ratio, using all 44 rules, no matching, with kappa/ln A measured on one seed half and ln_ratio on the
other half, and does it predict out of sample?

## Model (fixed now)

Per k (22, 25) separately, and pooled over k as a secondary check. Seeds are split into two disjoint halves.
Primary split: **parity of the seed id** (even / odd).

Covariate half X (even seeds), response half Y (odd seeds), "direction A":
1. Rule-level covariates from half X: `A_i = mean_s ln A`, `K_i = mean_s lnkappa` (rule means over that half's seeds).
2. Kappa residual: OLS of K on A across the 44 rules -> `r_i = K_i - (a + b A_i)`. Then z-score: `zA = (A - mean)/sd`,
   `zr = (r - mean)/sd` over rules (mean/sd from this half).
3. Random-intercept model on half Y window rows (one row per rule x seed x k in Y):
   `ln_ratio_is = b0 + bA zA_i + br zr_i + u_i + e_is`, `u_i ~ N(0, s_u^2)` per rule, `e_is ~ N(0, s_e^2)`.
   Fitted by REML (own implementation: profile likelihood over lambda = s_u^2 / s_e^2, closed-form GLS for the fixed
   effects; `scripts/mixed.py`). Pooled model: same with rows from both k, a k indicator, covariates computed per k, one
   random intercept per rule.
4. Effect size: `br` (ln_ratio change per 1 SD of the kappa residual) and `Std := br / sd_rules(mean ln_ratio in Y)`.
   Also s_u^2, s_e^2, and the share of the between-rule variance of u removed by adding zr to the zA-only model.

Out-of-sample ("fit on one half, evaluate on the other"): coefficients and the transformation (a, b, means, sds) are
frozen from the fit above; applied to the covariates computed from the *odd* seeds, and compared with rule-mean ln_ratio of
the *even* seeds. `R2_oos(M) = 1 - sum_i (ybar_i - yhat_i)^2 / sum_i (ybar_i - mean ybar)^2` over the 44 rules, fixed part
only (no BLUP). M0 = [1, zA], M1 = [1, zA, zr] (each fitted on its own); `dR2 = R2_oos(M1) - R2_oos(M0)`.
"Direction B" swaps the roles of the halves (sensitivity; reported, not tuned).

Uncertainty: (i) **rule-cluster bootstrap with a fresh random balanced seed split in every replicate** (B = 1000, seed
20261016; rules resampled with replacement and treated as distinct groups; within each resampled rule the seeds are randomly
permuted and split floor/ceil in halves), which carries both rule sampling and between-seed assignment variance;
(ii) a separate spread over R = 500 random balanced splits at the full 44 rules (mean, sd of `br`, fraction negative) as the
between-seed-split sd. Intervals are 2.5 / 97.5 percentiles.

Negative controls: (a) permutation of `zr` across rules holding zA and y fixed (1000 permutations, seed 20261016): two-sided
p of `|br|`; (b) whole-pipeline label shuffle: ln_ratio rows permuted as whole rule blocks across rules (200 shuffles) and the
bootstrap-CI-excludes-0 rate recorded.

Instrument calibration (`scripts/calibrate.py`, synthetic, known answer, before the real fit is interpreted): 44 rules,
3-4 seeds per half, s_e = 0.13, s_u = 0.30, true br in {-0.5, 0}, bA = 0.3; 300 simulated datasets (seed 20261016).
Also a measurement-noise variant (latent residual observed with noise sd 0.089/sqrt(4) and a matched ln A noise) to report the
attenuation of `br`.

## Predictions (fixed now)

Rationale: parent M3 gave partial Spearman -0.56 (k=22), -0.70 (k=25) on rule means, but with shared trajectories; the
parity-split N3 pair fraction was 0.79/0.81 against 0.82/0.76 un-split, so most of the signal should survive decoupling,
attenuated by the noise in 3-4-seed half means.

- **C (calibration, gate for everything else).** On synthetic data: bias of `br` within 10% of truth (true -0.5, noise-free
  covariates); bootstrap-CI coverage in [0.90, 0.99]; rejection rate at true br = 0 in [0.02, 0.10]; REML s_u, s_e within
  15% of truth on average. Whole-pipeline label shuffle on real data: CI excludes 0 in <= 10% of the 200 shuffles. If C fails,
  fix the instrument or declare the real fit uninterpretable; do not report it as evidence.
- **P1 (sign and size, direction A, per k).** `br < 0` and `Std <= -0.30` at both k = 22 and k = 25, with the bootstrap 95%
  interval excluding 0 at both.
- **P2 (out of sample).** `dR2 >= +0.05` at both k, and >= 90% of bootstrap replicates have `dR2 > 0`.
- **P3 (permutation).** Permutation p <= 0.01 at both k.
- **P4 (pooled over k).** Pooled `br < 0` with interval excluding 0 and `Std <= -0.30`.
- **P5 (direction B).** Same sign as P1 at both k (sensitivity).
- Expected magnitude: `Std` between -0.4 and -0.7 (attenuated relative to the full-seed rank correlations). A `Std` weaker than
  -0.30 counts as a failed prediction even if the interval excludes 0.

## Decision rules

- C, P1, P2, P3 all hold: the kappa residual at fixed ln A is a rule-level predictor of the excursion cutoff ratio that
  survives seed-decoupling and out-of-sample evaluation; a transplant intervention (T2) on kappa-contrasting rules at matched
  area is then justified (still observational until then).
- P1 holds, P2 fails: association is in-sample only (does not generalise to the other seed half); no T2.
- P1 fails at either k: the matched-pair pattern is not a rule-level association once trajectories are decoupled; the
  kappa-cutoff hint from T1b is closed as a size/coupling effect.
- Observational only; no causal claim follows from any outcome. A k = 22 vs 25 disagreement is reported as such.

## Commands

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-kappa-cutoff-mixed-effects/scripts/calibrate.py   # -> results/calibration.txt
uv run experiments/archive/2026-10-kappa-cutoff-mixed-effects/scripts/fit.py         # -> results/fit.txt, results/fit.json
```

## Status

Closed 2026-10-16: **registered hypothesis FAILED** (P1, P2, P3, P4 failed; calibration gate C held; P5 held). No T2 on this basis.
`notebook.ipynb` executed from a clean kernel under uv and agrees with this README.

## Results (2026-10-16; predictions above unchanged; base commit `997c9b2`, dirty tree; `posthoc.py` ran at `269288e`)

Commands as above plus `uv run .../scripts/posthoc.py` (exploratory, unregistered) -> `results/{calibration.txt,fit.txt,fit.json,posthoc.txt}`.
Input sha256[:16] `e813c6f21f63421c`, 1399 windows, 44 rules, 6-8 seeds per rule. Seed 20261016 throughout. REML costs ~4 ms per fit;
`calibrate.py` and `fit.py` each took roughly 15-30 min.

**C (calibration gate): held.** Noise-free covariates, true br = -0.5: mean estimate -0.489 (ratio 0.977), s_u 0.297 / s_e 0.130
(truth 0.30 / 0.13), bootstrap CI coverage 0.903 (edge of the [0.90, 0.99] band). Null (br = 0): rejection 0.077, estimate 0.000.
Whole-pipeline label shuffle on the real data: CI excludes 0 in 0.075 (k=22) and 0.045 (k=25) of 200 shuffles (bootstrap B=200
there). Noisy-covariate variant (seed sd 0.089 on ln kappa, 0.10 on ln A, 3-4 seeds per half): br attenuated to 0.895 of truth and
the CI covers the unattenuated truth only 0.787 of the time; not a gate, but it means real-data Std is a mild underestimate of a
latent effect under that noise model. The calibration is Gaussian and homoscedastic, which the real data are not (see below).

**Real data, direction A (kappa and ln A from even seeds, ln_ratio from odd seeds), registered fit:**

| | k=22 | k=25 | registered |
|---|---|---|---|
| br (ln_ratio per SD of kappa residual) | -0.415, boot95 [-0.662, -0.135] | -0.570, [-1.447, -0.200] | < 0, CI excludes 0 |
| Std = br / sd(rule-mean ln_ratio) | **-0.275** [-0.436, -0.091] | **-0.194** [-0.482, -0.072] | <= -0.30 |
| between-split sd of br (R=500 random halves) | 0.075 | 0.161 | reported |
| dR2_oos (frozen transform, other half) | +0.118 (boot95 [-0.101, +0.155]) | +0.073 ([-0.085, +0.208]) | >= +0.05 |
| bootstrap fraction dR2 > 0 | 0.875 | 0.866 | >= 0.90 |
| permutation p (zr across rules, 1000) | 0.020 | 0.096 | <= 0.01 |
| share of s_u^2 removed by zr | 0.147 | 0.052 | reported |
| direction B Std | -0.374 | -0.313 | same sign |

Pooled over k (k indicator, one rule intercept): br = -0.014, Std = -0.006, boot95 [-0.890, 0.287]. The pooled slope is ~0 although
both per-k slopes are negative; I did not diagnose this (the calibration covered single-k fits only, so a pooled-fit bug is not excluded).

Verdicts: **P1 FAILED** (sign and interval held, but Std -0.275 and -0.194 are weaker than the registered -0.30; the expected range
was -0.4 to -0.7). **P2 FAILED** (dR2 point estimates pass, the 0.90 bootstrap criterion does not). **P3 FAILED** (p = 0.02 and 0.096
vs 0.01). **P4 FAILED.** P5 held. Per the decision rule ("P1 fails at either k"), the matched-pair pattern is not established as a
rule-level association once trajectories are decoupled.

Reading (interpretation). The sign is negative in every analysis (all bootstrap and split fractions, both directions, both k) but the
effect is weaker than predicted, imprecise at k=25 and not stable under permutation there; the matched-pair 76-82% overstated the
rule-level association. Between-seed uncertainty is large: split sd of br 0.075 / 0.161 on top of rule sampling. **Misspecification is
probably the main caveat:** ln_ratio is heavy-tailed. The median within-rule seed sd of ln_ratio is 0.13, but its 90th percentile is
1.8-2.4 (max about 3.7) and ln_ratio reaches -7; REML s_e is 1.06 (k=22) and 1.39 (k=25), i.e. a minority of bursty/censored rules
dominates a homoscedastic Gaussian likelihood.

**Post hoc, exploratory, not registered, cannot rescue the verdict** (`results/posthoc.txt`, commit `269288e`): (i) dropping rules
whose all-seed ln_ratio sd > 0.5 (27 rules at k=22, 29 at k=25; a cut on response dispersion, not on its mean): Std -0.428
[-0.673, -0.188] / -0.392 [-0.587, -0.221], dR2 +0.254 / +0.173, bootstrap fraction > 0 of 0.996 / 1.000, permutation p 0.007 / 0.001,
so every registered threshold would be met on that subset. (ii) Normal-score ranks of ln_ratio, all 44 rules: Std -0.265 / -0.197,
p 0.020 / 0.054, still below threshold. The association looks cleaner among rules with stable cutoffs, but this is a 60% subset chosen
after seeing the failure on the same data; it needs a pre-registered replication (e.g. the k = 23, 24 windows in the same file) before
being called a finding.

Not resolved: why pooled br ~ 0; whether a heteroscedastic or robust model changes the all-rule answer; the sign/size of the ln A slope
differing between k (bA -1.0 vs -2.0 per SD); how much attenuation 3-4-seed half means cause on real data (about 10% under the synthetic
noise settings). Not used: windows k = 23, 24 in the input file (registered k = 22, 25 only).
