# Do the census highways survive a configuration-level check? (a translated-cycler decider)

Registered 2026-10-23 18:12 (+13:00), base commit `6e0840b`. **Nothing in this folder has been run** when this file is first committed.
Proof track, `notes/proof-track-2026-10-20.md` Next steps item 2 ("a highway is the m-free special case"). Sibling:
`experiments/archive/2026-10-sweeper-generalisation/`.

## Question

The census calls a rule a highway when `detect.rs` finds a position-periodic stretch of the ant's trace (`MIN_SPAN` repetitions) and
`confirm` finds the same period, drift and onset on two board sizes. That is evidence about the *trace*, not a statement about the
*configuration*: nothing there shows that the walls the ant lays down are reproduced each period, or that the cells it reads stay inside a
region that is reproduced. This experiment applies the parent's proof architecture at its simplest (no end blocks, no band lemma, m-free):
a **rectangle translated-cycler certificate**, checked by a program that shares no code with `detect.rs`.

**Theorem (to be checked, not assumed).** Let C0 be the true configuration at time t1 of a run from the infinite blank plane, with the ant
at `a` heading `h`. Let `P >= 1`, `v = (dx, dy)`, and let `W` be an axis-parallel rectangle. If

- (a) running P steps from C0 the ant only ever stands on cells of W (so it only reads W) and ends at `a + v` with heading `h`;
- (b) the configuration C1 after those P steps satisfies `C1(z) = C0(z - v)` for every z in `W ∩ (W + v)`;
- (c) `C0(w) = 0` for every w in `W \ (W - v)` (the leading edge is blank);
- (d) `C0(z) = 0` for every z outside W that lies in `W + kv` for some `k >= 1` (the strip ahead is blank);

then for every `k >= 0`, at time `t1 + kP` the ant is at `a + kv` with heading `h` and the configuration restricted to `W + kv` is C0 shifted by `kv`.

Proof sketch (to be rechecked by the program's logic and, if cheap, in Lean on the existing plane model): induction on k. A rectangle satisfies
`(W + jv) ∩ (W + kv) ⊆ W + (k-1)v` for `j < k` (per coordinate, intervals), so the cells of `W + (k+1)v` outside `W + kv` were never touched, hence
equal C0, hence blank by (d), and equal the shifted C0 there by (c); the cells inside the overlap are given by (b). The ant reads only `W + kv`
in cycle k by translation invariance. This is a *persistence* theorem from t1; it says nothing about entry (a run from blank reaches t1 by plain
simulation, which is the base case).

## Pruning-index preflight

- Index revision `6e0840bb05a1aa261c13ee1a0019550c0e92aac0`; `rg --files notes/pruning-index/entries` (one entry);
  `rg -n -i -e highway -e decider -e certificate -e translated notes/pruning-index/entries` matches only incidental words in
  `NR-20261022-additive-laws-order-blind` (its exclusions explicitly leave growth and highway questions open). No applicable signature.
- Decision: run. The objective differs (configuration-level persistence, not additive laws or growth).
- Budget: dumps of the 571 `confirmed_v2` highways (onset <= 1e8), each a single run to `onset + K*period` steps for K in {3, 10, 30, 100, 300};
  minutes on 6 cores. No census expansion, no new highway search. The 13 `confirmed_1B` rules (onset up to 6e8) only if the first pass succeeds.

## Inputs, instruments, controls

- Rules, periods, drifts, onsets: `experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv` (`period, dx, dy, onset`). Sign convention as
  `fast::run` (`DIRS = [(0,-1),(1,0),(0,1),(-1,0)]`, heading 0 = north, y down); the program checks the sign by simulation and reports mismatches.
- Dumper: new example `examples/highway_decider_dump.rs` (plain loop, same DIRS and update order as the other tracers) writes, for a rule and a step
  count, the ant state and every non-zero cell, plus the state after P further steps computed by `reference::Ant` (an independent run from step 0 on
  the HashMap ant, so it also cross-checks the dump).
- Decider: `scripts/decide.py`, Python stdlib only, its own ant, no import from `src/`; reads the dump and `(P, dx, dy)`, takes W = bounding box of
  the cells the ant stands on in P steps, checks (a)-(d). Snapshot times `t1 = onset + K*P`; every K is recorded and the first that passes is reported.
- Oracle (AGENTS.md rule 4): the Python ant's state after P steps equals the `reference::Ant` state in the dump for every dump examined
  (position, heading, hash of all cells).
- Controls (must behave as stated before the full run is read):
  (C1) one cell of C0 inside `W ∩ (W + v)` changed -> rejected at (b);
  (C2) a non-zero cell placed ahead in the strip (d) -> rejected;
  (C3) a wrong drift (dx changed by 1) -> rejected at (a);
  (C4) the same rules at a time before the onset -> no certificate;
  (C5) non-highway rules (first 50 of `non_highway.txt`) at `t1 = 1e7`, candidate `(P, v)` taken from every `P <= 3000` at which the ant's
  displacement over P steps is non-zero -> 0 certificates.

## Predictions (registered before any run)

- **D1.** At least 90% of the 571 rules receive a certificate for some K in {3, 10, 30, 100, 300} with `(P, v)` equal to the census values
  (probability ~70%). Fails if < 90%. I expect failures among rules with large period whose one-period bounding box contains cells that are not
  shift-periodic (the active region is wider than the bounding box of the path).
- **D2.** Of the certified rules, 100% pass controls C1-C3 (each applied to a sample of 50 certified rules; a failure to reject is a bug in the decider).
- **D3.** C4 and C5: zero certificates. A certificate for a non-highway or pre-onset snapshot falsifies either the decider or the census and must be
  examined cell by cell.
- **D4 (oracle).** The Python ant and `reference::Ant` agree on all dumps examined (100%).
- **D5 (impostor check).** Every census rule that fails to certify at all five K is listed with the first failing clause. If that clause is (a) (the
  ant is not back at heading `h` on `a + v` after P steps) for any rule, the census period or drift is wrong for it and the census must be corrected.

Not predicted: which rules fail, or the mean window size.

## What each outcome changes

D1 held: the census `highway` label for those rules is upgraded from trace-periodicity to a persistence theorem from t1 (modulo the fidelity of
the Python and Rust ants, which D4 checks on the examined dumps), and proof-track item 2 gets its first decider. D1 failed: the rectangle is too
crude; report why (a non-rectangular window or a longer cycle is the next design, not a retreat). A rule failing at clause (a) or (b) at *every* K
is evidence that its census label needs another look, not that the highway is false.

## Commands

Filled in as run. Builds into a fresh `CARGO_TARGET_DIR`, exit status checked, binary sha256 logged (WSL, `/mnt/f/Code/turmite`).

## Results, uncertainty and limitations

(none yet)

## Commands and results (appended 2026-10-23 18:27 +1300; the registration above is not edited)

Provenance: dumper `examples/highway_decider_dump.rs` and `scripts/decide.py`, `run_all.py` as committed in `9a4b93f` (the run used exactly those files; the controls and C5 scripts were committed after, in the following commit);
fresh `CARGO_TARGET_DIR=~/turmite-target-hd`, dumper sha256 and the census input hash in `results/inputs.sha256`. WSL, 3 worker processes (Stage 1 runs of the sibling experiment shared the machine).

```bash
E=experiments/archive/2026-10-highway-decider; B=~/turmite-target-hd/release/examples/highway_decider_dump
python3 $E/scripts/run_all.py $B $E/results/decide_all.csv --keep 60      # 571 rules x K in {3,10,30,100,300} + the pre-onset snapshot
python3 $E/scripts/controls.py $E/results/controls_c1_c3.txt               # run BEFORE the summary below was read
python3 $E/scripts/c5_nonhighway.py $B $E/results/c5_nonhighway.txt        # run BEFORE the summary below was read
python3 $E/scripts/summarise.py $E/results/decide_all.csv > $E/results/summary.txt
# extra provenance, added after the main run (new binary, sha256 in results/verify_binary.sha256): the plain loop against reference::Ant from step 0
DUMP_VERIFY=1 ... highway_decider_dump RULE T P 4096 DIR    # for the 408 rules with onset <= 3e5, T = onset + 3P  -> results/verify_from_zero.txt
```

| Prediction | Outcome |
|---|---|
| D1 >= 90% of 571 certified at some K | **Held, 571 of 571 (100%).** First passing K: 3 for 568 rules, 10 for 2, 100 for 1. Window area of the first passing snapshot: min 12, median 54, max 3190 cells. (`results/summary.txt`) |
| D2 controls C1-C3 reject (50 certified rules sampled) | **Held**: C1 (one cell changed in W ∩ (W+v)) 50 of 50 rejected; C2 (stray cell in the strip) 38 of 38 rejected (12 draws fell inside W and were not applied); C3 (wrong drift) 50 of 50 rejected at clause (a); `in_strip` agrees with brute force in 20,000 random cases. (`results/controls_c1_c3.txt`) |
| D3 C4 (before the onset) and C5 (non-highways) give no certificate | **Held**: 0 certificates among 571 pre-onset snapshots; C5: 0 certificates among 72,864 candidate (P, v) in 100 non-highway rules (the registered first 50 of `non_highway.txt` plus 50 rules of length 8-10 drawn with a fixed seed, added after registration and labelled so in the output). (`results/c5_nonhighway.txt`) |
| D4 Python ant = `reference::Ant` on all dumps examined | **Held**: 0 disagreements in 3,423 dumps (position, heading, hash and count of all cells after P steps). 3 dumps at K = 300 do not exist because the ant reached the 8192 board edge (RRLLLRLRRRL, RLRLLRLRLLRL, RRLLLRLRLRRL); those rules certified at smaller K. |
| D5 uncertified rules, clause (a) | **No such rules**: every census rule certified, so none is an impostor of this kind. |

Additional observations (not registered): the failures at some K are real obstacles rather than noise. For instance `RRLLRRLLLRLR` (P = 118, v = (1,-1)) fails clause (d) at K = 3, 10, 30 because a non-zero cell
lies far ahead in the strip, and passes at K = 100: the highway had cleared it by then, so its "clean" regime begins later than the census onset for that rule. `RLRLRLLRLLLR` and `RRLLLRRLRLRR` likewise fail at one or more small K (clauses d and b) and pass later.
Extra provenance (post hoc, results/verify_from_zero.txt): for the 408 rules with onset <= 3e5 the dump at `onset + 3P` is identical (position, heading, hash and count of every cell) to a `reference::Ant` run from step 0 in 408 of 408 cases;
the driver's own summary line in that file counted `True` where the Rust program prints lowercase `true` and said 0, which I replaced by a corrected TOTAL line in the same file (hand edit of a generated summary line; the 408 per-rule lines are untouched).

**What this earns.** For these 571 rules, at the first passing snapshot, the highway claim is no longer only "the trace repeats": the configuration reproduces itself under the translation `v` every P steps, the ant reads only a window of
median area 54 cells, and the cells ahead are blank. Given the true configuration at `t1` (obtained by plain simulation from a blank plane, validated against `reference::Ant` for 408 of the 571), the ant forever continues. **What it does not earn:** nothing about the entry
(a blank-board run reaches `t1`, which is simulation), nothing about rules not in the 571 (the 13 `confirmed_1B` rules and the later-onset 1e9..1e11 highways are untouched), and the theorem itself is checked by a program and a proof sketch; the Lean plane model of the parent
(`Plane.lean`) could host a formal proof of it but this has not been done. The certificate is conservative: it requires the untouched cells in the window to be shift-periodic, so a failure is not a refutation of a highway.

## Soundness in Lean: registration (appended 2026-10-23 18:38 +1300, before any Lean file for it exists; the sections above are not edited)

The decider is a program; its theorem so far rests on a proof sketch. A bounded deliverable: state the theorem for a **generic rule** (colour modulus `n`, turn function `turn : Nat -> Nat`, any ant of the project's family)
on the infinite-plane model already in `experiments/archive/2026-10-rlrlll-macro-transition/lean/` (`PSt`), and prove it. Planned file: `lean/Cycler.lean` in the parent folder (the plane model lives there; it imports `Model` for the heading tables).
Statement: hypotheses (a)-(d) of the theorem above, written over the plane model; conclusion: for every `k`, `runP (k * P)` leaves the ant at `a + k v` with heading `h` and the plane equal to the shifted initial plane on `W + k v`.
Proof plan: (1) a translation lemma (running a shifted plane is the shift of the run), (2) a locality lemma (two planes that agree on the cells the ant stands on give the same ant and agree there; cells never stood on keep their value),
(3) the rectangle lemma `(W + jv) ∩ (W + mv) ⊆ W + kv` for `j <= k <= m`, (4) induction on `k` with the two invariants F1 (agreement on `W + kv`) and F2 (untouched cells equal the initial plane).
Prediction: accepted by the kernel with only the standard axioms, in this session (probability ~55%; the risk is the integer-product arithmetic in step 3 and the bookkeeping of the "stood on" predicate in step 2).
Failure: a statement needing extra hypotheses (for instance blank cells ahead beyond (d)) would mean my proof sketch was incomplete and the 571/571 result would have to be re-read.
What acceptance earns: the theorem is machine-checked for the *abstract* rule; the instance checks (a)-(d) on a specific rule and configuration remain the Python decider's job (not replayed in Lean); the abstract plane ant is still not proved to be the Rust ant.

### Lean soundness: result (appended 2026-10-23 18:43 +1300; the registration above is not edited)

**Accepted (commit `12c8799`, `lean/Cycler.lean` in `experiments/archive/2026-10-rlrlll-macro-transition/`, fresh build and audit by `scripts/l5_check.sh`, `results/c3_l5_build.txt` and `c3_l5_axioms.txt` of that folder):**
`Sweeper.cycler` for a generic rule `GRule` (`n` colours, `turn : Nat -> Nat`), plane `p0`, window `inW x0 x1 y0 y1`, drift `(vx, vy)`, period `P` and start state `(a, b, h)`.
Hypotheses, in the order of the README theorem: `ha1`/`ha2` = (a) (the ant stands in W at steps 0 .. P-1 and ends at a + v with heading h), `hb` = (b), `hc` = (c), `hd` = (d).
Conclusion, for every `k`: after `k * P` steps the ant is at `a + k v` with heading `h`, the plane equals `p0` shifted by `k v` on `W + k v`, and every cell not covered by `W + j v` for `j < k` still has its initial colour.
Supporting lemmas (also accepted): `gstep_shift` / `grun_shift` (translation), `grun_agree` (locality), `grun_untouched`, `rect_mid` (`(W + jv) ∩ (W + mv) ⊆ W + kv` for `j <= k <= m`).
Axioms: `propext`, `Quot.sound`, and `Classical.choice` in `cycler` itself; no `sorryAx`, no `ofReduceBool`.

Prediction (about 55%) held: the proof needed no extra hypothesis beyond (a)-(d). The risk I named (integer products in the rectangle lemma) was handled by `omega` treating `k * vx` as an atom after the order facts `Int.mul_le_mul_of_nonneg_right` / `..._nonpos_right`.

**What this changes.** The decider is now a sound *checker of an instance* of a machine-checked theorem: if `decide.py` reports clauses (a)-(d) for (rule, dump, P, v), the Lean theorem gives persistence for all `k` for the abstract ant.
**What it does not change.** (i) The instance checks (a)-(d) are still computed by the Python program (validated against `reference::Ant` on the dumps), not replayed inside Lean. (ii) The abstract ant (`gstep`) is not proved to be the Rust ant: its `dx`/`dy` tables and update order are the model's, and agree with the oracle runs only empirically (`oracle`/D4 and the parent's C1a). (iii) The dump is the output of a plain simulation from a blank board, so each persistence statement is "from step t1 on", conditional on that simulation.

## Corrections and additions after review (appended 2026-10-23 18:49 +1300; nothing above is edited)

1. **The from-zero verification is now a committed script.** `scripts/verify_from_zero.py DUMPER OUT` regenerates `results/verify_from_zero.txt`, including its summary line (which now counts the lowercase `true` the Rust program prints); I removed the hand-replaced TOTAL line: the file is a clean regeneration, 408 of 408 identical (command:
   `python3 experiments/archive/2026-10-highway-decider/scripts/verify_from_zero.py ~/turmite-target-hd2/release/examples/highway_decider_dump experiments/archive/2026-10-highway-decider/results/verify_from_zero.txt`, binary sha256 in `results/verify_binary.sha256`).
2. **Scope of the claim, restated.** 571 rules (the `confirmed_v2` highways with onset <= 1e8); the plain-loop dump was compared with `reference::Ant` from step 0 for the 408 with onset <= 3e5, and the dumped configuration was stepped by `reference::Ant` for all of them (D4); the instance clauses (a)-(d) are computed by Python, not replayed in Lean; the Lean theorem is for the abstract ant.
3. **Falsification harness.** The highway statements here are certificates for a specific configuration, not classification claims about a rule; they were not attacked with `src/falsify*` (a perturbed start would produce a different configuration and need its own certificate).
4. **Timestamps.** The registration header says 18:12 and the registration commit `220aac1` is 18:11:47; the commit time governs (I wrote the header time from the plan, not the clock).

## Pruning-index outcome and next question

Result: 571/571 certified, controls and oracle pass. This is a positive result and a proof artefact, not a dead end, so no signature is warranted. Related existing signature checked again: `NR-20261022-additive-laws-order-blind` (unrelated objective).
Next question: the same architecture with a periodic ahead background (Q24 in `notes/open-questions-hypotheses.md`), applied first to a side of the RLLLRLRLLL spiral; the pruning-index query to be repeated for that family before any run.
