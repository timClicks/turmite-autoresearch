# Can excursion-duration *shape* tell diffusive mixing from sweeping?

Owner: Turmite Research Agent (AI research agent). Branch `exp/excursion-durations`.

**Registered 2026-10-27 20:30 NZDT (+13:00), base commit `5b96f680ba25ff898fc5ed91d2c33a43d6713233`,
before any measurement on the walkers or rules below.** Instrument construction and
oracle-check scaffolding after this commit are allowed; no calibration or pilot
outcomes may be inspected until the registration commit is recorded and the
instrument's `--check` mode is green on a tiny non-cohort smoke.

Implements proposal **P-C / Q32** from
[`notes/cube-root-routes-2026-10-26.md`](../../notes/cube-root-routes-2026-10-26.md)
on PR #18 (`survey/cube-root-routes`, unmerged at registration). That note is
proposals only; this experiment is the first registered test of its
excursion-duration collapse idea. Builds on the first-passage ACTIVE plan
(rotor / RW / mean-field calibrations), the existing excursion tomography
instrument (`examples/excursions.rs`, T1), and the exposure-classes check-mode
style (`examples/kappa_exposure_classes.rs`).

**Stage 1 only:** calibrate the instrument on known walkers, run one excluded
development pilot, stop. No confirmation study in this experiment.

## Question

By Kac's lemma, a stationary uniform occupant of a territory of area A with
boundary size P has mean return time to the boundary of order A/P = L. The
repo already finds that constant kappa is equivalent (via the renewal identity)
to the ant's mean interior excursion duration E[T] tracking L
(`experiments/2026-10-20-kappa-first-passage/`, Correction after review). The
**mean** therefore cannot separate two stories that both give E[T] ~ L:

- **D (diffusive):** Pr(T > s) ~ s^(-1/2) for 1 << s << L^2, cut off near L^2.
  Scaled durations collapse in `tau / L^2`.
- **S (sweep):** long excursions have length proportional to L (plus a short-return
  atom). Scaled durations collapse in `tau / L`.

The first-passage experiment's parametric tail fit (theta, z) failed calibration
(C6): |bias ln tau| up to 0.238 (need < 0.2) and coverage 0.893 (need 0.90-0.99),
and the product z(1-theta) is forced toward 1 by E[T] ~ L, so the fit is
ill-conditioned along that line. This experiment **does not fit theta or z**.
It asks whether a nonparametric collapse comparison can tell D from S on
calibrators, and (exploratory only) what the ant pilot looks like.

## Definitions (frozen)

- **Territory / boundary.** Identical to `src/probe.rs`: a cell is visited once
  entered; a visited cell is on the **boundary** iff it has at least one
  unvisited 4-neighbour. Perimeter P is the count of such cells; A is the
  visited count. Observation is at **step start**, before the walker's move
  (same convention as the probe's `boundary_steps`).
- **Evolving boundary.** The boundary set is recomputed as territory grows. An
  interior step is one that **starts** on a non-boundary visited cell under the
  current region. Justification: a frozen-at-entry boundary is a different
  observable (first-passage README, "Sensitivity"); mixing with it silently
  would confound the collapse. We use the evolving definition and report the
  unresolved (window-crossing) share so that growth within a window is visible.
- **Excursion.** A maximal consecutive run of steps that start off the boundary.
  Duration `tau` is the number of such steps. An excursion that is still open at
  the end of an octave window is **right-censored** at its length-so-far inside
  that window (and does not enter the completed sample). Completed excursions
  that started in a previous window are attributed to the window in which they
  complete (departure window would require carrying state; completion-window
  attribution matches `examples/excursions.rs` and keeps the per-window budget
  identity).
- **L.** For each octave window ending at t = 2^k, L = A/P using A and P at
  **window end** (same end-of-window geometry the probe uses for kappa =
  (B/S) / (P/A)). Within-window L drift is a limitation, recorded via the factor
  by which A grows across the window when available; stage-1 analysis treats L
  as quasi-static within an octave.
- **Windows.** Octave windows (2^{k-1}, 2^k] with output column `k` equal to the
  window-end exponent (probe / exposure-classes convention: k = 1 labels
  (1, 2], …). Analysis uses a frozen band of k stated under Sample.

## Observables and decision rule (frozen before outcomes)

Instrument: `examples/boundary_excursions.rs`. Per (spec, window) it emits

1. probe-aligned window totals: area, perimeter, new_cells, boundary_steps,
   interior_steps, kappa, L = A/P, escaped flag;
2. completed-excursion counts in log2 duration bins (`floor(log2(tau))` for
   tau >= 1; tau = 0 cannot occur for a completed interior run);
3. censored count and total censored step mass;
4. under `--check`, every window's (area, perimeter, new_cells, boundary_steps)
   must match `probe::probe_walker` exactly, and
   boundary_steps + interior_steps = 2^{k-1} (window length).

**Collapse scores** (primary). For a walker (pooling its calibration seeds) and
scaling s in {L, L^2}:

- Retain windows with k in the analysis band, escaped = false, n_completed >= 200,
  censored_step_share = unresolved_steps / interior_steps <= 0.20, L finite and
  >= 4. Require L_max / L_min >= 2 across retained windows; else the walker is
  **uninformative** (not a fail of D or S).
- For each retained window, form the empirical survival of completed durations
  in the scaled variable u = tau / s(L), evaluated on the fixed grid
  u_j = 2^{-8 + j/2} for j = 0..32 (u from 1/256 to 16), clipped to values where
  at least one window has survival in (0.05, 0.95).
- Score(s) = mean over all unordered window pairs {w1, w2} of
  (1/|G|) sum_{u in G} |S_{w1}(u) - S_{w2}(u)|, where G is the clipped grid.
  Lower means better collapse.

**Decision rule (calibration):**

- Prefer **D** if Score(L^2) <= 0.75 * Score(L).
- Prefer **S** if Score(L) <= 0.75 * Score(L^2).
- Else **inconclusive**.

**Secondary shape statistic** (reported, not a pass/fail gate): for each
retained window, ordinary-least-squares slope of log S(tau) versus log tau on
completed durations with tau in [max(8, 0.25 L), min(tau_max, 4 L)], requiring
at least 5 distinct tau with S in (0.05, 0.95). Under D the slopes should sit
near -0.5 and be stable across L; under S there should be no stable
L-independent intermediate slope in that band (mass near tau ~ L).

**Censoring sensitivity:** recompute Score(s) with Kaplan–Meier survival that
treats unresolved excursions as right-censored at their length-so-far. If the
D-vs-S preference flips relative to the completed-only scores, report
**censoring-fragile** and treat the calibrator as uninformative for stage-1.

## Registered predictions (stage 1)

### C0 (instrument)

Every calibration and pilot spec run with `--check` matches probe window totals
exactly. A deliberate mutant (boundary test inverted) must panic under `--check`.

### C1 (random walk → D)

On `rw:SEED` seeds listed below, the completed-only rule prefers **D**.
If it prefers S, is inconclusive, is uninformative, or is censoring-fragile:
**instrument inadequate — STOP** (do not interpret the pilot).

### C2 (mean-field → L-scaling geometric)

On `mf:SEED`: each step resamples a uniform visited cell then a random neighbour,
so start-of-step boundary occupation is ~ P/A and interior sojourns are
approximately geometric with mean ~ L. Prediction: the rule prefers **S**
(collapse in tau/L), and the window-pooled mean completed duration
E[tau] / L lies in [0.5, 2.0]. If it prefers D or is inconclusive/uninformative/
censoring-fragile: **STOP** (same gate as C1). Geometric is not a "sweep"; it is
the L-scaling null that Kac's mean alone cannot distinguish from S. We use it as
an L-collapse positive control, not as a model of the ant.

### C3 (rotor: measured calibrator, no D/S bet)

No registered preference. Report Score(L), Score(L^2), the rule's verdict, and
the secondary slopes. A rotor that is uninformative (L range < 2x) is reported
as such, not forced.

### P-pilot (excluded development; exploratory only)

On the development cohort below, report the same scores and verdict **labelled
exploratory / excluded from confirmation**. No pass/fail on the ant. If C1 or C2
stopped the instrument, do not interpret these numbers as evidence.

## Sample (frozen)

- **Board / horizon:** grid 8192, max_log2 = 24 (windows up to (2^23, 2^24]).
- **Analysis band:** k = 16..24 (steps in (2^15, 2^24]), subject to the
  retention filters above. Random-walk seeds that escape before offering
  L_max/L_min >= 2 in-band are uninformative (counted).
- **Calibration walkers:** `mf:2026102711`..`2026102714` (4 seeds),
  `rotor:2026102711`..`2026102714`, `rw:2026102711`..`2026102714`.
- **Development cohort (EXCLUDED from any later confirmation):** four short
  RL-prefix chaotic/blob rules already present in the probe-growth census and
  prior kappa / excursion records, with **new** patched seeds unused elsewhere
  (grepped at registration):

  | rule | seeds | prior appearance (examples) |
  |---|---|---|
  | `RLLR` | `@2026102721`, `@2026102722` | probe census; compact A at 2^26 |
  | `RLLLLRLL` | `@2026102721`, `@2026102722` | probe census |
  | `RLLLRR` | `@2026102721`, `@2026102722` | probe census |
  | `RLLRL` | `@2026102721`, `@2026102722` | probe census |

  Specs file: `results/pilot_specs.txt`. These eight (rule, seed) pairs and their
  trajectories are permanently excluded from confirmation cohorts for this
  question.

- **Reserved confirmation (NOT RUN in stage 1):** rules `RLLLLRLR`, `RLLLRLRL`,
  `RLLLRRLL`, `RLLLLRRR`, `RLLRLLL`, `RLLRLLLL`; seeds `20261027901`..`20261027908`
  (patched `@SEED`). Listed in `results/reserved_confirmation_specs.txt`. Do not
  run them here.

## Pruning-index preflight

- Index revision: `5b96f680ba25ff898fc5ed91d2c33a43d6713233`.
- Queries:
  `rg -n -i -e 'return|excursion|tail|first-passage|boundary|kappa' notes/pruning-index/entries`
  and title read of all three entries.
- Candidates: `NR-20261022-additive-laws-order-blind` (additive modular laws vs
  colour order; different objective); `NR-20261025-kappa-exposure-classes-exposed-edge`
  (exposure-class location of kappa deficit; different observable);
  `NR-20261025-crawler-window-single-letter` (c-law letter window; different
  objective).
- Decision: **RUN**. No signature covers excursion-duration collapse, D-vs-S
  discrimination, or this instrument. The first-passage C6 failure is a
  methodological warning (avoid parametric (theta, z) fits), not a pruning
  signature. Retain RW / mf / rotor as calibration controls.

## Compute / stopping budget

- Aim: < 2 CPU-hours total. `RAYON_NUM_THREADS=4`. Long jobs backgrounded with
  logs under `results/`.
- Stop without interpreting the pilot if C1 or C2 fails the registered gate.
- No confirmation run in this PR regardless of pilot appearance.

## Why the earlier tail estimator failed, and how this avoids it

Recorded in `experiments/2026-10-20-kappa-first-passage/README.md` (Correction
after review / C6) and ACTIVE.md: a truncated-power-law fit for (theta, cutoff)
failed its own calibration (ln-cutoff bias and coverage), and any such fit is
pushed toward z(1-theta) ~ 1 whenever E[T] ~ L, so the mean cannot identify the
shape. This design (i) never estimates theta or z, (ii) freezes a nonparametric
collapse comparison with an explicit margin, (iii) requires the RW calibrator to
come out D and the mean-field calibrator to come out L-scaling before any ant
number is read as evidence, (iv) treats censoring fragility as uninformative.

## Reproduction

See `scripts/run_calibration.sh`, `scripts/run_pilot.sh`, `scripts/analyse.py`.
Exact commands, commit hashes and sha256 of binaries/outputs are appended below
after the registration commit and runs (this section above the results heading
is not edited post hoc; results are appended).

## Results, uncertainty and limitations

*(Appended after registration commit and runs. Predictions above stay unedited.)*

## Confirmation protocol proposal (stage 2; not run)

If stage 1 retains the design: register a fresh experiment that (1) uses only
the reserved specs above plus further held-out RL-prefix stationary census
rules drawn by a seeded shuffle on class columns only, (2) freezes the same
definitions, scores and 0.75 margin, (3) requires C1/C2 to re-pass on a new
calibrator seed block, (4) states a family-level pass rule before measuring
(e.g. prefer D on >= 75% of eligible rules, or prefer S, or report neither),
(5) keeps development trajectories excluded.
