#!/bin/bash
# Stage 1 runs: three target rules on a 65536 board, plus positive (RLRLLL, to just after its exit at 12,974,495,927) and
# negative (RRLLLLRRL) controls. Fresh build; binary hash logged. Run from repo root in WSL after oracle.sh passed.
set -e
E=experiments/archive/2026-10-sweeper-generalisation
export CARGO_TARGET_DIR=$HOME/turmite-target-sg1
rm -rf "$CARGO_TARGET_DIR"
cargo build --release --example sweeper_generalisation_frontlog
FL=$CARGO_TARGET_DIR/release/examples/sweeper_generalisation_frontlog
{ echo "commit $(git rev-parse HEAD) dirty=$(git status --porcelain examples src | wc -l)"; sha256sum $FL; } > $E/results/stage1_binary.txt
run() { # name rule steps grid
  mkdir -p $E/scratch/$1
  /usr/bin/time -v $FL $2 $3 $4 $E/scratch/$1 1000000 > $E/scratch/$1/fingerprint.txt 2> $E/scratch/$1/time.log || true
}
run ctl_pos_RLRLLL RLRLLL 13000000000 32768 &
run ctl_neg_RRLLLLRRL RRLLLLRRL 3000000000 32768 &
run RLLLLRRL RLLLLRRL 40000000000 65536 &
run RLLLRLRLLL RLLLRLRLLL 40000000000 65536 &
run RLLLLRLRRL RLLLLRLRRL 60000000000 65536 &
wait
echo done > $E/results/stage1.done
