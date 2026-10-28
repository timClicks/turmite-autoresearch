#!/bin/bash
# usage (WSL, repo root): bash experiments/archive/2026-10-kappa-walker-reference/scripts/run_nrotor.sh
# Fresh target dir + checked build + binary sha256 (stale-build trap, AGENTS.md).
set -e
D=experiments/archive/2026-10-kappa-walker-reference
export CARGO_TARGET_DIR=$HOME/turmite-target-nrotor
cargo build --release --bin probe
git rev-parse --short HEAD > $D/results/commit_nrotor.txt
sha256sum $CARGO_TARGET_DIR/release/probe > $D/results/probe_bin_nrotor.sha256
$CARGO_TARGET_DIR/release/probe 27 8192 < $D/results/specs_nrotor.txt > $D/results/probe_nrotor.csv 2> $D/results/probe_nrotor.log
touch $D/results/run_nrotor.done
