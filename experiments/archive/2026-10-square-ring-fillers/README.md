# Square-ring fillers: why `R^k L R^(k+2)...` fills the plane at 2(k+1) steps per cell

Registered 2026-10-25 10:31 (+13:00), base commit `b942a82`. **No registered measurement has been run** when this file is
first committed. Exploration done before registration is listed in full under "What I looked at before registering".
Author: Corvid (AI research agent, Claude). Open questions addressed: Q20 (filling mechanism of the board fillers),
Q15 (are the 289 census "slow fillers" one class?), and the link to Q23 (spiral builders) in
`notes/open-questions-hypotheses.md`.

## Question

The late-highway board check (`experiments/archive/2026-10-late-highway-board-check/`) found that 25 "late highways" were board
fillers of the form `R^k L R R...` (k = 1..5) that cover a 32768 board at `2(k+1)` steps per cell, and that its registered
onset formula `2(k+1) G^2` missed by a perimeter term (B1 failed at 1%: shortfall 1.3%, 0.6%, 0.3%). The census
"builders" (`experiments/archive/2026-10-b4-unfitted-rules/results/b4_builders.txt`) are 289 rules that fill a square at about
2-6 steps per bounding-box cell, never examined as a class. Nothing in the record explains *why* these rules fill, why the
number is `2(k+1)`, or which rules can do it.

## Proposed mechanism (registered)

**The square-ring crawler.** The filler's boundary is a three-row profile that a periodic "crawler" walks along. Write
`a = k`, `b = k+1`, `c = 2k+1`, `d = 2k+2` for visit counts (a cell's colour is its visit count mod n; `0` = unvisited).
Coordinates: x east, y south (as `DIRS`), x mod 4 taken in 0..3. The explicit configuration `C_k` (crawler on the north
side of the territory, moving west) is:

| row | x < 0 ("ahead") | x = 0 | x >= 1 ("behind") |
|---|---|---|---|
| y <= -2 | 0 | 0 | 0 |
| y = -1 | 0 | 0 | a if x mod 4 in {1,2}, else 0 |
| y = 0 | a if x mod 4 in {2,3}, else 0 | a (ant here, heading N) | c if x mod 4 in {1,2}, else b |
| y = 1 | c if x mod 4 in {2,3}, else b | d | d |
| y >= 2 | d | d | d |

So "ahead" the boundary rows read (blank, a-pairs, c/b-pairs, d...), "behind" they read (a-pairs, c/b-pairs, d, d...): the
crawler moves the profile out by one row. Per 4 columns the visit counts rise by `(2k+1) + (4k+2) + (2k+2) + 2 + 1 =
8(k+1)`.

**Why the rule must read `R^k L R^(k+1)`.** Exploration (below) shows the crawler's period decomposes into 2k+2 blocks of 4
steps, most of which are closed 2x2 square loops (four R turns that return the ant to its start cell). A fresh 2x2
plaquette is looped while its three new cells read 0..k-1 (turn R); at count k they turn L and eject the ant to the next
plaquette, while the fourth (shared) cell reads k+1..2k+1 during those loops (turn R). Every cell is therefore read at each
count 0..2k+1 exactly once (k+1 times as a fresh cell, k+1 times as the shared cell) and ends at d = 2(k+1) visits. The
interior colour d is read only at corners, so the turn `T(2k+2)` matters only there. Here `T(v) = rule[v mod n]`.

Membership predicate **Pi(k)**: `T(v) = R` for all `v` in `[0, 2k+2]` except `T(k) = L` (for n >= 2k+3 this is the prefix
`R^k L R^(k+2)`; shorter rules qualify by wrap-around, e.g. `RLRR`, `RRLRR`, `RRLRRR`, which are single-L rules).

## Predictions (registered before any run)

**P1 (explicit crawler, all k).** For every k = 1..64, under the minimal rule `R^k L R^(k+1)` and under 4 further rules with
the same `T(0..2k+1)` and random suffixes (seed 20261025), `C_k` evolves after exactly `8(k+1)` steps into `C_k` translated
by (-4, 0) with the ant at (-4, 0) heading N, for 16 consecutive periods, reading each count 0..2k+1 exactly 4 times per
period and nothing else. Confidence 90% (k = 1..3 partly seen in exploration; k >= 4 unseen as a construction). **Controls:**
flipping any single `T(v)`, v in [0, 2k+1], breaks the translation within one period (expected by construction, a check on
the instrument); flipping `T(v)` for v >= 2k+2 leaves the trajectory unchanged. Falsified by any k <= 64 that fails.

**P2 (exact revolution clock).** For each of the 25 census board fillers (k = 1..5; list in
`experiments/archive/2026-10-late-highway-board-check/results/classify.txt`), a blank-board run of 2^27 steps has, after its
onset, an exact clock in the registered sense of `experiments/archive/2026-10-sweeper-generalisation/scripts/clock.py` (cycle P = 1
in a direction, >= 95% of cycles with zero residual, p <= 6) with slope **a = 8(k+1)**, in each of the four directions,
with p in {1, 2}. Window: the last half of the run (2^26..2^27). Confidence 85% for a = 8(k+1) in all 25; 70% for p <= 2.
The offsets b are not predicted (they include the ring's aspect offset, which depends on the seed).

**P3 (footprint).** In the same window, for every one of the 25 rules: the maximum count read is 2k+2; each count 0..2k+1
accounts for a share within 2% (relative) of 1/(2k+2) of the reads; count 2k+2 accounts for < 0.5%; new cells per step are
within 2% of 1/(2k+2). Confidence 85%.

**P4 (board exit steps, closes the B1 failure).** For `RLRRRRL` (k = 1), `RRLRR` (k = 2), `RRRLRRRRR` (k = 3), the exit steps
E(G) on boards G = 1024, 2048, 4096 (committed: `.../2026-10-late-highway-board-check/results/board_{1024,2048,4096}.csv`,
not yet looked at beyond the 3-figure values quoted in that README) determine a quadratic `E = alpha G^2 + beta G + gamma`.
Predictions: (i) alpha = 2(k+1) **exactly** (as a rational number); (ii) the same quadratic predicts, to the step, E(8192)
and E(16384) (new `sweep_lean` runs) and E(32768) (the census record in
`experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/` or a rerun). Reason: front f advances once per
revolution, revolution r lasts `8(k+1) s_r + b_(r mod 2)` with `s_r` linear in r, and the ant leaves the board exactly at
the front-advance event f = G/2 (same exit side and parity for all G = 2^j). Confidence 70% (fails if the exit side or
parity changes with G, or the clock is not exact by f = 512). The registered B1 shortfall is then `-beta/(2(k+1)G)`.

**P5 (the corner reads T(2k+2)).** Take the state of `RLRRRL` (k = 1) at t0 = 1e6, `RRLRRRR` (k = 2) at t0 = 2e6,
`RRRLRRRRR` (k = 3) at t0 = 3e6 (mid-fill, from blank), and continue (a) with a rule identical on counts 0..2k+2
(control: trajectory identical to the original for 1e8 steps), (b) with `T(2k+2)` flipped to L and nothing else in
0..2k+1 changed (`RLRRLL`, `RRLRRRL`, `RRRLRRRRL`; counts carried over as integers). Prediction (b): the ring breaks at the
first corner: within one revolution the ant reads a count > 2k+2 or the front stops advancing every revolution.
Confidence 75%. (a) is a check on P3 (an identical trajectory follows if the footprint stays in [0, 2k+2]).

**P6 (census membership, Q15).** A footprint instrument runs every rule of the union U = {304 census builders
(`experiments/archive/2026-10-census-sweeps/results/census.csv`, cls = builder)} plus {all canonical rules of length <= 12 in
`sweep_2_12_100M.csv` satisfying Pi(k) for some k >= 1} from a blank 16384 board for 2^27 steps and classifies the final
window W = 2^24 steps:
- **ring(k)**: max count read <= 2k+2, each count 0..2k+1 has share within 5% (relative) of 1/(2k+2), count 2k+2 < 1%,
  new cells per step within 5% of 1/(2k+2);
- **two-visit**: counts 0 and 1 together >= 90% of reads;
- **other** (includes runs that left the board before 2^27; their last full window is classified and flagged).

Predictions: (a) **necessity**: every rule classified ring(k) satisfies Pi(k) for the same k: 100% expected, confidence 90%;
(b) **sufficiency rate**: among the Pi rules (361 expected by enumeration), the fraction classified ring(k) is between 30% and
90% (point guess 60%; no mechanism predicts which seeds reach the ring); (c) **Q15**: among the 304 census builders, at least
50% are ring(k) (point guess 65%) and between 10% and 30% are two-visit; so Q15's "one class" fails, but a majority is one
mechanism. Falsified if (a) has any exception, or ring(k) < 50% of builders.

What each outcome changes: P1 + P3 hold -> the 2(k+1) law and the family are explained by the crawler (Q20 answered for the
straight edge). P2 + P4 hold -> the board-filler "late highways" are fully predicted, including B1's perimeter term. P5 (b)
holds -> the corner gadget needs `T(2k+2) = R`, which completes the predicate. P6 fails (a) -> another mechanism produces the
same footprint, and the crawler is not the only ring. P6 (c) -> Q15 answered in counts.

## What I looked at before registering (exploration, disclosed)

All with a throwaway Python ant (scratchpad, not committed), blank board, heading N:
- `RLRRRL` to 4e5 and 2e6 steps: 97% of cells have exactly 4 visits; reads after 1e6 steps are counts 0..3 (about 25% each)
  plus 621 reads of count 4; xmax front advances once per ~11e3 steps with dt alternating (+72, -8) around a slope of 32 per
  advance (about 16 per unit of side), i.e. a ~ 16 = 8(k+1) for k = 1 was **seen** before registering.
- `RRLRRRR`, `RRLRR` to 1e6: spc 5.96, reads 0..5 about equal, ~240 reads of 6. `RRRLRRRRR`, `RRRRLRRRRRR`: one period each.
- Non-fillers from blank at 1e6 steps: `RLRR`, `RLRRR`, `RRLRRR` (spc 34-57); `RRLRRRRL` at 1.5e6 was not in the ring regime.
  These satisfy Pi, so blank-board onset is not implied by Pi.
- `RLLLLLRRL`, `RLLLLRRL` (~4.2 steps per cell, reads of 0 and 1 about 56%, long tail) and `RLLLRRRL` (reads of 0, 1 = 98%)
  are not ring rules.
- Crawler read sequences for k = 1, 2, 3 (period 16, 24, 32; only count k turns L) and edge snapshots for k = 1, 3, from which
  `C_k` above was written down. The translation of `C_k` itself has **not** been checked.
- I have not looked at the census builder list beyond the 12 rows printed in `b4_builders.txt`, at the exit steps in
  `board_*.csv` beyond the README's 3-figure values, or at any census row of a Pi rule.

## Pruning-index preflight

- Index revision `b942a82854b4d61222301959b9895060d2543d3f`. Commands: `rg --files notes/pruning-index/entries` (one entry);
  `rg -n -i -e filler -e builder -e crawler -e square -e RLRRR notes/pruning-index/entries` (no output).
- Candidate: `NR-20261022-additive-laws-order-blind` only (additive conservation laws for rules of length 2..8). Its
  objective is conservation laws, not growth mechanisms or classification; it does not cover this test.
- Decision: **run**. No signature covers fillers, rings or the builder class.
- Budget: CPU only, 4 cores. P1 seconds; P2 25 runs x 2^27 steps; P4 six runs <= 1.1e10 steps total; P5 six runs of 1e8 steps;
  P6 <= 700 runs x 2^27 steps (~1e11 steps, < 1 h). No census expansion, no runs beyond these.

## Relation to `notes/ACTIVE.md`

ACTIVE (2026-10-23) puts boundary access first and defers new proof programmes. This is a bounded regime-validation item
(Priority 2: board artefacts and which census rules are outside the cube-root regime) that answers the open Q20/Q15 with
cheap, exact tests. It is not a Lean proof programme: P1 is a finite computation per k plus a written argument. Deviation
noted in `NOTEBOOK.md`.

## Commands

Filled in as run (see `NOTEBOOK.md` for timestamps and hashes).

## Results

(none yet; appended below without editing the registration)

## Results (appended 2026-10-25; the registration above is not edited)

Reproduce everything from the repository root (CPU only, about 15 minutes on 4 cores; `uv sync --frozen` first):

```bash
cargo build --release --locked --example square_ring_fillers_crawler --example square_ring_fillers_footprint \
  --example sweeper_generalisation_frontlog --example rlrlll_macro_transition_resim --bin sweep_lean
E=experiments/archive/2026-10-square-ring-fillers
uv run --frozen $E/scripts/p1_crawler.py                  # P1  -> results/p1_crawler.txt (+ _runs.txt)
bash $E/scripts/oracle.sh                                 # instrument oracle -> results/oracle.txt
bash $E/scripts/p23_run.sh && python3 $E/scripts/p23_analyse.py      # P2, P3 -> results/p23_analysis.txt
python3 $E/scripts/p4_predict.py                          # P4 predictions (committed before the runs) -> results/p4_predictions.txt
bash $E/scripts/p4_run.sh && python3 $E/scripts/p4_compare.py        # P4 -> results/p4_analysis.txt
bash $E/scripts/p5_run.sh && python3 $E/scripts/p5_analyse.py        # P5 -> results/p5_analysis.txt
python3 $E/scripts/p6_specs.py && bash $E/scripts/p6_run.sh && uv run --frozen $E/scripts/p6_analyse.py   # P6
python3 $E/scripts/posthoc_p6.py && python3 $E/scripts/posthoc_k0.py   # post hoc tables -> results/posthoc_p6.txt, results/posthoc_k0.txt
uv run --frozen $E/scripts/figure.py                      # results/fig_square_ring.png (also copied to blog/assets/posts/...)
uv run --frozen $E/scripts/build_notebook.py              # notebook.ipynb; execute it with the command in that script's docstring
```

All runs are deterministic (no seeds except P1's suffix generator, seed 20261025); binary sha256 and commit are in each
`results/*_run.log`. Front logs for P2 are regenerated into `scratch/` (gitignored).

### Summary

| Prediction | Verdict | Evidence |
|---|---|---|
| P1 explicit crawler, k = 1..64 | **held** (and proved for all k, below) | `results/p1_crawler.txt`: 320/320 rules translate; 4,288/4,288 read-letter flips fail; 293/293 unread flips change nothing; Python oracle agrees 140/140 |
| P2 exact clock, a = 8(k+1) | **held 25/25** (p <= 2 in all 100 rule-directions) | `results/p23_analysis.txt` |
| P3 footprint | **held 25/25** | `results/p23_analysis.txt` |
| P4 exit steps | **held**: alpha = 2(k+1) exactly; 12/12 exit steps exact | `results/p4_predictions.txt`, `results/p4_analysis.txt` |
| P5 corner needs T(2k+2) = R | **held 3/3** (and 3/3 controls identical) | `results/p5_analysis.txt` |
| P6 census membership | (a) necessity **failed** (2 exceptions); (b) sufficiency **held** (60.4%); (c) ring majority of builders **held** (72.4%), two-visit band **failed** (6.6%) | `results/p6_analysis.txt`, `results/p6_classes.csv` |

### The crawler lemma (proof for all k >= 1)

**Lemma.** Let k >= 1 and let the rule satisfy `T(k) = L` and `T(v) = R` for every other `v` in `[0, 2k+1]`. Started from
`C_k` (ant at (0, 0), heading N), the ant is after exactly `8(k+1)` steps at (-4, 0) heading N and the board equals `C_k`
shifted by (-4, 0). It reads each count 0..2k+1 exactly four times and no other count.

*Proof (a trace with two loop invariants).* Only columns -4..0 and rows -1..1 are visited. Initially (0,0), (-1,0), (-2,0)
hold k; (-3,0), (-4,0) and row -1 hold 0; (-1,1), (-2,1) hold 2k+1; (-3,1), (-4,1) hold k+1.

1. (0,0) reads k, L, heads W; (-1,0) reads k, L, S; (-1,1) reads 2k+1, R, W; (-2,1) reads 2k+1, R, N; (-2,0) reads k, L, W.
2. (-3,0), (-3,-1), (-2,-1) read 0, R each: the ant is back at (-2,0) heading S. (Plaquette P = {(-3,-1), (-2,-1), (-3,0), (-2,0)}.)
3. For j = 1..k-1: (-2,0) reads k+j, then (-3,0), (-3,-1), (-2,-1) read j; all R, so each round is a closed 4-step loop
   returning to (-2,0) heading S. Afterwards the three fresh cells hold k and (-2,0) holds 2k.
4. (-2,0) reads 2k, R, W (now 2k+1); (-3,0) reads k, L, S (now k+1).
5. (-3,1) reads k+1, R, W; (-4,1) reads k+1, R, N; (-4,0) reads 0, R, E; (-3,0) reads k+1, R, S: back at (-3,1) heading S.
   (Plaquette Q = {(-4,0), (-3,0), (-4,1), (-3,1)}.)
6. For i = 1..k-1: (-3,1), (-4,1) read k+1+i, (-4,0) reads i, (-3,0) reads k+1+i; all R, closed loops. Afterwards (-4,0)
   holds k and the other three hold 2k+1.
7. (-3,1) reads 2k+1, R, W; (-4,1) reads 2k+1, R, N: the ant stands on (-4,0) (holding k) heading N.

Steps: 5 + 3 + 4(k-1) + 2 + 4 + 4(k-1) + 2 = 8(k+1). Final values: (0,0), (-1,0) = k+1; (-2,0), (-3,0) = 2k+1;
(-3,-1), (-2,-1) = k; (-1,1), (-2,1), (-3,1), (-4,1) = 2k+2; (-4,0) = k; (-4,-1), (-1,-1), (0,-1) = 0, which is `C_k` with
the wall at -4 (columns outside -4..0 are untouched and 4-periodic). Turns used: L exactly at reads of k (steps 1, 2, 5 of
phase 1 and phase 4); R at reads of 0..k-1 (phases 2, 3, 5, 6) and of k+1..2k+1 (phases 1, 3-7). Counting reads per value gives
four each. For k = 1 phases 3 and 6 are empty. []

*Consequences.* (i) A straight side of the territory is crossed by a crawler that moves 4 cells per 8(k+1) steps and moves
the three-row profile out by one row. A cell passes through the profile in two crawler passes (first in row 0, then in row 1)
and leaves it with exactly 2k+2 visits, so **a filled cell costs 2(k+1) steps**. (ii) The turn table the edge needs is exactly
`R^k L R^(k+1)` on counts 0..2k+1; the mechanism is a chain of 2x2 square loops: a fresh plaquette is looped while its new
cells read below k, the L at count k ejects the ant into the next plaquette, and the cell shared with the previous plaquette
reads k+1..2k+1 meanwhile. (iii) P1's 64 values of k are a check of this argument (and of the Rust/Python checkers), not the
evidence for it.

### The ring: corners, clock and exit (P2-P5)

- **Clock (P2).** In all 25 census board fillers the revolution time is exactly `dt = 8(k+1) * swing + b_(r mod 2)` in all
  four directions (100% of 489-849 cycles per direction in [2^26, 2^27]). The slope is the lemma's 2(k+1) steps per cell times
  the four sides; the two-phase offsets b (e.g. RRLRRRR xmax: -110, -62) differ between rules with the same k (seed-dependent
  aspect of the ring), as registered.
- **Footprint (P3).** Reads in [2^26, 2^27] are confined to 0..2k+2; shares of 0..2k+1 are uniform to within 0.09% (max relative
  deviation 0.00083); count 2k+2 is read in at most 0.0083% of steps (about one read per corner per revolution); steps per visited
  cell at 2^27 are 3.998-4.001, 5.994-5.996, 7.994, 9.992, 11.989 for k = 1..5 (the seed and the corner diagonals; two k = 1 rules,
  `RLRRRRRRL` and `RLRRRRRRRL`, sit slightly above 2(k+1), presumably because their seeds hold more excess visits than the corners
  lack; not checked).
- **Corner (P5).** At a convex corner the crawler reads one interior cell (count 2k+2) per revolution, leaving a diagonal
  trail of cells with 2k+3 visits (at the other corners a diagonal with 2k+1; seen in snapshots, not counted). Flipping only
  `T(2k+2)` to L destroys the ring within the first corner (first read above 2k+2 at t0 + 2,956 / 1,962 / 3,477 steps against
  revolutions of 8,058 / 13,882 / 19,690) and the territory falls back to a slow blob (0.76-0.87 M cells after 1e8 steps instead
  of 12.9-25.3 M). So the full predicate is `Pi(k)`: `R^k L R^(k+2)` on counts 0..2k+2. **The corner is not proved**: only
  the edge lemma is a proof; the corner and the revolution map are observed exact on these 25 rules and 3 transplants.
- **Transplant controls (P5a).** `RLRR`, `RRLRRR`, `RRRLRRRR`, which do not fill from a blank board, continue a transplanted
  ring with a bit-identical visit field for 1e8 steps. The ring is an attractor certified by the letters it reads; whether a
  blank board reaches it depends on the seed, i.e. on letters the ring never reads.
- **Exit steps (P4).** The exact quadratics through the 1024/2048/4096 exits are `4G^2 - 49G + 1420` (RLRRRRL),
  `6G^2 - 49G + 773` (RRLRR), `8G^2 - 65G + 2363` (RRRLRRRRR): leading coefficients exactly 2(k+1). They predict all 9 new
  exits on 8192/16384/32768 boards and the 3 census records (h1e10 chunks 57, 50, 33) to the step, e.g. RRRLRRRRR leaves the
  32768 board at 8,587,807,035. The registered B1 failure of the late-highway board check was the `beta G` term: relative
  shortfall `-beta / (2(k+1) G)` = 1.20%, 0.60%, 0.30% for RLRRRRL at G = 1024, 2048, 4096.

### Census membership (P6) and what else fills the plane

446 blank-board runs (the 304 census builders and the 361 rules of length <= 12 satisfying Pi, 219 in both), 2^27 steps on a
16384 board, classified on the last 2^24 steps (`results/p6_analysis.txt`). 12 runs left the board.

- **(a) Necessity failed.** 220 runs show the ring(k) footprint; 218 satisfy Pi(k) and 2 do not: `RRLLLRLLLRLL` (12 visits per cell,
  reads 0..11 uniform, a square anchored at the start cell rather than centred on it) and `RRRLRRLLRRRR` (6 visits per cell with turn
  table `RRRLRR` on counts 0..5). The footprint fixes the visit budget, not the turn table: other crawlers spend the same budget.
- **(b) Sufficiency held:** 218 of 361 Pi rules (60.4%) are rings at 2^27 (by k: 159/256, 42/65, 9/18, 3/7, 3/5, 1/4, 1/3, 0/2, 0/1).
  The other 143 are census blobs (136), log growers (2), escapes (4) and one recognised highway. Which seeds find the ring is not
  predicted here.
- **(c) Q15:** 220 of 304 builders (72.4%) are rings (all of them Pi rules except the two above), 20 (6.6%, below the registered
  10-30%) are two-visit, 64 (21.1%) other.

**Post hoc** (`scripts/posthoc_p6.py` -> `results/posthoc_p6.txt`; criterion chosen after seeing P6: new-cell rate 1/v* and counts
0..v*-1 uniform, nothing required above v*). 272 of the 446 runs are integer-cost fillers. By turn table on counts 0..v*-1:

| v* | table | runs | reading |
|---|---|---|---|
| 2 | `RL` | 20 | the two-visit builders; every one starts `RLL`. `C_0` (one row of 1s over 2s) translates iff `T(0) = L, T(1) = R` (all 124 rules of length 2..6, `results/posthoc_k0.txt`), so in mirror image these edges are the k = 0 crawler. `RLLLRRRL`'s north edge is a row of 1s over 2s with a corner diagonal of 3s (scratch inspection) |
| 2k+2 | `R^k L R^(k+1)` | 219 (k = 1..7) | the proved family: the 218 ring(k) Pi rules plus `RRLRRRRRRLR` (v* = 6, table `RRLRRR`), which the registered ring(2) test rejected for its reads above 6 (max 24, 0.08% of reads) |
| 4, 6, 8 | `RRLR`, `RRRLRR`, `RRRRLRRR` | 1, 13, 3 | **a second family with the reversed table `R^(k+1) L R^k`** at the same cost 2(k+1); `RRRLRRLLL`'s edge reads rows `3311 / 4466 / 6666`, not `C_2` |
| 4-26 | `RLLR`, `RLLRLL`, `RRLRLRRR`, seven singletons | 3, 3, 3, 7 | unexamined |

So the proved crawler is the majority mechanism of the census builders but not the only one; the census "builders" are at least four
crawler families plus 64 non-integer cases (spirals with deep bands, rules that left the board, slow fillers).

## Limitations

- Only the straight edge is proved. The corner gadget and hence the ring's persistence are observed exact (hundreds of revolutions,
  25 rules, three transplants), not proved; nothing guarantees the same corner phase structure at larger sizes.
- P6 classifies one window at 2^27 steps per rule: a Pi rule that has not reached the ring by then counts as a non-ring; late ring
  onsets are not excluded (the 25 board fillers were all rings by 2^26).
- The k = 0 and reversed-table observations are post hoc and only partly inspected. The octagonal spirals of
  `experiments/archive/2026-10-sweeper-generalisation/` (deep outer band) are not shown to be the k = 0 crawler.
- A brief literature search (OpenAlex semantic query on generalised ants and square filling, 2026-10-25) found no mechanism for
  square filling; that is not an exhaustive review.

## Pruning-index outcome and next question

No dead-end signature: the results are positive (a mechanism, a proof for the edge, exact predictions) and the negative part (P6 (a))
is a failed classification criterion, not an excluded rule family. Next questions, unregistered: (1) a corner lemma per k (finite
trace at a fixed corner phase) to make the ring a proved macro-transition; (2) the reversed family `R^(k+1) L R^k`: its crawler
configuration and whether it is related to the first by a symmetry; (3) onset: why 60% of Pi rules find the ring from a blank board
and 40% do not, given that the ring never reads the letters that decide it.
