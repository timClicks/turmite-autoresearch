**Current status (2026-10-15): instrument calibration and feasibility pilot complete; scientific confirmation NOT RUN. See [results report](results/REPORT.md). The initial scaffold below is historical.**

# Kappa from excursion survival mass

Status: **draft research plan; no instrument implemented or measurement run**.
Created 2026-10-15 22:54 +13:00, base `b3a0f762ac2230b5df92188206a4d3a1081897be`
(dirty tree). [Mechanism note](../../../notes/kappa-mechanisms-2026-10-15.md).

## Question and mechanism

Does a transferable survival law explain boundary occupation through mean
interior return time? The fixed-area experiment predicts using q999; it has
not shown that a tail-mass model predicts the size of the effect. Earlier
tomography's top-1% contrast and early-to-late forecast failed. We will not
repeat those tests under new names.

For quasi-stationary cycles, predicted kappa is
`E[D] / (E[D] + E[T]) / g`, where g is the stated P/A normalization.
For integer T, `E[T] = sum_u Pr(T > u)`. Same-window reconstruction is only
an instrument check. Primary scientific target is independent-seed boundary
occupation; kappa conditional on independently measured geometry is secondary.

## Draft design and predictions (freeze before ant outcomes)

1. Pilot the existing 44-rule fixed-area cohort on four fresh starts per rule,
   solely to test output completeness and censoring; exclude pilot seeds from
   confirmation. Confirm with 32 fresh starts per rule, equally partitioned
   into predictor and outcome roles. Candidate bands start at 32768, 131072
   and 524288 visited cells, width A/16; cap each run at 2^30 steps. These are
   proposed budgets, not a claim of feasibility. Publish nonattainment.
2. Record logarithmic duration-bin **counts and time sums**, boundary episodes,
   completed interior episodes and clipped fragments. Follow an open episode
   beyond a band up to the run cap, attributing only its in-band time to that
   band's budget. Unresolved tails yield lower/upper bounds, not a completed-
   episode mean silently treated as unbiased. Entry-conditioned hazards can
   differ from time-sampled hazards; retain both labels.
3. Candidate tail onset is 64 steps; 16 and 256 are labelled sensitivities.
   Fit a short-return mass plus a truncated survival family to predictor
   seeds, fixing family and loss after synthetic calibration and before ant
   confirmation. Compare to empirical binned survival, q999 alone, and a
   geometry/boundary-residence baseline. Do not tune onset on target kappa.
4. Draft prediction T1: the survival model predicts outcome-seed B/S with
   rule-held-out R2 gain >=0.10 over geometry/residence and bootstrap lower
   bound >0 at both smaller bands. T2: parameters' frozen area-scaling law
   predicts the third band with median relative occupation error <=20%.
   Report q999 comparison whether better or worse. These thresholds are
   design choices. No success claim if censor bounds permit both verdicts.
5. Decompose model-predicted differences by replacing tail probability,
   tail conditional mean and boundary mean one at a time, averaging replacement
   order. These are model counterfactuals, not causal interventions. If only
   boundary residence transfers, reject the tail explanation at these scales.

## Controls, inference and gates

Exact path fixtures and reference-vs-fast property tests must conserve every
step, including episodes clipped at both edges. Synthetic geometric and
two-component renewal streams have known means; test right censoring and
serially correlated cycles. Rotor is a dynamical positive control; random
walk is a contrasting regime, not an assumed universal kappa constant.
Use separate control seeds and report estimator bias before ant inference.

Draft reliability gate: at least 80% of rules retain 12 seeds in each role
at each primary band; unresolved time <5% or bounds narrow enough to leave
the verdict unchanged. Freeze rule folds before outcomes; bootstrap rules
(2000 draws), retaining paired starts and windows. Report between-seed sd.
Pilot determines whether budget can meet these gates, never a favorable cohort.
No broad-census claim from this selected 44-rule cohort.

## Implementation and next action

Read the current fixed-area README and source, including its corrections.
Determine whether small committed outputs already contain time sums; if not,
extend the sampler in a new example named `kappa_tail_budget_*`, property-test
it, and generate new outputs here. Do not read another experiment's dumps or
overwrite its results. Freeze the exact cohort, seeds, distribution family,
folds and config hash in a dated append-only registration before confirmation.

See [PLAN.md](PLAN.md) for shared execution requirements, [SCHEMA.md](SCHEMA.md)
for outputs and [HANDOFF.md](HANDOFF.md) for the starting checklist.
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

### Completed feasibility pilot — 2026-10-15 23:24 NZDT

All 44 rules x four starts reached all three bands: 176/176 starts per band,
no escapes and zero unresolved interior time. Runtime was 655.44 s with peak
process RSS 530.4 MiB for four concurrent jobs (timing includes brief replay
contention). The quarter-cap reserve gate **FAILED**: max final step 831,505,321
exceeds 2^30/4, although every start attained its targets.

P(T>=64) has descriptive seed-half Spearman 0.957/0.962/0.985 across the three
bands; full entry mean has 0.656/0.635/0.847. This is feature repeatability, not
an association with kappa or evidence of a tail mechanism. No T1/T2 prediction
was tested. See [generated report](results/REPORT.md),
[summary](results/pilot_summary.json), [per-start features](results/pilot_features.csv)
and the [executed notebook](notebook.ipynb). Original scientific predictions
and their thresholds remain unchanged. Confirmation needs its own frozen model,
fold/seed manifest and state checkpoints after the reserve gate is resolved.


## Gate resolution and REGISTRATION — 2026-10-16 (NZDT), base 269288e (dirty tree)

Pre-registered criteria are in NOTEBOOK.md (entries 00:08-00:12); outcomes in entries 00:12-04:15. Summary:

| Gate | Result |
|---|---|
| G1 reserve | The pooled/per-rule parametric max-step projection was invalid and is discarded (results/reserve_projection.json). Replaced by a fresh validation: 96/96 starts (8 rules x 12 fresh seeds, cap 2^33) attained, max 796,445,346 steps. **Cap 2^32 (reserve 1,073,741,824) passes**, headroom 1.29x pilot max, 1.35x validation max. |
| G2 resume | **Deviation:** no mid-trajectory state checkpoint (private `Region`/`Accountant`/`Tails` state lives in src/, out of scope). Finished-trajectory resume: 1 vs 2 threads and SIGKILL-then-resume byte-identical (182 files), results/interrupt_resume.json. Slowest pilot trajectory 108 s; half-written-stem path untested. |
| G3 survival family | Truncated power-law family F: C1 pass, **C2, C3, C4, C5 fail** (results/fit_calibration.json). **F not frozen; E[T] is the empirical binned mean**, F a labelled sensitivity. Null result for the parametric family at these sample sizes. |
| G4 T1 machinery | Synthetic: 0/300 false positives, power ~100% for lam>=0.5. Weak control (saturated power, synthetic nuisances). |

**Registration (frozen 2026-10-16, before any confirmation outcome; confirmation NOT launched).**
Cohort: the 44 rules of the fixed-area cohort (list and sha256 in `results/confirm-v1.manifest.json`, sha256 of the manifest file 19a86779...). Seeds 2026101801..2026101832 (verified absent from all other manifests/notes); role by seed identity: predictor = even offsets (801,803,...), outcome = odd offsets (802,804,...), 16 each. Bands [32768,34816), [131072,139264), [524288,557056); board 4096; **cap 2^32**; 2 workers (est. 2.8 h from the pilot CPU total; expect >2 h); launch with `scripts/run.py --name confirm-v1` only. Estimator: empirical binned E[T] from entry-conditioned log2 time sums, tail onset 64 (16/256 sensitivities), plus separate p(T>=64) and tail conditional mean; unresolved time is reported as a lower bound and >=5% unresolved fails a band. T1 (unchanged thresholds): per band 0 and 1, y = mean over outcome seeds of B/S; baseline regressors (log predictor-seed boundary mean sojourn, log P/A at band start), full adds log E[T]; statistic = leave-one-rule-out PRESS R2 gain; PASS if gain >= 0.10 and the 95% percentile rule-bootstrap lower bound (2000 draws over the LOO residual pairs, seed 2026101599) > 0 at BOTH bands. T2: per rule, extrapolate log E[T], log m_B and log P/A linearly in log area from bands 0 and 1 (predictor seeds) to band 2; PASS if median relative error of predicted outcome-seed B/S <= 20% at band 2. q999 and geometry-only comparators are reported either way. Reliability gate: >=80% of rules keep 12 seeds per role per band; no escapes. Nonattainment is published, not dropped. No claim for the broad census from this cohort. Decomposition counterfactuals (README item 5) use the empirical p, tail mean and boundary mean.

**Result (2026-10-16, confirm-v1; see NOTEBOOK and results/confirm-v1.analysis.json).** Gates pass (1408/1408, no escapes, max step 8.13e8 <= 2^30, 44/44 rules x 12 seeds). T1 FAILS (band 0: gain 0.35, lower bound -0.018; band 1: gain 0.51, lower 0.25). T2 passes (median rel. err 0.123 vs 0.20) but the model-free persistence comparator is better (0.072) and q999 is worse (0.504). Analysis script was written after the run with choices fixed in its header (NOTEBOOK deviation entry). Decomposition (item 5) not yet run.

**Decomposition (2026-10-16, scripts/confirm_decomposition.py -> results/confirm-v1.decomposition.{json,csv}).** Band 0 -> band 2, Shapley over p_tail, tail mean, short mean (fourth factor, deviation), boundary mean. Tail mean carries median share 0.92 of |phi| (44/44 rules), p_tail 0.07, boundary mean 0.003; p_tail and tail mean offset each other strongly. Onsets 16 and 256 agree. Corr(model dF, observed dy) across rules 0.66. The 'only boundary transfers' rejection rule is not triggered, but this is largely forced by the identity (E_T >> m_B) and is a model counterfactual, not causal evidence. Script written after T1/T2; rule fixed in its header.
