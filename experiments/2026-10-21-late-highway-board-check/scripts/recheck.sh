#!/usr/bin/env bash
# Re-run each late highway alone on a 65536 board (budget per rule from recheck_specs.txt), two at a time (4.3 GB each).
set -euo pipefail
E=experiments/2026-10-21-late-highway-board-check
cargo build --release --bin sweep_lean
B=target/release/sweep_lean
mkdir -p $E/results/recheck
[ -f $E/results/recheck/recheck.log ] || echo "commit $(git rev-parse HEAD)" > $E/results/recheck/recheck.log
echo "binary_sha256 $(sha256sum $B | cut -d' ' -f1) start $(date -Is)" >> $E/results/recheck/recheck.log
run() { [ -f $E/results/recheck/$1.csv ] || { echo $1 | RAYON_NUM_THREADS=1 $B - - $2 65536 > $E/results/recheck/$1.tmp 2>/dev/null && mv $E/results/recheck/$1.tmp $E/results/recheck/$1.csv; }; }
export -f run; export E B
xargs -P 2 -L 1 bash -c 'run "$0" "$1"' < $E/results/recheck_specs.txt
echo "end $(date -Is)" >> $E/results/recheck/recheck.log
