#!/bin/bash
cd /mnt/f/Code/turmite
S=~/turmite-target-frontier2/release/examples/shape
for s in $(seq 211 216); do echo rotor:$s; done > experiments/archive/2026-10-a4-boundary-width/results/a4c_rotor_specs.txt
for r in RLR RLRLRRRLLR RLLLRLLRRLR RLRLLRRLL RLRLRRRRLR RLLRLLRLRRRL; do for s in 211 212; do echo $r@$s; done; done > experiments/archive/2026-10-a4-boundary-width/results/a4c_ants_specs.txt
$S 34 16384 < experiments/archive/2026-10-a4-boundary-width/results/a4c_rotor_specs.txt > experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_rotor.csv 2> experiments/archive/2026-10-a4-boundary-width/results/a4c_rotor.log && touch experiments/archive/2026-10-a4-boundary-width/results/a4c_rotor.done
$S 34 16384 < experiments/archive/2026-10-a4-boundary-width/results/a4c_ants_specs.txt > experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_ants.csv 2> experiments/archive/2026-10-a4-boundary-width/results/a4c_ants.log && touch experiments/archive/2026-10-a4-boundary-width/results/a4c_ants.done
touch experiments/archive/2026-10-a4-boundary-width/results/a4c.done
