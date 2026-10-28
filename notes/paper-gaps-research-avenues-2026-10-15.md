# Research avenues for the cube-root paper

Written 2026-10-15, base commit `da88e61`, working tree uncommitted.
Requested by the author while updating the manuscript's account of predicting
kappa. This note proposes work; it reports no new measurements and is not a
preregistration. Fix cohorts, seeds, windows, estimators, compute budgets and
decision thresholds in the relevant experiment README before running anything.

The paper already has a useful empirical result without a complete mechanism.
The main opportunity is to connect a predictive rule family to a measurable
transport process, while separating finite-size geometry from dynamics. The
priorities below are ordered by how directly they address that gap.

## 1. Find what the prefix predictor is predicting

**Gap.** Simple letter models failed, but the longer-prefix W3c lookup succeeded
on fresh stationary rules of lengths 13–14. Its area-controlled score still
uses measured early area. The exploratory cross-check shows that including
non-stationary census rules in training substantially reduces its gain even
on the same stationary test rules. That is evidence of conditional prediction,
not a rule-to-kappa mechanism. See the [W3c registration and corrections](../experiments/archive/2026-10-kappa-rule-space/README.md).

**Next test.** Combine direct fixed-area sampling with a frozen prefix model.
Train once on the existing census; test on fresh rules and starts. Record each
trajectory at prescribed visited-area targets and measure over narrow area
bands. Record shape, perimeter and colour-field age as covariates, rather than
assuming equal area fixes them. Set a budget and report nonattainment and escape.
First-passage sampling changes the ensemble and must be part of the claim.

Separate two questions: prediction in an oracle-defined stationary cohort,
and deployable prediction when stationarity is not yet known. For the latter,
use an early-window regime decision frozen before later kappa is measured,
with all later failures retained. Compare stationary-trained, pooled and
explicitly regime-aware predictors on the same test set. Include an area-only
baseline and report prefix-only prediction separately from models using area.

**Discriminating outcome.** A prefix advantage at fixed area, on fresh starts,
would strengthen the case for family-specific transport. Loss of the advantage
would point toward size/history or regime selection. Even success is within-family
transfer unless prefixes themselves are held out. An unseen-prefix split answers
a different and harder question; do not relabel the current test as that test.

## 2. Close the boundary-occupation time budget

**Gap.** An extreme excursion cutoff need not control mean return time: its
probability mass matters. The independent-area association survives disjoint
seed roles, but noisy area and earlier selection remain; the previous noise-floor
gate is still failed. See [the existing cutoff proposals](cutoff-research-avenues-2026-10-15.md)
and [independent-area results](../experiments/archive/2026-10-independent-area/README.md).

**Next test.** At the area targets above, partition steps into boundary episodes
and interior excursions. Reconstruct boundary occupancy exactly, including
episodes cut by either window edge and the changing boundary definition.
Calibrate this accounting against the reference implementation and known paths,
then rotor and random-walk controls. This reconstruction is an instrument check,
not independent evidence for the growth law.

Measure contributions to total interior time from predeclared duration bands,
alongside boundary residence time. Ask which components predict held-out
occupancy after size and geometry controls. Avoid another maximum-duration
correlation. The target is a quantitative time budget that can explain a
between-rule difference of the observed magnitude.

**Discriminating outcome.** If boundary residence carries the differences,
drop the claim that interior tails are the principal carrier. If tail mass
predicts occupancy but the cutoff alone does not, replace the cutoff story
with a tail-contribution model. Respect the earlier null excursion/dwell tests;
the new information must be explicit censor handling and quantitative accounting.

## 3. Challenge that transport model with paired mutations

**Gap.** A lookup groups rules without explaining why the group matters.

**Next test.** Extend the existing mutation programme after fixing a candidate
time-budget model. Pair base and mutant with common start-patch seeds; compare
early-prefix and later mutations at the same area targets. Record the proposed
mediator, kappa, shape and escape, with inference by base rule. Freeze the
model on one set of bases and predict directions and magnitudes on another.
Do not silently discard mutations that change regime.

**Discriminating outcome.** Reproducible kappa changes without the mediator
change required by the model would break that explanation, provided measurement
uncertainty is small enough. Joint changes are supportive but do not prove
mediation: a mutation changes both the walker and its evolving medium.
This should follow the accounting test, not precede it.

## 4. Locate the medium the crystal ray actually reads

**Gap.** The registered ground-phase intervention failed its strong predictions.
Counting tens of thousands of edited colour-2 cells does not establish that
the relevant staircase encountered those cells. Full-window alternation also
mixes the original ray with later motion. In all three tested rules, colours
2 and 3 specify the same immediate turn; a phase advance can affect motion
only through a revisit. See [the protocol and failed predictions](../experiments/archive/2026-10-crystal-rules/README.md).

**Next test.** First add exposure instrumentation without changing the old
verdicts. Record visits to edited cells, first divergent turn, revisit counts,
and alternating-run lengths before and after exposure. Distinguish a same-turn
phase edit from an immediate turn-changing edit, with matched edit locations
and counts. Audit the proposed opposite-turn sublattice directly; it remains
an exploratory interpretation, not an established background structure.

Then register complementary endpoint interventions: repair a candidate defect
at an observed ray end, and insert the same defect into an intact staircase.
Use matched within-ray sites and distant edit controls. An endpoint-selected
sample estimates rescue of known endpoints, not the population termination
hazard. Retain the old geometric detector as a secondary metric and calibrate
any new exact staircase-break detector on planted interruptions and oracle paths.

**Discriminating outcome.** Consistent rescue plus sabotage at the predicted
exposure would be stronger evidence than generic disruption. No exposure means
the intervention missed its target; exposure without the predicted motion change
challenges the proposed defect mechanism. Keep this investigation in crystal-rules.
It clarifies excluded builders and regime changes; it is not needed to claim
the empirical cube-root census.

## 5. Separate persistent global shape from local edge roughening

**Gap.** Outer-hull measurements rule out a simple hole-rim explanation of the
edge gap. The band analysis places more relative excess at long wavelengths,
but the normalised spectrum's temporal decay partly restates W/R scaling.
Its failed stability prediction was mis-specified; do not present that failure
as an independent discovery. See [hull-width results and correction](../experiments/archive/2026-10-hull-width/README.md).

**Next test.** Save r(theta) profiles across a registered checkpoint sequence,
including a census-sampled rule cohort and rotor controls at matched radii.
Measure real-space height differences and absolute band power. Separately
measure shape modes and residual fluctuations under a prespecified mode-removal
rule, with synthetic lobed and locally rough contours to calibrate the separation.
Track mode persistence over time: a persistent notch and a decorrelating local
fluctuation can have similar one-time widths.

**Discriminating outcome.** A gap confined to persistent low modes supports
large-scale shape dynamics. A residual gap with a stable correlation-length
scaling would motivate an interface model. Neither outcome alone identifies
a universality class; a wider W exponent is insufficient.

## 6. Make the forecast compete with ordinary persistence

**Gap.** The transport forecast is independent of later outcomes, but its early
budget is computed from area increments. Forecast skill demonstrates persistence;
it does not isolate a transport mechanism. Relative errors also explode near stalls.

**Next test.** On fresh runs, compare the frozen budget against an early-area
power-law extrapolation, a last-increment predictor and a same-rule/other-start
predictor, using identical information windows. Register both relative and
scale-normalised absolute errors, retaining near-stalls. Report escapes and
incomplete runs rather than implying that the complete-trajectory forecast
predicts breakouts. A useful stronger target is a prospective forecast from
the time-budget components in avenue 2.

**Discriminating outcome.** If ordinary growth-history baselines perform as
well, describe the finding as transport persistence rather than mechanistic
forecasting. Improvement from independently measured components would be a
stronger step toward explanation.

## Practical order and manuscript scope

Start with fixed-area sampling and complete episode accounting in one modest,
oracle-tested pilot. Use it to size a fresh-rule confirmation, then test paired
mutations. Run crystal exposure and edge-profile work as separate investigations;
neither needs a large census to establish whether its instrument hits its target.

Before submission, reconcile abstract, key results, evidence table and conclusion
with the prefix result and its training-regime limitation. Preserve failed
predictions. Replace stale data-path descriptions, generate newly quoted numbers
from small result files, and make each figure/number traceable to a saved recipe.
Pin a manuscript snapshot and archive only when the author requests a commit
and release. No new simulation, literature review or novelty claim was made
in preparing this note.
