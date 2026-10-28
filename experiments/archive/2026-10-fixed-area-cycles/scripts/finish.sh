#!/usr/bin/env bash
# Wait for the already-running production, then audit, analyse and execute notebook.
set -euo pipefail
export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy
E=experiments/archive/2026-10-fixed-area-cycles
deadline=$((SECONDS + 7200))
while [[ $(find "$E/dumps/prod8" -name '*.done' | wc -l) -ne 2816 ]] || [[ ! -f "$E/results/determinism.json" ]]; do
    if (( SECONDS > deadline )); then echo 'Timed out waiting for production/determinism'; exit 1; fi
    sleep 5
done
uv run "$E/scripts/audit.py" > "$E/results/audit.log" 2>&1
uv run "$E/scripts/analyse.py" > "$E/results/analysis.log" 2>&1
uv run "$E/scripts/figures.py" > "$E/results/figures.log" 2>&1
uv run "$E/scripts/results_notebook.py"
uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace "$E/notebook.ipynb" > "$E/results/notebook.log" 2>&1
echo 'Audit, frozen analysis and notebook execution complete.'
