**Current status (2026-10-15): instrument calibration and feasibility pilot complete; scientific confirmation NOT RUN. See [results report](results/REPORT.md). The initial scaffold below is historical.**

# Does field maturation explain kappa and its stationarity?

Status: **draft research plan; no instrument implemented or measurement run**.
Created 2026-10-15 22:54 +13:00, base `b3a0f762ac2230b5df92188206a4d3a1081897be`
(dirty tree). [Mechanism note](../../../notes/kappa-mechanisms-2026-10-15.md).

## Question and mechanism

Does a rule affect return hazards through the age and visit history of its
field? Equal area does not control elapsed time or completed colour cycles.
This could explain both prefix predictability and why kappa drifts in some
rules. It is a competing account of the prefix lead, not a generic search
through many field features.

## Draft design and predictions (freeze before ant outcomes)

1. Select 48 rules, half stationary and half drifting according to a frozen
   *existing* early-window definition, balancing length and prefix support.
   Freeze an explicit list; if strata lack support, report feasibility failure
   instead of selecting on new outcomes. Use 16 fresh starts per rule and
   four separate pilot starts; cap 2^30 steps. Candidate bands begin at
   32768, 131072 and 524288, width A/16. Report all nonattainment by stratum.
2. Track cell discovery time, exact visit count, and colour phase; derive age
   at each observation and completed cycle count floor(visits/n), adjusted
   for explicitly recorded initial patch colours. Census features must be
   cell-weighted; exposure features step-weighted. Keep them distinct to
   avoid presenting occupation-biased age as independent field structure.
3. Predeclare three primary features in the depth<=4 rim: fraction of cells
   with fewer than n visits, median log(1+cell age), and dispersion of completed
   cycle counts. Depth bands, normalization and sampling cadence must be
   frozen after calibration. Analyze conditional excursion-entry and return
   hazards; retain heading and phase as confounders rather than treating
   colour alone as an autonomous Markov state.
4. Fit models on predictor seeds and evaluate on disjoint outcome seeds with
   grouped rule folds: size/shape/history baseline; baseline+prefix;
   baseline+age; baseline+prefix+age. Baseline includes log elapsed time,
   area, P/A, shape and earlier growth, all measured in predictor trajectories.
   Draft A1: age adds >=0.10 held-out R2 for log kappa, with rule-bootstrap
   lower bound >0 at both smaller bands. A2: adding age halves the incremental
   prefix gain. Attenuation is conditional prediction, not causal mediation.
5. Freeze the smaller-band hazard model and forecast kappa drift to the third
   band. Draft A3: drift-sign accuracy >=70% and improvement over no-drift
   squared error >=10%, interval lower bound >0, across held-out rules.
   Repeat in each predeclared stratum. A stationary-only success cannot explain
   the drifting population. Earlier target kappa is allowed only in a clearly
   labelled forecast baseline, never as an independent mechanistic predictor.

## Controls, calibration and interpretation

Reference-test discovery/visit counts, including nonzero initial patches,
and exact phase progression. On synthetic age-labelled chains with planted
age-dependent hazards, recover the planted effect; permuted age labels
within geometry strata should remove it. Rotor and random walk measure
feature drift across known different regimes, not a presumed shared age law.

Use matched rule folds for all models, training-only feature normalization,
2000 rule bootstraps and between-seed sd. Draft coverage gate: >=80% of each
stratum reaches both primary bands with >=6 seeds per role; quantify split-
seed feature reliability before inference. Include training uncertainty in
resampling when feasible. A gate failure prevents a confident null.
If age predicts but does not weaken prefix effects, both can matter; if only
elapsed time predicts, the proposed field feature mechanism has failed.

## Implementation and next action

Extend the fixed-area sampler with observation-only age counters in
`kappa_field_age_*`. Profile memory per cell before deciding board size;
overflow must fail loudly. Start with small reference trajectories and freeze
the full manifest before scientific runs. No rejuvenation intervention is
planned yet: resetting metadata changes no dynamics, while resetting actual
colours changes more than age. A physical intervention needs its own design.

See [PLAN.md](PLAN.md), [SCHEMA.md](SCHEMA.md), and [HANDOFF.md](HANDOFF.md).
Results: **NOT RUN**. No scientific test has passed or failed in this scaffold.

## Scaffold verification — 2026-10-15 22:59 +13:00

Preflight and the planning notebook executed successfully under uv/WSL; local
Markdown links resolve. The shared workspace passed cargo test --release.
No new instrument or scientific prediction was tested. Commands are in HANDOFF.md;
verification scope and the local test-log path are recorded in NOTEBOOK.md.


## Instrument continuation — 2026-10-15 (NZDT)

The scaffold above is historical. Observation-only instrumentation and reference
checks are now implemented in `src/field_age.rs`, with example runners
`kappa_tail_budget_sampler` and `kappa_field_age_sampler`. The immediate scope
specified in HANDOFF is instrument calibration and a prospective feasibility
registration; scientific confirmation remains unregistered and NOT RUN.

Small four-rule profiles completed before the full pilot was registered.
`results/pilot-v2.manifest.json` was frozen before any three-band pilot outcome:
44 supported rules x four fresh pilot starts, bands [32768,34816),
[131072,139264), [524288,557056), cap 2^30, grid 4096, four workers. Full rules,
explicit seed lists, input/source hashes and commands are in the manifest.
This is a feasibility registration, not a scientific-confirmation registration.

The age draft's 48-rule matching gate failed before new ant simulation: only
22 stationary/drifting pairs exactly matched on length and three-letter prefix
are supported by the existing rule pool. That failure is preserved; the 44
supported rules are used for instrument feasibility only. The tail cohort uses
the existing 44-rule fixed-area cohort. No pilot seed is eligible for confirmation.

Calibration outputs are in results/calibration.json. The actual tail accountant
is checked on geometric, mixture and serially correlated renewal streams; the
age frequency estimator is checked on planted and permuted exogenous labels.
Exact metadata/rim/phase tests use the independent sparse ant oracle. Rotor and
random walk are dynamical bookkeeping controls. Neither a parametric survival
fit nor a log-kappa/drift prediction estimator has been calibrated or fit yet.

The original PLAN's mid-trajectory checkpoint requirement is not implemented.
This pilot uses source/config-hashed finished-trajectory markers; sampled
one-versus-six-thread replay and finished-run resume pass (results/determinism.json).
This deviation is recorded and must be resolved before confirmation readiness.
The first full manifest (pilot-v1) was rejected before simulation because another
chat added an unrelated module export to src/lib.rs; its rejected recipe is kept.
Pilot-v2 was rebuilt and registered with refreshed current source hashes.

The compact report is generated as [results/REPORT.md](results/REPORT.md), with
coverage, censoring, cost, feature reliability, between-seed dispersion and the
limits of validation. The shareable notebook reads only the compact results.
No scientific success/failure for T1/T2 or A1/A2/A3 follows from these pilots.

Cohort clarification (2026-10-15 23:31 NZDT): [cohort audit](results/cohort_audit.json) finds 169 stationary and 23 drifting rules in the existing pool. Therefore 24 drifting rules are unavailable even before matching; the 22 exact matched pairs are not merely a failure induced by strict matching. The original 48-rule support gate remains failed.


### Completed feasibility pilot — 2026-10-15 23:37 NZDT

Both primary bands reached 176/176 starts. The largest band reached 168/176:
stationary 88/88, drifting 80/88. All eight misses belong to two drifting rules,
all four starts each; they remain in every coverage denominator. No escapes
or unresolved in-band interior time. Max final step was 2^30; all-complete and
quarter-cap reserve gates **FAILED**. Ant batch wall time 757.86 s and process
peak RSS 514.2 MiB with four workers.

Descriptive seed-half Spearman for median log age is 0.413/0.321/0.718; immature
fraction 0.916/0.847/0.860; cycle-count variance 0.910/0.869/0.846. Third-band
reliability uses 42 complete-case rules; primary bands use all 44. These measure
precision, not age-vs-kappa prediction. No A1/A2/A3 scientific test was run.
The weak smaller-band median-age precision and nonrandom third-band missingness
must inform the next design; they do not reject an age mechanism.

See [report](results/REPORT.md), [summary](results/pilot_summary.json),
[per-start features](results/pilot_features.csv), [cohort audit](results/cohort_audit.json)
and [executed notebook](notebook.ipynb). Full release tests pass (tail-budget
results/final-release-tests.log). Finished-pilot rerun preserves original audit
bytes (results/resume_verification.json); mid-run state checkpoints remain absent.
Use `uv run experiments/archive/2026-10-kappa-field-age/scripts/run.py --name pilot-v2`
for verified reruns. Confirmation remains unregistered pending the documented
cohort, precision, checkpoint and estimator requirements. No commit was made here.
