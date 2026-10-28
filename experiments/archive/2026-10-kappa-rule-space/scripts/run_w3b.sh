#!/usr/bin/env bash
# W3b fresh-rule probe runs. usage (repo root, in WSL): bash experiments/archive/2026-10-kappa-rule-space/scripts/run_w3b.sh
set -euo pipefail
E=experiments/archive/2026-10-kappa-rule-space
[ -f $E/dumps/w3b_probe.done ] && { echo already done; exit 0; }
cargo build --release --bin probe
echo "git $(git rev-parse --short HEAD) $(date -Iseconds)" > $E/results/w3b_probe.log
./target/release/probe 27 8192 < $E/results/w3b_specs.txt > $E/dumps/w3b_probe.csv 2>> $E/results/w3b_probe.log
echo "finished $(date -Iseconds)" >> $E/results/w3b_probe.log
touch $E/dumps/w3b_probe.done
