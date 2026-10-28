#!/bin/bash
# A6 mechanism test. usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-a6-corruption-mechanism/scripts/run_a6.sh
cd /mnt/f/Code/turmite
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-a6-corruption-mechanism/scripts/a6_jobs.py
K=$HOME/turmite-target-frontier4/release/examples/knock
declare -A RARE=( [RRRRRLLLLLL]=8,10,6 [RLLLLRRRRLR]=6,8,0 )
for rule in RRRRRLLLLLL RLLLLRRRRLR; do
  d=experiments/archive/2026-10-knockout-maps/knock/$rule
  STRAT_OCC=$d/occ.u32 RARE=${RARE[$rule]} $K experiments/archive/2026-10-knockout-maps/dumps/$rule.grid $rule 67108864 jobs $d/a6.jobs $d/a6.csv 2> $d/a6.log && touch $d/a6.done
done
touch experiments/archive/2026-10-a6-corruption-mechanism/results/a6.done
