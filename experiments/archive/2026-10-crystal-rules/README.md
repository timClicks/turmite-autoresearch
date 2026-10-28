# crystal-rules: why do some rules draw diagonal "crystal" lattices?

Written 2026-10-14 19:03 (+13:00), commit 6ce3793. **Status (corrected 2026-10-15): S0, S3, S4 done; S1 ray anatomy done 2026-10-15 (P2 falsified, P4 held for 2 of 3, see "S1 ray anatomy: results"); S2 partly done (local patch, ground highway); transplant, ray-end knockouts, spinner isolation and exact periodicity deferred by scope, not run. Originally: "designed, nothing run yet" (registration text below is unedited).**
Every hypothesis and prediction below is registered before any measurement; append
results under "Results", do not edit this section.

## Observation that prompts it
Two 30M-step renders (user screenshots, `Downloads/RLLLLRRL_30M.png`,
`Downloads/LRRRRRLLR_30M.png`; a third rule, RLLLLLLLRRLRR, was named but not shown):
RLLLLRRL (2624x2630) and LRRRRRLLR (2824x2824). Both show

1. thin straight rays at 45 degrees to the image axes, hundreds to ~1500 cells long,
   which close into nested rotated rectangles/diamonds;
2. dense blobs at some corners/crossings, sparse elsewhere;
3. almost no re-use (busiest cell 164 / 139 visits in 30M steps) and a bounding box
   that is entirely "visited" because the rays sweep it.

This is not the t^(1/3) blob class. RLLLLRRL is already on record as a late grid
escape with no recognised highway (B5, `notes/frontier-2026-10-13-results.md`), and the
G1 breakout analysis found a phase switch to ~4 steps/cell
(`notes/research-frontier-2026-10-13-pm.md`, G1/K3). So the question may be the same
one as K3 / Q15 (frame builders): "crystal" may just be the frame-builder mode seen
at larger scale. Part of this experiment is to find out whether it is.

Assumptions (untested): (a) the renders are not rotated, so "45 degrees" is a diagonal
of the lattice, i.e. a staircase path (check in `experiments/archive/2026-10-occupancy-pages/scripts/render.py` before S1);
(b) all three rules show the same phenomenon (S0 tests it).

## Hypotheses (mechanisms that make different predictions)
- **H-ray (glider in a medium).** A ray is a periodic translating pattern: the ant moves
  through background laid down by earlier passes, repeating a short motif of period p
  (a diagonal "highway" whose background happens to be compatible). Rays end when the
  ant meets a cell whose colour breaks the motif. Predicts: the ray's colour motif is
  the same in every ray (up to the 4 rotations), p is small, only a subset of the
  rule's colours appears in rays, and a ray replayed alone on a blank board does NOT
  propagate (it needs its background).
- **H-spin (spinner + launcher).** The long same-turn run (L^4 in RLLLLRRL, R^5 in
  LRRRRRLLR, L^7 in RLLLLLLLRRLRR) makes the ant circle a 2x2 loop while cells walk
  through the run's colours; it leaves the loop when the cells reach the end of the
  run. Blobs are the spin sites, rays what the ant does between them. Predicts: node
  size grows with run length k; crystal-ness depends on the run, not on the tail
  letters; Hamming-1 mutations inside the run destroy it, mutations in the tail
  mostly don't.
- **H-reverse (reversibility).** The dynamics are time-reversible, so a ray and the
  ant's later return along it are the same path in opposite directions; rectangles
  are the ant retracing earlier structure. Predicts: a large fraction of ray length is
  later traversed in reverse, and the 164-visit maximum is retracing.
- **H-frame (K3).** Crystals are frame builders in the K3 sense: perimeter patrols,
  width ~ t^(1/2), 1D skeleton. Predicts alpha_w = 0.50 +- 0.03 and 2-6 steps per
  new cell in ray mode. Distinguishable from the others by the exponent and by whether
  rays are self-similar across scales.

These are not exclusive (H-spin could produce rays whose substance is H-ray); the
stages are designed so each result moves belief between them.

## Instruments (to build, with oracle tests per AGENTS.md)
- **Ray segmentation**, `examples/crystal_rays.rs`: run a rule on a blank 8192^2 board
  with the `fast` loop and record positions. Split the trajectory into maximal
  windows that are a straight diagonal (|dx| = |dy| within 1 cell over >= 128 steps,
  steps per cell <= 8). Output per ray: start t, length, heading (4 diagonals),
  duration, colour sequence over 2 periods, terminating cell colour, and whether it
  overlaps an earlier ray's cells (and in which direction). Property test: the
  segmentation of `reference` and `fast` trajectories agrees step for step; a
  synthetic piecewise-diagonal path recovers its planted rays.
- **Crystal score** (census, cheap, grid-only): fraction of visited cells lying on a
  45-degree run of visited cells of length >= 30, minus the same for axial runs.
  Speed-agnostic (classic ant highways move 2 cells per 104 steps, so trajectory
  straightness would be wrong here).
- **Calibration (AGENTS.md rule 5)** before use: positive control RL (one diagonal
  highway), RLRRRL (frame builder, axial lines not diagonal), a seeded random walk and
  the rotor walker (`src/walkers.rs`) as negative controls. Report the false-positive
  rate of the crystal score on the 3,512 census rules (`experiments/archive/2026-10-census-sweeps/results/non_highway.txt`) at the
  chosen threshold, and re-do the calibration if the threshold changes.

## Stages (each informs a decision)

**S0. Reproduce.** Regenerate RLLLLRRL, LRRRRRLLR, RLLLLLLLRRLRR on a blank board to
2^25 (deterministic, no seed). Confirm the renders match the screenshots and compute
the crystal score. Decision: are these three one phenomenon?

**S1. Anatomy of rays (H-ray vs H-spin vs H-reverse vs H-frame).** The three rules to
2^28: ray length distribution (log bins, tail exponent), heading set, colour motif and
period, steps per new cell in rays vs overall, fraction of ray length re-traversed in
reverse, what ends a ray (terminating colour, distance to the nearest earlier ray
along the heading), and the bounding-box width exponent 2^16..2^28 (`src/bin/probe.rs`).

**S2. Cause by intervention (the discriminating step).**
- *Ray transplant*: lift a mid-ray state (ant + strip of width 2p+4 around the ray
  axis) from the S1 run onto a board with (i) the original background, (ii) background
  reset to 0, (iii) background colours shuffled (seed 20261014). Metric: propagation
  length in units of the strip length. Machinery: `examples/transplant.rs`.
  Separates a self-sustaining highway from a medium-dependent ray.
- *Ray-end knockout*: at a terminating cell flip single cells in a 5x5 window and
  rerun; does the ray continue? Machinery: `examples/knock.rs`.
- *Spinner isolation*: blank board with the first k colours preset so that the ant
  spins; exit time and heading as function of k and the tail.

**S3. Mutation map (H-spin).** For each of the three rules, all Hamming-1 and Hamming-2
neighbours plus single-letter insertions/deletions in the long run (a few hundred rules
each); crystal score at 2^24; heat map of which positions matter. Control: the same scan
for 3 blob-class rules of similar length (RRRRRLLLLLL, RLLLLRRRRLR, RLRLLL), giving the
background rate at which a mutation changes the class.

**S4. Census (generalisation).** Crystal score for the 3,512 census rules at 2^24 and
for the unclassified rules of length <= 11. Features: max same-turn run k, net turn per
colour cycle (sum of turns mod 4), n, word symmetry (palindrome, reverse-complement).
Decision tree / logistic with leave-prefix-family-out cross-validation (rules sharing
a prefix have identical early trajectories, see the B5 note, so a random split
overstates independence). Decision: is "crystal" a clean class, and what predicts it?

## Predictions (fixed now)
1. S0: all three rules have >= 90% of visited cells on 45-degree runs by the crystal
   score and no recognised highway at 2^28. If one is axial or blob-like, the grouping
   is wrong and S1-S4 split into classes.
2. S1, H-ray: >= 80% of ray length (cells) shares one motif up to the 4 rotations,
   period p in [4, 40]. More than 5 motifs, or p > 100, falsifies H-ray.
3. S1, H-frame: bounding-box exponent 0.50 +- 0.05 over 2^20..2^28 for all three; if it
   is 0.33 +- 0.05, they are slow-filling blobs and the crystal picture is a
   finite-time crossover. My prior: 40% for 0.50, 40% in between (0.40-0.47), 20% for 0.33.
4. S1, H-reverse: <= 20% of ray length re-traversed in reverse (my belief: the 164
   max-visits are node blobs). > 50% supports H-reverse.
5. S2: transplanted ray with original background propagates >= 10x the strip length in
   >= 80% of trials; with background 0 it propagates < 1x in >= 80% of trials
   (medium-dependent). If the blank-background ray also propagates, it is a genuine
   highway and B5's "no recognised highway" is a detector failure (period > window).
6. S3: Hamming-1 mutations at positions inside the long run drop the crystal score
   below the 5th percentile of the control-scan scores in >= 60% of cases; mutations
   in the tail in <= 30%. Equal sensitivity falsifies H-spin.
7. S4: max same-turn run >= 4 in >= 80% of crystal-class rules, but < 50% of rules with
   run >= 4 are crystal (necessary, not sufficient). More than 20% of crystal rules
   with max run <= 3 falsifies H-spin as stated.

## What would show the framing is wrong
- No short motif (large motif count): "crystal" is the visual effect of long ballistic
  transits at scale, and the experiment becomes one about transit statistics.
- Ray length is fixed by the rule, not the geometry: correlation of ray length with the
  distance to the nearest earlier ray along its heading < 0.2 (> 0.5 means geometry
  sets it).

## Reproduce (planned; nothing run yet)
All via WSL from `/mnt/f/Code/turmite`:
```bash
cargo test --release --test crystal      # oracle test for the instrument
cargo run --release --example crystal_rays -- RLLLLRRL 28 experiments/archive/2026-10-crystal-rules/dumps
uv run experiments/archive/2026-10-crystal-rules/scripts/ray_stats.py
```
Budget: S0-S2 minutes; S3 ~1,000 rules x 2^24, minutes; S4 3,512 x 2^24, about an hour
on 6 cores with `rayon`. Deterministic; results keyed by rule; the only RNG is the
shuffled-background control (seed 20261014).

## Results
(none yet)

### Results so far (2026-10-14 19:38 (+1300), commit 6ce3793, uncommitted work)
Predictions above are unedited; verdicts here. Deviations (the crystal-score definition, the census path) are in NOTEBOOK.md.
- **S0 (done).** The renders are reproduced (max visits 164, 139). They are visit-count heat maps of a box that is ~100% visited: the "red" is a uniform ground state (visited 2x, colour 2: 80-83% of visited cells in all three rules). **Prediction 1 as written was mis-specified** (">= 90% of visited cells on 45-degree runs") and is not meaningful; the replacement (diag-run cover of non-ground cells, 0.96-0.98 vs 0.45 for the control RLRRRL) holds, but its "score > 3" threshold failed (1.95-2.32). The "no recognised highway at 2^28" part was not tested.
- **S1 (partly done).** Width exponent 0.495 / 0.503 / 0.502 over 2^20..2^28 (prediction 3: 0.50 +- 0.05, **held**, H-frame supported; also true for the control RLRRRL 0.499, so the exponent does not separate crystals from flat frame builders). Not done: ray length distribution, motif period, re-traversal fraction (prediction 2 and 4 untested), what ends a ray.
- **S2 (partly done).** A lone ant on a uniform ground of colour 2 is a true highway in all three rules (50 / 58 / 86 steps per diagonal cell), not on a blank board, and not for the control. This supports H-ray with the ground as the medium (prediction 5's logic, tested on a uniform board instead of a transplanted strip: blank-background propagation < 1x **held**; ray with original background not tested). A ground square of side 600-1200 reflects the ant: it stays inside while the box grows to 2-3.5x its side. Not done: transplant of an actual ray, ray-end knockouts, spinner isolation.
- **S3 (done).** Prediction 6 (run positions sensitive, tail not) **falsified**: all positions are sensitive; crystals are isolated under point mutation (0/142 Hamming-2). A different structure appeared: the family R L^k R R L is crystal-like (by the ground-fraction proxy, not the grid score) for k = 4..15; R L^k RRLRR for k >= 6; R L^k RRR LLL only for k=4. See the NOTEBOOK correction.
- **S4 (done, census length <= 12).** Prediction 7: all 8 crystal rules have max same-turn run >= 3 and 7 of 8 have a run >= 4 (the 8th, RLLLRRRLRLRR, has 3): held at 87.5% (n = 8; threshold >= 80%). Every crystal has ground (2x, colour 2); no ground-4x/6x rule is crystal. Necessary-not-sufficient part not computed.
- **Open:** why exactly ground 2 and a lone-ant highway on it are produced by the sweep (the 4-5 steps/cell fill is the same frame-builder mechanism as K3), what the ray end looks like, and whether k >= 4 is a threshold in the colours that turn L after the ground colour.

### Paired local-patch experiment registered 2026-10-14 22:15 (+1300), 7eff085
Select the first 12 nonoverlapping 4096-step windows within 2^25 with absolute dx >=64 and abs(abs(dx)-abs(dy)) <=4. Preserve the starting ant and 33x33 patch; set the exterior uniformly to colour 0 or 2. Replay 4096 steps, reporting displacement and the exact trajectory-prefix length against the intact baseline. Prediction: colour-2 exterior produces greater diagonal displacement than colour-0 in at least 9 of 12 paired samples per rule. This tests local-state propagation, not the originally proposed long-strip transplant or ray termination. Selection depends only on baseline displacement.

### Local-patch outcome (2026-10-14 22:16 +1300)
Prediction passed: 12/12 paired windows for each of the three rules travelled farther diagonally with colour-2 exterior than blank exterior. Inputs and SHA256: results/local_patch_summary.json; producer scripts/local_patch_summary.py under uv. The new trajectory loop passed its reference-oracle property test in release mode (results/trace_oracle_v2.log). This does not validate the old loops retroactively. Exact highway periods and boundary reflection remain unproven.

### S1 ray anatomy: operationalisation of predictions 2 and 4 (registered 2026-10-15 21:02 +13:00, base `da88e61`, before any crystal-rule ray CSV was produced)

Predictions 2-4 above stand unedited. The README did not fix what a "motif" or "re-traversed in reverse" means, so this fixes it now. Instrument: `examples/crystal_rules_rays.rs`
(tests: `cargo test --release --example crystal_rules_rays`, planted-ray recovery, board loop == reference ant, axial line not a ray, motif rotation invariance); calibration in `results/rays_calibration.txt`
(false rays in random walk / rotor / RLRRRL controls are at most 29 cells, so only rays with **length >= 64 cells** are analysed; this cutoff was chosen from the controls, before crystal-rule rays were seen).
Run: `crystal_rules_rays ant RULE 268435456 16384` for RLLLLRRL, LRRRRRLLR, RLLLLLLLRRLRR, and the control RLRRRL (blank board, no seed); raw CSV in the gitignored `dumps/`.

- Motif of a ray = least cyclic rotation of the smallest period p in 2..256 for which the colours read agree with themselves at lag p on >= 98% of the central half of the ray. A ray with no such p is "aperiodic".
  "Up to 4 rotations" in prediction 2 is read as cyclic phase (rotating the heading does not change the colour sequence); it is not a spatial rotation.
- **P2 (H-ray).** Over rays >= 64 cells, the single most common motif accounts for >= 80% of total ray length (cells) and its p is in [4, 40]; falsified if more than 5 distinct motifs each
  carry >= 1% of ray length, or if that dominant p > 100. Per rule; also report the share of aperiodic ray length.
- **P4 (H-reverse).** Length-weighted mean of rev_frac (share of a ray's cells already crossed by an earlier ray of the opposite heading) <= 0.20; > 0.50 supports H-reverse. Also reported: same-heading overlap, steps per cell, length distribution (log2 bins), terminating colour counts.
- Ray endpoints are accurate to about L = 128 steps by construction; lengths below ~5 x 128 / (steps per cell) cells carry that fractional error.
- Not done here: distance to the nearest earlier ray along the heading, ray-end knockouts (S2), exact periodicity proof.

### S1 ray anatomy: results (2026-10-15 21:06 +13:00, commit `da88e61`; predictions and the operationalisation above unchanged)

Commands: `cargo test --release --example crystal_rules_rays` (4 tests pass); calibration `results/rays_calibration.txt`; `crystal_rules_rays ant RULE 268435456 16384` (36-87 s per rule; raw CSV in gitignored `dumps/rays_*.csv`);
`uv run experiments/archive/2026-10-crystal-rules/scripts/s1_rays.py` -> `results/s1_rays.txt`. Rays >= 64 cells, blank board, 2^28 steps. The control RLRRRL produced 0 rays >= 64 cells.

| | RLLLLRRL | LRRRRRLLR | RLLLLLLLRRLRR |
|---|---|---|---|
| rays >= 64 cells / total length (cells) | 2960 / 741103 | 254 / 43460 | 5991 / 1383736 |
| median / max length | 179 / 1487 | 127 / 603 | 157 / 1078 |
| steps per cell, median | 2.09 | 2.20 | 2.32 |
| aperiodic share of length | 0.010 | 0.006 | 0.007 |
| colour motifs with >= 1% of length / dominant share, p | 8 / 0.335, p=2 | 20 / 0.157, p=2 | 23 / 0.126, p=4 |
| **P2 (H-ray)** | **FALSIFIED** (> 5 motifs, dominant share < 0.8) | **FALSIFIED** | **FALSIFIED** |
| reverse overlap (length-weighted), **P4** | 0.091 **HELD** | 0.199 **HELD (barely, <= 0.20)** | 0.375 in between (not held, not H-reverse) |
| same-heading overlap | 0.352 | 0.380 | 0.450 |

Headings are balanced over the four diagonals (shares 0.17-0.34). Ray lengths span 2^6..2^10 cells with a thin upper tail (no ray above 1487 cells; the 1500-cell rays of the screenshots are the maximum, not typical).

**What the registered test says.** P2 fails for all three rules as defined: the colours read along rays are not one motif. P4 holds for two rules and is inconclusive for RLLLLLLLRRLRR; no rule supports H-reverse (> 0.5).

**Exploratory (post hoc, added after seeing the colour motifs; not a test).** Nearly all motifs have period 2-6 and 2 steps per cell, and their colours are shifted copies (e.g. RLLLLRRL: `04`, `15`, `26`, `07`), which suggests they are one
dynamical object read at different background phases. Mapping each colour to its turn letter and re-canonicalising: the alternating-turn staircase `LR`/`LRLR` carries 0.81+0.07 (RLLLLRRL), 0.55+0.10 (LRRRRRLLR) and 0.67 (RLLLLLLLRRLRR, `LRLR`) of ray length;
65, 20 and 75 distinct turn-letter motifs remain, so the long tail of other motifs is real but small. Reading: most of the "ray" length is the ant alternately turning left and right, which is a staircase and therefore diagonal for any
rule, in a background (the colour-2 ground found in S2) that supplies the alternating colours. That fits H-ray with the ground as the medium and says the diagonal is cheap geometry rather than a deep motif; it does not by itself
explain why ground 2 forms or when rays end. Caveats: 98% self-agreement at lag p is a loose periodicity test; ray endpoints are good only to about 128 steps; the 64-cell cutoff came from controls but the
turn-letter collapse did not; one run per rule (deterministic, no seed); reverse overlap needs an earlier opposite ray, so it is low early in the run by construction; ground phase (colour shift) and colour-to-letter mapping are my reading, untested by intervention.
Still not done (S2): transplant to a reset background, ray-end knockouts, spinner isolation; exact periodicity; distance to the nearest earlier ray.

### S2 ground-phase reset registration — 2026-10-15 21:18 +13:00

Base commit da88e61; working tree includes the uncommitted S1 instrument. No phase-reset measurements have run. Mechanism: colour-2 ground supplies alternating turns; changing its phase should disrupt staircase transit and end rays sooner.

Design fixed before measurement: blank starts, three rules RLLLLRRL, LRRRRRLLR, RLLLLLLLRRLRR, no randomness (seed not applicable). Scan at most 2^25 steps on an 8192-square board. Starting after 2^18, select the first 16 online detections separated by at least 8192 steps: the previous 256 consecutive rolling 128-step windows must each have diagonal displacement abs(dx)>=16, abs(abs(dx)-abs(dy))<=2 and the same heading. Selection uses no future outcomes. Replay each selected state for 2048 steps in three arms: sham 2->2, reset 2->0, advance 2->3. Only cells exactly colour 2 in the inclusive radius-128 square centred on the ant are changed; ant position, heading and all other cells are preserved. Trials share a baseline trajectory and are not independent seeds.

Metrics: alternating-turn fraction among the 2047 adjacent turn pairs; first post-intervention rolling-window heading failure at step >=128 (2048 if none, right censored); number of edited cells; exact trajectory prefix versus sham; count of future steps outside the reset square. Termination is loss of the S1 geometric criterion in the original heading, not proof of a permanent ray end. Full 2048-step alternating fraction is primary; also report first-128-step fraction to expose later recovery. Locality and detector latency may dilute effects.

Registered predictions, per rule, paired against sham: (A) reset 2->0 lowers full-window alternating fraction by >=0.10 in at least 12/16 trials; (B) reset 2->0 produces strictly earlier geometric termination in at least 12/16; (C) advance 2->3 meets the same two thresholds, testing phase specificity beyond blanking. Fewer than 16 detections means that rule is not evaluable under these thresholds; report all detected trials, no replacement based on outcomes. Exact sham replay and zero-cell edits are controls. Report paired means and between-trial SD descriptively, censor counts and ties; no between-seed uncertainty is available.

Calibration before interpreting ant measurements: synthetic perfect alternating staircase has fraction 1 and censored termination; an axial path has fraction 0 and failure at 128. Oracle test: dense loop with identical phase edit agrees step-for-step and cell-for-cell with reference::Ant. Existing S1 detector calibration remains relevant because its window criterion is unchanged. No fit or exponent estimator is introduced.

### S2 phase-reset results — 2026-10-15 21:23 +13:00

Completed all 16 selected states per rule (48 paired states, 144 replays); base da88e61 with uncommitted source hashes recorded in each `results/phase_RULE.json`. No random initialisation or seed. Small trial CSVs, hash-checked `.done` checkpoints and provenance are in `results/phase_*`; generated data were not hand-edited. Summary: [phase_summary.txt](results/phase_summary.txt). Colleague write-up, executed from a clean kernel: [02-phase-reset.ipynb](notebooks/02-phase-reset.ipynb).

| Rule | 2->0 alternating drop >=0.10 | 2->0 earlier termination | Mean alternating delta (between-trial SD) | Mean termination delta, steps (SD) |
|---|---:|---:|---:|---:|
| RLLLLRRL | 0/16 | 3/16 | +0.050501 (0.059795) | -1.375 (4.603) |
| LRRRRRLLR | 0/16 | 6/16 | +0.073156 (0.092682) | -137.813 (268.734) |
| RLLLLLLLRRLRR | 2/16 | 8/16 | +0.041891 (0.112932) | -66.375 (111.481) |

**A and B failed for every rule. C also failed:** 2->3 alternating drops occurred in 1/16, 0/16, 0/16, with earlier termination in 0/16 for all three. All arms terminated by the geometric criterion within 2048 (zero censored); sham edited zero cells and matched the original replay for all 2048 steps. First-128-step deltas, ties, outside-square counts and edit counts are in the summary and CSVs. SD describes selected states on one trajectory, not between-seed uncertainty. The full-window alternating fraction includes the post-ray motion and can increase even when the original ray ends earlier.

**Interpretation:** the strong prediction that local ground erasure suppresses staircase motifs and usually ends rays sooner did not hold. Some resets advance termination, especially in the second/third rule, but the selected sample does not establish a general termination mechanism. Post hoc limitation: colours 2 and 3 give identical turns in all three rules; advance-to-3 tests revisit-sensitive phase effects, with no immediate turn change. The detector's 128-step latency, finite square and shared baseline also limit inference. An endpoint defect intervention and explicit counts of visits to edited cells remain open; neither was run here. Existing S2 transplant/spinner questions remain unresolved.

Reproduce from WSL (or prefix with `wsl -e bash -lc` on Windows), repository `/mnt/f/Code/turmite`:

```bash
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
cd /mnt/f/Code/turmite
cargo test --release --example crystal_rules_phase > experiments/archive/2026-10-crystal-rules/results/phase_tests.log 2>&1
cargo test --release > experiments/archive/2026-10-crystal-rules/results/phase_release_suite.log 2>&1
uv run experiments/archive/2026-10-crystal-rules/scripts/phase_reset.py > experiments/archive/2026-10-crystal-rules/results/phase_run.log 2>&1 &
wait
uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace experiments/archive/2026-10-crystal-rules/notebooks/02-phase-reset.ipynb
```

The driver builds release mode, writes each completed rule atomically and validates existing checkpoints before skipping. It refuses to replace existing data with a changed recipe; explicitly archive old outputs before changing the protocol. Resume verified via the same uv command redirected to `results/phase_resume.log`: source/recipe/data hashes match and the regenerated summary agrees. Calibration plus 32-case oracle property test passed (2 tests); full release suite passed. No dependencies changed, no commit made. The current trial outputs are reproducible uncommitted files intended for version control.

### S1 ray anatomy: correction after review (21:24 +13:00, commit `da88e61`)

My exploratory reading above ("staircase transit in the colour-2 ground ... fits H-ray with the ground as the medium") is **not supported by the numbers** and is withdrawn.
- The S2 ground highway runs at 50 / 58 / 86 steps per diagonal cell; the segmenter accepts at most 8 steps per cell, so it cannot see that object. The rays found here run at about 2 steps per cell and are a different phenomenon.
- The dominant colour pairs are not colour 2: RLLLLRRL `04`, `15`, `26`, `07`; LRRRRRLLR `16`, `68`, `47`. In each pair the rule turns the two colours in opposite directions (turn letters R/L), which is why they collapse to the alternating staircase LR / LRLR.
- What the data actually show: a staircase moving over a background in which alternate cells carry opposite-turn colours. That two-sublattice background may itself be the "crystal", and the open question is **why such a background forms**, not why the colour-2 ground forms.
  Untested: I did not print the colours around a long ray to confirm the sublattice picture.
P2 (falsified) and P4 verdicts, and all numbers in the results table, are unchanged.
**Reproduce note.** The "Reproduce (planned)" block above names `crystal_rays` and `ray_stats.py`, which do not exist. The actual commands are in `results/trajectory_recipe.txt` (trace) and, for rays: `cargo test --release --example crystal_rules_rays`;
`crystal_rules_rays ant RULE 268435456 16384 > experiments/archive/2026-10-crystal-rules/dumps/rays_RULE.csv`; `uv run experiments/archive/2026-10-crystal-rules/scripts/s1_rays.py`.
