# Proof track: from simulated regularities to checked macro-transitions (2026-10-20)

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
  RLRLLL sweeper is the macro-transition proposed in `experiments/2026-10-20-rlrlll-macro-transition/`, the fitted
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
| Crystal ray | finite-state transducer / regular language of ray words | `experiments/2026-10-crystal-rules/` |
| Tethered ant | trapping certificate: invariant region the ant cannot leave | `experiments/2026-10-13-tether-rules/` |
| Boundary excursion | return map on boundary states (must be shown well defined) | `experiments/2026-10-14-t1-excursion-tomography/`, kappa work |
| Long transient | transition between metastable macrostates (entry problem) | `experiments/2026-10-13-highways-unresolved-rules-1e10-1e11/` |

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

These must go through the literature-review process (`experiments/2026-10-15-literature-review/`) before being cited
in the paper.

## Experiments in this track

- `experiments/2026-10-20-rlrlll-macro-transition/`: is the RLRLLL sweeper a macro-transition (Stage 1 measurement,
  predictions P1-P5 registered at `4bc029a`), and if so, can it be checked for all heights (Stage 2)?
