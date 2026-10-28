# What could explain kappa? Mechanisms and discriminating experiments

## Evidence consolidation — 2026-10-23

The [claim ledger](evidence-ledger.md) reads the completed studies and their
corrections together. It separates calibrated occupation accounting, failed
out-of-sample closure, uninformative tail/context tests, shuffle reach and the
single-cell gate eligibility gap. No new measurements or predictions are added.
Use its pinned sources and next decisions before reading the historical plans
below as a current execution queue.

## Prospective first-passage follow-up — 2026-10-20 21:10 +13:00

[New scaffold](../experiments/archive/2026-10-kappa-first-passage/README.md), base
`44ed81f71f4bb1fdccdcdc1cbd586bc1b2eb5613`: compose depth-crossing kernels
into independent return and occupation predictions; test family transfer and
the conditional drift relation `1 + delta - z(1-theta)`. Instrument and all
measurements NOT RUN; confirmation manifest not yet frozen. This follows the
completed tail-budget T1 failure and T2 loss to persistence recorded in that
experiment's README, rather than treating its earlier pilot as the latest state.
It also separates true unseen-family transfer from new-start prediction using
the same rule's early kernel. Original historical entries below are preserved.

Written 2026-10-15 22:54 +13:00; base commit
`b3a0f762ac2230b5df92188206a4d3a1081897be`, dirty workspace.
Scope: brainstorming and prospective research plans, requested by the user.
No new measurement, literature review or claim of novelty. The numerical
thresholds in the linked plans are proposed design choices, not findings.
Plans are **drafts, not frozen preregistrations**.

## What needs explaining

With S steps, B boundary steps, visited area A and perimeter-cell count P,
the probe reports kappa = (B/S)/(P_end/A_end). The boundary is the visited
cells having an unvisited four-neighbour, including boundaries of holes.
It is not the convex hull. Explain both the rule-specific level and why it
stops drifting for some rules. These may be different problems.

The identity dA/dt = c kappa P/A does not predict kappa independently.
Nor does reconstructing B/S from the same trajectory's return times.
A useful explanation needs an independently measured mechanism, a quantitative
prediction on held-out rules or starts, and an intervention that can break it.
Keep three levels distinct: accounting, prediction, causal mechanism.

## Evidence we must not erase

- [Original mechanism tests](kappa-experiment-design.md): simple rule features,
  edge residence and matched-pair crust depletion did not explain kappa.
  Noisy-rotor kappa rose during crossover, contrary to the proposed monotone
  interpolation. Memory matters, but that does not identify its mechanism.
- [Excursion tomography corrections](excursion-tomography-2026-10-13.md):
  normalized short chords were a size artefact; rare-tail share and the
  early-to-late forecast failed their registered tests. A median excursion
  of one step gives little discrimination. Redoing these correlations is
  not a new mechanism.
- [Fixed-area cycles](../experiments/archive/2026-10-fixed-area-cycles/README.md):
  primary association failed its both-band criterion, secondary prediction
  passed, and the narrower-band sensitivity passed. The predictive feature
  was an extreme quantile, not the time mass in the tail. This is the main
  reason to pursue a time-budget model, not to call it established.
- [Prefix audit](../experiments/archive/2026-10-kappa-rule-space/README.md): prefix
  prediction survives flexible area adjustment within stationary rules;
  all-rules transfer is weak. The audit is on inspected data, and a single
  area measurement does not control field history. W5's short-lag bulk
  measures supplied too little predictive gain; long-lag reliability was
  inadequate. Do not call long-range transport ruled out.
- [Matched-area noise floor](../experiments/archive/2026-10-kappa-matched-area/README.md):
  its gate failed. These plans do not reopen a transplant on that selected
  pair set by silently changing the gate.

## 1. Tail mass, not just tail extent — first priority

Think of edge episodes of duration D alternating with interior episodes T.
For a stationary renewal approximation, boundary occupation is
E[D]/(E[D]+E[T]). No independence between successive cycles is required for
the long-run ratio, but existence of stable means and representative sampling
is essential. Clipped finite windows require explicit fragment accounting.

The useful unknown is what sets E[T]. For integer T,
E[T] = sum over u >= 0 of Pr(T > u). A cutoff alone omits the survival
amplitude and shape. A rare-trap mixture could have
E[T] = (1-p) mu_short + p mu_trap. Different rules could change p, trap
duration, or both, even when all have a similar top-percent time share.
This explains why a failed top-1% contrast need not kill a time-budget theory.

Test a compact survival model on separate seeds and predict occupation on
fresh ones. Then ask whether its parameters transfer across area bands.
Do not use a measured held-out E[T] to 'predict' its own kappa.
[Plan: tail budget](../experiments/archive/2026-10-kappa-tail-budget/README.md).

## 2. The prefix is a boundary preparation programme

A fresh cell encounters colours in their update order. Early rule letters
may therefore prepare local tracks before high colours are reached. The
relevant feature could be a first-return kernel over position, heading and
colour, rather than the frequency of L/R or a prefix lookup itself.
The prefix could set the probability of entering a long interior excursion
without changing the ordinary one-step return or edge dwell.

This is stronger than 'early letters matter': predict mutation effects from
how often the altered colour is actually read and what return transition
it changes. A late letter with comparable exposure is a useful control.
Compare birth-neighbourhood exposure with bulk exposure. Cyclic rotation
of a rule alone changes the physical initial background; joint rotation of
rule and colour labels is an exact relabelling control, not an intervention.
[Plan: prefix exposure](../experiments/archive/2026-10-kappa-prefix-exposure/README.md).

## 3. Sparse gates couple the active rim to interior traps

A depleted layer's average occupancy need not measure its permeability.
Two fields with the same depth profile could differ in the number and
direction of a few recurrent crossings. This suggests a rim/interior
transition model: rim-to-interior rate a, interior-to-rim rate b, with
rim occupation b/(a+b). A rim of depth more than zero is not the probe's
boundary; the model also needs independently measured within-rim boundary
occupation. Rates fitted to the same occupations merely restate the answer.

Look for spatial concentration and directional asymmetry of crossings,
then test whether disrupting observed gates changes return time more than
matched edits elsewhere. Geometry, colour phase and incoming heading could
all carry the gates; separating them is part of the experiment. This differs
from the failed crust-depth model and the failed angular-return statistic.
[Plan: return gates](../experiments/archive/2026-10-kappa-return-gates/README.md).

## 4. A slowly maturing field controls return hazards

Equal area need not imply equal age: cells can have different discovery
times, visit counts, colour phases and fractions of a completed colour cycle.
An apparent rule-specific kappa may partly reflect where each rule sits on
a slow maturation trajectory. Prefixes might predict that trajectory rather
than a permanent transport coefficient. A stationary occupation ratio could
arise when the age/phase distribution in the active layer becomes stationary.

Measure hazards conditional on cell age and visit count, using independent
seed groups and several fixed-area bands. Compare size/shape, age, and prefix
models on exactly the same held-out rules. Nonstationary rules are a declared
second stratum, not exclusions selected after inspecting target kappa.
[Plan: field age](../experiments/archive/2026-10-kappa-field-age/README.md).

## Other ideas worth retaining, but not launching yet

- **Finite-state scattering at a flat edge.** Enumerate a small strip's
  exit/return map under the rule; predict a launch probability for long
  excursions. Attractive route to a rule-only calculation, but a uniform
  distribution over edge states is unjustified. Prefix exposure should first
  reveal which states a real field supplies. Periodic strip cycles and
  artificial walls can dominate; report them instead of declaring a bulk law.
- **Effective accessible volume.** Uniform occupation on only a fraction of
  the visited field changes kappa even without edge attraction. Estimate
  accessibility on an earlier block and predict a later block. Same-window
  occupation-weighted volume risks an identity. Gates/age plans can test
  whether inactive cells are structurally inaccessible or simply slow.
- **Loop cancellation and directional balance.** A local imbalance accumulated
  across colour cycles could control persistence of traps. Derive a bound
  or invariant on signed exits, calibrated on the rotor, before another
  generic feature search. The ant reads heading as well as colour, so a
  rotor-style Eulerian identity cannot be assumed.
- **Outer edge versus internal holes.** Kappa could mix two boundary populations
  with different return hazards. Label both in the gate instrument and report
  their time budgets. This is a definition audit; do not replace P by hull
  perimeter and call the resulting quantity the old kappa.
- **Dynamic scaling of the entire return law.** If
  Pr(T>u|A) approximately equals a(A) F(u/tau(A)), then E[T] scales as
  a(A) tau(A) times the integral of F (with a separate short-time part).
  For stationary kappa, E[T]/E[D] should approach A/(kappa P)-1 under
  quasi-static geometry. A proposed collapse must predict this scaling,
  including amplitude; visually collapsing a quantile is insufficient.

## Order and stopping rules

Start with tail-budget accounting and field-age instrumentation; both extend
the existing fixed-area sampler without changing ant dynamics. Use a pilot
only for instrument reliability and cost, then freeze each confirmatory plan.
Next test prefix exposure with paired mutations. Gate edits are last, after
a gate statistic generalizes across seeds and above its noise floor.

The four directories are independent scopes, not permission to launch four
large sweeps. Each has a draft plan, schema, notebook and handoff. No runtime
estimate is claimed before profiling. A null prediction with adequate
reliability retires that mechanism at the tested scales; a failed reliability
gate means uninformative, not a scientific null. Preserve failures and regime
changes in the final accounting. A successful mechanism should eventually
predict kappa from rule and independently sampled field statistics, rather
than requiring the full target trajectory.

## Instrument/pilot continuation — 2026-10-15 23:38 +13:00

The first two plans now have shared observation-only instrumentation, independent
reference/property tests, synthetic calibration, and prospectively registered
feasibility pilots. These are **not scientific confirmation** of T1/T2 or A1/A2/A3.
Base b3a0f76, dirty source hashes recorded; later shared HEAD 3d00123 is unrelated.

Each pilot sampled 44 supported rules x four fresh starts at areas 32768, 131072
and 524288 (width A/16), cap 2^30, board 4096. Tail seeds 2026101501..1504; age
2026101511..1514. All starts reached both primary bands. Tail reached the third
band 176/176; age 168/176, with all eight misses in two preclassified drifting
rules. No escapes or unresolved in-band I time. Both pilots fail their quarter-
cap reserve gate. Age's original 48-rule cohort is unsupported: existing pool
has only 23 drifting rules, with 22 exact length/prefix-matched pairs.

Descriptive seed-half repeatability is high for tail probability >=64
(0.957/0.962/0.985) but lower for mean entry duration (0.656/0.635/0.847).
Median log age is weak at the smaller bands (0.413/0.321; 0.718 at the largest
among 42 complete-case rules); immature fraction and cycle-count variance are
more repeatable. These are instrument-precision findings, not associations with
kappa. Do not discard the median-age feature or missing drifting rules to obtain
a favorable scientific verdict.

Reproducible summaries/commands: [tail report](../experiments/archive/2026-10-kappa-tail-budget/results/REPORT.md)
and [age report](../experiments/archive/2026-10-kappa-field-age/results/REPORT.md), with
source/input/seed manifests and executed notebooks in each folder. Release tests
and sampled one-versus-six-thread replay pass; finished-pilot resume preserves
bytes. Mid-trajectory state checkpoints and fitted scientific estimator calibration
are still absent. Resolve those requirements and the cohort/reserve failures,
then freeze scientific roles/folds/models before new confirmation outcomes.

## Uniform-occupation baseline — 2026-10-16 00:45 +13:00 (accounting, not mechanism)

[experiments/archive/2026-10-kappa-uniform-baseline](../experiments/archive/2026-10-kappa-uniform-baseline/README.md).
The probe divides a window-mean B/S by the end-of-window P/A, so a walker uniform
on its territory at every instant gets kappa = 2∫_{1/2}^{1} x^(-a(1-β)) dx = 1.110
(a=2/3, β=1/2). A mean-field walker (resampled uniformly over visited cells each
step) measured 1.118 ± 0.009 (8 seeds, a=0.677, β=0.520; formula 1.107), as registered.
Consequence: "kappa < 1 means below uniform" should read "below ~1.11"; the ant's
~0.9 is ~0.81× uniform. Two kinds of claim stay separate: the *reference value*
(prediction-level, confirmed) and the *ant's level* (still unexplained). No
mechanism was tested; the four plans above remain the route and remain blocked
on their reserve-gate and checkpoint requirements.

## Return-gates Stage 1 outcome — 2026-10-16

Section 3 was tested in [experiments/archive/2026-10-kappa-return-gates](../experiments/archive/2026-10-kappa-return-gates/README.md)
(registration and results at the bottom of its README). Two gate summaries added no held-out predictive value beyond a
depth-profile baseline (DeltaR2 <= 0 at both bands), but the baseline alone reached R2 0.88-0.95, so the verdict is
UNINFORMATIVE (headroom and reliability gates failed), not a rejection of gates as a mechanism. The intervention stage was
not attempted. Lesson for the other plans: a baseline built from depth-profile ratios of the same trajectories is nearly an
accounting identity with occupation; use baselines from quantities that precede the window.

- Square-loop mechanism for the lead effect (H-loop) tested and rejected at this scale (and the fixed-area lead effect itself is reproduced by a collider model with no direct effect, `experiments/archive/2026-10-c-law-mechanism` Stage 4, see the reconciliation at the end of `open-questions-hypotheses.md`): see `open-questions-hypotheses.md` ("Kappa square-loop test", 2026-10-16) and `experiments/archive/2026-10-kappa-square-loop/README.md`.

## First-passage closure outcome — 2026-10-21

[experiments/archive/2026-10-kappa-first-passage](../experiments/archive/2026-10-kappa-first-passage/README.md) ("Results" at the bottom; frozen before the run, 768 runs, 46 of 48 rules eligible).
**P2 FAILED** (median relative error 1.07 against a 0.20 threshold; a band-1 persistence baseline was better; family-bootstrap interval for the improvement [-0.023, +0.001]).
P1, P3 and P4 were **not tested** (no calibrated tail estimator; no rule-conditional input for unseen families; radius-4 context not recorded), and a frozen deep-dominance rule
(depth-64 carries > 0.5 of E[T] in 35 of 46 rules) declares the milestone closure uninformative about locality.
Two methodological findings: (i) for a maximum-likelihood chain scored on its own data, predicted E[T] equals the sample mean regardless of the state partition (M0, M1, M2 agreed to 0.08%), so
in-sample "closure" cannot be wrong and a closure test must be out-of-sample (the synthetic control that detects failure did so only with a shifted entry law); (ii) interior episodes cannot change the territory, so frozen and evolving depth coincide.
Post-hoc, descriptive: over 46 rules the slope of ln E[T] on ln(A/P) is 0.998 (quartiles 0.88-1.10) and that of ln E[D] is about 0, so the registered condition 1 + delta - z(1-theta) = 0 holds in the median
(1 + delta - slope = 0.002 against a measured kappa slope of -0.003). This says kappa is constant because interior returns scale with the boundary scale; it does not say why, and 26% of rules drift strongly.
Next: a calibrated tail estimator (theta, z) on entry-conditioned T, a test of E[T] ~ L on new starts at larger bands, deeper milestones and radius-4 context in the recorder.

### Correction to the first-passage entry — 2026-10-21 03:06 +13:00

The sentence above that kappa is "constant because interior returns scale with the boundary scale" is bookkeeping, not a finding: with B/S of 0.005-0.05, f ~ E[D]/E[T], so ln kappa = ln L + ln E[D] - ln E[T] and slope_ET = 1 + slope_ED - slope_kappa is the renewal identity (per-rule residual median 0.036, but up to 1.6 for high-B/S rules). The new measurement is delta ~ 0 (E[D] flat over a 4x range of L), and the open question is only restated: why does E[T] track L.
The P2 failure follows for the same reason (B/S ~ 1/L misses any small-band persistence by about the L ratio). A post hoc geometry-conditional kappa persistence (own band-1 kappa times band-2 P/A) has median relative error 0.097: the null the design lacked. The 26% large-drift rules are unchecked as a class (possible highway onset). See the experiment README "Correction after review".

### First-passage stage V2 — 2026-10-21 03:58 +13:00

P1, P3 and P4 were run in a registered stage V2 (experiment README "Stage V2 results"); all three are **uninformative**, P2's FAIL stands. P1: the tail estimator failed its calibration (cutoff bias 0.24 against a 0.2 limit, theta coverage 0.893 against 0.90) and only 72% of rules were identifiable; its fitted exponents are not reported as findings (z comes from tau, the parameter whose calibration failed, and z(1-theta) ~ 1 is forced by E[T] tracking L). P3: the only frozen unseen-family model is a constant per fold; out-of-fold R2 -0.132 at every state level. P4: radius-4 contexts have training support for 0.5% of held-out segments (needs 30%), so no test. The on-disk mid-trajectory checkpoint gate is met (SIGKILL, resume, byte-identical). Open: a tail estimator that passes calibration, then z(1-theta) = 1 + delta.

### Boundary return map: colour-intervention outcome — 2026-10-21

[experiments/archive/2026-10-boundary-return-map](../experiments/archive/2026-10-boundary-return-map/README.md) (registered before running; 36 rules x 2 seeds, plus a 12-rule pilot).
Replacing colours outside radius r (within-depth shuffle) at boundary departures: the typical excursion's duration is fixed by colours within a few cells
(population-weighted r*/L about 0.05-0.1, almost flat in L; registered P1 "no compact state" falsified), but weighted by interior time the reach is about L
(median r*_t/L 1.16, scaling exponent about 1). So a compact boundary state describes the many short loops, not the time budget that sets kappa.
The pasted diffusive heuristic (return time ~ L^2) is not supported: it would give t^(1/4); the census kappa ~ const already excludes it.
Limits: the shuffle removes structure, not single cells; P5 was added after the pilot; the C2 random-walk control ran in the pilot only.

## 2026-10-23: same next-turn map, different return (excluded pilot)

[Protocol and results](../experiments/archive/2026-10-hidden-phase-return/README.md),
evidence revision `1c0d631a1745f3bf12ab9e7a1d87d9d0bb9b6974`.
A one-time shuffle of interior phases within depth bins and next-turn classes
preserves every current turn and the depth-bin colour histogram. In 160 selected
long departures (three rules, four new patched starts, two area bands), all 640
k=1 replays changed path and return tuple. All full-word shams matched. The mean
absolute log2 time effect was 3.06–7.14 across six rule/area cells; the ratio to
unrestricted shuffling was 0.32–0.62. This ratio is not an information fraction:
permutation classes and spatial edits differ between arms.

Minimum episode support failed in 17/24 start/area groups, so the pilot stopped
without confirmation and the registered all-six threshold (missed in two cells)
is descriptive, not a test. Sample: 160 episodes, four starts per rule.
All 9,680 baseline departures were accounted for, with no overflows or unfinished
episodes; no replay was censored. A post hoc extreme example (86,030 -> 6 steps)
was independently reproduced from its initial patch, with first divergence on
a cell's second read. It is a many-cell intervention, not single-cell attribution.

This is evidence against exact next-turn-map sufficiency on the tested edited
fields, not an explanation of kappa, natural-state insufficiency, a growth law
or a population mean effect. Current-turn versus future-clock distinctions and
the delayed-divergence argument already occur in the c-law renewal record.
The new result motivates distinguishing collective phase organisation from
individual delayed instructions, with adequate preconfirmed episode support
and a future occupation prediction. No such follow-up was run.
