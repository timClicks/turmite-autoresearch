# Does the prefix signal survive holding out whole prefix families? (2026-10-20)

## Question
`../2026-10-kappa-prefix-additive/` could not separate higher-order interaction structure from memorisation of prefix families
shared by train and test. If the signal is structure, a model should predict rules from families it has never seen; if it is
memorisation, only the lookup should work on seen families and it should collapse on unseen ones.

## Design (registered before running, 2026-10-20 07:10 +13:00, git 7339dc9)
- Data: the 2185 stationary blob census rules (`../2026-10-probe-growth-census/results/probe_summary.csv`, target ln kappa).
  (The 162 fresh rules share their 6-letter prefix families with the census, so they cannot test unseen families.)
- **Family** = first 6 letters. **Grouped CV:** 8 folds in which each fold holds out whole families (families assigned to folds
  by a seeded shuffle, seed 20261020); **random CV:** 8 folds of random rules (same seed), where test rules' families are in training.
  Out-of-fold strict R^2 against the training-fold mean, pooled over folds.
- Models: **P8** (8-letter prefix lookup with fallback to shorter keys, >= 3 rules); **A2** (ridge, penalty 1.0, 7 position
  indicators + 21 pairwise products, as in the sibling experiment); **A** (additive ridge).
- Bootstrap over rules for 95% intervals (2000 resamples).

## Predictions (written before the run)
- **D1:** P8 has random-CV R^2 >= 0.45 and grouped-CV R^2 < 0.30 (memorisation of families).
- **D2:** A2 grouped-CV R^2 is within 0.10 of its random-CV R^2 (its signal, if any, is not family memorisation).
- **D3:** A2 grouped-CV R^2 exceeds P8 grouped-CV R^2.

Failures are reported as failures; choices made after seeing results are labelled post hoc.

## Results (`results/holdout.txt`; 2185 census rules, 43 families, 8-fold CV, pooled out-of-fold strict R^2)
| model | random CV | family-held-out CV |
|---|---|---|
| A (additive) | +0.109 [+0.069, +0.150] | -0.162 [-0.200, -0.128] |
| A2 (pairwise) | +0.300 [+0.239, +0.357] | -0.690 [-0.857, -0.524] |
| P8 (lookup) | +0.591 [+0.468, +0.691] | -0.162 [-0.230, -0.107] |

**D1 HELD, D2 FAILED, D3 FAILED.**

**Reading.** When whole 6-letter prefix families are held out, every model does worse than predicting the training mean
(negative R^2); the lookup falls from 0.59 to -0.16 and the pairwise model from 0.30 to -0.69. So none of these models learns a
letter-level rule that transfers to unseen families: the predictive signal is **family membership** (rules sharing an opening
behave alike), which is what the paper's own caveat says (transfer within prefix families to longer rules, not to unseen
families). This is the answer to the sibling experiment's question: the lookup's advantage over additive and pairwise models is
memorisation of family means, not a structure the other models missed.
Caveats: only 43 families, with uneven sizes, and each held-out fold removes about five whole families, so this is a hard
extrapolation in which the held-out families' mean ln kappa can differ from the training mean by more than any letter-level model
can recover (the negative R^2 mostly reflects family-mean shifts; the test does not show that letter-level structure is absent
within a family or at lengths not tested); the pairwise ridge is untuned and overfits families (-0.69). Not tested: a model with
a family-level random effect, or held-out families at coarser or finer prefix lengths (4 or 8 letters).

## Reproduce
`uv run experiments/archive/2026-10-kappa-prefix-family-holdout/scripts/holdout.py` -> `results/holdout.txt`, `results/holdout.json`.
