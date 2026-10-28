#!/bin/bash
# Stage 4: tracer c for bases/mutants, then the P1/P2 kappa probe runs (same pipeline as Part B: probe 27 8192, seeds 601..608).
# usage (repo root, WSL): bash experiments/archive/2026-10-c-law-mechanism/scripts/run_p1.sh
set -e
cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals
E=experiments/archive/2026-10-c-law-mechanism
mkdir -p $E/dumps
cargo build --release --example c_law_mechanism_trace --bin probe 2>&1 | tail -1
T=./target/release/examples/c_law_mechanism_trace
echo "$T blank 24 4096 < $E/results/lists/s4_trace_rules.txt  ($(date -Is))" >> $E/results/stage2_run.log
$T blank 24 4096 < $E/results/lists/s4_trace_rules.txt > $E/results/trace_s4.jsonl
echo "probe 27 8192 < $E/results/p1/p1_specs.txt  start $(date -Is)" > $E/results/p1/p1_probe.log
./target/release/probe 27 8192 < $E/results/p1/p1_specs.txt > $E/dumps/p1_probe.csv 2>> $E/results/p1/p1_probe.log
echo "finished $(date -Is)" >> $E/results/p1/p1_probe.log
sha256sum target/release/probe >> $E/results/p1/p1_probe.log
touch $E/dumps/p1_probe.done
