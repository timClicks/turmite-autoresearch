#!/bin/bash
# Deviation rerun of the random-walk calibration at 2^20 steps (see NOTEBOOK 18:50). usage: bash experiments/archive/2026-10-c-law-mechanism/scripts/run_stage2b.sh
set -e
cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals
E=experiments/archive/2026-10-c-law-mechanism
T=./target/release/examples/c_law_mechanism_trace
echo "$T blank 20 4096 < $E/results/lists/calib_rw.txt  ($(date -Is))" >> $E/results/stage2_run.log
$T blank 20 4096 < $E/results/lists/calib_rw.txt > $E/results/trace_calib_rw.jsonl
