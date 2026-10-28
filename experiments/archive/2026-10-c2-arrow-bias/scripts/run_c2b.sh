#!/bin/bash
# C2b: small biases on a larger grid. usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-c2-arrow-bias/scripts/run_c2b.sh
cd /mnt/f/Code/turmite
for s in $(seq 1 8); do echo rotor:$s; for b in 0.02 0.05 0.1 0.15; do echo brotor:$s:$b; done; done > experiments/archive/2026-10-c2-arrow-bias/results/c2b_walkers.txt
~/turmite-target-frontier2/release/probe 28 32768 < experiments/archive/2026-10-c2-arrow-bias/results/c2b_walkers.txt > experiments/archive/2026-10-c2-arrow-bias/results/c2b_probe.csv 2> experiments/archive/2026-10-c2-arrow-bias/results/c2b_probe.log && touch experiments/archive/2026-10-c2-arrow-bias/results/c2b.done
