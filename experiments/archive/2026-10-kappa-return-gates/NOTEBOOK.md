# Lab notebook

### 2026-10-15 22:58 +13:00 · b3a0f762ac2230b5df92188206a4d3a1081897be · intent

User requested brainstorming notes and experiment scaffolds. Prepare a prospective plan from current evidence; do not run new measurements. Existing workspace changes are preserved.

### 2026-10-15 22:58 +13:00 · b3a0f762ac2230b5df92188206a4d3a1081897be · assumption

The mechanism in README is untested. Candidate cohort and budgets may be infeasible; calibration, coverage and seed-history audits must resolve this before registration. Thresholds and seeds are draft choices.

### 2026-10-15 22:58 +13:00 · b3a0f762ac2230b5df92188206a4d3a1081897be · decision

Separate this mechanism from prior failed tests; add explicit independent-seed prediction and reliability gates. No new scientific outputs exist. See README and the linked prior investigations.


### 2026-10-15 22:59 +13:00 · b3a0f762ac2230b5df92188206a4d3a1081897be · observation

Scaffold preflight and clean-kernel notebook execution passed using the uv/WSL commands in HANDOFF.md. All new Markdown links resolved in a PowerShell local-path check. The shared workspace passed cargo test --release; full log is local scratch at experiments/archive/2026-10-kappa-tail-budget/scratch/scaffold-release-tests.log (ignored). These checks validate scaffolding and existing code, not the proposed instrument. Initial sandbox WSL access failed with E_ACCESSDENIED; the approved elevated retry succeeded. No scientific runs were performed.

### 2026-10-15 22:59 +13:00 · b3a0f762ac2230b5df92188206a4d3a1081897be · decision

Planning complete; all predictions remain draft and NOT RUN. Next session should calibrate the proposed instrument, audit seed freshness, fix the cohort and budget, then append a frozen registration. No dependencies changed and no commit made.


### 2026-10-16 17:30 +13:00 · baac481911aa68db941e6b692be978dcfb5f08af · intent

Session goal: complete one experiment. Chosen: this one, Stage 1 only (reference + fast rim/interior crossing instrument, calibration, seed/cohort audit, frozen registration, pilot for split-half reliability, then G1 confirmation). No ant outcome data from this experiment exist yet.

### 2026-10-16 17:30 +13:00 · baac481911aa68db941e6b692be978dcfb5f08af · deviation

G2 (snapshot-fork gate/non-gate edit interventions) is out of scope for this session and will be registered as an unrun follow-up. Decided before any data. A G1 pass, G1 fail or reliability-gate failure each count as a completed Stage 1.

### 2026-10-16 17:55 +13:00 · baac481 · observation

Seed audit (manifests/configs/READMEs/logs outside dumps/scratch, plus file names and source): namespaces 20261015xx, 20261017xx, 20261018xx are used by sibling experiments; 202610(20|21|22)xx appear nowhere. This experiment uses pilot 2026102001-08, confirmation predictor 2026102101-64, confirmation target 2026102201-16, controls 2026102051-58, calibration 2026102061, bootstrap 2026102099. The PLAN.md candidates 2026101501.. and 2026101601.. are NOT used (the former collide with sibling pilots).

### 2026-10-16 17:56 +13:00 · baac481 · observation

Instrument implemented: src/return_gates.rs (incremental capped depth map, stage-A crossing / stage-B reclassification split, exposure tallies, excursions, hole split by flood fill). tests/return_gates.rs compares it with a from-scratch oracle (full BFS depth every step, set-based) on 24 random rules x 700 steps with three bands: passes. hole_split matches a set flood fill on 4 trajectories (RL has 22 hole-boundary cells, so the hole case is non-trivial). Synthetic planted/uniform test passes.

### 2026-10-16 17:58 +13:00 · baac481 · observation

Gate-concentration calibration (examples/kappa_return_gates_calibrate.rs, 200 replicates per row, heavy-tailed exposure): the Poisson/exposure null is unbiased at all densities (|null mean| <= 0.0015, null sd 0.0005-0.020). Sensitivity to a planted gate set (every 20th bin x6) is only 2.6 null-sd at 30 bins/400 events, 4.4 at 300/1000, 30 at 4000/60000. Real runs may sit in the sparse regime, so split-seed reliability (pilot) is a genuine risk for g1.

### 2026-10-16 18:00 +13:00 · baac481 · surprise

Development smoke runs (dev seed 7, scratch only, not registered; one crust-like rule RLLLLLLLLRR, rotor, random walk to area ~139k): about 1 s per trajectory; the ant crosses the rim/interior boundary only ~200-400 times per band (B is ~1-4% of departures), so per-run heading-resolved excursion counts are far below the 200 per heading I first drafted. Decision: g2 is computed from excursion counts pooled over predictor seeds with min 50 per heading (changed from 200 BEFORE any registered-seed data). Rotor/random-walk g1 minus null is -0.04..-0.01 (obs < null), i.e. not zero for known walkers; will be reported as calibration, not corrected.

### 2026-10-16 17:51 +13:00 · baac481 · deviation

Correction (appended; earlier entries are unedited): the four entries above timed 17:55, 17:56, 17:58 and 18:00 were written between 17:30 and about 17:47 by the real clock. Those clock times were approximate and ahead of it. The order of entries is correct.

### 2026-10-16 17:52 +13:00 · baac481 · observation

Pilot (192 runs, 24 rules x 8 seeds 2026102001-08, ~90 s on 6 threads, all complete): median ~475 (band 0) / ~1080 (band 1) crossing events and ~90 / ~150 occupied bins per run; reclassification share ~1e-4; hole-boundary fraction of P has median 0 for ants (rotor 0.22-0.24, random walk 0.66-0.75). Split-half (4v4) Spearman over 24 rules: g1 0.58 / 0.67, g2 0.15 / 0.57 (bands 0 / 1), target y 0.71 / 0.59. The Spearman-Brown seed rule gives S = 64 predictor seeds; the coverage gate passes (24/24 pooled over 8 seeds). No occupation-vs-gate regression was run on pilot data.

### 2026-10-16 17:53 +13:00 · baac481 · surprise

A code-path smoke test of analyse_confirm.py on pilot rows with target rows shuffled across rules (scratch, deleted) gave DeltaR2 = +0.108 at band 1 by chance (n = 24, bootstrap CI [-0.15, 0.42]). The draft criterion (DeltaR2 >= 0.10 and bootstrap lower bound > 0) would have failed only through the bootstrap bound. A permutation test was added to the band-pass rule BEFORE any confirmation data.

### 2026-10-16 17:55 +13:00 · baac481 · decision

Registration appended to README (frozen file hashes listed there). G2 out of scope. Launching the confirmation run (64 predictor + 32 target seeds per rule, 2304 trajectories) in the background.

### 2026-10-16 18:03 +13:00 · baac481 · deviation

Timestamp correction (appended): the registration section says "frozen 17:50" and the launch entry says 17:55; by the real clock the registration was appended at about 17:48 and the first launch attempt (a `&` chain that died when `wsl` exited, no data written) was at 17:48-17:49. The confirmation run was relaunched in the foreground-background tool mode shortly after and completed. The frozen-file hashes in the README match the files at analysis time (analyse_confirm.py 36d52d1be7856854, rg_lib.py 0a22336b723db6c0).

### 2026-10-16 18:04 +13:00 · baac481 · observation

Confirmation (2304 trajectories, all complete) analysed with the frozen script. Band 0: R2(B0) 0.882, R2(B0+g1+g2) 0.842, DeltaR2 -0.039 [-0.118, +0.006], permutation p 0.85, g1 / g2 split-half 0.92 / 0.56. Band 1: R2(B0) 0.946, R2(B0+gates) 0.945, DeltaR2 -0.0004 [-0.033, +0.031], permutation p 0.060, split-half 0.93 / 0.82. Gates: band 0 reliability FAILS (g2), band 1 headroom FAILS (R2(B0) > 0.90). Verdict: UNINFORMATIVE; the criterion itself failed at both bands.

### 2026-10-16 18:05 +13:00 · baac481 · surprise

The 4-feature baseline that deliberately excludes the boundary's own occupation (d0) already reaches R2 0.88-0.95 for held-out-seed occupation; adding predictor-seed ln(occupation) as an oracle changes R2 by only +0.001 / +0.018. The depth-profile ratios (d1/rim, interior/rim) are a time-budget measurement of the same quantity, so the baseline is close to an accounting identity and leaves no headroom at band 1. I did not foresee that when choosing the baseline from the README's "depth-profile" wording.

### 2026-10-16 18:06 +13:00 · baac481 · interpretation

Gate concentration and exit-heading return spread add no predictive information beyond that baseline; this is a null at these scales for these two features, not evidence about gates as a mechanism. A cleaner re-test would use a baseline built only from quantities that precede the window (area, shape, prefix) or from independently measured mechanism features, and would need the permutation criterion.

### 2026-10-16 18:07 +13:00 · baac481 · decision

Stage 1 complete with an UNINFORMATIVE verdict; G2 stays unrun. Updated README (results), notebook.ipynb, notes/kappa-mechanisms-2026-10-15.md and notes/open-questions-hypotheses.md. Full cargo test --release passes. Nothing committed (not requested).

### 2026-10-16 18:12 +13:00 · baac481 · observation

Why two band-0 rules were excluded: g1 was NaN for them (not g2 as I first wrote in a draft). Three predictor runs with 2-6 crossing events had a zero-total Poisson null draw, so the null share is NaN and the frozen mean propagates it. Registered result untouched. Exploratory sensitivity (sensitivity_g1_nan.py) with those runs' g1 ignored: 24 rules, DeltaR2 -0.029 [-0.104, +0.016], permutation p 0.71, g2 split-half still 0.56 -> same conclusion.
