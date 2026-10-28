#!/bin/bash
# P2/P3 runs (registered in README): the 25 census board fillers from a blank 8192 board for 2^27 steps.
# (1) front log (sweeper_generalisation_frontlog, oracle-tested in 2026-10-sweeper-generalisation) -> scratch/frontlog/RULE/
# (2) footprint over the last 2^26 steps -> results/p3_footprint.csv
# Run from the repository root.
set -euo pipefail
E=experiments/archive/2026-10-square-ring-fillers
cargo build --release --locked --example sweeper_generalisation_frontlog --example square_ring_fillers_footprint
FL=target/release/examples/sweeper_generalisation_frontlog
FP=target/release/examples/square_ring_fillers_footprint
mkdir -p $E/scratch/frontlog
{
echo "# commit $(git rev-parse HEAD) dirty=$(git status --porcelain --untracked-files=no | wc -l) $(date -Iseconds)"
sha256sum $FL $FP
} > $E/results/p23_run.log
xargs -P 4 -I{} sh -c "$FL {} 134217728 8192 $E/scratch/frontlog/{} 1000000 > $E/scratch/frontlog/{}.fingerprint 2> $E/scratch/frontlog/{}.stderr" < $E/results/board_fillers.txt
RAYON_NUM_THREADS=4 $FP 134217728 8192 67108864 < $E/results/board_fillers.txt > $E/results/p3_footprint.csv
echo "done $(date -Iseconds)" >> $E/results/p23_run.log
