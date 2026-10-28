# Active work and open items

Living index, last updated 2026-10-25 (square-ring filler follow-ups added to the backlog; priorities unchanged); before that 2026-10-23: priorities narrowed after reviewing the record at
`ac8d88dd8cb047b1a46fecdbade8b633b9165d59`. The sequence below governs new work;
the retained backlog is context, not a list of simultaneous commitments. Remove an item when it is
done or dropped; record the outcome in the experiment's NOTEBOOK and the relevant note, not here. Scientific claims belong in
`notes/open-questions-hypotheses.md`; this file only tracks what is unfinished.

## Pointer (2026-10-28): excursion-duration collapse stage 1 + Revisions 1–2

`experiments/2026-10-27-boundary-excursion-durations/` (stage-1 registration `9bfa496`; Revision 1 registration `9c2aeea`; Revision 2 registration `900f25f`, each before its measurement).
Implements P-C / Q32 from `notes/cube-root-routes-2026-10-26.md` on PR #18 (reference by branch/PR; do not mint colliding Q numbers here).
Stage-1: **revise** (RW D calibrator never grows L). Revision 1 reflecting cup: L grows but compactness (A/P²) fails and Score prefers S (frontier trapping); C1' **inadequate**; confirmation **not run**; cup-as-D design **retired** (`NR-20261027-reflecting-cup-d-calibrator`). MF L-control still passes; rotor inconclusive. Revision 2: Eden-style and IDLA both pass compactness but the frozen number-weighted Score does not prefer D (Eden S, IDLA inconclusive); gate **fail**, confirmation **not run**; both retired as D calibrators for this Score (`NR-20261028-excursion-score-compact-d-calibrators`). Instrument limitation, not an ant result. Paused: any next step needs a newly registered observable (e.g. tail-restricted collapse) calibrated on these walkers before ant data.

## Next phase: boundary access, regime validation, closure

**Central question:** what makes boundary access settle into the scaling needed
for cube-root growth, and when does it fail? Start with square-grid ants.
One substantial new experiment at a time. Planning allocation: 70% boundary-access
research, 20% regime validation, 10% consolidation and bounded closure. These are
priorities, not a preregistered protocol or new scientific results.

| Priority | Scope | Completion or stopping criterion |
|---|---|---|
| 1. Explain boundary access | One independently testable account of interior returns and boundary occupation. | Predict later occupation or drift on separate trajectories, beating persistence with the same permitted inputs. Stop a design that cannot distinguish explanations or only reconstructs its target from the target trajectory. |
| 2. Establish the regime | Audit the main cohort for board effects, transitions, censoring and selection bias; retain drifting cases as challenges. | State the finite-time regime covered and retain failures. Do not expand this into a general census or unlimited highway search. |
| 3. Close existing claims | Reconcile paper, notes and homepage; bound any RLRLLL proof-closure task before starting. | Separate observation, prediction, explanation and proof. Do not turn closure into a new proof programme. |

### Ordered sequence

1. **Use the consolidated evidence.** The [claim ledger and access guide](evidence-ledger.md)
   now separate observations, failed explanations, unresolved questions and next
   decisions, with pinned sources and a queryable JSON catalogue. Gate baseline
   eligibility remains unknown; its null does not reject all gate mechanisms.
   Consolidation is complete for this initial transport scope; choose the next
   test from those constraints rather than expanding the catalogue indefinitely.
2. **Choose one discriminating test.** The feasibility deliverable is two
   distinguishable explanations, an observable on which they disagree, and an
   instrument capable of resolving that disagreement. Use a small development
   cohort, reserve fresh starts and whole rule families where transfer is claimed,
   and freeze baselines and allowed inputs before outcomes. A fitted return-time
   exponent or an accounting identity alone does not meet this gate.
3. **Calibrate and run an excluded pilot.** Resolve precision, state support,
   censoring and cohort eligibility before scaling up. The earlier tail estimator
   failed calibration; detailed contexts rarely repeated; richer states did not
   independently predict mean returns. Stop or revise an inadequate design
   rather than adding features or trajectories without a discrimination argument.
4. **Run one confirmation study only if the gates pass.** Register the protocol,
   seeds, windows, compute budget and stopping criteria in its experiment README;
   maintain its lab and shareable notebooks. Report transitions, escapes, caps and
   non-reaching runs. End with a retain/revise/retire decision on the explanation.

Success for this phase is an independently successful explanation of a specific
transport feature, or a controlled rejection that narrows the possibilities.
Neither requires claiming that the cube-root exponent has been derived.

### Engineering support (not a research priority)

- **Tiled CPU grid backend (2026-10-23, done for the stepping runner):** `TURMITE_GRID=tiled` for `sweep_lean`
  (`src/tiled.rs`, `experiments/active/2026-10-tiled-grid-backend/`). Exact (all benchmark CSVs byte-identical to dense; oracle tests
  pass). Sparse tiles cut peak RSS to ~0.1x dense on compact/thin workloads and 12 MiB against 4.2 GiB on a 65536 board; packing
  helps little unless a large footprint has a big cache; LZ4 gave 0.19x dense on one structured rule only. Dense stays the default.
  Open follow-ups, each optional: tiled `probe` (two dense arrays remain), tile-grid offset for compact starts. No scientific
  classification changed and no sweep was run.

### Deferred this phase

- New lattices, dimensions and walker families, except controls needed by the
  selected test.
- Further prefix lookups without a specific transferable mechanism to test.
- Non-additive invariant mining until it has an explicit bridge to transport.
- A blanket fourth decade of the survivor census; validate the main cohort first.
- Extending formal proofs to more patterns; any existing RLRLLL closure work must
  have a bounded deliverable and budget.
- Other c-law, renewal, mutation and gate follow-ups below, unless selected through
  the feasibility gate above. Existing ownership and unopened-cohort safeguards remain.

These are scheduling decisions, not scientific exclusions. Pruning-index preflight
at `ac8d88dd8cb047b1a46fecdbade8b633b9165d59`: searched `return|kappa|boundary|phase|additive`
and read the sole entry, `NR-20261022-additive-laws-order-blind`, including its
membership predicate. Defer duplicate additive-law discrimination within its
recorded scope; it excludes neither transport mechanisms nor non-additive laws.
No transport-specific signature matched. Before an actual run, repeat the query
for its exact conditions and record the decision in its README and NOTEBOOK.

## Science: retained backlog (not an execution queue)

- **Seeded bootstrap that is not reproducible (found 2026-10-28, not fixed):**
  `experiments/archive/2026-10-kappa-matched-area/scripts/matched_area.py` gives different M2/M3 bootstrap intervals
  on every run, in the same environment, with the same input (sha256[:16] `e813c6f21f63421c`). Three runs at `2d8f189`
  gave M2 between-rule 95% intervals [1.096, 1.400], [1.088, 1.400], [1.086, 1.397]; the committed
  `results/matched_area.txt` (run at `797704a`, dirty tree) has [1.107, 1.403]. Point estimates (M1, the M2 slopes 1.271
  and 0.420, the M3 partial rho) reproduce exactly, and no M1-M3 verdict changes at this size of wobble (M2's
  within - between = -0.851 against a 0.3 bar). Likely cause, not yet confirmed by a fix: `seeds["rule"].unique()` and
  `group_by(...)` without `maintain_order=True` return rules in hash order, so the fixed `default_rng(20261014)` draws map
  to different rules each run (AGENTS.md rule 1: no hash-order dependence). Next: sort the rule list (or pass
  `maintain_order=True`), check two runs are byte-identical, then regenerate the result with a NOTEBOOK entry and
  report the interval shift. Wider audit: 46 scripts under `experiments/` and `research-outputs/` combine polars
  `unique()`/`group_by().agg()` with a seeded RNG (a crude grep, not a confirmed list), including this experiment's
  `matched_pairs.py` and `noise_floor.py`; any that feed RNG draws through an unordered result have the same flaw, and
  paper numbers built from them should be rechecked. (Before this check I had guessed a numpy version change; that
  guess was wrong.)

- **Wall or memory (done 2026-10-26, owner-requested, `experiments/active/2026-10-wall-vs-memory/`):** turn noise split by
  fresh/revisited cell. Randomising the first-departure turn disrupts compact growth in 6/6 core rules (condition means
  porous; 39/48 runs; dead end `NR-20261026-wall-vs-memory-no-wall-porous`, amended after review; not shown to be
  reflection specifically). The hybrid walker (forced R on fresh, memoryless interior) has a 0.73 at k = 24..30, 0.72 at
  k = 27..31, rotor 0.68: finite-window separation, asymptote unresolved. Follow-ups F-a..F-d registered in the README. Open: Q30 (where the edge fails between 10% and 100% fresh noise), Q31 (what memory
  adds: local-time discrepancy). Relevant to priority 1: boundary access depends on the fresh-ground turn, so a
  boundary-access explanation should say how that turn shapes returns.

- **Proof track (bounded closure only this phase; started 2026-10-20):** turn simulated regularities into checked macro-transitions
  (`notes/proof-track-2026-10-20.md`). First target: is the `RLRLLL` column sweeper `C(L) -> C(L+g)` for all heights?
  `experiments/archive/2026-10-rlrlll-macro-transition/`: P1-P5 held and the family is checked closed for all even m >= 2
  (cycle law 12m + (934, 1058, 898), |x|^2/t -> 3/4). Task C (2026-10-21): an independent second checker (stdlib Python, own ant, different proof architecture) reproduces every constant and agrees on 150 brute-force cycles; the two shift lemmas are Lean-checked for all n (core Lean, kernel decide, no sorry); the exact base-case criterion (real dump equals the ideal initial configuration on every cell the ideal ant visits) passes in 50 of 50 windows, but Task A's 3-row cone was too small (visited cells up to 7 rows outside it). Open: multi-cycle padding, entry seed, other escapes, a census-wide
  sweeper decider (`notes/proof-track-2026-10-20.md`, Next steps). L4 update (2026-10-22): end runs, composition for all n, bounded band inductions and the full single-cycle clocks/first arrival are now Lean-checked (`f90733c`, experiment README and `results/c3_l4_*.txt`). Multi-cycle padding and infinite-plane closure remain open; no Lean proof of persistence forever. Entry (2026-10-21): the cell-level family C(m,q) holds from step 12,676,237,591 (C(4,1), x = -1552), 184k steps before the edge crossing (rectangle exact, light-cone margin 3 rows chosen from observation, not derived); the clock formula extends exactly to m = -24 (x = -1510, column height 19); the wedge starts at height ~19, not zero; E1, A2, B2 failed as registered. Open: what at the blob NW corner makes the first column, why the formula holds at m < 2, deriving the cone margin. Single-core runs only; no conflict with the census. **Update 2026-10-23:** Task D ran (fast::run = plain loop at the base case); the Lean plane chain (`forever`, `forever_ideal`) closes multi-cycle padding for the ideal plane (the real board is not `Good`; plane-agreement lemma not proved); Task E explains the colour period 3 (one visit profile, visits 3,5,4); the other three "escapes" are two square spirals with exact clocks (RLLLRLRLLL from 2.635e10, p = 2; RLLLLRRL from ~1.47e10, p = 19 post hoc) and one blob, so the sweeper checker does not transfer and Stage 2 for the spirals is not started; a rectangle translated-cycler decider certifies 571/571 census highways (`experiments/archive/2026-10-highway-decider/`, `experiments/archive/2026-10-sweeper-generalisation/`, `notes/proof-track-2026-10-20.md` status update). Proof work stops here for this phase unless a bounded deliverable is registered.

- **Boundary return map (confirmation done 2026-10-21, `1998e7d`..`e1d6fc9`):** colour-shuffle intervention at boundary departures, 72/72 runs, 8252 departures. P1 (no compact state) falsified: the typical excursion is local (median r*/L 0.096 and 0.053, gamma 0.12). P2, P3, P4 met; P5 (time-weighted reach, registered after the pilot, so not blind) met: r*_t/L about 1.16, gamma_t about 1. So short loops have a compact local return map, but the interior time that sets E[T] and kappa depends on structure out to ~L. Cap censoring is 0.05% and does not drive it; shuffle-induced trapped replicas are not excluded. Open (all unregistered): single-cell flips on long excursions only (structure vs a few gate cells), a depth-resolved gate descriptor judged by this intervention, the same instrument on tethered/crystal rules. `experiments/archive/2026-10-boundary-return-map/README.md` ("Confirmation results"). (2026-10-22: the stray root `NOTEBOOK.md` held the 07:10-08:10 entries missing from the experiment notebook; merged there, root file removed.)

- **Single-cell gates (run 2026-10-22, registered, `3ec3cef`; committed `7e80168`):** 3 rules x 4 seeds, 213 ant departures, 617 matched pairs; exactness controls passed. Traffic-selected candidate cells show no resolved advantage over exposure-matched cells (time contrast -0.047 [-0.407, 0.290], reach 0.096 [-0.105, 0.301]); single cells often change outcomes, rule heterogeneity is large, 1.22% of interventions censored. Not a family-wide exclusion; the parent's sampler silently skips overflowing baselines, so eligibility is unknown. Open: other rules/more seeds, depth-resolved gate descriptor. `experiments/archive/2026-10-single-cell-gates/`.
- **Exact invariant mining (2026-10-22, `5df7de6`, `9bbfad4`, `849272d`):** additive modular miner (`src/invariants.rs`, `bin/invariants`; `cargo test --release --locked --test invariants` passes, run 2026-10-22 with a toolchain) and stage 2 (Smith normal form for all moduli, sublattice families, universal quotient; `experiments/_lib/lawmod.py`, README/NOTEBOOK/notebook.ipynb complete). Result: the law group of a rule is a function of `(n, ±D mod 4, trivial?)` only, so additive laws are blind to colour order (`NR-20261022-additive-laws-order-blind`); registered stage-2 P4 falsified (heading parity is tape-determined for even n); the two miners agree on 508 rules at m = 2, 4; no tile-free law is violated by the 582 confirmed highways. These are necessary constraints, not growth or highway certificates. **Open:** a non-additive family (pair potentials, ant potential reading the entered colour) with a null-functional quotient, Q21 in `notes/open-questions-hypotheses.md`; the full `cargo test --release --locked` suite result is in the stage-2 NOTEBOOK. Blog drafts (`blog/_drafts/`) are unpublished.

- **First-passage closure (done 2026-10-21):** P2 failed, P1/P3/P4 uninformative (stage V2; the tail fit failed calibration, so its theta and z are not reported as findings); boundary dwell is flat over L (delta ~ 0), so constant kappa is equivalent to E[T] tracking L (renewal identity, not a mechanism). Open: why E[T] tracks L; a calibrated tail estimator; deeper milestones; whether the large-B/S rules are highway onsets. `experiments/archive/2026-10-kappa-first-passage/` (README "Correction after review"), `notes/kappa-mechanisms-2026-10-15.md`.
  Proposed work list for it (added 2026-10-20; the calibration and the E[T]-versus-L measurement were done by the first-passage experiment, the rest is open; register predictions in the README before measuring):
  - *Instrument calibration (before trusting any exponent).* Known-answer walkers for theta and z: run the nested-depth and
    survival-tail estimator on the rotor walker (known t^(1/3) radius), a random walk on a growing cluster (theta = 1/2 at fixed
    geometry, negative control) and the mean-field walker (repo mean-field kappa 1.118); reproduce the probe's window-averaging
    convention. Synthetic renewal streams with a planted power-law tail and cutoff tau ~ L^z (known theta, z): check the fit
    recovers z(1-theta) and that censoring does not bias it (the tail-budget calibration covers geometric and mixture laws, not a
    scaling-form family). Censoring accounting: reuse the tail-budget sampler's lower/upper bounds for step-cap cutoffs.
  - *Closing the accounting loop.* Check kappa_inst = (A/P) f_d on the same runs (quasi-static geometry; if it fails, P/A drifts and
    the scaling argument has no footing). Cycle independence: autocorrelation of successive (D, T) pairs (stable means suffice, but
    strong correlation makes finite windows misleading).
  - *Escape mechanism.* Nested-depth crossing probabilities P(reach 2h before returning | reached h) for several h (constant ratio =
    scale-free tail; log ratio gives theta). Local-state ablation: condition on heading, colour phase, then larger neighbourhoods of
    recent history (plateau = local theory; continued gains = collective field organisation). Directional asymmetry via the
    return-gates instrument (its first stage was uninformative). Matched field edits: scramble the field structure the model says
    matters vs a same-size control; the model must predict sign and rough size of the change in kappa.
  - *Sign of kappa below uniform.* Residence-weight test: time-averaged occupation of boundary cells vs a uniform draw over the same
    cells at matched sizes. Moving-boundary coupling: a rotor or memoryless walker whose domain grows at the ant's measured rate;
    does kappa fall below uniform?
  - *Cross-checks.* Show the crossing model contains the failed explanations (dwell, crust depth, square loops) as special cases and
    predicts why they failed. Primary validation: the six-letter family hold-out (`experiments/archive/2026-10-kappa-prefix-family-holdout/`),
    fit on some families and beat the training mean on withheld ones. Scale dependence: is fitted z stable across area bands
    (32768, 131072, 524288) as in the tail-budget cohort (the c-law work suggests a size-dependent slope)?

- **Why does the c-law slope b fall with loop length, and what sets the intercept?** Registered Moore-lattice test (follow-up B, `experiments/archive/2026-10-lattice-c-law/README.md`): b = 0.775 at loop 4 (z = 8), 0.260 at loop 8; M-lin refuted, M-inv missed its own consistency clause by 0.005, so neither supported. b looks floor-like (~0.26-0.28 at l = 6 and 8), within-lattice doubling of l multiplies b by ~0.3. Intercept is lattice-set (1.3 for z = 3, 4; 2.4 for z = 6, 8), not loop-set. No mechanism; closing needs a derivation of N_b(l) and the intercept, then a registered test on another lattice.
- **Why is the hex lead fit so noisy, and what sets its intercept?** Follow-up A (2026-10-20, registered, `experiments/archive/2026-10-lattice-c-law/README.md`) removed the lacy outlier (beta < 0.8) and
  separated tail letter types: clean r-lead b = 0.262 [0.21, 0.31] (R^2 only 0.42), R-lead 0.876 (R^2 0.69), b_r/b_R = 0.30 [0.24, 0.37]; tail letter type adds ~nothing
  (R-lead CV gain +0.014, r-lead none). Intercept stays 2.4-2.8. Unexplained scatter remains; candidate features untested: second run length, letters 6-8.
- **Where does the lead slope of 1/c live, by colour? (follow-up, `experiments/archive/2026-10-lattice-c-law-colours/`, 2026-10-20).** The registered circulation
  decomposition failed (P1, P2, P6 failed; P3 passed on a flawed interior-contaminated estimator and is not counted). Post hoc: the slope lives in
  boundary reads at the circulating colours, ~0.95 per colour (hex R), 0.8 (square), 0.65 to 0.35 (tri), 0.7 to 0.5 (hex r); lag-ell ring returns carry them
  only on the square lattice; hex r fills ring centres (15% of lead-1 births). Shareable `notebook.ipynb` built and published (38 blog notebooks). Next: boundary-only episode segmentation, and what sets the per-colour survival plateau.
- **Origin of the c law constants a = 1.4, b = 0.68** (1/c = 1.36 + 0.70 lead). Candidate: loop-formation probability x 4 steps
  per revolution / births per chain. Also why letters 5-8 matter. `experiments/archive/2026-10-c-law-mechanism/README.md` (Stage 3,
  "Still open"), `experiments/archive/2026-10-c-law-mechanism/NOTEBOOK.md` (19:22 closing entry).
- **Local renewal mechanism for c:** rich lookup lacks pilot support (`0fa4db2`). Exact-rule finite colour-memory model then
  fails M1/M2 at r=4 and r=8 (`a878d5e`): nearby phase clocks plus uniform forgotten phases miss the cost/budget. An exact
  return bound ensures r=4 directly changes only >16-step phases. Long-budget loss can be hidden by more short loops.
  Read/write/pair closures also fail native return-budget and birth-wait tests (`94516e5`), rejecting physical-time stretching as a sufficient rescue. Next proposal: one coupled phase edit preserving two turns, with full memory thereafter; register branching/censoring and response horizons before measuring.
  Main cohort remains unopened. `experiments/active/2026-10-c-law-renewal/README.md`.
- **S-arm kappa drop (d = -0.198) is unexplained.** A total effect, not area-conditioned; confounded with flip direction
  (L>R +0.15, R>L -0.21, post hoc). Needs direction-balanced flips. `experiments/archive/2026-10-c-law-mechanism/README.md` (Stage 4
  results), `experiments/archive/2026-10-kappa-leadrun-fresh/README.md` (Part B addendum, Proposal 1).
- **Does lead have any direct effect on kappa?** Current bound |b| < ~0.06 per step given ln c, one cohort, one window,
  survivor-selected. A tighter test needs a mediator-free kappa (late windows only) or a second cohort.
  `experiments/archive/2026-10-c-law-mechanism/results/stage4_analysis.txt`, `notes/open-questions-hypotheses.md` (Reconciliation).
- **Mixed-turn loops (period 6/8) and opening-transient loops** were not tested; the square-loop failure only covers same-turn
  2x2 loops. (CI on the 8% figure done 2026-10-20: 7.6% [3.2, 12.3] at lead 6.)
  `experiments/archive/2026-10-kappa-square-loop/NOTEBOOK.md` (22:58 end-of-session entry), `experiments/archive/2026-10-kappa-square-loop/README.md` (Results).
- **Blob-regime boundary** of the c law between sparse-background density 0.2 and 0.7 (kept fraction 0-2% at density 1).
  `experiments/archive/2026-10-c-law-mechanism/README.md` (Stage 3 results).
- **Where the ant's boundary deficit lives (2026-10-20, `experiments/archive/2026-10-kappa-exposure-classes/`, Turmite Research Agent):** registered
  H-exposed (P3) and P4 FAILED; P0-P2b held (convention-free rho: ant 0.874, rotor 1.80, rw 1.31; kappa/1.105 matches rho rule by rule to 3.6%).
  Post hoc: the ant-specific shortfall is returns to flat-edge cells (rho_1^ret 0.59 vs rotor 1.14). Candidate observable for the priority-1
  discriminating test, not scheduled: an age-resolved flat-edge follow-up must pass that feasibility gate and record edge-cell colour phase
  (see `experiments/archive/2026-10-hidden-phase-return/`); adapted 2026-10-25 at merge to the narrowed plan. Side question: 3/256 patched starts of two stationary rules became board fillers within 2^26 steps.
  Review 2026-10-25 (README addendum): P4 is unscored, not failed; P2b is a proxy to about +-7-9%. The flat-edge reading is
  mostly composition and is not ant-specific: the ant/rotor ratio is 0.51 flat vs 0.55 exposed, and about half the gap is births. A follow-up needs
  fixed-weight criteria. Dead end `NR-20261025-kappa-exposure-classes-exposed-edge`; ledger BO-04 (mf kappa_unif 1.110 at 2^26).
- **kappa/kappa_unif distribution, location (open):** why the median is 0.81 x kappa_unif (below every walker reference).
  `experiments/archive/2026-10-kappa-uniform-baseline/results/census_spread.txt`, `notes/open-questions-hypotheses.md`.
- **kappa spread, remainder (open):** budgeted 2026-10-20 (post hoc, `experiments/archive/2026-10-kappa-spread-budget/`): about 0.15 start
  noise, 0.47-0.54 prefix-predictable, 0.31-0.38 rule-determined but unexplained. A registered held-out comparison
  (`experiments/archive/2026-10-kappa-spread-features/`, F1-F4 held) found the predictable part is in the first 8 letters (R^2 0.62),
  not the last 8 (-0.11) or composition (+0.08; adds +0.008 to the prefix). A second registered test
  (`experiments/archive/2026-10-kappa-prefix-runs/`, H1-H3 FAILED, H4 held) found the lead alone has R^2 ~0 unconditionally and the signal
  accumulates over the first four runs (0.25, 0.34, 0.48 vs 0.62 for 8 letters). A registered per-position ablation
  (`experiments/archive/2026-10-kappa-prefix-ablation/`, A3 FAILED) found the information is not front-loaded: loss from ablating
  position 5 is 0.40, positions 2-7 each 0.2-0.4, position 8 0.07. A registered additive comparison
  (`experiments/archive/2026-10-kappa-prefix-additive/`, B2 FAILED) found additive letter-by-position 0.11, plus pairwise 0.35, vs 0.62 for
  the lookup: the signal needs higher-order interactions. A registered family hold-out
  (`experiments/archive/2026-10-kappa-prefix-family-holdout/`, D2 and D3 FAILED) then found every model falls below the training mean on
  held-out 6-letter prefix families (lookup 0.59 -> -0.16; pairwise 0.30 -> -0.69): the signal is family membership, not a
  transferable letter-level rule. Still open: a family random effect plus within-family letter structure, other family
  granularities (4, 8 letters), and what the unexplained third is (middle letters, dynamics).
- **Square-ring fillers, open follow-ups (2026-10-25; experiment done, record in its README):** the board fillers' edge is a crawler of 2x2 square loops, proved for every k; exact clock
  `8(k+1) swing + b`, board exits predicted to the step, corner needs `T(2k+2) = R`; the ring footprint is 220/304 census builders (218 with this family's table), but the registered
  footprint-implies-family test failed (other integer-cost crawler families exist). Open: corner lemma, the reversed family `R^(k+1) L R^k`,
  why 40% of the right-turn rules never find the ring (Q27, Q29). Use the `Pi(k)` predicate (`experiments/archive/2026-10-square-ring-fillers/scripts/ring.py`)
  to exclude ring rules from transport cohorts rather than a steps-per-cell threshold. `experiments/archive/2026-10-square-ring-fillers/`.
- **Late-highway counts corrected (final 2026-10-22):** 25 of the 54 reported late highways are board fillers (`R^k L R R...`, escape at ~(k+1)·2^31 on the 32768 board, x4 per board doubling) and `RLLLRLRRR` is a ray truncated by the board; the other 28 all reproduce on a 65536 board (B2 held, 26/26 rechecks). Genuine yields: 16/807 = 1.98% in (1e9,1e10] (was 4.7%), 12/732 = 1.64% in (1e10,1e11] (was 2.2%). With (1e8,1e9] at 1.4%, the per-decade rate is consistent with flat ~2%: the "thinning tail" is withdrawn. Open: apply the board-independence check to the 1e8/1e9 census; a fourth decade on the 702 survivors (Q19); whether the 702 include bounded rules (RLLLLLR is 42x42 at 1e11). `experiments/archive/2026-10-late-highway-board-check/`, `notes/frontier-2026-10-13-results.md` (Correction 2026-10-21).
- **Highway preconditions (done 2026-10-21):** the grid the future depends on (`D(tau)`, nonzero cells read again) collapses from 10^3-10^5 cells to the highway's own trail ~0.1 period before onset; the pre-onset seed is that trail plus a median 3 cells (406 independent events, transplant-verified 566/566; a sufficient set, not shown minimal), and ~0.25 period later the ant heads away from its territory (402/406). No seed is shared across unrelated rules (P4 held only within prefix families); P5 (seed excess predicts onset) failed. Post hoc: onset grows with highway size (self-overlap rho 0.45, speed -0.54), ~0.018 decades per cell. Open: knock-out of the "+3" cells; out-of-sample test on the 54 late highways. `experiments/archive/2026-10-highway-preconditions/`.
- **Late-highway tail / unresolved rules** and why `RLRLLL` switches to a period-3 column sweeper (trigger unknown).
  `experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/`, `experiments/archive/2026-10-g1-ribbon-breakout/README.md`,
  `experiments/archive/2026-10-census-sweeps/results/unresolved_le10.txt`.
- **Paper figures 1-5 are built** (2026-10-20: `fig:walker-map`, `fig:edge-gap`, `fig:layers`, `fig:prefix`; late-switch earlier). `rebuild_figures.py`
  confirmed 2026-10-20 to regenerate all figures and `main.pdf` cleanly. Proposals 6-8 remain unattempted.
  `notes/paper-figure-proposals-2026-10-16.md`, `notes/handover-paper-figures-2026-10-17.md` (stale for item 4).

## Uncommitted work in progress (do not lose)

- As of 2026-10-22 the main working tree is clean (everything committed on local `main`, not pushed). Only worktree-held gitignored data remains at risk (see housekeeping).
- **c-law renewal work has an owning session (new runs deferred under the sequence above):** instrument and oracle tests committed (`ccbd9cd`), release suite passes,
  finite-memory model/clock (`c826721`) and failures (`a878d5e`) committed. All own jobs are terminal. Do not replace its pilot
  families, relaunch completed pilots, or open main outcomes before the next mechanism is registered.
- The n-rotor reference, uniform-baseline notebook edit and blog index/post listed here earlier are committed (`18b79d7`,
  `3117e1b`); `main` equals `origin/main` (`bf4ca54`) as of 2026-10-20 00:42.
- **rulepat, branch `claude/rule-pattern-experiment-aa95e3`**: committed 2026-10-20 as `275d52b` and merged into local `main`
  on 2026-10-20 at the user's request (reader guide added, covering only the early README steps). Still open: its gitignored
  `dumps/` (192 MB) and `scratch/` (3 MB) exist only in the worktree, so archive them before removing it; its README
  census steps (C1-C4) were not reviewed here.

## Repository housekeeping

- **Experiment folders reorganised (2026-10-28):** `experiments/YYYY-MM-DD-slug/` became
  `experiments/{active,archive,proposed}/YYYY-MM-slug/`; layout rules, the full old -> new table and the move
  procedure are in `experiments/README.md`, the map in `experiments/_migration/2026-10-28-buckets.tsv`. Gitignored
  `dumps*/`, `knock*/`, `scratch/` and `synth/` in other checkouts and worktrees stay under the old folder names
  until moved with `uv run --frozen experiments/_migration/relocate.py experiments/_migration/2026-10-28-buckets.tsv --local-only`
  (run it there after merging; it refuses to overwrite). Paths inside those worktrees, below, keep the old names because that is where the data is.

- **Jupyter**: `ipykernel`, `nbformat`, `nbclient` added to `pyproject.toml`/`uv.lock` (`7df6d35`). The leadrun-fresh notebook's Proposal 2 bounds are not in it (rebuild with `scripts/build_notebook.py` if wanted).
- **Blog index refreshed (done 2026-10-22):** c-law, lattice, lead-slope-by-colour and kappa-spread highlights and the null-result post link are on `blog/index.html`. The experiment pages were
  re-rendered 2026-10-20 (from a worktree under WSL set `GIT_DIR=/mnt/f/Code/turmite/.git/worktrees/<name>` and `GIT_WORK_TREE=$PWD`).
- **Stale worktrees and branches** (nothing deleted). On 2026-10-20 tracked work was committed on their own branches
  (`agent-a810708e829d8af34` as `4cb0261`, `g1-builder-structure` as `b985636`, rulepat as `275d52b`), but **gitignored data
  exists only in the worktrees and is lost on removal** (checked with `git status --ignored`): `g1-builder-structure/dumps/`
  73 MB (the only raw input for `g1_wake_extract.py`; regenerating takes hours), `rule-pattern-experiment-aa95e3/experiments/2026-10-14-rulepat/dumps/`
  192 MB and `scratch/` 3 MB (plus `target/`, rebuildable), `agent-a810708e829d8af34/experiments/2026-10-16-gpu-probe-port/scratch/` 19 MB.
  Archive what matters before any removal. `g1-builder-structure` is also the only home of `examples/builder_dump.rs` and
  `notes/g1-builder-structure-2026-10-14.md` (handover item 3). Deletion needs the user's go-ahead:
  - `.claude/worktrees/agent-a810708e829d8af34` and branch `backup/pre-census-split`: same commits; the unique `39df9f2` content is in
    `main`. Its uncommitted GPU probe port (`src/gpu/probe.rs`, `experiments/2026-10-16-gpu-probe-port/`) is an earlier attempt at what
    `main` has as `gpu_probe`; checked 2026-10-20: the two `results/` dirs differ (the port has `full_L2400*`, `cpu_full.*`, `block_sweep_*`; `gpu-probe` has the bench files), so keep the port's results before discarding.
  - `.claude/worktrees/g1-builder-structure`: old `data/` layout; content appears superseded by `main`. Checked 2026-10-20: no
    `TODO(G1)` remains in `main.typ`. Still archive `dumps/` (73 MB) first.
  - `.claude/worktrees/paper-figure-proposals` (locked): merged into local `main` on 2026-10-20 (user-approved local merge, not
    pushed; `main.typ` and `rebuild_figures.py` auto-merged, `ACTIVE.md` and `main.pdf` resolved by hand / recompile). Checked 2026-10-20: no commits
    beyond `main`; the worktree can be removed when finished.

## Closed (for reference, do not reopen without new grounds)

- **Paper follow-up revision (2026-10-20):** c law, corrected uniform reference,
  conditioning check and negative-test statuses incorporated; PDF rebuilt and
  visually checked, release tests passed. Recipe and output hash in the paper README.

- `experiments/archive/2026-10-kappa-square-loop/`: H-loop dead at this scale (P2 failed).
- `experiments/archive/2026-10-kappa-loop-surgery/`: closed unrun on 2026-10-19 (gate failed; premise further weakened by the collider result).


## Completed excluded pilot: hidden phase (2026-10-23)

[Hidden-phase return](../experiments/archive/2026-10-hidden-phase-return/README.md)
tested one-time interior shuffles that preserve every cell's next turn and
per-depth-bin colour counts. All 640 k=1 paths/return tuples changed (near-certain
for ~10^4 relabelled cells; full-word shams matched). 17/24 start/area groups failed minimum
long-episode support, so P1 is untestable under the frozen rules and its ratios
(two of six below 0.5) are descriptive. All baseline
eligibility was counted; no censoring occurred. Stop at this pilot. Evidence:
`1c0d631a1745f3bf12ab9e7a1d87d9d0bb9b6974`. No new confirmation run or family
exclusion is justified. Next-turn maps alone are insufficient on these edited
fields; a predictor of natural occupation still needs a separate-trajectory
comparison against persistence. The older gate experiment's eligibility warning
is not repaired retroactively by this different cohort.
