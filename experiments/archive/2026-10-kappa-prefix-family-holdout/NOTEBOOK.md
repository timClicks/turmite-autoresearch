# Lab notebook: kappa prefix family holdout

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 07:10 (+13:00) · 7339dc9 · intent
Separate higher-order letter structure from prefix-family memorisation, which the additive experiment could not. Hold out whole 6-letter prefix families in cross-validation on the census. Predictions D1-D3 registered in README and committed (1787ecc) before `scripts/holdout.py` existed.

### 2026-10-20 07:30 (+13:00) · 1787ecc · observation
Ran `holdout.py` (seed 20261020, 8 folds, 43 families). Pooled out-of-fold strict R^2, random CV vs family-held-out CV: A +0.109 vs -0.162; A2 +0.300 vs -0.690; P8 +0.591 vs -0.162. D1 held, D2 and D3 failed.

### 2026-10-20 07:35 (+13:00) · 1787ecc · surprise
I expected the pairwise model to keep at least some signal across families (D2, D3). It does worst of all (-0.69), worse than the training mean. Even the lookup, which falls back to shorter prefixes for unseen families, is below the mean.

### 2026-10-20 07:40 (+13:00) · 1787ecc · interpretation
The prefix signal is family membership, not a transferable letter-level rule, consistent with the paper's caveat. Caveats: 43 uneven families, about five held out per fold, and held-out family means differ from the training mean; negative R^2 largely reflects that. The test does not show that no structure exists within families.

### 2026-10-20 07:40 (+13:00) · 1787ecc · question
Does a model with a family random effect plus within-family letter structure beat the family mean alone? And does holding out families at 4 or 8 letters change the picture (a graded test of how coarse a family is)? Not done.
