# Lab notebook

### 2026-10-15 21:27 (+13:00) · da88e61 · intent
User requested a new fixed-area sampling and cycle-accounting scaffold so a
fresh agent can work quickly. Create a research plan and explicit interfaces;
do not start simulations or represent draft settings as preregistration.

### 2026-10-15 21:27 (+13:00) · da88e61 · assumption
The prior T1b cohort is a useful selected replication cohort, not representative
of all blob rules. Candidate seeds may have appeared elsewhere; verify before
claiming fresh trajectories. Tail precision and attainability are untested.

### 2026-10-15 21:27 (+13:00) · da88e61 · decision
Define bands by first area hits and episodes by dynamic pre-step boundary labels.
Preserve clipped fragments for exact accounting; separate this identity from
independent-seed, held-out predictive evidence. Keep numerical settings draft
until oracle tests, controls and a pilot establish feasibility. No results yet.

### 2026-10-15 21:33 (+13:00) · da88e61 · observation
`uv run experiments/archive/2026-10-fixed-area-cycles/scripts/preflight.py` passed;
source/config inputs exist, candidate pilot/production seeds are disjoint and
candidate bands are valid. Built notebook from the repository template using
`scripts/make_notebook.py`; uv/nbconvert executed it from a clean kernel and it
reports NOT RUN. Commands are in README/HANDOFF. No scientific measurements.

### 2026-10-15 21:33 (+13:00) · da88e61 · decision
Scaffolding complete: plan, code map, output contract, candidate config,
preflight, executed notebook and isolated bulk directories are ready. Next agent
starts with definitions and oracle-backed instrumentation, then calibrates
feasibility before freezing the primary test. No commit; no sampler implemented.

### 2026-10-15 21:31 (+13:00) · da88e61 · deviation
Corrects the two entries labelled 21:33 above: the observed local clock at
verification was 21:31, not 21:33. Their content and execution status stand.

### 2026-10-15 21:42 (+13:00) · da88e61 · intent
Session 2 (fresh agent). Following HANDOFF order: finalise conventions, build instrument (producer + accounting state machine, split so each has an independent oracle), property tests, controls, pilot. No ant outcomes inspected yet. Core code goes in `src/fixed_area.rs` (adds one `pub mod` line to the already-dirty `src/lib.rs`; the existing `pub mod bulk;` there belongs to another investigation and is left alone). Tests in `tests/fixed_area.rs`.

### 2026-10-15 21:42 (+13:00) · da88e61 · decision
Conventions fixed before code (PLAN B/C refinements; none depend on data):
1. State t = after t moves; stream is states 0..=T where departures 0..T-1 were executed and state T is the final (its departure not executed). Z_t=B iff x_t visited with >=1 unvisited 4-nbr in state t. Origin visited at t=0, so Z_0=B.
2. First episode (B, starting t=0): true_start_observed=false (conservative; the run start is not an observed transition). Never in a complete-contained set.
3. tau(a)=first t with A_t>=a; band = departures [tau(lo), tau(hi)). Requires lo>=2, hi>lo, bands ordered, hi_k<=lo_{k+1}; A grows by <=1 per step, so A_tau(a)==a exactly (asserted).
4. Run STOPS at tau(hi_last) (no follow-up). Hence at most one left-clipped and one right-clipped fragment per band per trajectory; clipping is structurally O(1) episodes, and the censoring gate reduces to the size of those two fragments vs band duration.
5. Complete-contained episode: both transitions observed AND [s,e) inside [tau_lo, tau_hi). Primary full-duration set = complete-contained (band attribution = fully contained only; episodes straddling a band edge get fragments in the band, flagged, and never enter duration quantiles). Straddlers are therefore not double counted.
6. Complete cycle = complete B episode immediately followed by complete I episode (I->B transition to next I->B transition); contained in band iff the whole [s_B, e_I) lies in the band. Records D=|B|, T=|I|.
7. Quantile: nearest-rank, q-quantile = sorted[ceil(q*n)-1] (no interpolation) so it is an observed duration; reported q in {0.5,0.9,0.99,0.999,0.9999} plus max. Tail burden uses fixed log2 duration bins (exact counts and step sums per bin per label) so any threshold 2^j can be applied later without rerunning.
8. "Complete I episode" for the 10k gate = complete-contained I episode in that band.
9. Escape = ant within 2 cells of grid edge after a move (as probe.rs); the state after that move is the final state, status=escaped, bands not reached are null.
10. Guard: sum_pa accumulated as f64 sequentially in t order (identical order in the oracle).

### 2026-10-15 21:48 (+13:00) · da88e61 · observation
Implemented `src/fixed_area.rs` (producer `drive` + pure `Accountant`), `tests/fixed_area.rs` (12 tests: accountant vs offline oracle on 600 synthetic streams, hand-worked cases, producer vs HashSet recount for ant/patched ant/rotor/random walk, oracle positions vs `reference`, escape; 3 deliberate mutants all caught) and CLI `examples/fixed_area_cycles_sampler.rs`. All 12 pass in --release. Smoke run (pilot seed 701, bands 32768-34816,131072-139264, grid 8192, cap 2^28; counts only, no associations inspected): `RLLLLLLLLRR@701`, `rotor:701`, `rw:701` each finish in <=0.6 s, 264 MB peak RSS, t_final 8.2e6 / 4.2e6 / 7.5e5. Complete-contained I episodes for the ant: 1087 (band 0) and 4143 (band 1); 2 clipped B fragments per band, 0 clipped I.
### 2026-10-15 21:48 (+13:00) · da88e61 · surprise
The draft gate "10,000 complete I episodes per seed/band" is unattainable for a 1/16-width band: ~0.08 episodes/step times ~1.3e4 band steps gives ~1e3 per seed at 2^15 (n^0.5 scaling up to ~4e3 at 2^17). The q99.9 of ~1e3 events is essentially the maximum. Runs are cheap (0.6 s), so the lever is seeds, not wider bands (wider bands change what 'fixed area' means).
### 2026-10-15 21:48 (+13:00) · da88e61 · decision
Revise the gate UNIT before the pilot (records a deviation from PLAN E / config.draft: no outcome data involved): the quantile gate is evaluated per rule x band x seed-group (seeds pooled within a group), threshold unchanged at >=10,000 complete-contained I episodes. Seeds per group to be chosen from the pilot's measured per-seed counts (ceil(10000 / min-over-rules median per-seed count), rounded to a power of two), with at least two disjoint groups per rule for the cross-seed design. Pilot widened from 'first four rules' to ALL 44 cohort rules x seeds 701..704, because runtime/attainability heterogeneity across the cohort is the feasibility question; pilot output is summarised by feasibility columns only (no kappa/L999 association is computed). Pilot seeds 701..704 are excluded from production. Cohort list: results/cohort_rules.txt (44 sorted unique rules from t1b_cutoff_seeds.csv).

### 2026-10-15 21:58 (+13:00) · da88e61 · observation
Pilot (184 specs x 3 runs; results/pilot_feasibility.txt, scripts/run_pilot.sh): all runs completed, no escapes; fresh_from_interior = 0 and B+I = steps in every row; 1-thread vs 4-thread payload CSVs byte-identical (368 files). Peak RSS 133 MB (1 thread) / 527 MB (4 threads). Per-seed complete-I counts: 1014..4719 (band 0), 4084..18601 (band 1), median seed-to-seed max/min 1.06. Slowest ant: RRRLLRLLLL (t_final 7.6e7 at 1/16; 8.3e7 at 1/8). Walkers/ants needed per-group seeds: band 0 binding rule RLLLRRRRRRRR needs 10 seeds -> 16.
### 2026-10-15 21:58 (+13:00) · da88e61 · deviation
G-budget (registered: t_final <= 2^28/4 = 6.71e7) FAILED in the pilot (max 7.64e7; every run did complete, 3.5x below the cap). The registered consequence is a cap revision, so cap raised to 2^29 (>= 4x the slowest observed 1/8-band run 8.3e7*... cap/4 = 1.34e8). No other gate failed.
### 2026-10-15 21:58 (+13:00) · da88e61 · observation
Controls (rotor, rw; seeds 801..928; results/controls.txt, controls_summary.csv). (i) I-episodes are never clipped: 0 clipped I steps in all 1024 control band-runs: band edges are arrivals on a fresh cell, which is B, so the single left/right straddlers are B fragments. Hence completed-only I accounting is not selected by band edges, a structural property to be checked on ants, not assumed. (ii) PA_end/PA_time = 0.995 (rotor, 1/16, both bands) so lnk_end - lnk_time = +0.005..0.007, an order of magnitude below between-seed sd of lnk (0.08..0.17). (iii) Direct vs cycle-reconstructed f_B: gap -0.0002 (rotor), -0.0011 (rw) at 1/16 band 0 (~0.2% of f_B); identity bookkeeping holds. (iv) Width: f_B falls 7-15% from 1/32 to 1/4 (rotor), ln kappa_end shifts by <=0.04; ln q999 shifts <=0.014 (rotor, 1/16 vs 1/32) vs 16-seed group sd 0.05-0.07 (rotor) or 0.17-0.36 (rw). (v) Scatter of pooled 16-seed ln q999 across the 8 control groups: rotor 0.070/0.050, rw 0.355/0.168 (band 0/1 at 1/16). Nothing here is a target-value test (no known answer for conditional kappa).
### 2026-10-15 21:58 (+13:00) · da88e61 · decision
FREEZE (config.frozen.json sha256 4bf1215ccd2275dc413e95c4434bf2b4d7de03ea784550d4b267fe4e4107fc1a, README section 'Registration'): primary kappa = kappa_time (rationale: (ii)); primary tail = ln pooled q99.9 per 16-seed group; 1/16 bands primary, 1/8 sensitivity only; production seeds 1001..1064 as 4 groups x 16; P1/P2 definitions, rotations, G-reliab, bootstrap as in the file. Registered before any production ant run; no ant kappa/tail association has been computed anywhere in this experiment.

### 2026-10-15 21:58 (+13:00) · da88e61 · deviation
Corrects the garbled parenthesis in the previous 'G-budget' deviation entry. Cap raised from 2^28 to 2^29 = 5.37e8; the gate (t_final <= cap/4 = 1.34e8) is then met by the slowest pilot run (8.33e7 at 1/8 width) with 1.6x headroom for seed variation (observed seed-to-seed spread of t_final for the slowest rule ~5%).

### 2026-10-15 22:00 (+13:00) · da88e61 · decision
Implementation details of the frozen analysis, fixed before production outcomes were opened (scripts/analyse.py; header comment): (1) P2 bootstrap resamples the per-rule leave-one-rule-out squared-error terms computed once on the 44 rules (no refit on bootstrap samples), so a duplicated rule never sits in its own training set; (2) Spearman with average ranks; (3) feature 'ln PA_time' = mean over the group's seeds of ln(PA_time), 'ln mean complete B duration' = ln(pooled complete-B steps / pooled complete-B count); (4) the 1/8-width run (prod8) re-uses the same seeds, so it is a sensitivity analysis, not an independent replication. No outcome files were opened while writing this script.

### 2026-10-15 22:02 (+13:00) · da88e61 · decision
Session stopped at a usage limit. State: full `cargo test --release` passes (incl. 12 fixed_area tests). Production (scripts/run_production.sh, log results/production.log) was still running in the background and may have been killed with the session; it is resumable (rerun the script; parameter-stamped .done markers skip finished specs). NOT done: run analyse.py (written, unrun, no outcomes seen), thread-count determinism check on production, notebook.ipynb (still the NOT RUN scaffold), README results section, linking in notes/.

### 2026-10-15 22:04 (+13:00) · da88e61 · intent
Session 3: user requested continuation. Production sampler is still live (PID 436679; 1487/2816 primary markers observed at 22:04). Preserve it; audit saved payloads and frozen analysis, verify production determinism and release tests, then analyse both complete batches and replace the shareable scaffold with a results notebook. WSL requires sandbox elevation in this session; access succeeded. No outcomes inspected yet.


### 2026-10-15 22:07 (+13:00) · da88e61 · decision
Before outcome analysis: add audit.py to verify every frozen marker, band endpoint, integer partition, duration count/sum and payload hash; analyse.py now requires the audit and cannot report overall success through failed reliability/coverage gates. Frozen estimands, folds and bootstrap unchanged. Run a one-thread replay of seed 1001 for all 44 rules at both widths against five-thread production; this samples 1/64 seeds and does not fully establish the registered all-production determinism clause of P3. Report this validation limit explicitly.


### 2026-10-15 22:10 (+13:00) · da88e61 · observation
Primary production completed: 2816/2816 markers, production.log at 22:09:55. Sensitivity production started automatically. Full cargo test --release passed (results/release_tests.log), frozen input preflight passed (results/preflight.log). Commands run through WSL with the prescribed uv environment. No associations inspected yet.

### 2026-10-15 22:10 (+13:00) · da88e61 · decision
Add --run prod16 to audit/analyse, writing distinctly named interim files, so the completed primary can be inspected while the same-seed sensitivity sweep runs. This changes scheduling/output paths only; the frozen analysis remains unchanged. Final default invocation will produce the combined result files.


### 2026-10-15 22:12 (+13:00) · da88e61 · observation
Primary payload audit passed for all 2816 specs / 5632 band rows, no incomplete runs and max censor-gate ratio 0 (audit.prod16.json; command: uv run experiments/archive/2026-10-fixed-area-cycles/scripts/audit.py --run prod16). A synthetic estimator check initially failed an exact floating-point equality between an intercept-only least-squares prediction and the arithmetic mean; revised the check to tolerance 1e-12. Exact linear-model and independent PRESS checks had already passed. No analysis estimator was changed.


### 2026-10-15 22:14 (+13:00) · da88e61 · deviation
Corrects the structural explanation in the 21:58 controls observation: a fresh arrival can fill a hole with all four neighbours already visited, so an area-band edge need not be B. Zero clipped I in the controls and primary production is empirical, not a theorem of this sampling scheme. Added a 3x3 hole-filling counterexample in tests/fixed_area.rs. No sampler or frozen estimator changed; retain the censor gate and audit every band rather than assume it away.


### 2026-10-15 22:16 (+13:00) · da88e61 · observation
Frozen primary analysis complete (uv run experiments/archive/2026-10-fixed-area-cycles/scripts/analyse.py --run prod16; results/analysis.prod16.json and .txt). All 2816 runs complete; max t_final 78900629; min pooled I count 16469/65701 (bands 0/1); no clipped I. Reliability q A/B = 0.613/0.969, kappa C/D = 0.964/0.954, all pass. P1 = -0.285 (95% CI [-0.558,-0.005]) / -0.814 ([-0.908,-0.665]); P1 FAILS the both-band rule because band 0 misses <= -0.30. P2 R2 gains +0.336 ([0.115,0.578]) / +0.544 ([0.316,0.822]); both pass. Full release tests pass again after the hole counterexample (results/release_tests_hole.log). Synthetic analysis checks pass (results/analysis_checks.log).

### 2026-10-15 22:16 (+13:00) · da88e61 · interpretation
The cutoff carries incremental held-out predictive information under this selected-cohort design, particularly at the larger area, but the primary prediction fails as registered. The smaller-area effect cannot be rescued by rounding -0.285 to the threshold or reporting only its confidence-interval sign. P2's success does not identify tail time burden as the carrier, nor establish causality: the predictor is a quantile, geometry is incompletely controlled, and the same 44 selected rules supply all folds. Await the predeclared width sensitivity; do not retune estimators.


### 2026-10-15 22:21 (+13:00) · da88e61 · observation
Changed ingestion only: parse the thousands of tiny CSVs with stdlib csv, construct polars frames once. uv run experiments/archive/2026-10-fixed-area-cycles/scripts/check_loader.py validates every primary summary field against the original-loader results/rule_summary.prod16.csv (agreement at 1e-12; results/loader_checks.log). Original primary outputs retained, not overwritten. All frozen transformations, statistics and gates unchanged. The earlier inline uv command failed to launch (-c without an interpreter); the successful check is the file-based command above.


### 2026-10-15 22:22 (+13:00) · da88e61 · observation
Production finished: prod16 2816 specs at 22:09:55; prod8 2816 specs at 22:21:24 (results/production.log, scripts/run_production.sh). The one-thread replay of all 44 rules at seed 1001 matches five-thread production at both widths: 88 specs, 440 files byte-identical (results/determinism.json; uv run experiments/archive/2026-10-fixed-area-cycles/scripts/check_determinism.py). This checks a subset, not the full registered all-seed P3 determinism clause. scripts/finish.sh is now running the combined audit/analysis and notebook execution.


### 2026-10-15 22:24 (+13:00) · da88e61 · observation
Combined production payload audit passed for both batches: 5632 runs total, 11264 band rows; every target reached, accounting/histograms/duration checks passed, max censor gate ratio zero at both widths. Command: uv run experiments/archive/2026-10-fixed-area-cycles/scripts/audit.py; results/audit.json and results/production.sha256 (manifest SHA256 8db06ca76587db93ddf2fbd5c068d6c51a9423c46cd2033b3d68df570ad712e3). Final frozen analysis is in progress; no sensitivity associations inspected yet.


### 2026-10-15 22:24 (+13:00) · 275c2af · deviation
Shared-workspace provenance correction: HEAD advanced elsewhere during this session, first to 4529f86 (literature review), then 275c2af (fixed-area experiment). This continuation issued no git commit command. Entries above retaining da88e61 identify the session's starting base; their actual write-time HEAD after the external commits may differ. The combined audit records observed HEAD 4529f86, while final analysis/notebook may record 275c2af. No sampler/core-source difference from current HEAD is present (git diff of src/fixed_area.rs, src/walkers.rs, src/rule.rs, example and Cargo.lock is empty). Post-run source and payload hashes remain the precise provenance. Do not reinterpret these commit changes as new simulations or rewritten predictions.


### 2026-10-15 22:28 (+13:00) · 275c2af · observation
Final pipeline completed: scripts/finish.sh ran combined audit, frozen analysis, figure and notebook. Sensitivity P1 -0.417 CI [-0.651,-0.132] / -0.815 [-0.905,-0.661], P2 gains +0.488 [0.219,0.767] / +0.530 [0.300,0.777]; all statistical/coverage gates pass. Maximum sensitivity final time 86613887; min pooled I counts 33089/131429. Results: analysis.json/.txt, rule_summary.csv, audit.json, production.sha256, run_status.csv, association.png/.json. The combined primary statistical object exactly equals the original primary analysis object. Figure visually inspected; final notebook regenerated and executed after adding sensitivity interpretation (results/notebook.log), no error outputs.

### 2026-10-15 22:28 (+13:00) · 275c2af · interpretation
P1 primary fails as registered; P2 secondary passes. Both width-sensitivity tests pass, demonstrating lower-area band-width dependence, not an independent rescue of P1. The higher-area association and the added predictive value persist. The changed width alters event counts and the first-area-hit ensemble simultaneously, so the reason for the smaller-area shift remains unresolved. No causal or direct tail-time-burden conclusion follows.

### 2026-10-15 22:28 (+13:00) · 275c2af · decision
Session complete for production, frozen analysis, reproducible summaries and shareable write-up. README, notebook and research-avenues note agree; tests and numerical checks passed. Explicit outstanding validation: P3 all-production thread determinism was not fully replayed (88/5632 production specs replayed, all match); no mid-run walker checkpoints or raw episode/cycle tables are claimed. Future mechanistic work needs a fresh registered intervention/time-burden design; do not tune this primary result post hoc. No commit command issued by this continuation; concurrent external commits are recorded above.

