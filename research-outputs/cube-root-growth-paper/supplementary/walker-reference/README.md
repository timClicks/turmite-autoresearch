# Supplementary dataset: calibration-walker kappa against its own uniform reference

`walker_reference.csv`: 48 rows, one per (walker, seed, window set). It re-expresses the probe's boundary
occupation `kappa` for the calibration walkers as a ratio to the value a walker that is uniform on its territory
at every instant would give, `kappa_unif(a, beta)`, using each walker's own measured exponents.

Rebuild (WSL, repo root; deterministic, no randomness):

```bash
uv run research-outputs/cube-root-growth-paper/supplementary/walker-reference/build_walker_reference.py
uv run research-outputs/cube-root-growth-paper/supplementary/walker-reference/build_walker_reference.py --check
```

Inputs: `experiments/archive/2026-10-kappa-walker-reference/results/probe_{mem,rotor}.csv` (SHA-256 in
`walker_reference.build.json`), produced by that experiment's `scripts/run.sh` at commit 34fbf45
(`probe 23 16384` for the memoryless walkers, `probe 27 8192` for the rotor; seeds 2026101901..08). The CSV is
regenerated, never hand-edited.

## Columns

| column | meaning |
|---|---|
| `walker` | `rw` random walk; `pw:Q` memoryless walker turning right with probability Q; `rotor` rotor walker |
| `seed` | run seed (the suffix of the probe spec) |
| `window_set` / `k_lo` / `k_hi` | windows used: `k` is log2 of the window END `t`; window k is (t/2, t] |
| `n_escaped_windows` | windows flagged as escaped from the board in that run (0 for all rows) |
| `a` | slope of ln area against ln t over the window set |
| `beta` | slope of ln perimeter against ln area over the window set |
| `kappa` | mean over windows of (boundary_steps / (t/2)) / (perimeter / area) |
| `kappa_unif` | `2 * int_{1/2}^{1} x^(-a(1-beta)) dx = 2(1 - 2^(-(1-p)))/(1-p)`, `p = a(1-beta)` |
| `ratio` | `kappa / kappa_unif` |

## Group means (mean over 8 seeds)

| walker | window set | ratio |
|---|---|---|
| rw | k12-22 | 1.277 |
| pw:0.25 / 0.5 / 0.75 | k12-22 | 1.235 / 1.316 / 1.255 |
| rotor | k12-22 / k20-26 | 1.686 / 1.799 |

The ant census (single run per rule, 2185 stationary blob rules) has median 0.814, IQR 0.664-0.957, 5-95%
0.443-1.332 (`experiments/archive/2026-10-kappa-uniform-baseline/results/census_spread.txt`; copied into the build JSON).
The mean-field uniform walker (ratio 1.010, sd 0.009) is from that earlier experiment and is not in this table.

## Caveats

- Eight seeds per walker; a, beta and ratio are fitted per seed, then compared. Walker means are not like with
  like against the ant's single-run, rule-dependent distribution.
- A single power law is a poor description of porous territories (memoryless walkers use k12-22 only; board
  limits). The experiment's local-exponent reference agrees to <= 0.006 but is not in this table.
- The rotor ratio depends on the window set (1.69 vs 1.80); the exponent `a` is still relaxing towards 2/3.
- The ratio is accounting against a reference, not a mechanism. See the experiment's `NOTEBOOK.md`.
