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


### 2026-10-15 23:10 +13:00 · b3a0f762ac2230b5df92188206a4d3a1081897be (dirty tree) · intent

User asked to begin this experiment. Scope for this session (HANDOFF): build and calibrate the exposure/launch instrument, resolve the draft choices, pilot for cost and replicate noise on development bases only, append a frozen registration. No validation-base mutant is simulated before the registration, and no confirmation run is launched in this session. Existing uncommitted work (including `src/field_age.rs`, another scope's untested code) is left alone; the new instrument does not use it.

### 2026-10-15 23:10 +13:00 · b3a0f762ac2230b5df92188206a4d3a1081897be · assumption

(1) Exposure of colour j is close to collinear with letter position j: a blank-start cell reads colour j only on visits j mod n, so per-cell reads of j fall with j. Only the 25 radius-2 patch cells escape that. So P2's "exposure beats position" is likely unidentifiable on total counts; what can differ is where colour j is read (boundary / depth share) and the launch kernel. Checked on the development pilot before P2 is frozen.
(2) Predictors must come from the base run or from seed-disjoint mutant runs, not from the trajectory whose B/S is the target (circularity noted in the mechanism note).
(3) The sibling scaffolds share this PLAN template and propose the same seed namespace 2026101501..; this experiment will use its own (13-digit) namespace.

### 2026-10-15 23:50 +13:00 · b3a0f762ac2230b5df92188206a4d3a1081897be (dirty tree) · observation

Instrument built: `src/prefix_exposure.rs` (producer `drive` + pure `Accountant`), `tests/prefix_exposure.rs`, runner `examples/kappa_prefix_exposure_sampler.rs`. It does not use `src/field_age.rs`. `src/lib.rs` gained `pub mod prefix_exposure;` next to the other scope's uncommitted `field_age` line. `cargo test --release --test prefix_exposure`: 11 tests pass (WSL, `CARGO_TARGET_DIR=~/turmite-target`). What they check:
- producer vs a HashMap oracle that recomputes every field, with a full multi-source BFS for depth at every step (160 proptest cases, rules of 2..14 colours, random seeds);
- accountant vs an independent offline implementation of bands and launch windows (160 cases, two bands, w = 1..9), plus a hand-worked stream and a censoring case;
- boundary stream vs `fixed_area::run` (b_dep, i_dep, band times and areas agree);
- depth known-answer on a filled 11x11 block (analytic distance to the edge, no BFS);
- controls: unchanged clones agree exactly; base and mutant agree through the state of the base's first read of the altered colour and differ at the next (200 cases); joint cyclic relabelling of rule and every field colour reproduces trajectories (100 cases); rotor and random-walk runs obey the invariants.
Power check on the depth map: update radius 5 disagrees with the oracle in 0 of 120 cases, radius 4 in 99, radius 3 in 107, so 5 is tight and the test would catch a too-small ball. The rotor/random-walk runs only check invariants; no known-answer calibration of the launch statistics on those walkers exists (none is analytic), so launch numbers are uncalibrated against any independent known quantity beyond the oracle agreement.
One spec costs ~0.7 s (RLLLLLLLLRLLR@2026101570001, bands 32768-34816 and 131072-139264, grid 4096, t = 5.6e5): compute is not a constraint at this design size. This rule has B/S = 0.70 in band 1, so it is an unusual base; flagged, not yet interpreted.

### 2026-10-16 00:20 +13:00 · 07a0951e22aba7e4e0d2a2c99bf8382a54235da0 (dirty tree) · observation

Cohort selected (`scripts/select_cohort.py` -> `results/cohort.csv`, `arms.csv`, `selection_manifest.json`). Source of labels: the W3c per-rule recipe (core band, >= 6 runs, |median g_k| < 0.05) recomputed from the gitignored `kappa-rule-space/dumps/w3c_probe.csv` (sha256 in the manifest); it reproduces W3c's counts (176 usable rules, 162 stationary, 14 nonstationary). 24 bases of length 13-14: 12 development, 12 validation, each side 10 stationary + 2 nonstationary, no quota shortfall. Families are the first five letters; development and validation families are disjoint (8 vs 8), so validation tests unseen 5-letter prefixes. Mutants of a validation base at positions 1-4 can still land in a development family; that is not controlled. Seed namespace 2026101570001.. (pilot) and 2026101571001.. (confirmation) appears nowhere else in the repo (audit in the manifest); the sibling scaffolds' proposed 2026101501.. namespace was NOT used. One arm rule, LLLRLLLLLLRLLL (position-0 anchor of a validation base), is non-primitive (period 7); it is simulated as written with 14 colours.

### 2026-10-16 00:20 +13:00 · 07a0951e22aba7e4e0d2a2c99bf8382a54235da0 (dirty tree) · observation

Pilot v1 (288 specs, development bases only, seeds 2026101570001..04, `sampler dumps/pilot 536870912 4096 64 32768-34816,131072-139264`, kept as `results/pilot_*_v1.*` and `dumps/pilot_v1`). Its launch statistic was Pr(an interior episode of >= 64 states begins within 64 steps of a fresh cell): 0.38 per discovery, with `left` = 1.000. Both are artefacts: consecutive fresh cells share one episode, so windows overlap and the same episode is counted for many discoveries; `left` is trivially 1 because the ant leaves the boundary within 64 steps of every discovery.

### 2026-10-16 00:20 +13:00 · 07a0951e22aba7e4e0d2a2c99bf8382a54235da0 (dirty tree) · deviation

README item 3 said to record "whether an interior episode lasts >=64 steps" after each fresh cell and treat overlapping records as correlated. Before registering, the primary kernel statistic is changed to a non-overlapping one: episodes (maximal interior runs) that begin in the band and last >= w states, per discovered cell, Lam_w, for w in {16, 64, 256, 1024}, plus tau_w = share of band time spent in episodes of >= w states. The per-discovery windows are kept as a secondary (forward/lateral displacement after 64 steps). Instrument extended and re-tested (11 tests pass, including an offline episode oracle and the identity tail_steps(w=1) = i_dep). Primary w = 256: episodes of >= 64 are only ~7% of discoveries yet carry 94-98% of band time, so 64 is not a rare-trap threshold, while 1024 leaves a few thousand events per arm; the pilot's association with the change in B/S rose with w (Spearman of d ln Lam_w with d ln B/S in band 0: -0.13, -0.22, -0.37, -0.52 for w = 16, 64, 256, 1024), so w = 256 is a compromise chosen on development-pilot data and 64 and 1024 are registered as secondaries. This choice used the development pilot, which is not a test. Pilot v2 (same specs, extended instrument) replaced v1 for all further analysis.

### 2026-10-16 00:20 +13:00 · 07a0951e22aba7e4e0d2a2c99bf8382a54235da0 (dirty tree) · observation

Pilot v2 results (`results/pilot_stats.txt`, `pilot_pairs.csv`; 288 specs, 2.1 s median / 3.3 s mean per spec, 962 CPU-s). 252 complete, 16 hit the 2^29 cap, 20 escaped. Valid (band reached, no short open episode) fraction by arm: base 1.00, late mutants 0.95/0.92 (bands 0/1), early 0.80/0.75, position-0 0.96/0.92: early mutants fail to attain more often. Base-arm pooled B/S 0.0216 and 0.0077, kappa_end 0.86 and 0.59 (census-like). Time budget: episodes lasting >= 1024 states are 1.5% of discoveries and 82-94% of band time. Between-seed sd of ln(B/S) within a rule: 0.53 (band 0), 0.65 (band 1); sd of the half-difference of two disjoint 2-seed means 0.56 and 0.55, consistent with iid seeds. So the paired effect of 4 seeds per side has se ~0.46: the pilot's median |d ln B/S| (early 0.41-0.54, late 0.26-0.29) is largely noise (late is at or below the null median 0.31 for band 1). With 32 target seeds per arm se falls to 0.13 (band 0) / 0.16 (band 1). Exposure: the share of reads of a colour is ~1/n for every colour (ln share -2.4..-2.7), so total exposure carries almost no information beyond n; what varies is where the colour is read: boundary share of reads (Spearman with position -0.92, R^2 0.35) and mean depth class of reads (R^2 on position 0.33-0.44; 53-56% of early values lie in the late range). Exposure is strongly but not wholly collinear with position, as the advisor-style prior suggested; P2 is identifiable only if the overlap gate in the registration is met on the confirmation data.

### 2026-10-16 00:20 +13:00 · 07a0951e22aba7e4e0d2a2c99bf8382a54235da0 (dirty tree) · decision

Seeds per (base, arm) raised from the README's draft 16 to 64 (32 prediction + 32 target): the pilot noise requires it, and cost permits it (9216 confirmation specs ~ 8.5 CPU-hours at the pilot's 3.3 s mean). Position 0 is excluded from the early pool (README draft said indices 0..7): it is read at every fresh cell and flipping it mirrors the rest of the rule; it is run as a separate descriptive anchor. Predictors come from the base run or from seed-disjoint runs (prediction seeds), never from the target seeds. Mutants are not canonicalised.

### 2026-10-16 00:20 +13:00 · 07a0951e22aba7e4e0d2a2c99bf8382a54235da0 (dirty tree) · observation

Reproducibility checks on the sampler (24 pilot specs): output of a 1-thread uninterrupted run is byte-identical to a run started with 3 threads on 10 specs and resumed with 6 threads (10 specs skipped via `.done`), 144 files compared, and also identical to the corresponding files of the 6-thread pilot run. The scripts' dry run of `confirm_analyse.py` on pilot data (2 prediction + 2 target seeds, validation replaced by development, stdout only, nothing saved) exercised every code path without error; its numbers are mechanics, not results.

### 2026-10-16 01:15 +13:00 · 997c9b2da6efa526fc6c5a57104d103e1345e916 (dirty tree) · decision

Arms revised after the concurrent W6 matched-area reanalysis (3d00123): positions 1 and 2 for every base, one mid (3..7), two late, position-0 anchor; pilot v2 (old arms) superseded by pilot v3 (336 specs; sd of ln B/S 0.533/0.700 frozen as S_POOL). Registration appended to README, hashes in results/registration_hashes.txt, handover in HANDOVER.md. Full release test suite ran with no failures in the log. No confirmation run done; session ended here at the user's request.

### 2026-10-16 00:06 +13:00 · 997c9b2da6efa526fc6c5a57104d103e1345e916 (dirty tree) · intent

Session resumed to continue the experiment. Found the registered confirmation already running (`scripts/run_confirm.sh`, launched 00:03:33, 3 threads, dev then val chained; ~220 of 5376 dev specs done at 00:05). Nothing to change: no code or registration edits. Plan: wait for `results/confirm_run.finished`, then run `confirm_analyse.py` once, check gates in order (G1, G2, G3), and report all P1-P5 outcomes in the README, this notebook and notebook.ipynb, whatever they are.


### 2026-10-16 00:00 +13:00 · 997c9b2da6efa526fc6c5a57104d103e1345e916 (dirty tree) · intent

Session goal: take the experiment from pilot to its confirmation run, with at most 3 threads (other agents share the machine). README had no frozen registration despite the v2 notebook entries saying predictions would be frozen (confirm_analyse.py cites a README "Registration" that did not exist). So the first step is to register, before any confirmation spec runs.

### 2026-10-16 00:08 +13:00 · 997c9b2da6efa526fc6c5a57104d103e1345e916 (dirty tree) · decision

Registration appended to README (P1, P2, P3 position gradient, P4 descriptive, P5 sign-mixed kappa from W6m; gates G1-G3; seeds, hashes, commands). Corrections to the earlier notebook: the actual spec count is 10752 (7 arms including the position-0 anchor x 24 bases x 64 seeds), not 9216; at the pilot's mean 3.3 s this is about 9.9 CPU-hours. Pilot stats for the final arm set were not regenerated (dumps/pilot is 259/336 specs complete; the quoted pilot numbers are from the old-arms run, pos 0 included in the early pool). I added to confirm_analyse.py: a requirement that the development slope of y on x_lnLam256 be negative for the P1 verdict, and the P5 block. Another process edited the same script at 00:03:06 (added P3 and P4 blocks); I adopted these and registered them in an addendum, because no outcome had been read. Launch at 00:03:33 preceded the 00:05 stamp in the README by about a minute; flagged in the addendum.

### 2026-10-16 00:10 +13:00 · 997c9b2da6efa526fc6c5a57104d103e1345e916 (dirty tree) · observation

Confirmation running: `scripts/run_confirm.sh` (3 rayon threads, dev specs then val specs, logs results/confirm_run_{dev,val}.log, finish marker results/confirm_run.finished). After ~3 min 254 dev specs were done. Machine load average was already about 3-6 from other agents, so expect it slower than the pilot.

### 2026-10-16 · 997c9b2da6efa526fc6c5a57104d103e1345e916 (dirty tree) · observation (design review; no confirmation outcome read)

External stat-phys design review (read-only, run while the confirmation was in progress, `dev` side ~1000/5376 specs; no outcomes read). The reviewer's claims were not independently verified except where noted. Findings, ranked:
1. P2 as coded (`confirm_analyse.py` ~L149-168) regresses SIGNED `y_lnbs` on unsigned features (lead/mid dummies, mean depth, ln boundary share). With the sign-mixed effects the registration itself expects (P4/P5), both models should score held-out R^2 near or below 0, so delta-R^2 >= 0.10 is close to unreachable by construction. A P2 "fail" therefore does NOT support rejecting the exposure account; read it as uninformative-by-design. (I confirmed the code regresses signed y; the consequence is the reviewer's inference.)
2. P1: Lam_w ~ 1.06 x Pr(T >= w) (pilot: ~1.06 episodes per discovered cell), so Y~X is partly rule-level accounting (a duration-scale change moves X without a launch-rate change). A P1 pass is predictive, not evidence of a launch mechanism. The pilot's rise of association with w (-0.13 -> -0.52) is what a scale change would also produce.
3. P1 power is limited by the ~10 stationary bases per side: reviewer's ceiling R^2 <= ~0.68 rho^2, needing true rho >~ 0.53 against a pilot ~0.45 (disattenuated); G2 is a weak gate (expected ~0.75). Type I risk negligible.
4. Survivorship differs by arm (valid 0.83-0.86 early/mid vs 0.92 late); dropped runs (cap hits, open episodes) are the long-excursion ones.
5. Estimator details: resolution threshold may be lenient for pairs with 16-31 valid runs; sign agreement leans on the dev intercept when X is small; R^2 is against the dev mean; P3's denominator is near pure noise so the ratio mostly measures lead signal over noise; a percentile bootstrap over ~10 bases under-covers.
6. Provenance (checked by me): README has two Registration sections that disagree (S_POOL 0.528/0.649 vs 0.533/0.700; the code uses 0.533/0.700; confidence 30% vs 45%; P5 defined in both). The registered script hash 971f6570... (first section) differs from `confirm_run.json`/`registration_hashes.txt` 458c8eaf..., and the script on disk now hashes to fcae4442... i.e. it was edited again AFTER launch. The 458c8eaf version no longer exists on disk, so I cannot diff it; the README addendum says the later edit was a P5 rename only, which I cannot verify. Governing statement: the analysis is the on-disk script at run time; its hash will be written to `confirm_analysis.json`; any difference in numbers from the pre-run version is unresolved.

decision: no change to the registered analysis, the running job or the specs. Added `scripts/confirm_exploratory.py` (unregistered; E1 P2 on |Y| and with flip direction, E2 Lam association across w, E3 survivorship, E4 empirical noise vs S_POOL, E5 sign/R^2 variants and band-0 P1, E6 noise-corrected P3), to be run only after `confirm_analyse.py` and reported in a section labelled exploratory. Mechanics tested on synthetic pairs (scratch/, gitignored) only. Follow-ups for a new experiment, not this one: >= 30 bases, a rule-only prediction of Lam change, a survival model separating launch amplitude from duration scale, an intervention that changes the fresh-cell kernel without flipping a letter.


### 2026-10-16 03:49 +13:00 · 269288eb62bf6b6ec125a3b420dd899057858be5 (dirty tree) · observation

Confirmation finished (10752 specs, 3 threads, about 3.7 h wall with other agents sharing the machine; no resume was needed, `.done` for all). Registered analysis run: P1 FAILED (held-out R^2 0.105 vs 0.20, CI [-0.21, 0.32], 20 resolved, agreement 75%); P2 FAILED on its interval bar (delta R^2 +0.215, CI [-0.002, 0.281]); P3 HELD (ratio 9.0, CI [1.27, 27.6]); P4 6/11 positive; P5 HELD (share positive 0.47, mean -0.11 vs median abs 0.33). Gates: 10 informative validation bases, reliability Spearman 0.97, P2 identifiable. Stops: dev 192 cap / 321 escaped, val 497 cap / 323 escaped.

### 2026-10-16 03:55 +13:00 · 269288eb62bf6b6ec125a3b420dd899057858be5 (dirty tree) · interpretation

The position effect is real and sign-mixed on fresh mutants; the launch-rate (Lam_256) account of it is not supported at the bar, and the exposure-vs-position question is inconclusive (point estimate favours exposure, interval touches 0 with 10 bases). Selection caveat: late validation mutants hit the cap more often (valid 0.73 vs dev 0.93) so attained late pairs may be biased towards easy cases. The sign of the Lam slope is negative as the pilot suggested, but weak.

### 2026-10-16 03:55 +13:00 · 269288eb62bf6b6ec125a3b420dd899057858be5 (dirty tree) · deviation

(1) The analysis script's hash at analysis time (fcae4442...) differs from the one in confirm_run.json (458c8eaf...) and from my P5 rename; the file was touched by another process during the run. I did not diff it against the registered logic beyond reading the P1-P5 blocks, which match the README. (2) Launch preceded the stated registration stamp by about a minute (addendum). (3) Pilot stats for the final arm set were never regenerated. notebook.ipynb updated and executed from a clean kernel; it reads results/confirm_analysis.json only.
