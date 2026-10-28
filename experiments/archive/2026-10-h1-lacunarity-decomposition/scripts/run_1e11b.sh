#!/bin/bash
# B5 extension (2026-10-13): the remaining survivors of the 1e10 run (list positions 241..), same protocol as run_1e11.sh, chunks 20.. .
# usage (WSL): RAYON_NUM_THREADS=6 CARGO_TARGET_DIR=~/turmite-target-frontier bash experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e11b.sh
cd /mnt/f/Code/turmite
if [ ! -f experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_20.txt ]; then
  for f in $(ls experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_*.csv | sort); do awk -F, 'NR>1 && $3=="budget"{print $1}' $f; done | tail -n +241 | split -l 12 -d --numeric-suffixes=20 -a 2 --additional-suffix=.txt - experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_
fi
for f in experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_*.txt; do
  b=${f%.txt}
  [ -f $b.done ] && continue
  $CARGO_TARGET_DIR/release/sweep_lean - - 100000000000 32768 < $f > $b.csv 2> $b.log && touch $b.done
done
