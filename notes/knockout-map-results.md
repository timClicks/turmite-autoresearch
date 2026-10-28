# Knockout map: results

Run 2026-10-12/13. Predictions written beforehand, unchanged:
knockout-map-hypotheses.md.

Code: examples/knock.rs (runner; its intact run agrees with examples/transplant
to 4 digits: near_home 0.4737/0.4938, spread 14.378/14.434), experiments/archive/2026-10-knockout-maps/scripts/knockout.py
(job generation), experiments/archive/2026-10-knockout-maps/scripts/knockout_analyse.py (statistics), experiments/archive/2026-10-knockout-maps/scripts/knockout_checks.py
(ad hoc checks quoted below). Data: experiments/archive/2026-10-knockout-maps/results/knockout_RULE_*.csv/json (coarse and
refine rows, tile table, hot tiles, summary). Fields: experiments/archive/2026-10-knockout-maps/dumps/RULE.grid from
`dump RULE 24 dumps` (7,264 and 11,144 visited cells; note experiments/archive/2026-10-tether-rules/dumps_f/ is a
different age, 2^26).

Recipe, from the repo root in WSL (no commit exists yet; Cargo.lock as is):

    export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
    export KNOCK=$HOME/turmite-target/release/examples/knock
    cargo build --release --examples      # CARGO_TARGET_DIR=$HOME/turmite-target
    for r in RRRRRLLLLLL RLLLLRRRRLR; do
      $CARGO_TARGET_DIR/release/examples/dump $r 24 dumps
      uv run experiments/archive/2026-10-knockout-maps/scripts/knockout.py coarse $r && uv run experiments/archive/2026-10-knockout-maps/scripts/knockout_analyse.py $r
      uv run experiments/archive/2026-10-knockout-maps/scripts/knockout.py refine $r
    done
    uv run experiments/archive/2026-10-knockout-maps/scripts/knockout_followup.py      # centred geometry, full-tile P4, fresh permutations

The coarse and refine runs were made with the system Python (numpy 1.26.4,
scipy 1.11.4); rerunning the analysis under uv reproduced every summary
number to the last 1-2 digits of float precision. `cargo test --release`
passes (all suites). knock.rs has no property test of its own: its loop is a
copy of transplant's and agrees with it on the intact fields (to 4 digits),
and a 1-thread rerun matches the 8-thread rows byte for byte.

Protocol as pre-registered: fresh ant at home, 2^26 steps, outcome over the
last quarter; patch = permute colours of the visited cells inside the patch;
3 permutations per tile (the ant is deterministic, so "seeds" are
permutations); null = 100 random 25-cell swaps per rule. The runner is
deterministic: a 1-thread rerun reproduces 7 sampled rows of the 8-thread run
byte for byte. No run left the board.

Baselines B (near_home, intact field): 0.4737 (RRRRRLLLLLL), 0.4938
(RLLLLRRRRLR). Loss = B - near_home.

## Answer

The hold depends on a few reproducible places, not on route structure that
this design can resolve. Shuffling one 5x5 patch usually costs nothing beyond
noise, but 3.5% of tiles are real hot spots, within about 20 cells of the
tether centre (the intact ant's mean position), and the worst 5x5 windows
remove about 20-30% of the tether (confirmed with fresh permutations). The excursion-route prediction (P3) is not supported once
occupancy is controlled.

| | RRRRRLLLLLL | RLLLLRRRRLR |
|---|---|---|
| coarse tiles (>= 5 visited cells) | 310 | 477 |
| tiles within null p95 (mean of 3) | 94.8% | 95.6% |
| hot tiles (mean > null p95 and 2 of 3 above single p95) | 11 (3.5%) | 17 (3.6%) |
| hot fraction expected under the null, same rule (simulated) | 0.7% | 0.7% |
| worst coarse tile loss (of B) | 0.099 (21%) | 0.120 (24%) |
| worst 5x5 window after stride-1 refinement | 0.124 at (-8,-12) | 0.151 at (7,6) |
| worst 3x3 window | 0.072 at (-7,-10) | 0.089 at (-1,7) |
| 5x5 swap null: mean loss / p95 | 0.0093 / 0.033 | 0.0094 / 0.028 |
| 3x3 swap null p95 (refine) | 0.0135 | 0.0236 |
| blank-cell tiles, loss | exactly 0 (n=20) | exactly 0 (n=3) |

Windows are located by (x, y) of the top-left corner relative to home, y
down (north is -y).

## Against the predictions

- P1 (mostly flat): yes. Over 94% of tiles are inside the null; no single
  coarse tile removes more than about a quarter of the tether.
- P2 (few reproducible hot spots): yes on count (3.5-3.6%, null 0.7%) and
  clustering. Reproducibility across permutations: Pearson 0.91/0.93 but
  that is carried by the few big tiles; Spearman 0.41/0.53 (met, narrowly, my
  bound was 0.4).
- P3 (route density): not supported. Spearman rho(loss, route) 0.31/0.44, but
  rho(loss, occupancy) is 0.28/0.47 and rho(route, occupancy) 0.88/0.92. After
  controlling log occupancy, distance from home and dose, partial rho =
  0.127 (bootstrap 95% CI -0.04 to 0.26) and 0.027 (-0.11 to 0.20). Both
  intervals contain 0 and neither reaches my 0.15 bound, so by the stated
  falsifier the return-path idea fails here, as I half expected.
- P4 (patch vs swap): not as predicted. Restricting to full tiles (all 25
  cells visited: 264 and 417 tiles; the mean tile has 23.4 visited cells, so
  edge tiles had permuted fewer cells than a swap), mean loss is 0.0060/0.0060
  against 0.0093/0.0094 for scattered 25-cell swaps, at similar dose (changed
  fraction 0.85 vs 0.86, and 0.74 vs 0.82). So a contiguous patch does not
  hurt more than the same number of scattered cells; if anything less. I
  have no tested reason for that. The hottest windows are the exception.
- P5 (blank control): exactly 0, as it must be. It checks the pipeline only.

## What the hot places look like

Distances in the pre-registered analysis are from the start cell. The intact
ant's mean position is not the start: (0.54, -5.49) for RRRRRLLLLLL and
(1.63, 4.53) for RLLLLRRRRLR, so I recomputed everything about that tether
centre (experiments/archive/2026-10-knockout-maps/scripts/knockout_followup.py).

- Loss by tile ring about the start cell, mean over tiles: r < 10: 0.011/0.015;
  10-15: 0.023/0.038; 15-20: 0.013/0.012; 20-30: 0.0065/0.006; beyond 30:
  0.002/0.003. About the tether centre it is monotone, highest in the middle:
  < 10: 0.024/0.034; 10-15: 0.021/0.025; 15-20: 0.013/0.012; 20-30:
  0.005/0.007; beyond 30: 0.002/0.003. So my first reading, "a band just
  outside the home disc", was partly an artefact of the offset centre: the
  sensitive region is a disc of radius about 15-20 around the tether centre,
  with its peak in the middle.
- Hot tiles by ring about the tether centre (< 10 / 10-15 / 15-20 / 20-30):
  4/5/2/0 for RRRRRLLLLLL and 6/7/3/1 for RLLLLRRRRLR.
- Shape differs between the rules. RLLLLRRRRLR's 17 hot tiles are spread
  around the tether centre (mean offset (-0.8, -0.2); 8 compass octants hold
  5,2,1,4,2,2,1,0), a rough disc. RRRRRLLLLLL's 11 are lopsided even about
  its tether centre: mean offset (-1.7, -5.2), all in the northern half
  (octant counts 0,0,0,2,2,2,4,1), nothing south or east of the centre.
- Route share: 42% of the intact ant's excursion steps (r > 10 from the start)
  fall in r = 10-15, 25% in 15-20, 23% in 20-30. Outside r = 10 all steps are
  excursion steps, so route density and occupancy are almost collinear
  (rho 0.88/0.92) there.
- Adding the centred distance as another control leaves the partial rho for
  route density unchanged: 0.128 and 0.027 (0.127 and 0.027 with the
  pre-registered controls), so item P3 stands.
- Knocking out a hot window weakens the tether where it was: own loss
  averages 0.058 and 0.045 over hot tiles, close to their near_home loss
  (mean 0.066 and 0.055), so the ant is not re-tethering elsewhere (that
  would keep own high), and the spread barely moves (15.4 against 14.4).
- Even 9 cells can matter: the best 3x3 windows lose 0.07-0.09 (15-18% of B)
  against a 3x3 null p95 of 0.014-0.024.

### Confirmation of the winners

The top 5 refined windows of each size were rerun with fresh permutations
(seeds 4-6, never used for selection). Mean loss, selection -> fresh:
RRRRRLLLLLL 5x5: 0.124->0.122, 0.119->0.136, 0.118->0.093, 0.115->0.129,
0.113->0.091; 3x3: 0.072->0.071, 0.072->0.062, 0.071->0.080, 0.071->0.055,
0.065->0.050. RLLLLRRRRLR 5x5: 0.151->0.147, 0.124->0.096, 0.121->0.092,
0.121->0.118, 0.120->0.133; 3x3: 0.089->0.075, 0.081->0.070, 0.080->0.105,
0.078->0.054, 0.075->0.073. All stay far above the null p95 (5x5 0.033/0.028;
3x3 0.014/0.024); the winner's curse is modest, the largest drops being
0.03-0.04 (RLLLLRRRRLR 5x5 (8,7) and (-1,6)). Honest range for the worst 5x5
window: 0.09-0.15, that is 20-30% of the tether.

## Caveats

- Refinement ran only around hot tiles, so the map of the rest is the coarse
  one. The selected losses are upper estimates (winner's curse), but the
  fresh-permutation check above shows the effect is small here.
- Each field gives one deterministic outcome; the null is the only noise
  estimate, and 100 swaps give a rough tail (p95 from 100 draws).
- The route/occupancy collinearity means the partial correlation has little
  power to find a route effect; a null here is not strong evidence against
  return paths, only that this test does not show them.
- near_home is measured around the original home; hot-tile knockouts keep the
  tether at the same place (own and spread), so this was not an artefact.
- One territory per rule, at age 2^24. Coarse grid origin fixed at the
  bounding-box corner; the tile offset was not varied.

## Next, not done

- Why is RRRRRLLLLLL's hot region one-sided (north of its tether centre)? Is
  it tied to a fixed direction in the rule's geometry or to where this
  particular field happened to build up? A second territory age (the 2^26
  grids in experiments/archive/2026-10-tether-rules/dumps_f/) would show whether the lobe moves.
- Is the sensitive disc set by the 10-cell tether radius or by the excursion
  scale? Redo the loss map with near_home measured at radius 6 and 15.
- A route definition that breaks the collinearity: last exit-to-return path
  of each excursion, or cells on the shortest homeward legs, instead of all
  steps outside r = 10.
