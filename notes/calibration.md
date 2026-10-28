# Calibration against the rotor (Eulerian) walker

Purpose: check that the instruments used on the ants (the probe, the fits,
the windows) give the right answers on a walker whose answers are known.

## Model

Rotor walker as in Kapri & Dhar (2009), arXiv:0906.5506: each site holds an
arrow (N, E, S, W), i.i.d. uniform initially. At each step the arrow at the
walker's site rotates 90 degrees clockwise and the walker steps along it.
Bou-Rabee & Peres (2026), arXiv:2608.23545, prove for this model that the
range grows as t^(2/3) with a deterministic limit shape (radius ~ t^(1/3)).

Implementation: `src/walkers.rs` (`Rotor`), checked step-for-step against an
independent HashMap version (`reference::Rotor`) by property tests in
`tests/probe.rs`; a mutation (anticlockwise rotation) is caught. The
statistics tool `examples/rotorstats.rs` was cross-checked against the
reference rotor on (seed, N, R^2, S) for three seeds and three N: identical.

Negative control: simple random walk (`RandomWalk`).

## Part A: the ant pipeline applied to the rotor (experiments/archive/2026-10-calib-instrument-calibration/results/calib_partA.json)

64 rotor seeds, 2^27 steps, fitted over the same window as the ants (windows
ending 2^20..2^26). Random walk: 16 seeds, 2^24 steps, a 7-octave window.

- Width exponent: 0.326 (sd 0.013 between seeds). Radius-of-gyration exponent:
  0.339 (sd 0.0055). True value 1/3.
- Area exponent: 0.687, true 2/3. Finite-window bias of about +0.02.
- Edge (perimeter-vs-area) exponent: 0.52, same as the ants. So the ants'
  0.52 is not evidence of a rough-edge correction to the exponent. Corrected
  on the page.
- c: 0.498, flat in time. kappa: 2.0, flat.
- Random walk: area exponent 0.93, edge exponent 0.93, fill 0.17, width
  exponent 0.50 with sd 0.09. Clearly distinguished.
- c is not diagnostic on its own: the random walk gives 0.44.

## Part B: reproducing Kapri & Dhar (experiments/archive/2026-10-calib-instrument-calibration/results/calib_partB.json, calib_contour.json)

1000 seeds to 1e7 steps; 60000 seeds to 1e6 steps for the contour.

- Displacement exponent, local slopes between checkpoints:
  0.263, 0.315, 0.306, 0.346, 0.332, 0.334 -> 1/3. K&D: 0.33 +- 0.01.
- Boundary-width exponent, local slopes: 0.19, 0.168, 0.150, 0.146, 0.137,
  0.132. K&D: 0.136, and they note the drift.
- Exactly-4 visits in the last 4S steps: 89.3% of visited sites.
- S / N^(2/3): 4.07 -> 5.69 from 1e4 to 1e7, still rising; coefficient of
  variation 8.9% -> 1.8%, consistent with a deterministic limit.
- Contour radius at 1e6: see calib_contour.json and the page.

## Part C: within-rule noise for ants (experiments/archive/2026-10-calib-instrument-calibration/results/calib_patched.json)

40 chaotic rules x 12 random 5x5 starting patches, 2^27 steps.

- Within-rule sd: width exponent 0.016, radius exponent 0.011, area 0.020.
- Between-rule true sd: 0.004 (ICC 6.5%), 0.006 (21%), 0.014 (33%).
- Grand means: width 0.3331, radius 0.3362.

## Consequences for the ant claims

- "Chaotic ants grow as t^(1/3)": consistent with exactly 1/3, given the
  rotor's behaviour in the same window.
- The edge exponent 0.52 is a finite-time effect, not a correction.
- Most of the spread of fitted exponents across ant rules is per-run noise;
  small genuine rule differences remain, which may be different rates of
  convergence rather than different exponents.
- Area exponents from 7-octave windows overshoot by about 0.02.

## Falsification instrument caveat (2026-10-22)
The adversarial harness in `src/falsify.rs` must not pool adaptive candidates and heterogeneous
attack families into a binomial confidence interval. Probabilistic highway claims remain
Unsupported until an IID sampling distribution is registered. See
`experiments/active/2026-10-falsification-harness/README.md` for the correction and regression recipe.
This is an instrument change, not a new growth-law measurement.
