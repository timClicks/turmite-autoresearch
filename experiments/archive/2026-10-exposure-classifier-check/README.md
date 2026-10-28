# Formal check of the exposure classifier behind 2026-10-kappa-exposure-classes

Owner: Turmite Research Agent (AI research agent). Branch `turmite-research-agent/formal-checks`
(worktree off `turmite-research-agent/onboarding`). Proof track: `notes/proof-track-2026-10-20.md`
(architecture rule: acceptance only from a small, separately written checker).

## Question and registered prediction

**Registered 2026-10-25 09:14 UTC, starting revision `8a073b75aab339e492863eaa6303a7d035906162`,
before the truth-table harness or the checker has been written or run.** Nothing in this folder has
been measured yet.

The 2026-10-20 experiment (`../2026-10-kappa-exposure-classes/`) split boundary occupation by
*exposure class* and failed its P3 (frequency clause) and P4 (wrong sign). The least interesting
explanation of a failed prediction is an instrument bug. This experiment asks: **is the class that
`examples/kappa_exposure_classes.rs` assigns exactly the documented function of the neighbourhood,
and are its counts consistent with the probe's perimeter `P` that kappa uses?**

### Specification (taken from the documentation, not the code)

Sources: the doc comment of `examples/kappa_exposure_classes.rs` (lines 4-12), the 2026-10-20
README ("Question", "Instrument"), and the doc comments of `src/probe.rs` (`perimeter`,
`boundary_steps`, `fresh_nbrs`).

- S-class. For a visited cell x with visited set V, the class is u(x) = the number of its four
  4-neighbours (N, E, S, W) not in V. u in {0..4}; u = 0 is interior.
- S-boundary (probe). x is a perimeter/boundary cell iff x in V and *at least one* 4-neighbour is
  not in V. P = number of boundary cells.
- S-labels. "Flat edge" is u = 1; "corners, bays and protruding tips have u >= 2"; the main
  statistic pools u = 2, 3, 4 as "2+"; u = 4 occurs "rarely".
- S-counts. p_u = number of class-u cells at window end; b_u = steps starting on a class-u cell;
  sum_u b_u = probe `boundary_steps`; sum_u u b_u = probe `fresh_nbrs`; sum_{u>=1} p_u = probe `perimeter`.

The neighbourhood radius the documentation names is the von Neumann radius-1 neighbourhood. The
checker works on a 3x3 Moore window (all 2^9 visited patterns) so that it can also show the four
diagonal cells are irrelevant, and on a radius-2 diamond (13 cells) for the inductive update lemma.

### Properties claimed (each is either proved by z3 on the spec, checked against the Rust table, or both)

- **P1 (totality/partition).** For every visited/unvisited pattern: a cell that is a boundary cell
  in the probe's sense (S-boundary, encoded as a disjunction over the four neighbours, not as a count)
  gets exactly one class in {1, 2, 3, 4}; a visited non-boundary cell gets class 0; an unvisited cell
  gets no class (the instrument's sentinel `u8::MAX`). Proved symbolically for the spec, and the
  dumped Rust table satisfies it for all 512 window patterns and all 9 window cells.
- **P2 (agreement).** The class stored by the actual Rust code (`Region::visit` / `Region::unv` in
  `examples/kappa_exposure_classes.rs`) equals S-class for every cell of the 3x3 window, for every
  one of the 512 visited patterns and **every** visit order of the visited cells (986,410 orders);
  the incremental class counts `pc[u]` equal the recount `scan()` and the spec's counts. z3 proves
  `table == spec` as a universally quantified statement over the 9-bit pattern.
- **P3 (D4 invariance).** S-class is invariant under the 8 rotations/reflections of the square
  lattice acting on the 3x3 window (proved for the spec), and the dumped table is invariant too.
  Non-vacuity control: a deliberately asymmetric spec (count only N, E, S) must be rejected.
- **P4 (consistency with P and with the probe counters).** (a) Symbolically: sum_{u=1..4} p_u = P
  and, per boundary cell, sum_u u [class = u] = number of unvisited neighbours (so sum_u u b_u =
  fresh_nbrs). (b) Replay: for scripted walks (every 4-connected subset of the 3x3 window that
  contains the start cell, toured repeatedly; plus 64 seeded bounded random walks), the instrument's
  own `run` + `check_against_probe` path and `probe::probe_walker` agree, and the checker's own
  replay of the same path with its spec classifier reproduces area, P, new_cells, b_u, f_u, p_u,
  boundary_steps and fresh_nbrs exactly in every emitted window.
- **P5 (history independence of the incremental update, code model).** A z3 transcription of
  `Region::visit` (counter set to the number of unvisited neighbours on arrival; each visited
  neighbour decremented; `pc` moved between bins) preserves the invariant "every visited cell's
  counter = its number of unvisited neighbours, and `pc[u]` = number of cells with counter u", for
  an arbitrary visit of an unvisited cell on the radius-2 diamond, and never decrements a counter
  below 1 (no `u8` underflow). This is an induction over visit sequences, so it covers boards and
  orders the exhaustive table does not.
- **P6 (labels are counts, not shapes).** The class depends only on the four 4-neighbours (the
  four diagonals are irrelevant: proved). Consequently the geometric labels are approximate: z3 finds
  (i) a u = 2 pattern whose two unvisited neighbours are opposite (a one-cell-wide strip, neither a
  corner nor a tip) and (ii) a u = 1 pattern that is not a straight flat edge (the two diagonal cells
  on the visited side unvisited, a T-junction). Prediction: both witnesses exist. The documented
  sentence "corners, bays and tips have u >= 2" is one-directional and stays true; the converse
  reading "u = 2 cells are corners" is false.
- **P7 (u = 4 never occurs in analysed windows).** For any walker that moves to a 4-neighbour each
  step (ant, rotor, random walk; mean-field steps from a visited cell to a neighbour), every visited
  cell has a visited neighbour once area >= 2, so p_4 = 0 and b_4 = 0 after the first step; the
  "2+" pool is really u in {2, 3}. Check: every row of the committed
  `../2026-10-kappa-exposure-classes/results/classes.csv` (k >= 9) has p4 = b4 = f4 = 0, and so do
  the scripted walks. (I have not looked at those columns.) Paper proof in the results section;
  not a z3 proof (it needs connectivity).

**Prediction: P1-P7 all hold**; I expect no instrument bug, because the 2026-10-20 `--check` mode
already compared every window with `probe_walker` and a board recount on all 344 runs. The new
content is (a) a universally quantified match with a documentation-level spec over all local
patterns and orders, which the runtime checks did not give, and (b) P6/P7, which bear on how the
P3/P4 verdicts may be read. **Failure criteria:** any z3 `sat` on a negated property, any table row
differing from the spec, any replay mismatch, or any nonzero p4/b4 in `classes.csv`. A failure of
P1-P5 would mean the 2026-10-20 class split is wrong and its P3/P4 verdicts must be re-evaluated
(appended, never edited). Negative controls (must be **rejected**): (N1) the table mutated by
clipping the class at 2 (the 2026-10-20 mutant); (N2) a single flipped entry; (N3) a walk row with
b_2 incremented by one; (N4) the asymmetric spec in P3; (N5) a Moore-count spec (8 neighbours)
compared with the table.

Competing explanation for the 2026-10-20 failures that this experiment cannot touch: exposure is
confounded with cell age, colour phase and depth. A clean pass here removes only the bug explanation.

## Pruning-index preflight

- Index revision `8a073b75aab339e492863eaa6303a7d035906162`; `rg --files notes/pruning-index/entries`;
  `rg -n -i -e exposure -e classifier -e "exposure class" -e z3 -e formal notes/pruning-index/entries`.
- Candidate signature IDs: none (no matches). The only entry, `NR-20261022-additive-laws-order-blind`,
  concerns additive conservation laws, not instruments.
- Decision: RUN. This is a finite instrument check, not a sweep; compute budget: seconds.

## Reproduction

(Filled in after the run.)

## Results, uncertainty and limitations

(Appended after the run; the registration above is not edited.)

## Reproduction (appended 2026-10-25 09:32 UTC; the sections above are not edited)

From the repository root (Rust 1.98.1, uv; CPU only, about 7 minutes total, almost all in z3's P3 table checks):

```bash
CARGO_TARGET_DIR_FRESH=$(mktemp -d) sh experiments/archive/2026-10-exposure-classifier-check/scripts/run_dump.sh
uv run --script experiments/archive/2026-10-exposure-classifier-check/scripts/check_classifier.py \
  > experiments/archive/2026-10-exposure-classifier-check/results/check.txt
uv run --frozen experiments/archive/2026-10-exposure-classifier-check/scripts/build_notebook.py
```

- Harness: `examples/exposure_classifier_check_dump/` (`main.rs` + `instrument_body.rs`, a verbatim copy of lines 20-248 of
  `examples/kappa_exposure_classes.rs`; the binary asserts at run time that the instrument contains it byte for byte).
  `results/dump.log`: commit `52bcd60`, clean `src/` and `examples/`, binary sha256 `bade9373…5dc4` (identical in two fresh
  target dirs), instrument sha256 `5ad6e2f3…2cb3`.
- Outputs: `results/table.csv` (512 patterns, sha256 `f9e0ae56…cdeb`), `results/walks.csv` (576 windows of 224 walks,
  `b1d9cc6f…a99a`), `results/paths.csv` (the walks' step directions, `fe9a58da…2a7f`).
- Checker: `scripts/check_classifier.py`, PEP 723, `z3-solver==4.13.4.0` (the pin of PR #15's `prove_prefix.py`, so the
  two z3 artefacts agree; z3 reports 4.13.4, Python 3.12.15). It reads only the dumps and the committed 2026-10-20
  `classes.csv` (sha256 `50ca6573…4f79`) and imports nothing from the repository. Its own sha256 and all input hashes are
  the first lines of `results/check.txt`.

## Results (appended 2026-10-25 09:32 UTC)

**65/65 checks as expected (`results/check.txt`): P1-P7 hold, and all six negative controls are rejected.**

| Property | Result | How |
|---|---|---|
| P1 totality/partition | **held** | z3, 9 cells × all 512 patterns; class from a count and from a subset enumeration agree; boundary ⇔ exactly one of C1..C4 |
| P2 Rust table == spec | **held** | z3: table (as a 512-way ite) == spec for all 9 cells and pc[0..4]; 986,410 visit orders enumerated, one outcome each, pc == scan() every time |
| P3 D4 equivariance | **held** | z3, 8 symmetries, spec and Rust table |
| P4a count identities | **held** | z3: Σ p_u = P; per boundary cell Σ u[C_u] = #unvisited neighbours |
| P4b replay | **held** | own replay of 224 walks (160 tours + 64 bounded random walks), 576 windows: area, p_u, new_cells, b_u, f_u and the probe's area, P, new_cells, boundary_steps, fresh_nbrs all exact; 0 mismatches |
| P5 `Region::visit` induction | **held** | z3 code transcription on the radius-2 diamond: invariant and pc bookkeeping preserved, no u8 underflow, pc index in 0..4 (frame for far cells by argument) |
| P6 counts, not shapes | **held** (as predicted) | diagonals irrelevant (spec and table); witnesses: u = 2 strip `000111000`, u = 1 T-junction `010011010` |
| P7 no u = 4 | **held** | p4 = b4 = f4 = 0 in all 576 walk windows and in all 6,154 rows of 2026-10-20 `classes.csv` (k = 9..26). Reason: the visited set is 4-connected with ≥ 2 cells after the first step |
| N1 clip-at-2 table | rejected (sat) | |
| N2 one flipped entry | rejected (sat) | |
| N3 walk row b2 + 1 | rejected (1 mismatch) | |
| N4 asymmetric N,E,S spec | rejected (not equivariant) | |
| N5 Moore 8-count spec | rejected (≠ table) | |
| N6 mutant `visit()` (E neighbour not decremented) | rejected (sat) | added beyond the registration, as a control on P5 |

**Impact on 2026-10-20 P3/P4 (registered predictions not edited).** The classifier is correct against its documented spec,
so the computed b_u, f_u, p_u and hence Q and the P3/P4 verdicts stand as recorded (P3 failed on its 75% clause; P4 had the
wrong sign). Two qualifications concern only the *words* attached to the classes: (i) "2+" is in practice u ∈ {2, 3}
(P7), so "tips" (u = 3) are the only extreme class; (ii) u = 2 includes one-cell-wide strips (opposite open neighbours)
as well as convex corners, and u = 1 includes T-junction-like cells whose diagonals are open (P6). "Flat edge vs corners,
bays, tips" is therefore a reading of an exposure count, not a shape classification. Nothing in the record measured the
mix of strips vs corners within u = 2.

**Limitations.** P2 is exhaustive on a 3x3 window (the class depends only on the 4-neighbourhood, so every local
configuration of a centre cell and its 4 neighbours appears), but the incremental counters are tested end-to-end only on the
scripted walks and by the P5 induction, whose frame step for cells outside the diamond is a paper argument. The checker
validates the instrument's classification, not the 2026-10-20 statistics pipeline (`analyse.py`) downstream of it. Level on
the proof track: an instrument check (level 3 for the classifier lemma), not a result about ants.

## Reproduction on later revisions — appended 2026-10-25 09:39 UTC

The harness guard (`main.rs`: `instrument_body.rs` must be a verbatim substring of
`examples/kappa_exposure_classes.rs`) pins the instrument as it was at `52bcd60`, i.e. the code that
produced the 2026-10-20 data. On `turmite-research-agent/onboarding` the review commit `0a010ff`
added the `Shadow` per-step check and a clippy rewrite of one loop, so after merging this branch
there (`05de7b2`) the guard refuses to run, by design. To reproduce the dumps, check out `421d477`.
Scratch cross-check (not committed): at `05de7b2`, with `instrument_body.rs` replaced in a temporary
worktree by lines 25-309 of the post-review instrument, a fresh-target build of the harness wrote
`table.csv`, `walks.csv` and `paths.csv` byte-identical (`cmp` silent) to the committed ones. So the
post-review instrument classifies identically on all 512 patterns and 224 scripted walks.
