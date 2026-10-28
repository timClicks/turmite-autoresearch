# Lab notebook: <experiment title>

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · intent
What I am about to do, why, and which decision it informs.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · assumption
Statement. How it could be checked / what would show it false. Status: untested.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · observation
Fact, with the command and file that produced it.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · interpretation
What I think it means; confidence; the alternative explanations I have not excluded.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · decision
Pruning preflight: index revision, exact queries, candidate signature IDs (or no
matches), scope comparison, run/skip/reopen decision and compute budget. Repeat
when scope changes. See `notes/pruning-index/README.md`.

### YYYY-MM-DD HH:MM (+TZ) · <git short hash> · dead-end
Criterion tested, evidence commit, limits, shared signature ID or reason no
signature is warranted, and what would reopen the question. Append corrections.

### 2026-10-25 · a25ab35 · intent
User: analysis of prefixes may be amenable to formal methods. Aim: exact statement of how long rules sharing a prefix share a trajectory, a machine-checked step proof, and an application to the Q19 data. Registered before running (commit 20291ed).

### 2026-10-25 · 20291ed · assumption
Colour c is first read on a cell's (c+1)-th visit, so divergence time is a visit-count record, a function of the common prefix only. Status: confirmed by R1.

### 2026-10-25 · 20291ed · deviation
First z3 run: NC1 returned `unknown`, not `sat`, because quantified range premises prevent a model. The control proved nothing. Rewrote the controls quantifier-free with twins (prove_controls.py) before using any lemma result. Registered S2 amended in the README addendum before the rewritten controls ran.

### 2026-10-25 · 20291ed · decision
Unified the three registered lemmas into (i)-(iii) after noticing W > F_c always. Registered as an addendum before running R1. Not a post-hoc fit.

### 2026-10-25 · 20291ed · surprise
Test passed first time. Checked that it was not vacuous: branch tally (7,761 exact / 152 repeated / 88 wrap-bound) and two manual mutants (one step late; strict wrap bound) both fail it. The strict mutant showed RL vs RLR differ exactly at the wrapped read (step 17).

### 2026-10-25 · 20291ed · observation
R2 FAILED: median F_c of the 702 survivors 5, 9, 17, 29, 33, 41, 53, 57, 73 for c = 1..9; slope 1.33 (registered 2.5-3.5). Max F_(n-1) = 389, max wrapped read 1009. My analogy to the cube-root law was wrong.

### 2026-10-25 · 20291ed · observation
R3: 42 pairs in the 21 equal-box groups all separate by step 45. R4: all 51 equal-onset late-highway pairs (exactly the 25 board fillers) separate within 205 steps (46 by lemma, 5 by lockstep run). Registered R4 prediction failed: it was the notes' shared-trajectory reading that was wrong.

### 2026-10-25 · 5a9da7d · interpretation
The lemma is exact but nearly useless as a sharing device: every letter of every length <= 10 rule acts within ~10^3 steps. It also kills a causal-horizon account of the kappa prefix effects. Doubts: only length <= 10; the F_c bound is observed, not proved; the z3 part proves one-step obligations only; the outer induction is not mechanised.

### 2026-10-25 · 5a9da7d · question
Why do rotations of a rule (19 of 42 equal-box pairs) reach the same bounding box when their trajectories separate within 45 steps? Rotation = same rule on a uniform background of non-zero colour. See Q25.

### 2026-10-25 · 1b7e996 · observation
corrects: the 2026-10-25 R4 results text in README. 205 steps against onsets of 4.3e9-1.3e10 is about seven orders of magnitude (not nine), and the largest class (i) bound is 105 (109 is a class (iii) wrapped-read bound). README text fixed; no data or code touched.

### 2026-10-25 · 1036678 · observation
corrects: wording in the README results and the appended notes bullet. (1) The 25 filler onsets are 25 distinct exact values clustered within ~1e-4 relative (e.g. 4293231098 .. 4294017917); none is exactly equal to another. "Equal onset" in my text means "within my 1e-4 tolerance". Exactly shared trajectories would give identical onsets, so this independently supports the refutation, but my "identical" was loose. (2) `notes/frontier-results.md` stated the shared-prefix reading only as a hedged hypothesis ("not verified by a trajectory comparison; open question"); the lockstep runs are that comparison, so it is a test of the hypothesis, not a refutation of an established claim. `notes/frontier-2026-10-13-results.md` (B5 extension) states it as fact with "identical" onsets, which the exact values do not support. (3) The causal-horizon account of kappa that I called refuted was my own construction, not a position in the notes; what is shown is only that every letter of the 702 length <= 10 survivors acts by step ~1000.
