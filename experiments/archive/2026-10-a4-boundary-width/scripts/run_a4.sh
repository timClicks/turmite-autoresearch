#!/bin/bash
# A4: boundary-width series to 2^32. usage (WSL): CARGO_TARGET_DIR=~/turmite-target-frontier2 RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-a4-boundary-width/scripts/run_a4.sh  (waits for experiments/archive/2026-10-b1-exact-exponent/results/b1.done)
cd /mnt/f/Code/turmite
while [ ! -f experiments/archive/2026-10-b1-exact-exponent/results/b1.done ]; do sleep 60; done
cargo build --release --example shape 2>&1 | tail -1
for r in RLR RLRLRRRLLR RLLLRLLRRLR RLRLLRRLL RLRLRRRRLR RLLRLLRLRRRL; do for s in 201 202 203 204; do echo $r@$s; done; done > experiments/archive/2026-10-a4-boundary-width/results/a4_ants_specs.txt
for s in $(seq 201 208); do echo rotor:$s; done > experiments/archive/2026-10-a4-boundary-width/results/a4_rotor_specs.txt
$CARGO_TARGET_DIR/release/examples/shape 32 16384 < experiments/archive/2026-10-a4-boundary-width/results/a4_rotor_specs.txt > experiments/archive/2026-10-a4-boundary-width/results/a4_shape_rotor.csv 2> experiments/archive/2026-10-a4-boundary-width/results/a4_rotor.log && touch experiments/archive/2026-10-a4-boundary-width/results/a4_rotor.done
$CARGO_TARGET_DIR/release/examples/shape 32 16384 < experiments/archive/2026-10-a4-boundary-width/results/a4_ants_specs.txt > experiments/archive/2026-10-a4-boundary-width/results/a4_shape_ants.csv 2> experiments/archive/2026-10-a4-boundary-width/results/a4_ants.log && touch experiments/archive/2026-10-a4-boundary-width/results/a4_ants.done
touch experiments/archive/2026-10-a4-boundary-width/results/a4.done
