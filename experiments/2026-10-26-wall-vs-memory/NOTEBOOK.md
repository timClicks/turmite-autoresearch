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
