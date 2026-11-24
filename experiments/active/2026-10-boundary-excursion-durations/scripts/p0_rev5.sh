#!/usr/bin/env bash
# Revision 5 P0 instrument gates (README "Revision 5 registration", Gates). Writes results/rev5_p0.txt.
# Needs BIN and SYN built with --release --locked into a fresh CARGO_TARGET_DIR (see run_rev5.sh header).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
EXP="$ROOT/experiments/active/2026-10-boundary-excursion-durations"
RES="$EXP/results"
SCR="$EXP/scratch/rev5_p0"
BIN="${BIN:?set BIN to the fresh boundary_excursions binary}"
SYN="${SYN:?set SYN to the fresh boundary_excursions_depth_synth binary}"
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-4}"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-$HOME/.venvs/turmite}" UV_LINK_MODE="${UV_LINK_MODE:-copy}"
mkdir -p "$SCR"
OUT="$RES/rev5_p0.txt"
: > "$OUT"
say() { echo "$*" | tee -a "$OUT"; }
say "Rev5 P0 gates; git $(git -C "$ROOT" rev-parse HEAD); script sha256 $(sha256sum "$0" | awk '{print $1}')"
say "bin sha256 $(sha256sum "$BIN" | awk '{print $1}'); synth sha256 $(sha256sum "$SYN" | awk '{print $1}')"

# P0b: Rev4 calibration reproduces byte-identically.
"$BIN" 24 8192 --check --hist "$SCR/hist.csv" --fhist "$SCR/fhist.csv" --dhist "$SCR/dhist.csv" \
  < "$RES/rev4_calib_specs.txt" > "$SCR/windows.csv" 2>"$SCR/run.log"
for x in windows hist fhist dhist; do
  cmp "$SCR/$x.csv" "$RES/rev4_calib_$x.csv"
  say "P0b rev4_calib_$x.csv byte-identical"
done
"$SYN" 2026102981 20 > "$SCR/rev4_synth_dhist.csv"
uv run --frozen python "$EXP/scripts/synth_rev4.py" "$SCR/rev4_synth_dhist.csv" > /dev/null
git -C "$ROOT" diff --exit-code -- "$RES/rev4_synth.txt" "$RES/rev4_synth.json"
say "P0b rev4_synth.{txt,json} rescored byte-identical (G1 line: $(grep '^G1' "$RES/rev4_synth.txt"))"
uv run --frozen python "$EXP/scripts/analyse_rev3.py" > /dev/null
uv run --frozen python "$EXP/scripts/analyse_rev4.py" > /dev/null
git -C "$ROOT" diff --exit-code -- "$RES/rev3_analysis.txt" "$RES/rev4_analysis.txt"
say "P0b rev3_analysis.txt and rev4_analysis.txt reproduce byte-identically"

# P0c: ant smoke on non-cohort rules, then mutants must panic. Amendment A1 (b1a0713): pilot board 8192, not 512
# (RL@7 escapes the 512 board and --check asserts equal window counts with the probe).
S='RL@7\nLLRR@7\n'
printf "$S" | "$BIN" 14 8192 --check --hist /dev/null --fhist /dev/null --dhist /dev/null > /dev/null 2>"$SCR/smoke.err"
say "P0c ant smoke RL@7, LLRR@7 (14, 8192) --check --dhist: exit 0"
for m in "--mutant" "--fine-mutant" "--depth-mutant --dhist /dev/null"; do
  set +e
  # shellcheck disable=SC2086
  printf "$S" | "$BIN" 14 8192 --check $m > /dev/null 2>"$SCR/err"
  ec=$?
  set -e
  if [[ $ec -eq 0 ]]; then say "P0c mutant $m FAILED to panic"; exit 1; fi
  say "P0c mutant $m panicked (exit $ec): $(grep -m1 -A1 panicked "$SCR/err" | tail -1 | cut -c1-110)"
done
say "P0b/P0c: PASS"
