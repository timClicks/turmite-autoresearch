#!/usr/bin/env bash
# Control walkers under the fixed-area estimator: rotor and random walk, seeds 801..928, band width
# 1/32, 1/16, 1/8, 1/4 of the entry area at the same entry areas (paired trajectories). Repo root, WSL.
set -euo pipefail
export CARGO_TARGET_DIR=${CARGO_TARGET_DIR:-$HOME/turmite-target}
E=experiments/archive/2026-10-fixed-area-cycles
cargo build --release --example fixed_area_cycles_sampler 2>/dev/null
BIN=$CARGO_TARGET_DIR/release/examples/fixed_area_cycles_sampler
specs=$(mktemp)
for s in $(seq 801 928); do echo "rotor:$s"; echo "rw:$s"; done > $specs
for w in 32 16 8 4; do
  b="32768-$((32768 + 32768 / w)),131072-$((131072 + 131072 / w))"
  env RAYON_NUM_THREADS=4 $BIN $E/dumps/controls_w$w 536870912 8192 $b < $specs 2> $E/dumps/controls_w$w.stderr
  echo "w=1/$w bands=$b done: $(ls $E/dumps/controls_w$w/*.done | wc -l) specs"
done
