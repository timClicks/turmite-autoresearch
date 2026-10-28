#!/usr/bin/env bash
# P2 re-measure on a verified HEAD build: `probe 27 8192` (CPU, 6 rayon threads) vs `gpu_probe 27 8192 --lanes 2400`
# on the 2400 kappa-leadrun-fresh specs. Replaces the stale-binary timing in bench.log (kept, not edited).
# usage (repo root, WSL): bash experiments/active/2026-10-gpu-probe/scripts/bench_p2.sh
# Phases run sequentially: gpu1, cpu, gpu2. Foreign processes are logged before/after each phase.
set -uo pipefail
export CARGO_TARGET_DIR=$HOME/turmite-target-p2   # fresh dir forces a build from the tree
source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh
E=experiments/active/2026-10-gpu-probe
SPECS=experiments/archive/2026-10-kappa-leadrun-fresh/results/specs.txt
DUMP=experiments/archive/2026-10-kappa-leadrun-fresh/dumps/probe.csv
T=$CARGO_TARGET_DIR/release
S=$E/scratch; mkdir -p $S
LOG=$E/results/bench_p2.log
[ -f $E/results/bench_p2.done ] && { echo already done; exit 0; }
cargo build --release --features cuda --bin probe --bin gpu_probe > $S/bench_p2_build.txt 2>&1 || { echo "build failed, see $S/bench_p2_build.txt" >&2; exit 1; }
for b in probe gpu_probe; do
  [ -z "$(find src Cargo.toml -newer $T/$b -type f | head -1)" ] || { echo "$b older than sources: stale" >&2; exit 1; }
done
echo "git $(git rev-parse --short HEAD) dirty(src,tests,Cargo.toml; filemode ignored)=$(git -c core.filemode=false diff --stat HEAD -- src tests Cargo.toml | wc -l) $(date -Iseconds)" > $LOG
echo "build: $(tail -1 $S/bench_p2_build.txt)" >> $LOG
for b in probe gpu_probe; do echo "$b sha256 $(sha256sum $T/$b | cut -d' ' -f1) mtime $(stat -c %y $T/$b)" >> $LOG; done
echo "specs: $SPECS ($(wc -l < $SPECS) lines, sha256 $(sha256sum < $SPECS | cut -d' ' -f1))" >> $LOG
echo "dump: $DUMP (sha256 $(sha256sum < $DUMP | cut -d' ' -f1))" >> $LOG
foreign() { ps -eo pid,args | grep -E '/release/|cargo' | grep -v grep | grep -v bench_p2.sh; }
check() {
  echo "-- $1 $(date -Iseconds) loadavg: $(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
  echo "   foreign procs: $(foreign | tr '\n' ';')" >> $LOG
  echo "   gpu: $(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader | tr '\n' ';')" >> $LOG
}
run() {  # $1 = phase, rest = command (stdin = specs)
  local ph=$1; shift
  check "before $ph"
  local t0=$(date +%s.%N)
  "$@" < $SPECS > $S/bench_p2_$ph.csv 2> $S/bench_p2_$ph.err
  local rc=$?
  local t1=$(date +%s.%N)
  echo "   $ph exit $rc wall $(echo "$t1 - $t0" | bc) s (whole process); cmp vs dump: $(cmp $S/bench_p2_$ph.csv $DUMP && echo identical)" >> $LOG
  check "after $ph"
}
run gpu1 $T/gpu_probe 27 8192 --lanes 2400 --stats $E/results/bench_p2_gpu1.json
run cpu  $T/probe 27 8192
run gpu2 $T/gpu_probe 27 8192 --lanes 2400 --stats $E/results/bench_p2_gpu2.json
echo "cmp cpu vs gpu1: $(cmp $S/bench_p2_cpu.csv $S/bench_p2_gpu1.csv && echo identical)" >> $LOG
echo "done $(date -Iseconds)" >> $LOG
touch $E/results/bench_p2.done
