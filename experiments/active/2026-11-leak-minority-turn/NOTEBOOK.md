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

### 2026-11-13 09:11 (+1300) · 5ee269f · observation
Run started (3016 specs, 3 threads); `cargo test --release --locked --test fresh_set` 4/4 while it ran. Probe binary sha256 matches PR #38's.

### 2026-11-13 09:36 (+1300) · eb7f41d · observation
Run ended 09:35 (24 min). `analyse.py`: G1 156/156, G2 PASS; 84 eligible, 81 scoreable. P1 Spearman -0.114 [-0.329, +0.108] FAILS;
P2 29/62 [0.35, 0.59] FAILS; P3 RRRR 4/6 (fail), RLLL 8/9 -> FAILS. Re-run and `PYTHONHASHSEED=7` give identical bytes.

### 2026-11-13 09:38 (+1300) · eb7f41d · interpretation
The composition reading from PR #38's post hoc look does not transfer: on new core-class rules the correlation is slightly negative
and its interval excludes the development value. Calibration says the rule would almost never fail if the development slope were
real, so I read this as a retired description, not a low-power miss. Confidence high within the class and window. Not excluded:
other functions of the rule table, or dynamics-based predictors.

### 2026-11-13 09:40 (+1300) · eb7f41d · surprise
Post hoc (`posthoc.py`): the spread of Lambda replicates almost exactly (sd 0.381 vs 0.383) with seed noise ~0.057. The effect is
real and rule-specific; only my explanation of its sign failed.

### 2026-11-13 09:45 (+1300) · eb7f41d · dead-end
Criterion: P1-P3 as registered at `fc60f7b`; evidence `eb7f41d`. Signature `NR-20261113-leak-handedness-composition-sign`. Limits:
core class, k = 12..22, board 16384, 4 seeds, EF 0.3/0.5. Reopen if a scoring error is found or the test is run in another class
or window.
