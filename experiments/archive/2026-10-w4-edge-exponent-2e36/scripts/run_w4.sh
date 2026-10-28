#!/bin/bash
cd /mnt/f/Code/turmite
~/turmite-target-frontier2/release/probe 36 32768 < experiments/archive/2026-10-w4-edge-exponent-2e36/results/w4_specs.txt > experiments/archive/2026-10-w4-edge-exponent-2e36/results/w4_probe.csv 2> experiments/archive/2026-10-w4-edge-exponent-2e36/results/w4_probe.log && touch experiments/archive/2026-10-w4-edge-exponent-2e36/results/w4.done
