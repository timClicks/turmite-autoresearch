#!/usr/bin/env bash
# Production run for the frozen config (config.frozen.json). Resumable: finished specs carry a parameter-stamped .done marker.
# Repo root, WSL:  nohup experiments/archive/2026-10-fixed-area-cycles/scripts/run_production.sh > experiments/archive/2026-10-fixed-area-cycles/results/production.log 2>&1 &
set -euo pipefail
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-$HOME/turmite-target}
E=experiments/archive/2026-10-fixed-area-cycles
echo "commit $(git rev-parse HEAD) config $(sha256sum $E/config.frozen.json | cut -d' ' -f1)"
cargo build --release --example fixed_area_cycles_sampler 2>/dev/null
BIN=$CARGO_TARGET_DIR/release/examples/fixed_area_cycles_sampler
specs=$(mktemp)
while read -r r; do for s in $(seq 1001 1064); do echo "$r@$s"; done; done < $E/results/cohort_rules.txt > $specs
wc -l < $specs
date
env RAYON_NUM_THREADS=5 $BIN $E/dumps/prod16 536870912 8192 32768-34816,131072-139264 < $specs 2> $E/dumps/prod16.stderr
echo "prod16 done: $(ls $E/dumps/prod16/*.done | wc -l) specs"; date
env RAYON_NUM_THREADS=5 $BIN $E/dumps/prod8 536870912 8192 32768-36864,131072-147456 < $specs 2> $E/dumps/prod8.stderr
echo "prod8 done: $(ls $E/dumps/prod8/*.done | wc -l) specs"; date
