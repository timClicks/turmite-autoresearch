#!/bin/bash
# usage (WSL, repo root): bash experiments/archive/2026-10-kappa-walker-reference/scripts/run.sh
set -e
D=experiments/archive/2026-10-kappa-walker-reference
cargo build --release --bin probe
git rev-parse --short HEAD > $D/results/commit.txt
./target/release/probe 23 16384 < $D/results/specs_mem.txt > $D/results/probe_mem.csv 2> $D/results/probe_mem.log
./target/release/probe 27 8192 < $D/results/specs_rotor.txt > $D/results/probe_rotor.csv 2> $D/results/probe_rotor.log
touch $D/results/run.done
