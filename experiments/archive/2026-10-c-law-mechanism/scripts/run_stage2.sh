#!/bin/bash
# Stage 2 tracer runs (README). Deterministic; output order = input order. usage: bash experiments/archive/2026-10-c-law-mechanism/scripts/run_stage2.sh
set -e
cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals
E=experiments/archive/2026-10-c-law-mechanism
cargo build --release --example c_law_mechanism_trace 2>&1 | tail -1
T=./target/release/examples/c_law_mechanism_trace
{
  echo "commit $(git rev-parse --short HEAD) (+ uncommitted working tree), $(date -Is)"
  echo "$T blank 24 4096 < $E/results/lists/calib.txt"
  echo "$T blank 24 4096 < $E/results/lists/sample.txt"
  echo "$T blank 24 4096 < $E/results/lists/valid_candidates.txt"
  echo "$T band 30 256 1024 512 20261019 < $E/results/lists/band.txt"
} > $E/results/stage2_run.log
time $T blank 24 4096 < $E/results/lists/calib.txt > $E/results/trace_calib.jsonl
time $T blank 24 4096 < $E/results/lists/sample.txt > $E/results/trace_sample.jsonl
time $T blank 24 4096 < $E/results/lists/valid_candidates.txt > $E/results/trace_valid_raw.jsonl
time $T band 30 256 1024 512 20261019 < $E/results/lists/band.txt > $E/results/trace_band.jsonl
wc -l $E/results/trace_*.jsonl >> $E/results/stage2_run.log
ls -la $E/results/trace_*.jsonl
