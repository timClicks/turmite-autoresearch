# Lab notebook: kappa prefix runs

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 03:50 (+13:00) · 014f2c2 · intent
Find which part of the 8-letter prefix carries the information about ln kappa, using run structure of the opening (lead, first two, three, four runs). Predictions H1-H4 registered in README and committed (17ad529) before `scripts/runs.py` existed.

### 2026-10-20 04:00 (+13:00) · 17ad529 · observation
Ran `runs.py` (seed 20261020). Held-out R^2 on 162 fresh stationary rules (train 2185): P8 +0.624, R1 -0.004, R2 +0.246, R3 +0.337, R4 +0.475. H1, H2, H3 FAILED; H4 held.

### 2026-10-20 04:05 (+13:00) · 17ad529 · surprise
The lead alone has R^2 of about zero. I had registered >= 0.15 because the leadrun experiment found slope +0.15 to +0.24 per lead step. That association was at fixed area, and the c-law Stage 4 showed it reproduces under conditioning on the area collider; an unconditional lead lookup is a different quantity and here it is empty.

### 2026-10-20 04:10 (+13:00) · 17ad529 · interpretation
The prefix information is distributed over the opening (0.25, 0.34, 0.48 for two to four runs, 0.62 for eight letters), not in one early run length. Caveat: run keys and letter-prefix keys differ in group count and granularity, and I ran no matched group-count control, so 'R4 < P8' mixes information and key granularity. Not tested: per-position and interaction effects.

### 2026-10-20 04:10 (+13:00) · 17ad529 · question
Which letters of positions 5-8 add the remaining 0.15 over R4? A registered per-position ablation on the 8-letter lookup (drop letter j, compare held-out R^2) with a group-count-matched control would say whether specific positions dominate.
