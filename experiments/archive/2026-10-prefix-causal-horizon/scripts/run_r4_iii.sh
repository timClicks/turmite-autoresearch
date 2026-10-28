#!/usr/bin/env bash
# True first position difference for the five R4 pairs the lemma does not settle (class iii), 32768 board, cap 1.4e10 steps.
set -euo pipefail
E=experiments/archive/2026-10-prefix-causal-horizon
cargo build --release --locked --example prefix_pair_diff
B=${CARGO_TARGET_DIR:-target}/release/examples/prefix_pair_diff
echo "commit $(git rev-parse HEAD) binary_sha256 $(sha256sum $B | cut -d' ' -f1) start $(date -Is)" > $E/results/r4_iii_provenance.txt
mkdir -p $E/scratch/iii
run() { $B $1 $2 14000000000 32768 > $E/scratch/iii/$1_$2.csv; }
export -f run; export E B
xargs -P 3 -L 1 bash -c 'run "$0" "$1"' < $E/results/r4_iii_pairs.txt
{ echo "rule_a,rule_b,result,steps"; cat $E/scratch/iii/*.csv; } > $E/results/r4_iii_pair_diff.csv
echo "end $(date -Is)" >> $E/results/r4_iii_provenance.txt
