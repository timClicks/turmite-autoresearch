#!/bin/bash
cd /mnt/f/Code/turmite
K=$HOME/turmite-target-frontier4/release/examples/knock
for rule in RRRRRLLLLLL RLLLLRRRRLR; do for R in 4 22; do d=experiments/archive/2026-10-knockout-maps/knock/$rule; mkdir -p /tmp/e2b_$rule
  [ -f $d/coarse_r$R.done ] && continue
  NEAR_R=$R $K experiments/archive/2026-10-knockout-maps/dumps/$rule.grid $rule 67108864 base /tmp/e2b_$rule > $d/base_r$R.txt
  NEAR_R=$R $K experiments/archive/2026-10-knockout-maps/dumps/$rule.grid $rule 67108864 jobs $d/coarse.jobs $d/coarse_r$R.csv && touch $d/coarse_r$R.done
done; done
touch experiments/archive/2026-10-e2-sensitive-disc/results/e2b.done
