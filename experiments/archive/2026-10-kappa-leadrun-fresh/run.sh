#!/usr/bin/env bash
# usage (repo root, in WSL): bash experiments/archive/2026-10-kappa-leadrun-fresh/run.sh
set -euo pipefail
E=experiments/archive/2026-10-kappa-leadrun-fresh
[ -f $E/dumps/probe.done ] && { echo already done; exit 0; }
cargo build --release --bin probe
echo "git $(git rev-parse --short HEAD) $(date -Iseconds)" > $E/results/probe.log
./target/release/probe 27 8192 < $E/results/specs.txt > $E/dumps/probe.csv 2>> $E/results/probe.log
echo "finished $(date -Iseconds)" >> $E/results/probe.log
sha256sum target/release/probe >> $E/results/probe.log
touch $E/dumps/probe.done
