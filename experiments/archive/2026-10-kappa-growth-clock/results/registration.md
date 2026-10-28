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

Pending. Predictions above remain fixed.
