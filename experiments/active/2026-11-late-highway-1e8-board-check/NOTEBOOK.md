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

### 2026-11-09 09:11 (+13:00) · 214377a · decision
Registration committed and pushed (`214377a`) before any recheck. Launched `scripts/recheck.sh` (background) and
`cargo test --release --locked` in parallel.

### 2026-11-09 09:13 (+13:00) · 214377a · observation
Recheck finished (tiled 65536: 09:11:01-09:11:22; dense 32768: to 09:12:58; binary sha256 1ecc3e8d...). `scripts/classify.py`
-> `results/classify.txt`: control RRLRLR confirmed on both boards (tiled 65536 equals the earlier dense 65536 row); 11 of 12
census rules confirmed on both boards; RLLRRLRLR stops at budget 922,854,955 with no highway (footprint 12831 x 11947, same
on both boards). cargo test: 227 passed, 0 failed.

### 2026-11-09 09:13 (+13:00) · 214377a · interpretation
P1 and P2 held as registered. The decade's count is 11/854 (1.29%), or 10/854 by onset binning. Q19's flat reading is
unaffected (Fisher p = 0.33 vs the next decade). The one artefact was already flagged by the 2026-10 `confirm` run; the
error was in the bookkeeping that ignored it.

### 2026-11-09 09:14 (+13:00) · 214377a · observation
Registered exploratory run, RLLRRLRLR to 1e10 on tiled 65536: escapes at 2,118,888,449, period 4, drift (-2, 0), onset
2,118,845,739 (third different onset on a third board). `results/explore/RLLRRLRLR_1e10_65536.csv`.

### 2026-11-09 09:15 (+13:00) · 214377a · deviation
Unregistered exploratory follow-up after seeing that escape: same rule on tiled 262144 and 1048576 to 1e10 (~50 s each).
Neither escapes; identical footprint 84683 x 83799 and tail_period 4 at the budget. Not scored; counts unchanged.

### 2026-11-09 09:16 (+13:00) · 00fee4a · surprise
RLLRRLRLR looks like a ray emitter: period-4 speed-1/2 straight runs that end, read as a highway only when one hits the
board edge. Bounding box 12.8k at 9.2e8 and 84.7k at 1e10 steps (apparent exponent ~0.8 from two points): fast, not a
cube-root blob. Question (not registered): what do the runs travel over and why do they stop? Same class as RLLLRLRRR?

### 2026-11-09 09:19 (+13:00) · 1892db7 · decision
Closing the session. Notebook written and executed (`scripts/build_notebook.py`; agrees with README). Notes updated:
Q19 update (open-questions), correction lines in `notes/frontier-2026-10-13-results.md` and `notes/frontier-results.md`,
ACTIVE.md open item removed. Atlas: evidence, open question, turn, reviewed date; guide row in `blog/experiment-guides.tsv`;
blog post 2026-11-09. Not changed (left for the owner): the paper sentence "1.4% in (10^8, 10^9]"
(`research-outputs/scholarly-articles/cube-root-growth/main.typ`), the fourth-decade registration's 12/854 figure, and the
archived `highway_stats.txt` (generated data). The experiment stays in `active/` until the owner reviews.
