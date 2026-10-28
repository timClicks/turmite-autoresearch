#!/usr/bin/env bash
# Part 3: footprint of each class representative on every uniform background, at 1e8 and 1e9 steps (2048 board), 3 at a time.
set -euo pipefail
E=experiments/archive/2026-10-rotation-boxes
cargo build --release --locked --example rotation_backgrounds
B=${CARGO_TARGET_DIR:-target}/release/examples/rotation_backgrounds
mkdir -p $E/scratch/bg
echo "commit $(git rev-parse HEAD) binary_sha256 $(sha256sum $B | cut -d' ' -f1) start $(date -Is)" > $E/results/uniform_bg_provenance.txt
run() { echo "$2" | $B $1 2048 | tail -n +2 > $E/scratch/bg/$1_$2.csv; }
export -f run; export E B
for T in 100000000 1000000000; do
  awk '{print "'"$T"' " $2}' $E/results/uniform_bg_classes.txt | xargs -P 3 -L 1 bash -c 'run "$0" "$1"'
  { echo "rule,k,steps,shape"; cat $E/scratch/bg/${T}_*.csv; } > $E/results/uniform_bg_shapes_$T.csv
done
echo "end $(date -Is)" >> $E/results/uniform_bg_provenance.txt
