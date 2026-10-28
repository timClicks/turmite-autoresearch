# Proof track: from simulated regularities to checked macro-transitions (2026-10-20)

## Instrument addition — 2026-10-22

[Additive modular mining](../experiments/archive/2026-10-invariant-mining/README.md)
provides exhaustive candidates in a declared ansatz and checks every local
transition. Use `cargo run --release --locked --bin invariants -- RULE ...`
before interpreting growth metrics; the experiment wrapper records provenance.
This supplies necessary constraints, not highway or growth certificates.
Colour-shift symmetries require transforming the initial field; they do not
identify distinct blank-background trajectories automatically.

Started 2026-10-20 from a proposal by the project owner. This runs **in parallel with** the empirical programme. It does
not replace it, and it reuses the same oracle, records and registration rules. Experiments live in their own folders as
usual; this note holds the cross-cutting plan and what counts as success.

## Why run it alongside the empirical work

The empirical track asks *how much* (exponents, prefactors, kappa, the c law) and answers with calibrated estimates. The
proof track asks *must it continue, and why*, and answers with a finite obligation that a checker accepts or rejects.
The two tracks feed each other:

- Simulation supplies the conjectures: a period-3 wake, a cycle time proportional to height, a bounded reach behind the
  front. Without those observations there is nothing to prove.
- A proof turns a fitted law into an exact one, and can say which part of a fit is finite-size. For example, if the
  RLRLLL sweeper is the macro-transition proposed in `experiments/archive/2026-10-rlrlll-macro-transition/`, the fitted
  `|x|^2 = 0.8634 t - 1.09e10` should have true asymptotic slope 0.75, not 0.86.
- A *failed* abstraction is informative too: if no bounded-reach macrostate exists, the behaviour needs its wake as
  state, which is a precise statement of why it resists simple description.

Compute does not conflict: the proof track needs single long runs (minutes on one core) and small finite checks, not
sweeps. It should not start heavy jobs while the 10^11 census holds the cores (`notes/ACTIVE.md`).

## Levels, and what counts as each

1. **Simulation**: a rule does X over a finite interval (the existing record).
2. **Experimental mathematics**: a regularity stated exactly enough to fail (zero-residual clock, exact block decomposition),
   registered before measurement.
3. **Formal analysis**: a finite proof obligation (base case plus induction step over a parameter such as column height),
   discharged by a checker independent of the code that found the conjecture.
4. **Theory**: the same theorem, or the same proof template, holding for a family of rules for a structural reason.

## Vocabulary of mechanisms (candidate formal objects)

| Structure | Formal object | Repo source |
|---|---|---|
| Highway | translation-periodic orbit (finite check) | `src/detect.rs`, census |
| Column sweeper | parameterised inductive invariant `C(L, q) -> C(L+g, q')` | `notes/g1-builder-structure-2026-10-14.md` |
| Crystal ray | finite-state transducer / regular language of ray words | `experiments/archive/2026-10-crystal-rules/` |
| Tethered ant | trapping certificate: invariant region the ant cannot leave | `experiments/archive/2026-10-tether-rules/` |
| Boundary excursion | return map on boundary states (must be shown well defined) | `experiments/archive/2026-10-t1-excursion-tomography/`, kappa work |
| Long transient | transition between metastable macrostates (entry problem) | `experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/` |

## Architecture rule

Conjecture generators (agents, scripts, search) may be wrong; they propose blocks, phases and invariants. **Acceptance
comes only from a checker**: a small, separately written program (or proof assistant) that replays the finite lemmas
against `src/reference.rs` semantics. An agent may not mark a statement proved on its own say-so. Every checked theorem
records the checker's version and input hashes, like any other result.

## Known limits (stated up front)

- A proof that a macrostate persists is not a proof that a blank-board run enters it. For RLRLLL, persistence and entry
  (at ~1.2677e10 steps) are separate problems; entry may be out of reach.
- Undecidability rules out a general procedure for all rules, not strong theorems about subclasses.
- The cube-root growth of chaotic rules is a statistical claim; the proof track does not expect to prove it soon. The
  diffusive heuristic `dL/dt ~ 1/L^2` is already close to the existing transport decomposition (`c kappa`, boundary access);
  a useful contribution would be a *model class* in which that heuristic is a theorem, not a proof for real ants.

## Prior art to check (from memory, not yet verified against sources)

- Busy Beaver Challenge (bbchallenge): deciders for translated cyclers and "bouncers" (machines sweeping a growing tape),
  and a Coq-checked BB(5) proof (2024). Bouncers are the 1D analogue of the column sweeper; their shift-rule induction is the
  template for Stage 2 here. A turmite is a 2D Turing machine, so the analogy is direct.
- Gale, Propp, Sutherland and Troubetzkoy, "Further travels with my ant" (Math. Intelligencer, 1995): proofs of symmetric
  growth for some generalised ants. Bunimovich and Troubetzkoy (1992): the unbounded-trajectory theorem for Langton's ant.
- Gajardo, Moreira and Goles (2002): Langton's ant is computationally universal (limits on what can be decided).

These must go through the literature-review process (`experiments/archive/2026-10-literature-review/`) before being cited
in the paper.

## Experiments in this track

- `experiments/archive/2026-10-rlrlll-macro-transition/`: is the RLRLLL sweeper a macro-transition (Stage 1 measurement,
  predictions P1-P5 registered at `4bc029a`), and if so, can it be checked for all heights (Stage 2)?
  **Result (2026-10-20):** P1-P5 held; the three-phase family is closed for all even m >= 2 (checker plus brute-force
  cross-checks and negative controls). First level-3 result of the track; see that README for what it rests on.
  **Entry (2026-10-21):** the cell-level family holds from step 12,676,237,591 (C(4,1) at x = -1552; base case moved 769,586 steps earlier, 184,176 before the edge crossing); the clock formula extends exactly to m = -24 (x = -1510, height-19 first column), so the wedge does not start at zero height; registered E1, A2, B2 failed. The 3-row light-cone margin is observed, not derived from the checker.
  **Task C (2026-10-21):** (C1) an independent second checker (stdlib Python, own ant, own pipeline S1 . descent^n . S3 . return^n . S5; `c1b.py`) reproduces 12m + 934/1058/898, lemma periods 2 (20 and 4 steps), m0 = 2, and 150 brute-force cycles; its ant agrees with `reference::Ant` on 1e6 steps and 12 windows; controls: broken ants and a mutated bulk cell rejected as registered, `RLRLLR` rejected at a different place than the first checker (scored split). (C2) cycles visit at most 2 rows above and 1 below their rectangle and up to 18 columns east of the front; the exact criterion (real configuration = ideal initial configuration on every cell the ideal ant visits, 97 cycles) passes in 50 of 50 windows including the base case C(4,1), but Task A's cone (3 + s//3) was too small (excess up to 7 rows); registered C2a failed. (C3) Lean 4: frame lemma and the two shift lemmas as iteration theorems for all n, six kernel-decided certificates (`experiments/archive/2026-10-rlrlll-macro-transition/lean/`); the end runs, composition and cycle-to-cycle padding are still paper steps.

## Next steps (proposed, none started)

1. *Assurance* (updated 2026-10-22, L4): Lean now accepts S1/S3/S5, bounded band inductions, the composition identity for all n, and the complete single-cycle clocks and first arrival at column -3 (`f90733c412c95029da2eafeaa8923a69339bc2a6`; experiment README, L4 continuation; `results/c3_l4_build.txt` and `results/c3_l4_axioms.txt`). Still open: cycle-to-cycle padding/infinite-plane closure (outputs have 12/14/13 blank rows above and 13 below, while inputs own 14 on both sides), and the independent long base-case re-simulation. This is not a Lean proof of infinitely many cycles or blank-board entry.
2. *Generalise the checker*, not the rule: run the same propose-then-check loop on the other no-highway escapes
   (`RLLLLRRL`, `RLLLLRLRRL`, `RLLLRLRLLL`) and on every census highway (a highway is the m-free special case). A
   "sweeper decider" over the census would be the proof-track analogue of the bbchallenge deciders.
3. *Entry* (mostly done 2026-10-21): family at the cell level from m = 4, clock to m = -24; cone margin derived (exact criterion, Task C; the observed 3-row margin was too small); open: explain the clock at m < 2, and what at the blob NW corner makes a height-19 first column.
4. *Explain, not just certify*: why the bulk row is `14435435...` and why the colour period is 3 for a length-6 rule.

## Status update 2026-10-23 (appended; the plan above is not edited)

- **Assurance (item 1):** the L4 caveats "multi-cycle padding" and "infinite-plane closure" are closed for the ideal plane: `Plane.lean`, `PlaneChain.lean`, `PlaneForever.lean`
  (`forever`, `forever_ideal`) prove, for every number of cycles, that the plane carries the next window; `scripts/l5_check.sh`, axioms propext/Classical.choice/Quot.sound only. Task D ran:
  `fast::run` and the plain loop agree at the 12,676,237,591-step base case (hash 27245db416b98a32, 87 s each). Not closed: the real board is not `Good` (old blob cells inside the window rows);
  the Lean model's fidelity to the Rust ant; the global-front premise. See the parent experiment's README (L5, Task D).
- **Item 2, generalise the checker:** (i) the other three "escapes" are not column sweepers: two are spiral builders (filled octagon-like territory, band rewritten once per revolution; see the experiment README correction 4; unattacked by the falsification harness) with exact affine clocks (RLLLRLRLLL from 2.635e10, phase period 2;
  RLLLLRRL from about 1.47e10, phase period 19, post hoc), one is a still-growing blob; the 3-stage sweeper checker does not transfer (the spiral has eight segments and a band of depth >= 77).
  Stage 2 for the spirals is *not done*; the cell-level steady-state test (99.2-99.7% equal after 5 revolutions) says a family exists. (ii) The `m`-free case is done as a **rectangle translated-cycler decider**:
  571/571 census highways certified (`experiments/archive/2026-10-highway-decider/`), controls and an independent-ant oracle pass. The decider is the first census-wide level-3 object of the track; its theorem is checked by
  a program and a proof sketch, not yet in Lean.
- **Item 4, explain:** the wake's colour period 3 is the three-column advance: one visit profile (1,4,4,2,1) on offsets -2..2 for every interior bulk row, visits per cell 3, 5, 4, below 6, so colour = visit count
  (parent Task E, 1836/1836 cells). The profile itself (the descent lemma's footprint) is not explained.
- **Item 3, entry:** untouched this session.
- **Addendum 2026-10-23 (later):** `Sweeper.cycler` (`lean/Cycler.lean`) proves the rectangle translated-cycler theorem for a generic rule and every number of periods, so the highway decider is a sound checker of instances of a
  machine-checked theorem (instance clauses are still computed by `decide.py`; the Lean ant is not proved equal to the Rust ant). `experiments/archive/2026-10-highway-decider/README.md`, "Lean soundness".
- **Addendum 2026-10-25:** instrument/ledger: the kappa exposure classifier (`kappa_exposure_classes`) passed an independent z3 check written from the docs (`experiments/archive/2026-10-exposure-classifier-check/`, 65/65, six negative controls; level 3 for the classifier only, not for any ant claim). Q20 (square-ring fillers): a PLAN for the inductive step, uniformity in k, RLRRRRLRR membership and patched-start entry, building on PR #11, is at `notes/q20-filler-proof-plan-2026-10-25.md` (nothing run).
