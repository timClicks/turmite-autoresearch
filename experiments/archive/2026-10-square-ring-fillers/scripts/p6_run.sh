#!/bin/bash
# P6 runs (registered in README): every rule of results/p6_specs.txt from a blank 16384 board for 2^27 steps; read histogram of
# the last 2^24 steps. Output results/p6_footprint.csv (input order). Run from the repository root.
set -euo pipefail
E=experiments/archive/2026-10-square-ring-fillers
cargo build --release --locked --example square_ring_fillers_footprint
FP=target/release/examples/square_ring_fillers_footprint
{ echo "# commit $(git rev-parse HEAD) dirty=$(git status --porcelain --untracked-files=no | wc -l) $(date -Iseconds)"; sha256sum $FP $E/results/p6_specs.txt; } > $E/results/p6_run.log
RAYON_NUM_THREADS=3 $FP 134217728 16384 16777216 < $E/results/p6_specs.txt > $E/results/p6_footprint.csv
echo "done $(date -Iseconds)" >> $E/results/p6_run.log
