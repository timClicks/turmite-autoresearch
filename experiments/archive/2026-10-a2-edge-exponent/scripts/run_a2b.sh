#!/bin/bash
cd /mnt/f/Code/turmite
for s in $(seq 11 16); do echo rotor:$s; done > experiments/archive/2026-10-a2-edge-exponent/results/a2b_walkers.txt
~/turmite-target-frontier2/release/probe 36 32768 < experiments/archive/2026-10-a2-edge-exponent/results/a2b_walkers.txt > experiments/archive/2026-10-a2-edge-exponent/results/a2b_probe.csv 2> experiments/archive/2026-10-a2-edge-exponent/results/a2b_probe.log && touch experiments/archive/2026-10-a2-edge-exponent/results/a2b.done
