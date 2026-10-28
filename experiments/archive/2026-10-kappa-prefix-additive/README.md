# Additive or interacting? Letter-by-position models of ln kappa (2026-10-20)

## Question
`../2026-10-kappa-prefix-ablation/` found the 8-letter lookup's information is spread over letters 2-7, but a conjunctive
key cannot separate main effects from interactions. Does an additive model over the same letters reach the lookup's R^2?

## Design (registered before running, 2026-10-20 06:00 +13:00, git bfa8c0e)
- Same split as the sibling experiments: 2185 stationary blob census rules (train), 162 fresh stationary rules (test), disjoint;
  strict held-out R^2 against the training mean.
- Features: binary indicator (1 if the letter is `L`) for positions 2..8 (position 1 is constant); rules shorter than 8 letters
  get 0 for missing positions plus an indicator `len < 8`... (the fresh test rules are all >= 13 letters, so this only affects training).
- **A:** ridge regression, 7 position indicators + the short-rule flag. **A2:** A plus all 21 pairwise products of the 7 indicators.
  Ridge penalty fixed at 1.0 on standardised features (not tuned). Reference: the 8-letter lookup P8 (>= 3 rules, fallback to shorter keys).
- Bootstrap over test rules, 2000 resamples, seed 20261020.

## Predictions (written before the run)
- **B1:** the additive model A has test R^2 < 0.40.
- **B2:** the pairwise model A2 has test R^2 >= 0.50.
- **B3:** P8 exceeds A by at least 0.15.

Failures are reported as failures; anything chosen after seeing the results is labelled post hoc.

## Results (`results/additive.txt`; 2185 train, 162 test, 0 in both)
| model | strict held-out R^2 | 95% CI |
|---|---|---|
| A: additive, 7 position indicators | +0.109 | [+0.003, +0.194] |
| A2: A + 21 pairwise products | +0.351 | [+0.234, +0.447] |
| P8: 8-letter lookup | +0.624 | [+0.473, +0.729] |

P8 - A = +0.515 [+0.372, +0.634]. **B1 HELD** (A < 0.40), **B2 FAILED** (A2 = 0.35 < 0.50), **B3 HELD** (P8 - A >= 0.15).

**Reading.** An additive model over letter positions captures about a sixth of what the lookup does, and adding all pairwise
interactions still leaves 0.27 of R^2 on the table. The signal therefore needs interactions of order three or higher among
letters 2-8, consistent with it being a property of whole opening patterns (families of rules sharing a prefix) and not of
individual letters. Caveats: ridge penalty fixed at 1.0 and not tuned (a tuned or nonlinear model such as a tree ensemble
might reach more than A2 without being a lookup); binary L/R indicators only; the lookup's advantage is partly memorisation of
prefix families that overlap between training and test, so "interaction structure" and "family membership" are not separated here.

## Reproduce
`uv run experiments/archive/2026-10-kappa-prefix-additive/scripts/additive.py` -> `results/additive.txt`, `results/additive.json`.
