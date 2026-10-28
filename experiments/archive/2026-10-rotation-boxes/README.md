# Q25: do cyclic rotations of a rule share structure, or only a bounding box?

Registered 2026-10-25 (part 2 below before it is run), base `decae71`. Follow-up to `experiments/archive/2026-10-prefix-causal-horizon/` (Q25 there).

## Background and the exact identity

`rot_k(w)[c] = w[(c + k) mod n]`. Colour `c'` of the rotated rule is colour `(c' + k) mod n` of `w`, so a rotated rule started on a blank board is the
original rule started on a uniform background of colour `k`. (Not a theorem about attractors; just a relabelling, checked by the oracle test below.)

## Part 1 (observational, run before this registration; `scripts/rotation_boxes.py` -> `results/rotation_boxes.txt`)

Committed census CSVs only. Among the 702 survivors at 1e11, over all 2,012 equal-length rotation (or mirror-rotation) pairs versus all other equal-length pairs,
the chance of sharing (width, height) is 52-129 times higher at every horizon 1e8..1e11 even against a composition-matched control (4 of 24,411 control pairs
at 1e11, against 21 of 2,012 rotation pairs; Fisher p <= 1e-16, but pairs inside one class are not independent). The 21 pairs sharing a box at 1e11 form 12 groups
(sizes 2-4) among 114 rotation classes with at least two survivors: about 10% of classes. The shared boxes are small (28-118 cells). Persistence is partial: of the 21 pairs, 9 share a box at 1e10, 13 at 1e9 and 8 at 1e8.
So: a real association, concentrated in a minority of classes, not a persistent identity of boxes across horizons. The earlier "19 of 42" statistic conditioned on equal boxes and is superseded by this unconditional comparison.

## Part 2 registration (before running)

**Question.** In the 12 groups, do the rotation partners have the same *shape* (the set of touched cells, up to translation and the eight symmetries of the square) after the same number of steps, or only a bounding box of the same size?

**Prediction P1 (68% confident):** at 1e8 steps at most 2 of the 21 pairs have identical touched shapes. The trajectories of rotation partners separate within 45 steps (prefix lemma), so equal shapes at a late time would require
an exact symmetry between two different dynamical systems; I expect equal boxes to be a coincidence of scale (slowly growing patterns of similar size) with only the rotation-class enrichment to explain.
**Alternative A1:** 11 or more of the 21 pairs have identical canonical shapes: the rotated rule then builds the same object on a different background (background-independence), and the box coincidence is structural.
Between 3 and 10 is reported as mixed, with the pair list. **Control C1:** each rule's shape is compared with itself under a different horizon (1e8 vs 1e8 + 1000 steps): must differ for a growing pattern, so the test can say "different".
**Control C2:** the shape hash of a rule against its own mirror image must be equal (the hash is symmetry-canonical): must always hold.
**Instrument.** `prefix_horizon::touched_shape` (canonical hash of the touched set over the 8 symmetries and translation), oracle-tested against the reference ant (count, bounding box and hash invariance under transforms of the reference set) in `tests/prefix_horizon.rs`.
**Pruning index.** Index revision `decae71`; `rg -n -i -e rotation -e "cyclic" -e background notes/pruning-index/entries`: expected no candidate (the only entry concerns additive laws); decision run.

### Preflight correction (appended before the run)
The query for "rotation|cyclic|background" matches `NR-20261022-additive-laws-order-blind`, which *tested* complement, reversal and cyclic rotations and found the additive-law fingerprint preserved by them. Its objective (additive local conservation-law groups) and observable differ from this one (touched-cell footprint after a fixed number of steps), so it neither supports nor excludes this test. Decision: run. My line above that predicted "no candidate" was wrong.

### Instrument fix before the run
The first `touched_shape` oracle test failed (bounding box 8 against 7): the tracker counted the cell the ant stands on after the last step, which is not yet written. Size is now measured on the touched cells; the test passes on 150 random rules up to 6,000 steps and the hash is invariant under translation and two symmetries (test also checks that line and L shapes hash differently).

## Part 2 result at 1e8 (appended; `results/rotation_shapes_1e8.csv`, `examples/rotation_shapes.rs`, 2048 board, commit `b79b485`)

* **P1 (at most 2 of 21 identical) FAILED narrowly; A1 (at least 11) also failed: mixed.** 4 of the 21 pairs have identical canonical footprints after 1e8 steps. They come from just two rotation classes: `RRRRRRLLR`, `RRRRRLLRR` and `RRRRRRRLL`
  (22x22, 428 cells; 3 pairs) and `RRRRRRRLLR` with `RRRRRRRRLL` (19x20, 346 cells; 1 pair). The other 17 pairs differ, often slightly (for example 22x22:428 against 22x22:444 cells for `RRRRRRLLR` and `RRRRLLRRR`).
* **C2 held:** a rule's footprint equals its mirror image's in 21 of 21 cases (the hash is symmetry-canonical).
* **C1 as registered was ill-posed:** every footprint is unchanged between 1e8 and 1e8 + 1000 steps, so the control cannot show that the test says "different". These patterns grow far too slowly for 1000 steps to matter (boxes go from about 22 at 1e8 to 28-32 at 1e11). A usable control needs a long interval; see F1.
* Limits: a touched-cell set ignores colours and the ant's phase, so equal footprints are necessary for "the same object", not sufficient; and 4 of 21 comes from 2 classes, not 4 independent cases.

### Follow-up F1 (registered before running; extends the plan, logged as a deviation)
Classes: the two with identical footprints at 1e8 (5 rules above). Run `rotation_shapes` on their pairs at 1e9 and 1e10 steps (and each rule's own 1e8 vs 1e9 vs 1e10 footprint as the repaired C1).
**Prediction F1a (60%):** the three-rule class stays identical at 1e9; the two-rule class too. **F1b (45%):** still identical at 1e10. **Repaired C1:** footprints at 1e8, 1e9, 1e10 of the same rule all differ (boxes grow ~0.1 decades per decade).
Reading: staying identical over two more decades would show the rotated rules build the same object up to symmetry (a shared attractor, not a box coincidence); separating would show the 1e8 equality was an early coincidence.

## F1 result at 1e9 (appended; `results/f1_shapes_1000000000.csv`, commit of this entry)

**F1a FAILED:** all four pairs that had identical footprints at 1e8 differ at 1e9 (cells 568 / 576 / 554 for the three-rule class; 470 / 462 for the two-rule class, 26x26 and 23x24 boxes respectively).
The footprints stay close in size but are not the same object, so the 1e8 equality was an early coincidence, not a shared attractor. Repaired C1: each rule's own footprint changes from 1e8 to 1e9
(for example `RRRRRRLLR` 22x22:428 -> 26x26:568), so the test can say "different". (The `self_shift` columns in the CSVs still compare against +1000 steps and are uninformative; ignore them.)
F1b (identical at 1e10) is conditional on F1a and is now moot; the 1e10 run (`results/f1_shapes_10000000000.csv`) was still in progress when this was committed, so that file is **incomplete until a later commit says otherwise**.

## F1 final: 1e10 (appended; `results/f1_shapes_10000000000.csv` is now complete, 4 pairs; binary sha256 `9be39882b1dd1539...`, built at `b79b485`)

Footprint (box : touched cells) of each rule at 1e8, 1e9, 1e10 steps:

| rule | 1e8 | 1e9 | 1e10 |
|---|---|---|---|
| `RRRRRRLLR` | 22x22:428 | 26x26:568 | 28x28:684 |
| `RRRRRLLRR` | 22x22:428 | 26x26:576 | 28x29:701 |
| `RRRRRRRLL` | 22x22:428 | 26x26:554 | 28x28:684 |
| `RRRRRRRLLR` | 19x20:346 | 23x24:470 | 26x26:602 |
| `RRRRRRRRLL` | 19x20:346 | 23x24:462 | 25x26:584 |

* **Repaired C1 held:** every rule's own footprint changes at each decade, so the test can say "different".
* **F1b (identical at 1e10) FAILED as stated:** three of the four pairs differ. **But one pair re-coincides:** `RRRRRRLLR` and `RRRRRRRLL` have exactly the same canonical footprint (28x28, 684 cells) at 1e10 after differing at 1e9 (568 against 554 cells).
  The touched set only grows, so two different growth histories ended on the same canonical shape. By hash that is not a collision risk (64-bit FNV over a 684-cell set), but it is **one pair at one time**, and I have no mechanism.
* What this does and does not show. It does not support "rotated rules build the same object": three of four pairs differ at 1e9 and 1e10, and the 1e8 equalities were early coincidences. It leaves open that distinct rules may fill toward a common envelope at different paces
  (suggested only by the 1e8 and 1e10 coincidences of one class; untested). A footprint ignores colours and the ant's phase, so even exact equality of footprints would not make the objects equal.
* **Q25 summary.** (1) Rotation-related pairs share bounding boxes far more often than composition-matched controls (real, concentrated in about 10% of rotation classes). (2) That is not a persistent shared structure: box equality at earlier horizons holds for 8-13 of the 21 pairs, and
  footprints coincide at 1e8 for two classes, separate at 1e9, and (one pair) coincide again at 1e10. (3) The background-independence idea (a rotation is the same rule on a uniform non-zero background) is neither supported nor excluded; the direct test (run the original rule on each uniform background and compare to the rotation) was not done.
  No pruning-index signature: the evidence is observational and the one re-coincidence is unexplained.

## Part 3: the uniform-background test (registered 2026-10-25 before any code or run for it; base `663c0d1`)

**Identity.** `rot_k(w)[c] = w[(c + k) mod n]`: the rotated rule on a blank board *is* `w` on a board whose every cell starts at colour `k` (colour `c` of the rotated rule is colour `(c + k) mod n` of `w`).
So the rotation-pair footprints above were already uniform-background runs. What part 3 adds: (a) the identity checked directly against an oracle; (b) **all `n` backgrounds** of each rule, which includes rotations that are not census survivors or not canonical;
(c) a **length-matched control population**, because the 12 groups of box-sharing pairs were selected for sharing a box, so their coincidence rate cannot be read as a base rate.

**Design.** Classes (rotation or mirror-rotation equivalence; representative = least rotation of the rule or its mirror): *test* = the 8 classes that contain the 21 box-sharing pairs (`results/uniform_bg_classes.txt`, lines `A`);
*control* = 8 other classes with at least two survivors, one per test class of the same length, chosen by sha256("q25-control:" + representative) order (lines `B`). For each class representative `w` of length `n` and each background `k = 0..n-1` run `w` on a uniform background `k` for 1e8 and 1e9 steps (2048 board) and take the canonical footprint (`touched_shape`, up to translation and the 8 symmetries).
A pair of backgrounds *coincides* if the footprints are identical. Mirror partners need no separate runs (the hash is mirror-invariant, control C2 above).

**Registered predictions.**
* **U0 (identity, certain if I have the semantics right):** the footprint of `w` on background `k` equals that of `rot_k(w)` on a blank board, exactly, for every rule, `k` and step count tested; and the footprint of `w` on background `k` equals an independent HashMap reference with default colour `k`.
* **U1 (55%):** at 1e8, at least 4 of the 8 test classes contain a coincident pair of backgrounds.
* **U2 (60%):** at 1e8, at most 1 of the 8 control classes does. If the control rate is as high as the test rate, the coincidences are generic to small slowly-growing rules and not special to rotation classes selected for box equality.
* **U3 (92%):** no class of the 16 has identical footprints for all `n` backgrounds at 1e8 (strong background independence is false).
* **U4 (75%):** at least 70% of the coincident background pairs found at 1e8 are no longer coincident at 1e9 (as the four known pairs were).
* Decision: if U1 and U2 hold, the box enrichment is a property of the selected classes (reading: some rules reach nearly the same footprint on different backgrounds early on); if the control rate matches the test rate, the box sharing carries no information beyond "small slow growers". Background-independence is supported only by U3 failing.

**Pruning index.** Index revision `663c0d1`; same queries as above ("rotation", "cyclic", "background"): one candidate, `NR-20261022-additive-laws-order-blind`, whose objective (additive law fingerprints) differs; no exclusion. Decision: run.

### Part 3 interim result at 1e8 (committed while the 1e9 run is in progress; `results/uniform_bg_shapes_100000000.csv`, `results/uniform_bg_analysis.txt`)

* **U0 held:** `tests/prefix_horizon.rs::uniform_background_equals_rotated_rule` (200 random cases, up to 5,000 steps): the footprint of `w` on background `k` equals that of `rot_k(w)` on a blank board and matches an independent HashMap reference with default colour `k`. Not a surprise: it is a relabelling.
* **U1 FAILED as registered:** 2 of 8 test classes (needed at least 4) have two backgrounds with identical footprints. **U2 FAILED as registered:** 2 of 8 control classes do (allowed at most 1). **U3 held:** no class has all backgrounds identical.
* **Post hoc refinement (not registered; flagged):** every control coincidence is forced by symmetry. `LLRLRRLR` and `LLLLLRRRRR` are their own mirror image after rotating by n/2, so backgrounds `k` and `k + n/2` give mirror-image footprints. Excluding those, the controls have **0** coincident pairs and the test classes keep **2 classes with 4 non-trivial pairs**
  (`LLLLLLLRR`: backgrounds 0, 1, 2 all identical; `LLLLLLLLRR`: backgrounds 0 and 1) — the two classes already known from F1. So with the refinement the coincidences are specific to those two classes, not generic; without it the registered U1/U2 say they are not.
* Unplanned observation: far more backgrounds leave the 2048 board within 1e8 steps in the control classes (23 of 74 backgrounds) than in the test classes (3 of 70). The test classes were chosen for small boxes at 1e11, which apparently selects classes whose members mostly stay bounded on every background. Not tested further.
* U4 (do the coincidences vanish by 1e9) is pending the 1e9 run.

### Part 3 final (1e9 finished; `results/uniform_bg_shapes_1000000000.csv`, `results/uniform_bg_analysis.txt`, commit/binary hash in `results/uniform_bg_provenance.txt`)

| prediction | outcome |
|---|---|
| U0 identity | **held** (oracle test, 200 random cases) |
| U1 at least 4 of 8 test classes with a coincident pair at 1e8 | **failed** as registered: 2 of 8 |
| U2 at most 1 of 8 control classes | **failed** as registered: 2 of 8 (both forced by mirror-rotation symmetry; post hoc refinement: 0 non-trivial) |
| U3 no class with all backgrounds identical | **held** (0 of 16, at 1e8 and 1e9) |
| U4 at least 70% of 1e8 coincidences gone at 1e9 | **held**: 4 of 4 non-trivial pairs gone (symmetric pairs excluded as post hoc, they coincide at every horizon by construction) |

* At 1e9 the test classes show 1 non-trivial coincident pair (`LLLLLLLLRR`, backgrounds 8 and 9), a different pair from the 1e8 one (0, 1); the controls show none beyond the symmetric ones. Coincidences come and go, as the 1e10 pair in F1 also did. Counts this small (1-4 pairs, 2 classes) support no rate estimate.
* Escapes of the 2048 board: test classes 3 of 71 backgrounds at 1e8 and 3 of 71 at 1e9; control classes 23 of 71 at 1e8 and 36 of 71 at 1e9. (The interim note above gave 70 and 74 as denominators; both populations have 71 backgrounds: corrected here, no data touched.) A control class such as `LLRLRLRLR` leaves the board from 7 of its 9 backgrounds by 1e9, so the background decides whether the rule builds a highway at all.
* **Conclusion for Q25.**
  1. Strong background-independence (U3) is false everywhere tested, and for typical survivor classes the background changes the outcome qualitatively (bounded versus escaping).
  2. The rotation-pair box association from part 1 is real but concentrated in classes whose members stay small and bounded on nearly every background; there footprints are close and occasionally identical, but identity does not persist across decades (1e8 -> 1e9: 4 of 4 lost; one pair regained at 1e10).
  3. I found no evidence that a rotation is "the same object on a different background" beyond early-time footprint coincidences. A mechanism for the 1e10 re-coincidence is still missing.
  4. Limits: 8 test classes, 8 length-matched controls, lengths 7-10, footprints only (colours and ant phase ignored), horizons 1e8/1e9 (1e10 only for the F1 pairs), a 2048 board (escape means only "beyond 2048"), one representative per class.
  5. No pruning-index signature (observational; the one non-persistent coincidence pattern is not a dead-end claim).
