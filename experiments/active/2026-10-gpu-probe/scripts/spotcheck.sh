#!/usr/bin/env bash
# Full-scale spot check: gpu_probe vs probe at `27 8192` on every 100th spec of the kappa-leadrun-fresh batch.
# usage (repo root, WSL): bash experiments/active/2026-10-gpu-probe/scripts/spotcheck.sh
# CPU_THREADS (default 1, niced) keeps the CPU side from disturbing other jobs; it does not change the output.
set -euo pipefail
source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh
E=experiments/active/2026-10-gpu-probe
SRC=experiments/archive/2026-10-kappa-leadrun-fresh/results/specs.txt
S=$E/scratch; mkdir -p $S
awk 'NR % 100 == 1' $SRC > $E/results/spotcheck_specs.txt
# Never pipe the build through `tail`: it hid a stale binary (source mtimes on /mnt/f did not advance, so cargo rebuilt nothing).
BUILD_OUT=$(mktemp)
cargo build --release --features cuda --bin probe --bin gpu_probe > $BUILD_OUT 2>&1 || { cat $BUILD_OUT >&2; echo "build failed" >&2; exit 1; }
tail -1 $BUILD_OUT
# A binary older than the newest source file is stale: use a fresh CARGO_TARGET_DIR or touch the sources.
for b in probe gpu_probe; do
  [ -z "$(find src Cargo.toml -newer $CARGO_TARGET_DIR/release/$b -type f | head -1)" ] || { echo "$b older than sources: stale build" >&2; exit 1; }
done
T=$CARGO_TARGET_DIR/release
t0=$(date +%s.%N)
RAYON_NUM_THREADS=${CPU_THREADS:-1} nice $T/probe 27 8192 < $E/results/spotcheck_specs.txt > $S/spot_cpu.csv 2> $S/spot_cpu.err
t1=$(date +%s.%N)
$T/gpu_probe 27 8192 --lanes 32 --stats $S/spot_gpu.json < $E/results/spotcheck_specs.txt > $S/spot_gpu.csv 2> $S/spot_gpu.err
t2=$(date +%s.%N)
{
  echo "git $(git rev-parse --short HEAD) $(date -Iseconds)"
  echo "specs: every 100th line of $SRC (24 specs), command: probe 27 8192 / gpu_probe 27 8192 --lanes 32"
  echo "rows: $(($(wc -l < $S/spot_cpu.csv) - 1))"
  echo "cpu_sha256 $(sha256sum < $S/spot_cpu.csv | cut -d' ' -f1)  (${CPU_THREADS:-1} thread, $(echo "$t1 - $t0" | bc) s)"
  echo "gpu_sha256 $(sha256sum < $S/spot_gpu.csv | cut -d' ' -f1)  ($(echo "$t2 - $t1" | bc) s incl. setup)"
  if cmp $S/spot_cpu.csv $S/spot_gpu.csv; then echo "RESULT byte-identical"; else echo "RESULT DIFFERENT"; fi
  echo "escaped runs: $(awk -F, 'NR>1 && $9=="true"{print $1}' $S/spot_cpu.csv | sort -u | wc -l) of 24"
  echo "gpu_stats $(cat $S/spot_gpu.json)"
} | tee $E/results/spotcheck.txt
