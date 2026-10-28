# kappa leading-run test on fresh, lead-stratified rules

Registered 2026-10-16 (+13:00), base commit `d4fd349`, **before any probe run on these rules**.
Follow-up to `../2026-10-kappa-prefix-decode` (post hoc finding: on the 162 stationary
pool rules, the number of identical opening letters ("leading run" `lead`) gives +0.33
held-out R^2 over a ln A(22) spline, beating the prefix-8 lookup's +0.20; residual rises
~+0.1 per step, same slope in census and pool).

## Question

Is the leading-run effect on ln kappa real and out-of-sample, at fixed area? The decode
result was found on data already scored, and `lead` correlates -0.56 with ln A(22).

## Design

300 fresh rules, lengths 13/14, stratified on `lead` = 1..6 (25 rules per lead x length cell,
`R^lead L` + uniform random tail; `scripts/sample.py`, numpy default_rng(20261016 + 1)). Excludes every
W3b/W3c rule (census is length <= 12). Eight patched seeds 601..608 each = 2400 runs,
`probe 27 8192`, same instrument and `per_rule` pipeline as W3c (core band
alpha_w in [0.25, 0.42], kappa > 0, >= 6 core-band runs, stationary = |g_k| < 0.05).
Stratification de-correlates `lead` from rule composition; lead-1 would be 50% of an
unstratified sample, lead >= 4 about 12%.

Model (fixed now): trained **only on the 2183 stationary census rules**, as in decode:
ln kappa = spline(ln A(22)) [knots at 10/25/50/75/90% quantiles, as `prefix_audit.basis`]
+ b * min(lead, 6). Evaluated on the fresh stationary rules. gain = held-out R^2 gain of the
lead term over the spline-only model, strict against the census training mean, bootstrap
over fresh rules (2000, seed 20261016).

## Predictions (thresholds are my design choices)

- **L1** gain >= 0.15 and 95% CI lower bound > 0 (decode's post hoc +0.33 is optimistic; expect shrinkage). ~65%.
- **L2** the census-fitted slope b lies within 0.07-0.13 per step, and the slope refit on fresh
  rules (same spline + lead, OLS) has CI containing b_census and excluding 0. ~60%.
- **L3** (confound check) split fresh rules into ln A(22) tertiles; the within-tertile
  slope of the residual on lead is > 0 in all three and the pooled within-tertile estimate has CI above 0. ~70%.
- **L4** (control) lead shuffled across fresh rules (200 permutations): median gain within +-0.02,
  95th pct <= +0.05.
- **L5** stationarity and core-band retention do not depend on lead: share of rules kept
  differs by < 0.20 between lead 1 and lead 6 strata. If violated, selection biases L1-L3; report only.
- **L6** (descriptive, no threshold) compare `lead` against R-count-in-first-8 and letter-2
  alone (decode's ablations) as fresh-sample gains.

A failure of L1 and L3 together means the decode finding was an area/composition proxy
that did not survive fresh data.

## Commands (WSL, repo root)

```bash
uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/sample.py      # already run, results/rules.txt, specs.txt
bash experiments/archive/2026-10-kappa-leadrun-fresh/run.sh                   # ~22 min, dumps/probe.csv (gitignored)
uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/analyse.py     # results/analysis.txt, analysis.json
```

## Results

Run 2026-10-16 ~20:15, commit 58b4f38 (dirty tree), seed 20261016, 2000 bootstraps; `results/analysis.txt`, `analysis.json`.
2400 runs, 365 runs escaped the board, 183/300 rules kept (>= 6 core-band runs), 176 stationary (test set). Per lead: 34/32/34/31/26/19.

| pred | outcome |
|---|---|
| L1 gain >= 0.15, CI > 0 | **HELD**: +0.651 [0.498, 0.828] (decode's post hoc +0.33 was not optimistic; here the spline-only baseline is weak, R^2 0.124, because stratifying on lead puts many large-lead rules in the test set; corr(lead, ln A22) = -0.72) |
| L2 census slope in 0.07-0.13 and fresh refit CI covers it | **FAILED as registered**: census slope is +0.195/step (my range was wrong: it came from the unconditioned residual table, not the spline-adjusted regression); fresh refit +0.152 [0.129, 0.174], excludes 0.195, so the slope shrinks ~22% out of sample but is clearly > 0 |
| L3 within-ln A tertile slopes > 0, pooled CI > 0 | **HELD**: tertile slopes 0.151 / 0.155 / 0.149, pooled +0.152 [0.128, 0.177] |
| L4 shuffled lead gain median within +-0.02, p95 <= 0.05 | **FAILED as registered**: median -1.43. The criterion was mis-specified: shuffling lead keeps the large census coefficient and injects variance, so gain is very negative, not ~0. It shows the lead term carries the signal; it is not the "pipeline gives ~0" control I intended. A proper null would refit the coefficient on shuffled lead (not done). |
| L5 retention differs < 0.20 (lead 1 vs 6) | **FAILED**: stationary share 0.68 (lead 1) falling monotonically to 0.38 (lead 6); kept share 0.74 -> 0.40. Selection depends on lead (mostly board escapes / too few core-band runs). L1-L3 hold on survivors only. |
| L6 alternatives | lead +0.651 [0.50, 0.83] vs letter-2-is-R +0.319 [0.25, 0.40] vs R-count-first-8 +0.290 [0.20, 0.39]: lead is better than both, CIs separate from the R-count at the top end only mildly |

Mean residual by lead (fresh, vs census spline-only): -0.148, +0.053, +0.127, +0.188, +0.377, +0.418 (census/pool table: -0.11 .. +0.45): same monotone shape.

**Conclusion.** The leading-run effect replicates on fresh, lead-stratified rules, and it holds at fixed area (L3), so it is not simply the ln A(22) proxy. Not established: causation (no mutation test), and survivor bias (L5 failed: high-lead rules escape or drop out more, so the 0.15-0.20 slope is for rules that stay on the board; selection could inflate or deflate it). Two registered predictions (L2 range, L4 control) were badly specified by me and are reported as failed, not repaired.

## Follow-up registered 2026-10-16 (+13:00), base commit 78bcafd, before running either part

Part A is analysis-only on data already scored, so it is NOT a blind prediction: the design below is fixed before I read
its output, but the probe data were seen. Part B needs new probe runs and is a genuine prediction.

### Part A: nulls and selection bounds (`scripts/followup.py`, no new runs)
- **A1 refit-on-shuffle null.** Permute `lead` among census training rules AND among fresh test rules, refit the
  coefficient, score the gain (200 permutations). A second version permutes within quintiles of ln A(22) (pooled
  census+fresh quantiles) so corr(lead, ln A) is preserved. Expect both medians near 0 (|median| <= 0.02), with the
  observed +0.651 beyond the 99th percentile. Replaces the failed L4.
- **A2 selection bounds.** Slope refit on the fresh stationary rules using (i) only leads 1-3 (retention highest),
  (ii) each rule length separately, (iii) inverse-retention weights by lead. Prediction: slope stays > 0 with CI excluding 0
  in all, and the leads 1-3 slope is within 0.05 of the all-lead slope (0.152). Also tabulate who drops out (escaped runs per lead and length).
- Exports `results/fresh_rules.csv` (one row per sampled rule) so the notebook reads committed data only.

### Part B: mutation dose-response (`scripts/mutants.py`, `run_mutants.sh`)
For each fresh stationary rule with lead k = 1..5, single-letter mutants (same seeds 601..608, `probe 27 8192`, same pipeline):
- arm **E** (extend lead): flip index k (L->R), so the lead grows by >= 1;
- arm **S** (shorten lead): for k >= 2 flip index k-1 (R->L), lead becomes k-1;
- arm **C** (control): flip a random L->R at index >= 8, lead unchanged (same composition change as E, no lead change).
Paired difference d = ln kappa(mutant) - ln kappa(base) over pairs where both are kept and stationary (>= 6 core runs,
|g_k| < 0.05); dA = ln A22 difference. Bootstrap over pairs (2000, seed 20261016).
- **M1** arm E: mean d > 0 with 95% CI lower bound > 0, and the pooled paired regression d ~ b*dlead + c*dA has b > 0 with CI excluding 0 (~55%).
- **M2** E - C difference in mean d has CI lower bound > 0, i.e. the effect is the lead and not the L->R composition change (~60%).
- **M3** arm S: mean d < 0 with CI upper bound < 0 (~50%; W6 found early-letter effects at fixed area go both ways).
- **M4** (descriptive) pair retention (mutant kept and stationary, given base was) by arm.
Failure of M1 and M2 together would mean the lead association is not causal at the single-flip scale, i.e. a correlate of something else in the opening.

### Part A results (run 2026-10-16, commit 78bcafd + dirty tree, `results/followup.txt`, `followup.json`, `fresh_rules.csv`)
- **A1 HELD.** Refit-on-shuffle gain: unrestricted median -0.001 (p99 +0.038, max +0.049); within ln A quintile median +0.000 (p99 +0.051, max +0.058). Observed +0.651 is far outside both. The pipeline produces ~0 gain from a lead label with no information, including when the label keeps its correlation with area.
- **A2 slope stays positive everywhere but the "within 0.05" part FAILED.** Fresh refit slope: all leads +0.152 [0.130, 0.174]; leads 1-3 +0.235 [0.196, 0.271] (differs from all-lead by 0.083 > 0.05); leads 1-4 +0.197; length 13 +0.144, length 14 +0.157; inverse-retention weights +0.144 [0.123, 0.167]. So the effect is not carried by one length and is robust to reweighting by lead retention, but the slope depends on the lead range: it is steeper at small leads (consistent with saturation/cap at 6; mean residual by lead rises -0.15 -> +0.42, concave after lead 5). The single "slope per step" is therefore a coarse summary.
- **Dropouts.** Kept/stationary per 50 rules by lead 1..6: 37/34, 32/32, 35/34, 31/31, 28/26, 20/19. Rules with >= 1 escaped run: 3, 12, 7, 4, 9, 16. Escapes are not monotone in lead and explain only part of the drop for lead 1-5; most missing rules fail the >= 6 core-band runs condition (non-core alpha_w, e.g. highway/other-class runs), not stationarity (only 0-3 kept rules per stratum are non-stationary). Retention falls sharply only at lead 6 (0.40 kept). Lead >= 5 estimates carry the most selection risk; the lead 1-4 slope (+0.197) is the least selected.
- Not done: a bound on what dropped rules would have had; IPW only reweights by lead, not by unobserved reasons for dropout.

### Part B results (rerun 2026-10-18, commit fa73570; files `results/*.rerun-2026-10-18.*`. The original 2026-10-16 run, `results/mutants_probe.log`, `mutants_analysis.txt`, `mutant_pairs.csv`, gives the same numbers up to float ULPs; see NOTEBOOK 2026-10-19 merge entry)
The first launch (2026-10-16) died at 600/3336 runs. It was rerun from scratch with the same command and specs (NOTEBOOK, 2026-10-18 deviation).
The probe made 3336 runs and finished at 19:51 (`results/mutants_probe.log`). Its `git` field is empty because WSL git cannot resolve this
worktree's gitdir; the actual commit is fa73570. Probe code is unchanged since the base run at d4fd349 (the only additions are `gpu/` and `onset.rs`).
Instrument identity check (`scripts/check_overlap.py`, `results/overlap_check.txt`): the 30 mutants that are also base-sample rules
reproduce `fresh_rules.csv` exactly. n_runs, ln kappa, ln A22 and g_k all differ by 0.0, and 18/30 are kept in both runs. `analyse_mutants.py` was run once, unmodified, with no crash.

There are 417 mutants of 157 stationary fresh bases (lead 1-5): 269 kept, 257 kept and stationary pairs. CIs are from a bootstrap over pairs (2000 resamples, seed 20261016).

| arm | pairs | mean d = dln kappa | 95% CI | mean dln A22 | mean dlead |
|---|---|---|---|---|---|
| E (extend lead) | 81 | -0.062 | [-0.152, +0.025] | -0.292 [-0.380, -0.205] | +1.64 |
| S (shorten lead) | 73 | **-0.198** | [-0.290, -0.110] | +0.013 [-0.068, +0.089] | -1.00 |
| C (late L->R) | 103 | -0.006 | [-0.049, +0.037] | -0.000 [-0.037, +0.036] | 0 |

| pred | outcome |
|---|---|
| M1 E mean d > 0 (CI > 0) AND pooled b > 0 | **FAILED as registered.** The first part fails: E mean d is -0.062 [-0.152, +0.025]. The second part holds: pooled d ~ c0 + b dlead + c dA gives b = +0.158 [+0.139, +0.179], c = +1.037 [+0.957, +1.119], c0 = -0.023 |
| M2 E - C mean d CI > 0 | **FAILED.** -0.056 [-0.159, +0.040] |
| M3 S mean d < 0 (CI upper < 0) | **HELD.** -0.198 [-0.290, -0.110], with area unchanged (dA +0.013) |
| M4 retention (kept+stationary / mutants) | E 81/152 (0.53), S 73/113 (0.65), C 103/152 (0.68). E loses the most, consistent with L5 (longer leads drop out) |

Descriptive output (registered as such) for area-matched pairs with |dA| < 0.15: E n=26, mean d +0.193; S n=37, mean d -0.237.
Post hoc (`scripts/describe_mutants.py`, `results/mutants_describe.txt`, written after seeing the above): the area-adjusted residual
d - 1.037 dA averages +0.241 (E), -0.211 (S) and -0.005 (C). E's total effect falls as dlead grows: dlead 1 (n=41) gives +0.04 with dA -0.13;
dlead 2 (n=31) gives -0.13 with dA -0.40; dlead 3-4 (n=9) have dA from -0.46 to -0.74.

**Reading.** Shortening the lead by one letter lowers ln kappa by about 0.2 while area stays the same. This matches the
cross-sectional slope (0.15-0.24 per step) and is the cleanest causal evidence here. Extending the lead has no net effect on ln kappa:
the same flip also shrinks the pattern (dln A22 about -0.29), and ln kappa moves with ln A at slope about 1. Net of area, extension
raises ln kappa by about +0.24 per mutant (+0.16 per lead step), symmetric with S. So the lead effect is causal at fixed area, in both directions.
Its total effect is sign-mixed: on the extension side it is cancelled by an area loss that has no counterpart on the shortening side.
The E/S asymmetry in dA is unexplained.

**Caveats.**
1. kappa = B·A/P at k=26 contains A, so the c ≈ 1 area slope is partly definitional, and dA shares run noise with d. "At fixed
area" therefore means conditional on the measured ln A22, as in the registered census model, not a clean structural decomposition. dA is a
mediator, not a confounder, so b is a direct effect and E's mean d is the total effect.
2. The pooled-regression CI treats pairs as independent, but up to 3 pairs share a base (and its measurement error), so that CI is somewhat too narrow. The within-arm CIs have one pair per base.
3. Selection: only 53% of E mutants survive the core-band and stationarity filter, against 65-68% for S and C. If the dropped E mutants differ in kappa, E's mean d is biased in an unknown direction.
4. No arm isolates "early flip, lead unchanged". C flips late letters, so M2 controls composition, not position. W6 found early-letter effects of both signs at fixed area, so S could partly be an early-position effect rather than a lead effect.
5. The area-adjusted E/S symmetry is post hoc.

#### Addendum 2026-10-18 20:15 (+13:00): correction to the Reading above
The registration says: *"Failure of M1 and M2 together would mean the lead association is not causal at the single-flip scale."*
M1 and M2 both failed. **By the criterion fixed before the run, single-flip causality of the lead association is not established.**
The Reading paragraph above ("causal at fixed area, in both directions") overrode that criterion post hoc and is withdrawn as a conclusion.
Revision, labelled as such: the registered half of M1 (pooled area-adjusted b = +0.158 [+0.139, +0.179]) and M3 (S: -0.198 [-0.290, -0.110]
at unchanged area) both point the same way as the cross-sectional effect. In hindsight, the total-effect criterion for E could not separate
a lead effect from the area loss that comes with lengthening the lead. The +0.24 area-adjusted E residual is post hoc, and c ≈ 1 is partly definitional.
So the evidence *suggests* a direct (area-conditional) effect, and the registered test should be replaced by one designed for it. This is not a result.
Further caveat on M3: arm S has no composition control. C is a late L->R flip, while S is an early R->L flip, so S's -0.198 combines
"one fewer R" with "early position", and no arm tests either factor alone. M3 alone therefore does not establish causality either.

## Proposed next steps, written 2026-10-19 (PROPOSALS ONLY: not registered, nothing run)
Both follow from the Part B addendum. Neither fixes a threshold, a sample or a prediction; each must be registered
here (with predictions, analysis script and base commit) before any run. Choices marked **open** are undecided.

### Proposal 1: lead-preserving early flips (position and composition controls)
*Gap it addresses.* No arm flips an early letter without changing the lead (caveat 4), so M3's -0.198 mixes "one fewer
R", "early position" and "shorter lead". C controls composition only at late positions. W6 found early-letter effects of both
signs at fixed area, so an early-position effect could masquerade as a lead effect.
*Design sketch.* Mutate the base's letter at index k+1 or k+2, where k is the base's lead run length, so the flip lies just past the
run and the lead stays k. Flip both directions (L->R and R->L) so letter composition changes in both senses. Paired against the base,
same seeds, same `probe 27 8192` settings and survivor filter as Parts A/B.
*What it would discriminate.* If the lead is the active factor, lead-preserving early flips should shift ln kappa by about zero at
fixed ln A, with no net sign. If early position or composition drives it, they should shift ln kappa by a size comparable to S
(about 0.2 in magnitude), with sign depending on flip direction (W6 mixed signs).
*Statistic.* Area-adjusted effect (regression of d ln kappa on dA), as in the Part B addendum, with bootstrap over bases (not pairs) to
handle shared bases.
*Open.* Which bases (all 157, or lead strata with room past the run); how many flips per base; index k+1 vs k+2 as separate arms;
whether to add a composition-matched lead-extending control (the missing S counterpart); required effect size and the sample size
that resolves it; whether "unchanged" needs an equivalence margin and what it is.

### Proposal 2: bound the arm-E dropout bias
*Gap it addresses.* Only 53% of extend-lead mutants pass the core-band and stationarity filter (S 65%, C 68%); if the dropped ones
differ in kappa, E's mean d is biased in an unknown direction (caveat 3). L5 already showed lead-dependent attrition in Part A.
*Design sketch (no new runs).* From the existing `mutants.csv` / `mutant_pairs.csv`, classify why each E mutant dropped (escape,
alpha_w outside band, non-stationary, too few seeds), then report bounds on E's mean d instead of a point estimate: for example
inverse-probability weighting by base lead and rule length, and worst-case (Manski-style) bounds from imputing the dropped E mutants
at the observed extremes of the kept ones. Repeat for S and C so the comparison is like for like.
*What it would discriminate.* Whether the failed M1/M2 conclusion (E not distinguishable from 0 or from C) is robust to attrition, or
whether plausible dropout behaviour could flip it either way. A bound that includes both signs means M1/M2 are uninformative, not failed.
*Open.* Which imputation range is defensible; whether dropped-for-escape mutants are censored (they never reach the measurement
area) rather than missing; whether non-stationary mutants need a separate arm because the model for them differs. Any choice made
after looking at the dropped rules' kappa must be labelled post hoc.

*Outcome (2026-10-20, post hoc, unregistered; `scripts/dropout_bounds.py`, `results/dropout_bounds.txt`).* IPW by base lead x length
changes nothing (E -0.058 [-0.149, +0.024], S -0.198, C -0.002). Worst-case bounds (dropped imputed at kept 5th/95th pct): E
[-0.35, +0.19], S [-0.42, +0.02], C [-0.12, +0.08]. E's bound includes both signs, so M1/M2 are uninformative about E, not cleanly
failed; S's negative sign holds unless the dropped S mutants averaged about +0.36. Dropout reasons were not separable without the
gitignored dumps.

### Ordering
Proposal 2 costs no compute and could be registered and run first; its outcome tells us whether the E arm is worth repeating inside
Proposal 1. Proposal 1 needs a new probe run (about 30 min at Part B's scale) and a registered sample size.
