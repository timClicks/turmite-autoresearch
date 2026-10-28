#!/usr/bin/env bash
# W5 bulk fingerprint. usage (repo root, WSL): bash experiments/archive/2026-10-kappa-rule-space/scripts/run_w5.sh
set -euo pipefail
E=experiments/archive/2026-10-kappa-rule-space
export CARGO_TARGET_DIR=$HOME/turmite-target
[ -f $E/dumps/w5_bulk.done ] && { echo already done; exit 0; }
cargo build --release --example kappa_rs_bulk
BIN=$CARGO_TARGET_DIR/release/examples/kappa_rs_bulk
echo "git $(git rev-parse --short HEAD) start $(date -Iseconds)" > $E/results/w5_run.log
echo "binary sha256 $(sha256sum $BIN | cut -d' ' -f1)" >> $E/results/w5_run.log
echo "cmd: kappa_rs_bulk 20000 262144 20 2048 < results/w5_specs.txt > dumps/w5_bulk.csv" >> $E/results/w5_run.log
$BIN 20000 262144 20 2048 < $E/results/w5_specs.txt > $E/dumps/w5_bulk.csv.part 2>> $E/results/w5_run.log
mv $E/dumps/w5_bulk.csv.part $E/dumps/w5_bulk.csv
echo "finished $(date -Iseconds)" >> $E/results/w5_run.log
touch $E/dumps/w5_bulk.done
