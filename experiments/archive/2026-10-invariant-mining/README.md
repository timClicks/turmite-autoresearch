# Exact additive modular invariant mining

## Registration — 2026-10-22 21:33 NZDT

Starting revision: 074f4a7808223b655f01eb6ffb7fe057b0b8aa8a.
Implement the T4 balance-law direction in `notes/research-frontier-2026-10-13-pm.md`.
Before running: predict recovery of checkerboard parity `x+y+t mod 2`,
heading parity `h+t mod 2`, and colour-clock balance `sum(c)-t mod n`
when the requested modulus divides n. No prediction about growth or highways.

Pruning preflight at the above revision: `rg --files notes/pruning-index/entries`
and `rg -n -i 'invariant|conservation|parity|symmetry' notes/pruning-index/entries`
returned no entries/matches. Decision: run small algebraic checks, no exclusions.
No stochastic sampling, seed, fit window, or large sweep is involved.

## Instrument and proof scope

Search `I = a*x + b*y + d*h + e*t + sum_sites w(colour) (mod m)`,
with w(0)=0. Enumerate all m^4 coefficient tuples; the heading-zero equations
uniquely determine w. Independently check all 4*n local transitions, including
both wraps. Zero residual implies invariance by induction for every finite
colour field and initial heading/position. For infinite backgrounds interpret
the field sum as the finite change from the initial field.

The output includes dependent laws and multiples, not a basis. A time coefficient
is a balance law; e=0 is a conserved state quantity. Search completeness is only
within this ansatz. Missing laws do not exclude nonlinear, edge-flux, spatially
weighted or history-dependent invariants. These constraints do not imply the
cube-root exponent, trapping, or highway formation. No family is pruned.

## Reproduction and pipeline use

From the root, with Rust edition 2024 and the locked uv environment:

```sh
cargo test --release --locked --test invariants
cargo test --release --locked
uv run --frozen experiments/archive/2026-10-invariant-mining/scripts/mine.py RL RR RLRR
```

The script builds in a fresh target directory, records binary and source hashes,
the revision, inputs and command in `results/provenance.json`, and writes
`results/invariants.csv`. Existing outputs are refused. Join on the full rule
string with census tables; do not identify cyclic shifts or primitive roots
when comparing full colour potentials. CLI moduli are 2 and 4; the library
accepts 2 through 16. Cost is O(m^4*n), independent of simulated step count.

Tests cover all rules of lengths 2..5, moduli 2,3,4, all initial headings,
a deterministic nonblank patch, and 64 oracle steps. They also exhaustively
compare the two-colour mod-2 search with brute-force potentials and include
a false candidate as a rejection control. This is instrument validation,
not statistical evidence; between-seed uncertainty is inapplicable.
