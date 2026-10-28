#!/bin/bash
# P5 (registered in README): transplant mid-fill states. For each k in 1..3: the original rule from blank for t0 + 1e8 steps;
# (a) control: switch at t0 to a rule identical on counts 0..2k+2 (RLRR, RRLRRR, RRRLRRRR: the first two never fill from blank);
# (b) switch at t0 to the rule with only T(2k+2) flipped to L (RLRRLL, RRLRRRL, RRRLRRRRL), reporting the first read > 2k+2.
# 8192 board, last-window 2^20 steps, fingerprints (visit-count hash vhash). Run from the repository root.
set -euo pipefail
E=experiments/archive/2026-10-square-ring-fillers
cargo build --release --locked --example square_ring_fillers_footprint
FP=target/release/examples/square_ring_fillers_footprint
{ echo "# commit $(git rev-parse HEAD) dirty=$(git status --porcelain --untracked-files=no | wc -l) $(date -Iseconds)"; sha256sum $FP; } > $E/results/p5_run.log
run() { # t0 original control flipped k
  local t0=$1 o=$2 c=$3 f=$4 k=$5
  local steps=$((t0 + 100000000))
  printf "%s#%d\n%s>%s@%d#%d\n%s>%s@%d#%d\n" $o $((2*k+2)) $o $c $t0 $((2*k+2)) $o $f $t0 $((2*k+2)) \
    | RAYON_NUM_THREADS=3 $FP $steps 8192 1048576 --fingerprint
}
{
run 1000000 RLRRRL RLRR RLRRLL 1
run 2000000 RRLRRRR RRLRRR RRLRRRL 2 | tail -n +2
run 3000000 RRRLRRRRR RRRLRRRR RRRLRRRRL 3 | tail -n +2
} > $E/results/p5_transplant.csv
echo "done $(date -Iseconds)" >> $E/results/p5_run.log
