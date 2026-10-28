# Draft research plan

Created 2026-10-15 21:27 +13:00 · da88e61 · no measurement yet.
All numerical settings here are candidates, not frozen preregistration.

## A. Sampling ensemble and budget

Start with the 44 rules in the committed T1b input (sorted unique strings).
This selected cohort tests persistence of an existing lead; it is not a census
or new-rule validation. Fresh candidate simulation seeds: 701..712; search
prior specs to verify no reuse before freezing. Patched starts, patch radius 2.
Proposed pilot: first four lexicographically sorted cohort rules, seeds 701..704;
do not use pilot seeds in confirmatory production (candidate 705..716 instead).
Include rotor and random walk using the same numerical seed list.

Candidate area bands [2^15, 2^15 + 2^11) and [2^17, 2^17 + 2^13),
width 1/16 of entry area. Pilot a 1/8-width sensitivity, using independent
trajectories if its results influence design. Step budget 2^28 per trajectory,
board side 8192, no unbounded retries. Review feasibility in the pilot.
Use at most four concurrent dense-grid jobs initially; measure peak memory
before raising concurrency. Reuse one trajectory across its bands, reporting
repeated-measure dependence. Not reaching a band is an outcome, not an exclusion
that may disappear from the denominator.

## B. Exact step and band convention

Let state t mean the state after t moves, with ever-visited area A_t, perimeter
cell count P_t, and walker position x_t. Origin is visited at t=0. Colours in
the initial patch do not count as visited unless the walker stood there.
The elementary record describes the departure step t -> t+1. Set Z_t=B iff
x_t is visited and has at least one unvisited four-neighbour in state t;
otherwise Z_t=I. Update visited geometry on arrival before classifying Z_(t+1).

Define tau(a)=first t with A_t >= a. Band step indices are
tau(A_lo) <= t < tau(A_hi). Thus the move arriving at A_lo is outside, and
the move arriving at A_hi is inside the band. Then S=t_hi-t_lo and
new_cells=A_hi-A_lo for a fully reached band, with no skipped integer areas.
Store actual endpoint states; budget/escape can leave a partial band.

Use dynamic boundaries, as probe does. Do not freeze a spatial frontier: that
would define a different observable. Geometry changes can switch labels even
without a spatial boundary-crossing interpretation; episodes are label runs.

## C. Episodes, cycles and censorship

Track maximal B or I runs continuously across band boundaries. An episode is
complete only if both its label transitions are observed. Store its intersection
with each band separately; flags distinguish observed true transitions from
clipping. A B-then-I pair between consecutive I->B transitions is a complete
cycle when both episodes and transitions are observed. It belongs to a
complete-cycle-only summary only if the entire cycle lies within the band.

For exact occupancy use ALL clipped episode intersections, not only complete
cycles. Sum B fragments=B, sum I fragments=I, B+I=S exactly, including partial
bands and a band with zero completed cycles. Cross-band episodes share stable
IDs; do not double-count them when constructing a full-duration distribution.
Do not wait beyond the computational cap to complete a long episode. A bounded
post-band follow-up may be considered only if frozen in the production protocol.

Completed-only quantiles are selection-biased: long excursions are less likely
to finish in a narrow band. Report complete counts, incomplete time shares,
clipping direction, maximum observed fragment and duration lower bounds.
Do not rename a completed-only quantile an uncensored tail estimate. Survival
methods would need scrutiny because area-band censoring is informative.

Pilot candidate gates: at least 10,000 complete I episodes per seed/band for
the 99.9th percentile, and incomplete-I overlap <=10% of interior time.
Report counts even when gates fail. The percentile needs far more events for
precision; use the pilot for precision/power design, not to declare 10,000
universally sufficient. If gates fail broadly, freeze a revised target (e.g.
tail time burden at fixed duration thresholds) before new confirmatory runs.
Do not silently replace the primary observable after seeing its association.

## D. Geometry normalization and time budgets

Store f_B=B/S, PA_end=P_end/A_end and PA_time=sum_t(P_t/A_t)/S.
Report kappa_end=f_B/PA_end for legacy comparability and
kappa_time=f_B/PA_time for within-band changing-geometry sensitivity.
Primary choice must be frozen after control calibration, before ant outcomes.
c=new_cells/B where B>0; undefined values remain null with reasons.

Cycle identity f_B=E[D]/(E[D]+E[T]) applies to the fully covered cycle subset;
the full band needs leftover fragments. It is bookkeeping, not evidence that
tails explain between-rule growth. Estimate mean durations as well as quantiles:
a cutoff alone does not determine the mean or its time budget.

Candidate burden metrics: fraction of observed interior time from full I
episodes exceeding a fixed threshold; completed-only top 1% duration share;
separate incomplete contribution bounds. Freeze thresholds from controls or
training data only; never choose a different threshold to maximize test fit.
Old L999/R_eq is a duration divided by length (steps/cell), NOT dimensionless.
At fixed target area report duration in steps first; any rescaling and exponent
must have an explicit rationale and calibration.

## E. Inference and held-out prediction

Unit of inference: rule, with seeds nested and bands repeated. Report per-rule
between-seed sd (ddof=1), not only fit errors. Bootstrap rules, keeping seeds,
bands and paired role assignments together; candidate 2000 draws, seed 20261016.
Use fixed train/test folds keyed by sorted rule with an explicit seeded shuffle.
Do not fit and judge the tail predictor on the same rules.

For association use cross-seed groups: geometry, interior predictors and outcome
from disjoint seeds; freeze rotations and how fractions/correlations combine.
For predictive models use interior features from one group, boundary-residence
baseline from another, f_B or kappa outcome from a third; report reliability.
Never use same-trajectory exact duration sums as a claim of predictive success.
Include baseline size/end-to-end geometry, P/A and shape measures, and specify
all transforms and permitted feature counts. With only 44 rules, favor simple
models and wide uncertainty over a feature search. Primary quantity and model
remain unresolved until precision and censoring gates are calibrated.

Candidate primary association and prediction thresholds appear in README.
Before freezing, designate one primary test and how repeated bands and
secondary models are controlled for multiplicity. Report all prespecified tests,
failed gates, missing targets and negative results; do not rescue failures with
post-hoc subsets. Any new-rule cohort is a separate preregistered experiment.

## F. Controls and stopping decisions

1. Deterministic synthetic B/I strings: always-B, always-I, alternating,
   transitions exactly at hits, a single episode spanning both endpoints,
   no completed cycles, budget stop and escape. Assert exact integer accounting.
2. Fast instrument versus brute-force reference visited-set recount, step for
   step, for ants, rotor and random walk; compare hit times and episode flags.
3. Rotor/random-walk runs under the same area-band estimator. Legacy growth
   calibration does not automatically calibrate this first-passage ensemble.
   No invented target value for conditional kappa; compare direct and reconstructed
   occupancy, band-width bias, censoring and endpoint/time-average normalization.
4. Determinism: one versus multiple rayon threads produces identical keyed
   summaries and manifests apart from explicitly separated runtime telemetry.
5. Runtime/coverage/precision pilot before production. Append deviations, freeze
   the final config, hash it, then run fresh confirmation. If tail inference
   cannot be made reliable within budget, report that negative feasibility result.

## G. Scope and completion

No mutation or field-transplant intervention in this experiment. A positive
outcome motivates that next design; it does not establish tail causality.
Done means oracle and release tests pass, controls and inclusion flow are
reported, outputs reproduce, README/NOTEBOOK/notebook agree, and cross-cutting
notes link the outcome. Commit only on user request.
