#!/bin/bash
# D3: turn-noise crossover. usage (WSL): CARGO_TARGET_DIR=~/turmite-target-frontier2 bash experiments/archive/2026-10-d3-noise/scripts/run_d3.sh
cd /mnt/f/Code/turmite
cargo build --release --bin ext 2>&1 | tail -1
for r in RLR RLL RLRLRRRLLR; do for e in 0.15 0.2 0.25 0.3 0.4 0.5; do for s in 1 2 3 4 5 6; do echo "sq:$r:eps=$e:seed=$s"; done; done; done | RAYON_NUM_THREADS=1 $CARGO_TARGET_DIR/release/ext 12 26 32768 64 > experiments/archive/2026-10-d3-noise/results/d3_noise.csv && touch experiments/archive/2026-10-d3-noise/results/d3.done
