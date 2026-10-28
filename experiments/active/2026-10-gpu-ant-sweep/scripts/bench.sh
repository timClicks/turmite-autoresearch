#!/usr/bin/env bash
# Benchmark gpu_sweep against sweep_lean (6 rayon threads) on one census slice and check the CSVs match.
# usage: bench.sh MIN MAX MAX_STEPS TAG "LANES..."
# Run from the repo root inside WSL:  bash experiments/active/2026-10-gpu-ant-sweep/scripts/bench.sh 2 12 1000000 L2-12-1e6 "1024 4096 8192 16384"
set -euo pipefail
cd "$(dirname "$0")/../../../.."
source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh
MIN=$1 MAX=$2 STEPS=$3 TAG=$4 LANES=$5
OUT=experiments/active/2026-10-gpu-ant-sweep/results
SCR=$HOME/gpu-scratch; mkdir -p $SCR
cargo build --release --features cuda --bin gpu_sweep --bin sweep_lean 2>/dev/null
T=$CARGO_TARGET_DIR/release
COMMIT=$(git rev-parse --short HEAD)
LOG=$OUT/bench_$TAG.log
echo "# bench $TAG: lengths $MIN..=$MAX, max_steps $STEPS, grid 8192, commit $COMMIT (+uncommitted gpu work), $(date -Is)" > $LOG
echo "# host: $(nproc) logical cores; $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)" >> $LOG
if [ -n "${LEAN_WALL:-}" ] && [ -f $SCR/lean_$TAG.csv ]; then LEAN=$LEAN_WALL; echo "# lean time reused from an earlier run of this same script (LEAN_WALL)" >> $LOG
else
s=$(date +%s.%N)
$T/sweep_lean $MIN $MAX $STEPS > $SCR/lean_$TAG.csv 2>/dev/null
e=$(date +%s.%N)
LEAN=$(echo "$e - $s" | bc -l)
fi
echo "sweep_lean wall_s=$LEAN rules=$(($(wc -l < $SCR/lean_$TAG.csv)-1))" >> $LOG
for L in $LANES; do
  s=$(date +%s.%N)
  $T/gpu_sweep $MIN $MAX $STEPS --lanes $L --stats $SCR/gpu_${TAG}_$L.json > $SCR/gpu_${TAG}_$L.csv 2> $SCR/gpu_${TAG}_$L.err
  e=$(date +%s.%N)
  W=$(echo "$e - $s" | bc -l)
  if cmp -s $SCR/lean_$TAG.csv $SCR/gpu_${TAG}_$L.csv; then SAME=identical; else SAME=DIFFERENT; fi
  echo "gpu lanes=$L wall_s=$W speedup_vs_lean=$(echo "$LEAN / $W" | bc -l | cut -c1-6) csv=$SAME | $(grep 'steps/s' $SCR/gpu_${TAG}_$L.err)" >> $LOG
done
cat $LOG
