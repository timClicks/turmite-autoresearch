#!/bin/bash
# B1/A2: 20 ants + 8 rotors to 2^34. usage (WSL): RAYON_NUM_THREADS=3 bash experiments/archive/2026-10-b1-exact-exponent/scripts/run_b1.sh
cd /mnt/f/Code/turmite
(cat experiments/archive/2026-10-b1-exact-exponent/results/b1_rules.txt; for s in $(seq 1 8); do echo rotor:$s; done) > experiments/archive/2026-10-b1-exact-exponent/results/b1_walkers.txt
split -l 7 -d -a 2 experiments/archive/2026-10-b1-exact-exponent/results/b1_walkers.txt experiments/archive/2026-10-b1-exact-exponent/results/b1_batch_
for f in experiments/archive/2026-10-b1-exact-exponent/results/b1_batch_??; do
  n=${f##*_}
  [ -f experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_$n.done ] && continue
  ~/turmite-target-frontier2/release/probe 34 32768 < $f > experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_$n.csv 2> experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_$n.log && touch experiments/archive/2026-10-b1-exact-exponent/results/b1_probe_$n.done
done
touch experiments/archive/2026-10-b1-exact-exponent/results/b1.done
