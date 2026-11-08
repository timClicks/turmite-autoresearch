# Lab notebook: Late-highway board check for the (1e8, 1e9] decade

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-11-09 09:08 (+13:00) · 6fba1c8 · intent
Close the ACTIVE.md item "apply the board-independence check to the 1e8/1e9 census" (priority 2, regime validation).
Re-run the 12 late highways found by the 1e9 rerun of the census on a 65536 board, with the B2 criterion of
`2026-10-late-highway-board-check`. Informs the (1e8, 1e9] term of the per-decade yield (Q19).

### 2026-11-09 09:09 (+13:00) · 6fba1c8 · decision
Pruning preflight at `6fba1c80227eebfcd3f27fee78087dd6c973e0e8`: `rg --files notes/pruning-index/entries` (7 entries);
`rg -n -i -e highway -e board -e onset -e filler -e census notes/pruning-index/entries`; `rg -l -F -w RULE` for each of the
13 rules. No matching signature (hits only in NR-20261022-additive-laws-order-blind, which excludes highway questions, and
NR-20261025-kappa-exposure-classes-exposed-edge, another objective). Decision: run (deliberate replication). Budget well
under one core-hour.

### 2026-11-09 09:10 (+13:00) · 6fba1c8 · surprise
The decade already had a two-board check: `experiments/archive/2026-10-census-sweeps/results/confirmed_1B.csv` (confirm on
8192 and 16384) confirms 11 of the 12 and marks `RLLRRLRLR` (period 4, drift (-2, 0)) unconfirmed, onset 763,443,858 vs
822,854,955. The 12/854 = 1.41% yield used in Q19 nevertheless counts it. So the decade's count is probably already wrong by
one, and the recheck is mainly a test on a larger board (the 8192 board is barely bigger than the ~8000-wide territories).

### 2026-11-09 09:10 (+13:00) · 6fba1c8 · assumption
The tiled backend gives byte-identical CSV to dense at 65536 (tests/tiled.rs and DESIGN.md). Check: control RRLRLR must
reproduce the dense 65536 row in the earlier experiment; the secondary dense 32768 run gives a second backend. Status: untested
on this machine at this board size.

### 2026-11-09 09:10 (+13:00) · 6fba1c8 · deviation
Free RAM is ~2.5 GB (15 GB total, ~13 GB used outside this job), too little for dense 65536 (4.3 GB). Primary run uses
`TURMITE_GRID=tiled` (unlimited cache, tile 2^6) instead of dense as in B2. Registered in the README before running.
Throughput check on a rule outside the study (`echo RLR | ... sweep_lean - - 200000000 65536`, tiled): 2e8 steps in 0.85 s.
