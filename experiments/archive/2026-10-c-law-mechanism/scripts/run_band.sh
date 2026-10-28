#!/bin/bash
# Band reruns after the void 2^30 run (README deviation): L = 24..29, each over the 60 band rules. usage: bash experiments/archive/2026-10-c-law-mechanism/scripts/run_band.sh
set -e
cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals
E=experiments/archive/2026-10-c-law-mechanism
T=./target/release/examples/c_law_mechanism_trace
for L in 24 25 26 27 28 29; do
  echo "$T band $L 256 1024 512 20261019 < $E/results/lists/band.txt  ($(date -Is))" >> $E/results/stage2_run.log
  $T band $L 256 1024 512 20261019 < $E/results/lists/band.txt > $E/results/trace_band_L$L.jsonl
done
