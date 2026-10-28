# kappa uniform baseline: what does the probe report for a walker that is uniform by construction?

Registered 2026-10-16 00:25 +13:00, base commit 997c9b2 (dirty workspace from other
experiments), **before any run**.

## Question

The paper reads kappa < 1 as "less edge time than uniform" and kappa > 1 as "more".
But the probe's kappa = (B/S)/(P_end/A_end) divides *window-averaged* boundary
occupation by the *end-of-window* edge fraction, while A and P grow through the
octave. So a walker with instantaneous occupation ratio exactly 1 need not give
probe kappa = 1. What value should be called "uniform"?

## Analytic prediction (registered)

If the walker is uniform over the territory at every instant, P(t)/A(t) ∝ A^(β-1)
with P ∝ A^β, A ∝ t^a. In the octave (t/2, t], B/S = mean of P/A, so

    kappa_unif(a, β) = 2 ∫_{1/2}^{1} x^(-a(1-β)) dx.

- smooth blob (β = 1/2), a = 2/3: kappa_unif = 3(1 - 2^(-2/3)) = **1.1102**
- β = 1/2, a = 0.95: 1.1587 (diffusive-ish memoryless walker)
- a = 1 (no deceleration, β = 1/2): 1.172
- Only a window starting at t = 0 would give 1.5; not used here.

## Mean-field walker (registered)

Each step: resample position uniformly over the currently visited cells, then step
to a uniform random 4-neighbour (entering fresh ground if that neighbour is
unvisited). Instantaneous occupation of edge cells is then exactly P/A in
expectation. The probe's bookkeeping is reproduced inside the example (same
Region logic, octave windows (2^k, 2^(k+1)], same definitions of B, P, A), because
the probe owns the walker position and cannot teleport.

Predictions:
1. Area slope a (fit over k = 12..22) in 0.62–0.72, if P ∝ sqrt(A) holds.
   If it falls outside, the mean-field territory is rough (β > 1/2) and the
   analytic kappa must be recomputed with the measured a and β, not 1.11.
2. Probe kappa within 0.03 of kappa_unif(a_measured, β_measured), where β is
   fitted from the same run's (A, P) pairs. Disagreement larger than that means
   my reading of the probe's kappa is wrong, and is the finding.
3. Consequence if confirmed: the ant's reported kappa ≈ 0.9 is a deficit of about
   0.9/1.11 ≈ 0.81 relative to uniform, the memoryless walkers' 1.3–1.45 are
   1.2–1.3 times uniform, and the rotor's 2.0 is 1.8 times uniform.

Seeds 2026101601..2026101608, board 4096, 2^23 steps (a position list gives O(1)
uniform sampling). Mean and between-seed sd reported.

## What this does not do

It does not explain the ant's kappa level. It only fixes the reference value.
Accounting, not mechanism.

## Commands

See `NOTEBOOK.md` and `results/` (filled in as it runs).

## Results (2026-10-16 00:41 +13:00)

Command: `cargo run --release --example kappa_uniform_baseline -- 2026101601 8 23 results/mf_walker.csv`; `uv run scripts/analyse.py` (output `results/analysis.txt`). Windows k = 12..22, 8 seeds.

| quantity | prediction | measured (seed sd) |
|---|---|---|
| area slope a | 0.62–0.72 | 0.677 (0.005) |
| perimeter exponent beta | ~0.5 | 0.520 (0.007) |
| probe kappa | 1.107 (formula, measured a, beta) ±0.03 | 1.118 (0.009) |

Predictions 1 and 2 held. The probe's uniform reference is **~1.11**, not 1. Restated against it, the ant's ~0.9 is ~0.81× uniform (the rotor and memoryless ratios were not recomputed with their own a, β). Accounting only: the ant's kappa level and the drift remain unexplained.
