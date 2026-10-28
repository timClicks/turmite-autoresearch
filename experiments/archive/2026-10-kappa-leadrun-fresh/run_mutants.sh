#!/usr/bin/env bash
# usage (repo root, in WSL): bash experiments/archive/2026-10-kappa-leadrun-fresh/run_mutants.sh
set -euo pipefail
E=experiments/archive/2026-10-kappa-leadrun-fresh
[ -f $E/dumps/mutants.done ] && { echo already done; exit 0; }
cargo build --release --bin probe
echo "git $(git rev-parse --short HEAD) $(date -Iseconds)" > $E/results/mutants_probe.log
./target/release/probe 27 8192 < $E/results/mutant_specs.txt > $E/dumps/mutants.csv 2>> $E/results/mutants_probe.log
echo "finished $(date -Iseconds)" >> $E/results/mutants_probe.log
sha256sum target/release/probe >> $E/results/mutants_probe.log
touch $E/dumps/mutants.done
