# kappa-matched-area: does rule-specific kappa survive controlling for territory size?

Registered 2026-10-14 22:25 NZDT, base commit `797704a` (dirty tree), before
`scripts/matched_area.py` was run. **No new simulation:** this reuses the committed T1/T1b
patched-start windows of `2026-10-t1-excursion-tomography` (`results/t1b_cutoff_seeds.csv`;
k = 22 and 25, 44 rules, 6-8 seeds each, escaped windows excluded as there).

## Question

T1/T1b found every strong excursion statistic collapsed to "inverse territory size", because at
fixed t, kappa and A are tied through dA/dt = c kappa P/A. The one hint, rule-mean
ln(L_99.9/R_eq) against rule-mean ln kappa (Spearman -0.835 at k=22, -0.918 at k=25), is
size-contaminated. Is there rule-specific kappa left once area is held fixed, and does the cutoff
association survive?

## Quantities and estimators (fixed now)

Unit = window (rule, seed, k). ln A = ln `area` at window end, ln kappa as in the files.
- M1: pooled OLS ln kappa ~ ln A (all windows, both k); then a one-way ANOVA intraclass
  correlation (unbalanced-n correction) of the residual by rule, plus the same ICC for ln kappa
  without the area adjustment.
- M2: between-rule slope (regress rule-means) and within-rule slope (rule-demeaned) of
  ln kappa on ln A, with rule-bootstrap 95% intervals (seed 20261014, 500 resamples).
- M3: partial Spearman of rule-mean ln(L_99.9/R_eq) and rule-mean ln kappa given rule-mean ln A,
  separately for k = 22 and k = 25 (rank-residual method), with a rule-bootstrap interval
  (2000 resamples). The open-time-share <= 0.10 subset is the censoring sensitivity.

## Predictions (fixed now)

1. **M1.** The rule ICC of the area-adjusted residual is >= 0.40 at the window level (the earlier
   fixed-t kappa ICC was 0.58; area is allowed to absorb at most about a third of the rule
   signal). If < 0.25, rule dependence of kappa at fixed A is essentially nil.
2. **M2.** The within-rule slope exceeds the between-rule slope by >= 0.3 (within a rule, A rises
   with t while kappa is flat in time, so its slope is near 0; across rules at fixed t the
   slope should be clearly negative). If the two agree within 0.15, area is the sole carrier of
   the between-rule differences.
3. **M3.** The partial Spearman of ln(L_99.9/R_eq) with ln kappa given ln A is negative with
   |partial rho| >= 0.30 at both k = 22 and 25, and its bootstrap interval excludes 0 at both.
   Otherwise the excursion-cutoff hint is declared a size effect.

## Decision rules

- 1 and 3 hold: rule-specific kappa at fixed area exists and tracks the extreme-excursion scale;
  next step is a transplant intervention (T2) with exact quantiles and matched-area pairs.
- 1 holds, 3 fails: kappa has a rule-specific part that is not the excursion cutoff; the T1 route
  is closed and the next test needs a different observable (e.g. colour flux through the edge,
  `examples/kappa_rs_colourflux.rs`).
- 1 fails: kappa at matched area is not a rule property; the paper's ICC 0.58 should be
  qualified as "at fixed t".
- Observational only; no causal claim follows from any outcome.

## Command

```bash
uv run experiments/archive/2026-10-kappa-matched-area/scripts/matched_area.py
```

Output: `results/matched_area.txt` (commit, input hash, numbers). `notebook.ipynb` is the template
stub until results exist.

## Status

Closed 2026-10-15: three registered analyses run (matched_area, matched_pairs, noise_floor); outcome unresolved-to-weak, no T2 on this pair set. Open: rule-level regression (unregistered, not run). `notebook.ipynb` executed from a clean kernel and agrees with this README.

## Results (2026-10-14 22:35 NZDT; predictions above unchanged)

`uv run experiments/archive/2026-10-kappa-matched-area/scripts/matched_area.py` -> `results/matched_area.txt`
(commit `797704a`, dirty tree; input sha256[:16] `e813c6f21f63421c`; 1399 windows, 44 rules).

1. **M1: FAILED as registered, not into the "nil" band.** Pooled ICC of the area-adjusted residual
   is 0.286 (needed >= 0.40; "essentially nil" was < 0.25). Raw ln kappa ICC 0.674.
   Post hoc, by window: adjusted ICC 0.561 (k=22) and 0.467 (k=25). These are not the registered
   estimator and are not used to rescue M1; the pooled slope mixes the between- and within-rule
   slopes below, which is what lowers the pooled value.
2. **M2: FAILED, and my sign assumption was wrong.** Slopes of ln kappa on ln A are *positive*:
   between rules 1.271 [1.107, 1.403], within rules 0.420 [0.152, 0.652] (500 rule-bootstrap
   resamples). Registered: within - between >= 0.3; observed -0.851. I had assumed kappa falls
   with area across rules; the opposite holds at fixed t in this sample. Area is not the sole
   carrier (the two slopes differ), but the registered picture of the confound was wrong.
3. **M3: HELD.** Partial Spearman of ln(L_99.9/R_eq) with ln kappa given ln A: -0.560
   [-0.743, -0.333] at k=22, -0.695 [-0.827, -0.526] at k=25; with open share <= 0.10:
   -0.551 and -0.693. |rho| >= 0.30 with intervals excluding 0 at both windows.

Reading (interpretation, not observation). Decision rules: 1 failed outright by its own
threshold, 3 held, so the registered branches conflict; the result is **unresolved**, not
"kappa has a rule-specific part at fixed area". What survives is that the cutoff/radius
association is not removed by a linear-in-ln A adjustment (M3), which is stronger than I
expected. Caveats: the ICC treats windows of one seed as exchangeable; ln A adjustment is
linear and is not matched-area pairs; the cutoff is a log-linear within-octave quantile with
censoring; rule means share seeds across k; 44 rules; M2's sign error means the T1 narrative
"inverse territory size" needs re-reading before the next design. Next: matched-area *pairs*
(rules within 5% in A at a fixed k, difference in ln kappa against difference in ln cutoff/R),
registered first, then a transplant intervention only if that holds.

### Matched-pairs results (2026-10-15 19:45 NZDT; predictions above unchanged)

`uv run experiments/archive/2026-10-kappa-matched-area/scripts/matched_pairs.py` -> `results/matched_pairs.txt`
(base commit `7eff085`, dirty tree; input sha256[:16] `e813c6f21f63421c`; 44 rules per k).

- **P-c held:** 62 (k=22) and 67 (k=25) matched pairs at tolerance 0.05.
- **P-a FAILED:** median |d ln kappa| in matched pairs is 0.142 vs 0.593 for all pairs (ratio 0.24) at k=22 and
  0.127 vs 0.658 (0.19) at k=25. Both are in the registered "< 0.25 -> kappa determined by area at fixed t"
  band (k=22 only just). Sensitivity at tol 0.10 gives 0.25 and 0.20: same conclusion.
- **P-b HELD:** in 82% (k=22, cluster-boot95 [0.64, 0.96]) and 76% (k=25, [0.55, 0.94]) of matched pairs the
  higher-kappa rule has the smaller ln(L_99.9/R_eq). Tol 0.10: 76%/77%, intervals exclude 0.5.

Reading (interpretation). The branches conflict again, now in a different way: most of kappa's rule
variation at fixed t is carried by area, yet the small residual kappa difference still orders the cutoff
in about 4 of 5 pairs. Per the registered decision rule P-a failing means the paper's rule-ICC for kappa
should be qualified as "at fixed t". Not tested: the matched-pair |d ln kappa| of ~0.13 is not compared
with the seed-to-seed noise (median between-seed ln-kappa sd is not computed here), so a residual of that
size may be mostly noise; if so P-b's 76-82% would be surprising and worth a closer look, but a residual
that small is also what a transplant (T2) would struggle to detect. Next: compute the seed-noise floor for
ln kappa and ln ratio, and restrict P-b to pairs with |d ln kappa| above it, before designing T2. Observational only.

## Seed-noise floor (registered 2026-10-15 20:10 NZDT, base commit `da88e61`, before `scripts/noise_floor.py` was run)

No new simulation; same input as above (`t1b_cutoff_seeds.csv`, escaped windows excluded), same matched pairs
(tol 0.05 registered, 0.10 sensitivity), rule means over seeds as before. Bootstrap seed 20261016.

Quantities: s_i = between-seed sd of ln kappa (and ln_ratio) within rule i at fixed k; SE of a pair difference
= sqrt(s_i^2/n_i + s_j^2/n_j); z = |d ln kappa| / SE.
- N1: median within-rule seed sd and median pair SE(d ln kappa); fraction of matched pairs with z > 2.
- N2: P-b (higher-kappa rule has smaller ln_ratio) restricted to pairs with z > 2, cluster bootstrap by rule.
- N3 (shared-seed coupling control): split each rule's seeds by parity; kappa and area-free matching from the
  full-seed ln A as before, but kappa from even seeds and ln_ratio from odd seeds, so no trajectory contributes to
  both sides of a pair comparison. Fraction of pairs where the even-seed higher-kappa rule has smaller odd-seed ln_ratio.
  Rules with < 2 seeds in either half are dropped (count reported).

Predictions (fixed now):
1. N1: median seed sd of ln kappa <= 0.10, median pair SE <= 0.05, and >= 60% of matched pairs at z > 2 (so the
   median matched |d ln kappa| of ~0.13 is mostly signal). If < 40% of pairs reach z > 2, the residual is mostly noise.
2. N2: restricted fraction >= 0.75 at both k with bootstrap interval excluding 0.5 (if the z > 2 pairs are fewer
   than 20 per k, report but do not judge).
3. N3: split-seed fraction >= 0.65 at both k. If <= 0.58 (or interval contains 0.5) at either k, the P-b result is
   attributed to within-seed coupling of kappa and ln_ratio, not a rule-level association.

Decision: 1-3 hold -> the residual is rule-level and orders the cutoff; design T2 on matched pairs with z > 2. N1 fails
-> P-b is uninformative at this noise level, no T2. N3 fails alone -> P-b is a within-trajectory identity, not a rule
property. Observational only.

### Seed-noise floor: result (2026-10-15, commit `da88e61`)

Command: `uv run experiments/archive/2026-10-kappa-matched-area/scripts/noise_floor.py` -> `results/noise_floor.txt`
(regenerated byte-identically on rerun). 44 rules per k, 6-8 seeds per rule, tol 0.05 (registered; 0.10 in the file).

| | k=22 | k=25 | registered | verdict |
|---|---|---|---|---|
| N1 median seed sd ln kappa | 0.089 | 0.089 | <= 0.10 | held |
| N1 median pair SE | 0.043 | 0.037 | <= 0.05 | held |
| N1 frac pairs z > 2 | 0.387 (24/62) | 0.582 (39/67) | >= 0.60 | **failed** at both k; k=22 is below the 0.40 "mostly noise" line |
| N2 P-b on z > 2 pairs | 0.917 [0.50, 1.00] (24 pairs) | 0.949 [0.78, 1.00] (39 pairs) | >= 0.75 and interval excludes 0.5 | k=22 **failed** (interval contains 0.5); k=25 held |
| N3 split-seed P-b | 0.790 [0.59, 0.95] | 0.806 [0.61, 0.95] | >= 0.65, interval excludes 0.5 | held at both k |

Sensitivity (tol 0.10) tells the same story: z > 2 fractions 0.43/0.59, N2 0.87 [0.61, 1.00] / 0.90 [0.75, 1.00], N3 0.72 [0.55, 0.88] / 0.77 [0.59, 0.91].

Reading against the pre-registered decision rule: N1 failed, so by the letter of the rule P-b is "uninformative at this noise level, no T2 on this
matched set". Two things cut the other way and are reported rather than used to rewrite the rule. (i) N3, the control aimed at
within-seed coupling, held clearly, so the association is not an artefact of kappa and ln_ratio sharing trajectories. (ii) Among
pairs that do clear the noise floor P-b is high (0.92/0.95), and at k=22 the complement (z <= 2) is still 0.76, whereas at k=25 the
complement is 0.50, i.e. at k=25 the association sits entirely in the resolved pairs, which is what a real signal diluted by noise
would look like, and is not what pure noise would look like (it would be 0.5 everywhere). Caveats: z uses seed sd of ln kappa only and treats rule sd as
known; pairs are matched on noisy mean ln A (selection on A noise can leak into kappa through Eq. 1); pairs share rules, so pair counts overstate
independent information (the bootstrap is by rule, but the k=22 interval is wide); the z > 2 cut is a post-selection on |d ln kappa|, so a high P-b there
is partly guaranteed to be easier to see, not independent evidence. Open: a rule-level (not pair-level) test, e.g. regress
ln_ratio on odd-seed kappa residual given A with rule random effects, would use all 44 rules without matching.

## Correction 2026-10-28 (append only): bootstrap intervals were not reproducible

`scripts/matched_area.py` drew its seeded bootstrap (`default_rng(20261014)`) over rules taken from polars
`unique()` / `group_by()`, whose order is per-process hash order, so every run gave different M2/M3 intervals.
Fixed at `4fd558b` (rules and per-rule tables sorted); three runs are byte-identical. Regenerated
`results/matched_area.txt` (`d60e0f4`): M2 between 1.271 [1.090, 1.395] (above: [1.107, 1.403]), within 0.420
[0.159, 0.645] ([0.152, 0.652]); M3 all seeds -0.560 [-0.742, -0.338] at k=22, -0.695 [-0.827, -0.508] at k=25;
open share <= 0.10: [-0.752, -0.312], [-0.823, -0.512]. Point estimates and every M1-M3 verdict are unchanged.
`matched_pairs.py` and `noise_floor.py` were checked the same way and are already deterministic. Run with
`uv run --frozen python scripts/matched_area.py` (`uv run --frozen` on the PEP 723 script now needs a script lockfile).
`notebook.ipynb` re-executed against the regenerated file.
