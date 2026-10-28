#!/bin/bash
# E4: knockout jobs with rare-colour accounting (RARE env). usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-e4-patch-vs-swap/scripts/run_e4.sh
cd /mnt/f/Code/turmite
K=$HOME/turmite-target-frontier3/release/examples/knock
declare -A RARE=( [RRRRRLLLLLL]=8,10,6 [RLLLLRRRRLR]=6,8,0 )
for rule in RRRRRLLLLLL RLLLLRRRRLR; do
  d=experiments/archive/2026-10-knockout-maps/knock/$rule
  [ -f $d/e4.done ] && continue
  RARE=${RARE[$rule]} $K experiments/archive/2026-10-knockout-maps/dumps/$rule.grid $rule 67108864 jobs $d/e4.jobs $d/e4.csv && touch $d/e4.done
done
touch experiments/archive/2026-10-e4-patch-vs-swap/results/e4.done
