#!/usr/bin/env bash
# First-read times of the 25 late-highway rules that share an onset with another rule, on a 32768 board, cap 1.4e10 steps.
# One process per rule (the horizon run is serial); the merged CSV is results/r4_first_reads.csv.
set -euo pipefail
E=experiments/archive/2026-10-prefix-causal-horizon
cargo build --release --locked --example prefix_horizon
B=${CARGO_TARGET_DIR:-target}/release/examples/prefix_horizon
mkdir -p $E/scratch/r4
echo "commit $(git rev-parse HEAD) binary_sha256 $(sha256sum $B | cut -d' ' -f1) start $(date -Is)" > $E/results/r4_provenance.txt
run() { echo "$1" | $B 14000000000 32768 | tail -n +2 > $E/scratch/r4/$1.csv; }
export -f run; export E B
xargs -P 3 -n 1 bash -c 'run "$0"' < $E/results/r4_rules.txt
{ echo "rule,n,steps,escaped,wrapped_read,first_reads"; cat $E/scratch/r4/*.csv; } > $E/results/r4_first_reads.csv
echo "end $(date -Is)" >> $E/results/r4_provenance.txt
