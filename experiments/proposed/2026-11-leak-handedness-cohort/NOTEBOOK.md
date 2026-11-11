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
