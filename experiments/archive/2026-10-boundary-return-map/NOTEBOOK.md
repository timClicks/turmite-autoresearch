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


### 2026-10-21 07:10 (+13:00) · bd60f47 · intent
User pasted a proposal: boundary return operator R: B -> B, a compact Markov boundary state, and a diffusive derivation of L ~ t^(1/3). Plan: (1) no new data for the heuristic: it is the existing kappa identity; the diffusive version (E[T] ~ L^2) gives t^(1/4) and is contradicted by kappa ~ const (README, "Relation to the pasted proposal"); (2) test the return-map idea by colour intervention at boundary departures rather than by fitting state partitions, because in-sample ML closure cannot fail (first-passage lesson).

### 2026-10-21 07:30 (+13:00) · bd60f47 · decision
README registered (P1-P4, controls C1-C4) before any sampler run.

### 2026-10-21 07:50 (+13:00) · bd60f47 · deviation
Sampling changed before any pilot: stratified by baseline episode length with a live undo log (typical departures are T=1-2 and would have hidden the deep excursions that carry the time budget). Registered in README as "Sampling (revised 07:50)".

### 2026-10-21 08:05 (+13:00) · bd60f47 · observation
Smoke test (A0=4096, 1 rule, scratch/smoke, not data): C1b live_ok 100% on ant, rotor, rw; C2 rw ident=1 at every r; r=4096 ident=1 for all. Two instrument bugs found by these controls and fixed before the pilot: (a) the replay used the walker cloned at arrival, not departure (rw live_ok 2/24); (b) `ident` included arrival colour, which differs whenever a shuffled arrival cell has the same turn, making ident < unexposed. Deviation from README: `ident` is now (T, arrival cell, arrival heading); colour is still recorded (`c`). P2's E_r is computed with this definition.

### 2026-10-21 08:10 (+13:00) · bd60f47 · intent
Pilot: 12 rules x 2 seeds + rw:301, rotor:301-302; bands 32768 and 131072; K=16 per stratum, M=8, cap 2^20, board 4096; 2 threads (a 1e11 sweep is using the CPUs, so wall time here is not a measurement). Command in results/pilot.log header via scripts; binary built into ~/turmite-target-brm. Predictions P1-P4 are tested only on the confirmation cohort.

### 2026-10-21 08:40 (+13:00) · 67f7d03 · observation
Pilot (25/27 specs; RLRLLLL ineligible, step budget). Controls C1b 2851/2851, rw identical, null ICC 0.011+-0.019. Population G reaches 0.8 at r*~1-7; time-weighted at ~L. Details in README "Pilot results".

### 2026-10-21 09:00 (+13:00) · 67f7d03 · decision
Registered P5 (time-weighted reach) after seeing the pilot (so pilot-informed), kept P1-P4 unchanged, added radius 256, committed as 1998e7d before launching confirmation.

### 2026-10-21 09:40 (+13:00) · 1998e7d · observation
Confirmation 72/72. P1 falsified (median r*/L 0.096/0.053, gamma 0.12), P1-alt met on the population statistic, P2 met, P3 met (C2 only from the pilot), P4 met with the outcome-conditioning caveat, P5 met (median r*_t/L 1.16, gamma_t 0.99). `results/confirm_analysis.txt`, `confirm_p4.txt`.

### 2026-10-21 09:45 (+13:00) · 1998e7d · surprise
I expected (and registered) P1: global reach even in the population statistic. It failed: the typical excursion is local. The global dependence lives only in the time-weighted view. My prior was wrong about the typical case and the pilot-informed P5 was right only because the pilot had shown it.

### 2026-10-21 09:50 (+13:00) · 1998e7d · interpretation
Two-population picture: short loops with a local return map, and rare long excursions whose duration depends on structure out to O(L). Alternatives not excluded: (i) the time-weighted reach reflects a handful of structural gates, not diffuse structure; (ii) shuffle-induced highway-like or trapped configurations lengthen T in the replicas, inflating the reach; (iii) censoring at the 2^20 cap for deep excursions (not tabulated here: check cens fraction before citing).

### 2026-10-21 10:00 (+13:00) · 4a34642 · observation
Cap check for alternative (iii): 317 of 660160 replicas (0.05%) censored at 2^20; 0 of 8252 baselines. Censoring does not drive the time-weighted reach. Alternative (ii) (shuffle creating long trapped replicas) is not excluded; its signature would be replica T far above baseline T at small r.
