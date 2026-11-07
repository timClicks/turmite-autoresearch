# Implementation handoff and acceptance checks

A dependency-free Python sparse implementation and independently written Python oracle tests are now included; see [PYTHON.md](PYTHON.md). The Rust/tiled implementation, complete gate instruments, and cross-language execution checks remain outstanding. The Python tools support short diagnostic runs and resumable state; do not treat those technical checks as passed Q33 confirmation gates.

## Integration plan

1. Read src/walkers.rs, src/probe.rs, src/tiled.rs and the current CLI before choosing a spec syntax. Suggested future syntax: cap:RULE:M:SEED, where M is a positive integer or inf, with the fixed q encoded in a versioned walker definition. This syntax is a plan, not a working command.
2. Implement the simplest sparse reference independently from the fast walker. Preserve read/turn/paint/move order, exactly one RNG draw per step, origin exception and permanent departed bits. At the forced step consume but ignore the draw.
3. Extend the tiled CPU path and checkpoint format with visited bits, r, RNG state, counters and run-histogram state; version the format. Signed coordinates must use floor division and nonnegative local tile indices. No wrapping at a dense-board edge.
4. Integrate growth-only sub-octave samples and octave boundary instruments. Avoid full hull rescans every step: exact hulls are required only at saved checkpoints, with check-mode comparisons on small traces. Define pre-entry depth measurement from a frozen territory or replay, never from the already expanded set.
5. Add cap-forced counters and explicit event records sufficient to independently recompute fresh-run distributions. A final unfinished run contributes observed duration with a right-censor flag, not a completed short return.
6. Reuse Rev3 time-weighted excursion code without quietly changing its boundary, band or censoring conventions. Q33's explicitly named boundary counters may differ from that instrument; document each, rather than passing incompatible counters to Score_tw.
7. Freeze ordered-regime detectors from archived highway/crawler/sweeper examples before confirmation. Keep an independent Python checker for RLRLLL-style transitions.
8. Only port to Metal/wgpu if its census runner supports the new state and all requested statistics with byte-identical CPU results. Census throughput from another kernel is not a performance guarantee. Register timing predictions before benchmarking a new port.

## Required oracle/geometry checks

- cap=1,2,4; the origin exception; no visited-cell U override; colour wrap to zero with departed bit retained.
- An injected all-straight fresh stream returns after the forced reversal, with exactly m departures outside origin.
- Cap=inf matches the independently implemented uncapped persistent-fresh policy.
- The original-ant control matches reference::Ant and stored no-noise probe rows.
- Fresh RLU finite-cap and own-colour-zero identities from DESIGN.md as small correctness checks, not large empirical arms.
- Bit-level RNG thresholds, exact probabilities and shared draw consumption after caps.
- Negative x/y and tile crossings; compression/reload; resume versus uninterrupted output; thread-count independence.
- Full rescans versus incremental A, bounds, perimeter, boundary count and numerator counters.
- Filled squares, lines, hollow rings and disconnected planted patches for hull/occupancy conventions.
- Synthetic A=t^a and W=t^w data through the exact nine-point octave fit, missing sample handling and crossing interpolation.
- Planted collapse curves, flat-curve negative control and censored curves through the exact matched-support score.
- Detector positive and negative controls, with uncertain onset intervals and no conversion of allocation failures to structural labels.

## Runtime and output contract

Use a 1 GiB bounded tile pool for the process, not 1 GiB independently per concurrent lane. Bound active lanes to respect total memory; log peak usage, retries and allocation failures. If the backend cannot guarantee a process-wide pool, run sequentially or lower per-run limits with an explicit logged schedule. All finite-coordinate bounds must be surfaced and invalidate affected windows.

Write run spec, source/binary/input hashes, machine/OS/toolchain, thread count, actual commands, wall/CPU time, pool settings and checkpoint version before execution. Use a fresh CARGO_TARGET_DIR for scientific builds to avoid stale binaries. Lock dependencies; analysis uses uv run --frozen and polars in deterministic sorted order.

Proposed output tables (schema frozen before confirmation): specs, checkpoints, octave_fits, fresh_runs, cap_exposure, excursions_tw, ordered_candidates, run_outcomes, gate_report and provenance. Primary keys include rule, arm, seed and step/window. Status columns distinguish complete, left/right censored, ordered, uncertain and resource incomplete. Raw traces go in experiment scratch/dumps; small committed summaries belong in results only after measurement. No empty CSV is presented as a zero result.

Exact build/run/analyse commands and executable schemas must be committed with the implementation. They are deliberately not fabricated in this documentation-only proposal.

## Amendment A2 memory default (2026-11-05)

The 1 GiB process-wide pool above is insufficient if an uncapped arm approaches A ~ t near 2^31 (~2e9 cells). Until excluded-pilot A(t) is measured, run uncapped arms sequentially, fail loud on allocation failure, and log peak RSS per arm. After the pilot, either keep that schedule or register a resized pool before confirmation. This is a resource plan, not a growth prediction.

## Amendment A3 memory detail (2026-11-06)

Sequential uncapped arms avoid cross-arm pool contention; each arm still faces the 1 GiB process-wide pool alone. Planning figure until pilot A(t): see Amendment A5 for the corrected per-cell cost sources. A resource-censored uncapped partner removes that rule from P3/P5 paired support and can bias those scores toward slowly growing rules; report the resource-censor fraction with P3/P5 and do not impute.

## Amendment A5 memory sources (2026-11-07)

Two different backends, two different figures (neither is a growth prediction):

- **Tiled Rust backend** (`experiments/active/2026-10-tiled-grid-backend/DESIGN.md` lines 44–51): about **1 byte per resident/packed cell** (lean colour byte; packed can be ≤1 B/cell). Under a 1 GiB process-wide pool that is order 1e9 cells, so a near-ballistic uncapped arm toward A ~ 2e9 at N=2^31 is still resource-censored well before the horizon.
- **Python sparse simulator** (`experiments/_lib/turmite_sim.py`): cells live in a `dict[(x,y), colour]`. Hash-map overhead is much larger than 1 B/cell; until measured, treat **~24–32 B per departed cell** as a planning guess for that dict (not for the tiled backend). Exact layout is frozen with G0.

## Amendment A6 memory measurement (2026-11-08)

Supersedes the numeric planning figures in Amendment A5 for both backends (resource plan unchanged: sequential uncapped arms, fail loud, log peak RSS; no growth prediction):

- **Tiled Rust backend** (`experiments/active/2026-10-tiled-grid-backend/DESIGN.md` lines 44–51): memory is **`tiles_touched × bytes_per_tile`**. Resident tile `(T+2)^2` bytes; packed `T^2·w/8 + T^2/8`. One byte per departed cell is only a lower bound for compact interiors. Thin or near-ballistic arms (few cells per touched tile) cost up to about **T bytes per departed cell**; at T=64 that is ~64 B/cell, so a 1 GiB pool censors far earlier than a compact fill. Even at 1 B/cell, 1 GiB holds ~1.07e9 cells against A≈2e9 at N=2^31.

- **Python sparse simulator** (`experiments/_lib/turmite_sim.py`): measured with CPython 3.13.5 and `tracemalloc` on 2026-11-08:

  ```
  python3 - <<'PY'
  import tracemalloc
  n, base = 10**6, 10**9
  tracemalloc.start()
  d = {(base + i, base + (i % 997)): (i % 256) for i in range(n)}
  current, peak = tracemalloc.get_traced_memory()
  print(current / n, peak / n)
  PY
  ```

  Result: **~162 B/cell** at 10^6 cells (coordinates outside the small-int cache); ~172 B/cell at 10^5. Treat that as the planning figure until G0 freezes the layout. At 162 B/cell, 1 GiB holds only ~6.6e6 departed cells.
