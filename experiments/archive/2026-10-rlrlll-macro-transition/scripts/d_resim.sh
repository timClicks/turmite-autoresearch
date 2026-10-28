#!/bin/bash
# Task D. Fresh target dir; build exit status checked; binary hash logged. Run from repo root in WSL.
set -e
E=experiments/archive/2026-10-rlrlll-macro-transition
export CARGO_TARGET_DIR=$HOME/turmite-target-resim
rm -rf "$CARGO_TARGET_DIR"
cargo build --release --example rlrlll_macro_transition_resim
B=$CARGO_TARGET_DIR/release/examples/rlrlll_macro_transition_resim
{ echo "# commit $(git rev-parse --short HEAD) (+ uncommitted example if dirty); sha256 $(sha256sum $B)"
  echo "# $B RLRLLL 12676237591 32768"
  $B RLRLLL 12676237591 32768; } > $E/results/d_resim.txt
cat $E/results/d_resim.txt
