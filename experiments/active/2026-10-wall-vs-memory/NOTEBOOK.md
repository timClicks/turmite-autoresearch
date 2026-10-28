# Lab notebook: wall or memory

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-26 22:50 (+1300) · 5b96f68 · intent
Owner asked to set up the "hybrid walker" experiment proposed in chat: a walker
with memoryless turns inside its territory but the ant's forced R on fresh
ground, to separate the two ingredients of the original cup mechanism. Informs
whether the next boundary-access work should look at the edge rule or at
interior memory.

### 2026-10-26 22:58 (+1300) · 5b96f68 · decision
While designing, generalised the hybrid into a 2x2 factorial: turn noise applied
separately on fresh cells (EF) and revisited cells (EV). The hybrid is the
corner EV=1, EF=0; EV=EF=1 is exactly pw:0.5; EV=EF=0 is the ant. The extra
corner F1 (EV=0, EF=1) tests the ant itself, which the hybrid alone cannot.
Dropped the Q (interior chirality) and P (wall strength) ladder from the chat
proposal: P is covered by EF, and Q only adds chirality.

### 2026-10-26 22:58 (+1300) · 5b96f68 · decision
Pruning preflight at 5b96f68: queries and outcome in README (three entries,
incidental word hits only, none in scope). Decision: run.

### 2026-10-26 23:00 (+1300) · 5b96f68 · assumption
Thinking the hybrid through before registering moved my prior towards
H-memory: a forced-R step on fresh ground closes a loop of at most four steps
back to the entry cell, then the walker leaves at random, so loops can chain
outward; the random-cookie walker (similar first-visit-only structure) stayed
at a ~ 0.92. I said the opposite emphasis in chat (wall as the leading
candidate). Status: untested; the run decides.

### 2026-10-26 23:05 (+1300) · 5b96f68 · decision
Registered question, walker semantics, exact identities, classification,
calibration gates G1-G3 and corner/dose predictions in README before writing
the walker. Rule cohort drawn with `scripts/select_rules.py` (seed 20261026).

### 2026-10-26 23:45 (+1300) · 086c1ac · deviation
`Rule` rejects one-letter rules, so the rule-free corners run as `hy:RL:1:0` and
`hy:RL:1:1` (README addendum). Label only; trajectories are rule-free (tested).

### 2026-10-26 23:50 (+1300) · 086c1ac · observation
`HybridWalker` (src/walkers.rs) and `hy:` spec in `bin/probe`. `cargo test --release
--locked --test hybrid_walker`: 5/5 pass. Full `cargo test --release --locked`: exit 0,
49 test binaries ok (rustc 1.97.0, log kept in session scratch, not committed).
`scripts/analyse.py` written and committed before the run.

### 2026-10-26 23:15 (+1300) · f1bd2c8 · deviation
corrects: 2026-10-26 23:05, 23:45, 23:50 entries and README header/addendum times.
Those times were my estimates, not clock readings. Git commit times are
authoritative: registration 086c1ac 22:55:21, walker f1bd2c8 23:02:13, Stage 1 run
23:02:30-23:05:33 NZDT. Order registration -> code -> run holds.

### 2026-10-26 23:15 (+1300) · f1bd2c8 · observation
Stage 1 ran (`results/analysis.txt`). Gates G1-G3 pass. F1 porous in 6/6 rules
(a up by 0.19-0.29). V1 intermediate: early a 0.801, late a 0.759 (sd 0.061).
Neither dose prediction met.

### 2026-10-26 23:15 (+1300) · f1bd2c8 · surprise
F1. I expected the ant's memory to keep it compact without the wall; instead every
rule became nearly as porous as the memoryless walker. My registered prior was wrong.

### 2026-10-26 23:15 (+1300) · f1bd2c8 · interpretation
The fresh-ground rule is necessary in these six rules. The wall alone gets most of
the way (0.93 -> 0.76-0.80) but not to the ant's 0.59-0.70 within 2^27. Local a of V1
drifts down about 0.01 per octave, so slow convergence and a separate exponent are
both open. Alternatives not excluded: six rules from one class, finite windows.

### 2026-10-26 23:15 (+1300) · f1bd2c8 · decision
Register Stage 2 (V1 to 2^31, 16 seeds, rotor control) in README before running;
scoring in `scripts/analyse_stage2.py`, committed first.

### 2026-10-26 23:30 (+1300) · 3040a0b · observation
Stage 2 ran 23:14-23:18 NZDT (`results/stage2_analysis.txt`). S0 passes (rotor 0.677). V1 a(24..30) 0.732
(sd 0.021), beta 0.585; local-a slope -0.0045 per octave, bootstrap 95% [-0.0124, +0.0031]. Frozen reading
"separate exponent", 0.002 over threshold. The 16 runs sharing seeds with Stage 1 reproduce its rows exactly for k <= 27.

### 2026-10-26 23:30 (+1300) · 3040a0b · interpretation
Stage 2 is unresolved in substance, whatever the frozen label says: the threshold margin is a tenth of the seed sd and
the trend interval holds both readings. The firm result is F1 (wall necessary in 6/6 rules).

### 2026-10-26 23:30 (+1300) · 3040a0b · dead-end
F1 recorded as `NR-20261026-wall-vs-memory-no-wall-porous` (empirical; exactly the 48 tested specs; evidence
3040a0b). Reopen on a walker semantics correction, a longer horizon returning these specs to 2/3, or for other rules.
No signature for V1 (unresolved) or the dose arms (failed contrast predictions, not a dead end).

### 2026-10-26 23:30 (+1300) · 3040a0b · decision
Write-up: README outcome, `notebook.ipynb` (built by `scripts/build_notebook.py`, executed from a clean kernel, reads
committed results only), figure `scripts/figure.py`, notes (cube-root-hypothesis update, Q30/Q31), ACTIVE backlog,
atlas filing under cube-root-growth, blog post and homepage card. Stop here; follow-ups (Q30 EF dose curve, Q31 local-time
discrepancy, longer V1) need new registrations.

### 2026-10-27 20:45 (+1300) · 15d41a9 · intent
Respond to the external review of PR 19. Plan: narrow claims; correct the window label; fix the oracle's
float-vs-floor noise comparison; make reproduction really re-simulate; add post hoc checks; register follow-ups
(forced L, mediator statistics, convergence extension, colour-zero noise) without running them.

### 2026-10-27 20:50 (+1300) · 15d41a9 · observation
Reviewer's numbers reproduce (`results/posthoc_review.txt`, new): 39 of 48 F1 runs individually meet the porous
thresholds (7, 6, 6, 8, 7, 5 of 8 per rule); V1 a(24..30) = 0.7320, seed-level bootstrap 95% [0.722, 0.742]; refit at
k = 27..31 gives 0.7170; mean 10% shifts +0.047 (revisit) and +0.028 (fresh). `k` is log2 of the window END
(`csv_rows`), so the early fit k = 12..22 ends at 2^22.

### 2026-10-27 20:55 (+1300) · 15d41a9 · deviation
Earlier text (README "What this cannot show", notebook caveat, pruning-entry confound) said the early window ends at
2^23. Wrong by one octave; corrected in the README addendum and the pruning-entry amendment. The frozen fit
(k = 12..22) is unchanged; no score changes.

### 2026-10-27 21:05 (+1300) · 15d41a9 · decision
Oracle: specified integer semantics (`walkers::noise_threshold32`, noisy iff low32 < floor(eps * 2^32)); the sparse
reference restates it independently; `noise_threshold_boundary_is_strict_integer_comparison` aims the first SplitMix64
draw (via an inverse of `mix64`) at threshold - 1, threshold, threshold + 1. Production behaviour unchanged (the
old expression was already `(eps * 2^32) as u64`, a floor for eps >= 0), so no result should move.

### 2026-10-27 21:20 (+1300) · 15d41a9 (7 tracked files modified) · observation
Fresh rerun of both stages into the gitignored `scratch/rerun` with the new `run.sh` / `run_stage2.sh` (fresh
`CARGO_TARGET_DIR`, 4 threads, ~3 + ~3 min): `verify.py --against results/` passes, `probe.csv` and `stage2_probe.csv`
are byte-identical to the committed ones, and `analyse.py` / `analyse_stage2.py` outputs are identical. So the
semantics change moved nothing, and the committed numbers regenerate. The rerun's binary hash is in
`scratch/rerun/*provenance.txt` (not committed: the build differs from the original only by the refactor).

### 2026-10-27 21:30 (+1300) · 15d41a9 · interpretation
Narrowed reading: first-departure turn randomisation disrupts compact growth in six sampled rules (condition means);
reflection as the mechanism is untested (F1 also breaks first-visit chirality and short-loop geometry); V1 is a
finite-window separation with window-dependent a (0.732 -> 0.717), unresolved asymptotically; 10% fresh noise left the
class unchanged but shifted a. Independent units: six rules (seeds shared).

### 2026-10-27 21:35 (+1300) · 15d41a9 · decision
Follow-ups F-a..F-d registered in the README addendum (item 9) with predictions, not run. Notes (Q32), pruning-entry
amendment 1, blog post/homepage/atlas/guide wording and `notebook.ipynb` updated to match.

### 2026-10-28 18:20 (+1300) · 4fd558b · intent
Session start. Owner asked for the next priority to be pursued. Plan: (1) fix and audit the hash-order bootstrap
bug (other experiment); (2) the boundary-access discriminating test, starting from this experiment's registered
follow-ups F-a..F-d.

### 2026-10-28 18:30 (+1300) · 4fd558b · surprise
While designing F-b: under any deterministic quarter-turn fresh policy a fresh run is at most 4 cells (four equal
turns close a 2x2 block onto the run's first, now departed, cell). So F-b's excursion length cannot vary among the
deterministic arms; it only separates F1 again. F-a's eight seeds are also moot: forced L is deterministic.

### 2026-10-28 18:35 (+1300) · 4fd558b · decision
Registered Stage 3 in the README before any code: `ft:RULE:T` for T in {R, L, U}, 6 rules, one run each, three
explanations (H-bound / H-chiral / H-match) with a reading table, a "stalled" class added before running, gates T0/T1.
F-b deferred with reason. Pruning preflight: no member entry; run. Priors H-bound 40%, H-chiral 30%, H-match 20%.

### 2026-10-28 19:00 (+1300) · feb6e2d · intent
T0 passed (`cargo test --release --locked --test fresh_turn`, 4 tests, 96 proptest cases per property, fixed seed
20261028). Specs, runner and scorer committed at `feb6e2d` before the run. Launching
`RAYON_NUM_THREADS=3 sh scripts/run_stage3.sh` (3 threads: an unrelated single-threaded audit is using one core).
