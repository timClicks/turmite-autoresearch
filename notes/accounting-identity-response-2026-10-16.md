# Accounting, prediction and mechanism: response to criticism

2026-10-16 00:18 NZDT. Editorial audit of existing evidence; base commit
`997c9b2da6efa526fc6c5a57104d103e1345e916`, with pre-existing working changes.
No simulations, estimator changes or new scientific measurements in this audit.

## Suggested response to the reviewer

We agree that the three-factor equality is an accounting identity and that
reconstructing the exponent from factors measured on the same trajectory
does not validate a physical mechanism. Describing this as a “calibrated
mean-field decomposition” overstated the result. We have replaced the subtitle
with “Rules of length ≤ 12: calibrated growth and boundary transport”.
Calibration refers to the growth estimators and their finite-window bias,
not to a derivation of boundary access.

The revised methods separate the identity, the conditional scaling argument
and the missing dynamical closure. Stationary entry probability and relative
boundary occupation, together with square-root boundary scaling, imply the
cube-root regime conditionally. Their occurrence and persistence are empirical
observations; their origin is not derived. The occupation ratio is a directly
counted observable, but expressing it as a normalized ratio does not explain
it. Neither factor reconstruction nor same-run prefactor collapse is presented
as independent mechanism validation. The geometric amplitude also enters the
growth prefactor, so even knowledge of entry and occupation alone would not
fully predict it.

We retain two predictive results while stating their limits. A registered
future-window test on existing simulations finds that early transformed-area
budgets forecast later increments better than an other-rule baseline. The
budget uses only area endpoints: this is evidence for persistence, not for
the separate physical roles of the transport factors. A registered prefix
lookup transfers to fresh longer rules within a measured stationary cohort.
This narrows the claim that occupation is wholly unpredictable from the rule,
but neither the cohort filter nor the lookup supplies a transport mechanism.
Its success does not generalize to all retained rules or unseen prefix families.

The negative edge, excursion and stochastic-control results remain constraints
on the tested explanations. They do not establish a replacement explanation
by elimination. The revised conclusion identifies the contribution as a
calibrated growth census, predictive regularities and constraints on candidate
mechanisms. Why these ants attain their rule-specific occupation and why it
stabilizes remain unresolved.

## Evidence boundaries

- [Original hypothesis](cube-root-hypothesis.md): P5 was not an independent
  falsification criterion. Its correction is appended without changing the
  original registration.
- [Transport forecast](transport-forecast-2026-10-13.md): 1,185 complete
  trajectories of 99 rules, early windows k=20–22, later windows k=23–26;
  bootstrap seed 20261013. Median of equal-weight rule-mean relative increment
  errors: 0.08486 versus 0.26922; reduction 68.48%, interval 61.33–80.58%.
  These are existing saved results, not new estimates. Exclusions, near-stall
  tails, controls and the exploratory other-seed check remain explicit.
- Prefix result: the manuscript loads
  `research-outputs/scholarly-articles/cube-root-growth/kappa_prediction.json`, extracted by
  `uv run research-outputs/scholarly-articles/cube-root-growth/kappa_prediction_numbers.py`
  from the recorded W3c results. On 162 stationary fresh rules, prefix-only
  strict R² is 0.633; adding prefix to early area improves R² by 0.240
  [0.148, 0.347], 2,000 rule bootstraps, seed 20261045. The training set is
  fixed in that bootstrap; families overlap intentionally across the split.
- [Mechanism plans](kappa-mechanisms-2026-10-15.md) distinguish independent
  prediction from reconstructing occupation using its own return-time budget.
  Existing pilot instruments are not evidence for the proposed mechanisms.

## What would materially answer the mechanistic objection?

This is a research requirement, not a new preregistration or a claim that the
following experiment has run. Before new measurements, freeze a model that
predicts boundary access from independently sampled field or return dynamics,
its calibration, seed-role assignment, cohort and failure thresholds. Test on
separate starts and, where transfer is claimed, held-out rule families. Sample
at fixed area and record geometry and field history; a single early-area
regression does not remove every size or age confound. Handle window-crossing
excursions and band failures explicitly.

Compare later-growth predictions with an early-area-history baseline, because
the current total-budget forecast already uses area history alone. Predict
both occupation level and drift, rather than selecting stationary outcomes
and then claiming stationarity is explained. A targeted field intervention
with matched control edits should then change the predicted return dynamics
and occupation in the specified direction and magnitude. Same-seed accounting
closure, successful prediction and causal intervention are separate tests.
Existing failed precision gates must be resolved rather than bypassed.

## Manuscript changes

Edited `research-outputs/scholarly-articles/cube-root-growth/main.typ`: subtitle,
contribution list, factor definitions and scaling assumptions, geometry
prefactor, original P5 interpretation, prefix-score interpretation,
future-window forecast scope, outlier caption, interior-mixing claims,
evidence table, limitations and conclusion. Original numerical inputs and
negative results were retained. No commit was made.

Verification commands (WSL, repository root):

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
typst compile --root . research-outputs/scholarly-articles/cube-root-growth/main.typ research-outputs/scholarly-articles/cube-root-growth/main.pdf
cargo test --release
```

Build and release-test logs are under `tmp/accounting-review/`.

Verification completed: Typst compiled without diagnostics; the full
`cargo test --release` suite passed (exit 0; compiler warnings remain).
The 39-page PDF's changed title, accounting, prefix, forecast and
limitations/conclusion pages (1, 8, 14, 15, 28) were rendered and visually
reviewed. PDF SHA-256:
`64920b08ca86eedb82537a48fd316146170874c27692b72517990e11b50f1dc4`.
`git diff --check` passes for the edited tracked files. No data, estimator,
dependency or simulator changes were needed, and nothing was committed.
