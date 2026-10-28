#!/bin/bash
# Restart the B5 driver with 6 rayon threads (12 rules per chunk = exactly 2 rounds of 6) at the next chunk boundary. Safe: chunks are resumable.
cd /mnt/f/Code/turmite
n0=$(ls experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/*.done 2>/dev/null | wc -l)
while [ $(ls experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/*.done 2>/dev/null | wc -l) -le $n0 ]; do sleep 2; done
pkill -f run_1e11.sh; pkill -f 'release/sweep_lean - - 100000000000'
sleep 2
export RAYON_NUM_THREADS=6 CARGO_TARGET_DIR=$HOME/turmite-target-frontier
setsid nohup bash experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e11.sh > experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/run2.log 2>&1 < /dev/null &
echo restarted at $(date) with $(ls experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/*.done | wc -l) chunks done
