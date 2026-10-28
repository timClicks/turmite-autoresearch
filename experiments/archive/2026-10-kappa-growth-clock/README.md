# Does the leading run predict boundary occupation beyond the growth clock?

Registered 2026-10-16 21:14 +13:00, base c9811f56911ff4e7fd8cfe5e76cd5d461968265b,
dirty shared workspace. No measurements of this cohort have been made.

## Question and design

The fresh-leading-run study found a positive lead coefficient after controlling
early area, but early area is a post-treatment variable and the mutation response
is asymmetric. Does the association survive replacing early area with area at the
actual measurement window? This is a descriptive growth-history audit, not a
causal adjustment or a new explanation for kappa.

Generate 16 independent nine-letter suffixes using numpy default_rng(2026101607).
Each family contains four 14-letter rules `R^k L R^(4-k) SUFFIX`, k=1..4. Thus
length, total R count and all letters at indices >=5 are identical within family.
Exclude any family containing a rule in the earlier fresh or mutant manifests.
Four fresh patch seeds 202610160701..202610160704; probe 24 4096 (2^24 steps).
These are fresh rules and starts; neither stationarity nor growth exponent is
used to select the cohort. Moving the first L also changes its index: this design
does not distinguish lead length from the position of that letter.

Primary window k=23, secondary k=21,22. Early area is end-of-window A18.
For each rule, average logs across seeds that complete the target and early
windows with B>0. Require >=3/4 seeds per rule. Report all escapes and exclusions.
Primary gate: >=12 complete families, all four rules qualifying. Fit only those
complete families; report selection by lead. Gate failure makes scientific
predictions uninformative. Report between-seed sd alongside means.

## Predictions fixed before measurement

Thresholds are design choices. Primary P1: in OLS ln kappa ~ spline(ln A23)+lead,
the lead coefficient is positive with 95% family-bootstrap interval above zero
and at least half its coefficient in ln kappa ~ spline(ln A18)+lead. Splines are
linear hinges at 25/50/75% training quantiles, with a linear term and intercept.
If the early coefficient is <=0, the expected effect has not replicated and P1 fails.

P2: adding lead to the current-area spline improves leave-one-family-out R2
by >=0.05, with lower 95% family-bootstrap interval above zero. R2 denominator
is squared deviation from each fold's training mean. Knots are fit in each fold.
Bootstrap 2000 draws, seed 2026101608; gain intervals resample out-of-fold loss
contributions by family (uncertainty conditional on fitted folds).

Specificity/accounting, descriptive only: decompose the lead coefficient using
ln kappa = ln(B/S) - ln(P/A), with exactly the same design matrix. Report current
area + early area (linear) sensitivity, and all three windows. Never call this
decomposition independent prediction. No intervention is justified by this audit.

## Controls and reproducibility

Before ant analysis, calibrate coefficient recovery and zero added signal on
synthetic responses in the exact spline model; verify the decomposition identity.
There is no growth-exponent estimator in this experiment, so rotor/random-walk
exponent calibration is not used. Run release tests. Spot-check four first-family
specs on CPU against GPU, byte for byte, before the main GPU batch; GPU lanes=256,
pool=4 GB, grid=4096. Record source/input hashes, exact commands and dirty state.
Batch checkpoint `.done` is accepted only when recipe hashes match. Completed
CSV windows are published under results; bulk CSV stays in dumps. No existing
results are overwritten. All scripts run from the repo root under uv in WSL.

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-kappa-growth-clock/scripts/sample.py
bash experiments/archive/2026-10-kappa-growth-clock/scripts/run.sh
uv run experiments/archive/2026-10-kappa-growth-clock/scripts/analyse.py
uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-kappa-growth-clock/notebook.ipynb
```

Related: `../2026-10-kappa-leadrun-fresh/README.md`,
`../../../notes/kappa-mechanisms-2026-10-15.md`. No literature claim is being made.

## Results

**UNINFORMATIVE: support gate failed.** All three windows retain only 7/16
complete families versus the required 12. P1/P2 were not fitted or scored.
There are 212 usable starts of 256 in each window; 40 miss A18 and four more
miss the target. Overall 45 starts eventually escape, including one after a
complete target window. No zero-boundary exclusions occur. Qualifying rules
(>=3 starts) by lead 1/2/3/4: 16/9/15/13 out of 16 each. This is differential
retention, not evidence for or against the lead effect.

Do not lower the gate or interpret a survivor-only fit as confirmation. A larger
board could diagnose censoring, but this run does not identify highways or other
growth regimes; no detector was run. Any follow-up must retain this cohort,
preserve its failures and register its cap/grid before measurement.

Recipe: commands above, base c9811f5 (dirty source hashes in
`results/run-sources.sha256`; frozen protocol in `results/registration.md`).
`results/seed_status.csv` lists every exclusion; `rule_means_k*.csv` includes all
64 rules, with n=0 for absent usable starts. `results/windows.csv` publishes
k=18..23; `analysis.json` records hashes, counts and estimator calibration.
Seeds and parameters remain as registered. No effect uncertainty is reported
because the gate stopped fitting; per-rule between-seed sd(log kappa) is in the
CSV summaries where available.

All release tests passed, GPU probe tests 5/5 passed, and four CPU/GPU 2^24
trajectories are byte-identical. Synthetic planted slope 0.20 is recovered to
roundoff; with correlated lead/area and family noise, 200 synthetic repeats have
mean bias +0.000212 for both null and planted 0.15 slopes. The known area-only
cross-validation gain is 0.0000231. These calibrate the instrument, not the ants.
GPU batch: lanes=256, pool=4 GiB, grid=4096, 15.66 seconds, no requeues (descriptive
timing, no CPU speed benchmark). The notebook is executed separately.

The **full 256-spec CPU replay is byte-identical** to the frozen GPU output
(`results/cpu-replay-check.txt`). This also supplies a reproduction path without
the GPU port, which was uncommitted shared work when this investigation ran:
`bash experiments/archive/2026-10-kappa-growth-clock/scripts/replay_cpu.sh`.
If the GPU dump is absent, copy `dumps/cpu-replay.csv` to `dumps/probe.csv`
inside this experiment before running analyse.py. The replay verifies the frozen
digest before reporting success. `scripts/check_replay.py` verifies seven
published analysis files byte for byte; batch resume verifies its recipe/digest.
