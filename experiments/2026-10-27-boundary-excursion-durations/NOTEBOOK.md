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
