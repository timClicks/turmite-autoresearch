# Lab notebook: boundary excursion-duration collapse (stage 1)

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation.

### 2026-10-27 20:30 NZDT · 5b96f68 · intent
Stage-1 experiment for P-C / Q32 (diffusive vs sweep excursion-duration collapse)
from `notes/cube-root-routes-2026-10-26.md` on PR #18. Bias to prior work: reuse
probe boundary definition, exposure-classes check-mode style, first-passage's
calibrator list (mf / rotor / rw), and T1's excursion episode definition; avoid
the failed parametric (theta, z) tail fit (C6). Register definitions, scores and
stop gates before any measurement. No confirmation in this experiment.

### 2026-10-27 20:30 NZDT · 5b96f68 · decision
Pruning preflight at index revision `5b96f680ba25ff898fc5ed91d2c33a43d6713233`.
Queries: `rg -n -i -e 'return|excursion|tail|first-passage|boundary|kappa' notes/pruning-index/entries`
plus full read of the three entry titles/claims. Candidates:
`NR-20261022-additive-laws-order-blind`, `NR-20261025-kappa-exposure-classes-exposed-edge`,
`NR-20261025-crawler-window-single-letter` — all different objectives/observables.
Decision: **RUN**. Budget: < 2 CPU-hours, board 8192, max_log2 24, 4 threads.
Stop if C1 (rw→D) or C2 (mf→L-scaling) fails.

### 2026-10-27 20:30 NZDT · 5b96f68 · assumption
Window-end L = A/P is an adequate scale for octave-window collapse at stage 1
(quasi-static within a window). False if within-window L drift, or completion-window
attribution of long excursions, destroys RW's L^2 collapse under the frozen score.
Status: untested (calibration will test).

### 2026-10-27 20:30 NZDT · 5b96f68 · assumption
Mean-field interior sojourns behave as approximately geometric with mean ~ L, so
Score(L) beats Score(L^2) by the 0.75 margin. False if MF's neighbour-step
correlation or growing P/A within a window breaks L-collapse at these sizes.
Status: untested.

### 2026-10-27 20:31 NZDT · 5b96f68 · question
Does the rotor's excursion-duration shape prefer L or L^2 collapse at accessible
sizes, or neither? P-C left this as a measured calibrator; T1 and FLP/Bou-Rabee
arguments suggest sweep-like structure, but that is not registered here.
