# Lab notebook

### 2026-10-15 21:12 (+13:00) · da88e61 · intent
User asked to move the science forward. Test the unclosed area-selection
confound of the matched-area cutoff association with independent seed groups.
Prediction and estimator registered in README before executing code.

### 2026-10-15 21:12 (+13:00) · da88e61 · assumption
Seeds are independent patched starts, and two surviving seeds per role provide
a noisy but meaningful rule mean. Excluding escapes can select trajectories;
the design cannot remove that bias. Six role assignments share rules and seeds,
so bootstrap rules jointly, never treat assignments or pairs as replicates.

### 2026-10-15 21:18 (+13:00) · da88e61 · observation
Ran `uv run experiments/archive/2026-10-independent-area/scripts/analyse.py` via WSL.
`results/analysis.json`: synthetic null 0.497, association control 0.957;
44 rules/window; registered concordance 0.730 [0.605,0.842] at k=22,
0.757 [0.617,0.881] at k=25. Both pass. Tolerance 0.10 also passes.
Initial sandboxed WSL invocation failed with access denied; elevated WSL succeeded.

### 2026-10-15 21:18 (+13:00) · da88e61 · deviation
Clarification of registration: bootstrap assignments are kept together within
a window; independent draws are used for the two marginal window intervals.
No joint-window inference is made. The retained rules are the same at both windows.

### 2026-10-15 21:18 (+13:00) · da88e61 · interpretation
Shared-trajectory matching does not suffice to explain the association. Noisy
area, previous rule selection and escape conditioning remain possible confounds.
Earlier failed noise-floor gate remains failed; this does not authorize a
mechanistic claim. Need independent trajectories at matched size and a powered
intervention; this analysis alone cannot say whether the cutoff causes growth.

### 2026-10-15 21:22 (+13:00) · da88e61 · decision
Analysis complete. `cargo test --release` passed (`results/cargo-test.log`).
Reran the registered analysis byte-identically, output SHA-256
737ad21e7495302cfc70176a60b7adb4d6a86c3136db8bc521962fcaaeebf610.
Generated the notebook with `uv run experiments/archive/2026-10-independent-area/scripts/make_notebook.py`
and executed it with uv/nbconvert from a clean kernel (command in README).
Scientific notes updated; no commit made. Next step is prospective matched-size
data and intervention design, not another reformulation of these same pairs.
