# Lab notebook: GPU probe

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-16 20:47 (+13) · 5b97961 (dirty tree) · intent
Task: port `probe` (plain rules and `RULE@SEED`) to the GPU with byte-identical CSV, so `probe 27 8192` batches stop
using the CPU. User message mid-session: "can you use cuda to avoid the cpu contention?" - taken as: the point of the
port, and do the work on the GPU where possible, no CPU-heavy runs while their job is live. Plan: refactor the CPU
window/CSV code into shared functions, new kernel + host module + binary + tests, register predictions, then time.

### 2026-10-16 20:48 (+13) · 5b97961 · observation
The user's own `probe 27 8192` batch (3336 mutant specs, pid 2027659, ~590% CPU, started 20:36) is live. Per the task I do
not benchmark while it runs and I do not touch it. My builds and tests run under `nice`, CPU oracles with `RAYON_NUM_THREADS=2`.
Footprint estimate from the existing 2400-run dump (kappa-leadrun-fresh/dumps/probe.csv, last row per run): sum of
bbox tiles (w/64+2)(h/64+2) = 1.61e6 (mean 670, max 10100 per run); 365 of 2400 runs escaped the 8192 board.
At 8 KiB per tile that is about 13 GB, so it fits in 20 GB VRAM and a 16-bit cell is affordable.
Also: the earlier kappa-leadrun probe wall time (19:46:58 -> 20:07:29 = 1231 s) overlapped the GPU-sweep benchmarks (see
`2026-10-gpu-ant-sweep/NOTEBOOK.md`, deviation), so it is not a clean CPU baseline; the CPU baseline is re-measured here.

### 2026-10-16 20:4x (+13) · 5b97961 · decision
Cell layout: one u16 per cell (colour | unv+1), 8 KiB tiles, instead of two byte planes (the task suggested measuring
both). Reason: a single load per step gives everything. NOT measured against two planes; recorded as untested.
One-byte packing (n <= 32) is the fallback if VRAM binds. Scheduler duplicated from `GpuSweeper::run` rather than
generalised, so `tests/gpu.rs` keeps guarding an untouched sweep.

### 2026-10-16 20:4x (+13) · 5b97961 · decision
Patch init at tile allocation for the patch cells inside that tile (not "when the first tile is allocated" as the task
suggested): at size 8192, c = 4096 is a multiple of 64, so the 5x5 patch spans four tiles. Tests include grids with
c = 63, 64, 65 for this.

### 2026-10-16 20:4x (+13) · 5b97961 · observation
CPU refactor check: old binary saved as `~/probe_old` before editing; new `probe` vs `probe_old` on 18 mixed specs
(plain, `@`, rotor:, rw:, sbg:, brotor:, nrotor:, pw:, cookie:, rcookie:, errw:), at `17 1024` and `15 8192`: `cmp`
identical both times (149 and 125 lines). First `gpu_probe` vs `probe_old` on the ant specs (`17 1024`: 59 lines,
`15 8192`: 50 lines; 16 lanes, odd slice 100003): byte-identical on the first try.

### 2026-10-16 20:4x (+13) · 5b97961 · observation
`cargo test --release --features cuda --test gpu_probe`: 5/5 pass in 109 s (48 proptest cases x 7 rigs: one-tile 64,
ragged 100, c=63/64/65 grids, tight pool of 16 tiles, 64 lanes at min_log2 8; scheduling independence by reversing job
order; starved pool with `oom_requeues > 0` asserted; mid-window escape; error paths).

### 2026-10-16 20:55 (+13) · 5b97961 · observation
Full-scale spot check (`scripts/spotcheck.sh`, every 100th spec of kappa-leadrun-fresh, 24 specs, `27 8192`): GPU CSV
byte-identical to the new CPU `probe` (439 rows, sha256 84fa1fa8..., 2 of 24 runs escaped the board). CPU side ran 1 thread
niced (291 s) because the user's batch was live; GPU 54 s for 24 ants on 32 lanes. Output: `results/spotcheck.txt`.

### 2026-10-16 20:58 (+13) · 5b97961 · observation
All 2400 specs on the GPU (`gpu_probe 27 8192 --lanes 2400`), compared with the existing kappa-leadrun CPU dump
(`2026-10-kappa-leadrun-fresh/dumps/probe.csv`): `cmp` IDENTICAL; `oom_requeues` 0; wall 177 s (device path 161 s).
This run is NOT a benchmark: the user's 3336-spec probe was still running on 6 cores until 20:53:47 (their log), and the
CPU baseline needed for a ratio had not been measured. Kept in scratch/ only. Prediction P1 (second half) and P3 hold.

### 2026-10-16 20:59 (+13) · 5b97961 · deviation
The user's batch finished at 20:53:47, but at ~20:59 a different session started building my tree into
`~/turmite-target-probeport` and running `gpu_probe 27 8192 --lanes 2400` (pid 2051469, not mine). I did not touch it. A timing run
now would overlap it on the GPU (and its CPU part on 1 core), so I wait until no `release/` or cargo process has been seen for
3 minutes (`~/quiet_649.sh`) and then run `scripts/bench.sh` (gpu1, cpu, gpu2, never overlapping, with before/after process checks).

### 2026-10-16 21:02 (+13) · 5b97961 · decision
User said "pause" and then "prepare to wrap up for the day.. write a handover doc". Stopped before the clean benchmark; killed only my own
wait helper. Wrote `HANDOVER.md`. State: code and correctness done (tests 5/5, 24-spec and 2400-spec byte-identity); timing (P2), the
rest of the test suite after the `src/probe.rs` refactor, `notebook.ipynb` and the commit remain. The one 177 s GPU figure is contaminated
(user's CPU batch live) and must not be cited as a benchmark. If the clean ratio lands near 7x, P2 (2-6x) is falsified on the fast side.

### 2026-10-17 17:56 (+13) · 53ccccc · observation
Clean benchmark (`scripts/bench.sh`, idle machine, phases sequential): gpu1 177.4 s, cpu 681.6 s, gpu2 176.9 s, all three CSVs byte-identical to the
kappa-leadrun CPU dump. Speedup 3.84x. P2 (2x-6x, central 3.5x) HELD; P3 held (0 requeues); P1 held; P4 untested.

### 2026-10-17 17:57 (+13) · 53ccccc · interpretation
The handover's "about 7x, P2 falsified" was wrong: it divided by a CPU time (1231 s) contaminated by the GPU-sweep benchmarks. The clean CPU time is 681.6 s.
The GPU figure was the same with and without the user's batch running (177 s both times), so the GPU path was never the contaminated side. Pool use (2.41e6 tiles)
exceeded my 1.6e6 bounding-box estimate by about 50% without requeues. Single spec set, so 3.84x is a measurement for this workload, not a general speed claim.

### 2026-10-17 17:58 (+13) · 53ccccc · observation
`cargo test --release` (plain) and `--features cuda --test gpu --test onset` pass after the `src/probe.rs` refactor (plain log was tail-only).

### 2026-10-18 19:37 (+13) · 14b9a24 · intent
Run P4 as registered in the README ("Steps/s rises with lanes from 1024 to 2400 (every ant resident)"), text unchanged. Recipe:
`scripts/bench_lanes.sh`, `gpu_probe 27 8192 --lanes L` on the same 2400 kappa-leadrun-fresh specs as P2, L in {1024, 1536, 2400}, two
repeats each in interleaved order 2400,1024,1536,1536,1024,2400. Every CSV is cmp'd against the CPU dump. Operational criterion, fixed now:
P4 holds if the mean whole-process wall time strictly decreases 1024 > 1536 > 2400 with each gap larger than the larger within-L repeat
spread, and the same order holds for device-path time (`wall_secs` in `--stats`). Steps/s uses one numerator for all L (outputs are identical,
so `total_steps`, the budget of non-escaped runs, is the same), so the ratio of steps/s is the inverse ratio of times. Caveat registered now:
at L < 2400 ants queue and lanes are refilled between slices, so lower L also means more slices and more host turnarounds, and the 2400 case
has an all-ants-resident tail with idle lanes that the queued cases partly avoid. The test therefore compares batch throughput, not per-lane
throughput at fixed occupancy.

### 2026-10-18 19:37 (+13) · 14b9a24 · deviation
Machine not idle: another session's `run_mutants.sh` (worktree `.claude/worktrees/paper-figure-proposals`, CPU `probe 27 8192` on 3336
mutant specs, 6 threads, started 19:34:34) is running. Not mine; not touched. `bench_lanes.sh` waits until no `release/` or cargo process
has been seen for 3 minutes before its first phase. The gpu_probe binary is rebuilt from HEAD (writes `total_steps`, which the P2 build did
not), so its sha256 differs from `bench.log`'s; same kernel source as 53ccccc (no src changes since).

### 2026-10-18 19:45 (+13) · 14b9a24 · surprise
The P2 benchmark (`results/bench.log`, header "git 53ccccc") did not run a binary built from 53ccccc. The binary at
`~/turmite-target/release/gpu_probe` before this session's rebuild had sha256 4d3e395d... (the value in `bench.log`) and mtime
2026-10-16 20:46:17, and its output format ("2400 jobs in 160.96s", `--stats` without `total_steps`/`steps_per_sec`) does not match
53ccccc's `src/bin/gpu_probe.rs`, which prints and writes both. So `bench.sh`'s `cargo build ... | tail -1` either failed or did not
rebuild, and the pipe hid it. Consequence for P2: the timed binary is the 2026-10-16 20:46 build, the one that produced the 24-spec and
2400-spec identity checks that evening; its kernel and scheduler may differ from 53ccccc in ways I cannot reconstruct. The outputs were
byte-identical to the CPU dump, so P1's conclusion stands for that binary; the 3.84x is a measurement of that binary, not provably of 53ccccc.
Copy kept: `scratch/p2_binary/gpu_probe` (gitignored). `bench_lanes.sh` builds after the quiet wait, checks the build's exit status and logs mtime.

### 2026-10-18 19:45 (+13) · 14b9a24 · correction
In the 19:37 deviation entry, "same kernel source as 53ccccc (no src changes since)" is true of HEAD vs 53ccccc but says nothing about the
P2 binary, which (previous entry) was not built from 53ccccc. P4 is therefore self-contained: its own 2400-lane phases are the baseline,
and P4 numbers should not be divided into or by P2's.

### 2026-10-18 19:40 (+13) · 14b9a24 · correction
The two entries stamped "19:45" (surprise, correction) were written at about 19:38; I mis-stamped them. Content unchanged.
`bench_lanes.sh` launched 19:38 (pid 165521), waiting for the other session's mutant batch (800/3336 at 19:39, expected done ~19:56).

### 2026-10-18 20:00 (+13) · 14b9a24 · observation
Cause of the stale P2 binary found. `src/bin/gpu_probe.rs`, `src/gpu/probe.rs`, `src/gpu/probe.cu` on `/mnt/f` carry mtimes 2026-10-16
20:41-20:43, older than the binary (20:46), although their content changed later (current source prints "steps in" and "setup", the
binary does not). Cargo's freshness check therefore kept the old binary: `bench_lanes.sh`'s build step "finished in 0.08s" and the first
P4 phase started (19:55:19) with sha256 4d3e395d..., the P2 binary. I stopped that run (my own pid, killed after ~1 min), kept its log as
`scratch/bench_lanes_aborted_stale.log`, deleted its partial CSV. Wider hazard: anything built in `~/turmite-target` since 10-16 may be
stale the same way, including the README's "5/5 gpu_probe proptests" and post-refactor `cargo test` claims.

### 2026-10-18 20:01 (+13) · 14b9a24 · decision
Build into a fresh `CARGO_TARGET_DIR=~/turmite-target-p4` (did compile turmite, 8.5 s incremental of deps; sha256 91c072f7...; contains
"steps in"). `bench_lanes.sh` now exports that dir and aborts unless the binary's sha equals `EXPECT_SHA`. The first phase's `cmp` against
the CPU dump is the first full-scale identity check of the HEAD binary; if it differs, P4 timing is secondary and I stop. Source mtimes not
touched. After the phases, if time allows, `cargo test --release --features cuda --test gpu_probe` in the fresh dir.

### 2026-10-18 20:27 (+13) · 14b9a24 · observation
`bench_lanes.sh` finished 20:25:24, all six phases clean (no foreign process before/after any phase; load ~1). Binary 91c072f7... (fresh
build). Every CSV byte-identical to the CPU dump: first full-scale identity check of the HEAD binary, passed 6/6. Whole-process wall
r1/r2: L=2400 156.64/156.24 s, L=1536 219.30/219.41 s, L=1024 280.34/280.25 s. Device path (`wall_secs`): 154.35/154.16, 217.16/217.26,
278.14/278.12 s. `total_steps` 273133076480 in every run (as expected, outputs identical). Launches 128/256/319; 0 requeues; pool_tiles
2409451/2416681/2420965 (2400/1536/1024).

### 2026-10-18 20:28 (+13) · 14b9a24 · interpretation
P4 HELD on the pre-fixed criterion: mean times strictly fall with L, gaps ~61-63 s vs repeat spread <= 0.40 s, same order on the device
path. Device steps/s 0.982e9 / 1.257e9 / 1.771e9. This is mostly queueing: with refill, 2400 jobs at L=1024 is ~2.3 job-rounds, at 1536
~1.6, at 2400 one. Per-lane steps/s falls with occupancy (9.59e5, 8.19e5, 7.38e5 per lane; -23% from 1024 to 2400), so the GPU is not
idle-lane-bound at 1024 but loses per-lane speed as resident ants grow; cause untested (memory traffic is the guess). The test measures
batch throughput on one spec set with n = 2 per L, not per-lane efficiency at fixed occupancy. HEAD at L=2400 (156 s) is faster than the
stale P2 build (177 s); not compared further since the binaries differ and no new CPU baseline was taken.

### 2026-10-18 20:40 (+13) · 14b9a24 · observation
`cargo test --release --features cuda --test gpu_probe` on the fresh build (`~/turmite-target-p4`): 5/5 pass. Plain `cargo test --release` and `--test gpu --test onset`
were last run in the possibly stale `~/turmite-target` and are not yet rerun on a verified build. Open: paired P2 re-measure (rebuild `probe` at HEAD, re-time CPU, ~11 min).

### 2026-10-19 08:25 (+13) · 6de71f2 · intent
Finish HANDOVER items 1-4. Machine idle (no `release/` or cargo processes; GPU 0-20% from the other adapter). New `scripts/bench_p2.sh` builds `probe` and `gpu_probe` in a fresh
`~/turmite-target-p2`, checks exit status and that binaries are newer than the sources, logs sha256, then times gpu1, cpu, gpu2. No tests while it runs.

### 2026-10-19 08:53 (+13) · 6de71f2 · observation
`bench_p2.sh` exit 0, no foreign process before/after any phase. Binaries: probe 7d341949..., gpu_probe 91c072f7.... Whole-process wall: gpu1 157.06 s, cpu 912.49 s, gpu2 156.94 s; device path
154.79/154.72 s. All three CSVs cmp-identical to the kappa-leadrun dump; cpu vs gpu1 identical. Speedup 5.81x.

### 2026-10-19 08:55 (+13) · 6de71f2 · interpretation
By the criterion registered 2026-10-16 (falsified if >= 4.9x), P2 is **falsified** at HEAD, from above. The stale-build 3.84x ("held") is superseded. The GPU time barely moved (177 -> 157 s); the
CPU baseline went 681.6 -> 912.5 s (+34%) and that drives the ratio. Why the CPU `probe` is slower is unexplained (old binary f1a309cf from the suspect dir; possible code change in the `src/probe.rs`
refactor, or machine state). Not bisected. Prediction text not edited.

### 2026-10-19 09:10 (+13) · 6de71f2 · observation
Verified-build tests (`~/turmite-target-p2`): `cargo test --release` all ok; `--features cuda --test gpu --test onset --test gpu_probe`: 7/7, 1/1, 5/5. `bench.sh` and `spotcheck.sh` fixed (build exit status,
stale-binary check). The earlier stale-dir test passes are superseded.

### 2026-10-19 09:15 (+13) · 6de71f2 · question
Open: why is the HEAD CPU `probe` 34% slower than the old one? A cheap check is to time `probe 27 8192` on a 100-spec subset with the old commit (before the `src/probe.rs` refactor) built in a fresh dir. Not done.
