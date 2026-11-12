# Lab notebook: leak handedness on a cohort

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-11-12 08:55 (+1300) · 251100a · intent
Daily session. Every open PR (#30-#33, #35, #37) waits on the owner's review or design choices, so I picked an unblocked
priority-1 item that needs none of them: Q42, the leak titration's handedness lead (forced-L base appeared to need more leak
than forced R; 3 rules). This decides whether the base-turn/colour-0 match matters for compactness beyond the fresh-run bound.

### 2026-11-12 09:00 (+1300) · 251100a · observation
Calibration input, not target data: median within-rule per-seed sd of early a in the committed leak-titration runs is about
0.025 (EF 0.1-0.9, both arms). First draft of `scripts/calibrate.py` drew the two arms' EF = 1 levels independently and averaged
them, which inflates per-rule Lambda noise to sd ~0.23 (bug in the synthetic model, not the rule). Fixed to a shared EF = 1 level:
true lag 0 gives "no lag" 95% at sd 0.025, false "lag" 0.0%; lag 0.10 is called 100%. `results/calibration.txt`.

### 2026-11-12 09:05 (+1300) · 251100a · decision
Pruning preflight at `251100a`: 7 entries read; candidates `NR-20261026-wall-vs-memory-no-wall-porous` and
`NR-20261028-wall-vs-memory-bounded-random-fresh-compact`; no spec is a member (different rules / bounded sets). Run.
Registered cohorts (C 77, E 9, 14 excluded with reasons), gates G1-G2, predictions P1-P2 and priors in the README before writing
`run.sh` or `analyse.py`. Both arms through `fs:` so the encoding is identical. Budget ~2700 runs, stop at 2 h.

### 2026-11-12 09:00 (+1300) · add989a · decision
Committed `run.sh` and `analyse.py` while the probe was running and before reading any output. Deviation (minor): the run
started from `19e4aa0`, before `run.sh` itself was committed, so `provenance.txt` records the registration commit. Code oracle
`cargo test --release --locked --test fresh_set`: 4/4 passed. Toolchain is rustc 1.99.1 (Stage 3b used 1.97.0); G1 tests that.

### 2026-11-12 09:21 (+1300) · add989a · observation
Run finished (2708 specs, 21.5 min, 3 threads). `analyse.py`: G1 172/172 identical, G2 pass (mean d -0.0015), 77/77 scoreable.
P1 UNRESOLVED: median Lambda +0.023, 95% [-0.158, +0.186]. P2 FAIL: E porous 9/36 (needed >= 18), C 0/308.

### 2026-11-12 09:22 (+1300) · add989a · surprise
The P1 interval is eight times wider than the calibration's. Lambda's spread across rules is sd 0.38 against ~0.05 seed noise:
the base-turn handedness matters a lot for most rules, but with a rule-dependent sign. My calibration assumed one shared lag
with spread 0.05, so the registered median test was the wrong instrument for this. Recorded as a design defect, not repaired.

### 2026-11-12 09:23 (+1300) · add989a · interpretation
POST HOC (`scripts/posthoc.py`, written after seeing P1): Lambda correlates with the fraction of R letters (Spearman +0.40);
all 7 `RRRR...` rules lag under base L, 12/14 `RLLL...` rules lag under base R. Reading: the leak does less damage when the forced
fresh turn is the rule's minority turn. Confidence low: one look among several, composition and prefix confounded, cohort B only.
The three P2 collapse rules all start `RLL`, consistent with it. Not registered; needs a per-rule sign prediction on new rules.

### 2026-11-12 09:23 (+1300) · add989a · decision
No dead-end signature (unresolved and failed-generalisation, not a controlled null). Moved the folder to `active/` with
`relocate.py` (map `experiments/_migration/2026-11-12-leak-handedness-cohort.tsv`); `analyse.py` re-run from the new path is
byte-identical, also under `PYTHONHASHSEED=7`. Next: notebook.ipynb, Q42 update, ACTIVE pointer, atlas and guide, blog post.

### 2026-11-12 09:25 (+1300) · 81f5264 · deviation
corrects: 2026-11-12 09:05 decision. The registration time written in that entry and in the README ("09:05") was entered ahead
of the clock; the registration commit `19e4aa0` is dated 08:58:54 (+1300) and the probe started at 08:59:16 (+1300)
(`provenance.txt`, 19:59:16Z). The order registration -> run holds; the stated minute was wrong. README carries a dated note.
