# Which part of the prefix carries kappa? Run structure of the opening (2026-10-20)

## Question
`../2026-10-kappa-spread-features/` found the predictable part of ln kappa is in the first 8 letters (held-out R^2 0.62) and not in the
last 8 or in composition. Earlier work (`../2026-10-kappa-leadrun-fresh/`) tied ln kappa to the *lead* (length of the initial run of R,
slope +0.15 to +0.24 per step, with a collider caveat). How much of the prefix signal is run structure of the opening?

## Design (registered before running, 2026-10-20 03:50 +13:00, git 014f2c2)
- Same train / test as the sibling experiment: 2185 stationary blob census rules (`probe_summary.csv`, ln kappa), 162 fresh stationary
  rules (`prefix_audit_predictions.csv`, `target`, cohort stationary / loo / linear), disjoint by rule; strict held-out R^2 against the training mean.
- A rule is split into maximal runs of equal letters (e.g. `RRLLLRL` -> R2 L3 R1 L1). Key `Rk` = the lengths of the first k runs
  (k = 1, 2, 3, 4), so `R1` is the lead alone. Group-mean lookup on the key, falling back to fewer runs with >= 3 training rules, then
  the training mean. Reference: the 8-letter prefix lookup P8 from the sibling experiment, recomputed here.
- Bootstrap over test rules, 2000 resamples, seed 20261020.

## Predictions (written before the run)
- **H1:** the lead alone (`R1`) has test R^2 >= 0.15.
- **H2:** the first two runs (`R2`) reach R^2 >= 0.40.
- **H3:** the first three runs (`R3`) come within 0.10 of P8.
- **H4:** no run-structure key exceeds P8 by more than 0.05 (the 8-letter prefix contains them).

Failures are reported as failures. Anything chosen after seeing results is labelled post hoc.

## Results (`results/runs.txt`; 2185 train, 162 test, 0 in both)
| key | strict held-out R^2 | 95% CI | minus P8 |
|---|---|---|---|
| P8 (first 8 letters) | +0.624 | [+0.472, +0.732] | |
| R1 (lead alone) | -0.004 | [-0.034, +0.013] | -0.628 |
| R2 (first two runs) | +0.246 | [+0.120, +0.369] | -0.378 |
| R3 (first three runs) | +0.337 | [+0.202, +0.482] | -0.288 |
| R4 (first four runs) | +0.475 | [+0.286, +0.627] | -0.149 [-0.260, -0.047] |

**H1 FAILED** (lead alone is at 0, not >= 0.15). **H2 FAILED** (0.25 < 0.40). **H3 FAILED** (R3 is 0.29 below P8). **H4 HELD**
(no run key beats P8).

**Reading.** The lead (initial R run) carries no *unconditional* information about ln kappa on these fresh rules; this is
consistent with the 2026-10-19 reconciliation, which found the lead-kappa association appears at fixed area and is reproduced
by conditioning on the area collider, not by a direct lead effect. The predictive information in the prefix accumulates over
successive runs (0.25, 0.34, 0.48 for two to four runs, against 0.62 for eight letters); at least four runs (and still not all of
the eight-letter prefix) are needed to recover most of it. So the prefix signal is a distributed property of the opening, not a
single early run length. Not tested: which specific runs or letter patterns dominate (a per-position or interaction analysis),
letters 9 onward (suffix and composition were tested in the sibling experiment and carry nothing), and whether the key
structure in R4 vs P8 differs by more than information content (R4 keys are coarser or finer than 4-letter prefixes depending on run
lengths, so the R vs P comparison is not matched on number of groups; no group-count control was run).

## Reproduce
`uv run experiments/archive/2026-10-kappa-prefix-runs/scripts/runs.py` -> `results/runs.txt`, `results/runs.json`.
