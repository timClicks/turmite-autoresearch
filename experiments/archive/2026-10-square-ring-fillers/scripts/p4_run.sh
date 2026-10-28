#!/bin/bash
# P4 step 2: exit steps of the three fillers on 8192, 16384 and 32768 boards with sweep_lean (census binary), after the
# predictions in results/p4_predictions.txt were committed. Run from the repository root.
set -euo pipefail
E=experiments/archive/2026-10-square-ring-fillers
cargo build --release --locked --bin sweep_lean
B=target/release/sweep_lean
{ echo "# commit $(git rev-parse HEAD) dirty=$(git status --porcelain --untracked-files=no | wc -l) $(date -Iseconds)"; sha256sum $B; } > $E/results/p4_run.log
for G in 8192 16384 32768; do
  printf "RLRRRRL\nRRLRR\nRRRLRRRRR\n" | RAYON_NUM_THREADS=3 $B - - 9000000000 $G > $E/results/p4_board_$G.csv
  echo "G=$G done $(date -Iseconds)" >> $E/results/p4_run.log
done
