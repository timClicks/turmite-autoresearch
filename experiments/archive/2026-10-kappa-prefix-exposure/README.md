# Why would early rule colours set kappa?

Status: **instrument built and piloted; confirmation registered 2026-10-16 00:05 (see Registration at the end), run complete 2026-10-16, see Results at the end**. The draft sections below are superseded where the Registration says so.
Created 2026-10-15 22:54 +13:00, base `b3a0f762ac2230b5df92188206a4d3a1081897be`
(dirty tree). [Mechanism note](../../../notes/kappa-mechanisms-2026-10-15.md).

## Question and mechanism

Does a rule prefix determine a fresh-cell return kernel that controls entry
into long interior excursions? Prefix prediction is established only within
the studied stationary cohort; it is not yet an exposure-based mechanism.
This extends W6's mutation pilot rather than re-running a letter-position scan.

## Draft design and predictions (freeze before ant outcomes)

1. Select 24 distinct base rules of lengths 13–14 from a versioned census
   manifest, stratified by pre-existing regime label and prefix support,
   without ranking on prospective mutation effects. Use 12 development and
   12 untouched validation bases, grouping by prefix family where possible.
   Report whether validation tests unseen prefixes or new suffixes; these
   are different claims. Include nonstationary bases as a separate stratum.
2. For each base choose two early positions (indices 0..7) and two later
   positions (8..n-1), balanced deterministically over bases. Flip each
   position separately. Use 16 common start-patch seeds per base/mutant;
   pair initial patches and headings. Hash explicit rules, positions and
   initialized patches; do not canonicalize away the physically chosen
   fresh colour. Pilot four separate starts per base for instrument cost.
3. Candidate areas: 32768 and 131072, bands A/16; cap 2^29 steps per run.
   Log per-colour exposure separately in the boundary, depth 1–4 and bulk,
   plus visit-count classes. For newly discovered cells, follow the next
   64 steps and record heading/displacement, boundary departure and whether
   an interior episode lasts >=64 steps. Handle overlapping launch records
   as correlated observations, not independent samples.
4. Fit a development-only model predicting mutation-induced changes in long-
   excursion launch probability from changes in this return kernel and
   exposure. Combine with separately estimated return durations to predict
   changes in B/S; explicitly state any geometry inputs needed for kappa.
   Draft P1: validation paired effect directions agree in >=70% of resolved
   pairs and paired-effect R2 >=0.20, with base-bootstrap lower bound >0.
   Resolution threshold is fixed from pilot replicate sd before confirmation;
   report all effects and counts, not only resolved pairs.
5. Draft P2: the exposure/kernel model improves held-out paired-effect R2 by
   >=0.10 over a position-only early/late model. If position remains predictive
   but exposure/kernel does not, reject this account of the prefix advantage.
   Compare early and late edits at overlapping exposure; no overlap means
   the matched-exposure contrast is unidentifiable, not a positive finding.

## Controls and failure conditions

Unchanged-rule clones must agree exactly. Joint cyclic relabelling of the
rule and all field colours must reproduce trajectories; rotating the rule
alone is a different initial-background experiment. Before first exposure
to the altered colour, base/mutant trajectories must be identical. After
divergence, common seeds no longer imply equal environments: record that
limitation rather than claim direct mediation.

Retain escape, periodicity and regime transitions as outcomes. Analyze total
mutation effects on all attainable runs and conditional stable-regime effects
separately; no late-kappa-based exclusions. Bootstrap by base (2000 draws),
not by mutation or episode. Report sd over paired starts, censoring and power.
If fewer than eight validation bases have informative attainable comparisons,
report inadequate coverage rather than expand after seeing effect directions.

## Implementation and next action

Read W6 and the latest prefix audit first. Reuse rule/start generation only
after verifying its colour convention. Add reference-checked exposure and
first-divergence tallies in `kappa_prefix_exposure_*` examples. Freeze a manifest
with base/mutant relations, seed roles, selection code and input hashes.
Prefer tail-budget estimates if that model passes; if it fails, test launch
effects but do not claim a quantitative kappa explanation.

See [PLAN.md](PLAN.md), [SCHEMA.md](SCHEMA.md), and [HANDOFF.md](HANDOFF.md).
Results: **NOT RUN**. No scientific test has passed or failed in this scaffold.

## Scaffold verification — 2026-10-15 22:59 +13:00

Preflight and the planning notebook executed successfully under uv/WSL; local
Markdown links resolve. The shared workspace passed cargo test --release.
No new instrument or scientific prediction was tested. Commands are in HANDOFF.md;
verification scope and the local test-log path are recorded in NOTEBOOK.md.


## Registration (frozen 2026-10-16 00:05 +13:00, BEFORE any confirmation spec is run)

Base commit `997c9b2da6efa526fc6c5a57104d103e1345e916`, working tree dirty. The 16-seed, positions-0..7,
primary-kernel-w=64 items of the draft above are superseded by this section (reasons: NOTEBOOK entries of
2026-10-16 00:20 "deviation" and "decision"; pilot data used for those choices are development bases only).
No validation-base mutant has been simulated. Source hashes (sha256): `src/prefix_exposure.rs` 1f9dc086..., 
`examples/kappa_prefix_exposure_sampler.rs` 10966a7a..., `tests/prefix_exposure.rs` 5f7e4ac3..., `scripts/kpe_lib.py` 67917ff6...,
`scripts/confirm_analyse.py` 971f6570... (full hashes are written to `results/confirm_run.json` at launch and to `confirm_analysis.json`
after the run), `results/arms.csv` b3924e38..., `results/cohort.csv` 2ef3bf89..., `specs_confirm_dev.txt` 547e6532..., `specs_confirm_val.txt` 833d3f15....

**Design.** 24 bases (12 dev, 12 val; 10 stationary + 2 nonstationary per side; `results/cohort.csv`), 7 arms per base
(`base`; `a1`,`a2`,`m1` = flips at positions 1,2,3, "early"; `l1`,`l2` = two later positions, "late"; `p0` = position-0 flip, descriptive
anchor only), 64 seeds per (base,arm): prediction seeds 2026101571001..071032, target seeds 2026101571033..071064. Specs: 5376 dev + 5376 val
= 10752 (lists in `results/specs_confirm_*.txt`). Boards 4096^2, step cap 2^29, bands A in [32768,34816] (band 0) and [131072,139264]
(band 1, primary), launch window 64, episode thresholds {1,16,64,256,1024}. Mutants not canonicalised. Compute budget about 10 CPU-hours
(pilot mean 3.3 s/spec), run at 3 threads.

**Definitions** (`scripts/kpe_lib.py`; pooled ratios of sums over a seed set). B/S = boundary steps over steps in the band; kappa_end;
Lam_w = episodes begun in band lasting >= w states per discovered cell; effect of a mutation `y_lnbs` = ln(B/S)_mutant - ln(B/S)_base on TARGET
seeds; predictor `x_lnLam_w` = same difference of ln Lam_w on PREDICTION seeds (disjoint from targets). A pair is *attained* if both arms have
>= 16 valid runs in both roles (valid = band reached, no short open episode at stop). Escapes, cap hits and unattained mutants are reported, not
imputed. Resolved pair: |y_lnbs| > 2 se, se = s_pool*sqrt(2/32) with s_pool = 0.528 (band 0) / 0.649 (band 1) from the v2 development pilot.

**Gates (checked before P1/P2 verdicts).** (G1) coverage: >= 8 validation bases with an informative attained stationary pair, else "inadequate
coverage", no verdict (no expansion after seeing effects). (G2) reliability: over development stationary pairs, Spearman correlation of y_lnbs
between the two target-seed halves (seeds 1-16 vs 17-32 of the target set) >= 0.30, else P1 and P2 are uninformative. (G3) P2 only: overlap of
early and late mean read depth: >= 30% of early values inside the late range and >= 6 pairs on each side; else "unidentifiable".

**Predictions (primary: stationary bases, band 1, arms a1,a2,m1,l1,l2; the model is fitted on development bases only and scored on validation).**
- **P1.** Held-out validation R^2 of `y_lnbs ~ x_lnLam256` (OLS on dev; development slope must be negative) >= 0.20, base-bootstrap
  (2000 draws, seed 7015001) lower 95% bound > 0, >= 10 resolved pairs, and sign agreement >= 70% among resolved pairs. w=64 and 1024 are
  secondaries reported without a bar. Expectation, written now: the pilot's association (Spearman -0.17 to -0.37 for w=256) is weak, and replicate
  noise dominated it, so I expect P1 to be marginal; I put about 30% on it holding.
- **P2.** An ex-ante exposure model (lead/mid position indicators + mean read depth + log boundary read share, from the base run on prediction
  seeds) raises held-out R^2 over the position-only model by >= 0.10 with base-bootstrap lower bound > 0, subject to G3. If position stays
  predictive but exposure does not, this account of the prefix advantage is rejected. Expectation: about 20%; pilot exposure and position are
  strongly collinear (R^2 0.33-0.44).
- **P5 (sign-mixed kappa, from kappa-rule-space W6m; key `P5_sign_mixed_kappa`).** W6m found early letters change kappa at fixed area in both directions (M2 failed: the early
  effect is not a mean shift; signed shifts by letter were +0.109, -0.032, -0.004, +0.048 in the W6 pilot, no consistent direction). Prediction:
  for positions 1-2 (arms a1,a2; stationary; band 1; attained; dev+val pooled, n >= 20) the share of pairs with ln(kappa_mut/kappa_base) > 0 is in
  [0.25, 0.75] and |mean shift| <= 0.5 x median |shift|. A consistent direction (share outside the interval or |mean| > half the median) falsifies the
  sign-mixed expectation. Consequence: P1's predictor must carry sign, which is why the Lam change is regressed on the signed y, not on |y|.
- **Descriptive, no bar:** valid-run shares for early vs late arms (pilot: early 0.75, late 0.92), median |y| early vs late, kappa shifts, position-0
  anchor, nonstationary bases (listed separately), per-colour exposure tables. Per-arm tests beyond P1-P3 are exploratory and labelled so.

**Commands.** Run (WSL, repo root, `CARGO_TARGET_DIR=~/turmite-target`, `RAYON_NUM_THREADS=3`; `.done` markers make it resumable and the output
is byte-identical for any thread count, verified in the pilot):
`cargo run --release --example kappa_prefix_exposure_sampler -- dumps/confirm_dev 536870912 4096 64 32768-34816,131072-139264 < results/specs_confirm_dev.txt`
(same with `confirm_val`; logs `results/confirm_run_*.log`). Analysis: `uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/confirm_analyse.py`
-> `results/confirm_pairs.csv`, `results/confirm_analysis.json`. Pilot stats for the new arm set were not regenerated; the pilot numbers quoted
above come from `results/pilot_stats_v2_oldarms.txt` (same bases, arms 0..7 early pool).

Results: see "Results" below.

## Registration — 2026-10-16 (git 997c9b2, dirty tree; hashes in results/registration_hashes.txt)

Registered BEFORE any validation-base mutant, and before any confirmation run on development bases, was simulated. Only the 336-spec development pilot (seeds 2026101570001..04) has run. Full rationale and deviations from the draft above: NOTEBOOK.md (2026-10-16 entries). Handover: [HANDOVER.md](HANDOVER.md).

**Design (frozen).** 24 bases of length 13-14 from W3c's 176 usable rules (`results/cohort.csv`): 12 dev + 12 validation, each 10 stationary + 2 nonstationary; dev and validation 5-letter prefix families disjoint. Arms per base (`results/arms.csv`, rules used as written, never mirrored): base; single-letter flips at positions 1 (a1), 2 (a2), one in 3..7 (m1), two in 8..n-1 (l1, l2); position-0 flip (p0, descriptive anchor only). Seeds 2026101571001..64 per arm: first 32 = prediction role, last 32 = target role. Radius-2 patch (shared by base and mutant of equal length). Bands [32768, 34816) and [131072, 139264); primary band = the second. Grid 4096 (walker stops 12 cells short of the edge), cap 2^29 steps, launch window 64, episode thresholds 1/16/64/256/1024. Specs: `results/specs_confirm_{dev,val}.txt` (5376 each, ~10 CPU-h total at 2.6-3.3 s/spec).

**Estimators (frozen = scripts/confirm_analyse.py + kpe_lib.py).** Per arm and role, pool valid runs by ratio of sums (>= 16 valid seeds per arm and role, else unattained). Y = ln(B/S)_mutant - ln(B/S)_base on target seeds. X = ln Lam_w(mutant) - ln Lam_w(base) on prediction seeds, Lam_w = (episodes begun in band lasting >= w states + 0.5)/new cells. Stationary bases only in tests; nonstationary listed separately. Resolved pair: |Y| > 2 * se, se = 0.700*sqrt(2/32) (primary band; 0.533 for band 0), constants from pilot v3. Bootstrap over validation bases, 2000 draws, seed 7015001. Coefficients from dev bases only.

**Gates (uninformative if failed, not a null).** Dev split-half Spearman of Y (two 16-seed halves of target seeds) >= 0.30; >= 8 validation stationary bases with an attained pair; all specs complete; tests pass at the registered commit.

**Predictions.**
- **P1 (primary):** dev-fitted Y ~ X(w=256); validation held-out R^2 >= 0.20 with bootstrap lower bound > 0, AND sign agreement >= 70% among resolved pairs with >= 10 resolved. w=64 and 1024 secondary. Confidence ~45%.
- **P2:** ex-ante model (lead/mid dummies + mean read depth and ln boundary share of the altered colour, from base runs on prediction seeds) beats the lead/mid dummies alone by held-out delta R^2 >= 0.10, bootstrap lower bound > 0; unidentifiable (not a pass) unless >= 30% of early mean-depth values lie in the late range and >= 6 pairs each side. Confidence ~20%.
- **P3:** median |Y| of lead (positions 1-2) over late >= 1.5, bootstrap lower bound > 1 (replicates the W6 matched-area finding on fresh mutants at fixed area). ~70%.
- **P4 (descriptive):** sign mix of resolved lead pairs. **P5 (descriptive):** valid share early < late (pilot: 0.85 vs 0.93).

**Interpretation, fixed now.** P1+P2 true: launch-rate change tracks the B/S change and exposure predicts it beyond position (predictive, not yet causal). P1 true, P2 false: launches account for it but why a letter changes them is open. P1 false with gates passed: the w=256 launch-frequency account of the prefix effect is rejected at these scales. Any gate failed: uninformative. All results reported, including nulls.

Results: **NOT RUN** (confirmation).

### Registration addendum (2026-10-16 00:08 +13:00, still before any confirmation outcome was read)

The confirmation was launched at 00:03:33 (`results/confirm_run.json`), a little before the 00:05 stamp above (the registration text was
written and saved before launch; the stamp is approximate). While I was registering, `scripts/confirm_analyse.py` was edited on disk by another
process (00:03:06) to add two items I had not registered: **P3** (position gradient: median |y_lnbs| of leading-position arms a1,a2 over late arms
l1,l2 on validation, held if ratio >= 1.5 and base-bootstrap lower bound > 1; replicates the W6 matched-area M1 on fresh mutants) and
**P4** (descriptive: share of positive y_lnbs among resolved leading-position pairs, expected near 0.5 per W6m; no bar). I adopt both as
registered here, since no outcome had been read, and renamed my sign-mixed kappa item P5. The sha256 of the script in `confirm_run.json`
(458c8eaf...) is the pre-run version of that edited file (before my P5 rename, which does not alter any computation); the final hash is in
`confirm_analysis.json`. The analysis script was only dry-run on pilot data (mechanics, not results).

## Results (confirmation run, analysed 2026-10-16 03:49 +13:00)

All 10752 specs finished (`results/confirm_run.finished`; logs `results/confirm_run_{dev,val}.log`; analysis `results/confirm_analysis.json`,
`confirm_analysis.log`, `confirm_pairs.csv`). Stops: dev 4863 complete / 192 hit the 2^29 cap / 321 escaped; val 4556 / 497 / 323.
Coverage: 10 validation bases informative (gate G1 met, >= 8); 39 validation and 44 development attained stationary pairs (25 early, 14 late on
validation). Reliability gate G2: Spearman 0.97 between target-seed halves (informative). Primary band 1, stationary bases, bootstrap over 10
validation bases (so intervals are wide).

| Item | Criterion | Observed | Verdict |
|---|---|---|---|
| P1 (w=256) | held-out R^2 >= 0.20, boot lower > 0, >= 10 resolved, agreement >= 70%, dev slope < 0 | slope -0.26; R^2 0.105, CI [-0.21, 0.32]; 20 resolved, agreement 75%; Spearman -0.41 | **FAILED** (R^2 and CI bars). w=64 R^2 0.103, w=1024 0.092: same |
| P2 | delta R^2 >= 0.10, boot lower > 0, G3 identifiable | R^2 position 0.045, exposure 0.260, delta +0.215, CI [-0.002, 0.281]; G3 met (40% overlap, 20/31 pairs) | **FAILED** on the interval bar by 0.002; point estimate clears 0.10. Not a clean rejection or support |
| P3 (position gradient) | median abs y early(1-2)/late >= 1.5, boot lower > 1 | ratio 9.0, CI [1.27, 27.6]; n 17 vs 14 | **HELD** (wide interval) |
| P4 (descriptive) | none | 6 of 11 resolved leading pairs positive (0.55) | sign-mixed as expected |
| P5 (sign-mixed kappa) | share positive in [0.25, 0.75] and abs mean <= 0.5 median abs | n 34, share 0.47, mean -0.11 (CI [-0.41, 0.14]), median abs 0.33 (a1 -0.28, a2 +0.04) | **HELD** |

Descriptive: median abs d ln(B/S) early 0.47 (dev and val) vs late 0.15 (dev) / 0.07 (val); median abs d ln kappa early 0.31 / 0.41 vs late 0.14 / 0.12.
Valid-run share early 0.83 / 0.82 vs late 0.93 / 0.73 (dev / val: late validation mutants hit the cap more often than in dev). Position-0
anchor: median abs y 0.55 (n 22). Nonstationary bases are listed in the JSON (large positive y for most; not tested).

Interpretation (limited). The prefix/position effect at fixed area replicates on fresh mutants (P3) and is sign-mixed (P4, P5), consistent with W6/W6m.
The proposed mechanism, that the change in the rate of long interior excursions launched from fresh cells carries that effect out of sample,
is not supported at the registered bar: Lam_256 explains about 10% of validation variance with an interval including zero. Exposure features add
+0.215 R^2 over position alone, but the lower bootstrap bound is just below 0, so this is suggestive only. Caveats: 10 validation bases;
early mutants fail to attain more often (selection); the predictor and target share the base run only through the ratio, and common seeds diverge
after first exposure (no direct mediation claim). Script provenance: the analysis hash is fcae4442... (the script was edited by another process
before the run, see addendum; the P1-P3 computations match the registered text). Git HEAD at analysis was 269288e (HEAD moved during the run; the
sampler sources were unchanged, hashes in `confirm_run.json`).
