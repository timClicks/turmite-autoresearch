# Q20 follow-up: a proof plan for the square-ring fillers (2026-10-25)

**STATUS: PLAN, NOT A RESULT.** Nothing here has been measured, proved or checked. No predictions in this note are registered.
They are drafts to register, with a base commit, in a future experiment folder before anything is run. Author: Grok Bot
(executor subagent), from the record at `8a073b7` plus open PR #11 (`ccr-e81a847a-srmhih`, not merged when this was written).
If #11 changes before it merges, re-read it. This plan builds on #11 and does not repeat it.

## What PR #11 already establishes, and what it leaves open

PR #11 is `experiments/archive/2026-10-square-ring-fillers/`, "Square-ring fillers: why R^k L R^(k+2)… fills at 2(k+1) steps per
cell".

**Proved by hand for every k ≥ 1 (README, "The crawler lemma"):** the edge lemma. Let `Pi(k)` be the condition `T(k) = L` and
`T(v) = R` for the other v in `[0, 2k+1]`, where `T(v) = rule[v mod n]`. Under `Pi(k)`, the three-row edge configuration `C_k`
becomes `C_k` shifted by (-4, 0) after exactly `8(k+1)` steps. In that period each count 0..2k+1 is read four times, and no
other count is read.

**Checked by program for k = 1..64 (P1):**
- 320 rules.
- Read-letter flips fail and unread flips do nothing.
- A Python oracle agrees.

**Observed, not proved:**
- The corner gadget and the claim that it needs `T(2k+2) = R` (P5, 3 transplants).
- The ring's persistence.
- The exact revolution clock `dt = 8(k+1)·swing + b_(r mod 2)` (P2, 25/25 rules).
- The exit quadratics `E(G) = 2(k+1)G² + βG + γ`, which predict 12/12 exits to the step (P4). β and γ are fitted, not derived.

**Open (#11's own list, plus Q27 and Q29):**
- the corner lemma
- the ring as a proved macro-transition
- onset from a blank board (218/361 Pi rules reach the ring by 2^27; Q27)
- the reversed family `R^(k+1) L R^k` (Q29)
- 2 ring-footprint rules outside Pi
- the k = 0 / two-visit builders

**Assurance status of the edge lemma.** Under the architecture rule of `notes/proof-track-2026-10-20.md`:
- The per-k instances k ≤ 64 are checker-accepted (level 3, per instance).
- The all-k statement is a paper proof. No independent checker has replayed its phases symbolically in k.

## Target theorem (to be checked, not assumed)

Fix k ≥ 1 and a rule satisfying `Pi(k)`. A cell's colour is its visit count mod n. The model below works with visit counts
`v ∈ ℤ≥0` and `T(v) = rule[v mod n]`, so short rules that qualify by wrap-around (for example `RLRR`) are covered.

**Macrostate `R(L, δ, q)`.** This is a ring configuration at a fixed phase: the crawler has just arrived at the start of the
north side, in the orientation of `C_k`. It has three parts:
- a territory whose outer boundary is an axis-parallel rectangle of width `L` and height `L + δ`
- on each side, the three-row profile of `C_k` (rows a-pairs / (c,b)-pairs / d; `a = k, b = k+1, c = 2k+1, d = 2k+2`), at the
  side's column phase mod 4
- corner cells as observed: a diagonal trail of `2k+3` at one corner type and `2k+1` at others (#11, P5 text; **not counted yet**)

`q ∈ {0, 1}` is the phase that #11's clock shows as `b_(r mod 2)`. The predicate constrains **only the cells the ring can read**:
- the profile rows
- the one interior cell per corner that the corner gadget reads
- the cells of the corner trail it rereads, if any

Deep interior content, including the seed blob, is left free. The real board is never "ideal": the parent experiment's `Good`
predicate (L5) had to be weakened in exactly this way. So this must be in the definition from the start.

**Inductive step (one revolution):** `R(L, δ, q) → R(L + 2, δ, 1 − q)` in exactly

    T_rev(L, δ, q) = 2(k+1) · ΔA(L, δ) + e_k(δ, q)

steps, where:
- `ΔA = 2(2L + δ) + 4` is the number of cells whose visit count reaches d during the revolution. Each side moves out by one
  row, and the corners add 4.
- `e_k(δ, q)` is a finite corner excess, independent of L, to be extracted from the corner lemmas.
- Two revolutions, `R(L) → R(L + 4)`, return to the same column phase mod 4. This is the expected reason the phase period is 2.
  It is a hypothesis to check, consistent with #11 P2's p ≤ 2.

**Where `2(k+1)` and the perimeter term come from.**
- The edge lemma moves 4 columns of the profile out by one row per `8(k+1)` steps. A cell crosses the profile in two crawler
  passes and leaves it with exactly `d = 2(k+1)` visits. Steps per filled cell are therefore `2(k+1)`, the leading term of
  `T_rev`.
- Summing over revolutions up to a board of side G gives `E(G) = 2(k+1)·A(G) + Σ_r e_k(δ, q_r)`. There are about G/2
  revolutions, so the corner excess contributes a term linear in G.
- `A(G) ≈ G(G − δ) + O(G)` contributes `−2(k+1)·δ·G`.

The registered B1 failure of the late-highway board check was exactly this `βG` term (#11 P4). The plan predicts β from δ and
the corner costs. Until now β has only been fitted.

**What "proved" would mean:** for every L ≥ L0(k), `R(L, δ, q)` reaches `R(L + 2, δ, 1 − q)` in `T_rev` steps. By induction,
the ring persists forever on the infinite plane with the exact clock. That is a column-sweeper-shaped theorem
(`C(L, q) → C(L + g, q')`, vocabulary table of the proof-track note) with g = 2 per revolution, or g = 4 per phase period.

## Level on the proof track

| Statement | Level |
|---|---|
| Edge lemma per k ≤ 64 | **3 per instance** (already done, #11 P1) |
| Edge lemma, all k | **2+**: paper proof plus instance checks. **Target 3** via a symbolic-in-k checker (O1) |
| Ring macro-transition `R(L) → R(L+2)` for each census k = 1..7, all L | **target 3**: the first level-3 object for a 2D filler. Same shape as the RLRLLL column sweeper |
| The same, uniformly in k (one argument for every `Pi(k)` rule) | **target 4**: one proof template for a family of rules, for a structural reason (square loops plus the L at count k) |
| Lean | optional, after the above. The `Cycler.lean` / `PlaneForever.lean` style would carry over |

## Finite obligations and how to discharge them

Each obligation names its checker. The architecture rule applies throughout:
- the checker is written separately from anything that found the conjecture
- it replays against `src/reference.rs` semantics (DIRS = N, E, S, W with y south; turn then move; increment the colour mod n)
- it records the checker version and input hashes

**O1. Edge lemma, symbolic in k (closes "all k" at level 3).** Work in PR #15's z3 style (`prove_prefix.py`):
- the grid is an SMT array `ℤ → ℤ → ℤ`
- k is a symbolic integer ≥ 1
- `T` is an uninterpreted function constrained by `Pi(k)`

#11's seven phases each become one obligation:
- phases 1, 2, 4, 5 and 7: straight-line traces of fixed length
- phases 3 and 6: loop invariants indexed by j or i with `1 ≤ j < k`, stated as one 4-step round preserving the invariant
  plus exit at j = k

All of this is quantifier-free linear arithmetic over arrays, except the "unchanged outside" frame. That frame can be stated
as a `ForAll` over cells, as #15 does, or replaced by tracking the 15 cells of columns -4..0 × rows -1..1 explicitly. The
second option is preferable because it keeps the obligations decidable.

Outer composition: `5 + 3 + 4(k−1) + 2 + 4 + 4(k−1) + 2 = 8(k+1)`, plus the final-configuration equality.

Negative controls that z3 must report as sat:
- flip one `T(v)` for symbolic `v ∈ [0, 2k+1]`
- shift the L to `k ± 1`
- drop the `T(2k+1) = R` constraint

This obligation is uniform in k by construction, because the geometry is k-independent and only the counts are symbolic.

**O2. Iterated edge (symbolic in the side length).** The edge configuration is 4-periodic ahead of the crawler, so this is a
translated cycler with a **periodic, non-blank ahead background**. The highway decider
(`experiments/archive/2026-10-highway-decider/`) cannot certify it as it stands, because its condition (d) requires a blank strip
ahead. Generalising (c) and (d) to "ahead equals a shift-periodic background of period v" is exactly Q24's open extension. It
would be reused here, and it is the cheapest piece of new machinery.

Lean already has the iteration theorem shape (`Sweeper.cycler`, `PlaneForever.forever`).

**O3. Corner lemmas, per fixed k (new; the main risk).**
- Enumerate the corner cases: 4 corners × side-length phase mod 4 × q. #11's snapshots show two corner types (diagonal 2k+3
  vs 2k+1), so expect at most 32 cases per k, many related by the ring's rotation.
- For each case, obtain the trace from a simulation (conjecture generator) and state it as a finite lemma. The lemma's input
  is an ideal corner window: the incoming side's profile at its phase, the outgoing side's profile, and the interior d-cell(s).
  Its output is `C_k` on the outgoing side at a stated column phase, after a stated number of steps.
- Discharge per k by an independent replay checker. This is cheap: each window is bounded, and per-k is a finite
  computation. Use the exact-cone criterion of the parent experiment's Task C2: on every cell the ideal ant visits, the real
  configuration equals the ideal one. The observed margins were too small once before, so do not hard-code a cone.
- Uniform in k: only if the corner trace turns out loop-structured like the edge (fresh plaquettes looped while below k).
  Then discharge it as O1. Otherwise uniformity in k stays open, and the theorem is per k = 1..7.

**O4. Composition and clock (symbolic in L, then arithmetic).**
- One revolution is corner ∘ edge^(m_N) ∘ corner ∘ edge^(m_E) ∘ … . Each `m_side = (side length − corner overlap)/4` is
  linear in L and δ, and requires each side length's residue mod 4 to match the corner case used.
- Check the interface conditions symbolically in L with a linear-arithmetic predicate for `R(L, δ, q)`. Each corner's output
  must satisfy the next edge's input predicate on its read cone, and the configuration after the last corner must equal
  `R(L + 2, δ, 1 − q)` on the read cone. A z3 encoding with L, δ symbolic and the profile given by `x mod 4` cases is
  feasible. It is the same kind of obligation as PR #15's lift lemmas.
- Sum the steps to obtain `T_rev` in closed form, then `E(G)` once the board's exit event is added.
- Check the closed form against #11's fitted quadratics **before** any new run. For RLRRRRL `4G² − 49G + 1420`, for RRLRR
  `6G² − 49G + 773`, and for RRRLRRRRR `8G² − 65G + 2363`, β and γ must come out exactly. This is a strong test: three
  integers per rule, fitted elsewhere and not tuned here.

**O5. Frame / light cone.** Prove that a revolution reads only the cells the predicate fixes. This is the same obligation
as O1–O4's explicit cell lists. Done together with them, it is not a separate checker.

## What it would NOT prove

- **Entry.** Nothing above says a run from a blank board, or from a 5×5 random patch, ever reaches `R(L0, δ, q)`. #11 P6:
  only 218 of 361 Pi rules (length ≤ 12) are rings at 2^27 from a blank board, and some never fill from a blank board
  (`RLRR`, `RLRRR`, `RRLRRR`). Entry is Q27 and needs a separate certificate per seed: a long-transient "entry problem" in
  the vocabulary table. At best it is a finite replay of one seed up to the base case, as the RLRLLL base case was done.
- **`RLRRRRLRR` in particular.**
  - *Turn table:* it **is** in the family. `T(0..4) = R L R R R` satisfies `Pi(1)`, and its prefix is `R^1 L R^3`, which is
    `R^k L R^(k+2)` with k = 1. The ring would never read its letters `T(5..8) = R L R R`.
  - *Blank board:* it is **not** a filler. #11's `results/p6_classes.csv` classifies its blank-board run as `other` / blob,
    232 steps per visited cell at 2^27, 577,722 cells.
  - *Patched starts:* the 2026-10-20 kappa run found that its patched starts `@1` and `@3` fill at exactly 0.250116
    births/step, about 3.998 steps per cell. That matches the k = 1 rate, and #11 reports 3.998–4.001 steps per cell for
    k = 1 rings.
  - *Conclusion:* it is a Pi(1) rule whose ring entry depends on the seed. It is a concrete instance of Q27, not a different
    filler. However, the kappa instrument recorded no read histogram or clock, so "the patched fill is the ring(1) crawler"
    is **inferred from one number and not observed**. Draft prediction F1 below makes it checkable.
- **`RLLLRLLL@2`** (0.4998 births/step, about 2 steps per cell; 2026-10-20). It is not in `Pi(k)` for any k ≥ 1. It
  starts `RLL`, the mirror-image k = 0 two-visit edge of #11's post hoc table, so it is outside this theorem.
- **Other families:** the reversed family `R^(k+1) L R^k` (Q29), the two ring-footprint rules outside Pi (`RRLLLRLLLRLL`,
  `RRRLRRLLRRRR`), and the spiral builders (Q23).
- **Finite boards.** The plane theorem plus an exit event gives E(G), but the exit itself (which side, which parity) is a
  separate finite check per G. #11 P4 observed it to be stable for G = 2^j.
- **Fidelity.** The z3 and replay models must be shown to agree with `reference::Ant` on instances. A Lean model, if used,
  would carry the same caveat as `Cycler.lean`.

## Prerequisite empirical observations (cheap; to be measured, then frozen, before writing the lemmas)

1. Corner-case census for k = 1..3: the list of corner phases met in 2^27-step runs of the 25 board fillers, and whether the
   set is closed (no new case after revolution r0).
2. Count the corner trails: their cells, visit counts (2k+1 / 2k+3) and whether they are ever reread. The predicate depends
   on this.
3. Aspect δ per rule, and whether δ is constant after onset (#11 says the b offsets are seed-dependent, which suggests δ
   differs between rules).
4. The read cone of one revolution, in cells beyond the profile, per corner case.

## Draft falsifiable predictions (to register later; NOT registered here)

- **F1 (`RLRRRRLRR` patched starts are ring(1)).** Rerun `RLRRRRLRR@1` and `@3` with the 2026-10-20 patch seeds through #11's
  footprint instrument, final window 2^24 steps.
  - Prediction: reads confined to 0..4; counts 0..3 each within 2% of 1/4; count 4 < 0.5%; an exact clock with slope 16 in
    all four directions.
  - `@2` and `@4` are not rings.
  - Falsified by any read count > 4 at more than 0.5%, or by no exact clock.
- **F2 (closed corner set).** For each of the 25 census fillers, the corner cases from observation 1 form a set of at most
  32 per k, with no new case after the first 10% of revolutions.
- **F3 (derived β).** The corner lemmas plus δ give β and γ equal to #11's fitted values exactly for RLRRRRL, RRLRR and
  RRRLRRRRR, and predict β for the other 22 census fillers from their measured δ, before any of their exits are compared.
- **F4 (edge lemma symbolic in k).** O1 discharges with all obligations unsat, and the three negative controls are sat.
  Expected, since #11 has the paper proof, and it is a check on the transcription.
- **F5 (uniformity in k of the corner).** The corner traces for k = 1..7 share one loop structure (phase lengths affine in
  k). Low confidence, and the most informative of the five: it decides whether the family theorem is level 4 or stays per k.

## Effort and risks

- **O1:** about half a day. #15's z3 harness is the template, and the trace is in #11. Risk: low.
- **O2:** about one day. It extends the highway decider with a periodic ahead background, and also answers part of Q24.
  Risk: moderate (soundness of the periodic-background condition; a Lean statement would help).
- **O3:** 1–3 days per k. Risk: **high**. Corners may have more cases than expected, phase may depend on δ mod 4, and the
  cone may be larger than snapshots suggest (Task C2's cone was too small once). If the corner set is not closed, the
  macrostate needs a larger phase variable or the plan fails as stated.
- **O4:** about one day once O3 exists. Risk: the aspect δ may drift, so `R(L, δ, q)` would need δ(L). The definition of
  `ΔA` at corners is easy to get off by one, and F3 is the guard against that.
- **Entry (Q27):** not in scope. Any claim about blank-board fillers needs a per-seed base case.
- **Cost of not doing it:** the 2(k+1) law and the exit quadratics remain level-2 regularities with a level-3 edge.

## Links

Q20, Q27, Q29 and Q24 in `notes/open-questions-hypotheses.md`; `notes/proof-track-2026-10-20.md`; PR #11
(`experiments/archive/2026-10-square-ring-fillers/`); PR #15 (`experiments/archive/2026-10-prefix-causal-horizon/`, z3 conventions);
`experiments/archive/2026-10-highway-decider/`; `experiments/archive/2026-10-rlrlll-macro-transition/` (Task C2 cone criterion, L5
`Good`); `experiments/archive/2026-10-kappa-exposure-classes/` (RLRRRRLRR@1/@3 numbers);
`experiments/archive/2026-10-invariant-mining/`. Additive invariants give necessary constraints only. The colour-clock balance
`Σc − t mod n` is consistent with every cell ending at d visits, but does not help with the corner.
