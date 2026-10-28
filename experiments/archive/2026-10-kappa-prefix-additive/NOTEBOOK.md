# Lab notebook: kappa prefix additive

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 06:00 (+13:00) · bfa8c0e · intent
Test whether the prefix signal for ln kappa is additive over letter positions or needs interactions. Predictions B1-B3 registered in README and committed (32c0f82) before `scripts/additive.py` existed.

### 2026-10-20 06:40 (+13:00) · 922a870 · observation
Ran `additive.py` (seed 20261020, ridge lambda 1.0, 2000 bootstraps). Held-out R^2 on 162 fresh stationary rules: additive A +0.109, additive+pairwise A2 +0.351, 8-letter lookup P8 +0.624. B1 held, B2 FAILED, B3 held.

### 2026-10-20 06:40 (+13:00) · 922a870 · deviation
The reader guide for this experiment was added before the run, saying 'registered but not yet run', because the blog renderer fails without a guide for each tracked experiment and main was about to receive this folder. Updated to the result after the run (see the guide row).

### 2026-10-20 06:45 (+13:00) · 922a870 · interpretation
Letter-by-position effects explain little; pairwise interactions explain about half of what the lookup does; the rest needs order-three-or-higher structure or family membership. I cannot separate these with this design, because the lookup also exploits prefix families shared between train and test. The B2 failure means I overestimated what pairs could recover.

### 2026-10-20 06:45 (+13:00) · 922a870 · question
Does a flexible model that cannot memorise families (trained on rules whose 6-letter prefix families are held out entirely) retain any of the 0.62? That is the family-versus-structure question and needs a split by prefix family; not done.
