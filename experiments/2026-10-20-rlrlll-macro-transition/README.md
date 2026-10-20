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

Run in a cloud container (Linux, cargo 1.97, 4 cores), not the WSL machine; all single-threaded and deterministic.

```bash
E=experiments/2026-10-20-rlrlll-macro-transition
cargo build --release --example rlrlll_macro_transition_trace --example rlrlll_macro_transition_check
# Stage 1 trace (2 min 53 s): blank 32768 board, arm at the first front advance after 12,677,000,000
./target/release/examples/rlrlll_macro_transition_trace RLRLLL 12677000000 $E/scratch/run1 32768 48 25 2> $E/scratch/run1.log
cp $E/scratch/run1/cycles.csv $E/results/cycles.csv
uv run $E/scripts/stage1_cycles.py $E/results/cycles.csv > $E/results/stage1_cycles.txt
uv run $E/scripts/stage1_snapshots.py $E/scratch/run1 > $E/results/stage1_snapshots.txt
# Stage 2: propose the family from snapshots 0, 1, 2, then check it
uv run $E/scripts/extract_canonical.py $E/scratch/run1 0 $E/results/canonical_k0.txt
./target/release/examples/rlrlll_macro_transition_check RLRLLL $E/results/canonical_k0.txt   # -> results/check_k0.txt
uv run $E/scripts/stage2_compare.py > $E/results/stage2_compare.txt
```

Tracer binary sha256 in `results/trace_binary.sha256`; checker sha256 in the header of `results/check_k0.txt`.
Snapshots (`scratch/`, gitignored, ~74 MB) are regenerated by the trace command. Negative controls:
`results/check_negative_controls.txt`.

## Results (appended 2026-10-20 23:55 +13:00; predictions above not edited)

Stage 1 trace: armed at step 12,677,001,095 (front x = -2194); the ant left the board at step 12,974,495,927 at
(x, y) = (-16384, -5895), the same step and cell as the independent G1 `ribbon_trace` run. 4,729 cycles recorded.

| Prediction | Outcome | Evidence |
|---|---|---|
| P1 exact affine clock, alpha = 12 | **Held.** `T_k - 12 L_k` takes exactly three values (358, 394, 518), cycling with period 3, on 100% of 4,729 cycles; least squares slope 12.000006 | `results/stage1_cycles.txt` |
| P2 constant growth, mean in [1.9, 2.1] | **Held, sharper than predicted.** `g_k = 2` on every one of 4,728 differences (period 1) | same |
| P3 reach <= 24 | **Held.** Max reach 20 columns behind the front; by phase exactly 12, 20, 19 | same |
| P4 self-similar front | **Held on the 373 snapshotted boundaries** (cycles 0-63, 1000-1063, 3000-3063 and every 25th), not on all 4,729 (deviation: snapshots were sampled). Bulk period 1 row (every bulk row identical), 3 top blocks (one per phase), 1 bottom block, ant at dx 0, dy 6 or 7, heading 3 | `results/stage1_snapshots.txt` |
| P5 slope falls towards 0.75 | **Held.** Per-decile d\|x\|^2/dt falls monotonically 1.538 -> 0.825; the checked law below gives the limit 9/12 = 0.75 exactly | `results/stage1_cycles.txt`, `results/stage2_compare.txt` |

**Stage 2: the family is closed (checked).** `results/canonical_k0.txt` proposes C(m, q), q = 0, 1, 2, read off
snapshots 0-2. The checker (`examples/rlrlll_macro_transition_check.rs`) shows, for every even m >= 2:

    C(m, 0) -> C(m + 2, 1) in 12 m +  934 steps
    C(m, 1) -> C(m + 2, 2) in 12 m + 1058 steps
    C(m, 2) -> C(m + 2, 0) in 12 m +  898 steps

each shifted 3 columns west, with the ant never going east of the 48-column window or west of the new front. Two
shift lemmas carry the induction over the bulk: a descent `A.r^2 -> r'^2.A` (A = 2 rows, 20 steps per 2 rows) and a
return `r'^2.A -> A.r''^2` (A = 1 row, 4 steps per 2 rows), so `12 = (20 + 4) / 2` steps per bulk row. The step
counts and end states agree with brute-force `reference::Ant` runs at m = 2, 4, 6, 8, 10, 20, 50, 100, 434 for all
three phases (27 runs, all identical). Negative controls fail as they should: one bulk cell changed (col 46, 3 -> 4)
gives "segments differ" in all three phases, and the wrong rule `RLRLLR` leaves the strip.

**Consequence (base case + closure).** Snapshot 0 of the blank-board run (step 12,677,007,177) *is* C(434, 0). So,
given the correctness of that 1.27e10-step simulation, `RLRLLL` from a blank board never forms a highway: from that
step on it is the sweeper forever, cycle k + 1 takes exactly `12 (434 + 2k) + (934, 1058, 898)[k mod 3]` steps, and
`|x_f|^2 / t -> 3/4`. The law reproduces all 4,728 measured cycle lengths exactly (`results/stage2_compare.txt`).
The fitted G1 slope 0.8634 was a finite-size value of a quantity whose limit is 0.75.

What this does **not** establish, and the trust it rests on:
- *Entry* (why the blob produces the sweeper) is untouched. A post hoc probe (`results/cycles_early.csv`, armed at
  1.26e10) shows the exact law already holds from the first front advance past the old blob edge (step
  12,676,421,767, x = -1820, column height 226); extrapolating the wedge to zero height puts its apex inside the blob.
  The base case is one simulation by the plain
  loop shared with `g1_ribbon_breakout_builder_dump` (not itself proptested against `reference`; its exit step agrees
  with `ribbon_trace`, which is a consistency check, not a proof).
- The checker is ~600 lines of uncertified Rust. Every concrete step is a `reference::Ant` step, and the brute-force
  runs and negative controls test it, but a proof-assistant formalisation (or an independent second checker) is the
  next level of assurance.
- Why the wake has colour period 3 for a rule of length 6, and why the bulk row is `14435435...`, are not explained by
  the check: it certifies, it does not explain.
