#!/bin/bash
# Stage 2c: band interior ablation (README). usage: bash experiments/archive/2026-10-c-law-mechanism/scripts/run_ablation.sh
set -e
cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals
E=experiments/archive/2026-10-c-law-mechanism
cargo build --release --example c_law_mechanism_trace 2>&1 | tail -1
T=./target/release/examples/c_law_mechanism_trace
for K in Z Y H U; do
  echo "$T band 27 256 1024 512 20261019 $K < $E/results/lists/band_chosen_L.txt  ($(date -Is))" >> $E/results/stage2_run.log
  $T band 27 256 1024 512 20261019 $K < $E/results/lists/band_chosen_L.txt > $E/results/trace_band_abl_$K.jsonl
done
