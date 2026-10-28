# CI identity check for `sweep_lean` and the tiled backend

Created 2026-10-24T10:00Z, base commit `b942a82854b4d61222301959b9895060d2543d3f`.

## Question

`.github/scripts/check_determinism.py` compares `sweep` and `probe` CSVs at 1 and
3 Rayon threads. Most census data, though, comes from `sweep_lean` (documented as
"identical results" to `sweep`), and since 2026-10-23 it has a second storage
backend (`TURMITE_GRID=tiled`) whose CSV is documented as byte-identical to dense.
Neither claim is exercised by the hosted reproducibility job; they are covered only
by `cargo test` property tests and a one-off benchmark. Can the small CI batch
(every canonical nontrivial rule of lengths 2-6, 32,768 steps, grid 256) also pin
them down, end to end through the CLI?

## Pruning-index preflight

Index revision `b942a82854b4d61222301959b9895060d2543d3f`. Searched
`sweep_lean|tiled|determinis` in `notes/pruning-index/entries/`; sole entry is
`NR-20261022-additive-laws-order-blind` (additive conservation laws), which is
unrelated to implementation identity. No match. Decision: run. This is an
engineering identity check, not a sweep over a rule family, and excludes nothing.

## Registered predictions (before any run of the new checks)

P1. `sweep_lean` (dense) stdout is byte-identical to `sweep` stdout on the CI batch.
P2. `sweep_lean` is byte-identical at 1 and 3 Rayon threads, dense and tiled.
P3. Tiled with default settings, and with stress settings (tile side 2^2, cache of 2
    tiles, packed and raw; tile side 2^6 with 16 cache tiles and lz4), is
    byte-identical to dense. The stress settings force constant eviction, so a
    passing result is not vacuous.
P4. The new check can fail: a deliberately corrupted comparison input is
    reported as a failure (a planted-fault control).

A failure of P1-P3 would be a real discrepancy and must be reported as such, not
patched around. Passing says only that outputs agree on this batch, toolchain and
step budget; it is not evidence about asymptotic behaviour or other inputs.

## Results

Run 2026-10-24 on code commit `2474a93` (+ uncommitted script edits, committed with this record).
Environment: rustc 1.97.0 (CI pins 1.98.1, so the hosted run is the first on the pinned toolchain), 4 cores.

Command (from repository root):

```bash
cargo build --release --locked --bin sweep --bin sweep_lean --bin probe
uv run --frozen python .github/scripts/check_determinism.py --output "$SCRATCH/repro"
```

Outcome: `PASS`, 14 recorded runs in `recipe.json`, zero failures, 22 s wall.

| Prediction | Outcome |
|---|---|
| P1 `sweep_lean` dense == `sweep` | Held. Both CSVs sha256 `186ba51b...fa2cd` (57 rules, 9 with a highway, 48 budget-stopped, 1 other stop). |
| P2 1 vs 3 threads, dense and tiled | Held. |
| P3 four tiled configs == dense | Held. |
| P4 check can fail | Held for the vacuity guard: with the 2^2-tile cache widened to 100000 tiles the script exits 1 ("did not exercise packed_stores; agreement would be vacuous"). Not demonstrated for a genuine byte difference, because no implementation fault was available to inject; that comparison is a plain `!=` on bytes. |

Stress-setting counters (2^3 tiles, 4 resident, 57 rules): 72,234 evictions in total, of which 72,233 raw stores
(raw), 72,233 packed stores (packed), and 46,390 packed + 25,843 LZ4 stores (lz4).

**A near-miss worth recording.** My first lz4 stress setting (2^6 tiles, 16 resident) agreed with dense but
never evicted or compressed anything: a 256-cell grid holds only 16 such tiles. It would have been a passing
test of nothing. The script now asserts from `TURMITE_GRID_STATS` that each stress setting evicts and uses
the storage path it names.

## What this does and does not show

- Shows: on 57 rules x 32,768 steps x 256-cell grid, stdout of `sweep_lean` is byte-identical to `sweep`
  regardless of thread count and storage backend, and the tiled paths were really exercised. Now enforced
  on every push.
- Does not show: agreement at other step budgets, grids, seeded backgrounds, checkpoint/resume, or on
  rules of length > 6; nor that either implementation matches the `reference` oracle (`cargo test`
  property tests do that; this check compares two fast paths with each other). Escaped and highway rows
  are a minority (9/57). Same toolchain, same machine: no cross-platform claim.
- `cargo test --release --locked` was not rerun: no Rust source changed.

