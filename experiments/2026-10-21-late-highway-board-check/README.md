# Are the axis-aligned late highways board artefacts?

Created 2026-10-21 21:00 +13:00, base `fd03a6d`. Status: **REGISTERED, nothing run yet.**

## Question

Of the 54 late highways in the 1e10/1e11 survivor census (`experiments/2026-10-13-highways-unresolved-rules-1e10-1e11/`,
32768 board), 28 rules are axis-aligned with short periods, unlike 96% of census highways (diagonal). They form an
arithmetic series in the rule `R^k L R R ...`:

| family | k | period | census onset | onset / 2^31 |
|---|---|---|---|---|
| RLRRR..., RLRRRLL... (16 rules) | 1 | 16 | 4.2932-4.2942e9 | 2.00 |
| RRLRR... (7 rules) | 2 | 24 | 6.4395-6.4410e9 | 3.00 |
| RRRLRRRR, RRRLRRRRRR | 3 | 32 | 8.5875-8.5881e9 | 4.00 |
| RRRRLRRR, RRRRLRRRR | 4 | 40 | 1.073e10 | 5.00 |
| RRRRRLRR, RRRRRLRRRR | 5 | 48 | 1.288e10 | 6.00 |

(`RLLLRLRRR`, period 8 diagonal, onset 5.72e9, is outside the series and not part of the prediction.) The 32768 board
has exactly 2^30 cells, so these onsets are `2 (k + 1)` steps per board cell. `notes/frontier-results.md` already
flagged the clusters near multiples of 2^32 as an oddity and read them as shared trajectories; it did not test board size.

## Hypothesis (registered before any run)

**H-artefact.** These rules are board fillers (the census "frame builder" class, ~2-6 steps per cell): they cover the
board at `2 (k + 1)` steps per cell and their "highway" is motion along or off the board edge, not a highway in the
plane. Prediction **B1**: on boards `G` = 1024, 2048, 4096, each of `RLRRRRL` (k = 1), `RRLRR` (k = 2) and `RRRLRRRRR`
(k = 3) reports a highway with the census period and an onset within 1% of `2 (k + 1) G^2 (1 - 0.0003)`, i.e. the onset
scales as `G^2`. **H-real** (alternative): onset is the same on every board (the `confirm` criterion), so on the small
boards either the same onset appears or the ant leaves the board first.

Consequence if B1 holds: 28 of the 54 late highways (and the onset clusters behind the "decade yield" numbers in
`notes/frontier-2026-10-13-results.md`) are artefacts and must be removed; the late-highway rate per decade must be
recomputed. Census rules escaping on a 32768 board at multiples of 2^31 have not been checked on other board sizes
(the B5 confirmation covered only RRLLLRLRL).

## Commands

```bash
cargo build --release --bin sweep_lean
for G in 1024 2048 4096; do printf "RLRRRRL\nRRLRR\nRRRLRRRRR\n" | ./target/release/sweep_lean - - 2000000000 $G > $E/results/board_$G.csv; done
```

## Results

(Appended below; the registration above is not edited.)

### Results, part 1 (appended 2026-10-21 21:25 +13:00)

**B1 as registered: failed on its 1% tolerance, but H-artefact holds unambiguously.** `results/board_{1024,2048,4096}.csv`:
onsets of `RLRRRRL`, `RRLRR`, `RRRLRRRRR` are 4.14e6 / 1.67e7 / 6.69e7, 6.24e6 / 2.51e7 / 1.004e8 and 8.32e6 / 3.34e7 /
1.339e8, i.e. x4 per board doubling, and the escape footprint is the full board (width >= G - 4). The shortfall below
`2 (k+1) G^2` is 1.3%, 0.6%, 0.3% (halving with G: a perimeter term), so the registered 1% band fails at G = 1024, 2048.
H-real is rejected: onsets differ by a factor of 16 between G = 1024 and 4096.

Post hoc classification (`scripts/classify.py`, `results/classify.txt`; footprint >= 0.99 G in both directions, a rule
chosen after seeing the footprints): **25 of the 54 late highways are board fillers** (21 of 38 in (1e9, 1e10], 4 of 16 in
(1e10, 1e11]); the earlier sweeps (`sweep_v2`, `sweep_1B`) have none.

**A second artefact: `RLLLRLRRR`** (period 8, diagonal, not a filler). Re-run on a 65536 board (`results/control_65536.csv`)
it has not escaped by 6e9 steps. `examples/late_highway_board_check_trace.rs` shows both boards identical up to the census
escape (5,723,554,150; `results/rlllrlrrr_32768.csv` reproduces the census row); the "highway" starts at (10186, -2544),
inside the old bounding box, and runs to x = 16383, the old territory's east edge, which coincides with the 32768 board's
last column. On the 65536 board the ant then walks along x = 16384 (north-south, along its own boundary) and the territory
keeps growing slowly (max x 16651 at 5.8e9): a ray over old structure, cut off by the board. `RRLRLR` (control)
reproduces its census onset exactly on 65536 (1,076,356,698).

Trace commands: `./target/release/examples/late_highway_board_check_trace RLLLRLRRR {32768,65536} 1000000000 4000000000
5700000000 5723529364 5723540000 5723554150` and, on 65536, `... 5723560000 5723570000 5723600000 5723700000 5724000000
5730000000 5800000000` (output quoted above; not saved as files).

## Part 2 registration (2026-10-21 21:30 +13:00, before the run)

The other 26 non-filler late highways (all except `RRLRLR`, `RLLLRLRRR`, and `RRLLLRLRL`, which B5 already confirmed on
65536) are re-run on a 65536 board with budget = census steps + 1e8 (`results/recheck_specs.txt`). **B2**: at least 24 of
26 (>= 90%) reproduce the census period, drift and onset exactly. Below that, the late-highway counts carry a second
artefact class of non-negligible size. Confidence ~70%.

```bash
bash experiments/2026-10-21-late-highway-board-check/scripts/recheck.sh   # results/recheck/RULE.csv, recheck.log
```

## Figure: board fillers vs genuine highways (added 2026-10-21)

`uv run experiments/2026-10-21-late-highway-board-check/scripts/render.py [--ray]` builds
`examples/late_highway_board_check_render.rs`, runs it (snapshots in `scratch/render/`, ~15 s) and writes
`results/fillers_vs_highways.png`. Rows: the filler `RLRRRRL` on 1024 and 2048 boards (a growing square that covers
99% of the board before it leaves, at 4.15e6 and 1.67e7 steps: x4 for x2 board), then the genuine highway `RRRLLLRRRR`
(census onset 4,146,461) on the same boards (a blob covering 3.7% / 1.1% of the board, leaving along one diagonal arm
at 4.26e6 / 4.39e6, the difference being only the arm's extra length to the bigger board's corner). `--ray` adds
`RLLLRLRRR` on the 32768 board (5.7e9 steps). Deterministic; no seeds.

### Part 2 results, provisional (appended 2026-10-22 07:50 +13:00; 19 of 26 rechecks finished, 7 running)

`results/recheck/*.csv` (`sweep_lean`, 65536 board, binary sha256 in `results/recheck/recheck.log`; the run was
interrupted once and resumed, finished rules are skipped, so no row is from a resumed run). **All 19 finished rechecks
reproduce the census period, drift and onset exactly.** B2 (>= 24 of 26) cannot fail on the 19 alone; it is scored when the
last 7 (onsets 3.2e10-6.1e10, all in (1e10, 1e11]) finish.

Ledger (`scripts/classify.py` -> `results/classify.txt`): of the 54 reported late highways, **25 are board fillers, 1 is a
board-truncated ray (`RLLLRLRRR`), 21 are confirmed on a 65536 board** (19 rechecks plus `RRLRLR` and, from B5,
`RRLLLRLRL`), **7 are pending**.

| decade | survivors | reported highways | artefacts | genuine (confirmed) | pending | genuine yield (reported) |
|---|---|---|---|---|---|---|
| (1e9, 1e10] | 807 | 38 | 22 | 16 | 0 | **1.98%** (4.71%) |
| (1e10, 1e11] | 732 | 16 | 4 | 5 | 7 | **0.68-1.64%**, 1.64% if all pending confirm (2.19%) |

With the earlier decade (1e8, 1e9] at 12/854 = 1.4% (`highway_stats.txt`), the three decades are statistically
indistinguishable: Fisher exact p = 0.45 for 1.4% vs 1.98%, p = 0.70 for 1.98% vs 1.64%. (Against the lower bound
0.68%, p = 0.029; the pending rules decide this.) **The "thinning tail" reading in the notes (first 4x, then 2x per decade)
came from the artefacts**: the corrected counts are consistent with a flat rate of about 1.5-2% of survivors per decade
from 1e8 to 1e11. The board fillers were also counted as highways rather than as escapes without a highway; corrected,
escapes without a highway are 59/807 = 7.3% in (1e9, 1e10] (was 37, 4.6%) and 18/732 = 2.5% in (1e10, 1e11] (was 14, 1.9%);
the fillers are growing rules that leave any finite board, not highways.

Census procedure lesson: an escape with a periodic tail is not a highway unless (i) the escape footprint is well short of
the board in the direction perpendicular to the drift (fillers fail this) and (ii) the onset is board-independent
(`confirm` on a second board size; the ray fails this). The 1e8/1e9 sweeps have no full-board footprints, but (ii) was
never applied to them.

### Part 2 results, final (appended 2026-10-22 09:25 +13:00)

**B2 held: 26 of 26** re-run late highways reproduce the census period, drift and onset exactly on a 65536 board
(`results/recheck/*.csv`; the run was interrupted twice and resumed, each rule ran uninterrupted from a blank board;
binary sha256 in `results/recheck/recheck.log`, unchanged across relaunches). With `RRLRLR` and `RRLLLRLRL` confirmed
separately, all 28 non-artefact late highways are genuine. Final ledger (`results/classify.txt`, commit `ecab728`):

| decade | survivors | reported | board fillers | ray | genuine | genuine yield (reported) |
|---|---|---|---|---|---|---|
| (1e9, 1e10] | 807 | 38 | 21 | 1 | 16 | **1.98%** (4.71%) |
| (1e10, 1e11] | 732 | 16 | 4 | 0 | 12 | **1.64%** (2.19%) |

Against (1e8, 1e9] at 12/854 = 1.41%: Fisher exact p = 0.45 (1.41% vs 1.98%) and p = 0.70 (1.98% vs 1.64%). The three
decades are consistent with a flat per-decade yield of about 1.4-2.0% of survivors; nothing here supports a thinning tail.
One caution against over-reading: three decades and 12-16 events each cannot exclude a slow decline either (a factor
of 0.6 per decade would also fit within the Poisson errors).
