# Lab notebook: GPU ant sweep

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-16 · d4fd349 · intent
User goal (/goal): "A re-usable CUDA-enabled utility to sweep runs thousands of independent (rule, seed) ants".
Build a feature-gated CUDA module + `gpu_sweep` binary whose output matches `sweep_lean` byte for byte,
test it against the CPU oracles, then measure speed against `sweep_lean` at 6 threads. Prediction P2
(3-8x) is registered in the README before timing.

### 2026-10-16 · d4fd349 · observation
Environment: `nvidia-smi` shows RTX 4000 Ada (20 GB, driver 582.08) + Quadro P1000; WSL sees both
(`nvidia-smi -L`). No `nvcc`, `sudo` needs a password. `uv pip install --target ~/cuda-libs nvidia-cuda-nvrtc-cu12`
gave NVRTC 12.9.86 and a scratch crate using `cudarc 0.19.10` (driver + nvrtc + dynamic-loading) ran a kernel on device 0.

### 2026-10-16 · d4fd349 · decision
"Seed" has no meaning for the blank-background census ant (deterministic). The only existing seeded
instrument in the repo is the random background (`ext::bg_colour`). So a job's seed is that background
seed (`None` = blank). Considered porting the noisy-turn stream too; deferred (needs a per-lane RNG and
the CPU oracle in `ext.rs` has several ants/state; out of scope for this utility).

### 2026-10-16 · d4fd349 · assumption
Number of colours <= 128 (u8 cell, rule bits in 4 x u32), same bound family as `lean` (< 100). Check: host asserts.

### 2026-10-16 20:0x (+13) · d4fd349 · observation
Correctness first: `gpu_sweep 2 10 1000000` vs `sweep_lean 2 10 1000000` (1013 rules, grid 8192): `cmp` says
byte-identical. `cargo test --release --features cuda --test gpu`: 6/6 pass (proptest vs `fast::run` over
4 rigs: one-tile grid 64, ragged grid 100, tight pool of 16 tiles, 64 lanes; seeded background vs a dense CPU
reference using `ext::bg_colour`; known highways; error paths). `pool_pressure_requeues_and_stays_correct`
asserts `oom_requeues > 0`, so the requeue path is really exercised.

### 2026-10-16 20:0x (+13) · d4fd349 · surprise
`tests/gpu.rs` first failed because each rig auto-sized its tile pool to all free VRAM and the first one took
everything ("no room for a tile pool"). Fixed in the tests (explicit `pool_tiles`); the library default stays
"all free VRAM", so anyone holding two sweepers must set `pool_tiles`. Documented in the README.

### 2026-10-16 20:1x (+13) · d4fd349 · deviation
Contamination: the kappa-leadrun probe (`experiments/archive/2026-10-kappa-leadrun-fresh`, started ~19:45, finished
20:07:29) was running on all 6 cores during my first 1e6 benchmark and during the first ~85 s of the 1e8 lean
baseline. I did not know it was running. Those lean timings (179.4 s at 1e6, 374.8 s at 1e8) are NOT used. I
re-ran both lean baselines alone on an idle machine. The probe's output is unaffected (it depends only on seeds);
its own wall time may be inflated for the overlapping minutes.

### 2026-10-16 20:1x (+13) · d4fd349 · observation
Profile of `gpu_sweep 2 12 1000000` (4083 jobs): setup 1.2-1.4 s, device path 3.8-4.6 s of which the kernel
itself ~0.4 s (blocked-on-device 0.38 s for 3.8e9 steps), and onset replays 8.4 s on the CPU (a fresh 67 MB
grid per highway job). Added `src/onset.rs` (scratch-reusing replay, `tests/onset.rs` checks it against
`highway_onset_flat`, Langton's onset 9976): onset time 8.4 s -> 5.5 s, CSV still identical.
Clean 1e8 lean baseline: 287.3 s (`results/bench_L2-12-1e8.log`).

### 2026-10-16 20:4x (+13) · d4fd349 · observation
Clean benchmarks (idle machine; `results/bench_L2-12-1e6.log`, `bench_L2-12-1e8.log`, `bench_summary.json` from
`scripts/summarise_bench.py`): lengths 2..=12 (4083 rules). 1e6 steps: lean 67.7 s, GPU 5.7 s at 4096 lanes (11.8x).
1e8 steps: lean 287.3 s, GPU 154.4 / 86.2 / 59.0 s at 1024 / 2048 / 4096 lanes (1.9 / 3.3 / 4.9x). All CSVs identical.
`oom_requeues` = 0 in every benchmark.

### 2026-10-16 20:4x (+13) · d4fd349 · interpretation
P2 holds at 1e8 (4.9x, inside 3-8x). The 1e6 number (11.8x) mostly reflects `sweep_lean`'s per-rule overhead, not
stepping (kernel ~0.4 s for 3.8e9 steps), so it should not be quoted as the speedup. Throughput scaled ~linearly
in lanes up to 4096 at 1e8, so P3 (saturation by 2k-8k) is untested here: the slice has only 4083 jobs.
Confidence moderate: one run per cell. Alternative: the 1e8 gain at 4096 lanes is partly tail-limited (last ants alone).

### 2026-10-16 20:4x (+13) · d4fd349 · decision
Left out of this version: turn noise, multi-ant / turmite states, probe statistics (the active kappa-leadrun
experiment needs `probe`, not `sweep`; asked about, answered no), and a GPU onset pass. Listed under "Open / next".
