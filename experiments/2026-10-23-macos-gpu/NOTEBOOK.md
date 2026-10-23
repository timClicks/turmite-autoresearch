# macOS GPU support lab notebook

## 2026-10-23T11:55:01Z — intent — b942a82854b4d61222301959b9895060d2543d3f

Add an optional native wgpu sweep backend. Keep bounded-board, seeded-background and highway semantics. Start with public oracle tests before the implementation. The local device reports Apple M4 Max, 40 GPU cores, Metal support and 64 GiB system memory. Do not infer a speedup from hardware specifications.

## 2026-10-23T11:55:01Z — decision — b942a82854b4d61222301959b9895060d2543d3f

Use one invocation per ant and reuse the CUDA tile-pool design. Retain the current CUDA and CPU code paths. Add a separate `wgpu_sweep` binary so optional backend dependencies and errors remain explicit. The pruning-index match concerns conservation laws and does not exclude this correctness work.

## 2026-10-23T12:15:49.551Z — observation — c0c93c981811ef96074791c0a96d439029a05ecc

The public oracle test first failed because portable_gpu did not exist. After implementation, the Metal oracle passed. The original 16-tile pressure fixture did not force exhaustion on this GPU; its retry-count assertion failed. Replaced that fixture with four lanes sharing one tile on a one-tile board, so retries are forced while every solo job can fit. The corrected pressure test and reuse after a solo allocation error passed.

## 2026-10-23T12:15:49.551Z — observation — c0c93c981811ef96074791c0a96d439029a05ecc

All seven Metal integration tests, two CLI parser tests, shader validation, invalid-configuration tests and the explicitly enabled counter-carry hardware test passed. The full CPU release suite passed 205 tests. Clippy succeeded with both GPU features; old warnings remain, none in the added files. The 57-rule census CSV equals CPU sweep byte-for-byte. A mixed blank/seeded CLI example also ran on Metal. See results/validation.json for commands, source and binary hashes, seed and output provenance.

## 2026-10-23T12:15:49.551Z — decision — c0c93c981811ef96074791c0a96d439029a05ecc

Keep this as native census support. Do not claim a Mac speedup from correctness evidence. Future work should first measure lane count, slice length, readback and host detection costs; compare an optional native wgpu 64-bit shader before committing to a separate Metal implementation. CUDA hardware, hosted CI and other GPU platforms remain untested here.

## 2026-10-23 — intent / deviation (f3c8aae)

Measure end-to-end Metal speed relative to both CPU runners. Registered cases and predictions in README before running. CodSpeed exec harness is unavailable on Apple ARM; user explicitly authorized local wall-clock timing. Use monotonic Node timing, rotating backend order, output equality and five measured repetitions. No runtime implementation changes. Desktop applications are active; record this confounder.

## 2026-10-23T12:56:39.801Z — observation (f3c8aae860e2c8f3db8715b697132aba14e03a74)

Completed small: five samples per backend, one warmup each, rotating order. Every CSV matched SHA-256 186ba51b60017135b6695af3f20f37a63fd0ad0ed20ca68725aaa58e269fa2cd. Median seconds: fast=0.00515525, lean=0.006230708, Metal=0.040484834. See results/benchmark-small.json for all samples and provenance.

## 2026-10-23T12:57:19.060Z — observation (f3c8aae860e2c8f3db8715b697132aba14e03a74)

Completed batch: five samples per backend, one warmup each, rotating order. Every CSV matched SHA-256 7034cff93e7238bbdf7f551b5506b6ba05db3e365967c17487e64d1dbe4a145e. Median seconds: fast=1.313243167, lean=2.573710375, Metal=0.712973875. See results/benchmark-batch.json for all samples and provenance.

## 2026-10-23T12:58:25.291Z — observation (f3c8aae860e2c8f3db8715b697132aba14e03a74)

Completed long: five samples per backend, one warmup each, rotating order. Every CSV matched SHA-256 c747b55d4d8cabbc641c30939e858a5b46807681a7e85b3570a2f5ac484641d3. Median seconds: fast=2.8472575, lean=2.572413709, Metal=4.099581417. See results/benchmark-long.json for all samples and provenance.

## 2026-10-23T12:58:46.039Z — registered follow-up

The first three cases show that longer budgets with only 1013 jobs lose to CPU, while 4083 shorter jobs win. Before measuring the wide case, predict that 4083 jobs at ten million steps improve the CPU/Metal ratio relative to the 1013-job long case. Keep grid 2048, 4096 lanes, default slice and pool, five repetitions and 16 CPU workers. This changes the rule population as well as batch width, so it cannot isolate occupancy as the cause. No shader or runtime changes.

## 2026-10-23T13:01:51.158Z — registered pool follow-up (655aec0a556ab0328c556014dd3fa10e1dde6983)

The wide warmup and first measured runs report about 2000 pool-pressure retries with 65536 tiles (256 MiB). Predict that increasing only the pool to 262144 tiles (1 GiB) removes retries and reduces time on the same 4083-rule, ten-million-step workload. Keep lanes 4096, slice 65536, grid 2048, five samples and CPU baselines unchanged. The larger pool also increases setup/zeroing cost. This is an adaptive follow-up; preserve default-pool measurements.

## 2026-10-23T13:02:58.845Z — observation (655aec0a556ab0328c556014dd3fa10e1dde6983)

Completed wide: five samples per backend, one warmup each, rotating order. Every CSV matched SHA-256 0d5b87b237422585a5bde2eb0d254b3fecb44fcc85c5f6db03743d733e7c8612. Median seconds: fast=11.427976125, lean=10.329889084, Metal=20.640537459. See results/benchmark-wide.json for all samples and provenance.

## 2026-10-23T13:05:56.689Z — observation (f4fd86d1c17eaf37ae6749caf711f701133fbac6)

Completed wide-pool: five samples per backend, one warmup each, rotating order. Every CSV matched SHA-256 0d5b87b237422585a5bde2eb0d254b3fecb44fcc85c5f6db03743d733e7c8612. Median seconds: fast=11.236093375, lean=10.192403167, Metal=5.067945125. See results/benchmark-wide-pool.json for all samples and provenance.

## 2026-10-23T13:06:29.167Z — interpretation / decision

On this M4 Max, the 4083-rule, one-million-step batch was 1.84x faster on Metal than the faster CPU runner. At ten million steps, the default 256 MiB pool caused 1650–2118 retries and Metal was 2.00x slower. A 1 GiB pool removed retries and made the same workload 2.01x faster (5.068 s versus 10.192 s). The 57-rule case was 7.85x slower, and the 1013-rule, ten-million-step case was 1.59x slower. All ratios use five-run medians and the best CPU baseline per case. Desktop applications remained active. These are end-to-end measurements, not shader-only timings.

The default-pool wide-case prediction failed. The registered pool increase removed retries. Keep defaults unchanged: the useful pool size depends on the workload. Save both winning and losing cases. No CUDA comparison or kernel profiling was performed.
