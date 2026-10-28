# Lab notebook

### 2026-10-16 21:14 (+13:00) · c9811f5 · intent

User requested a fresh experiment. Test whether the leading-run association
survives contemporaneous area adjustment, using new paired-suffix families and
fresh seeds. Registration is in README.md. Keep work isolated because the shared
tree contains ongoing GPU and ribbon work.

### 2026-10-16 21:14 (+13:00) · c9811f5 · assumption

The current CPU/GPU probe implements the same octave window definition. Verify
four specs byte-for-byte before trusting the GPU batch. Conditioning on current
area remains post-treatment and cannot identify a direct causal lead effect.

### 2026-10-16 21:14 (+13:00) · c9811f5 · decision

Use constant length/composition families instead of independent random rules.
Choose leads 1..4 because the prior study lost many high-lead rules; do not filter
stationarity here. Record retention rather than silently changing the cohort.

### 2026-10-16 21:18 (+13:00) · c9811f5 · observation

`bash experiments/archive/2026-10-kappa-growth-clock/scripts/run.sh` completed.
`results/release-tests.log` passes, `gpu-tests.log` has 5/5 passes, and
`spot-check.txt` records four byte-identical CPU/GPU trajectories. The GPU batch
has no pool requeues (`results/gpu.json`). Synthetic controls from
`uv run experiments/archive/2026-10-kappa-growth-clock/scripts/calibrate.py` recover
the planted coefficient; finite-noise mean bias is +0.000212 over 200 repeats
(`results/calibration.json`).

### 2026-10-16 21:18 (+13:00) · c9811f5 · observation

`uv run experiments/archive/2026-10-kappa-growth-clock/scripts/analyse.py` yields
7/16 complete families in all three windows; support threshold is 12.
`results/analysis.json` and `seed_status.csv`: 45/256 eventual escapes, 40
missing early windows, four further missing target windows, 212 usable starts.
`rule_means_k23.csv`: qualifying rule counts 16/9/15/13 by lead. No models fit.

### 2026-10-16 21:18 (+13:00) · c9811f5 · surprise, interpretation

Restricting lead to 1..4 did not preserve balanced support. Lead 2 loses most
rules here, unlike a monotone high-lead attrition story. This does not diagnose
highways: the instrument only records board escape. The complete-family gate
prevents an unplanned survivor analysis. Growth-clock confounding remains open.

### 2026-10-16 21:18 (+13:00) · c9811f5 · decision

Close as UNINFORMATIVE. Keep the cohort and threshold fixed; do not expand the
board or replace families after seeing attrition. Publish all seed statuses,
including rules with no usable starts. Next candidate is a separately registered
censoring audit on this same cohort. Finish notebook execution and deterministic
rerun checks before committing the final record.

### 2026-10-16 21:21 (+13:00) · 9af869a · deviation

First replay comparison failed because another investigation committed to the
shared branch between analysis runs, changing the report's ambient HEAD field.
No scientific decision changes. Pin that provenance field to run-commit.txt;
the analysis source is separately SHA-256 pinned. Rerun analysis and require
byte-identical outputs before closing. Preserve unrelated staged/working changes.

### 2026-10-16 21:23 (+13:00) · 9af869a · observation

`bash experiments/archive/2026-10-kappa-growth-clock/scripts/replay_cpu.sh` reproduces
the entire 256-spec GPU CSV byte for byte (`results/cpu-replay-check.txt`).
`uv run experiments/archive/2026-10-kappa-growth-clock/scripts/check_replay.py` now
preserves all seven published outputs byte for byte (`results/replay-check.txt`).
Batch resume verifies its recipe and raw digest, then skips computation.

### 2026-10-16 21:24 (+13:00) · 916d2f4 · decision

Closed: registered support gate failed; P1/P2 remain untested. Notebook executed
top to bottom against committed inputs using the README nbconvert command
(`results/notebook-check.log`). Analysis replay still matches after commit.
README, executed notebook and JSON agree. No Rust instrument or dependency was
changed by this experiment. Retain fresh cohort for a prospectively registered
censoring follow-up; no additional runs are launched in this session.
