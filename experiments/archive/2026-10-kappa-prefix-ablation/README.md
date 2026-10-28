# Which prefix positions carry kappa? Per-position ablation (2026-10-20)

## Question
`../2026-10-kappa-prefix-runs/` showed the prefix signal is distributed over the opening (first four runs 0.48, eight letters 0.62).
Which of letters 1-8 carry it?

## Design (registered before running, 2026-10-20 05:20 +13:00, git f40da67)
- Same train / test as the sibling experiments: 2185 stationary blob census rules, 162 fresh stationary rules, disjoint; strict
  held-out R^2 against the training mean; lookup P8 (first 8 letters, fall back to shorter keys with >= 3 training rules).
- **Ablation of position j (j = 1..8):** the key ignores letter j (replaced by `*` in the key for all depths that include it).
- **Group-count control:** ablating a position merges groups, which changes the bias-variance trade-off independently of
  information. Control: permute the letters at position j among training rules (200 permutations, seed 20261020) and re-run the
  lookup unchanged on the test rules; this keeps the number of groups and destroys the information at j. Report the mean control R^2.
- Loss = R^2(P8) - R^2(ablated). Bootstrap over test rules (2000 resamples) for the ablation loss.

## Predictions (written before the run)
- **A1:** position 1 (always R in this cohort) has loss within 0.01 of 0.
- **A2:** each of positions 2, 3, 4 has ablation loss >= 0.05.
- **A3:** no position in 5-8 has a larger ablation loss than the largest loss among positions 2-4 (information is front-loaded).
- **A4:** for each position the permutation-control loss is at least as large as the masking loss minus 0.05 (masking is not
  hiding a large information effect behind regrouping; failure means the masking and the control disagree).

Failures are reported as failures; anything chosen after seeing the results is labelled post hoc.

## Results (`results/ablate.txt`; 2185 train, 162 test, 0 in both; P8 R^2 +0.624)
| position | R^2 with letter ablated | loss [95% CI] | permutation control loss |
|---|---|---|---|
| 1 | +0.624 | +0.000 | +0.000 |
| 2 | +0.395 | +0.229 [+0.128, +0.331] | +0.252 |
| 3 | +0.370 | +0.255 [+0.138, +0.383] | +0.280 |
| 4 | +0.279 | +0.345 [+0.223, +0.474] | +0.388 |
| 5 | +0.224 | **+0.400** [+0.230, +0.565] | +0.442 |
| 6 | +0.330 | +0.294 [+0.171, +0.405] | +0.321 |
| 7 | +0.408 | +0.216 [+0.096, +0.321] | +0.234 |
| 8 | +0.552 | +0.073 [-0.002, +0.157] | +0.099 |

**A1 HELD, A2 HELD, A3 FAILED, A4 HELD.**

**Reading.** The information is not front-loaded: ablating position 5 costs the most (0.40), and positions 2-7 each cost 0.2-0.4,
whereas position 8 costs 0.07 (interval includes 0). The permutation control, which keeps the group count and destroys only the
information at the position, gives slightly larger losses at every position, so the masking result is not a regrouping artefact.
Caveat that limits the reading: the lookup is a conjunctive key over the whole prefix, so a large loss at one position
says that position matters in combination with the others, not that it matters additively; it cannot separate main effects from
interactions, and the lost R^2 across positions sums to far more than 0.62. Which letter patterns matter (for instance, where
the first L-to-R changes fall) is untested. Together with the run-structure result (lead alone 0, four runs 0.48) this says the
signal is a property of roughly letters 2-7 taken together.

## Reproduce
`uv run experiments/archive/2026-10-kappa-prefix-ablation/scripts/ablate.py` -> `results/ablate.txt`, `results/ablate.json`.
