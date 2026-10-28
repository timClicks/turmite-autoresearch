#!/bin/bash
cd /mnt/f/Code/turmite
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-e3-route-collinearity/scripts/e3b_jobs.py
K=$HOME/turmite-target-frontier4/release/examples/knock
for rule in RRRRRLLLLLL RLLLLRRRRLR; do d=experiments/archive/2026-10-knockout-maps/knock/$rule
  STRAT_ROUTE=$d/e3/route.u32 STRAT_RET=$d/e3/ret.u32 $K experiments/archive/2026-10-knockout-maps/dumps/$rule.grid $rule 67108864 jobs $d/e3b.jobs $d/e3b.csv 2> $d/e3b.log && touch $d/e3b.done
done
touch experiments/archive/2026-10-e3-route-collinearity/results/e3b.done
