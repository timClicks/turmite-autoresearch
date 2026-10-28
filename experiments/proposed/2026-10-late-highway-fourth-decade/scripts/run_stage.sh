#!/usr/bin/env bash
# Run rules FIRST..LAST (1-based, inclusive) of sample_order.txt to 1e12 steps, 4 at a time, tiled grid, 65536 board.
# Resumable: finished rules are skipped; interrupted ones resume from a checkpoint (results are identical either way).
set -euo pipefail
E=experiments/proposed/2026-10-late-highway-fourth-decade
FIRST=${1:?first}; LAST=${2:?last}
cargo build --release --locked --bin sweep_lean
B=${CARGO_TARGET_DIR:-target}/release/sweep_lean
mkdir -p $E/results/runs $E/scratch/ckpt
echo "commit $(git rev-parse HEAD) binary_sha256 $(sha256sum $B | cut -d' ' -f1) stage $FIRST-$LAST start $(date -Is)" >> $E/results/runs/stage.log
run() {
  r=$1; [ -f $E/results/runs/$r.csv ] && return 0
  echo $r | TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=unlimited TURMITE_INACTIVE=packed \
    TURMITE_CKPT_DIR=$E/scratch/ckpt TURMITE_CKPT_EVERY=5000000000 TURMITE_GRID_STATS=$E/results/runs/$r.json \
    RAYON_NUM_THREADS=1 $B - - 1000000000000 65536 > $E/results/runs/$r.tmp 2>/dev/null && mv $E/results/runs/$r.tmp $E/results/runs/$r.csv
}
export -f run; export E B
sed -n "${FIRST},${LAST}p" $E/results/sample_order.txt | xargs -P 4 -n 1 bash -c 'run "$0"'
echo "stage $FIRST-$LAST end $(date -Is)" >> $E/results/runs/stage.log
