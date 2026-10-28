# Claim ledger: boundary access and regime changes

Generated from human-authored `claims.json` by `scripts/ledger.py render`.
Reviewed 2026-10-28T15:50:00+13:00; all evidence pinned at `581f20329d0a92f595dfe858817c5b739f656b4a`.
No new measurements. Verdicts apply to the stated test and scope, not entire mechanisms.

## Compact decision view

| ID / verdict | Supported observation or test outcome | Failed explanation / inference | Unresolved question | Next decision |
|---|---|---|---|---|
| [BO-01](#bo-01) / accounting-only | The growth-factor decomposition and renewal ratio account for growth/occupation. They do not independently explain why occupation stabilizes. | Reconstructing the exponent or kappa from factors or return budgets on the same trajectory validates a mechanism. | What independently predicts the level and drift of boundary access? | Require a frozen out-of-sample prediction beating persistence with the same permitted inputs; score causal intervention separately. |
| [BO-02](#bo-02) / supported | Uniform instantaneous sampling gives octave-probe kappa about 1.11, not 1. Mean-field control measured 1.118 with between-seed SD 0.009; formula using measured exponents gives 1.107. | Treating kappa=1 as the uniform reference for growing octave windows. | Why do the tested ants spend less boundary time than the appropriate uniform reference? | Use the matching window and geometry baseline before interpreting any occupation deficit. |
| [BO-03](#bo-03) / failed | Prefix lookup predicts within represented families, but whole six-letter-family holdout gives strict R2 -0.162 for P8, versus +0.591 in random CV. Tested additive and pairwise models also fall below the training mean. | The tested prefix models learn a transport rule that transfers to unseen prefix families. | Can an independently motivated transport feature transfer beyond family membership? | Reserve whole families wherever transfer is claimed; do not extend lookup features without a discriminating mechanism. |
| [BO-04](#bo-04) / supported | A seed-disjoint, longer-horizon replication of the BO-02 control gives the same uniform reference. Eight mean-field seeds 1..8 run to 2^26 steps on board 8192 give a window-mean octave-probe kappa over k=17..26 of 1.110 (between-seed SD 0.007, range 1.102-1.120), against BO-02's 1.118 (SD 0.009) and the formula value of 1.107. | That the ~1.11 uniform reference in BO-02 is specific to its seeds or to the 2^23-step horizon. | Is the 0.008 difference from BO-02 a horizon or window effect (k=17..26 against k=12..22) or seed noise? | Keep kappa_unif at about 1.105-1.11 for square-grid, end-reference octave windows in this growth regime. Recompute it for any other exponent, window convention or lattice. |
| [RD-01](#rd-01) / mixed | Tail-budget T1 fails its both-band criterion. T2 meets its absolute accuracy threshold (median relative error 0.123) but persistence is better (0.072). | A passing absolute forecast threshold establishes a useful explanation of return dynamics. | What sets mean interior return time beyond what persistence already predicts? | Carry the stronger persistence comparator into the next design and freeze its allowed inputs. |
| [RD-02](#rd-02) / failed | First-passage P2 fails: M2 median relative error 1.07; mean absolute error 0.0372 versus 0.0277 for band-1 persistence. Boundary dwell has descriptive median slope -0.0007 over L=A/P. | Richer fitted state partitions independently close the mean return budget; E[T] tracking L itself explains constant kappa. | Why does mean interior duration track L where boundary dwell is flat and kappa stable? | Separate in-sample identities from predictive tests; compare against geometry-adjusted persistence only if geometry is equally available to all models. |
| [RD-03](#rd-03) / uninformative | First-passage V2 P1 tail test fails calibration/identifiability; P3 has no rule-conditional input; P4 has median supported context share 0.005 against required 0.30. | These tests establish tail exponents, prove a local state sufficient, or reject all local closures. | Can an instrument identify return structure at the available sample sizes? | Require known-answer calibration and context support in an excluded pilot before a new confirmation test. |
| [RD-04](#rd-04) / supported | Population-weighted shuffle reach is local (median r*/L 0.096,0.053); time-weighted reach is much larger (1.16 in both bands). P1 no-compact-state prediction fails; pilot-informed P5 meets its criterion. | A compact description of typical short excursions necessarily captures the interior time budget. | Which distant field structure controls long durations: distributed organization, sparse sensitive cells, or another feature? | Seek competing predictions about time-weighted outcomes; do not treat shuffle reach as a Markov sufficiency proof or single-cell result. |
| [RD-05](#rd-05) / uninformative | Traffic-selected single cells show no resolved advantage over exposure-matched controls: time contrast -0.047 [-0.407,0.290], reach 0.096 [-0.105,0.301]. Exactness controls pass. | This null establishes diffuse control or excludes sparse gates in general. | Would another independently justified gate descriptor discriminate, once baseline eligibility is known? | Count all skipped/overflowing baselines and report eligibility before designing another gate test; do not simply enlarge this selected sample. |
| [RD-06](#rd-06) / failed | The frozen number-weighted excursion-duration collapse Score never preferred tau/L^2 on a compact diffusive calibrator. Eden-style growth (median A/P^2 0.065) gave S (Score L 0.102 vs L^2 0.161); internal DLA (0.071) gave inconclusive (0.067 vs 0.077). Mean-field still preferred L. The gate failed and the ant cohort was not run. | A number-weighted survival-collapse Score with margin 0.75 can certify diffusive (tau/L^2) boundary excursions, so its S or inconclusive readout on ants would show the absence of diffusion. | Can a separately registered tail-restricted or step-weighted collapse statistic prefer L^2 on IDLA while mean-field still prefers L? | Register and calibrate a different observable on these walkers before any ant data; do not retune q1, margin, u-grid or mask, and do not run the reserved cohort under this Score. |
| [RG-01](#rg-01) / unresolved | First-passage cohort has 734 complete runs, 32 caps and two board escapes out of 768. Large occupation deviations were not individually diagnosed; they may include regime transitions. | Every large occupation deviation is ordinary drift within the same blob regime. | Which trajectories remain in the regime the transport model is meant to explain? | Audit the main cohort for transitions, board contact and censoring; keep non-reaching runs in denominators and drifting rules as challenges. |
| [RG-02](#rg-02) / supported | Final board audit separates 54 reported late highways into 25 fillers, one truncated ray and 28 board-rechecked cases. All 26 scheduled rechecks finished; there are no seven pending cases in the final ledger. | Finite-board escape with a periodic tail is sufficient for a highway classification; uncorrected late counts establish a thinning tail. | How much apparent regime change in the main transport cohort is a boundary artefact? | Use the final corrected counts and board-independent onset checks; do not launch a blanket extra census decade. |
| [RG-03](#rg-03) / supported | Rotor calibration in the ant window gives width exponent 0.326 (seed SD 0.013) and area 0.687 versus asymptotic 2/3; finite-window bias matters. | The estimator is unbiased, so a tight finite-window census proves a universal asymptotic exponent and complete taxonomy. | Which differences persist beyond finite-window bias and changing regimes? | State measured windows, seeds, calibration and classification limits beside every exponent claim. |

## Scope and evidence

Always retrieve these limits with the compact row. Source READMEs/notes include
recipes, manifests and corrections; linked data are retained measurements, not reruns.

### BO-01

**boundary-occupation · identity · accounting-only**

Scope: Probe boundary = visited cells with an unvisited four-neighbour, including holes; f=B/S, probe kappa=f/(P_end/A_end). Renewal means need representative cycles and finite-window fragment accounting.

Limits: Conditional cube-root scaling additionally assumes geometry and stable factors. The small-f approximation f~E[D]/E[T] can fail at large f.

Evidence: [accounting](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/notes/accounting-identity-response-2026-10-16.md); [passage](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/README.md).

### BO-02

**boundary-occupation · calibration · supported**

Scope: Eight mean-field seeds 2026101601..08; 2^23 steps; fits k=12..22; square-grid control.

Limits: A calibrated reference is not a mechanism. Do not transfer this numeric baseline unchanged to other growth exponents or window conventions.

Evidence: [uniform](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-uniform-baseline/README.md); [uniform_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-uniform-baseline/results/analysis.txt).

### BO-03

**boundary-occupation · prediction · failed**

Scope: 2185 selected stationary census rules; 43 families; eight folds, seed 20261020; 2000 rule bootstraps. P8 intervals: random [0.468,0.691], grouped [-0.230,-0.107].

Limits: Uneven families, selected stationary cohort and untuned ridge. Failure of these models does not exclude all letter-level structure; rule bootstrap is not between-family uncertainty.

Evidence: [prefix](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-prefix-family-holdout/README.md); [prefix_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-prefix-family-holdout/results/holdout.json); [accounting](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/notes/accounting-identity-response-2026-10-16.md).

### BO-04

**boundary-occupation · calibration · supported**

Scope: Mean-field walker mf:1..8 (uniform over the visited set by construction); 2^26 steps; board 8192; octave windows k=17..26 (t in (2^16, 2^26]); square grid; instrument examples/kappa_exposure_classes.rs, whose windows were checked against probe::probe_walker.

Limits: Post hoc and unregistered: these are the calibration runs of the exposure-class experiment, summarised in its 2026-10-25 review. It uses the same mean-field algorithm (reimplemented in the exposure instrument) and the same probe definitions as BO-02, so it does not test the definitional choice. Growth exponents were not refitted, so the formula value was not recomputed for these windows. The difference of about 2 combined standard errors is not interpreted. This is a calibration, not a mechanism.

Evidence: [exposure](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-exposure-classes/README.md); [exposure_review](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-exposure-classes/results/review.txt); [exposure_review_script](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-exposure-classes/scripts/posthoc_review.py); [uniform](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-uniform-baseline/README.md); [uniform_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-uniform-baseline/results/analysis.txt).

### RD-01

**return-dynamics · prediction · mixed**

Scope: 44 rules, 32 starts each (16 predictor/16 outcome), seeds 2026101801..1832; area bands starting 32768,131072,524288; cap 2^32; 1408/1408 runs.

Limits: T1 lower interval bound is -0.018 in band 0 despite positive point gain; analysis script written after run. Empirical binned mean used because parametric calibration failed. Decomposition is accounting, not intervention.

Evidence: [tail](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-tail-budget/README.md); [tail_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-tail-budget/results/confirm-v1.analysis.json).

### RD-02

**return-dynamics · prediction · failed**

Scope: 48 rules/12 families, eight kernel seeds 202610208001..8 and eight outcome seeds 202610209001..8; three area bands 32768,131072,524288; 46 eligible rules. Paired improvement interval [-0.0234,+0.0009].

Limits: Depth-64 component dominates in 35/46 rules; locality not tested by P2. Geometry-adjusted comparator is post hoc and uses outcome geometry. High-f rules invalidate the small-f identity approximation; dwell slope is descriptive, not a universal law.

Evidence: [passage](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/README.md); [passage_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/results/confirm_analysis_skipP3.json); [dwell_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/results/describe.json).

### RD-03

**return-dynamics · instrument · uninformative**

Scope: Same first-passage cohort; P4 trains on kernel seeds 8001..8004 and holds out 8005..8008 (full prefix 20261020); tail identifiability 33/46 eligible rules.

Limits: Cutoff log-bias reaches 0.238 versus <0.2 gate; theta coverage 0.893 versus >=0.90. Do not publish fitted theta/z as findings. Context folding did not cause low support; support is heterogeneous.

Evidence: [passage](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/README.md); [tail_calibration](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/results/calibration_c6.json); [context_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/results/p4_test.json).

### RD-04

**return-dynamics · intervention · supported**

Scope: 36 confirmation rules x seeds 202610208001..2, 72 runs, 8252 departures; area bands 2^15 and 2^17; depth-class colour shuffles, eight replicas, duration cap 2^22.

Limits: P5 was informed by pilot; time-weighted thresholds unreached in 9/36 and 13/36 rule-bands. Gamma_t uses only 22 finite pairs. Shuffle changes colours and spatial structure together; successive-return memory untested. Deep/shallow split conditions on outcome.

Evidence: [return_map](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-boundary-return-map/README.md); [return_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-boundary-return-map/results/confirm_analysis.json).

### RD-05

**return-dynamics · intervention · uninformative**

Scope: Three rules x four seeds 202610208001..004; 213 ant departures, 617 matched pairs; sampled T>=512, two area bands 32768,131072; cap 1048576. Hierarchical rule/seed bootstrap 10000 draws, seed 2026102201.

Limits: Only three rule clusters. Baseline undo-log overflow silently skipped: full eligibility unknown. Intervention censoring 15/1234 (1.22%) limits claims to capped time/path reach. Traffic ranking does not define all possible gates.

Evidence: [gate_design](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-single-cell-gates/README.md); [gates](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-single-cell-gates/NOTEBOOK.md); [gate_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-single-cell-gates/results/analysis.json).

### RD-06

**return-dynamics · instrument · failed**

Scope: Revision 2 calibration only: eden (q1 = 1/64) and idla, seeds 2026102841..44, board 8192, k=16..24, 36 windows each; same Score, mask and compactness rule as stage 1 and Revision 1. Earlier failures: free RW (L never grew) and reflecting cup (porous).

Limits: Four seeds; IDLA L range only four-fold. Walker code was committed with the results rather than before measuring (definitions frozen in registration 900f25f). Post hoc plots suggest the IDLA tail collapses in tau/L^2; untested. Says nothing about ant excursions.

Evidence: [excursion](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/active/2026-10-boundary-excursion-durations/README.md); [excursion_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/active/2026-10-boundary-excursion-durations/results/rev2_analysis.json); [excursion_pruning](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/notes/pruning-index/entries/NR-20261028-excursion-score-compact-d-calibrators.md).

### RG-01

**regime-changes · observation · unresolved**

Scope: First-passage 48-rule cohort at 2^32 cap and board 8192; caps concentrated in RLRLLLL and RRRRRRLLLLLL; two escapes in RRRRRRRLR outcome runs.

Limits: No new transition detector or classification attack here. RLLLRRRLL and RLLRRLLLLLLL are inspection candidates, not diagnosed highway onsets. Stationary selection is not an explanation of stationarity.

Evidence: [passage](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/README.md); [passage_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/results/confirm_analysis_skipP3.json); [dwell_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-kappa-first-passage/results/describe.json).

### RG-02

**regime-changes · instrument · supported**

Scope: Blank starts, late reported onsets (1e9,1e11], recheck board 65536. Corrected yields: 16/807 (1.98%) and 12/732 (1.64%).

Limits: Finite board agreement does not prove infinite-time persistence or all-start classification; this audit supplies no falsification-harness verdict. Three decades with few events cannot exclude slow decline. Earlier 1e8/1e9 cohorts were not all subjected to the second-board check.

Evidence: [boards](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-late-highway-board-check/README.md); [board_data](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/experiments/archive/2026-10-late-highway-board-check/results/classify.txt).

### RG-03

**regime-changes · calibration · supported**

Scope: 64 rotor seeds to 2^27; fitted windows ending 2^20..2^26. Patched-ant calibration separately uses 40 rules x 12 random 5x5 patches.

Limits: Calibration on this walker/window does not license a universal bias correction. A patched start is not an infinite random background. No universal ant exponent established by this audit.

Evidence: [calibration](https://github.com/timClicks/turmite-autoresearch/blob/581f20329d0a92f595dfe858817c5b739f656b4a/notes/calibration.md).
