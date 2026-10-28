# Lab notebook

### 2026-10-22 21:33 +13:00 · 074f4a7 · intent
Read parent README and append-only notebook before designing. Parent explicitly leaves single-cell arm unregistered. Registered new conditional long-excursion test, three rules/four seeds, traffic candidates and exposure-matched controls before measuring. Pruning index empty (queries and revision in README), RUN. Existing unrelated untracked falsification-harness results untouched.

### 2026-10-22 21:38 +13:00 · 3ec3cef · observation
Command: `UV_PROJECT_ENVIRONMENT=/home/tim/.venvs/turmite uv run --frozen experiments/archive/2026-10-single-cell-gates/scripts/run.py` in WSL (environment path local provenance only). Fresh release build, independent sparse oracle 40 synthetic cases passed. All 16 specs completed; 213 ant departures, 617 matched pairs; 260 departures including controls. Live checks and 532 sham/offpath/rw control rows passed exactly. 25 unmatched candidates across ants and walkers. Analysis `uv run --frozen experiments/archive/2026-10-single-cell-gates/scripts/analyze.py`; analysis.json. Registered predictions not supported: time contrast -0.047 [-0.407,0.290], reach contrast 0.096 [-0.105,0.301]. Seed SD and rule contrasts in analysis.json. Censoring 15/1234 ant interventions (1.22%) triggers registered restriction to capped outcomes. No uncensored time finding.

### 2026-10-22 21:38 +13:00 · 3ec3cef · interpretation
Single cells often alter outcomes, but traffic-selected candidates have no resolved advantage over exposure-matched cells. Rule heterogeneity substantial; three rules cannot exclude a sparse-gate mechanism. Reach interventions censored at cap are likewise restricted path reach, not ultimate reach. A negative candidate-ranking result is not family-wide exclusion.

### 2026-10-22 21:38 +13:00 · 3ec3cef · deviation
Registration timestamp 21:33 was rounded ahead of file creation; first registration saved ~21:32, committed in 3ec3cef before run at 21:34:49. The parent's live sampler silently skips episodes whose undo logs overflow cap; this version inherits that behavior and does not count skipped censored baselines. Therefore full eligibility/censoring of all baseline departures is unknown; 0 sampled baseline censoring does not certify the omitted population. Random walk 301 yielded no long departures; rw302 yielded one. Controls establish exactness, not statistical power. Scripts/implement.py is a historical generator only; canonical source is examples/single_cell_gates.rs including oracle test. Do not rerun generator over final source.
