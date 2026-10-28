# Kappa-cutoff mixed-effects lab notebook

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-16 00:01 (+13:00) · 997c9b2 · intent
Session start. Do the open follow-up of kappa-matched-area (noise-floor section): rule-level random-intercept regression of ln_ratio on the kappa residual given ln A, all 44 rules, no matching, seed halves decoupled. Informs whether T2 (transplant on kappa-contrasting matched-area rules) is justified. Read parent README/NOTEBOOK/noise_floor.py/results first.

### 2026-10-16 00:10 (+13:00) · 997c9b2 · assumption
(1) Seeds are exchangeable replicates of a rule and the same seed id at k=22 and 25 are the same trajectory family, so a split by seed id keeps covariate and response halves independent. Untested; the parity vs random-split comparison is a partial check. (2) A linear ln kappa ~ ln A residual (fit across rules within a half) is an adequate "kappa given area". Untested; parent M2 said slopes differ between and within rules. (3) Rule bootstrap with duplicated rules as distinct groups is adequate for the interval on br; checked only by synthetic coverage. (4) ln_ratio = ln(L_99.9/R_eq) shares R_eq with area in construction, so part of any lnA effect on y is mechanical; zA is in the model for that reason. Status of all: untested.

### 2026-10-16 00:10 (+13:00) · 997c9b2 · decision
Registered model, predictions (C, P1-P5), pass/fail and decision rules in README.md before any fit. Implement REML myself (scripts/mixed.py), not statsmodels: the model is a single random intercept with rule-level covariates, so own code is small and testable on synthetic data; no new dependency.

### 2026-10-16 00:30 (+13:00) · 997c9b2 · intent
Launched scripts/calibrate.py (300 synthetic datasets x bootstrap B=200 per scenario) and, in parallel, scripts/fit.py. Per-fit cost is ~4 ms so both take tens of minutes. The real fit is not to be interpreted unless calibration criterion C holds.

### 2026-10-16 00:45 (+13:00) · 997c9b2 · observation
calibrate.py -> results/calibration.txt. Noise-free br=-0.5: est -0.489, s_u 0.297, s_e 0.130, coverage 0.903; null rejection 0.077; noisy covariates: br ratio 0.895, coverage 0.787 (vs unattenuated truth). Real-data label shuffle (in fit.py): CI excludes 0 in 0.075 / 0.045. Criterion C held, barely on coverage.

### 2026-10-16 00:45 (+13:00) · 997c9b2 · observation
fit.py -> results/fit.txt/.json. Direction A: Std -0.275 (k=22), -0.194 (k=25); br CIs exclude 0; dR2_oos +0.118/+0.073 but bootstrap frac>0 0.875/0.866; permutation p 0.020/0.096; pooled br -0.014 [-0.89,0.29]; direction B Std -0.374/-0.313. P1-P4 failed, P5 held.

### 2026-10-16 00:45 (+13:00) · 997c9b2 · surprise
REML s_e = 1.06 / 1.39 although the median seed sd of ln_ratio is 0.13. A minority of rules has seed sd 2-4 (ln_ratio down to -7): the homoscedastic Gaussian model is misspecified for those. Pooled br ~ 0 despite per-k slopes -0.4/-0.6 is also unexplained; not debugged (calibration covered single-k fits only, so a pooled-fit bug is not excluded).

### 2026-10-16 00:55 (+13:00) · 269288e · deviation
Ran an unregistered posthoc.py after seeing the failure (quiet-rule subset sd<=0.5; normal-score response). Labelled exploratory in README. HEAD had moved from 997c9b2 to 269288e between fit and posthoc (another session committed; input hash unchanged). Quiet subset meets every registered threshold (Std -0.43/-0.39, p 0.007/0.001); normal scores do not (Std -0.27/-0.20).

### 2026-10-16 00:55 (+13:00) · 269288e · interpretation
Registered hypothesis failed; the negative sign is robust but the all-rule effect is weaker than predicted and fragile at k=25. The matched-pair 76-82% overstated it. The subset result is post hoc on the same data (subset chosen on response dispersion): hypothesis-generating only. Confidence: moderate that the sign is real, low on magnitude. Alternatives: bursty rules carry real kappa-cutoff coupling the Gaussian model cannot see; or the association is a censoring artefact of the cutoff estimator.

### 2026-10-16 00:55 (+13:00) · 269288e · decision
No T2 on the basis of this fit. Next (needs registering): replication on quiet rules at k=23,24 plus a heteroscedastic/robust model for all rules; a two-k synthetic calibration to diagnose the pooled model first. notebook.ipynb written; open-questions entry added. No commit.
