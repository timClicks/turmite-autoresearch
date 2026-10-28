#!/usr/bin/env bash
# W6 pilot probe runs. usage (repo root, in WSL): bash experiments/archive/2026-10-kappa-rule-space/scripts/run_w6.sh
set -euo pipefail
E=experiments/archive/2026-10-kappa-rule-space
[ -f $E/dumps/w6_probe.done ] && { echo already done; exit 0; }
cargo build --release --bin probe
echo "git $(git rev-parse --short HEAD) $(date -Iseconds)" > $E/results/w6_probe.log
./target/release/probe 26 8192 < $E/results/w6_specs.txt > $E/dumps/w6_probe.csv 2>> $E/results/w6_probe.log
echo "finished $(date -Iseconds)" >> $E/results/w6_probe.log
touch $E/dumps/w6_probe.done
