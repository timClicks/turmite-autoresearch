# Lab notebook: boundary excursion-duration collapse (stage 1)

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation.

### 2026-10-27 20:30 NZDT · 5b96f68 · intent
Stage-1 experiment for P-C / Q32 (diffusive vs sweep excursion-duration collapse)
from `notes/cube-root-routes-2026-10-26.md` on PR #18. Bias to prior work: reuse
probe boundary definition, exposure-classes check-mode style, first-passage's
calibrator list (mf / rotor / rw), and T1's excursion episode definition; avoid
the failed parametric (theta, z) tail fit (C6). Register definitions, scores and
stop gates before any measurement. No confirmation in this experiment.

### 2026-10-27 20:30 NZDT · 5b96f68 · decision
Pruning preflight at index revision `5b96f680ba25ff898fc5ed91d2c33a43d6713233`.
Queries: `rg -n -i -e 'return|excursion|tail|first-passage|boundary|kappa' notes/pruning-index/entries`
plus full read of the three entry titles/claims. Candidates:
`NR-20261022-additive-laws-order-blind`, `NR-20261025-kappa-exposure-classes-exposed-edge`,
`NR-20261025-crawler-window-single-letter` — all different objectives/observables.
Decision: **RUN**. Budget: < 2 CPU-hours, board 8192, max_log2 24, 4 threads.
Stop if C1 (rw→D) or C2 (mf→L-scaling) fails.

### 2026-10-27 20:30 NZDT · 5b96f68 · assumption
Window-end L = A/P is an adequate scale for octave-window collapse at stage 1
(quasi-static within a window). False if within-window L drift, or completion-window
attribution of long excursions, destroys RW's L^2 collapse under the frozen score.
Status: untested (calibration will test).

### 2026-10-27 20:30 NZDT · 5b96f68 · assumption
Mean-field interior sojourns behave as approximately geometric with mean ~ L, so
Score(L) beats Score(L^2) by the 0.75 margin. False if MF's neighbour-step
correlation or growing P/A within a window breaks L-collapse at these sizes.
Status: untested.

### 2026-10-27 20:31 NZDT · 5b96f68 · question
Does the rotor's excursion-duration shape prefer L or L^2 collapse at accessible
sizes, or neither? P-C left this as a measured calibrator; T1 and FLP/Bou-Rabee
arguments suggest sweep-like structure, but that is not registered here.

### 2026-10-27 20:45 NZDT · 9bfa496 · decision
Instrument `examples/boundary_excursions.rs` written (probe-aligned Region,
evolving boundary, completion-window attribution, log2 duration bins, right-censored
open excursions). `--check` matches `probe::probe_walker` on rw/rotor/patched;
`--mutant` inverts `on_boundary` and panics under `--check` (C0). Mean-field uses
the exposure-classes `MeanFieldSync` (uniform resample of visited cells, then a
random neighbour). Tiny non-cohort smoke (grid 256, max_log2 12, seeds 7) green
before the long calibration.

### 2026-10-27 20:46 NZDT · 9bfa496 · observation
C0 smoke on `rw:7` / `rotor:7` (256 board, max_log2 12): check exit 0. Mutant
on `rw:7` panicked at window k=9 with boundary_steps mismatch (probe 133 vs
mutant 123) as required. Starting calibration under frozen specs
(`results/calib_specs.txt`), board 8192, max_log2 24, RAYON_NUM_THREADS=4,
binary sha256 d16f6e6870320e07536e1b7edfb571607dd938747a4942d228276d799ae00a92.

### 2026-10-27 20:55 NZDT · 9bfa496 · observation
Calibration complete under `--check` (12 specs, board 8192, max_log2 24). C0 PASS.
C2 PASS: mf Score(L)=0.0580 < 0.75·Score(L²)=0.1221, verdict S; mean τ/L=1.010.
C3: rotor inconclusive (Score L 0.120 vs L² 0.146). C1 FAIL: rw retained windows = 0
because L=A/P stays ~2.55–3.83 across k=16..24 (never reaches L≥4; range <2×). Instrument
inadequate — STOP. Synthetic pure-scale Score check still separates D from S, so the
statistic is fine; the RW-on-own-range calibrator is the wrong family for L=A/P.

### 2026-10-27 20:56 NZDT · 9bfa496 · observation
Excluded pilot ran (8 rule@seed, `--check`). Descriptive only under STOP: pooled frozen
Score would prefer D; not evidence. Trajectories remain excluded.

### 2026-10-27 20:57 NZDT · 9bfa496 · decision
**Revise** (not retain, not abandon). Keep definitions, MF control, Score, check-mode,
excluded-pilot discipline. Replace D calibrator with a compact-domain growing walker;
re-register C1 before any confirmation. Recorded in README Results and blog post.

### 2026-10-27 20:50 NZDT · c2b3c39 · intent
Revision 1 after user approval of the stage-1 **Revise** recommendation
(`Work on your fix`). Keep original registration, C1 FAIL, and excluded pilot on
record. Replace the D calibrator; re-freeze Score only by carrying the stage-1
margin forward; gate confirmation on C0∧C1'∧C2.

### 2026-10-27 20:50 NZDT · c2b3c39 · decision
Walker search: no reflecting/cup/IDLA/sticky compact-domain walker in
`src/walkers.rs` or prior experiments; cookies, edge-reinforcement, persistent,
and memoryless/noisy-rotor controls all expand freely (same failure mode as RW
for L=A/P). Implement reflecting-cup mover in `examples/boundary_excursions.rs`.
Pruning: still **RUN** (new calibrator, same question; no new NR signature that
covers cup excursion collapse). Primary P=0.10; diagnostics 0.05 and 0.25 chosen
for compactness only, before outcomes.

### 2026-10-27 20:50 NZDT · c2b3c39 · assumption
A reflecting cup with stay-on-reject and small P produces a compact blob with
growing L=A/P and a diffusive interior sojourn law (D). False if frontier
rejection traps the walker on the boundary hard enough that Score prefers S
(registered as C1' inconclusive, not as evidence for sweep). Status: untested.

### 2026-10-27 20:50 NZDT · c2b3c39 · decision
Confirmation family rule frozen: ≥75% of eligible reserved rules sharing D (or
S) to retain that account; otherwise revise. Development cohort remains excluded.
No confirmation run unless C0, C1' (cup:0.10→D + compactness), and C2 (mf→S with
mean τ/L in band) all pass under the unchanged 0.75 Score margin.

### 2026-10-27 21:05 NZDT · 9c2aeea · observation
Revision-1 instrument: `ReflectingCup` in `examples/boundary_excursions.rs` (stay-on-reject).
C0: `cup:1.0:7` ≡ `rw:7` under `--check`. Binary sha256 c84e20780315f4cc….
Rev1 calib (20 specs, board 8192, max_log2 24) complete; see `results/rev1_calib_outer.log`.

### 2026-10-27 21:06 NZDT · 9c2aeea · observation
C1' INADEQUATE. Primary cup:0.10: L grows (range ≈6.47×; A range ≈56×) but median A/P² ≈0.0188 < 0.04; Score prefers S (0.103 vs 0.169). Diagnostics p=0.05/0.25 also S and fail compactness. C2 PASS (mf mean τ/L≈0.998). Rotor inconclusive. Confirmation not run.

### 2026-10-27 21:07 NZDT · 9c2aeea · interpretation
The cup fixed stage-1's "L never grows" failure but hit the registered trapping/compactness risk: frontier rejection keeps the walker near the edge (S-like Score) and the blob stays porous (A/P²). Not evidence about ants. Retire this cup-as-D design; do not P-shop.

### 2026-10-27 21:07 NZDT · 9c2aeea · decision
**Stop** confirmation. Pruning-index NR for reflecting-cup D calibrator. Next compact-domain candidate must be re-registered (visited-neighbour reflection, Eden, or IDLA) before any measurement.

### 2026-10-28 15:50 NZDT · e40df03 · intent
Revision 2 at the user's request ("Can we explore eden style and internal dla?").
Two new D calibrators, frozen before measuring: C1E `eden` (neighbour-supported
births, `q1 = 1/64` fallback for straight edges) and C1I `idla` (origin restarts
counted as ordinary excursions). Same Score, margin and compactness rule. The
earlier registration, the Revision 1 cup verdict and the excluded pilot stay
unchanged.

### 2026-10-28 15:50 NZDT · e40df03 · decision
Pruning preflight (`eden|idla|internal|aggregation|compact`): the only related
entry, the reflecting-cup NR, defers Eden and IDLA to a new registration.
Nothing covers them. **RUN.**

### 2026-10-28 15:50 NZDT · e40df03 · assumption
IDLA's centre-launched excursions scale as L², so C1I should prefer D. This
tests whether the instrument can see diffusion. It does not test likeness to
the ant (IDLA width ~ t^(1/4)). For Eden, D is predicted, but the
L-independent short head of boundary-launched excursions may push the Score
toward S or inconclusive. If so, that is an instrument finding. Status:
untested.

### 2026-10-28 15:50 NZDT · e40df03 · decision
Gate: confirmation runs only if C0 ∧ C2 ∧ (C1E PASS ∨ C1I PASS). The
confirmation readout is interpreted relative to the passing calibrator(s).
Otherwise stop. `idlar` (restart excursions dropped) is a diagnostic only.

### 2026-10-28 15:50 NZDT · 1da42bd · observation
Revision 2 calibration (20 specs, about 2 s wall, binary `9f282ce…`). C0 PASS: the scan recount, birth invariants and idla≡idlar geometry all held, and the mutant panicked. Both walkers are compact. Eden: L range 7.34, median A/P² 0.065. IDLA: L range 4.01, median A/P² 0.071. Neither prefers D:

- Eden: Score L 0.102 vs L² 0.161, so **S**.
- IDLA: Score L 0.067 vs L² 0.077, so **inconclusive**.
- Neither verdict is censoring-fragile.
- Diagnostic `idlar`: S (0.085 / 0.128).
- C2 mf: S (0.055 / 0.149), PASS.
- C3 rotor: inconclusive (0.113 / 0.135).

Post hoc, exploratory: the IDLA long tail overlies better under τ/L², but the number-weighted Score is dominated by the shared short head.

### 2026-10-28 15:50 NZDT · 1da42bd · interpretation
Compactness is no longer the problem. Short boundary returns have an L-independent head in every compact walker tried, and the frozen Score is number-weighted. So it reads S or inconclusive even where diffusion is built in (IDLA restarts). This is an instrument limitation. It says nothing about whether ant excursions are diffusive or sweep-like.

### 2026-10-28 15:50 NZDT · 1da42bd · decision
Gate FAIL (no calibrator PASS), so **stop**. The reserved confirmation cohort was not run. Retire Eden-style (q1 = 1/64) and IDLA as D calibrators for this Score (`NR-20261028-excursion-score-compact-d-calibrators`). A different observable, for example tail-restricted or step-weighted collapse, needs its own registration and calibration on these walkers before any ant data.

### 2026-10-28 15:50 NZDT · 1da42bd · deviation
1. The walker code and `scripts/run_rev2.sh` were written after registration `900f25f` and committed with the results in `1da42bd`, not before measuring. The definitions, seeds, Score, margin, compactness rule and gate were all frozen in `900f25f`. The binary hash is in the outer log, and the committed source rebuilds to it.
2. The registration heading says 15:50 NZDT, but Git records the registration commit at 15:46 and the results commit at 15:49 (+13:00). The commit order, registration before results, is the authoritative ordering. The earlier text is left unchanged.

### 2026-10-28 16:30 NZDT · 6e54ba4 · decision
Moved from `experiments/2026-10-27-boundary-excursion-durations/` to
`experiments/active/2026-10-boundary-excursion-durations/` to follow the bucket layout that main adopted
in PR #24 (merged into this branch at `6e54ba4`). The move used `experiments/_migration/relocate.py` with the
one-row map `experiments/_migration/2026-10-28-boundary-excursion-durations.tsv`. Bucket `active`, because
this experiment is the current `notes/ACTIVE.md` pointer, PR #20 is still under review, the reserved
confirmation cohort is unopened, and the next step (a separately registered tail-restricted or step-weighted
statistic) would be registered here. That matches the README's definition of active ("open work"); `archive`
("concluded or paused") would fit if that next step is dropped.

The rewrite changed path strings only, following PR #24's convention, including in earlier entries of this
NOTEBOOK, the NR entries and `notes/`. It did not change wording, results or data. Generated run records keep the
old path, because the relocation script does not touch generated data: the `results/*.log` files and
`results/sha256sums.txt`. Translate them with the map. Registrations and other
records that cite a commit (`9bfa496`, `9c2aeea`, `900f25f`, `1da42bd`, `ea42524`) refer to the old path as it
existed at that commit. The slug drops the day (`2026-10-27-` → `2026-10-`), and the blog redirects the old
page URL. The only hand fix was a relative link in the README's stage-1 header to
`notes/cube-root-routes-2026-10-26.md`, recomputed for the new depth. That file lives on PR #18 and is absent
from this branch, so the rewriter skipped it. The scripts' `ROOT` now climbs four levels.
`examples/boundary_excursions.rs` changed only in a `//!` doc comment.

### 2026-10-28 16:35 NZDT · e0e657a · observation
1. After the merge, the instrument binary built from this tree hashes to
`cfa9c7d4fc339e359f34dddc7bad4f23949e062a65e3d45ef95393e272b34e62`, not the `9f282ce…` recorded in the Rev2 outer
log. Sources at `d8ca95f` still rebuild to exactly `9f282ce…`. Main's `src/` changes alone give `d6f64cb…`
(comment-only for this binary), and the `//!` path change in the example gives `cfa9c7d…`. So the difference
comes from source text and build metadata, not code. Rerunning the Rev2 calibration at the registered settings
with the new binary, in a scratch worktree, gave byte-identical `rev2_calib_windows.csv` and `rev2_calib_hist.csv`, and
`analyse.py rev2` gave byte-identical `rev2_analysis.json` and `.txt`. The committed results were not touched.
2. Deviation: the headings of the 16:30 move entry above and the 16:40 ledger re-pin entry in
`experiments/archive/2026-10-evidence-ledger/NOTEBOOK.md` are later than the commits that carry them. Git records `581f203` at 16:29:00
and `e0e657a` at 16:29:38 (+13:00). The commit times are authoritative, and the headings are left unchanged.

### 2026-10-28 16:50 NZDT · 570f207 · plan
**Post hoc, exploratory. This is not a gate and not a registration of a new statistic.** The question is how much of the
excursion count and how much of the off-boundary time short excursions contribute in the existing Rev2 calibration data.
No new runs, and no ant or pilot data.
- **Data:** `results/rev2_calib_windows.csv` and `results/rev2_calib_hist.csv`. Kinds `eden`, `idla`, `mf`, `rotor`, pooling 4 seeds each.
  The windows are those that `analyse.py` retains for the Score: k 16..24, not escaped, n_completed ≥ 200,
  censored_step_share ≤ 0.20, L ≥ 4.
- **Cutoff, fixed before computing: "short" means τ ≤ 3**, which is log2 bins 0 and 1. That is the smallest cutoff the
  log2 histogram resolves exactly; it cannot split at τ ≤ 4. τ ≤ 7 (bins 0–2) is reported alongside as a sensitivity line only.
- **Count share:** short completed excursions ÷ all completed excursions. This is exact.
- **Time share:** short-excursion steps ÷ the window's `interior_steps`, summed over retained windows. The denominator is exact.
  The numerator is bracketed by bin edges (bin 0 = 1 step; bin 1 = 2–3 steps). A second bracket uses completed-excursion
  time from bin edges as the denominator.
- **Prior guess on record (unverified, told to the user):** "nearly half of excursions, a sliver of time". The numbers will be reported against it as they come out.
- Script `scripts/short_share.py` writes `results/rev2_short_share.{json,txt}`.

### 2026-10-28 16:58 NZDT · f466101 · observation
**Post hoc and exploratory**, as planned in the 16:50 entry. Source: `results/rev2_short_share.txt` (from `scripts/short_share.py`).
Short means τ ≤ 3. Time is given as a bracket from the bin edges, with the window's interior steps as the denominator.

| kind | share of completed excursions | share of off-boundary time |
|---|---|---|
| eden | 0.520 | 0.0067–0.0085 |
| idla | 0.339 | 0.0006–0.0007 |
| mf | 0.076 | 0.0028–0.0039 |
| rotor | 0.728 | 0.0123–0.0154 |

The τ ≤ 7 sensitivity line gives 0.66, 0.41, 0.17 and 0.85 of the counts, with every time share below 0.026.

**Guess on record:** "nearly half of excursions, a sliver of time".
- **Eden:** the guess held. Just over half of the excursions, under 1% of the time.
- **IDLA:** about a third of the excursions, roughly 0.1% of the time.
- **Rotor:** larger than guessed. About three quarters of the excursions, but still under 2% of the time.
- **Mean-field:** the guess does not apply. Only about 8% of its excursions are short.

The "sliver of time" half held for every kind. These numbers fit the Rev2 registration's stated worry: a number-weighted Score is dominated by a short head that does not move with L. They do not test it. Nothing is registered by this entry.

### 2026-10-28 16:39 NZDT · e726ae1 · deviation
The three entries above have headings ahead of the box clock. Their commits are authoritative:
- the 16:35 observation is in `570f207` at 16:33:58;
- the 16:50 plan is in `f466101` at 16:36:01;
- the 16:58 observation is in `e726ae1` at 16:37:03 (+13:00).

The order still holds: the plan and cutoff were committed before `short_share.py` was first run. The headings are left unchanged.

### 2026-10-29 09:17 NZDT · 9701882 · decision
Pruning preflight for Revision 3 (time-weighted survival; synthetic + eden/idla/idlar/mf/rotor calibration, board 8192,
max_log2 24, band k 16..24), index revision `970188200819dd17cc6c60c3cb2816bb26f1cafe`. Query:
`rg -n -i -e "time-weighted|time weighted|step-weighted|tail-restricted|size-biased|excursion|eden|idla|synthetic|gambler" notes/pruning-index/entries`.
Candidates: `NR-20261028-excursion-score-compact-d-calibrators` (read in full) and `NR-20261027-reflecting-cup-d-calibrator`.
The first excludes eden/idla only as D calibrators *for the number-weighted Score*, and lists time-weighted /
tail-restricted statistics under "not permitted" to exclude. Its discriminating next test is exactly a new
weighted statistic that must prefer D on idla while mf prefers L. The cup entry is a different walker.
Decision: **RUN** under a new observable (any negative gets a new ID, the old entry is not reopened). Budget < 15 CPU-min.

### 2026-10-29 09:17 NZDT · 9701882 · intent
Revision 3 (calibration only). Register a time-weighted (size-biased) survival collapse Score_tw, with the same pairwise
Score, margin 0.75, grid, and Rev2 retention plus n_eff ≥ 30. Freeze a G1 synthetic gate with laws known D/S by
construction (gambler's ruin with M ∝ L vs M ∝ √L, heavy short heads, geometric) before trusting walkers whose
D status is only theoretical (Eden interior = exact SRW; IDLA restart exits ~R²). Fresh seeds 2026102951..54
(walkers) and SeedSequence(2026102971) (synthetic); both grepped unused at `9701882`. No ant data today.
Tail-restricted survival was considered and rejected a priori (fixed τ0 leaves the L-independent head; cL is not
a D scaling; cL² is circular). Full rules: README "Revision 3 registration".

### 2026-10-29 09:17 NZDT · 9701882 · observation
Documentation discrepancy, found while freezing Rev3: `analyse.py` comments `U_GRID` as "1/256 .. 16" and the
stage-1 README / NR entry repeat 2^-8..16. The code `2**(-8 + j/2), j=0..32` spans 1/256..**256**. All past Scores
used the code's grid, so no result changes. Rev3 freezes the grid explicitly as 1/256..256.

### 2026-10-29 09:17 NZDT · 9701882 · assumption
Eden's quasi-static domain and boundary regularity at L ≈ 7–50 are close enough to asymptotics for SRW hitting
times to give D under Score_tw. False if C1E-tw is S/inconclusive while G1 passes. Status: untested.

### 2026-10-29 09:21 NZDT · 3d87d8b · observation
G0 instrument (no calibration data yet). `examples/boundary_excursions.rs` gains `--fhist` (8 sub-bins/octave,
count + sum_tau), `--check` fine self-check and per-window consistency, and a new `--fine-mutant` (files τ into f^1).
Smoke (7 specs seed 7, max_log2 14, grid 512): windows and `--hist` output **byte-identical** to the binary
built from `9701882`; `--check` exit 0; `--mutant` and `--fine-mutant` both panic (exit 101). Python `tw_score.fine_range`
matches the Rust lo/hi on every fhist row. Detail: `results/rev3_g0.txt`. rustfmt was applied to the new code
only (the file was not rustfmt-clean before; unrelated hunks were reverted).
`cargo test --release --locked`: 227 passed, 0 failed.
Scripts: `tw_score.py` (shared Score_tw), `synth_rev3.py` (G1), `analyse_rev3.py` (walkers), `run_rev3.sh`.
`tw_score.number_weighted_score` reproduces the frozen `analyse.py` number-weighted Score exactly on a toy input.
The registration heading says 09:17; the commit `3d87d8b` is stamped 09:16:57 +13:00 (heading 3 s ahead of the clock; order unaffected).

### 2026-10-29 09:22 NZDT · a8a93b1 · observation
G1 synthetic gate **PASS** (`results/rev3_synth.txt`): SD, SD2 → D 20/20; SG, SS1, SS2 → S 20/20; opposite verdict 0/20
everywhere. Median Score_tw ratios (L²/L) were 0.15–0.20 for SD and 0.34–0.39 for SD2 (the heavy head costs margin
but still clears 0.75). For the S laws they were 4.1–10.5. The number-weighted Score on the same data called SD and SD2 **S in 20/20**.

### 2026-10-29 09:23 NZDT · a8a93b1 · observation
Walker calibration (fresh seeds 2026102951..54; `results/rev3_analysis.txt`). Score_tw(L) vs (L²):
- eden: 0.1078 vs 0.0252 → D;
- idla: 0.1427 vs 0.0404 → D;
- idlar: 0.0776 vs 0.0401 → D;
- mf: 0.0163 vs 0.1421 → S;
- rotor: 0.0897 vs 0.0483 → D.
No verdict was censoring-fragile. Compactness passed for eden and idla. **C1E-tw, C1I-tw and C2-tw all PASS**, so the
instrument is calibrated for an excluded pilot. The number-weighted replication line matched Rev2 (eden S, idla inconclusive, mf S).
Retention drops: idlar 5 and rotor 1 window, all for n_eff < 30.

### 2026-10-29 09:24 NZDT · a8a93b1 · surprise
Rotor → D under Score_tw, against my unscored guess of S. The figure shows a sharp cliff at s/L² ≈ 2^4–2^5. Since the
rotor's A/P² is roughly constant at ≈ 0.009, A ≈ 110 L², so the cliff is at τ ≈ 0.15–0.3·A: area-filling sweeps, not diffusion.

### 2026-10-29 09:24 NZDT · a8a93b1 · interpretation
Post hoc. In shape-stable domains A ∝ L², so Score_tw separates "τ ∝ L" (boundary-local sweep) from "τ ∝ L² or A", but
cannot separate diffusion from area-filling sweeps. A D verdict on ants must not be read as "diffusive" without
a further discriminator. The depth–duration readout (τ vs max boundary distance d) is the natural one. It
would be falsified as a discriminator if the rotor also gave τ ~ d².

### 2026-10-29 09:24 NZDT · a8a93b1 · decision
Gates pass, so stop here as instructed: **no pilot, no confirmation today**. The next step is a separately registered
excluded ant pilot under Score_tw, with the claim scoped as above, or with a registered depth–duration readout added first.
Not tuned: margin, grid, mask, n_eff threshold, laws.

### 2026-10-29 09:24 NZDT · a8a93b1 · question
Does the rotor's cliff at τ ≈ A/5 reflect a deterministic Eulerian sweep of the territory interior (rotor circuits),
and does the cliff position stay fixed as A/P² drifts? If so, a per-window τ/A collapse should beat τ/L² for the rotor
but tie for Eden. That is a cheap discriminator to register next to the depth–duration readout.

### 2026-10-29 17:58 NZDT · 8904956 · intent
Revision 4: depth–duration readout, calibration only, **no ant data**. Per completed excursion, record max depth d
(L1 distance to the frozen boundary) and distinct cells N. The exponent β is the median per-window OLS slope of
ln mean τ on ln mean d over d ∈ [4, L]. Calls: area ≥ 1.70, line ≤ 1.30. Gates: G0, G1 synthetic (SD, SDL, SA → area;
SB, SC → line), eden and idla → area, new `bal` straight-line walker → line. Fresh seeds 2026102961..64 (walkers) and
2026102981 (synthetic), grepped unused. Full rules: README "Revision 4 registration".

### 2026-10-29 17:58 NZDT · 8904956 · interpretation
Correction to my Rev3 remark, made before any data: depth alone cannot separate diffusion from area-filling sweeps,
because a raster or Eulerian tour of the depth-≤d region also takes ~d². What depth separates is area-filling vs
line-like. A revisit ratio τ/N is registered as a report-only hint for the diffusion-vs-sweep question.

### 2026-10-29 17:58 NZDT · 8904956 · question
Pruning preflight: 4 entries hit the words depth/sweep/excursion. Only the compact-D calibrator entry is in this
observable family, and it retires the number-weighted Score only. Decision: RUN.

### 2026-10-29 18:05 NZDT · 20afc60 · observation
Rev4 run at `acefd81`. G0 PASS: byte-identical to `8904956`, all 3 mutants panic, cargo test 227/0. G1 PASS: 20/20 for
every law (SD 1.92, SDL 1.92, SA 1.95, SB 1.06, SC 0.44). Walkers: eden β 1.994 area, idla 1.997 area (6 windows), bal
0.413 line. All three walker gates PASS. Report-only: idlar 1.997 area, rotor 1.901 area, mf 0.492 line. Between-seed
SDs are ≤ 0.09. About 8 CPU-min.

### 2026-10-29 18:05 NZDT · 20afc60 · surprise
mf reads **line** (β ≈ 0.49 with tiny seed spread), against my low-confidence "not line". A teleporting mover's d is
the max of τ independent draws, so τ grows only slowly with d. That is registered limitation 4, now concrete: line
means line-like motion only for spatially continuous movers.

### 2026-10-29 18:05 NZDT · 20afc60 · surprise
Rotor γ = 0.185, the highest of any kind (eden 0.133). I predicted |γ| < 0.05. The rotor revisits cells more than
diffusion does, so "few revisits ⇒ sweep" is wrong here and the γ hint is retired for diffusion-vs-sweep.

### 2026-10-29 18:05 NZDT · 20afc60 · interpretation
IDLA's gate rests on 6 windows covering ~1% of its off-boundary time. idlar has the identical retained β, so no restart
excursion enters d ≤ L, as registered. The gate certifies local area-like motion only.

### 2026-10-29 18:05 NZDT · 20afc60 · deviation
(1) The registration heading reads 17:58, but the commit stamp is 17:55:58. The heading was written ~2 min ahead; the
commit still precedes all Rev4 data. (2) `uv run --frozen --script` → `uv run --frozen python` (`acefd81`), before the
walker run; the synthetic CSV was regenerated by the fixed script. (3) `--mutant` is run without `--dhist` in G0 so it
hits its original check. (4) mf was not dropped (~100 s per spec, under the 20-min rule).

### 2026-10-29 18:05 NZDT · 20afc60 · decision
All gates pass. Stop as registered: **no ant data**. The proposed unregistered pilot (excluded stage-1 rules, new seeds,
Score_tw + β, no γ claim) is in the README. Not tuned: thresholds, d range, bin counts, L floor, laws.

### 2026-11-25 08:53 NZDT · a9dfa4d · intent
Session start. Revision 5: register and run the **excluded ant pilot** proposed after Rev4. It covers the stage-1 development
rules RLLR, RLLRL, RLLLRR and RLLLLRLL on new seeds @2026112501..04, read with Score_tw (Rev3) and β (Rev4) as
area-filling / line-like / disagree / unread. **No diffusion claim and no confirmation.** Reserved rules and seeds are untouched. Checked
for leftover local work first: the local branches `exp/excursion-*` have 0 commits beyond main, and nothing for this pilot
is untracked. Rules are in the README under "Revision 5 registration".

### 2026-11-25 09:20 NZDT · a9dfa4d · assumption
The instruments are applied outside their calibrated L range. Calibrators reached L ≈ 50–66, while ant windows reach L ≈ 100–170 at
k = 24 (from the committed stage-1 geometry, which I looked at only for feasibility). I keep the frozen band rather than truncating it, and
register an L ≤ 50.7 sensitivity flag instead. The registration was drafted 08:53–09:20 and committed after that, and it was not run on data before registration.

### 2026-11-25 09:02 NZDT · 743beba · deviation
Timestamp correction: the registration heading says "drafted 08:53–09:20". The 09:20 NOTEBOOK assumption entry has the same problem. Both times
were written ahead of time. The actual drafting window was 08:53 to the commit at 08:55:20 NZDT (`78f7f9e`), after reading the README/NOTEBOOK
from 08:51. The registration still precedes all Rev5 measurement. The analysis/run scripts were committed at 08:57:45 (`743beba`).
Before that, the readout was self-tested on relabelled Rev4 *walker* data (`scripts/selftest_rev5.sh`): eden→AREA-FILLING, bal→LINE-LIKE,
rotor→AREA-FILLING, idla→UNREAD ("β covers little of the time", 1%). Beta medians equal `rev4_analysis.json`. No ant data were used.

### 2026-11-25 09:02 NZDT · 743beba · observation
P0a PASS (227/0, rustc 1.100.0 stable; CI pins 1.98.1). P0b PASS: Rev4 calibration and synthetic gate reproduce byte-identically,
and the Rev3/Rev4 analyses reproduce. P0c FAIL as registered: `RL@7` escapes the 512 smoke board in window 14, and `--check`
asserts equal window counts. The instrument keeps the partial escape window, and the probe drops it. `RL@7` at grid 8192 passes `--check`.

### 2026-11-25 09:02 NZDT · 743beba · decision
Amend P0c (A1, README) to use the pilot board 8192, with the same rules and mutants, before any pilot data. I am overriding my own stop rule
transparently. The reason is that the failure is a smoke-design error, diagnosed on a non-cohort rule. A reviewer may treat the pilot as void.

### 2026-11-25 09:05 NZDT · e45f7a8 · observation
P0 attempt 2 (A1, grid 8192) passed: smoke `--check --dhist` exits 0, and all three mutants panic. The pilot ran once, 09:05:10–09:05:30, with 16/16 specs and
no escapes. Readings: RLLR UNREAD (Score_tw inconclusive 0.0775 vs 0.0679; β 1 window), **RLLRL AREA-FILLING** (D 0.0911 vs 0.0419; β 1.932,
seed SD 0.012, coverage 0.25, not L-range-fragile, not seed-heterogeneous), RLLLRR UNREAD (0/36 windows pass n_eff ≥ 30), RLLLLRLL
UNREAD (1/36). Overall: **≥ 2 UNREAD, so the pilot is uninformative for ants at this horizon** (frozen statement).

### 2026-11-25 09:10 NZDT · e45f7a8 · surprise
I gave the failure mode ~10%, and I did not foresee its cause. Ant off-boundary time sits in a few huge excursions: per-window n_eff medians are 10–34 in the
unread rules, and excursions > L² carry 91–97% of the time. The longest is a median 17–62 L², or 0.66–3.9 territory areas. There are almost no excursions at
intermediate depth (median 0 populated d-bins in [4, L]). The excursion population is bimodal, with shallow returns plus rare centre-reaching sojourns. The walkers never looked like
this, so the protective filters bind (post hoc, `results/rev5_diag.txt`).

### 2026-11-25 09:10 NZDT · e45f7a8 · interpretation
RLLRL, the one readable rule, has the most deep-intermediate excursions and the highest n_eff. That makes it the least ant-like of the four on this
diagnostic, so its AREA-FILLING reading may not transfer. Speculation: if a sojourn lasts of order the territory area A ∝ t^(2/3) and
the boundary is visited only between such sojourns, then the number-weighted mean (≈ L, by Kac/kappa) and the time-weighted law (≈ A)
are governed by different populations. The cube-root question may sit in the rare sojourns, not in the typical return.

### 2026-11-25 09:10 NZDT · e45f7a8 · decision
Stop the pilot as registered. No rerun, no new seeds, no loosening of n_eff, bin counts or the L floor on these data, and no confirmation. The next step needs a
registered revision with a synthetic bimodal law ("many shallow returns + rare area-sized sojourns") in G1. It should first ask whether
per-window n_eff grows with window length on walkers that mimic it. No pruning signature: this is uninformative, not a negative result.

### 2026-11-25 09:09 NZDT · 2a5966a · deviation
The three 09:10 entries above were written ahead of the clock again. They were actually written about 09:07–09:08 and committed in `2a5966a` at 09:08:52.
From here on, stamps come from `date` at writing time. Updated `notes/open-questions-hypotheses.md` and `notes/ACTIVE.md` (Rev5 pointer and next step),
the experiment guide row, the atlas (one new open question in boundary-return) and the homepage card. No new data.

### 2026-11-26 08:59 NZDT · a375e94 · intent
Session start (daily run): apply the automated review of PR #42 (head `cfb8903`) on branch `exp/excursion-pilot-scoretw-beta`. Scope: post hoc controls on existing outputs, wording
corrections, the `--check` escape fix, the notebook. Not in scope and not done: any new ant run, Rev6, a bimodal gate, confirmation. Reserved specs and seeds untouched.
Registered Rev5 text is not edited; corrections go to the README section "Review fixes (2026-11-26)" and to these entries. Stamps come from `date` at writing time.

### 2026-11-26 08:59 NZDT · a375e94 · observation
S1 control. `diag_rev5.py --res scratch/rev5_selftest` on the relabelled Rev4 walker calibrators (`results/rev5_diag_calibrators.txt`) reproduces the reviewer's table. Median per window:
n_eff Eden 379, IDLA 545, rotor 81, bal 7750; longest τ/A 1.02, 1.29, 0.29, 0.015; longest τ/window 0.012, 0.006, 0.030, 0.0002; populated d-bins in [4, L] 14, 2.5, 9.5, 13.
Ants (3 unread): n_eff 34/12/10, longest τ/A 0.98/3.4/3.9, longest τ/window 0.070/0.141/0.172, bins 0. RLLRL: 115, 0.66, 0.032, 13.

### 2026-11-26 08:59 NZDT · a375e94 · interpretation
Correction of my 09:10 (2026-11-25) entries and the README "why unread" paragraph: excursions of order A and nearly empty mid-depth bins are not ant-specific (IDLA has both). What separates
the three unread ant rules from the calibrators is the low n_eff and the largest excursion being 7–17% of the window. "The calibrators never looked like this" was wrong in part. The earlier wording
stays in the history (`cfb8903`); the README marks it superseded and the homepage, atlas, open question, ACTIVE and notebook are rewritten.

### 2026-11-26 08:59 NZDT · a375e94 · observation
S3 post hoc density (per-log-band shares of excursions and time by d/L and τ/L², end of `results/rev5_diag.txt`). In the unread ant rules 98–99% of excursions have d < L/16 and 87–94% of time is in
d ∈ [L, 2L). Count share per octave of d/L in [¼,½), [½,1), [1,2): RLLR 0.001/0.000/0.004, RLLLRR 0.003/0.002/0.004, RLLLLRLL 0.003/0.002/0.003, i.e. at most a weak upturn with tens of excursions per window;
RLLRL falls monotonically; IDLA 0.062/0.036/0.447 (a far stronger dip and upturn). So "bimodal" is not established; wording is now "heavy-tailed, possibly bimodal", and not ant-specific.

### 2026-11-26 08:59 NZDT · a375e94 · deviation
S7. A1 had changed the smoke board, not the instrument. `examples/boundary_excursions.rs` `check_against_probe` now compares only completed windows: on escape the instrument may keep exactly one extra
partial escape window; otherwise counts must be equal. New `tests/boundary_excursions_escape.rs` (RL@7 on a 512 board; failed with `window count` before the fix, passes now; plus non-escaping controls).
`scripts/repro_rev5_review.sh` (RAYON_NUM_THREADS=4, rustc 1.100.0): the escaping smoke exits 0, and the Rev5 pilot (windows, hist, fhist, dhist), Rev3 calibration and Rev4 calibration outputs are byte-identical to the committed files
(`results/rev5_review_repro.txt`, commit `d73616d`). The change is in `--check` only, so no output file can differ.

### 2026-11-26 08:59 NZDT · a375e94 · observation
S6/Q1. The registration header "08:53–09:20" is wrong (README Review fixes R6; see the 09:02 entry of 2026-11-25). Git cannot show whether `analyse_rev5.py` and the other scripts were drafted before
`78f7f9e`: it records only that they were committed 2 min 25 s after, and that the walker self-test ran before `743beba`. Stated as unknown; what is established is that no ant data existed before 09:05:10 on 2026-11-25.
M8 (≥ 2 UNREAD is tested before ≥ 1 DISAGREE; precedence recorded after the data; outcome unaffected, 0 DISAGREE), M9 (β retention has no n_eff filter) and S4 (n_eff floor selection bias; registrable prediction that n_eff grows like L
under a P(τ>x) ~ x^-1/2 tail truncated at ~A) are recorded in the same README section and the open question.

### 2026-11-26 08:59 NZDT · a375e94 · decision
Deferred: (i) the reviewer's question whether the longest excursions are highway transients or trapped loops: needs a new instrument mode, not a cheap post hoc check on existing outputs; listed open. (ii) Rev6 / bimodal or
variance-robust gate: not started; the user decides (ACTIVE.md notes both options, neither registered). (iii) The Rev5 blog post (M10) is a short honest post added after S1 was resolved.
Notebook: status cell fixed, provenance cell prints the commit, corrected "why unread" and "does not show" cells, executed top to bottom under uv with `--with nbconvert --with ipykernel` (no `uv.lock` change); figure PNGs are not embedded (70 kB file).

### 2026-11-27 08:56 NZDT · d66c060 · intent
Session start (daily run, written before the first command of the work): apply the incremental automated review of PR #42 (head `d66c060`, posted 2026-11-27 06:56 NZDT). Scope: add `idlar`
(restart-free IDLA) to the post hoc calibrator control and restate R1/R2 (S1); correct the 2026-11-26 session-start stamp (M2); make `repro_rev5_review.sh` write to scratch by default (M3);
re-pin the homepage evidence and Revision 5 links and the blog post commit field (M4); notebook "at current main" wording (M5); wording nits (M6); band-assignment docstring (M7).
Not in scope: new ant runs, new observables, Rev6, confirmation; reserved specs and seeds untouched. Registered text not edited.

### 2026-11-27 09:11 NZDT · d66c060 · deviation
Correction (review Minor 2): the 2026-11-26 "08:59 · intent" session-start entry was written after the work it scopes (repro started 08:54:56; `d73616d` committed 08:58:36). Left in place (append-only).
Today's 08:56 intent entry was written before any edit or run of this round (only the review and files had been read).

### 2026-11-27 09:11 NZDT · d66c060 · observation
S1 follow-up (post hoc, no ant data): `scripts/calib_idlar_rev5.sh` → `results/rev5_diag_calibrators_idlar.txt` (idlar in the RLLLLRLL slot; reruns byte-identical). idlar medians per window: n_eff 50.4 (32/36 ≥ 30),
τ > L² time share 0.699, populated d-bins 2.5, longest τ/A 0.799, longest τ/window 0.00439; d/L count shares 0.379, 0.174, 0.110, 0.063, 0.039 (monotone), [L, 2L) time share 0.634. Matches the reviewer's figures.
4 ≤ d ≤ L counts are unchanged by dropping restarts (median 160). Eden, rotor and idlar fall monotonically in d/L; bal rises monotonically.

### 2026-11-27 09:11 NZDT · d66c060 · interpretation
Second correction: IDLA's strong deep upturn, deep population and 97% τ > L² share were restart artefacts, so my 2026-11-26 "two-population shape is not specific to ants" is withdrawn. No restart-free walker shows the
ants' weak [L, 2L) upturn; whether it is real is open (per-seed/bootstrap check not done). Still standing: τ ~ A is not ant-specific (Eden 1.02 A); idlar keeps sparse mid-depth bins. Longest τ / window is the clean separator
(ants 0.070–0.172; walkers ≤ 0.030); n_eff is weaker (idlar 50 vs RLLR 34). README R10–R16 and notes/ACTIVE/open question/homepage/blog post updated; notebook markdown cells 33 and 36 edited (no code change, not re-executed;
provenance cell still prints the 2026-11-26 execution commit).

### 2026-11-27 09:11 NZDT · d66c060 · observation
`repro_rev5_review.sh` (now logs to scratch by default; header records dirty-path count and `git diff HEAD` sha256) rerun with rustc 1.100.0, RAYON_NUM_THREADS=2, incremental `--release --locked` build
(binary sha256 `00367c34dc4ccdf4…`) on the dirty working tree of this round (4 modified tracked paths at start): escaping smoke exits 0 (6 escaped RL@7 rows); Rev5 pilot windows/hist/fhist/dhist, Rev3 calib windows/hist/fhist
and Rev4 calib windows/hist/fhist/dhist all byte-identical. REPRO: PASS, 08:57:38–09:06:27. `selftest_rev5.sh`: PASS. `diag_rev5.py` (both modes) and `analyse_rev5.py` leave the tree clean; `sha256sum -c` on the Rev5 lines: OK.

### 2026-11-27 09:11 NZDT · d66c060 · decision
Deferred: the per-seed/bootstrap test of the upturn (cheap, post hoc on existing `rev5_pilot_dhist.csv`, but outside this bounded round); which statistic (n_eff or longest τ / window) to register next is left to the
user with the choice of next revision. No Rev6, no new observable registered, no confirmation, reserved specs and seeds untouched. Homepage link and blog commit field are re-pinned to the evidence commit of this round in a follow-up commit.

### 2026-11-28 10:00 NZDT · 18937bf · intent
Session start (written before any edit of this round; only the review and committed files had been read, plus a read-only check of L in `rev4_calib_windows.csv` and `rev5_pilot_windows.csv`): apply the third automated review of PR #42 (head `18937bf`, posted 2026-11-28 06:55 NZDT; no blocking issues).
Scope: homepage card wording about Eden (should-fix 1); a caveat on the structurally empty shallowest d/L band when L ≤ 16 (minor 2); a note that longest τ / window, if registered, needs a window-length scaling prediction (minor 3); record the reviewer's question on bootstrap vs per-seed sign test under R16a.
Not in scope: new runs, the R16a check itself, new observables, Rev6, confirmation; reserved specs and seeds untouched. Registered text not edited; README and NOTEBOOK changes append-only.

### 2026-11-28 10:01 NZDT · 8de04c8 · observation
Third-round review fixes (no runs, no data changes): homepage card Eden wording corrected (R17); L ≤ 16 band caveat added with window counts computed read-only from the committed windows CSVs (R18; idlar 23/36, eden 16/36,
ants 4–8/36 with L < 16); longest τ / window marked post hoc with a note that a registration needs a window-length scaling prediction (R19); reviewer's bootstrap-vs-sign-test question added to R16a. No registered text,
results file, script or notebook cell changed.
