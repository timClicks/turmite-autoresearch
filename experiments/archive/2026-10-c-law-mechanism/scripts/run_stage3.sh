#!/bin/bash
# Stage 3 (README): sparse-background dose-response. usage: bash experiments/archive/2026-10-c-law-mechanism/scripts/run_stage3.sh
set -e
cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals
E=experiments/archive/2026-10-c-law-mechanism
T=./target/release/examples/c_law_mechanism_trace
: > $E/results/lists/sbg_specs.txt
while read -r R; do
  echo "sbg:$R:1:0" >> $E/results/lists/sbg_specs.txt
  for D in 0.02 0.05 0.1 0.2 0.4 0.7 1.0; do
    for S in 1 2 3 4; do echo "sbg:$R:$S:$D" >> $E/results/lists/sbg_specs.txt; done
  done
done < $E/results/lists/band.txt
wc -l $E/results/lists/sbg_specs.txt
echo "$T blank 24 4096 < $E/results/lists/sbg_specs.txt ($(date -Is))" >> $E/results/stage2_run.log
$T blank 24 4096 < $E/results/lists/sbg_specs.txt > $E/results/trace_sbg.jsonl
wc -l $E/results/trace_sbg.jsonl
