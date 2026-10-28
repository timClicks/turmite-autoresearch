#!/bin/bash
# B5 extension, checkpointed (2026-10-20): as run_1e11b.sh but sweep_lean saves mid-trajectory state every 5e9 steps, so a kill
# loses at most that much per rule and a rerun resumes. Checkpoints live in the (gitignored) experiment scratch/ckpt/.
# usage (WSL): RAYON_NUM_THREADS=6 CARGO_TARGET_DIR=~/turmite-target-b5-ckpt bash experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e11c.sh
cd /mnt/f/Code/turmite
E=experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11
export TURMITE_CKPT_EVERY=5000000000
for f in $E/results/h1e11/chunk_*.txt; do
  b=${f%.txt}
  [ -f $b.done ] && continue
  TURMITE_CKPT_DIR=$E/scratch/ckpt/$(basename $b) $CARGO_TARGET_DIR/release/sweep_lean - - 100000000000 32768 < $f > $b.csv 2> $b.log && touch $b.done
done
