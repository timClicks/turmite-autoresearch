# Are the other three no-highway escapes macro-transitions? (proof track, generalisation)

Registered 2026-10-23 18:05 (+13:00), base commit `d8c0892`. **Nothing in this folder has been run** when this file is
first committed. Parent: `experiments/archive/2026-10-rlrlll-macro-transition/` (RLRLLL column sweeper, closed family
C(m, q)); plan: `notes/proof-track-2026-10-20.md`, Next steps item 2.

## Question

`RLLLLRRL`, `RLLLLRLRRL`, `RLLLRLRLLL` are the only no-highway "escapes" of the 1e11 cohort
(`experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/`: stop = escaped at steps 12,601,085,717 /
39,619,909,558 / 28,427,043,780; final boxes 32750x32735, 32404x32601, 32683x32750 on the 32768 board).
**"Escaped" only means the ant touched the board edge.** Nothing in the record says any of them runs a sweeper.
The three boxes are nearly square, so a board-filling growth (area ~ t, many revisits, no repeating cycle) fits the
record as well as a sweeper does. This experiment first decides which it is, and only then (Stage 2) tries to
generalise the RLRLLL checker. A sweeper is **not assumed**.

Competing readings, all registered as outcomes:

- **SW (sweeper):** after some onset a front advances in one axis direction by a repeating cycle whose length is an exact affine
  function of the cycle's perpendicular swing, `dt = a * swing + b(q)`, `q` a phase of period <= 6. Same signature as P1 of the parent.
- **HW (missed highway):** swing constant and `dt` periodic (translation-periodic). A census correction if found.
- **FI (filler / no finite-state cycle):** the front advances irregularly; no exact clock. Includes growth with square-ish
  boxes at ~4 steps per new cell. The escape is then a board effect on an open-ended process.
- **IN (inconclusive):** instrument or budget failure. Not a dead end.

## Pruning-index preflight

- Index revision: `d8c0892db5e97d4d4f6f8de0933814a51b5a5b7c`.
- Commands: `rg --files notes/pruning-index/entries`; `rg -n -i -e RLLLLRRL -e RLLLLRLRRL -e RLLLRLRLLL -e sweeper -e escape -e column notes/pruning-index/entries` (exit 1, no output).
- Candidates: sole entry `NR-20261022-additive-laws-order-blind`. Membership (rules of length 2..8, additive-law mining) covers
  `RLLLLRRL` (length 8) for a different objective (conservation laws); nothing about growth, sweepers or escapes. It does not apply.
- Decision: **run.** Same rules, new objective (macro-transition structure). The parent experiment's RLRLLL result is a
  positive control, not a prune.
- Budget (bounded closure, per `notes/ACTIVE.md` 2026-10-23): Stage 1 = three single-core runs, each <= 1 h wall time on the
  32768 board, plus one 65536-board repeat for the first rule that survives. Stage 2 only if Stage 1 gives SW for >= 1 rule, and
  then for **one** rule at a time, capped at one working session each; stop on the first rule where the proposal cannot be
  closed by finite lemmas and record why. No sweeps, no census expansion.

## Amendment (2026-10-23 18:15 +13:00, before any run; the text above is kept as committed in `7aed7de`)

After a side note from the user that a filler fits the census equally well, Stage 1 runs all three rules on a **65536** board
(4 GiB each, so the ant passes the census escape step instead of stopping there), budget <= 1.5 h per run. G5 becomes: a
32768-board repeat of the first rule that shows SW reproduces the 65536 run's cycles up to the 32768 exit. "Window" for the
exact-clock test = the last 2e8 steps before the rule's census escape step, and separately the last 2e8 steps of the whole run.
Nothing else changes.

## Instrument

New example `examples/sweeper_generalisation_frontlog.rs` (hot loop = the plain loop of the parent's tracer). It logs, for each of
the four directions d, every step at which the global extreme in d advances: `(t, extreme, perpendicular min, perpendicular max
of the ant since the previous advance in d)`. Cycles for any period P are derived afterwards in Python by grouping consecutive
advances (cycle boundary k = first time the front reaches f0 + P k); the swing of a cycle is the union of the perpendicular
ranges of its advances. Direction-agnostic (no assumption that the front moves west) and no assumption about P or the
clock constants.

Oracle (AGENTS.md rule 4): the example's final `(t, x, y, heading, FNV-1a of every cell colour)` is compared with `fast::run`
at 1e7, 1e8 steps for each rule (`scripts/oracle.sh`), and a Python reference ant reproduces the event log for the first 2e5 steps
(`scripts/oracle_log.py`). Positive control: RLRLLL with the same tool must recover `dt - 12 swing in {358, 394, 518}`-type
three-phase exactness (parent P1) at P = 3, direction west. Negative control: the unrelated rule `RRLLLLRRL`
(log growth in the census) must give no exact clock.

## Predictions (registered before any run)

Definitions. For direction d and period P in 1..8, cycles are as above. **Exact clock on a window** = there are an integer `a`
and values `b_0..b_{p-1}` (p <= 6) with `dt_k = a swing_k + b_{k mod p}` for >= 95% of the cycles in the window and every
residual zero (not small). Window = last 2e8 steps before the ant leaves the board (the census escape point), unless noted.
The best (d, P, p) is reported; with 4 x 8 x 6 candidates the multiplicity is irrelevant because the criterion is zero residual on
hundreds of cycles, but the number of candidates tried is reported.

- **G1 (RLLLLRRL).** Exact clock on the last-2e8 window: P(true) ~ 45%. Reason: census class "builder", 3.96 steps per new cell
  and width exponent 0.49, the same signature RLRLLL has after its switch, but the box is square at the end.
  Falsified if no (d, P, p) gives an exact clock.
- **G2 (RLLLRLRLLL).** Exact clock on the last-2e8 window: ~40%; onset (first cycle after which the clock is exact to the end)
  between 1e10 and 2.5e10: ~60% given SW. The expansion of 8.5x between 1e10 and 1e11 looks like a late switch.
- **G3 (RLLLLRLRRL).** Exact clock: ~30%. Expansion 2.2x only; most likely FI or an unfinished transient.
- **G4 (filler discrimination).** For each rule, in 1e6-step windows over the last 2e8 steps, report steps per new cell and the
  aspect of the box of newly visited cells (the parent's signature S: spc < 8 and aspect >= 20). Prediction: S holds in
  >= 90% of windows for a rule iff that rule is SW. Falsified if a rule has S holding and no exact clock, or the reverse
  (then S is not a sweeper signature and the parent's G1 note must say so).
- **G5 (board independence).** For any rule with SW, repeating on the 65536 board reproduces the identical cycle sequence
  (same `dt`, `swing` for every cycle that ended before the first run's board exit). Falsified by any difference.
  (Dynamics are board-independent until the edge, so this tests the tool, not the physics.)
- **G6 (controls).** Positive control passes and negative control fails as stated above. If either does not, no verdict on the
  three rules is recorded: outcome IN.

What each outcome changes: SW for >= 1 rule -> Stage 2 (propose block family from front snapshots, generalised checker, one
rule at a time). All FI -> record as a negative result: the "no-highway escape" label hides at least these growth types, and
the proof track's census-wide decider has no sweeper to find among them; the unresolved list's remaining survivors are the next place.

## Stage 2 sketch (only if SW)

Reuse the parent's architecture, parametrised by data: stage list `S_0, L_1^n, S_1, L_2^n, ..., S_k` of finite runs and iteration
lemmas (patch `G . B^p -> r' . G` with sentinel rows), composition by list identity, 150+ brute-force cycle cross-checks,
mutation and wrong-rule controls, and a Lean certificate generator only for the lemma stages. The proposer (a script) may be
wrong; acceptance only by the checker. Direction is normalised by rotating headings, never by mirroring (a mirror changes the rule).

## Commands

Filled in as they are run (see `NOTEBOOK.md` for timestamps and hashes). Builds go to a fresh `CARGO_TARGET_DIR`,
exit status checked, binary sha256 logged. Runs are in WSL (`/mnt/f/Code/turmite`).

## Results, uncertainty and limitations

(none yet)

## Stage 1 results (appended 2026-10-23 18:36 +1300; the registration and amendment above are not edited)

Provenance: front-log example at commit `1461cb9` (binary sha256 in `results/stage1_binary.txt`, `7d135c9b...`; the oracle in `results/oracle.txt` passed on the same source: fingerprint equal to `fast::run` at 1e7 and 1e8 steps and event logs equal to an independent
Python ant for 2e5 steps, for all five rules used here). Runs: `scripts/run_stage1.sh` (five parallel single-core jobs, WSL, 65536 board for the three targets, 32768 for the two controls; wall times 4:16 (positive control), 0:56 (negative control), 13:58, 18:49 and 22:34 minutes).
Analysis: `scripts/analyse_stage1.sh` -> `results/stage1_analysis.txt` (registered), `results/stage1_posthoc*.txt` and `results/stage1_onset.txt` (post hoc, labelled). Peak memory 4.2 GiB per 65536-board run.

Where the runs ended: **RLLLLRRL** left the 65536 board at step 20,245,062,163 (x = -32768); **RLLLRLRLLL** at 34,863,498,538 (y = 32767); **RLLLLRLRRL** did not leave it by the 6e10-step budget (ant at (11866, -11200), 1.24e9 non-zero cells).
So "escaped" in the census meant: the territory had reached +-16384 at 1.2601e10 / 2.8427e10 / 3.9620e10 steps, and nothing else.

| | census exit (32768 board) | registered test (p <= 6) in the window before that step | registered test, last 2e8 steps of the run | window signature S (spc < 8 and aspect >= 20) | what the run shows |
|---|---|---|---|---|---|
| RLRLLL (positive control) | n/a | EXACT, direction xmin, P = 3, p = 3, a = 12, 100% of 4714 cycles | - | 281 of 297 windows (94.6%) | recovers the parent's clock |
| RLLLLRRL | 1.2601e10 | **no**, best exact fraction 0.155 (614 cycles) | **no**, 0.19 (48 cycles) | 0 of 182 / 0 of 200; median 2.0 steps per new cell, aspect 1.00 | see below |
| RLLLRLRLLL | 2.8427e10 | **EXACT**: xmin, P = 1, p = 2, a = 8, b = (-218, -186), 100% of 782 cycles | **EXACT**, 100% of 384 cycles | 0 of 200 / 0 of 200; 2.0 steps per new cell, aspect 1.00 | square spiral, exact clock |
| RLLLLRLRRL | 3.9620e10 | no (34 cycles; irregular) | no (<= 39 cycles; gaps up to 4e9 steps) | 0 of 48 / 0 of 22; 2.4-7.1 steps per new cell, aspect 1.0 | not in a periodic regime by 6e10 |
| negative control RRLLLLRRL (registered) | - | NO_DATA: 14 front events in 3e9 steps | - | - | vacuous control |
| negative controls RLLLLRRLL, RLRLLLLRRL (added after registration, 3e9 steps) | - | no (best 0.14 / 0.23 on 51 / 31 cycles) | - | 0 of 117 / 0 of 1958 | the criterion rejects chaotic growth, but at low power |

**Scoring against the registered predictions.**
- **G1 (RLLLLRRL, ~45%): failed as registered.** The registered test (phase period p <= 6) finds no exact clock in either window. *Post hoc* (`results/stage1_posthoc_rlllrrl.txt`, `stage1_posthoc_maxp64.txt`): from cycle about 19,600 (step about 1.47e10) the residual `dt - 8 swing` is exactly periodic with **period 19** in the revolution index
  (14 distinct values 38 ... 2110, direction xmin and xmax identical, 100% of 383 cycles in the last window and of the 4000 cycles examined in 28000-32000), so there is an exact affine clock with a 19-revolution super-cycle; my cap p <= 6 was too small. Before about 1.47e10, including the whole window in which the 32768 board ended the census run, revolutions are irregular (residuals up to 3.5e5).
  So the census exit of RLLLLRRL happened about 2e9 steps *before* its exact regime began.
- **G2 (RLLLRLRLLL, ~40% clock, ~60% onset in (1e10, 2.5e10) given a clock): the clock held; the onset prediction failed.** The exact clock begins at step **26,351,953,955** (revolution 2876, swing 5809) and holds for the **29,854 consecutive revolutions** to the exit (`results/stage1_onset.txt`); the onset is above my predicted range. (Post hoc: the 470 revolutions before it follow the same clock with constants (-178, -210) and occasional defects, then the constants shift by -8 to (-186, -218).) The census exit at 2.8427e10 therefore fell inside the exact regime.
- **G3 (RLLLLRLRRL, ~30%): failed (inconclusive power).** No exact clock; too few revolutions (<= 39 per 2e9 steps) for the test to be informative. The census exit was the blob reaching the edge of the 32768 board; the 65536 run shows no board-independent breakout up to 6e10.
- **G4 (S holds in >= 90% of windows iff the rule has an exact clock): falsified as registered.** S holds in 0% of the windows of every target rule, while two of them have an exact clock. S (a narrow-ribbon signature) is a column-sweeper signature; it is not a necessary signature of an exact clock.
- **G5 (board independence): see the block below.**
- **G6 (controls): positive control passed; the registered negative control returned NO_DATA (vacuous); the added negative controls are rejected.**

**Reading (interpretation, with the confounds I know).** The three escapes are not three sweepers. Two of them (RLLLRLRLLL, RLLLLRRL) are *square spirals*: the territory is a filled square whose boundary the ant circles at 2 steps per cell (median steps per new cell 2.0, new-cell box = the whole square, aspect 1.00); each revolution takes `8 * swing + b` steps and grows the side by 2, with exact constants after a late onset
(2.635e10 and about 1.47e10 steps). Neither is a column sweeper in the parent's sense, and the census label "builder" at about 4 steps per cell for RLLLLRRL describes an earlier phase. The third (RLLLLRLRRL) was still growing like a blob at 6e10, its census exit being the edge of the smaller board.
Not shown: that either spiral continues forever (that is the Stage 2 question), what triggers the late onset, or why RLLLLRRL's super-cycle has period 19. Windows, direction and cycle choices were fixed before the runs; the p-range was not wide enough, which I report rather than retune.

### G5 and the supplementary controls (appended 2026-10-23 18:39 +1300)

**G5 (board independence): held.** RLLLRLRLLL on the 32768 board (`scripts/run_g5_negctl.sh`) left at step 28,426,781,994 (y = 16383); all four event logs and `windows.csv` before that step equal the 65536 run's, row for row (16347 / 16333 / 16365 / 16382 events and 28426 windows; `results/g5_compare.txt`).
My first comparison used the census exit step 28,427,043,780 and printed FAIL: that step is one revolution (262k steps) later than the instrument's own exit, because the census board check is one cell wider, so the larger run simply had one more row; I reran with the smaller run's own exit step (the registered meaning) and the file header says so.
This tests the tool (dynamics are board independent until the edge), not the physics. Supplementary negative controls (added after registration): `results/stage1_negctl_extra.txt`.

### Stage 2 probe (appended 2026-10-23 18:39 +1300; unregistered feasibility look at RLLLRLRLLL, five revolutions at about swing 6055)

`examples/sweeper_generalisation_spiral_probe.rs` (binary sha256 in `results/spiral_probe_binary.sha256`), `scripts/spiral_analyse.py`, `scripts/spiral_steady.py`; outputs `results/spiral_probe_analysis.txt`, `results/spiral_steady.txt`. T0 = 26,357,767,165 and T1 = 26,358,008,611 are cycle ends read from the Stage 1 log; board 8192; the ant has the same trajectory as in the 65536 run by G5.
- Along each straight stretch of a side the ant's position sequence is exactly periodic with **period 4 and displacement 2** (e.g. (0,-2), (2,0), (0,2), (-2,0) on the four sides): 2 steps per cell. Between sides are stretches of 1000-2000 cells with diagonal velocity, so the path is more octagonal than square.
- The ant is not confined to the new outer layer: it visits depths from -5 (outside the T0 bounding box) to **76** cells inside it, 70% of its steps at depth >= 8.
- The outer band (depth 0-63, sampled) is a steady profile moving outward: after five revolutions 99.7% (west), 99.6% (east), 99.2% (north), 99.2% (south) of the sampled cells equal the T0 cells at the same depth from the edge, with the along-side coordinate shifted by 5 (one per revolution); the differing cells sit at a few fixed along-positions at every depth (seams).
Reading: a macro-family `C(L)` exists at the cell level (steady band, sides periodic with period 4), but proving it needs a band of depth >= 77, about eight straight and diagonal segments with a periodic *ahead* background (the previous revolution's layer, not blank ground), and seam blocks. That is a new proof architecture, not a parameter change of the three-stage sweeper checker, and I did not start it (registered stop rule: Stage 2 is capped at one working session per rule, and the first rule needs a different design).

## Corrections and additions after review (appended 2026-10-23 18:49 +1300; nothing above is edited)

1. **Period-19 onset, tested directly** (`scripts/onset.py --derive 19`, `results/stage1_onset.txt`): for RLLLLRRL the revolution constants are exactly periodic with period 19 from revolution **19,596** in direction xmin (step 14,724,680,227, swing 39,166) and from 19,578 in xmax, and stay so for all
   13,170 remaining revolutions to the exit at 20,245,062,163. The "about 1.47e10" in the Stage 1 reading is therefore right (1.4725e10), measured and not inferred from block medians; the census exit of the 32768 board (1.2601e10) was 2.12e9 steps earlier. RLLLRLRLLL's onset (period 2) is unchanged: revolution 2876, 29,854 revolutions to the exit.
2. **Reproducibility.** The three post hoc outputs that I first produced with inline snippets are now regenerated by committed scripts: `scripts/posthoc_rlllrrl.py` -> `results/stage1_posthoc_rlllrrl.txt`; `scripts/posthoc_onset_context.py` -> `results/stage1_onset_context.txt` (previously appended to `stage1_onset.txt`);
   `scripts/posthoc_maxp64.sh` -> `results/stage1_posthoc_maxp64.txt`. Commands: `python3 scripts/posthoc_rlllrrl.py scratch > results/stage1_posthoc_rlllrrl.txt` etc., from this folder in WSL. The files in git history before this commit were hand-driven versions of the same computations.
3. **A meaningless line removed.** The first `stage1_posthoc_maxp64.txt` printed RLLLLRLRRL with phase period 60 and exact fraction 0.897 on 68 cycles, about one cycle per phase class, which fits anything. `clock.py` now has an optional `--minper N` guard (default 0, so every registered number is unchanged); the post hoc file uses `--minper 8` and RLLLLRLRRL then shows 0.13 (period 4, 39 cycles) and 0.13 (period 8, 67 cycles). The period-19 fit of RLLLLRRL rests on 383 cycles (about 20 per phase class) and passes the guard.
4. **Wording of the spiral.** I called these runs "square spirals" in which the ant "circles the boundary". The Stage 2 probe says more: most steps (70%) are at least 8 cells inside the territory's bounding box and the ant reaches 76 cells deep; straight stretches (period 4, displacement 2) are joined by diagonal stretches 1000-2000 cells long. Read "spiral" as: a filled, octagon-like territory whose outer band of about 80 cells is rewritten once per revolution, 2.0 steps per new cell, one cell of growth per side per revolution. The exact clock and the new-cell statistics are unaffected.
5. **Falsification harness.** All classification statements in this experiment ("sweeper", "spiral", "blob") rest on blank-board runs, the clock test and the probe. None was attacked with `src/falsify*` (perturbed starts, obstacles, search); a `Survived` there would still not be a proof. Treat them as unattacked observations.

## Pruning-index outcome and next question

No dead-end signature is warranted: the experiment found structure (two exact clocks), not a family-wide negative. One partial negative is recorded here for the record, with its limits: the three-stage column-sweeper checker of the parent does not transfer to these rules (they need a band of depth >= 77, about eight segment kinds and a periodic ahead background); that is a statement about one design, not about the rules.
Reopen/next: a registered Stage 2 for RLLLRLRLLL with a rectangle-cycler generalisation whose ahead background is periodic instead of blank (the side of a spiral), with a prediction about the band depth and the seam count; the pruning-index query would be repeated for that rule family and objective first.
