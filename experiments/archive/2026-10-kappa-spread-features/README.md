# What carries the rule-determined spread of ln kappa? Prefix vs suffix vs composition (2026-10-20)

## Question
`../2026-10-kappa-spread-budget/` found that the first eight rule letters predict about half of the variance of ln kappa
(held-out R^2 0.55-0.63 on rule means) and that about a third is rule-determined but unexplained. Is the predictable part
specific to the **start** of the rule string (consistent with the lead-run / early-evolution story), or would other string
summaries do as well (end of the string, letter composition)?

## Design (registered before running, 2026-10-20 03:10 +13:00, git 91a2243)
- **Train:** census rules in `../2026-10-probe-growth-census/results/probe_summary.csv`, blob class, `kappa > 0`,
  `|g_k| < 0.05` (stationary), ln kappa as target. **Test:** the fresh stationary rules (13-14 letters, 162) with ln kappa
  `target` from `../2026-10-kappa-rule-space/results/prefix_audit_predictions.csv` (one row per rule, cohort `stationary`,
  encoding `loo`, area `linear`). Train and test are disjoint by rule. The training filter approximates the audit's
  (2183 rules there); the exact count is reported.
- **Models** (all area-free, rule string only; strict held-out R^2 against the training mean, as in W3c):
  - **P8:** mean of ln kappa over training rules sharing the first 8 letters, falling back to shorter prefixes with >= 3 rules (the W3c lookup).
  - **S8:** same with the **last** 8 letters (suffix), same fallback.
  - **C:** ordinary least squares on composition: length, count of R, number of runs, longest run of L, longest run of R.
  - **P8+C:** P8 prediction plus C as a second regressor (OLS on training predictions made leave-one-out within training).
- **Uncertainty:** bootstrap over test rules, 2000 resamples, seed 20261020.

## Predictions (written before the run)
- **F1:** P8 test R^2 is within 0.1 of the W3c value 0.633 (the training cohort differs slightly).
- **F2:** S8 test R^2 is at least 0.2 below P8 (the predictable part is specific to the start of the string).
- **F3:** C test R^2 < 0.2.
- **F4:** P8+C improves on P8 by less than 0.05 (composition adds nothing beyond the prefix).

Any of these failing is reported as failed. Choices made after seeing results will be labelled post hoc.

## Results (`results/features.txt`; 2185 train rules, 162 test rules, 0 in both)
| model | strict held-out R^2 | 95% CI |
|---|---|---|
| P8 (first 8 letters) | +0.624 | [+0.486, +0.732] |
| S8 (last 8 letters) | -0.114 | [-0.298, +0.034] |
| C (composition) | +0.079 | [-0.052, +0.190] |
| P8 + C | +0.632 | [+0.499, +0.737] |

P8 - S8 = +0.739 [+0.571, +0.919]; (P8 + C) - P8 = +0.008 [-0.025, +0.043].
**F1-F4 all HELD.** Post hoc control (unregistered): leave-one-out inside the training set gives P8 +0.589 and S8 -0.065
(training lengths 3-12, test 13-14), so the suffix failure is not only a length-alignment artefact of the transfer.

**Reading.** The rule-determined, predictable part of ln kappa sits in the first eight letters. The last eight letters carry
nothing measurable (even slightly negative), and simple composition (length, R count, run structure) adds nothing beyond the
prefix. This is consistent with the lead-run / early-evolution picture, where the opening of the rule sets the regime, and is
evidence against kappa being a bulk property of letter composition. It does not say which feature of the prefix matters (the
prefix lookup is a family-membership predictor, see the paper's caveats), and prefix families overlap between train and test.
It also does not explain the remaining unexplained third of the spread: the prefix, suffix and composition summaries tried here
do not reach it. Not tested: middle letters, interactions beyond the group means, and any dynamical (non-string) predictor.

## Reproduce
`uv run experiments/archive/2026-10-kappa-spread-features/scripts/features.py` -> `results/features.txt`, `results/features.json`.
