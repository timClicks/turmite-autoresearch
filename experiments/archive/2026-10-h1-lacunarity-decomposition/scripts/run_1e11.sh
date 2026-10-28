#!/bin/bash
# B5 (frontier 2026-10-13): first 240 rules (in the fixed-seed shuffled chunk order of run_1e10.sh)
# that were still stop=budget at 1e10, rerun from scratch to 1e11 steps with the lean ant, grid 32768.
# Chunked and resumable: experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_NN.{txt,csv,done}.
# usage (WSL): RAYON_NUM_THREADS=5 CARGO_TARGET_DIR=~/turmite-target-frontier bash experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/run_1e11.sh
cd /mnt/f/Code/turmite
cargo build --release --bin sweep_lean 2>/dev/null
if [ ! -f experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_00.txt ]; then
  for f in $(ls experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_*.csv | sort); do awk -F, 'NR>1 && $3=="budget"{print $1}' $f; done | head -240 | split -l 12 -d -a 2 --additional-suffix=.txt - experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_
fi
for f in experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11/chunk_*.txt; do
  b=${f%.txt}
  [ -f $b.done ] && continue
  $CARGO_TARGET_DIR/release/sweep_lean - - 100000000000 32768 < $f > $b.csv 2> $b.log && touch $b.done
done
