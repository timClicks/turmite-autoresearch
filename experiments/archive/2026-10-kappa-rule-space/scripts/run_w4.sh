#!/usr/bin/env bash
# W4 colour-resolved tally. usage (repo root, WSL): bash experiments/archive/2026-10-kappa-rule-space/scripts/run_w4.sh
set -euo pipefail
E=experiments/archive/2026-10-kappa-rule-space
export CARGO_TARGET_DIR=$HOME/turmite-target
[ -f $E/dumps/w4_colourflux.done ] && { echo already done; exit 0; }
cargo build --release --example kappa_rs_colourflux
echo "git $(git rev-parse --short HEAD) $(date -Iseconds)" > $E/results/w4_run.log
$CARGO_TARGET_DIR/release/examples/kappa_rs_colourflux 18 27 8192 < $E/results/w4_specs.txt > $E/dumps/w4_colourflux.csv 2>> $E/results/w4_run.log
echo "finished $(date -Iseconds)" >> $E/results/w4_run.log
touch $E/dumps/w4_colourflux.done
