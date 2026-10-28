#!/usr/bin/env bash
# Confirmation run (README Registration). From repo root in WSL. Resumable: finished specs are skipped via .done markers.
set -e
export CARGO_TARGET_DIR=~/turmite-target RAYON_NUM_THREADS=3
E=experiments/archive/2026-10-kappa-prefix-exposure
cargo build --release --example kappa_prefix_exposure_sampler
for side in dev val; do
  $CARGO_TARGET_DIR/release/examples/kappa_prefix_exposure_sampler $E/dumps/confirm_$side 536870912 4096 64 32768-34816,131072-139264 \
    < $E/results/specs_confirm_$side.txt 2> $E/results/confirm_run_$side.log
done
echo ALLDONE > $E/results/confirm_run.finished
