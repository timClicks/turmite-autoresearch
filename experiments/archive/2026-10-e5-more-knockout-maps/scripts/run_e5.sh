#!/bin/bash
# E5: knockout maps on 6 more tethered rules (experiments/archive/2026-10-e5-more-knockout-maps/results/e5_rules.txt, 2^24 dumps) + RRRRRLLLLLL with the tile origin shifted by (2,2). usage (WSL): RAYON_NUM_THREADS=1 bash experiments/archive/2026-10-e5-more-knockout-maps/scripts/run_e5.sh
cd /mnt/f/Code/turmite
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
D=$HOME/turmite-target-frontier4/release/examples/dump
mkdir -p dumps_e5 knock_e5
for R in $(cat experiments/archive/2026-10-e5-more-knockout-maps/results/e5_rules.txt); do
  [ -f experiments/archive/2026-10-e5-more-knockout-maps/dumps_e5/$R.grid ] || $D $R 24 dumps_e5
  [ -f experiments/archive/2026-10-e5-more-knockout-maps/knock_e5/${R}_off0/done ] || OFFX=0 OFFY=0 uv run experiments/archive/2026-10-e5-more-knockout-maps/scripts/e5_map.py ${R}_off0 experiments/archive/2026-10-e5-more-knockout-maps/dumps_e5/$R.grid $R
  [ -f experiments/archive/2026-10-e5-more-knockout-maps/knock_e5/${R}_off2/done ] || OFFX=2 OFFY=2 uv run experiments/archive/2026-10-e5-more-knockout-maps/scripts/e5_map.py ${R}_off2 experiments/archive/2026-10-e5-more-knockout-maps/dumps_e5/$R.grid $R
done
R=RRRRRLLLLLL
[ -f experiments/archive/2026-10-e5-more-knockout-maps/knock_e5/${R}_off2/done ] || OFFX=2 OFFY=2 uv run experiments/archive/2026-10-e5-more-knockout-maps/scripts/e5_map.py ${R}_off2 experiments/archive/2026-10-knockout-maps/dumps/$R.grid $R
touch experiments/archive/2026-10-e5-more-knockout-maps/results/e5.done
