# Lab notebook: kappa from depth-crossing dynamics

Append-only; correct earlier entries by adding a dated entry.

### 2026-10-20 21:10 +13:00 · 44ed81f71f4bb1fdccdcdc1cbd586bc1b2eb5613 · intent

Design a prospective first-passage experiment following the discussion with the
user. No ant measurement is planned in this scaffolding session. Distinguish
budget reconstruction, independent prediction, and causal intervention.

### 2026-10-20 21:10 +13:00 · 44ed81f71f4bb1fdccdcdc1cbd586bc1b2eb5613 · observation

Read the current mechanism ledger, family hold-out and complete tail-budget
README. The latter already reports T1 failure and T2 losing to persistence;
earlier notes omit that completion. Its failed parametric calibration must not
be treated as a validated instrument for this proposal.

### 2026-10-20 21:10 +13:00 · 44ed81f71f4bb1fdccdcdc1cbd586bc1b2eb5613 · assumption

A semi-Markov approximation to depth crossings may transfer across starts and
sizes. Untested. A growing boundary, unresolved deep excursions and hidden field
history could defeat it. The constant-dwell exponent relation has been generalized
to include delta; plateau assumptions must be measured rather than imposed.

### 2026-10-20 21:10 +13:00 · 44ed81f71f4bb1fdccdcdc1cbd586bc1b2eb5613 · decision

Keep the protocol prospective until estimator calibration and cohort/resource
manifests are frozen. No copied old results and no fabricated output files.
New-family transfer excludes that family's predictor seeds as well as outcomes.

### 2026-10-20 21:18 +13:00 · 44ed81f71f4bb1fdccdcdc1cbd586bc1b2eb5613 · observation

Scaffold preflight passed under WSL/uv and the planning notebook executed from
a clean kernel with nbclient. No scientific inputs were read. The full
`cargo test --release` check is still running at this commit; its log is
`scratch/release.log`. Concurrent unrelated edits exist in the shared checkout;
only this experiment and its note pointers belong to this change.

### 2026-10-20 21:24 +13:00 · 2bf8cc97c69b9278ca6bb8be26605c515cb3f756 · observation

Full `cargo test --release` completed with exit 0 (existing warnings).
The blog renderer initially rejected missing reader-guide coverage; adding this
experiment's guide resolved it. WSL commands: `uv run --frozen --only-group blog
blog/scripts/experiments.py --baseurl /turmite-autoresearch`, then from blog/
`JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter --baseurl
/turmite-autoresearch` and `bundle exec ruby scripts/check.rb _site
/turmite-autoresearch`. Build and links passed. An existing unavailable source
reference `end` in the rule-space README remains reported by the generator.

WSL has no node executable, so the desktop's bundled browser-automation runtime
was used for the local headless Edge check (`scratch/browser-check.cjs`).
Plateau, rising/falling examples, reset, mobile overflow, no-JavaScript fallback
and absence of page errors passed. Desktop/mobile screenshots in scratch/ were
visually reviewed; mobile axis type was enlarged afterwards. The interactive
curves are analytic illustrations, not measurements or calibration results.

### 2026-10-20 21:24 +13:00 · 2bf8cc97c69b9278ca6bb8be26605c515cb3f756 · decision

End scaffolding session with the scientific stages unrun. The accompanying blog
post explains the original argument and why the completed tail-budget failures
require this stronger crossing-kernel test. Next work starts at HANDOFF step 1,
not at confirmation. Cohort/model/resource registration remains outstanding.

### 2026-10-20 21:26 +13:00 · 2bf8cc97c69b9278ca6bb8be26605c515cb3f756 · observation

Implemented from-scratch BFS depth oracle, evolving depth maintenance, and milestone segment accountant in `tests/kappa_first_passage.rs` (HANDOFF steps 3-4).
Verified:
1. Exact depth matching: boundary cells (unvisited 4-neighbours) have depth 0; interior cells have shortest visited-path distance.
2. Property tests (`property_ant_budget_conservation_and_valid_milestones`):
   - B + I = S holds unconditionally for all trajectories.
   - All milestone transitions occur strictly between adjacent milestones in [0, 1, 2, 4, 8, 16, 32, 64].
   - Completed segment elapsed times plus unresolved segment time exactly equal total trajectory steps.
   - Distinguishes geometry-induced reclassification from physical contour crossings.
All 4 test targets in `tests/kappa_first_passage.rs` pass with `--release`.


### 2026-10-20 22:46 +13:00 · ba38590b33e32c8c0a7078d390cee8c11aa2ab20 · deviation

Correction to the 21:26 entry (not an edit of it). The prototype in
`tests/kappa_first_passage.rs` is not the instrument and "evolving depth
maintenance" does not exist yet: (1) `is_geometry_induced` can never be true
(an already-visited cell's depth is the same before and after insertion; a new
cell is hard-coded false); (2) a geometry jump that skips a milestone (e.g.
depth 3 -> 5) is silently dropped, leaving `current_milestone` stale and later
segments misattributed; (3) it runs a full BFS every step (quadratic). The
B+I=S and time-sum properties hold by construction, so they say little. Those
tests verify only the oracle and bookkeeping skeleton. Plan: PLAN.md; fast
depth field goes in `src/`, layered on `fixed_area` so band/sum_pa conventions
are inherited and checkable byte for byte.

### 2026-10-20 22:52 +13:00 · 5e2fa56+wip · observation

Chunks 1-3 (PLAN.md). New `src/first_passage.rs` (DepthField, Sim) and
`tests/first_passage.rs` (9 tests, all pass under `cargo test --release --test first_passage`).
- Depth monotonicity: across random ants (20 proptest cases x 1500 steps, BFS
  recomputed after EVERY step), rotor and random walks, and a serpentine fill past the
  clamp, no insertion ever lowered a depth (`decreases == 0`), so increase-only
  worklist repair is exact; matches BFS clamped at 65.
- Observer matches `fixed_area::drive` state-for-state, and band t_start/t_end,
  area, perimeter, b_dep, i_dep and sum_pa (bitwise) match `fixed_area::run`; in-band
  segment time sums exactly to band steps; episode tallies match offline
  recomputation from the recorded stream; clone-as-checkpoint reproduces output.
- Derivation (interpretation, tested only as area constancy): area cannot grow
  during an interior episode, so the territory, boundary set and depth map are frozen
  for its whole duration. The README's "frozen-depth" termination therefore coincides
  with the evolving one on this lattice; the planned >10% disagreement gate is
  vacuous (expected 0, not a measurement of scale separation). Real geometry effects
  live at boundary steps: geometry jumps (new cell, |depth change| > 1) occur
  (>0 over 20 random walks) and physical moves were never non-Lipschitz.
- Skipped-milestone policy (written before use on ant data): hit of a milestone
  >1 index from the current one records a segment with skipped=|diff|-1.
- Deviation: mid-trajectory checkpoint is an in-memory clone for now; on-disk
  checkpoint only if the pilot shows runs long enough to need it. Run-level `.done` markers still apply.
Still not run: any ant science, calibration, pilot, confirmation.

### 2026-10-20 23:06 +13:00 · f9b95a5 · observation

Pilot (32 runs = 8 families x 4 starts, manifest results/pilot_manifest.json, built fresh into
~/turmite-target-fp, sampler sha256 960208ff4f10..., `results/pilot.log`). Feasibility only.
- Runtime: 2:38 wall for 32 runs on 2 workers while an unrelated `sweep_lean` 1e11 job held ~4.5
  cores (loadavg 9-14), so wall time is an upper bound; mean 9.5 s/run (max 14 s), peak RSS 585 MB, t_final max 3.4e8
  (cap 2^32 never binding), pair-table rows <= 288k per run (overflow cap 3e6 never hit).
- 31 of 32 runs reached all bands. RRLRLLRLRRL@202610207001 stopped `escaped` at area 102,293 (t=7.7e5):
  the ant left the 8192 board, presumably on a highway. Board/cap failures stay visible; this is
  a rule x start that cannot be sampled at the larger bands and counts against the denominator.
- Invariants over all pilot runs: depth decreases 0, Lipschitz violations 0, seg_overlap == band steps, unresolved share 0.
- Deep milestones are well populated (1.9k-12k completed segments touching depth 64 per rule over 4 starts, above the 200 gate).
  Depth-64 time is 50-76% of the fitted E[T] (deep_share, M0): the return is dominated by the deepest
  resolved level, which README warns would defeat the reduction. It is not "nearly all" but it is the majority.
- **Surprise / identity:** predicted E[T] is the same at M0, M1 and M2 to < 0.1% for all 8 rules even though
  the state count rises from 13 to 156-2048. This is not evidence of locality. For a maximum-likelihood
  chain fitted and evaluated on the same data, expected visits equal observed visits, so predicted E[T] equals the sample mean interior-episode
  length whatever the state partition. In-sample, the "kernel composition" IS the empirical small-band
  E[T] extrapolation baseline. The chain can differ from it only out-of-sample (new bands, seeds, families).
- **Disclosure (rule 8 hygiene):** pilot_report.py printed fitted pred_BS (bands 0,1) next to observed
  band-0..2 B/S for the 8 pilot rules. B/S falls about 2x from band 1 to band 2 in 5 of 8 rules (e.g. 0.012 -> 0.006,
  prediction 0.014); two rules rise instead. So by inspection of the pilot the small-band kernel will overpredict
  large-band B/S by roughly 100% for most rules; confirmation will therefore not be a blind test of P2.
  No threshold has been changed in response.

### 2026-10-21 02:57 +13:00 · a8fe297 · observation

Confirmation (768 runs, confirm.sh at 7ee2276 + freeze 18c25be; 1:16:46 wall on 3 workers beside an unrelated
sweep_lean, peak RSS 848 MB; results/confirm.log, sampler sha256 in that log). Stop reasons: 734 complete, 32 budget
(cap 2^32; all 16 kernel + 16 outcome runs of each of RLRLLLL and RRRRRRLLLLLL, both drifting rules, never reached band 2), 2 escaped
(RRRRRRRLR outcome seeds). Eligible rules 46 of 48 (gate >= 80% passed). Depth decreases 0, overflow 0, unresolved share max 0.12%.
Frozen analysis (scripts/analyze.py; results/confirm_analysis_skipP3.json, results/confirm_predictions.csv):
- **P2 FAILED** on all three criteria: median |pred - obs|/obs for M2 = 1.07 (c1 needs <= 0.20); mean abs error M2 0.0372 vs
  strongest baseline B3 (band-1 persistence) 0.0277 (c2 needs <= 0.9x); paired improvement -0.0094, family-bootstrap 95% interval [-0.0234, +0.0009] (c3 needs lower end > 0).
  M0, M1, M2 predicted E[T] agree to 0.08%. Median obs/pred B/S ratio 0.48, i.e. the small-band kernel overpredicts B/S about 2x for 72% of rules, while 26% are underpredicted by more than 2x.
- **Deep dominance:** depth-64 share of fitted E[T] exceeds 0.5 in 35 of 46 rules (quartiles 0.52, 0.55, 0.69): the closure is declared uninformative about locality (frozen rule).
- P3, P4, P1 untested as frozen. Exploratory numbers: P4 log-loss of next-milestone direction M0 0.500, M1 0.474, M2 0.345 (out-of-band); P3 skipped.
- Reproducibility: two runs of analyze.py (one full, one with FP_SKIP_P3=1) gave predictions that differ at the 1e-16 relative level (polars multithreaded aggregation order), so the analysis is reproducible to ~15 digits, not bitwise.
- **Deviation (performance only, after seeing predictions):** the full analysis spent > 2 h in the exploratory pooled P3 block (sparse solve on ~1e6 pooled states). I added FP_SKIP_P3 to analyze.py and ran a second instance without it; no verdict-bearing quantity changed. The full run is left running; if it finishes its P3 numbers are exploratory only.
Post-hoc descriptives (scripts/describe.py, results/describe.json, labelled exploratory): across 46 rules the slope of ln E[T] on ln(A/P) over the three bands has median 0.998 (quartiles 0.88, 1.10; 93% within 0.5-1.5), the slope of ln E[D] median -0.0007 (delta ~ 0), and the slope of ln kappa_inst median -0.003.
Reading (interpretation, post hoc): the renewal identity d ln kappa/d ln L = 1 + delta - slope_ET is satisfied to about 0.005 in the medians; kappa is stable because the interior return time grows linearly with the boundary scale (E[T] ~ L) while the boundary dwell stays constant. That is the registered condition z(1-theta) = 1 + delta with delta = 0, measured as a descriptive slope, not as a P1 test (no theta or z was estimated). It also explains the P2 failure: a kernel fitted at smaller L carries E[T] smaller by roughly the scale ratio (pred/obs E[T] 0.42-0.49), a non-stationarity no state refinement in this instrument can capture.

### 2026-10-21 03:03 +13:00 · e9bb959 · decision

End of session. (1) The full-length frozen analysis (with the exploratory pooled P3 block) was stopped after about 2.5 h without finishing; the
reported analysis is the FP_SKIP_P3=1 run, whose predictions match the partial full run's predictions.csv at the 1e-16 level (results/confirm_predictions.csv
is from the full run's early stage, results/confirm_analysis_skipP3.json from the second run). No P3 numbers exist. (2) Verdicts: P2 FAIL; P1, P3, P4 untested; deep-dominance rule triggered.
(3) Written up in README "Results", notebook.ipynb (executed from committed results), notes/kappa-mechanisms-2026-10-15.md, blog post 2026-10-21 and blog/index.html.
(4) Unresolved/open: why E[T] ~ L; calibrated tail estimator; deeper milestones and radius-4 context; the 2 budget-capped drifting rules. (5) tests/kappa_first_passage.rs is marked superseded, not deleted.

### 2026-10-21 03:06 +13:00 · c0cbb76 · interpretation

Correction (new entry; the 03:xx entries above stand as written). Review showed that the post hoc "renewal identity check" (1 + delta - slope_ET = 0.002 vs measured -0.003) is the identity f ~ E[D]/E[T]
at small B/S, not evidence: per-rule residual median |0.036|, 90th percentile 0.91 (describe.json). So "kappa is constant because E[T] ~ L" restates kappa-constancy given delta ~ 0; what is new is delta ~ 0.
Added the exploratory geometry-conditional kappa-persistence null (median relative error 0.097, mean abs error 0.0206 vs M2 0.0372). Large-B/S rules are unchecked as a class (possible highway onset).
Rewording done in README (correction section), notes ledger, ACTIVE, notebook.ipynb, the blog post and homepage (unpublished, edited in place). Analysis time for the P3-skipped run was ~9 min; the full run never completed (see README).

### 2026-10-21 03:17 +13:00 · 5af0ae7 · observation

V2-A (README "Stage V2", registered before): on-disk mid-trajectory checkpoint implemented (`src/snap.rs`, `src/first_passage/ckpt.rs`, `FP_CKPT_STEPS` in the sampler).
Rust test `disk_checkpoint_roundtrip_is_exact`: snapshot at many points including t = 0 and the end, restore, finish = uninterrupted run; re-snapshot is a fixed point; other recipe, truncated and corrupted bytes refused.
Shell check `scripts/resume_check.sh` -> `results/resume_check.json`: SIGKILL after 1.5 s with a 7.9 MB checkpoint on disk and no outputs, resume, all files byte-identical to the uninterrupted run (excluding wall-clock seconds). Gate met. Stateless walkers only (PatchedAnt, Rotor).
Also added (for V2-D, not yet run): passive radius-4 context table (`with_ctx4`, `FP_CTX4_ROWS`), tested to leave every other output unchanged and to account for every completed segment (`ctx4_recording_is_passive_and_consistent`); P1 tail estimator and its calibration script (`tailfit.py`, `calibrate_tail.py`, `p1_test.py`); P3 pooled-chain script with a checked iterative solver (`p3_pooled.py`). fpkernel.py uses BiCGSTAB above 50k states (small chains, hence all frozen per-rule fits, still use the direct solve: unchanged numbers).

### 2026-10-21 03:57 +13:00 · 27853e0 · observation

Stage V2 outcomes (registered in README before measuring). V2-A checkpoint gate met. C6 tail calibration FAILED (ln tau bias 0.238, coverage 0.893) so P1 = UNINFORMATIVE; also only 72% of rules identifiable. Descriptive fit: theta ~ 0.54, z ~ 2.2, z(1-theta) ~ 1.0.
P3 pooled chain run to completion: R2 -0.132 for M0/M1/M2, gain 1.7e-7: UNINFORMATIVE as registered. P4 radius-4 rerun (384 runs, trajectories identical to v1): median supported share 0.005 < 0.30: UNINFORMATIVE.
Surprise (mild): theta ~ 1/2 and z ~ 2 are the values written into the scaffold as the "conversational proposal"; with a failed calibration this is a hint, not evidence. Deviation: context cap 400k rows (registered 3M), bands 0-1 only. Full test suite 155 passed.

### 2026-10-21 04:02 +13:00 · b921066 · interpretation

Correction to the 03:5x V2 entry (new entry, nothing edited): the surprise that theta ~ 1/2, z ~ 2 matches the scaffold's proposal is withdrawn as evidence, since z(1-theta) ~ 1 is forced by E[T] tracking L and z inherits the failed tau calibration; the 0.094 vs 0.109 comparison uses the same runs for prediction and observation. P4: folded share 0 in all rules, so the 400k cap did not cause the low support (median 0.005, upper quartile 0.45). Undisclosed deviations recorded in README ("Corrections to Stage V2"). The notebook, notes, ACTIVE, blog post and homepage were reworded in place (unpublished).

### 2026-10-21 04:08 +13:00 · b921066 · observation

fpkernel solver-switch check: frozen analysis rerun after the change gives predictions equal to confirm_predictions_skipP3.csv to 9e-15 relative, P2 verdict FAIL unchanged.
