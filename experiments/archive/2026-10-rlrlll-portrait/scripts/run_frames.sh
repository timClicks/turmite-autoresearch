#!/bin/bash
# Fresh target dir; build exit status checked; binary hash logged. Run from the repo root.
set -e
E=experiments/archive/2026-10-rlrlll-portrait
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-$HOME/turmite-target-portrait}
cargo build --release --example rlrlll_portrait_frames
B=$CARGO_TARGET_DIR/release/examples/rlrlll_portrait_frames
mkdir -p $E/scratch/frames
{ echo "# commit $(git rev-parse HEAD)$(git diff --quiet HEAD -- examples/rlrlll_portrait_frames.rs || echo ' (example dirty)')"
  echo "# sha256 $(sha256sum $B | cut -d' ' -f1)  $(basename $B)"
  echo "# $B RLRLLL $E/scripts/times.txt $E/scratch/frames 32768 16 256"
  start=$(date +%s); $B RLRLLL $E/scripts/times.txt $E/scratch/frames 32768 16 256 2>&1
  echo "# wall $(( $(date +%s) - start )) s"; } > $E/results/run_frames.log
cat $E/results/run_frames.log
