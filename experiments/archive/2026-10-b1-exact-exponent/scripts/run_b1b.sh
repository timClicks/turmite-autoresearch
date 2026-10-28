#!/bin/bash
cd /mnt/f/Code/turmite
for r in RLLLRLLRRLR RLLRLLRLRRRL RLR RLRLLRRLL RLRLRRRLLR RLRLRRRRLR RLL RLRLRRL RRRLRLLL RLRLLRRLRL RRRLRLRRRRL RLLLRRLRRRLR RLRR RLRLRRRLR RLRLLRRLRRRR; do for s in 301 302 303; do echo $r@$s; done; done > experiments/archive/2026-10-b1-exact-exponent/results/b1b_walkers.txt
split -l 9 -d -a 2 experiments/archive/2026-10-b1-exact-exponent/results/b1b_walkers.txt experiments/archive/2026-10-b1-exact-exponent/results/b1b_batch_
for f in experiments/archive/2026-10-b1-exact-exponent/results/b1b_batch_??; do n=${f##*_}; [ -f experiments/archive/2026-10-b1-exact-exponent/results/b1b_probe_$n.done ] && continue
  ~/turmite-target-frontier2/release/probe 34 32768 < $f > experiments/archive/2026-10-b1-exact-exponent/results/b1b_probe_$n.csv 2> experiments/archive/2026-10-b1-exact-exponent/results/b1b_probe_$n.log && touch experiments/archive/2026-10-b1-exact-exponent/results/b1b_probe_$n.done; done
touch experiments/archive/2026-10-b1-exact-exponent/results/b1b.done
