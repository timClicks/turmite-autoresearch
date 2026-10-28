#!/bin/bash
# C2: biased-arrow rotor vs unbiased control. usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-c2-arrow-bias/scripts/run_c2.sh
cd /mnt/f/Code/turmite
for s in $(seq 1 12); do echo rotor:$s; for b in 0.25 0.5 0.75 0.9; do echo brotor:$s:$b; done; done > experiments/archive/2026-10-c2-arrow-bias/results/c2_walkers.txt
~/turmite-target-frontier2/release/probe 28 8192 < experiments/archive/2026-10-c2-arrow-bias/results/c2_walkers.txt > experiments/archive/2026-10-c2-arrow-bias/results/c2_probe.csv 2> experiments/archive/2026-10-c2-arrow-bias/results/c2_probe.log && touch experiments/archive/2026-10-c2-arrow-bias/results/c2.done
