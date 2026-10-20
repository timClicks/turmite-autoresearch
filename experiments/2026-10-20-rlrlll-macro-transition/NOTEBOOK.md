# Lab notebook: RLRLLL column sweeper as a macro-transition

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-20 23:40 (+13:00) · ba38590 · intent
Start a proof-oriented track in parallel with the empirical programme, prompted by a proposal (from the project
owner) to turn simulated regularities into machine-checkable macro-transitions. First target: the RLRLLL column
sweeper, because the G1 note already shows a period-3 wake and a cycle time proportional to sweep height. Predictions
P1-P5 registered in README before any run here. This runs in a cloud container (4 cores), not on the WSL machine
where the 1e11 census holds all cores, so it does not compete with that job.

### 2026-10-20 23:40 (+13:00) · ba38590 · assumption
The steady phase reads only a bounded strip behind the front (P3). If false, no finite macrostate exists without
carrying the wake. Checked directly by the reach statistic W_k. Status: untested.
