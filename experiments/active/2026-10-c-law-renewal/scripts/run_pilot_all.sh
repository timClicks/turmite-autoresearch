#!/usr/bin/env bash
set -euo pipefail
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/turmite" UV_LINK_MODE=copy
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$root"
exp=experiments/active/2026-10-c-law-renewal
mkdir -p "$exp/results/pilot_v1"
printf '%s\n' "$$" > "$exp/results/pilot_v1/session.pid"
trap 'printf "%s\n" "$?" > "$exp/results/pilot_v1/session.exit"' EXIT
uv run --frozen "$exp/scripts/calibrate.py"
uv run --frozen "$exp/scripts/run_pilot.py" --stage build
uv run --frozen "$exp/scripts/run_pilot.py" --stage controls
uv run --frozen "$exp/scripts/run_pilot.py" --stage pilot
uv run --frozen "$exp/scripts/pilot_report.py"
