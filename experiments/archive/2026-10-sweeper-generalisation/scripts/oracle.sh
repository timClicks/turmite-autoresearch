#!/bin/bash
# Oracle for sweeper_generalisation_frontlog: (1) its final fingerprint equals fast::run's (via the parent's resim example) at
# 1e7 and 1e8 steps for each rule; (2) an independent Python ant reproduces its event logs for 2e5 steps. Run from repo root in WSL.
set -e
E=experiments/archive/2026-10-sweeper-generalisation
export CARGO_TARGET_DIR=$HOME/turmite-target-sg
rm -rf "$CARGO_TARGET_DIR"
cargo build --release --example sweeper_generalisation_frontlog --example rlrlll_macro_transition_resim
echo "# commit $(git rev-parse --short HEAD) dirty=$(git status --porcelain | wc -l)"
sha256sum $CARGO_TARGET_DIR/release/examples/sweeper_generalisation_frontlog $CARGO_TARGET_DIR/release/examples/rlrlll_macro_transition_resim
FL=$CARGO_TARGET_DIR/release/examples/sweeper_generalisation_frontlog
RS=$CARGO_TARGET_DIR/release/examples/rlrlll_macro_transition_resim
mkdir -p $E/scratch
for R in RLLLLRRL RLLLLRLRRL RLLLRLRLLL RLRLLL RRLLLLRRL; do
  for T in 10000000 100000000; do
    a=$($FL $R $T 16384 $E/scratch/oracle_$R 1000000 2>/dev/null | sed 's/.*hash=\([0-9a-f]*\) nonzero=\([0-9]*\)/\1 \2/')
    b=$($RS $R $T 16384 | grep '^fast' | sed 's/.*hash=\([0-9a-f]*\) nonzero=\([0-9]*\).*/\1 \2/')
    [ "$a" == "$b" ] && echo "FINGERPRINT $R $T identical ($a)" || { echo "FINGERPRINT $R $T MISMATCH frontlog=[$a] fast=[$b]"; exit 1; }
  done
  $FL $R 200000 1024 $E/scratch/oraclelog_$R 1000 >/dev/null 2>&1
  python3 $E/scripts/oracle_log.py $R 200000 $E/scratch/oraclelog_$R
done
