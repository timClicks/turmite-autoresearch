# Lab notebook: leak minority turn (Q42 follow-up)

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-11-13 08:50 (+1300) · a2c9494 · intent
Daily session. Open PRs #30-#38 all wait on review; PR #33's validation was already done on 11-04 (NOTEBOOK entry in the
Q33 folder). PR #38's CI had sat queued for ~23 h; pushed an empty commit to retrigger it. Chosen next step: the held-out
test that PR #38 names, of its post hoc composition reading, stacked on PR #38. Informs whether the rule-by-rule handedness
effect has a transferable description within the core class.

### 2026-11-13 09:08 (+1300) · a2c9494 · observation
`select_specs.py`: pool 2298, cohort H 110 rules, anchor A 6 rules, 3016 specs. Composition of H: 30 rules fr < 0.45, 54 > 0.55,
14 balanced; 9 `RRRR`, 14 `RLLL`. `calibrate.py` (synthetic): table in `results/calibration.txt`. A first, loop-based version of
the bootstrap Spearman was too slow and was replaced by a vectorised row-rank version before the table was produced; its first
line (n 50, b_dev) matched the loop version's output exactly on the same RNG stream, a check that the two rankers agree.

### 2026-11-13 09:10 (+1300) · a2c9494 · decision
Pruning preflight as in the README (no member signature); run. Predictions P1-P3, gates G1-G2 and calibration registered in the
README before any held-out ant run and before `run.sh` / `analyse.py` exist. Budget about 25 min, stop at 90.
