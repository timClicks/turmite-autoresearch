#!/bin/bash
# E1: knockout map at other ages and with the field rotated 90 degrees (RRRRRLLLLLL). usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-e1-one-sided-hot-region/scripts/run_e1.sh
cd /mnt/f/Code/turmite
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
D=$HOME/turmite-target-frontier4/release/examples/dump
R=RRRRRLLLLLL
mkdir -p dumps_e1 knock_e1
# rotated field: relative coordinates (x,y) -> (-y,x), i.e. 90 degrees clockwise on screen; roll by one to keep home at (C,C)
uv run --with numpy python -c "
import numpy as np
S=4096
g=np.fromfile('experiments/archive/2026-10-knockout-maps/dumps/$R.grid',dtype=np.uint8).reshape(S,S)
np.roll(np.rot90(g,-1),1,axis=1).tofile('experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/${R}_rot90.grid')"
[ -f experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/${R}_k22.grid ] || { $D $R 22 dumps_e1 && mv experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/$R.grid experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/${R}_k22.grid && rm -f experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/$R.traj; }
[ -f experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/${R}_k25.grid ] || { $D $R 25 dumps_e1 && mv experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/$R.grid experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/${R}_k25.grid && rm -f experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/$R.traj; }
for spec in "rot90 experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/${R}_rot90.grid" "k22 experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/${R}_k22.grid" "k25 experiments/archive/2026-10-e1-one-sided-hot-region/dumps_e1/${R}_k25.grid" "k26 experiments/archive/2026-10-tether-rules/dumps_f/$R.grid"; do
  set -- $spec
  [ -f experiments/archive/2026-10-e1-one-sided-hot-region/knock_e1/${R}_$1/done ] || if [ "$1" = rot90 ]; then export START_H=1; else unset START_H; fi; uv run experiments/archive/2026-10-e1-one-sided-hot-region/scripts/e1_map.py ${R}_$1 $2 $R
done
touch experiments/archive/2026-10-e1-one-sided-hot-region/results/e1.done
