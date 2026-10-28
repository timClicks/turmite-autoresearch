#!/bin/bash
cd /mnt/f/Code/turmite
grep -v -F -f <(awk -F, 'NR>1 && $2==-1{print $1}' experiments/archive/2026-10-d2-three-dimensions/results/d2_cube.csv | sort -u | sed 's/$/,/') <(sed 's/$/,/' experiments/archive/2026-10-probe-growth-census/results/cube_long_specs.txt) | sed 's/,$//' > experiments/archive/2026-10-d2-three-dimensions/results/d2c_specs.txt
~/turmite-target-frontier2/release/ext 28 34 64 1024 < experiments/archive/2026-10-d2-three-dimensions/results/d2c_specs.txt > experiments/archive/2026-10-d2-three-dimensions/results/d2c_cube.csv 2> experiments/archive/2026-10-d2-three-dimensions/results/d2c_cube.log && touch experiments/archive/2026-10-d2-three-dimensions/results/d2c.done
