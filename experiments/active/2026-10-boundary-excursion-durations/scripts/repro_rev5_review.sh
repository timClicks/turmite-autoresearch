#!/usr/bin/env bash
# Rev5 review fix S7 check: after the `--check` escape-convention fix in examples/boundary_excursions.rs, the Rev5 pilot and the
# Rev3/Rev4 calibration outputs still reproduce byte for byte, and the escaping smoke (RL@7 on a 512 board) now exits 0.
# Writes only under scratch/rev5_review/ and results/rev5_review_repro.txt (a log). Needs BIN (fresh --release --locked build).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
EXP="$ROOT/experiments/active/2026-10-boundary-excursion-durations"
RES="$EXP/results"; SCR="$EXP/scratch/rev5_review"
BIN="${BIN:?set BIN to the fresh boundary_excursions binary}"
export RAYON_NUM_THREADS="${RAYON_NUM_THREADS:-2}"
mkdir -p "$SCR"; OUT="$RES/rev5_review_repro.txt"; : > "$OUT"
say() { echo "$*" | tee -a "$OUT"; }
say "Rev5 review reproduction; git $(git -C "$ROOT" rev-parse HEAD); $(rustc --version); $(cargo --version); RAYON_NUM_THREADS=$RAYON_NUM_THREADS"
say "bin sha256 $(sha256sum "$BIN" | awk '{print $1}'); started $(date '+%Y-%m-%dT%H:%M:%S%z')"
printf 'RL@7\nLLRR@7\n' | "$BIN" 14 512 --check --hist /dev/null --fhist /dev/null --dhist /dev/null > "$SCR/esc.csv" 2>"$SCR/esc.err"
say "S7: RL@7,LLRR@7 (14, board 512) --check exits 0; RL@7 escaped rows: $(grep -c '^RL@7.*,true$' "$SCR/esc.csv")"
"$BIN" 24 8192 --check --hist "$SCR/p_hist.csv" --fhist "$SCR/p_fhist.csv" --dhist "$SCR/p_dhist.csv" \
  < "$RES/rev5_pilot_specs.txt" > "$SCR/p_windows.csv" 2>"$SCR/p.log"
for x in windows hist fhist dhist; do cmp "$SCR/p_$x.csv" "$RES/rev5_pilot_$x.csv"; say "pilot rev5_pilot_$x.csv byte-identical"; done
"$BIN" 24 8192 --check --hist "$SCR/r3_hist.csv" --fhist "$SCR/r3_fhist.csv" < "$RES/rev3_calib_specs.txt" > "$SCR/r3_windows.csv" 2>"$SCR/r3.log"
for x in windows hist fhist; do cmp "$SCR/r3_$x.csv" "$RES/rev3_calib_$x.csv"; say "rev3_calib_$x.csv byte-identical"; done
"$BIN" 24 8192 --check --hist "$SCR/r4_hist.csv" --fhist "$SCR/r4_fhist.csv" --dhist "$SCR/r4_dhist.csv" \
  < "$RES/rev4_calib_specs.txt" > "$SCR/r4_windows.csv" 2>"$SCR/r4.log"
for x in windows hist fhist dhist; do cmp "$SCR/r4_$x.csv" "$RES/rev4_calib_$x.csv"; say "rev4_calib_$x.csv byte-identical"; done
say "REPRO: PASS; finished $(date '+%Y-%m-%dT%H:%M:%S%z')"
