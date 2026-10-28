# Lab notebook: kappa prefix ablation

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 05:20 (+13:00) · f40da67 · intent
Find which of letters 1-8 carry the prefix signal for ln kappa. Predictions A1-A4 registered in README and committed (593d127) before `scripts/ablate.py` existed. A permutation control keeps the group count fixed so masking is not confused with regrouping.

### 2026-10-20 05:30 (+13:00) · 593d127 · observation
Ran `ablate.py` (seed 20261020, 2000 bootstraps, 200 permutations). Loss in held-out R^2 from ablating position 1..8: 0.00, 0.23, 0.26, 0.35, 0.40, 0.29, 0.22, 0.07 (P8 R^2 0.624). A1, A2, A4 held; A3 FAILED.

### 2026-10-20 05:35 (+13:00) · 593d127 · surprise
I expected the information to be front-loaded (the lead-run picture). Position 5 costs the most and positions 6-7 cost as much as positions 2-3. Only position 8 is nearly free.

### 2026-10-20 05:40 (+13:00) · 593d127 · interpretation
The signal is spread over roughly letters 2-7. The lookup is a conjunctive key, so a large loss at one position means it matters jointly with the others; the losses sum to far more than the 0.62 total, which is the signature of interaction or redundancy. This experiment cannot separate main effects from interactions. The permutation control agrees with masking at every position (A4).

### 2026-10-20 05:40 (+13:00) · 593d127 · question
Does an additive model (letter-by-position effects, ridge) reach 0.6, or does the signal need interactions? A registered comparison of an additive model with the full 8-letter lookup on the same split would answer it.
