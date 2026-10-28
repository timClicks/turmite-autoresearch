#!/bin/bash
cd /mnt/f/Code/turmite
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
uv run experiments/archive/2026-10-d1-turmite-sqrt-cluster/scripts/d1b_specs.py
RAYON_NUM_THREADS=1 ~/turmite-target-frontier2/release/ext 12 20 2048 64 < experiments/archive/2026-10-d1-turmite-sqrt-cluster/results/d1b_specs.txt > experiments/archive/2026-10-d1-turmite-sqrt-cluster/results/d1b_screen.csv 2> experiments/archive/2026-10-d1-turmite-sqrt-cluster/results/d1b.log && touch experiments/archive/2026-10-d1-turmite-sqrt-cluster/results/d1b.done
