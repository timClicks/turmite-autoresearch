# From excursion cutoffs to a mechanism: prospective research avenues

Written 2026-10-15 21:18 +13:00, base commit `da88e61`, dirty tree.
Recorded at the user's request after the independent-area analysis. These are
proposals, not completed experiments or fully specified preregistrations.
Freeze cohorts, seeds, area targets, windows, estimators and decision thresholds
in a new experiment README before measuring. Do not use these proposals to
reinterpret earlier failed predictions as passes.

## Motivation

The [independent-area test](../experiments/archive/2026-10-independent-area/README.md)
strengthened the cutoff–kappa association by separating trajectories used for
area matching, boundary activity and excursion cutoffs. It did not remove
measurement error in area, rule selection or escape conditioning, and it did
not establish causality. The earlier matched-area noise-floor gate remains
failed. The next work should distinguish mechanisms rather than add another
correlation on the same sample.

## 1. Sample at fixed territory size rather than fixed time

**Question.** Does the cutoff association persist when territory size is set
by design rather than matched using noisy rule means?

**Design.** Record each trajectory when it first reaches prescribed visited
areas. Measure excursions and boundary activity over narrow, predeclared area
bands, recording elapsed steps and the changing perimeter-to-area ratio.
Use fresh seeds and assess rule-level variation; do not pool correlated
windows as independent observations. Define how excursions crossing band
boundaries are handled before running. First-passage sampling changes the
ensemble: slow trajectories and rules that fail to reach a target must be
reported, with explicit computational budgets and censoring.

**Prediction.** At the same area, rules with shorter normalized extreme
excursion cutoffs still have higher kappa. A null or reversed association
would weaken the interpretation of the existing fixed-time association as
something beyond size and growth history.

**Limit.** Equal area does not fix shape, perimeter, field age or internal
colour structure. Report these differences rather than treating matched size
as a complete causal control.

## 2. Separate return frequency from boundary residence time

**Question.** Does higher boundary occupancy come from shorter interior
excursions, longer boundary episodes, or both? Do rare long excursions carry
the differences between rules?

**Design.** Partition steps into consecutive boundary and interior episodes
using the probe's boundary definition at the start of each step. Record full
boundary-to-interior-to-boundary cycles, including incomplete cycles at both
window edges. With boundary duration D and interior duration T, complete-cycle
occupancy is sum(D) / sum(D + T); obtain exact finite-window occupancy by also
accounting for incomplete episodes. Reconstruct the measured boundary fraction
before normalizing by the same P/A convention used for kappa. This accounting
identity checks instrumentation; it is not itself an explanation.

**Prediction.** If the excursion-tail mechanism is useful, between-rule changes
in the interior duration contribution, especially the longest episodes,
should quantitatively account for differences in boundary occupancy beyond
changes in boundary residence. Define tail bands and a held-out prediction
test in advance. A shorter maximum or high quantile alone need not reduce
mean return time: the tail's probability mass matters too.

**Discriminating failure.** If boundary residence explains the variation, or
tail contributions fail to predict held-out occupancy after size and geometry
controls, the cutoff is more plausibly a marker than the proposed carrier.
Reconcile this with the prior null results for typical excursions and edge
dwell in [the kappa programme](../experiments/archive/2026-10-kappa-rule-space/README.md);
do not simply repeat those measurements under a new name.

**Controls.** Calibrate episode accounting on oracle-checked short paths,
then rotor and random-walk controls. Check censoring and changing-boundary
effects explicitly; no assumption of independent or stationary cycles is
needed for finite-window accounting.

## 3. Connect mutation position to excursion dynamics

**Question.** Do early rule letters affect growth more strongly because they
alter long interior trapping episodes?

**Design.** Extend the existing paired single-letter mutation design to record
cycle durations and tails, preferably at the area targets above. Use common
patch seeds for each base–mutant comparison; analyse uncertainty by base rule.
Compare early and late positions while reporting letter transition, rule
length, drift, escapes and exclusion rates. The existing mutation pilot is
motivation, not an independent confirmation of a new tail prediction.

**Prediction.** Early mutations produce larger changes in the interior tail
contribution than late mutations, and those changes predict the direction of
the kappa change. A stronger mechanism would predict the magnitude on held-out
bases using the cycle decomposition.

**Discriminating failure.** Reproducible mutations that change kappa while
leaving the relevant excursion-duration distribution unchanged would challenge
the tail mechanism. A null tail change is informative only if uncertainty is
small enough to exclude the change required by that mechanism. Conversely,
joint changes in kappa and tails do not establish mediation: a mutation also
changes the evolving field and geometry.

## Priority

Start with fixed-area sampling and cycle accounting together. They address
the remaining size concern and identify which time budget carries the
boundary-occupancy difference. Then use mutations to challenge the resulting
quantitative prediction. No new simulation or literature review was performed
to write this note; no novelty claim is made.

## Scaffold follow-up — 2026-10-15 21:27 +13:00

Fixed-area sampling and cycle accounting now have a dedicated
[experiment scaffold](../experiments/archive/2026-10-fixed-area-cycles/README.md),
including a [fresh-agent handoff](../experiments/archive/2026-10-fixed-area-cycles/HANDOFF.md),
draft plan, candidate config and output schema. It contains no new measurements
and is not a frozen preregistration.

## Fixed-area primary result — 2026-10-15, continuation

The [fixed-area experiment](../experiments/archive/2026-10-fixed-area-cycles/README.md)
now has a frozen registration and completed primary analysis: 44 selected T1b
rules, 64 fresh seeds each, area bands beginning at 32768 and 131072.
All primary coverage, quantile-count, censoring and reliability gates pass.
The registered primary association prediction **fails** its both-band rule:
mean cross-seed Spearman -0.285 (95% rule-bootstrap interval [-0.558,-0.005])
at the smaller area misses <= -0.30; the larger-area value is -0.814
([-0.908,-0.665]). Secondary held-out prediction **passes**, with R2 gains
+0.336 ([0.115,0.578]) and +0.544 ([0.316,0.822]) beyond the registered
boundary-residence/P-A baseline. Bootstrap: 2000 rule draws, seed 20261016.
Recipe and exact outputs are in that README and `results/analysis.prod16.json`;
commands: `uv run experiments/archive/2026-10-fixed-area-cycles/scripts/audit.py --run prod16`,
then the corresponding `scripts/analyse.py --run prod16` (WSL/uv).

This supports incremental prediction within the selected cohort, especially
at the larger area, while leaving the primary failure intact. It does not show
that tail time burden causes the difference: the frozen feature is q999,
not a direct time-burden measurement, and equal area does not control shape,
age or colour field. Prior failed noise-floor and tomography predictions remain
failed. A fresh-arrival band edge can fill an interior hole; zero observed
interior clipping is empirical rather than guaranteed. Full all-seed production
thread replay remains unverified; see the experiment's validation scope.

The completed 1/8-width sensitivity uses the same seeds and gives P1 -0.417
([-0.651,-0.132]) / -0.815 ([-0.905,-0.661]), and P2 gains +0.488
([0.219,0.767]) / +0.530 ([0.300,0.777]); both sensitivity tests pass.
This shows the smaller-area primary conclusion depends on band width; it is
not an independent replication and does not replace the failed primary test.
Final combined results are `results/analysis.json`; the executed notebook and
figure are linked in the experiment README. All 5632 runs pass the accounting
audit; the 88-spec thread replay passes, with its limited scope stated.
