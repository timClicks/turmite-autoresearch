# Native macOS GPU support

## Question and registered predictions

Registered 2026-10-23T11:55:01Z, from `b942a82854b4d61222301959b9895060d2543d3f`.
Can the existing CUDA sweep contract run through wgpu and Metal without changing the ant or its detector?

- Correctness: every `RunResult` field must equal the CPU oracle for blank and seeded backgrounds, including grid escape, partial heading words, tile crossings and pool-pressure retries.
- Scheduling: changing job order, lane count or slice size must not change a job's output.
- Portability: CPU builds must not need wgpu or a GPU. macOS selects Metal; other native platforms can use Vulkan or DX12.
- Performance hypothesis, not measured: batches of independent ants can hide memory latency on Apple GPUs. A single ant remains serial. No speedup factor is predicted or claimed in this implementation task.

The implementation uses the existing bounded board and sparse 64-by-64 tiles. It keeps byte-sized cells by packing four cells into each WGSL `u32`. Each tile belongs to one invocation, so cell writes need no atomics. Step counters and background seeds use pairs of `u32` values to preserve `u64` semantics without optional shader extensions.

## Pruning-index preflight

At the starting revision, queried `notes/pruning-index/entries` with `rg -n -i -e 'metal|wgpu|gpu|oracle'` and read the only signature, `NR-20261022-additive-laws-order-blind`. That record concerns additive conservation laws; it does not cover GPU implementation or oracle validation. Decision: run bounded correctness checks, without a scientific sweep or exclusions. No dead-end signature is warranted for a platform port.

## Dependencies and backend choice

The optional `wgpu` feature adds wgpu for validated compute and native Metal/Vulkan/DX12 access, pollster for its synchronous CLI, and bytemuck for checked host/shader data layouts. CPU users do not compile these dependencies.

A separate native Metal shader would add a second platform-specific implementation. wgpu translates the same WGSL kernel to Metal and leaves room for other native GPUs. A direct Metal backend is a later option only if measurement identifies a limitation that wgpu cannot address.

Primary documentation: [wgpu](https://docs.rs/wgpu/30.0.1/wgpu/), [WGSL types](https://www.w3.org/TR/WGSL/#types), [Metal resource storage modes](https://developer.apple.com/documentation/metal/resource-storage-modes).

## Reproduction

No justfile or Nix flake exists in this revision. Use release builds.

```sh
PROPTEST_RNG_SEED=20261023 cargo test --release --locked --features wgpu --test portable_gpu
cargo clippy --release --locked --features wgpu --all-targets
cargo test --release --locked
cargo run --release --locked --features wgpu --bin wgpu_sweep -- 2 6 32768 256 --lanes 64
```

GPU tests require a real compatible adapter and fail if it is absent. They do not silently fall back to CPU execution.

## Results and limitations

Validated on Apple M4 Max through Metal at source revision `c0c93c981811ef96074791c0a96d439029a05ecc`. The [correctness record](results/validation.json) contains compiler versions, commands, test counts and SHA-256 hashes of source, binaries, inputs and outputs.

- Full CPU release suite: 205 tests passed.
- Metal integration suite: seven tests passed, including 32 property cases across three configurations with seed 20261023. The independent hardware counter/history test passed across the 32-bit carry boundary.
- WGSL validation and CLI parsing passed. Clippy completed with CUDA and wgpu enabled together; existing repository warnings remain, with no diagnostics in the new files.
- A census of 57 canonical nontrivial rules of lengths 2 through 6, at 32768 steps and grid 256, produced CSV identical to the CPU `sweep` output. Saved output: [census.csv](results/census.csv); device counters: [census-stats.json](results/census-stats.json).
- The mixed blank/seeded stdin path ran with a full-width seed and non-word-aligned slices: [input](results/stdin.txt), [output](results/stdin.csv), [counters](results/stdin-stats.json).

These initial checks establish correctness. The later [timing report](BENCHMARKS.md) measures end-to-end performance on this Mac. CUDA hardware tests, hosted Actions and other native GPU platforms were not run. The first port targets census sweeps. The CUDA `gpu_probe` statistics and the browser simulator are separate instruments.

## CLI and Rust API

```sh
# Explicit rule list, with an optional full-width background seed.
printf 'RL\nRLR 18446744073709551615\n' | cargo run --release --locked --features wgpu --bin wgpu_sweep -- - - 1000000 8192 --lanes 128 --slice 65536 --pool-tiles 65536 --stats run.json
```

The Rust API is `turmite::portable_gpu::{GpuConfig, GpuSweeper, Job}`. Construct a sweeper with `GpuSweeper::new`, then call `run(&jobs, progress)`. Returned rows follow input order. Reuse the sweeper for later batches. `config()` exposes the fixed allocation settings; `device_name`, `backend` and `stats` expose the selected device and completed-job counters.

Default memory is bounded: a 256 MiB tile pool, about 64 MiB each for tile directories and heading rings, another ring-sized staging buffer, and small state/free-list buffers. Exact sizes depend on grid, history and lanes. The constructor checks the adapter's binding and buffer limits before allocation. A shared-memory Mac still needs room for these buffers and CPU onset replay; the pool does not consume all reported system memory.

`--pool-tiles` sets the pool explicitly. If concurrent ants exhaust it, failed ants restart at a lower concurrency. If one ant cannot fit alone, the call returns an error. It never emits a truncated successful row. The next call clears device state after either success or a pool-exhaustion error.

Supported: one-state square-grid ants, 1..=128 colours in the library, blank or `bg_colour` seeded backgrounds, `u64` lifetime budgets, and independent jobs. The CLI parser accepts the repository's standard 2..=128-colour rules on stdin; enumerated rule lengths are 2..=31. Backend limits can impose smaller grid or lane counts. Checkpoints, the CUDA probe statistics, other walkers, other lattices, multi-ant runs and browser WebGPU are not part of this port.

Escape follows `fast::run`: the step out of the board counts, and the outside cell does not extend the bounding box. The known `lean` edge case when the budget ends on exactly that step is not copied; see the tiled-grid design note. This can affect CSV equality with `sweep_lean` for that exact boundary condition.

## Further performance work

The [timing report](BENCHMARKS.md) compares full process wall time with both CPU runners. Gains depend on batch size and tile-pool pressure. Kernel-only timing and profiling remain to be done. Use many independent, long-running jobs to evaluate throughput. Compare the same rules, seeds, grid, detection history, horizon and output hashes against the CPU runner. Separate setup, stepping, readback, detection and onset replay; compare full process wall time as well as dispatch time. Use repeated runs on an idle Mac and report spread and thermal conditions. Keep timestamp queries optional and validate their values before using them.

Start by varying lane count and slice length; the tradeoff is latency hiding versus state readback and dispatch overhead. The current host waits for state readback once per slice and processes detection before the next slice. Overlapping that work and specializing away seeded-background code are later candidates, subject to profiling. Native MSL/objc2-metal is an alternative if validated bounds checks, packed loads, or 64-bit emulation prove material. Its additional implementation and synchronization obligations require the same oracle checks.

wgpu also exposes optional native `SHADER_INT64` arithmetic ([feature documentation](https://docs.rs/wgpu/30.0.1/wgpu/struct.Features.html)). A capability-checked shader variant using it is a smaller next experiment than a separate Metal backend. The initial shader uses paired words so the same exact simulation does not depend on that optional feature.

## Registered timing comparison (2026-10-23)

Before measurements, at source revision f3c8aae: predict that GPU startup makes the 57-rule, 32768-step census slower than both CPU runners. Predict that increasing batch size and step budget improves the CPU/Metal time ratio; the initial port may still lose to the lean CPU loop. No numerical speedup is assumed.

Use `scripts/bench.mjs` for three bounded blank-board workloads: small (lengths 2..6, 32768 steps, grid 256, 64 lanes); batch (2..12, one million steps, grid 2048, 4096 lanes); long (2..10, ten million steps, grid 2048, 1024 lanes). Metal uses 65536-step slices and 65536 pool tiles. Compare `sweep`, `sweep_lean` and `wgpu_sweep`, all release builds and 16 Rayon workers. One warmup per command, then five samples with rotating backend order. Include process setup, simulation, detection, onset replay and CSV writes. Check every output hash. Report median and range, not kernel-only timing. Each invocation has a 180-second limit. `bench.mjs` hashes and runs the binaries under `CARGO_TARGET_DIR` (default `target/`) and refuses to overwrite an existing `results/benchmark-<case>.json`; to repeat a case pass a rerun tag (`node scripts/bench.mjs small rerun1`), which saves `benchmark-small-rerun1.json` and leaves the committed samples intact.

The user authorized local timing after CodSpeed's exec harness failed to install on aarch64-apple-darwin. The machine has active desktop applications; record process and thermal snapshots. This is a desktop comparison, not an isolated hardware benchmark. Pruning-index query `metal|wgpu|gpu|benchmark` found no relevant entries; proceed with platform timing, without scientific exclusions.

## 2026-10-23T12:58:46.039Z — registered follow-up

The first three cases show that longer budgets with only 1013 jobs lose to CPU, while 4083 shorter jobs win. Before measuring the wide case, predict that 4083 jobs at ten million steps improve the CPU/Metal ratio relative to the 1013-job long case. Keep grid 2048, 4096 lanes, default slice and pool, five repetitions and 16 CPU workers. This changes the rule population as well as batch width, so it cannot isolate occupancy as the cause. No shader or runtime changes.

## 2026-10-23T13:01:51.158Z — registered pool follow-up (655aec0a556ab0328c556014dd3fa10e1dde6983)

The wide warmup and first measured runs report about 2000 pool-pressure retries with 65536 tiles (256 MiB). Predict that increasing only the pool to 262144 tiles (1 GiB) removes retries and reduces time on the same 4083-rule, ten-million-step workload. Keep lanes 4096, slice 65536, grid 2048, five samples and CPU baselines unchanged. The larger pool also increases setup/zeroing cost. This is an adaptive follow-up; preserve default-pool measurements.

## Timing outcome

On this M4 Max, the 4083-rule, one-million-step batch was 1.84x faster on Metal than the faster CPU runner. At ten million steps, the default 256 MiB pool caused 1650–2118 retries and Metal was 2.00x slower. A 1 GiB pool removed retries and made the same workload 2.01x faster (5.068 s versus 10.192 s). The 57-rule case was 7.85x slower, and the 1013-rule, ten-million-step case was 1.59x slower. All ratios use five-run medians and the best CPU baseline per case. Desktop applications remained active. These are end-to-end measurements, not shader-only timings.

See [BENCHMARKS.md](BENCHMARKS.md) for sample ranges, exact settings and raw evidence. The prediction that a wider long batch would improve the ratio failed with the default pool; the adaptive larger-pool follow-up removed the observed retries. No runtime source changed.
