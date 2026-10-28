#!/usr/bin/env bash
# Timing of `probe 27 8192` (CPU, 6 rayon threads) vs `gpu_probe 27 8192` on the 2400 kappa-leadrun-fresh specs.
# usage (repo root, WSL): bash experiments/active/2026-10-gpu-probe/scripts/bench.sh
# Phases run one after the other, never overlapping: gpu1, cpu, gpu2. Before and after each phase the script
# logs what else is running (processes named release/*, nvidia-smi, load average), so contamination is visible.
set -uo pipefail
source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh
E=experiments/active/2026-10-gpu-probe
SPECS=experiments/archive/2026-10-kappa-leadrun-fresh/results/specs.txt
DUMP=experiments/archive/2026-10-kappa-leadrun-fresh/dumps/probe.csv   # earlier CPU `probe 27 8192` output, same specs
T=$CARGO_TARGET_DIR/release
S=$E/scratch; mkdir -p $S
LOG=$E/results/bench.log
# Never pipe the build through `tail`: it hid a stale binary (source mtimes on /mnt/f did not advance, so cargo rebuilt nothing).
BUILD_OUT=$(mktemp)
cargo build --release --features cuda --bin probe --bin gpu_probe > $BUILD_OUT 2>&1 || { cat $BUILD_OUT >&2; echo "build failed" >&2; exit 1; }
tail -1 $BUILD_OUT
# A binary older than the newest source file is stale: use a fresh CARGO_TARGET_DIR or touch the sources.
for b in probe gpu_probe; do
  [ -z "$(find src Cargo.toml -newer $CARGO_TARGET_DIR/release/$b -type f | head -1)" ] || { echo "$b older than sources: stale build" >&2; exit 1; }
done
echo "git $(git rev-parse --short HEAD) dirty=$(git status --porcelain src tests Cargo.toml | wc -l) $(date -Iseconds)" > $LOG
echo "probe sha256 $(sha256sum $T/probe | cut -d' ' -f1)" >> $LOG
echo "gpu_probe sha256 $(sha256sum $T/gpu_probe | cut -d' ' -f1)" >> $LOG
echo "specs: $SPECS ($(wc -l < $SPECS) lines, sha256 $(sha256sum < $SPECS | cut -d' ' -f1))" >> $LOG
check() {  # $1 = label
  echo "-- $1 $(date -Iseconds) loadavg: $(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
  echo "   release/ procs: $(ps -eo pid,pcpu,args | grep -E 'release/' | grep -v grep | grep -v bench.sh | tr '\n' ';')" >> $LOG
  echo "   gpu: $(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader | tr '\n' ';')" >> $LOG
}
run() {  # $1 = phase, rest = command (stdin = specs)
  local ph=$1; shift
  check "before $ph"
  local t0=$(date +%s.%N)
  "$@" < $SPECS > $S/bench_$ph.csv 2> $S/bench_$ph.err
  local t1=$(date +%s.%N)
  echo "   $ph wall $(echo "$t1 - $t0" | bc) s (whole process); cmp vs dump: $(cmp $S/bench_$ph.csv $DUMP && echo identical)" >> $LOG
  check "after $ph"
}
run gpu1 $T/gpu_probe 27 8192 --lanes 2400 --stats $S/bench_gpu1.json
run cpu  $T/probe 27 8192
run gpu2 $T/gpu_probe 27 8192 --lanes 2400 --stats $S/bench_gpu2.json
cp $S/bench_gpu1.json $E/results/bench_gpu1.json; cp $S/bench_gpu2.json $E/results/bench_gpu2.json
echo "cmp cpu vs gpu1: $(cmp $S/bench_cpu.csv $S/bench_gpu1.csv && echo identical)" >> $LOG
echo "done $(date -Iseconds)" >> $LOG
touch $E/results/bench.done
