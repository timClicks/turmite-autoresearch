# Lab notebook: loop surgery (causal test of H-loop)

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-16 21:00 (+13:00) · 9dce376 · intent
Scaffolded as the interventional follow-up to `../2026-10-kappa-square-loop/`, at the user's request for directories that let later researchers evaluate the predictions. Draft only: nothing is frozen or run. Purpose: observational P3 cannot rule out reverse causation (high boundary occupancy producing more loops), so suppress loops directly and compare to matched-rate noise and a non-loop shape control.

### 2026-10-16 21:01 (+13:00) · 9dce376 · assumption
(a) A loop-completing turn can be flipped without changing the ant's local environment in other ways that matter to kappa; this is false in general (the flipped step writes a different next heading and the cell colour still increments), so arm N and M controls matter more than arm S alone. (b) Matching arms on flip rate is enough to match "amount of perturbation"; it is not: flips at loop closures happen in a correlated, state-dependent way. Compare realised dynamics (new-cell rate, area growth exponent) across arms as well as kappa. Both untested.

### 2026-10-16 21:02 (+13:00) · 9dce376 · question
Is there a cleaner intervention than flipping turns, for example a rule-level edit that removes loops while holding the lead and area fixed? None found; a lead-k rule always loops on fresh cells by construction (P1), so lead and loop duration cannot be separated by rule edits alone. This is why the intervention acts on trajectories, not rules.

### 2026-10-16 20:56 (+13:00) · 9dce376 · deviation (corrects: timestamps of entries above)
The entries above carry times 20:55-21:02, written while the wall clock was at about 20:50-20:54, so some are stamped slightly in the future. Order is correct; treat the stamps as approximate. Also: the parent mutant probe run finished 20:53 (`../2026-10-kappa-leadrun-fresh/dumps/mutants.done` exists); `analyse_mutants.py` had not been run when this was written.

### 2026-10-19 21:35 (+13:00) · 51c3f83 · decision (closure; corrects nothing above)
Closed without running. The gate in README and HANDOFF was "run only if the parent's P2 holds". `../2026-10-kappa-square-loop/` ran its single analysis on 2026-10-16 (`results/analysis.txt`) and P2 FAILED (loop-step fraction by lead 1..6: 0.159, 0.184, 0.166, 0.179, 0.202, 0.257, not monotone; lead-colour 2x2 laps at most 1.6% of steps at lead 6). P3, P4, C1, C2, C3 failed too, and the parent's registered kill logic declares H-loop dead at this scale. So there is no loop-carried effect for surgery to remove: `LoopBreakAnt` was never written, the cohort was never drawn, S1-S4 were never frozen, and no data exist. The S1-S4 probabilities in the README are untested drafts, not predictions that failed. Not shown by the parent, and so not tested here: that loops of other shapes (period 6/8, mixed turns) or earlier loops are irrelevant; if a later experiment finds a loop-like mediator that survives its own observational tests, this design (surgery vs rate-matched noise vs non-loop-shape mirror) could be reopened in a new folder with fresh registration. Also kept from the 21:00 assumption entry: turn flips perturb more than loops, so any revival needs the N and M controls and a realised-dynamics comparison. No code, results or other folders were touched.

### 2026-10-19 (+13:00) · 8f4b978 · interpretation
Co-reading note appended at the 2026-10-19 merge (the entry corrects nothing above). `../2026-10-c-law-mechanism/` Stage 4 (registered before computation; Q1-Q4, P-1 held; re-run of 4a/4b at merge reproduced the numbers) shows the fixed-area lead-on-ln-kappa slope (+0.15) is reproduced by conditioning on the collider ln A22 = f(ln c, ln kappa) with no direct effect (null +0.145 [0.137, 0.153]; adding ln c gives +0.014 [-0.045, +0.062]). Read the interpretation and any 'causal at fixed area' wording above as superseded in part: association conditional on area, not evidence of a direct lead effect. Unexplained and still open: the S-arm drop (-0.198) and its confounding with flip direction. See notes/open-questions-hypotheses.md, Reconciliation 2026-10-19.
