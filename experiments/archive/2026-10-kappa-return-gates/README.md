**Status (2026-10-16): Stage 1 COMPLETE. Instrument built and validated, registration frozen, pilot + confirmation run. G1 verdict UNINFORMATIVE (criterion failed at both bands; band 0 g2 reliability and band 1 headroom gates failed). G2 unrun. See "RESULTS" at the bottom. The text between here and the REGISTRATION section is the historical draft.**

# Spatial gates and interior return bottlenecks

Status: **draft, gated research plan; no instrument or intervention run**.
Created 2026-10-15 22:54 +13:00, base `b3a0f762ac2230b5df92188206a4d3a1081897be`
(dirty tree). [Mechanism note](../../../notes/kappa-mechanisms-2026-10-15.md).

## Question and mechanism

Can a small set of directional rim/interior crossings explain the mean time
away from the boundary? Mean crust depletion and angular return summaries
already failed their tests. The new claim is that *where and how crossings
occur* matters more than the average depth profile.

## Draft design and predictions (freeze before ant outcomes)

1. Observation first: 24 rules selected independently of new gate statistics,
   balanced across existing crust/uniform and stationary/nonstationary labels;
   16 fresh starts each, areas 32768 and 131072, bands A/16, cap 2^29 steps.
   Freeze classification source and missing-label treatment before selection.
2. Define rim as instantaneous visited depth <=4; measure actual boundary
   occupancy within it separately. Freeze a depth map at band entry as a
   secondary material-coordinate definition. Cells changing depth without a
   walker crossing must not count as spatial transport. Record both causes
   of a rim/interior label change. Split hole boundaries from the exterior
   using a reference flood-fill; never substitute hull perimeter for P.
3. Bin rim/interior crossing edges by fixed 8x8 spatial tiles anchored at the
   starting origin, directed heading and colour phase. Candidate gate statistic:
   top-decile share of crossings, adjusted against a null preserving available
   edge counts and occupation exposure. Gate identification uses one half
   of an observation window; test recurrence on the other half and on
   independent starts using distributional summaries, not identical coordinates.
4. Draft G1: gate concentration and directional return rates improve independent-
   seed occupation prediction by >=0.10 held-out R2 over area, P/A, boundary
   residence and depth-profile baseline, with rule-bootstrap lower bound >0.
   A two-state occupation identity fitted on target data is not a pass.
5. Only after G1 and reliability pass, fork snapshots for paired interventions:
   no edit, gate-phase edit, and matched nongate edit. Select gate sites from
   a *prior* observation block. Preserve visited mask, position and heading;
   change the same number of colours by the same phase increments, matching
   depth, original colour, visit count and distance. Record first edit exposure
   and trajectory divergence. Matching failure is reported, not relaxed after
   outcomes. Dynamic colours change while geometry starts identical.
6. Draft G2: a frozen transport model predicts the sign of gate-minus-control
   effects on subsequent interior time in >=70% of resolved rule contrasts,
   and gate edits have larger absolute effects than matched edits with paired
   bootstrap lower bound >0. Follow 2^16 and 2^20 steps as separate transient
   horizons. Do not prescribe a universal increase/decrease without the
   calibrated model. Record growth/shape changes during follow-up.

## Controls and gates

Reference BFS depth and flood-fill tests on holes, narrow necks and growing
paths; property-test incremental counters. Synthetic directed two-compartment
chains test detection of planted bottlenecks and rejection of uniform flow.
Rotor and random walk check scale dependence without assuming gate-free paths.
No-edit clones must be bit-identical, and an edit to a never-read location
must leave the path identical until its first relevant exposure.

Before G2: split-block gate rank reliability >=0.7 across usable rules,
at least 80% cohort coverage and a prospective power calculation from pilot
noise. If that fails, stop at an unreliable-instrument verdict. Bootstrap
rules, with snapshots/starts nested (2000 draws). Log off-manifold edited
fields and distinguish immediate from relaxed response. Even G2 success
does not prove that these edited states occur naturally.

## Implementation and next action

Build observation instrumentation before any edit runner. Start with exact
reference maps on small paths; optimize only after agreement. Do not use the
old failed matched-area pair gate as authorization for a transplant. This is
a separately registered, within-snapshot experiment with its own feasibility
gate. Rust examples: `kappa_return_gates_*`.

See [PLAN.md](PLAN.md), [SCHEMA.md](SCHEMA.md), and [HANDOFF.md](HANDOFF.md).
Results: **NOT RUN**. No scientific test has passed or failed in this scaffold.

## Scaffold verification — 2026-10-15 22:59 +13:00

Preflight and the planning notebook executed successfully under uv/WSL; local
Markdown links resolve. The shared workspace passed cargo test --release.
No new instrument or scientific prediction was tested. Commands are in HANDOFF.md;
verification scope and the local test-log path are recorded in NOTEBOOK.md.


---

## REGISTRATION (Stage 1, G1) — frozen 2026-10-16 17:50 +13:00, before any confirmation seed was run

Base commit `baac481911aa68db941e6b692be978dcfb5f08af` with a dirty working tree (this experiment, `src/return_gates.rs`,
its tests and examples are uncommitted). Everything below supersedes the draft design above where they differ; the
differences are listed under "Departures from the draft". The pilot (seeds 2026102001-08) has been run and analysed for
reliability, coverage and seed count ONLY (no regression of occupation on gate features was fitted to pilot data).
G2 (snapshot-fork edits) is **out of scope and unrun**; it would be a separate registration.

**Question.** Do spatially resolved rim/interior crossing statistics improve held-out prediction of boundary occupation
over area/shape/depth-profile baselines, on rules and seeds not used to compute the features?

**Instrument** (`src/return_gates.rs`; oracle test `tests/return_gates.rs`: from-scratch BFS every step, 24 random rules,
passes; `results/return_gates_tests.log`). Depth = 4-neighbour distance through visited cells to the nearest visited
boundary cell (holes included), capped at 5; rim = depth <= 4; depth 0 is the probe's boundary label (asserted in the
sampler for every run). Each step is split into stage A (the move under the old map; a newly discovered cell counts as rim)
and stage B (the map update at a fixed position): stage-A label changes are crossings, stage-B label changes are
reclassifications and are tallied separately. Crossings and exposures are keyed (8x8 tile of the rim-side cell, heading
after the move, exit/entry). Observation window: departures from states with area in [A, A+A/16) for A = 32768 (band 0)
and 131072 (band 1); excursions begun inside a window are followed to their end. Board 4096, cap 2^29 steps, fresh
`PatchedAnt` start (radius-2 random patch from the seed), as in the sibling field-age/tail-budget runs. Hole vs exterior
boundary cells are counted by flood fill at each band's upper edge (`hole_split`, tested against a set flood fill).

**Cohort** (`scripts/select_cohort.py`, `results/cohort.csv`, `results/cohort_manifest.json`). 24 rules, 6 per cell of
{crust, uniform} x {stationary, nonstationary}, from `experiments/archive/2026-10-kappa-rule-space/results/rules_pool.csv`
(192 rules, sha256 in the manifest): crust iff pool `c >= 0.60`; stationary iff `|g_k| < 0.05`; first 6 by
sha256("return-gates-cohort-v1|" + rule). No missing labels exist (the script aborts rather than impute). The labels are
existing summaries from earlier experiments; no gate statistic or new outcome entered selection. Pool cell sizes:
15 / 14 / 154 / 9 (crust-stationary / crust-nonstationary / uniform-stationary / uniform-nonstationary).

**Seeds** (audited unused, see NOTEBOOK entry of 17:55): pilot 2026102001-08; controls 2026102051-58; confirmation
PREDICTOR seeds 2026102101..2026102164 (the first S are used), TARGET seeds 2026102201..2026102232 (32); bootstrap
2026102099 (permutations 2026102199); synthetic calibration 2026102061. Predictor and target roles are disjoint seeds of the
same rules. S = 64 by the pre-set rule below.

**Seed-count rule (applied to the pilot; `results/pilot_analysis.json`, `results/seed_count.json`).**
S = smallest of {8,16,32,64} whose Spearman-Brown projection of the 4-vs-4 pilot split-half Spearman correlation is >= 0.7
for BOTH g1 and g2 at BOTH bands. Result: S = 64 (g2 at band 0 projects to only 0.734; its 4v4 split-half is 0.147 on 22 rules).
Target seeds were raised from the draft 16 to 32 because the pilot's split-half Spearman of the target itself projects to
~0.75-0.83 at 8 seeds and ~0.92-0.95 at 32. Both choices were made on pilot data before any confirmation seed existed.

**Per-rule, per-band quantities** (`scripts/rg_lib.py`, `scripts/analyse_confirm.py`).
Target y = ln(sum B / sum steps) over target seeds (boundary occupation of departures in the window). From PREDICTOR seeds:
- B0 baseline (4 features): ln(mean P/A over departures), ln(mean completed boundary-run length), ln(d1/(d1+d2+d3+d4)),
  ln(d5/(d1+d2+d3+d4)), where d_k = departures from depth-k cells (d5 = depth >= 5). d0 (occupation of the boundary) is
  excluded deliberately: with it the baseline would be a second measurement of y.
- Gate features (exactly 2): **g1** = mean over predictor seeds of [top-decile share of crossing events over all
  (tile, heading, kind) bins with positive exposure] minus [the same share under Poisson counts with the observed total
  and rates proportional to exposure; 100 draws, seed from FNV(spec) mixed with the band]; **g2** = max - min over the four
  exit headings with >= 50 pooled completed excursions of ln(mean excursion duration).

Model: ridge, lambda = 1.0, features standardised by training-fold mean/sd, unpenalised intercept; leave-one-rule-out over
rules with every feature defined. R2_oos = 1 - SSE / sum (y - training-fold mean)^2.

**G1 (per band).** DeltaR2 = R2_oos(B0+g1+g2) - R2_oos(B0) >= 0.10, AND 95% percentile bootstrap lower bound > 0
(2000 resamples of rules applied to the held-out predictions; training-fold uncertainty is not included), AND permutation
p <= 0.05 (g1,g2 shuffled together across rules, B0 intact, 500 permutations, p = (1 + #{null >= observed}) / 501).
**G1 passes iff it passes at both bands.** The permutation requirement is an addition to the draft: a shuffled-target
smoke test on pilot rows reached DeltaR2 = +0.108 by chance at n = 24 (bootstrap interval [-0.15, 0.42]), so the draft
criterion alone is weak. Added before confirmation data.

**Gates (any failure makes a G1 verdict UNINFORMATIVE; whether the criterion passed is still reported).**
Coverage >= 20 of 24 rules evaluable at each band; split-seed Spearman of g1 and of g2 over the predictor seeds
(interleaved halves of the 64) >= 0.7 at each band, no Spearman-Brown correction; headroom R2_oos(B0) <= 0.90.
Reliability is measured on the confirmation predictor seeds, not only projected from the pilot.

**Verdict strings.** `PASS`, `FAIL (informative)`, or `UNINFORMATIVE: ...`. A reliable FAIL rejects the stated
prediction at these scales and with these two features; it does not rule out other gate features, other depth
definitions, or colour-phase-resolved gates.

**Exploratory, never gating (labelled in the output).** g1-only and g2-only increments; B0 plus ln(predictor-seed occupation)
as an oracle-ish ceiling; Spearman of y with g1/g2; stratum membership of evaluable rules. Rotor and random-walk controls
(`results/controls_analysis.json`) and hole-boundary fractions are descriptive.

**Calibration (done before confirmation).** The gate-concentration null is unbiased at all tested event densities
(`results/g1_null_calibration.json`: |mean| <= 0.0015) with sensitivity to a planted set of only ~2.6 null sd at 30
bins / 400 events (the crust-rule regime) and 30 sd at 4000 bins / 60000 events. Rotor: g1 mean -0.043 in both bands;
random walk, band 1: -0.011 (observed concentration below the exposure-proportional null, so not zero for known walkers).
Thread independence and interrupted-resume byte identity verified on 12 specs (`results/determinism.json`). The
reclassification share of label changes is ~1e-4 (median), so crossings are overwhelmingly spatial.

**Departures from the draft (all made before confirmation data).**
1. Colour phase is dropped from the crossing key (tile x heading x kind only): with ~500-1000 events per run, adding
   phase would leave most bins empty. Phase-resolved gates are not tested here.
2. Gate identification/recurrence uses independent *seeds* (predictor vs target) and split seeds for reliability, not
   split observation windows within one run.
3. Seed counts 64 predictor / 32 target instead of 16 per rule (cost is ~0.5 s of wall time per trajectory).
4. The candidate seeds in PLAN.md (2026101501.., 2026101601..) were replaced (collisions with sibling experiments).
5. Permutation criterion added; both bands required (as in the sibling field-age plan).
6. G2 not attempted; the draft's directional return rates are summarised by the single feature g2 above.

**Frozen files (sha256 prefixes at registration).** `src/return_gates.rs` cb801b78048e8713;
`examples/kappa_return_gates_sampler.rs` a6e05ed77a6c9af7; `tests/return_gates.rs` 827820841ec1fe67;
`scripts/analyse_confirm.py` 36d52d1be7856854; `scripts/rg_lib.py` 0a22336b723db6c0; `scripts/run_stage.py` 94aac644f3263ed1;
`results/cohort.csv` 21eb3858b2f75131; `results/seed_count.json` 34e13c6355cbfe60; `results/pilot_runs.csv` 7f252a0552fe770b.

**Commands (from /mnt/f/Code/turmite in WSL, with `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`).**
`cargo test --release --test return_gates`;
`uv run experiments/archive/2026-10-kappa-return-gates/scripts/select_cohort.py`;
`uv run .../scripts/run_stage.py pilot` then `analyse_pilot.py`; `run_stage.py controls` then `analyse_controls.py`;
`uv run .../scripts/verify_determinism.py`;
`cargo run --release --example kappa_return_gates_calibrate > results/g1_null_calibration.json`;
`uv run .../scripts/run_stage.py confirm` then `analyse_confirm.py`.

Results: pilot, controls and calibration as above; **confirmation NOT YET RUN at the time of this registration**.


---

## RESULTS (Stage 1, G1) — 2026-10-16 ~18:00 +13:00

**Status: Stage 1 complete. Verdict `UNINFORMATIVE`; the G1 criterion itself failed at both bands. G2 unrun.**
Confirmation: 24 rules x (64 predictor + 32 target seeds), 2304 trajectories, every one reached both bands (no board
escapes, no budget stops). Analysis: `scripts/analyse_confirm.py` (hash identical to the registered one) ->
`results/confirm_analysis.json`, `results/confirm_analysis.log`; runs in `results/confirm_runs.csv`, manifest
`results/confirm_manifest.json`. Full `cargo test --release` passes (`results/release_tests_full.log`).

| | band 0 (A = 32768) | band 1 (A = 131072) |
|---|---|---|
| rules evaluable | 22 / 24 (2 rules have undefined g1, see below) | 24 / 24 |
| R2_oos baseline B0 | 0.882 | 0.946 |
| R2_oos B0 + g1 + g2 | 0.842 | 0.945 |
| DeltaR2 [95% bootstrap] | -0.039 [-0.118, +0.006] | -0.0004 [-0.033, +0.031] |
| permutation p | 0.85 | 0.060 |
| split-half Spearman g1 / g2 | 0.92 / **0.56** (gate 0.7 failed) | 0.93 / 0.82 |
| headroom (R2 B0 <= 0.90) | ok | **failed (0.946)** |
| band criterion | fail | fail |

Target spread: sd of y across rules 0.81 (log units); held-out RMSE of B0 0.28 (band 0) and 0.19 (band 1).

**What this shows.**
- The registered prediction is not supported: adding the two gate features did not improve held-out prediction of boundary
  occupation at either band (DeltaR2 <= 0, upper bootstrap bounds +0.006 and +0.031, far below +0.10).
- The test is largely *decided by the baseline*, not by the gates. Four predictor-seed features that exclude the boundary's
  own occupation (P/A, boundary-run length, and the depth-profile ratios d1/rim and interior/rim) already explain 88-95% of
  between-rule variance in y out of sample. Adding the predictor-seeds' own ln(occupation) as an oracle changes R2 by
  only +0.001 (band 0) and +0.018 (band 1), so B0 sits at the seed-noise ceiling. At band 1 a +0.10 gain was arithmetically
  unreachable (headroom gate), which is why the verdict is UNINFORMATIVE rather than a clean rejection.
- Band 0: g2 was not reliable across seeds (0.56 < 0.7), even with 64 predictor seeds per rule (the pilot projected 0.73
  from a 4v4 estimate of 0.15); g1 was reliable (0.92) and still added nothing (g1-only DeltaR2 -0.018, exploratory).

**What this does NOT show.**
- It does not show that gates do not exist or do not matter causally: only that these two summaries of crossing locations
  and exit-heading return times add no *predictive* information beyond a depth-profile baseline that nearly equals the
  answer. The depth-profile ratios are themselves a time-budget measurement of the same occupation, so a baseline this
  strong is close to the accounting identity warned about in `notes/kappa-mechanisms-2026-10-15.md`.
- It says nothing about G2 (interventions), colour-phase-resolved gates (dropped from the key), or other tile sizes/depth
  thresholds. No such variants were run.
- Exploratory Spearman of y with g1 / g2: band 0 -0.03 / 0.38, band 1 0.36 / 0.37 (n = 22-24, not corrected, not gating).

**Caveats.** n = 24 rules (6 per label cell); labels from earlier pooled summaries; target and predictor seeds are disjoint but
the rules are the same, so this is within-cohort held-out *seeds*, not held-out *rules* for the features' definitions
(the leave-one-rule-out folds do hold out rules for the regression). Bootstrap does not include training-fold
uncertainty. The 4v4 pilot reliability for g2 was a poor guide for the Spearman-Brown seed rule (band 0). Controls: rotor and
random walk give g1 (observed minus null) of -0.04 and -0.01 rather than 0 (`results/controls_analysis.json`), so g1's absolute
level is not interpretable, only its between-rule ranking.

**Unexplained / follow-ups.** (i) Which gate-free quantity makes B0 so predictive? It is probably the persistent-time-away
budget itself; testing it needs a baseline built from *independent* mechanism quantities, not from occupation-profile
features of the same trajectories. (ii) If gates are to be tested again, drop the depth-profile baseline or use only
features that precede the window (area, shape, prefix), and keep the permutation criterion. (iii) G2 remains a separate
registration. Added to `notes/open-questions-hypotheses.md`.

**Edge case found after the run (reported, registered result unchanged).** Two band-0 rules were excluded because g1 was NaN:
three predictor-seed runs with only 2-6 crossing events had a Poisson-null draw with zero total events, which makes the null
share NaN and poisons the frozen rule-level mean (4 such runs in the whole file, none at band 1). The registered code was not
changed. An EXPLORATORY sensitivity (`scripts/sensitivity_g1_nan.py`, `results/sensitivity_g1_nan.json`) ignores those runs'
g1 only and keeps all 24 rules at band 0: R2(B0) 0.871, R2(B0+gates) 0.842, DeltaR2 -0.029 [-0.104, +0.016], permutation p 0.71,
g1 / g2 split-half 0.90 / 0.56. Same conclusion; the g2 reliability gate at band 0 still fails.
