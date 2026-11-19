#!/usr/bin/env bash
# Re-run each (1e8,1e9]-census late highway alone (recheck_specs.txt: RULE BUDGET) on new boards, one rule per process.
#   primary   : 65536 board, tiled backend (sparse tiles; CSV byte-identical to dense, tests/tiled.rs) -> results/recheck_65536/
#   secondary : 32768 board, dense backend (default)                                                 -> results/recheck_32768/
# The box has ~2.5 GB free RAM, too little for a dense 65536 board (4.3 GB), hence tiled for the primary run.
# Resumable: finished rules (RULE.csv present) are skipped. Run from the repository root.
set -euo pipefail
E=experiments/active/2026-11-late-highway-1e8-board-check
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-${TMPDIR:-/tmp}/turmite-lh1e8-target}   # separate target dir outside the checkout (stale-build trap, AGENTS.md)
cargo build --release --locked --bin sweep_lean
B=$CARGO_TARGET_DIR/release/sweep_lean
mkdir -p $E/results/recheck_65536 $E/results/recheck_32768
for d in recheck_65536 recheck_32768; do
  L=$E/results/$d/recheck.log
  [ -f $L ] || echo "commit $(git rev-parse HEAD)" > $L
  echo "binary_sha256 $(sha256sum $B | cut -d' ' -f1) start $(date -Is)" >> $L
done
run65() { [ -f $E/results/recheck_65536/$1.csv ] || { echo $1 | RAYON_NUM_THREADS=1 TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=unlimited \
  TURMITE_GRID_STATS=$E/results/recheck_65536/$1.json $B - - $2 65536 > $E/results/recheck_65536/$1.tmp 2>/dev/null \
  && mv $E/results/recheck_65536/$1.tmp $E/results/recheck_65536/$1.csv; }; }
run32() { [ -f $E/results/recheck_32768/$1.csv ] || { echo $1 | RAYON_NUM_THREADS=1 $B - - $2 32768 > $E/results/recheck_32768/$1.tmp 2>/dev/null \
  && mv $E/results/recheck_32768/$1.tmp $E/results/recheck_32768/$1.csv; }; }
export -f run65 run32; export E B
xargs -P 4 -L 1 bash -c 'run65 "$0" "$1"' < $E/results/recheck_specs.txt
echo "end $(date -Is)" >> $E/results/recheck_65536/recheck.log
xargs -P 1 -L 1 bash -c 'run32 "$0" "$1"' < $E/results/recheck_specs.txt   # 1.07 GB per dense board: one at a time
echo "end $(date -Is)" >> $E/results/recheck_32768/recheck.log
