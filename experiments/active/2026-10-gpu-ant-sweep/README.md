# GPU ant sweep: a reusable CUDA utility for (rule, seed) batches

**Status:** working (2026-10-16): correct and benchmarked; extension ideas at the end. **Goal:** a re-usable CUDA utility that runs
thousands of independent (rule, seed) ants at once, with output provably identical to the CPU
oracle chain `reference -> fast -> lean`.

## Question

Can one RTX 4000 Ada (20 GB, sm_89) beat `sweep_lean` on 6 CPU threads for census-style sweeps
at the *same* grid size and step budget (so classification semantics are unchanged), and by how much?

## Design (decided before any benchmark)

- Job = `(rule, bg_seed: Option<u64>, max_steps)`. `bg_seed = None` is the census instrument
  (blank background, identical to `sweep`/`sweep_lean`). `Some(s)` is the repo's existing seeded
  meaning: i.i.d. uniform background colours `ext::bg_colour(s, x, y, n)` (`walkers::mix64`).
  The ant itself is deterministic, so the seed only enters through the background.
- Virtual `GRID x GRID` grid per ant through a **tile directory** (64x64-byte tiles, tile ids from a
  global pool, popped with `atomicAdd`, freed when the job retires). A dense 8192^2 u8 grid is 64 MB
  per ant (~300 ants in 20 GB); tiles make thousands of resident ants fit with unchanged escape semantics.
- Headings are logged 2 bits/step into a per-lane ring; the CPU rebuilds the position trail backwards
  from the final state and runs the unchanged `detect::find_highway` / `exit_confirms`. Escape test and
  bounding box are kept in registers.
- Kernel launches are sliced (default 2^20 steps) to stay under the WDDM watchdog, the host refills
  finished lanes between slices, and results are written **by job index**, so output does not depend
  on scheduling or on how many lanes ran.
- Pool exhaustion retires the lane, requeues the job and halves the active-lane cap; a job that
  fails alone is a hard error (never a silently wrong row).
- Toolchain: `cudarc` (dynamic loading, NVRTC at runtime, no nvcc, no sudo). Behind the cargo
  feature `cuda`, so `cargo test --release` without it is unchanged.

## Predictions (registered 2026-10-16, before any timing)

P1 (correctness). `gpu_sweep` CSV is byte-identical to `sweep_lean` (same MIN MAX MAX_STEPS GRID)
on lengths 2..=10 at 1e6 steps, and GPU `RunResult` equals `fast::run` on every field in the
proptests (including escapes at every edge, mid-run slice boundaries, tile crossings).
P2 (speed). Aggregate throughput of 3-8x `sweep_lean` at 6 threads on the same census slice.
Falsified if < 2x. Reasoning: memory-latency-bound dependent loads, many resident warps, but
tile lookups, ring writes and straggler lanes cost something.
P3 (scaling). Throughput rises with lane count and saturates somewhere between 2k and 8k lanes.

## Use it

One-time setup in WSL (no sudo, no CUDA toolkit; NVRTC comes from a pip wheel, the driver is the Windows one):

```bash
uv pip install --target ~/cuda-libs nvidia-cuda-nvrtc-cu12==12.9.86
source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh        # LD_LIBRARY_PATH, CARGO_TARGET_DIR=~/turmite-target
```

CLI, same arguments and CSV as `sweep_lean` (byte-identical when no seeds are used):

```bash
cargo run --release --features cuda --bin gpu_sweep -- 2 12 100000000 8192 --lanes 4096 --stats results/x.json > out.csv
printf 'RRLLLRLLLRRR\nRL 7\n' | gpu_sweep - - 1000000        # stdin lines: RULE or RULE SEED
gpu_sweep 2 10 1000000 --bg-seeds 1..8                       # every rule x background seeds 1..=8 (adds a bg_seed column)
```

Library (`--features cuda`), results are index-aligned with the jobs and independent of lanes/slices/batch:

```rust
use turmite::gpu::{GpuConfig, GpuSweeper, Job};
let mut sw = GpuSweeper::new(GpuConfig { lanes: 4096, ..GpuConfig::default() })?;
let results: Vec<turmite::fast::RunResult> = sw.run(&jobs, |done| eprintln!("{done}"))?;
```

Seed semantics: the ant is deterministic, so a "seed" can only be the random background of `ext::bg_colour`
(the repo's existing seeded instrument); `None` is the blank census background. Turn noise, several ants,
turmites with states and the probe statistics (visited set, perimeter, windows) are **not** ported.
Limits: 1..=128 colours; a job whose footprint exceeds the whole tile pool is an error; if you hold two
sweepers, give each an explicit `pool_tiles` (the default grabs all free VRAM).
Tuning: lanes should be at least about 4000 (device throughput at 1e8 steps rose 2.5e9 -> 4.7e9 -> 7.3e9
steps/s for 1024 -> 2048 -> 4096 lanes and had not saturated); `--slice` only needs to keep one launch under ~1 s.

## Results (2026-10-16)

Tests (`source scripts/env.sh; cargo test --release --features cuda --test gpu --test onset`): all pass. They compare
every `RunResult` field with `fast::run` over four rigs (grid 64 = one tile, ragged grid 100, a 16-tile pool
that forces requeues, 64 lanes), compare seeded backgrounds against a dense CPU reference, check known
highways (Langton's ant period 104) and check the error paths. `tests/onset.rs` checks `src/onset.rs`.

Benchmarks (`scripts/bench.sh`, `scripts/summarise_bench.py`, logs and `bench_summary.json` in `results/`),
census lengths 2..=12 = 4083 rules, grid 8192, `sweep_lean` on 6 rayon threads, GPU = RTX 4000 Ada,
wall time of the whole process (includes ~1 s GPU setup, CPU highway-onset replay and CSV), one run each:

| steps | `sweep_lean` | GPU 1024 lanes | 2048 | 4096 | CSV vs `sweep_lean` |
|---|---|---|---|---|---|
| 1e6 | 67.7 s | 5.8 s (11.7x) | n/a | 5.7 s (11.8x); 8192 lanes: 6.0 s (11.3x) | identical in every run |
| 1e8 | 287.3 s | 154.4 s (1.9x) | 86.2 s (3.3x) | 59.0 s (4.9x) | identical in every run |

Also: `gpu_sweep 2 10 1000000` vs `sweep_lean` (1013 rules) byte-identical in the first check.

Against the registered predictions:
- **P1 holds.** Every GPU CSV compared (13 runs) is byte-identical to `sweep_lean`; all proptests pass.
- **P2 (3-8x, falsified if < 2x): holds at 1e8 steps (4.9x at 4096 lanes), exceeded at 1e6 steps (11.8x), but the 1e6
  figure is mostly not stepping.** At 1e6 steps `sweep_lean` spends its time on per-rule overhead (clearing and
  scanning a 67 MB grid, rebuilding a 250k-position trail); the GPU kernel itself needed ~0.4 s for 3.8e9 steps.
  The 1e8 figure is the fair stepping comparison. At 1024 lanes the 1e8 result is 1.9x, below the
  2x line, but that is an under-filled device, not the registered configuration.
- **P3 (saturation between 2k and 8k lanes): not confirmed.** At 1e8 steps throughput was still rising
  linearly at 4096 lanes, and this slice has only 4083 jobs so more lanes cannot be tested here. At 1e6 steps the curve is
  flat from 1024 lanes, but there the run is limited by setup, detection and onset replay, not by lanes.

What this does not show: variance (one run per cell, no repeats), behaviour with more jobs than lanes at large
budgets (pool pressure, `oom_requeues` was 0 in every benchmark), or speed on rules with `n > 12`.
The tail of a sweep (last few ants running alone) lowers the average device throughput; a sweep with many more
jobs than lanes should come closer to the steady rate (not measured).

### Contamination (reported, not used)
A first 1e6 benchmark and the first 1e8 `sweep_lean` run overlapped the `2026-10-kappa-leadrun-fresh` probe on all
cores (lean read 179.4 s and 374.8 s). Those numbers are discarded; the table above is from re-runs on an idle machine.
The probe's own output is unaffected (seed-determined), its wall time may be inflated.

## Open / next
- (Done 2026-10-16/19: the probe port exists as `gpu_probe`, see `../2026-10-gpu-probe/`; it was byte-identical to `probe` and ran
  about 5.8x faster at `probe 27 8192`, with the caveat in its README.) When to choose which GPU tool and how to time them safely:
  `../../README.md` ("Using the GPU sweeper") and `AGENTS.md` ("GPU (CUDA) tools").
- Original item, kept for the record: port the probe statistics (visited flag, area, perimeter, gyration moments, octave windows) to the kernel: that is
  what the `probe 27 8192` runs need (stepping-bound, ~3e11 steps per 2400 runs). Needs its own oracle test against `src/probe.rs`.
- Onset replay is still CPU (9 s of 59 s at 1e8): could be a second GPU pass.
- Overlap the onset replay with the sweep and stream CSV rows; stop paying NVRTC compile on each launch (cache the PTX).
