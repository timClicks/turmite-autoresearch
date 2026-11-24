#!/usr/bin/env bash
# Revision 5 excluded ant pilot (README "Revision 5 registration", registered at 78f7f9e).
# Do NOT run reserved_confirmation_specs.txt. Build first (fresh target dir; check exit status):
#   CARGO_TARGET_DIR=<fresh> cargo build --release --locked --example boundary_excursions --example boundary_excursions_depth_synth
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
EXP="$ROOT/experiments/active/2026-10-boundary-excursion-durations"
RES="$EXP/results"
BIN="${BIN:?set BIN to the fresh boundary_excursions binary}"
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-4}"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$HOME/.venvs/turmite}" UV_LINK_MODE="${UV_LINK_MODE:-copy}"
grep -q '^P0b/P0c: PASS' "$RES/rev5_p0.txt" || { echo "P0 not passed: stop before pilot" >&2; exit 2; }
PROV="$RES/provenance.txt"
{
  echo "# Revision 5 excluded ant pilot"
  echo "commit $(git -C "$ROOT" rev-parse HEAD)"
  echo "run_script_sha256 $(sha256sum "$0" | awk '{print $1}')"
  echo "p0_script_sha256 $(sha256sum "$EXP/scripts/p0_rev5.sh" | awk '{print $1}')"
  echo "analyse_script_sha256 $(sha256sum "$EXP/scripts/analyse_rev5.py" | awk '{print $1}')"
  echo "git_status_porcelain_begin (tracked + untracked, incl. ignored under the experiment folder)"
  git -C "$ROOT" status --porcelain
  git -C "$ROOT" status --porcelain --ignored --untracked-files=all -- "$EXP"
  echo "git_status_porcelain_end"
  echo "rustc $(rustc --version)"
  echo "bin_sha256 $(sha256sum "$BIN" | awk '{print $1}')"
  echo "specs_sha256 $(sha256sum "$RES/rev5_pilot_specs.txt" | awk '{print $1}')"
  echo "RAYON_NUM_THREADS $RAYON_NUM_THREADS"
  echo "command $BIN 24 8192 --check --hist results/rev5_pilot_hist.csv --fhist results/rev5_pilot_fhist.csv --dhist results/rev5_pilot_dhist.csv < results/rev5_pilot_specs.txt > results/rev5_pilot_windows.csv"
  echo "start $(date '+%Y-%m-%dT%H:%M:%S%z')"
} > "$PROV"
"$BIN" 24 8192 --check --hist "$RES/rev5_pilot_hist.csv" --fhist "$RES/rev5_pilot_fhist.csv" \
  --dhist "$RES/rev5_pilot_dhist.csv" \
  < "$RES/rev5_pilot_specs.txt" > "$RES/rev5_pilot_windows.csv" 2>"$RES/rev5_pilot_run.log"
{
  echo "end $(date '+%Y-%m-%dT%H:%M:%S%z')"
  for x in windows hist fhist dhist; do
    echo "rev5_pilot_${x}_sha256 $(sha256sum "$RES/rev5_pilot_$x.csv" | awk '{print $1}')"
  done
  echo "analysis_command uv run --frozen python scripts/analyse_rev5.py"
} >> "$PROV"
uv run --frozen python "$EXP/scripts/analyse_rev5.py"
echo "analysis_sha256 $(sha256sum "$RES/rev5_analysis.json" | awk '{print $1}')" >> "$PROV"
