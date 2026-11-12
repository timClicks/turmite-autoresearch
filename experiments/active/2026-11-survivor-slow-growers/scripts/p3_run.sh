#!/usr/bin/env bash
# P3: re-run the 8 sampled slow survivors from blank to 2e11 steps on a 32768 board (the census board), tiled grid, 4 at a time.
set -euo pipefail
E=experiments/active/2026-11-survivor-slow-growers
cargo build --release --locked --bin sweep_lean
B=${CARGO_TARGET_DIR:-target}/release/sweep_lean
mkdir -p $E/results/p3
echo "commit $(git rev-parse HEAD) binary_sha256 $(sha256sum $B | cut -d' ' -f1) start $(date -Is)" >> $E/results/p3/run.log
run() {
  r=$1; [ -f $E/results/p3/$r.csv ] && return 0
  echo $r | TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=unlimited TURMITE_GRID_STATS=$E/results/p3/$r.json \
    RAYON_NUM_THREADS=1 $B - - 200000000000 32768 > $E/results/p3/$r.tmp 2> $E/results/p3/$r.err \
    && mv $E/results/p3/$r.tmp $E/results/p3/$r.csv && echo "$r done $(date -Is)" >> $E/results/p3/run.log \
    || { rc=$?; echo "$r FAILED rc=$rc $(date -Is)" >> $E/results/p3/run.log; }
}
export -f run; export E B
xargs -P 4 -n 1 bash -c 'run "$0"' < $E/results/p3_sample.txt
echo "end $(date -Is)" >> $E/results/p3/run.log
