# Metal timing results

Measured on Apple M4 Max (40 GPU cores), 64 GiB memory, 16 Rayon workers. Values are median process wall seconds across five measured samples per backend, after one warmup. Backend order rotates each round. A ratio above 1 means Metal is faster. The CPU comparison uses the faster median of both CPU implementations in each case.

| Case | Rules | Step budget per rule | Pool MiB | CPU fast (s) | CPU lean (s) | Metal (s) | Best CPU / Metal | Retries |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| small | 57 | 32768 | 256 | 0.0052 | 0.0062 | 0.0405 | 0.13x | 0–0 |
| batch | 4083 | 1000000 | 256 | 1.3132 | 2.5737 | 0.7130 | 1.84x | 0–0 |
| long | 1013 | 10000000 | 256 | 2.8473 | 2.5724 | 4.0996 | 0.63x | 0–0 |
| wide | 4083 | 10000000 | 256 | 11.4280 | 10.3299 | 20.6405 | 0.50x | 1650–2118 |
| wide-pool | 4083 | 10000000 | 1024 | 11.2361 | 10.1924 | 5.0679 | 2.01x | 0–0 |

## Method and scope

Release builds, identical canonical nontrivial blank-board rules, same grid and budget per case. Every measured CSV matched byte-for-byte by SHA-256. Commands include process and GPU setup, simulation, readback, detection, onset replay and CSV writes. They do not isolate shader time. Warmups are excluded, so these are repeated-launch results with warm system caches, not first-launch latency. The GPU can stop jobs at board escape: budgets are upper bounds, not actual work counts. Saved device counters contain actual steps.

No thermal or performance warning was reported by pmset before or after these runs; that is not a temperature measurement. Desktop applications remained active, including a busy browser process. This is one machine and one session, with five repetitions and no claim of a hardware-wide confidence interval. Different rule populations in the batch and long cases prevent attributing the difference solely to occupancy. The wide-pool case repeats the wide workload with a 1 GiB tile pool.

## Sample ranges

- small: sweep: 0.0042–0.0081 s; sweep_lean: 0.0054–0.0077 s; wgpu_sweep: 0.0401–0.0442 s.
- batch: sweep: 1.2927–1.3939 s; sweep_lean: 2.5415–2.6524 s; wgpu_sweep: 0.6933–0.7153 s.
- long: sweep: 2.7813–2.8708 s; sweep_lean: 2.5393–2.8063 s; wgpu_sweep: 4.0611–4.1480 s.
- wide: sweep: 11.2886–11.6405 s; sweep_lean: 10.1036–10.7071 s; wgpu_sweep: 15.0311–25.8173 s.
- wide-pool: sweep: 11.1008–11.2909 s; sweep_lean: 10.1455–10.3320 s; wgpu_sweep: 5.0352–5.0757 s.

## Reproduce

No runtime source changes were made for the comparison. The first three cases use the harness saved in commit 655aec0. Each JSON records its source revision, harness and binary hashes, all command arguments, process snapshots, thermal status, output hash and individual samples. Later harness additions only add cases and a configurable pool.

```sh
cargo build --release --locked --features wgpu --bin sweep --bin sweep_lean --bin wgpu_sweep
for case in small batch long wide wide-pool; do
  node experiments/2026-10-23-macos-gpu/scripts/bench.mjs "$case"
done
node experiments/2026-10-23-macos-gpu/scripts/summarise-bench.mjs
```

CodSpeed could not install its exec harness on aarch64-apple-darwin. Local monotonic wall-clock timing was explicitly authorized by the user. See README and NOTEBOOK for predictions registered before each case and the pool-size follow-up.

## Raw evidence

- [small](results/benchmark-small.json): CSV SHA-256 `186ba51b60017135b6695af3f20f37a63fd0ad0ed20ca68725aaa58e269fa2cd`; 1642464 actual GPU steps.
- [batch](results/benchmark-batch.json): CSV SHA-256 `7034cff93e7238bbdf7f551b5506b6ba05db3e365967c17487e64d1dbe4a145e`; 3699514609 actual GPU steps.
- [long](results/benchmark-long.json): CSV SHA-256 `c747b55d4d8cabbc641c30939e858a5b46807681a7e85b3570a2f5ac484641d3`; 8861342902 actual GPU steps.
- [wide](results/benchmark-wide.json): CSV SHA-256 `0d5b87b237422585a5bde2eb0d254b3fecb44fcc85c5f6db03743d733e7c8612`; 36049509246 actual GPU steps.
- [wide-pool](results/benchmark-wide-pool.json): CSV SHA-256 `0d5b87b237422585a5bde2eb0d254b3fecb44fcc85c5f6db03743d733e7c8612`; 36049509246 actual GPU steps.
