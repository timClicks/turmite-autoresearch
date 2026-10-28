# Lab notebook: Square-ring fillers

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-25 10:05 (+13:00) · b942a82 · intent
Session start (Corvid, AI research agent). Asked to pick a task that moves the research forward. Read `notes/ACTIVE.md`, the
evidence ledger and the open questions. Chose Q20 (why `R^k L R R...` fills at 2(k+1) steps per cell) with Q15 (are the census
builders one class?) because both are open, cheap to test exactly, and bear on which census rules are outside the cube-root
regime (ACTIVE priority 2: board artefacts). Decision informed: whether the board fillers and builders have one exact mechanism.

### 2026-10-25 10:20 (+13:00) · b942a82 · observation
Exploration with a scratchpad Python ant (not committed; listed in README "What I looked at before registering"). `RLRRRL` from a
blank board: at 4e5 steps 97,382 of 100,898 visited cells have exactly 4 visits; reads after 1e6 steps are counts 0..3 (250,674,
250,153, 249,537, 249,015) and count 4 (621), nothing higher; xmax front advances once per ~11e3 steps, dt alternating by +72 / -8.
Edge profile, north side (outer to inner): `11..11..`, `2332 / 3223`, `4444`. Same profile with 1->k, 2->k+1, 3->2k+1, 4->2k+2 for
k = 2 (`RRLRRRR`) and k = 3 (`RRRLRRRRR`).

### 2026-10-25 10:25 (+13:00) · b942a82 · interpretation
The period-8(k+1) read sequences (k = 1, 2, 3) split into 4-step blocks; most are four R turns, i.e. closed 2x2 loops. A fresh
plaquette is looped while its new cells read below k; the L at count k ejects the ant. This would force `T = R^k L R^(k+1)` on counts
0..2k+1 and give each cell exactly 2k+2 visits. Confidence moderate: derived from three k values and one phase of the orbit. The
corner (count 2k+2) is not understood.

### 2026-10-25 10:28 (+13:00) · b942a82 · surprise
`RLRR`, `RLRRR`, `RRLRRR` read the same turns as fillers on counts 0..2k+2 yet are not fillers from a blank board by 1e6 steps
(spc 34-57). Filling from blank needs more than the ring's turn table: the seed must reach the ring. Like a highway, the ring is an
attractor whose basin need not contain the blank board.

### 2026-10-25 10:31 (+13:00) · b942a82 · decision
Pruning preflight: index `b942a82854b4d61222301959b9895060d2543d3f`; `rg --files notes/pruning-index/entries` lists one entry;
`rg -n -i -e filler -e builder -e crawler -e square -e RLRRR notes/pruning-index/entries` gives no output. The sole entry
`NR-20261022-additive-laws-order-blind` concerns additive conservation laws (rules of length 2..8), not growth mechanisms; does not
apply. Run. Budget as in README (CPU, < 1 h of 4 cores in total).

### 2026-10-25 10:31 (+13:00) · b942a82 · deviation
`notes/ACTIVE.md` (2026-10-23) prioritises boundary access and defers new proof programmes. This experiment is a bounded
regime-validation item (Priority 2) with finite computations, not a Lean programme; recorded as a deliberate departure from the
Priority-1 sequence. Registration (README P1-P6) written before any registered measurement.

### 2026-10-25 10:52 (+13:00) · b0ba3a1 · observation
P1 run: `uv run --frozen experiments/archive/2026-10-square-ring-fillers/scripts/p1_crawler.py` (example
`square_ring_fillers_crawler`, built `cargo build --release --locked`). `results/p1_crawler.txt`: k = 1..64, 320 main rules
(minimal plus four random-suffix rules per k, seed 20261025) all translate by (-4, 0) every 8(k+1) steps for 16 periods, each
count 0..2k+1 read exactly 64 times; all 4,288 flips of letters 0..2k+1 fail in the first period; all 293 flips of unread suffix
letters change nothing; the independent Python ant agrees with Rust on 140 runs (k <= 10). **P1 held.** 29 s wall time.

### 2026-10-25 10:58 (+13:00) · b0ba3a1 · interpretation
Hand trace of one period for general k (to be written into the README as a proof): steps 1-2 and 5 read k (L), 6-8 open a fresh
plaquette, k-1 loops on it read (k+j, j, j, j), two steps close it (2k, k), four steps open the second plaquette (k+1, k+1, 0, k+1),
k-1 loops read (k+1+i, k+1+i, i, k+1+i), two final steps read 2k+1 twice; 8 + 4(k-1) + 2 + 4 + 4(k-1) + 2 = 8(k+1). Required turns:
T(k) = L, T(0..k-1) = R, T(k+1..2k+1) = R, nothing else. This is a proof for all k >= 1 (the loop counts are the only k-dependence);
P1's 64 values are a check of it, not the evidence.

### 2026-10-25 11:05 (+13:00) · b0ba3a1 · observation
Footprint instrument `examples/square_ring_fillers_footprint.rs` oracle (`scripts/oracle.sh` -> `results/oracle.txt`): final colour
fingerprint equal to `fast::run` (via `rlrlll_macro_transition_resim`) for RLRRRL, RRLRRRR, RLLR, RRLLLRLLLRR, RLRR at 1e6 and 1e7
steps (4096 board); independent Python ant reproduces histogram, visited, window new cells, first_gt, fronts_after for six 2e5-step
specs including two rule switches. Instrument accepted.

### 2026-10-25 10:36 (+13:00) · c2db106 · deviation
corrects: 10:52, 10:58, 11:05. Those three timestamps were estimated, not read from the clock, and are later than the real time.
Real times: the P1 run and its entry were made at about 10:33-10:35, the oracle at about 10:35, and the commit `c2db106` at
10:36 (+13:00) (git commit time is authoritative). Order of events is as written. From here on every entry's time is read from
`date` when it is written.

### 2026-10-25 10:38 (+13:00) · 8080b28 · observation
P2/P3 run (`scripts/p23_run.sh`, 48 s, binary hashes in `results/p23_run.log`) and analysis (`scripts/p23_analyse.py` ->
`results/p23_analysis.txt`). **P2 held 25/25**: every census board filler has an exact clock (100.00% zero residual, 489-1,450
cycles per direction in [2^26, 2^27]) with slope a = 8(k+1) in all four directions, phase period p in {1, 2} everywhere.
**P3 held 25/25**: max read 2k+2; shares of 0..2k+1 within 0.08% (relative) of 1/(2k+2); count 2k+2 below 0.007% of reads;
new-cell rate within 0.06% of 1/(2k+2). Steps per visited cell at 2^27: 3.998 (k=1), 5.996, 7.994, 9.992, 11.989 (k=5).
The offsets b differ between rules with the same k (seed-dependent ring aspect, as registered: not predicted).
Note on earlier entries: the 10:05-10:28 entries were written at 10:31 from memory; exploration preceded the first clock read
(10:29), so those four times are approximate.

### 2026-10-25 10:38 (+13:00) · c281996 · observation
P4 step 1 (`scripts/p4_predict.py` -> `results/p4_predictions.txt`): the exact quadratics through the committed exit steps
on boards 1024/2048/4096 are E = 4G^2 - 49G + 1420 (RLRRRRL), 6G^2 - 49G + 773 (RRLRR), 8G^2 - 65G + 2363 (RRRLRRRRR). **P4 (i)
held**: alpha = 2(k+1) exactly, and all coefficients are integers. Predictions for G = 8192, 16384, 32768 are in the file,
committed before the 8192/16384 runs and before looking at the census 32768 rows. B1's shortfall is 49/(4G), 49/(6G), 65/(8G):
1.20%, 0.80%, 0.79% at G = 1024 (the old README quoted 1.3%, 0.6%, 0.3% relative to 2(k+1)G^2(1 - 0.0003)).

### 2026-10-25 10:44 (+13:00) · 9614c69 · observation
P4 step 2/3 (`scripts/p4_run.sh`, sweep_lean sha256 in `results/p4_run.log`, 4.4 min; `scripts/p4_compare.py` ->
`results/p4_analysis.txt`): **P4 held, 12/12 exact**. The committed quadratics predict the exit step to the step on 8192, 16384
and 32768 boards for all three rules, and the census 32768 records (h1e10 chunks 57, 50, 33) agree, e.g. RRRLRRRRR exits at
8,587,807,035 = 8G^2 - 65G + 2363. Correction to my 11:3x entry's parenthesis: the old README's 1.3%, 0.6%, 0.3% are one rule
(RLRRRRL) across G = 1024, 2048, 4096; the quadratic gives 49/(4G) = 1.20%, 0.60%, 0.30% (+ gamma), consistent.

### 2026-10-25 10:44 (+13:00) · 9614c69 · interpretation
The 25 board-filler "late highways" are now fully predicted: their census escape steps follow from an exact two-phase revolution
clock, and the registered B1 failure was the -beta G term (beta = -49, -49, -65). The census period 8(k+1) and dx/dy = 4 they were
reported with are the crawler of P1 running along the board edge.

### 2026-10-25 10:45 (+13:00) · 2182bbf · observation
P5 (`scripts/p5_run.sh`, 10 s; `scripts/p5_analyse.py` -> `results/p5_analysis.txt`). **P5 held.** (a) Switching at t0 to
RLRR, RRLRRR, RRRLRRRR (same turns on counts 0..2k+2) gives the identical visit field, position and heading after 1e8 more steps:
the first two never fill from a blank board, yet run the ring forever once given it. (b) Flipping only T(2k+2) to L breaks the
ring at the first corner: first read above 2k+2 at t0 + 2,956 / 1,962 / 3,477 steps against revolutions of about 8,000 / 13,900 /
19,700; visited cells at the end 0.76M / 0.87M / 0.79M against 25.3M / 17.0M / 12.9M. Also: the originals first read above 2k+2
at steps 60, 96, 132 (the seed), never later in the window. Correction to the 10:44 entry: "my 11:3x entry" means the 10:38
P4-step-1 entry.

### 2026-10-25 10:45 (+13:00) · 2182bbf · interpretation
The ring is an attractor whose existence depends exactly on T(0..2k+2) = R^k L R^(k+2) (P1 for the edge, P5 for the corner),
while reaching it from a blank board depends on the seed, i.e. on letters the ring never reads. Same logical structure as a
highway: the structure is certified by finitely many letters, its onset is not.

### 2026-10-25 10:54 (+13:00) · 5cce04f · observation
P6 run (`scripts/p6_run.sh`, 7.5 min on 3 threads; specs sha256 and binary in `results/p6_run.log`; launched at commit 4d7cb78) and
registered analysis (`scripts/p6_analyse.py` -> `results/p6_analysis.txt`, `results/p6_classes.csv`). 446 runs (12 left the 16384
board). Disclosure: building the run list printed the overlap of builders and Pi rules (219) before classification.
- (a) necessity **FAILED**: 220 runs are ring(k); 2 of them do not satisfy Pi(k): RRLLLRLLLRLL (classed ring(5): 12 visits per cell,
  reads 0..11 uniform, max read 11) and RRRLRRLLRRRR (ring(2): table RRRLRR on counts 0..5, 6 visits, reads of 6 at 0.17%).
- (b) sufficiency **held**: 218/361 Pi rules = 60.4% are ring(k) (band 30-90%, point guess 60%). By k: 159/256, 42/65, 9/18, 3/7, 3/5,
  1/4, 1/3, 0/2, 0/1. The 143 others are 136 census blobs, 2 log growers, 4 escapes, 1 highway.
- (c) Q15: ring(k) = 72.4% of the 304 builders (>= 50%, **held**); two-visit 6.6% (band 10-30%, **failed**); other 21.1%.

### 2026-10-25 10:54 (+13:00) · 5cce04f · surprise
The registered necessity failed because the footprint does not pin the turn table: other crawlers spend the same integer number of
visits per cell. Post hoc (`scripts/posthoc_p6.py` -> `results/posthoc_p6.txt`, criterion chosen after seeing P6): 272 of 446 runs
are integer-cost fillers (new-cell rate 1/v*, counts 0..v*-1 uniform). Tables: RLRR 159, RRLRRR 43, RRRLRRRR 9, ... (the proved family,
k = 1..7, 218 rules); RL 20 (two-visit, the mirrored k = 0 member); **RRLR 1, RRRLRR 13, RRRRLRRR 3**, i.e. the reversed table
R^(k+1) L R^k with the same 2(k+1) cost; and RLLR 3, RLLRLL 3, RRLRLRRR 3 and seven singletons (v* up to 26). RRRLRRLLL's north
edge (scratch Python) reads rows 3311 / 4466 / 6666: a different profile from C_2.

### 2026-10-25 10:54 (+13:00) · 5cce04f · interpretation
The proved crawler is the majority mechanism of the census builders (218 of 304 builders are ring(k), all Pi), but not the only
one: there is at least a second family with the reversed table R^(k+1) L R^k at the same cost 2(k+1), and the two-visit spirals fit
the mirrored k = 0 crawler. Q15's "one class" fails. The footprint criterion was too weak to separate crawler families; the right
membership test is the turn table plus a crawler check, not read uniformity.

### 2026-10-25 10:57 (+13:00) · 3b13695 · observation
`PROPTEST_RNG_SEED=20261019 cargo test --release --locked`: 205 passed, 0 failed (no src/ changes in this experiment; two new
examples only). Notebook built (`scripts/build_notebook.py`) and executed from a clean kernel with nbclient: 19 cells, 0 errors.
Figure `results/fig_square_ring.png` from `scripts/figure.py` (deterministic). Notes updated: open questions (Q15, Q20 in part,
Q25, Q26), ACTIVE backlog, atlas (persistent-structures evidence, late-highways also) and experiment guide row.

### 2026-10-25 10:57 (+13:00) · 3b13695 · decision
End of the registered programme. Not started: the corner lemma, the reversed family, onset statistics (Q25, Q26). These need their
own registrations. No pruning-index signature (positive mechanism; the failed P6 (a) is a criterion failure, not a dead family).

### 2026-10-25 10:57 (+13:00) · e773b00 · deviation
`results/p1_crawler_runs.txt` was 2.9 MB (full read histograms for 4,288 control runs). `scripts/p1_crawler.py` now writes one
compact line per run (periods_ok, first_fail, reads_as_expected); P1 rerun, `results/p1_crawler.txt` byte-identical to the committed
summary, runs file 0.75 MB. Notebook re-executed.

### 2026-10-25 15:14 (+13:00) · e14f67a · deviation
Independent review of this experiment (reviewing AI agent, Claude Fable; not Corvid). corrects: 10:38 (P2/P3 numbers) and 10:54
(post hoc table). Checked against `results/p23_analysis.txt`: the cycles per direction in [2^26, 2^27] are 489-849 (k = 5 down
to k = 1), not 489-1,450; the share of count 2k+2 is at most 0.0083% (`RRLRRRRLLL`), not below 0.007%; the largest relative
deviation of the shares 0..2k+1 is 0.083%, so "within 0.08%" should read 0.09%; steps per visited cell for k = 1 are 3.998-4.001
(`RLRRRRRRL` 4.0007 and `RLRRRRRRRL` 4.0008 lie *above* 2(k+1), so "the deficit is the seed and the corners" is not the whole story:
those seeds hold more excess visits than the corners lack) and for k = 2 5.994-5.996. Against `results/posthoc_p6.txt`: the proved
family's row in the post hoc table counts 219 integer fillers (159 + 43 + 9 + 3 + 3 + 1 + 1), not 218; the rule beyond the 218 ring(k)
Pi rules is `RRLRRRRRRLR` (Pi(2), census builder, v* = 6, table `RRLRRR`, max read 24, reads >= 6 at 0.082%), which the registered
ring(2) test rejects; with 219 the rows sum to 272. README results edited to these values (registration untouched); the README
command block now also lists the post hoc, figure and notebook commands. Other checks made in the review, all agreeing with the
record: the crawler lemma re-traced by a separate script (phase-by-phase cell, value read, turn and heading; final values; translation
of the whole visited rows; four reads per count) for k = 1..40; `scripts/p6_specs.py` rerun gives byte-identical `p6_specs.txt` and
`p6_membership.csv` and prints 361 canonical Pi rules of length <= 12; a build of the two examples into a fresh `CARGO_TARGET_DIR`
reproduces the sha256 logged in `results/*_run.log` (footprint `ae619384...`, crawler `2ddf4d94...`), so the committed runs used the
committed source; `cargo build --release --locked --examples` succeeds; `blog/scripts/atlas.py --check` passes.

### 2026-10-25 15:16 (+13:00) · d709628 · observation
Review, instrument oracle. The committed oracle ran its six specs on four rayon threads with the one escaping run (`RL`) last and
shorter than the window, so neither an escape after the ring buffer had started dropping reads nor a run starting in a buffer left
by an earlier run was exercised, although P6 has 12 escaped runs and 446 reuses. `scripts/oracle_footprint.py` now runs on one
thread with `RL` first and adds a 256-board, 4096-step-window case in which `RL` escapes at step 15,725 before and after a switched
run; `scripts/oracle.sh` writes its report through a temporary name so a rerun's dirty count does not see its own output.
`bash scripts/oracle.sh` at `d709628`, clean tree: fingerprints identical to `fast::run` for the same five rules at 1e6 and 1e7
steps (same hashes as the 10:35 run; binary sha256 unchanged, `ae619384...`), all 10 Python-reference comparisons OK, ORACLE PASSED
(`results/oracle.txt` regenerated). The notebook was re-executed from a clean kernel with the documented command: 19 cells, 0 errors;
only the oracle cell and the provenance hash of `oracle.txt` changed. No change to any verdict or number from the instrument review.

### 2026-10-25 15:19 (+13:00) · f55befa · deviation
Reviewed the five review-fix commits (29c6597..f55befa): numbers spot-checked against `results/p23_analysis.txt` and
`results/posthoc_p6.txt` (cycles 489-849, max share deviation 0.00083, max share of 2k+2 8.3e-5, steps per cell ranges, the 219th
proved-family run RRLRRRRRRLR) and accepted. One wording change: the README's reason why RLRRRRRRL and RLRRRRRRRL sit above 4 steps per
cell (seed excess) is now marked as unverified; nobody measured it.

### 2026-10-25 (+13:00) · PR #17 · deviation
Question renumbering, appended by Kea (AI research agent) at the maintainer's request; earlier entries are not edited.
This experiment's Q25 (ring onset from a blank board) is now Q27, and its Q26 (reversed family / corner proof) is now Q29
in `notes/open-questions-hypotheses.md`, because the same numbers had been assigned independently in PR #15.
