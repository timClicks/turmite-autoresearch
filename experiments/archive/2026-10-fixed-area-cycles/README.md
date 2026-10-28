# Fixed-area sampling with cycle accounting

**Current status: production, registered analysis and executed notebook complete.**
P1 fails the registered both-band criterion; secondary P2 passes at both bands.
The original scaffold
description below is historical; the dated pilot and frozen registration at the
end supersede its draft parameters. See NOTEBOOK.md for the continuation log.

## Original scaffold (historical)
Created 2026-10-15 21:27 +13:00 at base `da88e61` (dirty workspace).
User requested a directory, files and research plan for a fresh agent.

## Start here

Read [HANDOFF.md](HANDOFF.md), then [PLAN.md](PLAN.md) and
[SCHEMA.md](SCHEMA.md). Candidate parameters are in `config.draft.json`.
The next agent should implement and calibrate the instrument, then freeze a
dated preregistration here before inspecting ant outcomes. This scaffold
does not implement the sampler or launch jobs.

## Question

At comparable visited area, does the extreme interior-excursion tail predict
boundary activity across rules? If so, is the difference carried by interior
return time rather than boundary residence time?

Motivation: [research avenues](../../../notes/cutoff-research-avenues-2026-10-15.md),
[independent-area test](../2026-10-independent-area/README.md),
[earlier excursion audit](../../../notes/excursion-tomography-2026-10-13.md),
[matched-area noise-floor failure](../2026-10-kappa-matched-area/README.md).
The previous association is a lead, not evidence of causality. Its failed
noise-floor gate remains failed.

## Proposed predictions — NOT frozen

1. At each prespecified area band, rule-mean ln kappa is negatively associated
   with the exact completed-excursion 99.9th percentile, using disjoint seed
   groups for predictors and outcomes. Candidate success bar: Spearman <= -0.30
   with rule-bootstrap upper 95% bound <0 at both primary bands. Quantile
   reliability and censoring must pass a pilot gate first; otherwise this
   prediction is not testable with the proposed budget.
2. A model using interior tail burden improves prediction of independent-seed
   boundary occupancy beyond size, geometry and boundary residence. Candidate
   bar: rule-held-out R² gain >=0.10 with bootstrap lower bound >0. Explicit
   features, folds, baseline and training-mean R² definition must be frozen
   first. Exact accounting on the same trajectories does not test this claim.
3. Complete episodes plus clipped fragments reconstruct every step exactly;
   this is an instrument acceptance condition, not a scientific discovery.

## Commands available now

All toolchains run in WSL, from `/mnt/f/Code/turmite`:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-fixed-area-cycles/scripts/preflight.py
```

This validates the scaffold, resolves source paths and prints hashes. It runs
no simulation and writes no results. See HANDOFF for future build/test commands.

## Output and reproducibility contract

Scripts locate the repository via `Path(__file__).resolve().parents[3]` and
write only inside this experiment. Bulk episodes/checkpoints go in `dumps/`
or `scratch/`; small summaries, run manifests and completion markers go in
`results/`. Do not hand-edit generated results. Deterministic rule/seed order,
explicit RNG seeds, input/config/source hashes and exact commands are required.
Only completed, verified per-run outputs receive `.done` markers. Resume must
check hashes and parameters before skipping work. Never silently reuse results
from a different config. No new dependencies are proposed.

## Results / status

No scientific results. `notebook.ipynb` is a shareable scaffold that runs with
standard-library Python, reports provenance and explicitly reports missing
results. Fill it from small committed summaries after the experiment runs.
No Rust source, existing results or dependency locks changed by scaffolding.

## Scaffold verification

`scripts/preflight.py` passed under uv/WSL. The notebook was built from
`experiments/_template/notebook.ipynb` using `scripts/make_notebook.py`, then
executed successfully from a clean kernel with the nbconvert command in HANDOFF.
It explicitly reports NOT RUN. The generator refuses to overwrite an existing
notebook. No scientific simulations were run; release tests are required when
the sampler is implemented. The prior session's release tests passed, but do
not validate this unimplemented instrument.

---

## Pilot protocol (registered 2026-10-15 21:48 (+13:00), da88e61; BEFORE the pilot ran)

Scope: feasibility only. 44 cohort rules (results/cohort_rules.txt) x seeds 701..704, plus rotor:701..704 and rw:701..704; bands [32768,34816) and [131072,139264) (1/16 width) and a sensitivity run with 1/8-width bands [32768,36864), [131072,147456); grid 8192, cap 2^28, `RAYON_NUM_THREADS=4`. Seed-reuse check: no use of seeds 701..716 in prior specs found by grep of experiments/ (2026-10-15).
Reported per spec x band: status, t at band end, steps, complete-contained I counts, complete-I share of band steps, clipped fragments (count, max), q99.9 and its rank position n*0.001, plus wall time and peak RSS. NOT computed in the pilot: any relation between tail/L999 and kappa/f_B across rules.
Gates frozen now (revisions only by dated deviation):
- G-budget: every pilot run must reach tau(hi) of the last band with t_final <= 2^28/4, else cap/grid are revised before production.
- G-escape: no escaped runs; peak RSS per job <= 400 MB (concurrency 4-6 allowed).
- G-quantile (unit = rule x band x seed-group): >= 10,000 complete-contained I episodes (>=10 observations beyond q99.9). Seeds per group derived from the pilot as in the NOTEBOOK decision.
- G-censor: (largest clipped I fragment + clipped I steps)/ (band I steps) <= 0.10 per spec x band.
- G-bias: rotor and rw controls have to satisfy the exact accounting identities (fresh_from_interior = 0, B+I = steps) and the pilot runs from 1 and default thread count must agree byte-for-byte (determinism).
Failure of any gate is reported as such; no rule or seed is dropped from the denominator.

---

## Registration (frozen 2026-10-15 21:58 (+13:00), da88e61; BEFORE any production ant run)

Everything below is in `config.frozen.json` (sha256 `4bf1215ccd2275dc413e95c4434bf2b4d7de03ea784550d4b267fe4e4107fc1a`, also in results/config.frozen.sha256). Pilot and controls are done (results/pilot_feasibility.txt, results/controls.txt; summary in NOTEBOOK). No ant tail-vs-kappa association has been computed by anyone in this experiment.

Design: 44 cohort rules x 64 fresh seeds 1001..1064 = 4 disjoint groups A,B,C,D of 16; primary bands [32768,34816), [131072,139264); grid 8192; cap 2^29; 1/8-width bands are a sensitivity run only.
Per rule x band x group: ln q999 = ln of the nearest-rank 99.9th percentile of the pooled complete-contained I durations; ln kappa_time = mean over the group's 16 seeds of ln(f_B / PA_time).
- **P1 (primary)**: statistic = mean of Spearman(ln q999 from A, ln kappa from C) and Spearman(ln q999 from B, ln kappa from D) over the 44 rules. Predicted sign negative. Success: statistic <= -0.30 and its rule-bootstrap (2000 draws, seed 20261016, rules resampled with all groups and both bands) 95% percentile upper bound < 0, at BOTH bands (intersection-union, so no multiplicity adjustment).
- **P2 (secondary)**: leave-one-rule-out OLS; baseline features ln mean complete-B duration and ln PA_time; added feature ln q999; R2_cv = 1 - sum(y - yhat_loo)^2 / sum(y - ybar_loo)^2; rotations (tail A, baseline B, outcome C) and (tail B, baseline D, outcome A); success: mean gain >= 0.10 with bootstrap lower bound > 0 at both bands.
- **G-reliab**: Spearman(ln q999 A vs B) >= 0.5 and Spearman(ln kappa C vs D) >= 0.5 at each band; if it fails P1/P2 are reported as untestable at this precision (numbers still shown).
- **P3** (instrument): fresh_from_interior = 0, B+I = steps, fragments + complete episodes partition B and I, and byte-identical output across thread counts, on all production runs.
- Gates G-budget, G-escape, G-quantile (>=10,000 complete I episodes per rule x band x group), G-censor as in the Pilot protocol; failures are reported, nothing is dropped.
- Additional descriptive (not tests, no thresholds): kappa_end instead of kappa_time; 1/8-width bands; within-rule between-group sd; completed-only vs clipped shares.
Revisions only by dated deviation in NOTEBOOK.md.

## Primary results — 2026-10-15, session 3

All 44 rules x 64 seeds = 2816 primary runs completed, with both bands reached;
max final time 78,900,629 < cap/4. Every saved band's B/I accounting, duration
count/sum, histogram totals and exact area endpoints pass the payload audit.
No interior time was clipped. Minimum pooled complete-I counts per group are
16,469 and 65,701 (bands 0/1), above 10,000. Reliability gates pass: q999 A/B
Spearman 0.613/0.969, kappa C/D 0.964/0.954.

| Registered test | Area 32768 band | Area 131072 band | Both-band verdict |
|---|---|---|---|
| P1 mean cross-seed Spearman | -0.285; 95% CI [-0.558,-0.005] | -0.814; [-0.908,-0.665] | **FAIL**: smaller-area statistic misses <= -0.30 |
| P2 held-out R2 gain | +0.336; [0.115,0.578] | +0.544; [0.316,0.822] | **PASS** (secondary) |

These are rule-bootstrap percentile intervals (2000 draws, seed 20261016).
For P2, the registered bootstrap resamples fixed held-out squared-error terms;
it does not refit models and therefore conditions on the fitted training sets.
Per-seed kappa sample sd and within-rule group dispersion are in
`results/rule_summary.prod16.csv` and `results/analysis.prod16.json`.
P2 baseline/full R2 by rotation are 0.197/0.514 and 0.130/0.486 (smaller area),
0.152/0.684 and 0.162/0.720 (larger area).

Interpretation: the extreme cutoff adds predictive information beyond the
registered boundary-residence/P-A baseline in this selected cohort. The primary
prediction nevertheless fails; neither rounding nor the larger-area result
rescues its both-band rule. This does not establish a causal mechanism, a direct
tail-time-budget explanation, or generalisation to new rules. Fixed area leaves
shape, age and colour-field differences uncontrolled.

Correction to the earlier control interpretation: a fresh arrival can fill an
interior hole, so first area hits are not guaranteed to be boundary states.
The zero observed I clipping is empirical, and the censor gate remains necessary.
The hand-worked hole case is now in `tests/fixed_area.rs`.

Reproduce from the WSL repo root, with
`export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`:

```bash
bash experiments/archive/2026-10-fixed-area-cycles/scripts/run_production.sh
uv run experiments/archive/2026-10-fixed-area-cycles/scripts/check_determinism.py
uv run experiments/archive/2026-10-fixed-area-cycles/scripts/audit.py
uv run experiments/archive/2026-10-fixed-area-cycles/scripts/analyse.py
uv run experiments/archive/2026-10-fixed-area-cycles/scripts/check_analysis.py
uv run experiments/archive/2026-10-fixed-area-cycles/scripts/check_loader.py
uv run experiments/archive/2026-10-fixed-area-cycles/scripts/figures.py
uv run experiments/archive/2026-10-fixed-area-cycles/scripts/results_notebook.py
uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-fixed-area-cycles/notebook.ipynb
cargo test --release
```

The completed-primary interim audit/analysis used `--run prod16`; final combined
files are produced by the default commands above. `scripts/finish.sh` waits for
production and the determinism sample, then runs the final pipeline. It does
not start production. `results/release_tests.log`, `release_tests_hole.log` and
`analysis_checks.log` record successful validation. No dependencies changed.
Dirty base commit: da88e61b690507526ba4e2a2c017d9c7941beb91. No commit made.

Reproducibility limits: resume is per finished trajectory with parameter-only
markers, not a source-hashed walker checkpoint. The continuation leaves sampler
source unchanged; post-run hashes record checked payloads and current sources.
The one-thread production replay covers one of 64 seeds per rule at both widths;
it cannot establish P3's full all-production determinism clause.

## Width sensitivity and final validation — 2026-10-15

All 2816 sensitivity runs completed; max final time 86,613,887 < cap/4.
All accounting/coverage gates pass, zero clipped I, minimum pooled I counts
33,089/131,429. Reliability q A/B = 0.756/0.975, kappa C/D = 0.969/0.965.

| 1/8-width sensitivity | Area 32768 band | Area 131072 band |
|---|---|---|
| P1 mean cross-seed Spearman | -0.417; 95% CI [-0.651,-0.132] | -0.815; [-0.905,-0.661] |
| P2 held-out R2 gain | +0.488; [0.219,0.767] | +0.530; [0.300,0.777] |

Both sensitivity predictions pass their numerical and statistical gates. These
reuse the same rules/seeds and do not rescue the primary P1 failure. The weaker
small-area association is sensitive to band width; these data alone do not
separate greater event counts from the changed sampling ensemble. No post-hoc
retuning was performed. The larger-area association and P2 prediction persist.

Final outputs: [analysis](results/analysis.txt), [machine-readable analysis](results/analysis.json),
[rule/group summaries](results/rule_summary.csv), [payload audit](results/audit.json),
[thread replay](results/determinism.json), [figure](results/association.png),
and [executed notebook](notebook.ipynb). The final primary statistical results
exactly match the original-loader interim primary results. Figure visually
checked; notebook executes without error outputs (results/notebook.log).

All 5632 production runs / 11264 band rows pass accounting. The one-thread
determinism sample passes for 88 specs / 440 files. **P3 is only partially
validated:** full all-seed thread replay is not done. Release tests pass,
including 13 fixed-area tests; synthetic numerical checks pass. The earlier
noise-floor failure remains failed. No causal conclusion is warranted.

Provenance: initial base da88e61; shared-workspace HEAD advanced externally to
4529f86 during the combined audit and then 275c2af before final analysis/notebook.
This continuation issued no commit command. Each output records its observed
commit and hashes; sampler sources were unchanged during the continuation.
See NOTEBOOK's provenance correction rather than treating these as distinct
simulation batches. New report files remain for the user's next commit.
