# Is RLRLLL's column sweeper a provable macro-transition?

Registered 2026-10-20 23:40 (+13:00), base commit `ba38590`. **Nothing in this folder has been run** when this file is
first committed. This is the first experiment of the proof track (`notes/proof-track-2026-10-20.md`): it asks whether a
behaviour seen in simulation can be turned into a finite proof obligation, rather than measured more precisely.

## Question

After about 1.2677e10 steps from a blank board, `RLRLLL` switches abruptly from blob growth to a boustrophedon column
builder (`notes/g1-builder-structure-2026-10-14.md`): slow traverses at ~10 steps per row, fast returns at ~2 steps per
row, three new columns per cycle, a wake that is exactly period-3 in x with colours 3, 4, 5, and a sweep height
`L ~ 0.67|x| - 960` that grows as the builder moves west. All of that is post hoc, from two 4e5-step windows of one run.

If the sweeper is a genuine macro-transition there is a family of configurations `C(L, q)` (`L` the column height, `q` a
finite phase) and integers such that

    F^{T(L,q)} (C(L, q)) = shift_3 C(L + g(q), q'),     T(L, q) = alpha L + beta(q),

for every admissible `L`. Proving that for all `L` turns an infinite trajectory into a finite check, and would give the
exact asymptotics of the builder instead of a fitted `|x|^2 = 0.8634 t - 1.093e10`.

This experiment has two stages. Stage 1 (measurement) tests whether the macrostate exists in the simulated run at all, with
predictions below. Stage 2 (proof) is attempted only if Stage 1 passes, and is judged by an independent checker, not by
the agent that proposes the invariant.

## Definitions (frozen before measurement)

- **Run**: `RLRLLL`, blank board 32768 x 32768, ant at the centre heading north, `DIRS` and update order of
  `src/fast.rs` / `examples/g1_ribbon_breakout_builder_dump.rs`. Deterministic; no seed.
- **Front**: `x_f(t)` = the minimum x of all cells visited by time t (the builder moves west, towards negative x).
- **Cycle boundary**: the step at which `x_f` first reaches `x_f(t_on) - 3k`, k = 1, 2, ..., where `t_on` is the first
  front advance after 1.2677e10. Cycle k runs between boundaries k and k+1; `T_k` is its length in steps.
- **Height** `L_k`: the number of visited cells in column `x_f(t_on) - 3k` (the column opened at boundary k), counted
  at boundary k+1, after one full cycle. `g_k = L_{k+1} - L_k`.
- **Reach** `W_k`: max over steps of cycle k of `(x_ant - x_f)`, i.e. how far behind the front the ant goes.
- **Front window**: columns `[x_f, x_f + W)` with `W = max_k W_k + 1`, rows spanning the visited extent, at a cycle
  boundary, with y re-centred on the topmost visited row of column `x_f + 3`, plus ant offset and heading.
- **Steady phase**: all cycles that end before the ant leaves the board (exit was at step 12,974,495,927).

## Predictions (registered before any measurement in this folder)

- **P1 (exact affine clock).** There are integers `alpha`, `beta` (allowing `beta` to depend on a phase with at most 4
  values) such that `T_k = alpha L_k + beta` holds **exactly** (zero residual) for at least 95% of steady-phase cycles,
  with `alpha = 12` (10 + 2 steps per row from the G1 note). Fails if the best affine fit leaves nonzero residuals on more
  than 5% of cycles, or `alpha != 12`.
- **P2 (constant growth).** The sequence `g_k` is eventually periodic with period <= 4 and mean in [1.9, 2.1]
  (the G1 slope 0.67 per column predicts 2 rows per 3-column cycle).
- **P3 (finite reach).** `W = max_k W_k <= 24` over the steady phase: the ant never reads columns more than 24 behind the
  front, so the older wake (and the blob) is causally irrelevant once the sweeper runs.
- **P4 (self-similar front).** Every front-window snapshot at a cycle boundary decomposes as
  `top_q . B^m . bottom_q`: fixed end blocks of at most 64 rows (at most 4 distinct phases `q`), and a bulk band of `m`
  repetitions of one block `B` whose period in y is <= 12 rows, with `m` the only thing that changes between cycles.
  Fails if no such decomposition covers >= 95% of boundaries.
- **P5 (derived asymptote; consequence of P1, P2).** With `alpha = 12` and `g = 2`,
  `d|x|^2/dt -> 18 / (alpha g) = 0.75` as `L -> infinity`. The fitted 0.8634 is then a finite-size effect of the
  offset `L ~ (2/3)|x| - 960`: the local slope `6|x| / (alpha L)` should fall monotonically towards 0.75 across the
  steady phase. Fails if the per-window local slope does not decrease with |x|.

What would change the plan: if P3 fails (unbounded reach), the sweeper reads its old wake and a finite macrostate cannot
exist without carrying the wake as state; the experiment records that as the negative result the proposal anticipated.
If P1 holds but P4 fails, the clock is regular while the configuration is not, which would point to an invariant coarser
than equality of configurations (for example a regular language of column words).

## Out of scope (stated in advance)

- **Entry.** A proof of the sweeper says nothing about why a blank-board run reaches it at 1.2677e10. Whether the first
  cycles after onset already lie in the family `C(L, q)` is recorded as an observation, not predicted.
- **Other rules.** Generalising to other no-highway escapes (`RLLLLRRL`, `RLLLLRLRRL`, `RLLLRLRLLL`) is a later step.

## Stage 2 sketch (if Stage 1 passes)

A proof obligation is finite if it is stated over the decomposition of P4:
1. *Traverse lemma*: with the ant entering the bulk band `B^m` in a fixed local state, it leaves the band after exactly
   `m s` steps having rewritten each `B` into a fixed `B'`, for all `m` (an induction on `m` whose step is one finite
   simulation of the ant across one `B`, with the neighbouring blocks fixed).
2. *End lemmas*: finite simulations of the turnarounds from each `top_q` / `bottom_q` with bounded context.
3. *Closure*: the composition of 1 and 2 maps `C(m, q)` to `shift_3 C(m + g/p, q')`, closing the induction.

The checker must be a small, separately written program (or a proof assistant) that consumes the proposed blocks and
replays only the finite lemmas against `src/reference.rs` semantics. Proposals may come from anywhere; acceptance comes
only from the checker.

## Commands

(Filled in as runs happen; see `NOTEBOOK.md`.)
