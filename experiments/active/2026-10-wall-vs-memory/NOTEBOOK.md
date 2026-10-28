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

### 2026-10-28 18:26 (+1300) · 3164e1a · observation
Stage 3 ran in 10 s (18 runs). T1 6/6. L: compact 4/6, two forced-L runs (`RLRLLRRLRLR`, `RLRLLRRRRRRR`) are one
byte-identical diagonal highway, escaping by 2^17. U: compact 5/6, `RRRRLLLLLLLR:U` a 3-wide straight highway by 2^15.
All complete windows compact. Registered reading: none (L split). F-a side prediction failed (3/6); U's held (4/6).

### 2026-10-28 18:40 (+1300) · 3164e1a · surprise
I did not foresee early highways; the registration only named a "stalled" class. The scorer (committed first)
counts them as not compact, which is right for a highway, but the class was unregistered. Also unforeseen: U's
late a is tighter across rules (0.692, sd 0.012, n = 5) than the ants' (0.665, sd 0.039). Post hoc.

### 2026-10-28 18:45 (+1300) · 3164e1a · interpretation
Selection confound: the cohort is compact non-highway *under R*, so only the R arm is filtered against highways.
Census base rate of onsets < 4096 steps is 7% (268/3963, n = 8..12), so 2 independent early highways in 12 runs
is unremarkable. Reading per arm: U compact contradicts H-chiral and H-match; escapes contradict the strong H-bound.
Surviving statement: bounded fresh runs are compatible with compact growth and need neither chirality nor the
colour-0 match. Six rules only.

### 2026-10-28 18:50 (+1300) · 3164e1a · decision
Register Stage 3b: all three arms on a new cohort of core-class rules, with escapes named as a class and scored
separately from the compact/non-compact question, so the reading can be applied with power. Cheap (seconds per run).

### 2026-10-28 19:10 (+1300) · ad29f50 · decision
Registered Stage 3b in the README (100 new core-class rules, arms R/L/U, escape class named, gate T2, reading on
f = compact / non-escape, sd-ratio prediction from the Stage 3 post hoc observation). Cohort draw is byte-identical
across two processes (rules sorted before and after the draw). Scorer tested only on synthetic input (Stage 3 rows
relabelled onto the new names), not on any Stage 3b output. Committing, then running.

### 2026-10-28 18:33 (+1300) · 383fe4c · observation
Stage 3b ran (300 runs, 3 min 16 s). T2 passes. f_L 0.857 [0.771, 0.915] (78/91), f_U 1.000 [0.943, 1.000] (63/63);
escapes L 9, U 37; porous in no arm. Registered reading: unresolved. U escape-rate prediction failed (37% vs 2-20%).
sd-ratio prediction held (0.725 [0.556, 0.958]); U late a 0.687 held.

### 2026-10-28 18:40 (+1300) · 383fe4c · surprise
All 13 non-compact, non-escape L runs are ordered fillers: A/t constant (1/10, 1/8, 1/6, 1/4, ...), mostly exact
squares. The forced-L policy turns some chaotic rules into square-spiral fillers. Post hoc check of A/t, w/h and
perimeter / 2(w + h) on the last three windows.

### 2026-10-28 18:45 (+1300) · 383fe4c · interpretation
No porous run among 300 bounded-policy walkers. Candidate dichotomy: bounded fresh runs and no crystallisation give
compact growth. The confound left in Stage 1 is that F1's fresh turns are both random and unbounded. A random but
bounded policy separates them: R and U mixed at random is bounded (a U returns at once, R closes a 2x2 block within 4).

### 2026-10-28 19:30 (+1300) · 9f8a06a · decision
Registered Stage 3c (random but bounded fresh turns RU/LU vs unbounded RLU; F1 identity gate). Priors H-bound 65%,
H-random 25%. Added a "filler" class before running, from the Stage 3b post hoc finding.

### 2026-10-28 19:50 (+1300) · 9fbcbf2 · intent
T0' passes (`cargo test --release --locked --test fresh_set`: sparse reference, RL = F1, RU/LU bound, RLU long runs;
hybrid_walker and fresh_turn still pass). Specs (350), runner and scorer committed before the run; the scorer was
checked on synthetic input only (F1 and Stage 3b rows relabelled), where it reproduces Stage 1's F1 numbers.

### 2026-10-28 19:45 (+1300) · 3d13c18 · observation
Stage 3c ran (350 runs, 4 min 16 s). T3 6/6. Bounded random: A RU 47/48 compact, LU 42/48, B RU 86/100; porous 1 of
196. Unbounded random RLU: compact 2/148, porous 73/148. Registered reading unresolved in both cohorts (LU 0.875, B RU
0.860 under 0.90; A RLU p 0.375 under 0.50). H-random's prediction (f <= 0.50) is far off. RLU p >= 0.7 failed.

### 2026-10-28 19:50 (+1300) · 3d13c18 · deviation
The run's provenance says 2 dirty tracked files: my uncommitted fixes to `a7_census.py` and `a5_home_types.py` (other
experiments, Python only). The probe binary does not read them; its sources were committed at `3d13c18`.

### 2026-10-28 19:55 (+1300) · 3d13c18 · interpretation
The bound on fresh runs is the strongest separator found: bounded policies 0 + 1 porous of 514 runs, unbounded 73/148
(+ F1 39/48). Bounded randomness shifts early a by +0.056 (sd 0.040) in cohort B: compact but not the ant. My
thresholds (0.90, 0.50, 0.70) were too sharp for the near-edge intermediates; I do not move them after the fact.

### 2026-10-28 18:55 (+1300) · 367df8f · deviation
My hand-written entry times from 18:30 onwards ran ahead of the clock (entries stamped 19:10-19:55 were written between
18:28 and 18:44; the clock reads 18:51 as I write this). Git commit times are authoritative; the README has a table
mapping each registration and run to its commit or provenance time. The order registration -> code -> run holds for
Stages 3, 3b and 3c. Earlier entries are left as written.

### 2026-10-28 (+1300) · merge of origin/main · deviation
Merging main brought in Q34-Q37 (cube-root-routes proposals, numbered on main first). My questions Q34 and Q35 from
2026-10-28 are renumbered **Q38** (forced turns crystallise rules) and **Q39** (bounded regime near 0.70); Q33 is unchanged.
References in notes, the homepage and the notebook are updated; links pinned at `df2e5bb` still show the old numbers.
