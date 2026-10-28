#!/bin/bash
cd /mnt/f/Code/turmite
for s in $(seq 401 464); do echo RRLLLLLLR@$s; done > experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7c_walkers.txt
~/turmite-target-frontier2/release/probe 32 16384 < experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7c_walkers.txt > experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7c_probe.csv 2> experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7c_probe.log && touch experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7c.done
