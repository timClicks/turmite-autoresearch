# Can excursion-duration *shape* tell diffusive mixing from sweeping?

Owner: Turmite Research Agent (AI research agent). Branch `exp/excursion-durations`.

**Registered 2026-10-27 20:30 NZDT (+13:00), base commit `5b96f680ba25ff898fc5ed91d2c33a43d6713233`,
before any measurement on the walkers or rules below.** Instrument construction and
oracle-check scaffolding after this commit are allowed; no calibration or pilot
outcomes may be inspected until the registration commit is recorded and the
instrument's `--check` mode is green on a tiny non-cohort smoke.

Implements proposal **P-C / Q32** from
[`notes/cube-root-routes-2026-10-26.md`](../../../notes/cube-root-routes-2026-10-26.md)
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
(`experiments/archive/2026-10-kappa-first-passage/`, Correction after review). The
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

Recorded in `experiments/archive/2026-10-kappa-first-passage/README.md` (Correction
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

## Results (appended after registration `9bfa4964332323daffe73af0854c020475f1c659`)

**Registration commit (hypotheses frozen, no outcomes):** `9bfa4964332323daffe73af0854c020475f1c659`  
**Instrument binary sha256 (prefix):** `d16f6e6870320e07`  
**Board / horizon:** 8192 / max_log2 24 / RAYON_NUM_THREADS=4 / `--check` on every long run.  
**Compute:** C0 smoke + calibration (~12 walker specs) + excluded pilot (8 rule@seed) finished in well under the 2 CPU-hour budget (wall clock under a few minutes on this box; see `results/*_outer.log`).

### C0 (instrument)
PASS. Tiny non-cohort smoke (`rw:7`, `rotor:7`, grid 256, max_log2 12) matched `probe_walker`. `--mutant` inverted `on_boundary` and panicked under `--check` (boundary_steps mismatch at window k=9). All calibration and pilot specs also ran with `--check`.

### C1 (random walk → D)
**FAIL — instrument inadequate — STOP.** Retained windows under the frozen filters: 0. Cause: window-end $L=A/P$ for `rw:2026102711`..`14` stays in about [2.55, 3.83] across k=16..24, so the $L \ge 4$ filter never fires and $L_\mathrm{max}/L_\mathrm{min}$ cannot reach 2. Diagnostic (not a gate): even with $L \ge 2$ the frozen Score prefers S or is inconclusive, and $L$ range stays below 2×. A 2D random walk on its own range is not a compact blob of growing linear size $L$; using it as the D calibrator was a design error relative to the $L=A/P$ scale.

### C2 (mean-field → L-scaling)
**PASS.** Score(L)=0.0580, Score(L²)=0.1628, verdict=S; mean completed $\tau/L$ = 1.010 (band [0.5, 2.0]). L range ≈ 6.81× over 36 retained windows. Not censoring-fragile.

### C3 (rotor, measured)
Score(L)=0.1202, Score(L²)=0.1462, verdict=**inconclusive** (allowed). mean $\tau/L$ ≈ 1.88. L range ≈ 6.39×.

### Synthetic Score check (not a walker)
`results/synthetic_score_check.txt`: planted pure-scale laws with $L$ over an 8× range are separated correctly (D→D, S/geom→S). So the collapse statistic itself works; C1 failed because the RW calibrator is the wrong physical family for $L=A/P$.

### P-pilot (EXCLUDED / exploratory — not evidence)
C1 STOP forbids reading these as a D/S claim. Descriptive only (`results/analysis.json`):
pooled ants Score(L)=0.1629, Score(L²)=0.0801, frozen verdict would have been D on 67 windows — **do not promote**. Per-rule exploratory verdicts in `analysis.json`. Trajectories permanently excluded from confirmation.

### Why the earlier tail estimator failed, and how this avoided it
First-passage C6 (`experiments/archive/2026-10-kappa-first-passage/`): parametric $(\theta,z)$ fit failed |bias ln τ| and coverage, and $z(1-\theta)\sim 1$ is forced by $E[T]\sim L$. This experiment never estimated $\theta$ or $z$; it used a nonparametric collapse Score with a 0.75 margin, required RW→D and MF→S before any ant reading, and treated censoring flips as uninformative. The new failure mode is different: the chosen D calibrator cannot grow $L$.

### Retain / revise / stop
**Revise.** Keep the excursion definition, probe `--check`, MF L-control, rotor as measured calibrator, nonparametric Score, and excluded-pilot discipline. Replace the D calibrator with a **compact-domain** walker whose linear size grows (e.g. random walk in a growing disk/cup of radius $R$ with $L\sim R$, or Brownian hitting times in a growing interval), re-register C1 against that calibrator, and only then revisit confirmation. Do not interpret the excluded pilot as evidence.

### Confirmation protocol proposal (stage 2; not run)
Unchanged in spirit from the registration section, with one addition: (0) re-pass C1 on the revised compact-domain D calibrator and C2 on a fresh MF seed block; (1) reserved specs in `results/reserved_confirmation_specs.txt` plus further held-out RL-prefix census rules; (2) same Score and 0.75 margin; (3) family-level pass rule frozen before measuring; (4) development trajectories stay excluded.


## Confirmation protocol proposal (stage 2; not run)

If stage 1 retains the design: register a fresh experiment that (1) uses only
the reserved specs above plus further held-out RL-prefix stationary census
rules drawn by a seeded shuffle on class columns only, (2) freezes the same
definitions, scores and 0.75 margin, (3) requires C1/C2 to re-pass on a new
calibrator seed block, (4) states a family-level pass rule before measuring
(e.g. prefer D on >= 75% of eligible rules, or prefer S, or report neither),
(5) keeps development trajectories excluded.

## Revision 1 registration (2026-10-27 20:50 NZDT, +13:00)

**Registered before any revised measurement.** Base commit for this revision:
`c2b3c3902ac2c5b7fd27aec85185aadc03fbf0dd` (stage-1 results on record). The
original registration (`9bfa496`), C1 FAIL verdict, and the excluded pilot stay
unchanged. This section only adds C1' and the confirmation gate.

### Search for an existing compact-domain walker

Preflight (same pruning index revision `5b96f68`, plus title/keyword read of
`notes/walker-comparisons-2026-10-13.md`, `src/walkers.rs`, kappa-uniform /
walker-reference experiments, frontier notes on the memoryless κ≈1.3–1.45
figure):

- `RandomWalk`, `CookieWalk`, `EdgeReinforcedWalk`, `PersistentWalk`,
  `NoisyRotor` (eps→1 = memoryless): all **expand freely** onto unvisited
  cells. Their territories are porous; stage-1 already showed RW never grows
  L=A/P into the analysis band. Not suitable as a compact-domain D calibrator.
- No reflecting / sticky / cup / internal-DLA walker exists in `src/walkers.rs`
  or the probe examples. The κ≈1.3–1.45 memoryless figure is a free-expansion
  control, not a cup.

**Decision: implement a new reflecting-cup mover** in
`examples/boundary_excursions.rs` (same place as `MeanFieldSync`, because the
`Walker` trait cannot see the visited set). Credit the search above; do not
claim novelty beyond this instrument.

### Reflecting cup (frozen definition)

Spec: `cup:P:SEED` with `P` in `{0.05, 0.10, 0.25}` (decimal). Seeds
`2026102731`..`2026102734` (four per P; 12 cup specs). Also `cup:1.0:SEED` as
an oracle-only smoke (must match `rw:SEED` window totals when the accept draw
is skipped at P=1).

Each step:

1. Draw a uniform direction among the four lattice neighbours (same SplitMix64
   stream convention as `RandomWalk`).
2. If the target is already visited: move there.
3. If the target is unvisited: with probability P accept the birth and move;
   with probability 1−P **stay** (reject the move; do not relocate to another
   neighbour).

Justification for stay (not “bounce to a random visited neighbour”): stay is
the minimal rejection of an expansion attempt; it does not require enumerating
visited neighbours and does not add a degree bias among them. P is the only
growth knob.

**P grid (frozen before outcomes, compactness only):** {0.05, 0.10, 0.25}.
Smaller P spends more time mixing before birthing, favouring a filled blob;
larger P approaches free RW. Primary gate uses **P=0.10**; 0.05 and 0.25 are
reported diagnostics (same Score rule). No P is chosen by looking at
excursion scores.

### Compactness pre-check (registered; required for C1')

On windows retained under the same filters as Score (k∈[16,24], not escaped,
n_completed≥200, censored_step_share≤0.20, L≥4), for the primary P=0.10 pool:

1. L_max/L_min ≥ 2;
2. A_max/A_min ≥ 4 (area should track L² growth);
3. median over retained windows of A/P² ≥ 0.04 (lattice disk/square isoperimetric
   order; spider/porous territories fall well below).

If any fails: **C1' inadequate — STOP** (do not run confirmation).

### Prediction and ambiguity (frozen)

- **Predicted shape: D** (collapse in τ/L²; heavy intermediate tail).
- **Known contamination risk:** rejection at the frontier makes the walker
  spend extra time on boundary cells. Near-boundary trapping can inflate the
  short-return atom and make even a cup look **S**-like under Score, while the
  Kac mean remains ~L for both D and S. This is why the mean cannot decide.
- **C1' outcomes:**
  - Prefers **D**, compactness passes, not censoring-fragile → **C1' PASS**.
  - Prefers **S** or **inconclusive**, compactness passes → **C1' INCONCLUSIVE**
    (trapping not ruled out) → STOP confirmation; do not read ants.
  - Uninformative, compactness fail, or censoring-fragile → **C1' INADEQUATE**
    → STOP.

Diagnostic P∈{0.05,0.25}: reported; they do not override the primary gate.
If primary is inconclusive but a diagnostic is cleanly D with compactness, still
STOP (do not shop for P after seeing scores).

### Decision rule (re-frozen; not tuned on ant data)

Identical to stage 1: prefer D if Score(L²) ≤ 0.75·Score(L); prefer S if
Score(L) ≤ 0.75·Score(L²); else inconclusive. Same retention filters, same u-grid,
same censoring-fragile rule. Grounds: stage-1 synthetic check already separated
planted pure-scale D vs S under this margin; revision changes only the D
*calibrator*, not the Score. **No retuning on ant or cup excursion outcomes.**

### Gates before confirmation

- **C0:** `--check` budget identity on cup/mf; probe match on rw/rotor/ant;
  `cup:1.0:seed` matches `rw:seed` on (area, perimeter, new_cells, boundary_steps)
  for a tiny non-cohort smoke; mutant still panics.
- **C1':** primary `cup:0.10` → D + compactness as above.
- **C2:** mean-field re-evaluated under the same frozen Score (re-run or re-score
  on revision calib); must again prefer S with E[τ]/L ∈ [0.5, 2.0].
- **C3:** rotor remains measured-only (no D/S bet).

If C0, C1', and C2 all PASS: run **exactly** the reserved confirmation cohort in
`results/reserved_confirmation_specs.txt` (rules/seeds/windows unchanged). If any
gate fails: stop, record, **do not** run the cohort.

### Confirmation decision rule (frozen now; used only if gates pass)

On reserved specs, same Score/margin/filters; development trajectories stay
excluded.

- Per eligible rule (pooled seeds): verdict D / S / inconclusive / uninformative.
- Report every window, escape, non-reaching run, censored share.
- **Family-level:** among rules with a D or S verdict (eligible), prefer **D**
  if ≥ 75% prefer D; prefer **S** if ≥ 75% prefer S; else **neither**.
- **Retain / revise / retire:**
  - Family D → retain the **diffusive-excursion** account as the working
    explanation for this cohort (sweep not supported here).
  - Family S → retain the **sweep-like** account for this cohort.
  - Neither, or < 4 eligible rules → **revise** (instrument or cohort insufficient).
  - Do not retire the cube-root question; this test only discriminates excursion
    shape accounts.

### Sample (revision)

- Board / horizon / analysis band: unchanged (8192, max_log2 24, k=16..24).
- Cup: `cup:0.05|0.10|0.25:2026102731`..`2026102734` (primary gate on 0.10).
- MF / rotor re-calib seeds: `2026102731`..`2026102734` (fresh block; stage-1
  seeds remain on record and are not reused for the gate).
- Confirmation: only `results/reserved_confirmation_specs.txt`, and only if gates pass.

### Compute

Aim < 2 CPU-hours for revision calib + (if gated) confirmation. RAYON_NUM_THREADS=4.

## Revision 1 results (appended after registration `9c2aeea1732e2cb281544f7c4e07829847272873`)

**Revision registration (hypotheses frozen, no outcomes):** `9c2aeea1732e2cb281544f7c4e07829847272873`  
**First revised-results commit:** `889f31833d3b2829e2fd847766afc410e9234c28`  
**Instrument binary sha256:** `c84e20780315f4cc3b1a83b9200d314a6569c166ec9c1c9b42e0450d11ea0682`  
**Board / horizon:** 8192 / max_log2 24 / RAYON_NUM_THREADS=4 / `--check` on every long run.  
**Compute:** rev1 calib 20 specs finished in ~1–2 s wall on this box (see `results/rev1_calib_outer.log`); confirmation **not run**.

### C0
PASS. `cup:1.0:7` matched `rw:7` window totals (area, perimeter, new_cells, boundary_steps) under `--check`. Cup/mf budget identity held. Stage-1 mutant behaviour unchanged.

### Compactness pre-check (primary cup:0.10)
**FAIL.** Retained windows: 36; L_range ≈ 6.47 (≥ 2); A_range ≈ 55.9 (≥ 4); median A/P² ≈ 0.0188 (**< 0.04**). Territory grows in L but is too porous/ragged relative to the frozen isoperimetric cut. Diagnostics: p=0.05 median A/P² ≈ 0.0257; p=0.25 ≈ 0.0056 (worse). Figure: `results/figures/cup_compactness.png`.

### C1' (cup:0.10 → D + compactness)
**INADEQUATE — STOP.** Score(L)=0.1031, Score(L²)=0.1690, frozen verdict=**S** (not D); compactness fail; not censoring-fragile. Mean τ/L ≈ 2.46. Diagnostics also prefer S (p=0.05 and 0.25). Matches the registered near-boundary trapping caveat: stay-on-reject at the frontier inflates short returns so Score looks sweep-like even though L grows. Do **not** interpret as evidence for the ant's sweep account.

### C2 (mf re-gate)
**PASS.** Score(L)=0.0593, Score(L²)=0.1663, verdict=S; mean τ/L ≈ 0.998. Fresh seeds `2026102731`..`34`.

### C3 (rotor, measured)
Score(L)=0.1195, Score(L²)=0.1536, verdict=**inconclusive** (allowed). mean τ/L ≈ 1.93. L_range ≈ 7.50.

### Confirmation
**Not run** (C1' gate failed). Reserved specs in `results/reserved_confirmation_specs.txt` remain untouched.

### Retain / revise / stop (Revision 1)
**Stop confirmation; retire this reflecting-cup design as a D calibrator** (pruning entry below). Keep the excursion instrument, MF L-control, Score/margin, and reserved cohort. A future revision needs a compact-domain walker that (i) passes A/P² (or an equivalent filled-blob test) and (ii) prefers D under Score without P-shopping — e.g. reflecting onto visited neighbours only, Eden growth, or internal DLA — registered before measuring.

## Revision 2 registration (2026-10-28 15:50 NZDT, +13:00)

**Registered before any Revision 2 measurement.** Base commit:
`e40df036740c1868af077b58aae0c00ddabdb247` (branch tip after the Copilot merge of
`main`; Revision 1 results on record). The original registration (`9bfa496`),
the stage-1 C1 FAIL, the Revision 1 cup verdict
(`NR-20261027-reflecting-cup-d-calibrator`) and the excluded pilot stay
unchanged. This section adds two new D calibrators, C1E and C1I, and re-states
the confirmation gate. Prompted by the user's request to explore an Eden-style
walker and internal DLA.

### Pruning-index preflight

`rg -i -e eden -e idla -e internal -e aggregation -e compact` over
`notes/pruning-index/entries/` (index at `e40df03`):

- `NR-20261027-reflecting-cup-d-calibrator`: retires the stay-on-reject cup
  (`cup:P`) as a D calibrator, and says explicitly that "Eden/IDLA are
  different designs requiring a new registration". It does not cover them.
- `NR-20261026-wall-vs-memory-no-wall-porous`: matches "compact" only as a
  property of ant territories under fresh-ground noise; it is a different
  question.
- No entry mentions Eden growth, internal DLA, aggregation or a
  visited-neighbour birth rule.

**Decision: RUN.** No signature covers these designs. `src/walkers.rs` has no
Eden or IDLA walker (checked again), so both are implemented as new movers in
`examples/boundary_excursions.rs` next to `ReflectingCup`, because they need
the visited set.

### C1E: Eden-style compact walker (frozen definition)

Spec `eden:SEED`. A simple random walk on the visited set with a
neighbour-supported birth rule. Each step:

1. Draw a uniform direction among the four lattice neighbours (same SplitMix64
   stream convention as `cup`).
2. If the target is visited, move there.
3. If the target is unvisited, count its visited 4-neighbours `n` (the
   walker's own cell is one of them, so `n ≥ 1`).
   - If `n ≥ 2`: accept the birth and move (probability 1, no extra draw).
   - If `n = 1`: accept with probability `q1 = 1/64`, else **stay**.

**Justification (compactness only).** The cup failed compactness because every
frontier proposal could birth with the same probability, so single-support
births grew fingers. Under this rule, a cell bordered on two or more sides by
territory (a notch or a kink beside a step) fills as soon as it is proposed. A
cell that would stick out from a flat face (one supporting neighbour) is born
only rarely. Faces then advance row by row: a rare bump nucleates, and the kinks
beside it fill in. This is the layer-growth picture of a faceted, filled blob.

**Stall check.** Any axis-aligned rectangle (for example the 1×1 start, a
straight row, or a full square) has **no** unvisited cell with two or more
visited 4-neighbours. With `q1 = 0` the walker would stall forever. The frozen
fallback is `q1 = 1/64` (exact in the Q32 accept draw). It is strictly
positive, so every frontier proposal has positive birth probability and there
is no absorbing state. It is below the smallest cup `P` (0.05) by more than
3×, so single-support births are rarer than in any Revision 1 cup run. It was
not chosen by running anything. No other `q1` is run: no grid and no
diagnostics.

### C1I: internal DLA (frozen definition)

Spec `idla:SEED`. One walker (a "particle") at a time:

1. The particle starts at the origin (the first visited cell).
2. It takes simple random-walk steps (uniform direction, SplitMix64) on the
   visited set. Steps onto visited cells are always accepted.
3. The first time a step targets an unvisited cell, the particle moves there
   and that cell is born.
4. The next particle restarts at the origin. The restart is an instantaneous
   **teleport**: it costs no time step. The next step starts at the origin.

**Restart treatment (frozen): restarts are not boundaries.** The instrument is
applied unmodified. A step is a boundary step iff it *starts* on a visited
cell with an unvisited neighbour. The step after a teleport starts at the
origin (interior once the blob has grown), so the run from restart to first
boundary hit is a **completed excursion**, counted like any other. The step
that ends the previous particle (the birth) starts on a boundary cell, so it
already closes any open excursion. The teleport therefore never splices two
excursions together.

Why not censor these runs or treat restarts as excursion boundaries? These
centre-launched runs are exactly the excursions whose duration is set by
diffusion across the blob, of order L² (expected exit time from the centre of
a disk of radius R is R²/2). Censoring them would remove the diffusive scale
the calibrator is meant to supply. Treating the teleport as a boundary visit
would change the instrument's definition for one walker only.

**Registered diagnostic, not gate:** `idlar:SEED` is the identical trajectory
(same seed and geometry), but excursions that **began at a restart** are
dropped. They are not completed and not censored, and their steps stay in the
`interior_steps` budget. This lets the boundary-return excursions be read
alone. It does not override C1I.

**Growth note.** IDLA width grows like t^(1/4), not t^(1/3): each birth costs a
particle about R² steps, so A ~ t^(1/2). This matches the internal-DLA remark
in `notes/cube-root-hypothesis.md`. C1I therefore **does not** test whether
IDLA resembles the ant. It tests whether the instrument and Score can see
diffusive, L²-scaled excursions inside a compact, growing territory.

### Predictions and ambiguity (frozen)

- **C1I: predicted D.** About one centre-launched excursion per particle, each
  of order L², with only a few short boundary-return excursions per particle.
  The particle leaves through a boundary cell with probability ≥1/4 per
  boundary step.
- **C1E: predicted D, with an honest ambiguity.** The territory grows slowly,
  and the walker's stationary law on it is uniform. Its excursions all start
  next to the boundary. In a two-dimensional domain, the number-weighted
  survival of such excursions has an L-independent short-time head (roughly
  τ^(-1/2)) and only its cutoff scales with L². The Score compares
  number-weighted survival curves on a fixed u-grid, so a short head that does
  not move with L may push the Score toward S or inconclusive **even for a
  genuinely diffusive, compact walker**. The stage-1 synthetic check planted
  pure-scale laws, which have no such head. A C1E result that is compact but S
  or inconclusive is therefore read as evidence about the **instrument**: the
  Score may not see boundary-launched diffusion. It is not read as evidence
  that Eden is sweep-like.

### Compactness pre-check (unchanged rule, applied to each calibrator)

Use the same retention filters as Score (k∈[16,24], not escaped,
n_completed≥200, censored_step_share≤0.20, L≥4, ≥200 binned durations).
Apply the check to the pooled `eden` seeds and, separately, the pooled `idla`
seeds:

1. L_max/L_min ≥ 2;
2. A_max/A_min ≥ 4;
3. median A/P² ≥ 0.04.

`idlar` has the same geometry as `idla`, so its compactness is reported only.

### Calibrator outcomes (frozen; one label per walker)

- **PASS:** compactness passes, frozen verdict D, not censoring-fragile.
- **INCONCLUSIVE:** compactness passes, verdict S or inconclusive.
- **INADEQUATE:** compactness fails, or verdict uninformative or
  censoring-fragile.

Score rule unchanged: prefer D if Score(L²) ≤ 0.75·Score(L); prefer S if
Score(L) ≤ 0.75·Score(L²); else inconclusive. The u-grid, filters, KM
censoring-fragile rule and margin are all unchanged. If a walker fails, it
fails. There is no parameter shopping, no re-run with other seeds and no
alternative restart treatment.

### Controls

- **C0 (instrument):**
  - The stage-1 probe match on `rw:7`/`rotor:7` and the mutant panic, re-run
    on a tiny non-cohort smoke.
  - `--check` budget identity on every spec.
  - For `eden` and `idla`, which have no `probe_walker` equivalent, `--check`
    instead recomputes area and perimeter from scratch at every recorded
    window by scanning the board. This is an independent count, not the
    incremental `Region` counters, and the two must agree.
  - `eden` must also show that every accepted birth had `n ≥ 2` or used the
    `q1` draw; `idla` births must start on a boundary cell.
  - `idla:S` and `idlar:S` must agree on area, perimeter, new_cells and
    boundary_steps in every window.
- **C2 (mean-field):** fresh seeds; must again prefer S with mean τ/L in
  [0.5, 2.0].
- **C3 (rotor):** measured only; no D/S bet.

### Gate (frozen)

Run the reserved confirmation cohort (`results/reserved_confirmation_specs.txt`,
exactly as reserved) **only if** all three hold:

- C0 PASS;
- C2 PASS;
- **at least one** of C1E or C1I is PASS.

If both C1E and C1I are INCONCLUSIVE or INADEQUATE: **stop**, and do not run
the cohort.

If the gate passes, apply the confirmation decision rule frozen in
Revision 1, unchanged: per-rule verdicts, a ≥75% family rule, and fewer than 4
eligible rules means revise. Interpret the readout **only relative to the
passing calibrator(s)**:

- **If only C1I passes:** the instrument has shown that it can see diffusive
  L² excursions that are launched from inside the territory. An ant S or
  "neither" readout then cannot be read as "the ant does not diffuse along
  its boundary".
- **If C1E passes:** boundary-launched diffusion is also visible.

### Sample (Revision 2)

- Board, horizon and band unchanged: 8192, max_log2 24, k=16..24,
  `RAYON_NUM_THREADS=4`, `--check` on every run.
- Fresh seeds `2026102841`..`2026102844` (four each) for:
  - `eden:SEED`;
  - `idla:SEED`;
  - `idlar:SEED`;
  - `mf:SEED`;
  - `rotor:SEED`.

  That is 20 specs in `results/rev2_calib_specs.txt`.
- Confirmation: only `results/reserved_confirmation_specs.txt`, and only if
  the gate passes.

### Compute

Expected to be minutes of wall time at most for the calibration (Revision 1
took seconds). Confirmation cost is as reserved.

## Revision 2 results (appended after registration `900f25ff9a6ec2abb90233670dc104789b58248e`)

**Revision 2 registration (hypotheses frozen, no outcomes):** `900f25ff9a6ec2abb90233670dc104789b58248e`  
**First Revision 2 results commit:** `1da42bdb2c3c23fb0d20bf99af4baefec5b9575d`  
**Instrument binary sha256:** `9f282ce855e0397954dd96c64ef983ed116153e020088c87a36b93532c935688`  
**Board / horizon:** 8192 / max_log2 24 / k=16..24 / `RAYON_NUM_THREADS=4` / `--check` on every run.  
**Compute:** C0 smoke plus the 20 calibration specs took about 2 s wall on this box (`results/rev2_calib_outer.log`). Confirmation **not run**.

**Deviation (procedural, recorded):** the `eden`/`idla`/`idlar` walker code and
`scripts/run_rev2.sh` were written after the registration commit and were
committed only with the results (`1da42bd`), not in a separate commit before
measurement. The calibration ran with HEAD at `900f25f` and those files
uncommitted. The outer log records the binary hash. The committed source
rebuilds to that same hash (a later rustfmt pass was reverted because moved
panic line numbers changed the binary). The definitions, seeds, Score, margin,
compactness rule and gate were all fixed in `900f25f` before measuring. No
parameter was changed after outcomes, and no other `q1` was run.

All 36 band windows (4 seeds × k=16..24) were retained for every spec family.
No run escaped the board. The largest censored step share was ≈0.092 (rotor),
and ≤0.011 for every other family.

### C0
**PASS.** The `--check` smoke at grid 512 / max_log2 14 (`rw`, `rotor`, `cup:1.0`,
`eden`, `idla`, `idlar`, `mf`) covered four checks:

- the probe matches rw and rotor;
- `cup:1.0` ≡ `rw`;
- a full-bounding-box rescan matches the incremental area, perimeter and
  boundary counters at every window;
- birth invariants hold: Eden supported + fallback births + 1 = area; each
  IDLA birth starts from an unvisited cell; births + 1 = area.

Under `--check`, `idla` and `idlar` gave identical geometry. The stage-1
mutant still panics (exit 101).

### Compactness pre-check (unchanged rule)

| walker | L range | A range | median A/P² | compactness |
|---|---|---|---|---|
| eden | 7.34 (L 6.8–50.0) | 62.7 | 0.0652 | **pass** |
| idla | 4.01 (L 6.8–27.3) | 16.5 | 0.0714 | **pass** |

Both territories are filled, compact blobs whose L grows across the band. The
IDLA L range matches the registered width growth (about t^(1/4) over eight
doublings gives about four-fold).

### C1E (eden → D)
**INCONCLUSIVE.** Score(L)=0.1017, Score(L²)=0.1612, frozen verdict **S**
(not D). Not censoring-fragile (KM 0.1018 / 0.1613). Mean τ/L ≈ 3.07. This
is the registered Eden ambiguity: excursions launched from the boundary have
an L-independent short head, and the number-weighted Score is dominated by
that head.

### C1I (idla → D)
**INCONCLUSIVE.** Score(L)=0.0673, Score(L²)=0.0773, frozen verdict
**inconclusive** (neither ratio clears the 0.75 margin). Not
censoring-fragile (KM 0.0673 / 0.0774). Mean τ/L ≈ 26.7: the
restart-launched excursions are long, as registered.

### Diagnostic `idlar` (restart excursions dropped; not a gate)
Score(L)=0.0846, Score(L²)=0.1282, verdict S, mean τ/L ≈ 3.01. Once the
centre-launched excursions are removed, the IDLA boundary returns look like
Eden's. The IDLA D signal is carried only by the restart-launched excursions.

### Exploratory observation (post hoc, not a registered test)
In `results/figures/ccdf_idla.png`, the long tail in the τ/L² panel visibly
overlies better than in the τ/L panel. The Score does not reward this,
because it weights every excursion equally and the short head is shared
across L. This observation suggests, but does not establish, that a
tail-restricted or step-weighted Score might see the diffusive part. Any such
Score would need its own registration and calibration.

### C2 (mf re-gate)
**PASS.** Score(L)=0.0550, Score(L²)=0.1494, verdict S. Mean τ/L ≈ 0.997.
L range 6.60. Fresh seeds `2026102841`..`44`.

### C3 (rotor, measured)
Score(L)=0.1134, Score(L²)=0.1350, verdict **inconclusive** (allowed). Mean
τ/L ≈ 1.90. L range 6.21.

### Gate and confirmation
C0 PASS ∧ C2 PASS, but neither C1E nor C1I is PASS. **Gate FAIL, so stop.**
The reserved confirmation cohort (`results/reserved_confirmation_specs.txt`)
was **not run** and remains untouched.

### Retain / revise / stop (Revision 2)

**Stop.** Three compact or growing D candidates have now failed to make the
frozen number-weighted Score prefer τ/L²: the stay-on-reject cup, Eden-style
growth and IDLA. The two Revision 2 walkers pass compactness, so this failure
is not a geometry failure. The frozen Score cannot certify diffusive excursions
in these walkers, because their short boundary returns do not scale with L.
This is an **instrument limitation**. It is not evidence about the ants:

- it does not show that ant excursions are sweep-like;
- it does not show that ants fail to diffuse.

Retire Eden-style (`q1 = 1/64`) and IDLA as D calibrators *for this Score*
(`NR-20261028-excursion-score-compact-d-calibrators`). Any further step needs
a newly registered observable that is calibrated against the same walkers
before any ant data. One example is a tail-restricted collapse statistic. Do
not tune `q1`, the margin, the u-grid or the mask on these results.

## Next steps proposal (appended 2026-10-28 16:39 NZDT; post hoc, not registered)

Post hoc and exploratory (NOTEBOOK plan `f466101`, observation `e726ae1`; `results/rev2_short_share.txt`). In the retained Rev2
windows, short excursions (τ ≤ 3) are about 52% of completed excursions for Eden, 34% for IDLA, 73% for the rotor and 8% for
mean-field. They are under 2% of off-boundary time for all four. The number-weighted Score gives each of them a full vote.
Proposed for a future registration (nothing below is frozen):

1. **Time-weighted collapse:** the fraction of off-boundary time spent in excursions longer than s, compared across windows in
   s/L and s/L². This is the time-weighted outcome that `notes/ACTIVE.md` asks for.
2. **Depth–duration scaling:** record each excursion's maximum boundary distance d. Diffusive excursions give τ ~ d², sweeping
   ones give τ ~ d. The slope near 2 versus near 1 can be read within one run, with no fit of L across windows.
3. **Standing calibration panel:** Eden-style, IDLA, and the RW-in-compact-domain where valid on the diffusive side. Use a slope-1
   positive control. The square-ring fillers crawl a three-row edge profile, so they are expected to have almost no deep excursions
   (unchecked). A ballistic walker inside the visited set is the proposed slope-1 candidate and needs its own definition and checks.
4. **Synthetic-mixture gate:** before any walker calibration, a statistic must classify planted mixtures correctly, for example
   about 90% short returns with a diffusive or a sweep tail.
5. **Earlier estimator:** the first-passage C6 fit used only τ ≥ 64 and calibrated on mixtures with a geometric short
   component. It failed on ln-cutoff bias, coverage and identifiability, not on short-return swamping.

Write-up: `blog/_posts/2026-10-28-what-two-failed-calibrations-taught-the-instrument.md`.
