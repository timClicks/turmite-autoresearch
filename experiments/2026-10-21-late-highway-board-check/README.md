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
