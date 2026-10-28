# Lab notebook: alpha-gap

Append-only. Newest entry last. Tags: intent, assumption, observation, interpretation, surprise, decision, dead-end, question, deviation.

### 2026-10-15 23:32 (+13:00) · 07a0951 · intent
Test whether the log/blob cut at alpha = 0.15 is objective (reviewer complaint 2). Tests and predictions are in README.md, registered before code.

### 2026-10-15 23:50 (+13:00) · 07a0951 · observation
`gap_robustness.py` run. Dip p < 0.001; GMM low component 0.094; blob median 0.3312/0.3326/0.3328/0.3329 for cuts 0.10/0.15/0.20/0.25 (0.3293 at 0.05).
Histogram trough is 0.17-0.26, not at 0.15. Details in results/gap_robustness.json.

### 2026-10-15 23:50 (+13:00) · 07a0951 · surprise
Registered prediction 2 (change < 0.001 for cuts in [0.10, 0.25]) failed: spread 0.0017, driven by the 0.10 cut admitting ~200 slow rules.
Predictions 1 and 3 held.

### 2026-10-15 23:50 (+13:00) · 07a0951 · interpretation
The paper's phrase "chosen by eye from the gap" overstated: there is a density trough, but at 0.17-0.26. The cut should be described as an operational
boundary on the flank of the log-grower peak; results are insensitive for cuts >= 0.15. The dip test is weak evidence (rejects unimodality only).
Alternative not excluded: alpha for log-growers is itself a poor estimator when growth is logarithmic (fit over 6 octaves), so the left tail's shape is partly estimator noise.

### 2026-10-15 23:50 (+13:00) · 07a0951 · decision
Report the failed prediction and the trough location in the paper; keep cut 0.15 for continuity with all earlier numbers, and show the sensitivity table.
