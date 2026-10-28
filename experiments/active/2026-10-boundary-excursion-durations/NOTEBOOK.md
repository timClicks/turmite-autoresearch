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
