#!/bin/bash
# E6: formation of the hot windows. usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-e6-hot-window-age/scripts/run_e6.sh
cd /mnt/f/Code/turmite
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-e6-hot-window-age/scripts/e6_jobs.py
D=$HOME/turmite-target-frontier4/release/examples/dump; K=$HOME/turmite-target-frontier4/release/examples/knock
mkdir -p dumps_e6
for R in RRRRRLLLLLL RLLLLRRRRLR; do
  for A in 18 20 22 24; do
    if [ $A = 24 ]; then G=experiments/archive/2026-10-knockout-maps/dumps/$R.grid; else
      G=experiments/archive/2026-10-e6-hot-window-age/dumps_e6/${R}_k$A.grid
      [ -f $G ] || { $D $R $A dumps_e6 && mv experiments/archive/2026-10-e6-hot-window-age/dumps_e6/$R.grid $G && rm -f experiments/archive/2026-10-e6-hot-window-age/dumps_e6/$R.traj; }
    fi
    [ -f experiments/archive/2026-10-knockout-maps/knock/$R/e6_k$A.done ] && continue
    $K $G $R 67108864 base /tmp/e6_$R > experiments/archive/2026-10-knockout-maps/knock/$R/e6_base_k$A.txt 2>/dev/null || { mkdir -p /tmp/e6_$R; $K $G $R 67108864 base /tmp/e6_$R > experiments/archive/2026-10-knockout-maps/knock/$R/e6_base_k$A.txt; }
    $K $G $R 67108864 jobs experiments/archive/2026-10-knockout-maps/knock/$R/e6.jobs experiments/archive/2026-10-knockout-maps/knock/$R/e6_k$A.csv && touch experiments/archive/2026-10-knockout-maps/knock/$R/e6_k$A.done
  done
done
touch experiments/archive/2026-10-e6-hot-window-age/results/e6.done
