# Knockout map: hypotheses before measuring

Written 2026-10-12, before any knockout run. Only the territories have been
regenerated (examples/dump.rs, 2^24 steps: 7,264 visited cells for
RRRRRLLLLLL, 11,144 for RLLLLRRRRLR, matching the published ~7,000/~11,000).
No tether value for the intact field, patch or control has been measured in
this session, so predictions below are relative to the intact baseline B.

## Question

pattern-fields-results.md says what holds the hard ant tracks exact cells, not
local statistics, and guesses the carrier is long-range return paths. Which
5x5 patches of the real territory does the home depend on, and do they lie on
the routes of the intact ant's excursions?

## Protocol (fixed now)

- Rules: RRRRRLLLLLL and RLLLLRRRRLR. Field: experiments/archive/2026-10-knockout-maps/dumps/RULE.grid. Run as
  published: fresh ant at home, heading north, 2^26 steps, outcomes over the
  last quarter (last 16 of 64 blocks) via examples/transplant.
- Knockout: permute the colours of the visited cells inside one 5x5 patch
  among themselves (colour counts kept). Unvisited cells stay blank, so the
  territory's edge shape never changes. Coarse grid: tiles of 5x5 with origin
  at the territory's bounding-box corner; a tile counts if it holds >= 5
  visited cells (about 280 and 440 tiles).
- "Seeds": the ant is deterministic and transplant's seed only matters in
  `shuffled` mode. So 3 seeds = 3 different permutations of the patch. The
  intact field has zero variance and a single run B.
- Primary outcome: tether = share of time within 10 cells of home
  (`near_home`), mean over the last 16 blocks. Also recorded: `near_prev`
  (own) and spread, so a tether that moved is not mistaken for a lost one.
  Effect of a patch: loss = B - tether.
- Dose covariate per patch: fraction of cells whose colour actually changed
  (a near-uniform tile barely changes when shuffled).

## Controls

1. Blank-cell knockouts. Permuting an all-blank patch changes nothing, so the
   field and result are bit-identical to the intact run. Predicted loss = 0
   exactly. This is a degenerate determinism and pipeline check, not a noise
   estimate. (Alternative I have NOT used: writing territory-like colours into
   blank ground outside the edge. That changes the colour counts and the
   shape, and would be a different experiment.)
2. Random swap of the same size: choose 25 visited cells at random anywhere in
   the territory and permute them among themselves. This is the real null:
   any change near the ant's path can alter the trajectory chaotically.
   100 draws per rule, 1 permutation each, giving a null distribution of loss
   at equal dose but without spatial clustering. It also tests whether
   contiguity matters.

## Route density (from the intact field)

Run the intact field as published (same run as B). An excursion is the stretch
of steps between leaving r <= 10 of home and next re-entering it. Route
density of a tile = excursion steps spent in the tile per cell. Total
occupancy of a tile = all steps in the tile per cell, and distance of the tile
from home are the confounds. Statistic: Spearman rho between tile loss
(mean over 3 permutations) and route density, plus the partial rho controlling
for log occupancy and distance from home, plus dose. Raw rho alone is not
evidence: near-home busy tiles would pass for return routes.

## Hot spot definition (fixed now)

A tile is hot if its mean loss over 3 permutations exceeds the 95th percentile
of the random-swap null and at least 2 of the 3 permutations individually
exceed it. Reproducibility check: correlation across tiles between two
independent permutations' losses.

## Refinement (after the coarse map)

Slide 5x5 windows at stride 1 inside and around hot tiles, then 3x3 and 1x1
inside the best window, 3 permutations each.

## Predictions

Bounds from the dose-response data: keeping a random 97% of cells nearly
fully tethers, and 90% tethers weakly. A 5x5 tile is 0.2-0.4% of the
territory.

- P1 (mostly flat). Most tiles (>= 80%) lose no more than the null's 95th
  percentile. The sum of single-tile losses is far smaller than B. No single
  tile removes the tether by itself, with the possible exception of tiles at
  the home.
- P2 (few, reproducible hot spots). I expect 3-10% of tiles hot, clustered
  rather than isolated, if the return-path idea is right. Split-permutation
  reproducibility across tiles r >= 0.4.
- P3 (route density). If return paths carry the hold, partial rho between
  loss and route density is positive, >= 0.15 after controlling occupancy,
  distance and dose. My own guess is that this is optimistic: I expect raw rho
  with occupancy to dominate (raw rho with route density >= 0.4, mostly
  explained by occupancy) and the partial rho to be small (0 to 0.15).
- P4 (random swap vs patch). Equal-dose random swaps have a smaller mean loss
  than contiguous patches only if damage is spatially cooperative. I expect
  similar mean loss; a clearly smaller loss for scattered swaps would suggest
  contiguous structure (paths) matters.
- P5 (control). Blank-cell knockouts lose exactly 0.

## Falsifiers

- Return-path idea fails: partial rho with route density <= 0.05 (or its
  bootstrap interval spans 0) after occupancy and distance control.
- No localised dependence: hot tiles do not reproduce across permutations
  (reproducibility r < 0.2), or the hot fraction is within the null's 5%.
  The hold is then diffuse/chaotic and the map says nothing about location.
- The tether effect of a tile is within the null at every tile but the
  home-adjacent ones: the dependence is occupancy, not route structure.

## Caveats

- One territory per rule at one age (2^24); one fresh-ant trajectory defines
  both baseline and route density.
- Deterministic chaotic runs: a single outcome per field. The null is the
  only noise estimate.
- near_home counts time only near the original home; a tether that forms
  elsewhere reads as zero, hence the near_prev and spread columns.
