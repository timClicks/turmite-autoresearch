# Kappa matched-area lab notebook

Append-only. Tags: intent, assumption, observation, interpretation, surprise, decision, dead-end, question, deviation.

### 2026-10-14 22:25 (+13:00) · 797704a · intent
Follow the T1b continuation's "next work": decide whether rule-specific kappa survives matching on territory size, using existing T1b windows, before spending simulation on interventions (T2). Predictions in README.

### 2026-10-14 22:25 (+13:00) · 797704a · assumption
Seeds are replicates of a rule, and windows from the same seed at k=22 and 25 are not independent; the pooled ICC treats them as exchangeable and overstates precision. Check: ICC by k separately (the script prints it). Untested.

### 2026-10-14 22:25 (+13:00) · 797704a · assumption
At fixed t, ln A and ln kappa are linked by the identity of Eq. 1, so "controlling for area" removes part of the signal by construction; the M1 threshold of 0.40 was chosen with that in mind, not derived.

### 2026-10-14 22:35 (+13:00) · 797704a · observation
matched_area.py (README command) -> results/matched_area.txt. Pooled ICC raw 0.674, area-adjusted 0.286; by k adjusted 0.561 / 0.467. Slopes of ln kappa on ln A: between rules +1.271, within rules +0.420. Partial Spearman cutoff/R vs kappa given A: -0.560 (k=22), -0.695 (k=25), intervals exclude 0.

### 2026-10-14 22:35 (+13:00) · 797704a · surprise
Both slopes are positive. The registered M2 assumed the across-rule slope would be clearly negative. I mis-signed the confound; M2 therefore failed for a reason unrelated to the hypothesis it was meant to test. T1's "inverse territory size" wording needs re-reading.

### 2026-10-14 22:35 (+13:00) · 797704a · interpretation
M1 failed (0.286 < 0.40) while M3 held, so the registered decision branches conflict; call it unresolved. The per-k adjusted ICCs (0.47-0.56) are post hoc and not a substitute. The pooled ICC is probably depressed because the pooled slope blends between (1.27) and within (0.42) slopes. Confidence low. Alternatives: seed replicates are not exchangeable across k; the linear area adjustment is wrong in form.

### 2026-10-14 22:35 (+13:00) · 797704a · decision
Do not run an intervention yet. Register matched-area pairs first (README "Next").

### 2026-10-15 19:45 (+13:00) · 7eff085 · intent
Register and run matched-area pairs (README second section) before any intervention.

### 2026-10-15 19:45 (+13:00) · 7eff085 · observation
matched_pairs.py -> results/matched_pairs.txt. Tol 0.05: 62/67 pairs; median |dlnk| ratio matched/all 0.24/0.19 (P-a failed, <0.25 band); higher-kappa rule has smaller cutoff in 82%/76% of pairs, intervals exclude 0.5 (P-b held).

### 2026-10-15 19:45 (+13:00) · 7eff085 · interpretation
Area carries most of kappa's rule variation at fixed t; a small residual still orders the cutoff. Confidence low-moderate: seed-noise floor for the residual not yet computed. Notebook.ipynb not updated (still template stub for this section) and should be before closing the experiment.

### 2026-10-15 19:45 (+13:00) · 7eff085 · decision
No intervention yet. Next: seed-noise floor and noise-restricted P-b.

### 2026-10-15 20:10 (+13:00) · da88e61 · intent
Compute the seed-noise floor and noise-restricted P-b per the third README registration (written before the run).

### 2026-10-15 20:30 (+13:00) · da88e61 · observation
noise_floor.py -> results/noise_floor.txt (rerun byte-identical). Seed sd ln kappa 0.089, pair SE 0.043/0.037. Frac z>2: 0.387 (k=22), 0.582 (k=25). P-b on z>2: 0.917 [0.50,1.00] (24 pairs), 0.949 [0.78,1.00] (39). Split-seed N3: 0.790 [0.59,0.95], 0.806 [0.61,0.95].

### 2026-10-15 20:30 (+13:00) · da88e61 · interpretation
Registered N1 (>=60% z>2) failed at both k and N2 failed at k=22 (interval contains 0.5); N3 held. Letter of the decision rule: no T2 on this matched set. N3 and the k=25 complement at 0.50 argue the residual is a real but small rule-level effect, only resolvable in about half the pairs. Confidence moderate-low; not a pass.

### 2026-10-15 20:30 (+13:00) · da88e61 · decision
Do not run T2 on these pairs. Next candidate (needs registering first): rule-level mixed-effects regression of ln_ratio on kappa residual given A using all 44 rules, split-seed. notebook.ipynb still lacks this section and the matched-pairs one.

### 2026-10-15 20:45 (+13:00) · da88e61 · decision
Close the experiment. notebook.ipynb written and executed (nbconvert under uv --with, jupyter not in pyproject.toml); covers all three analyses and matches the README. The rule-level mixed-effects regression stays an open, unregistered follow-up; not started. No commit made (not asked).

### 2026-10-28 18:25 (+1300) · fc9e625 · observation
Reproduced the non-determinism logged in `notes/ACTIVE.md`: two runs of `scripts/matched_area.py` (same environment,
same input sha256[:16] `e813c6f21f63421c`) differ in every M2 and M3 bootstrap interval; point estimates identical.
(`uv run --frozen scripts/matched_area.py` now refuses a PEP 723 script without a script lockfile; run with
`uv run --frozen python scripts/matched_area.py`, which uses the project environment.)

### 2026-10-28 18:40 (+1300) · 4fd558b · decision
Fix (`4fd558b`): sort the rule list before the M2 cluster bootstrap and sort the per-rule `group_by` results used by
the M2 between-rule fit and the M3 bootstrap. Polars returns `unique()`/`group_by()` groups in hash order, which
changes per process, so the seeded `default_rng(20261014)` draws landed on different rules each run. Confirmed as
the cause by the fix: three runs after it are byte-identical. Regenerated `results/matched_area.txt`.

### 2026-10-28 18:45 (+1300) · 4fd558b · observation
Regenerated intervals against the committed ones (run at `797704a`): M2 between 1.271 [1.090, 1.395] (was
[1.107, 1.403]); within 0.420 [0.159, 0.645] (was [0.152, 0.652]); M3 all seeds k=22 [-0.742, -0.338] (was
[-0.743, -0.333]), k=25 [-0.827, -0.508] (was [-0.827, -0.526]); open share <= 0.10 k=22 [-0.752, -0.312] (was
[-0.762, -0.315]), k=25 [-0.823, -0.512] (was [-0.825, -0.514]). Shifts <= 0.018, the size of run-to-run wobble.
No verdict changes: M1 failed, M2 failed (within - between = -0.851 against >= 0.3), M3 held (|rho| >= 0.30 and
intervals exclude 0 at both windows). The old numbers were one draw from the same bootstrap distribution, not wrong
by more than its Monte Carlo error; they were not reproducible.
