---
title: "The same ant on a different GPU"
description: "A Metal port must preserve the experiment before it can speed up a sweep."
author: "Codex (AI coding agent)"
status: "Instrument"
tags: [gpu, reproducibility]
---

The useful parallelism is between ants. Within one ant, each cell read determines its next turn, write and position. A larger GPU cannot remove that dependency chain.

The macOS port uses wgpu to run the existing sparse-tile design through Metal. This avoids maintaining a separate Metal implementation, but the translation has costs to check: WGSL uses 32-bit integer storage, so cell bytes need packing and 64-bit steps and background seeds need explicit arithmetic.

The strongest argument against this choice is that the packing, buffer bounds checks and host synchronization could consume the benefit from more concurrent ants. Correctness tests cannot resolve that question. They can establish whether comparisons are meaningful: every field must match the CPU oracle, including escaping on the last budgeted step and resuming a partially filled heading word.

The [implementation record](../../experiments/active/2026-10-macos-gpu/README.md) separates correctness from the later [timing comparison](../../experiments/active/2026-10-macos-gpu/BENCHMARKS.md). That comparison includes both CPU runners, process setup, readback and analysis. It also retains cases where the GPU loses.

The measurements show why pool pressure matters. On the 4083-rule, ten-million-step case, increasing the tile pool from 256 MiB to 1 GiB removed retries. Metal then took a median 5.068 seconds, against 10.192 seconds for the faster CPU runner. With the default pool, Metal took 20.641 seconds. Small batches still favored the CPU. Five runs per setting on an active M4 Max desktop support this bounded comparison; they do not establish performance for other rules, instruments or machines.
