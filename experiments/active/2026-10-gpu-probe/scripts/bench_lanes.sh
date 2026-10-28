#!/usr/bin/env bash
# P4: `gpu_probe 27 8192 --lanes L` on the 2400 kappa-leadrun-fresh specs for L in 1024, 1536, 2400, two repeats each,
# interleaved (2400,1024,1536,1536,1024,2400) so a slow drift in machine state does not alias onto L.
# usage (repo root, WSL): bash experiments/active/2026-10-gpu-probe/scripts/bench_lanes.sh
# Waits (before building) until no foreign `release/` binary or cargo process has been seen for 3 minutes, then builds and runs the phases one after
# the other, each after 30 s with no foreign process. Before and after each phase it logs other processes, nvidia-smi and load average (as bench.sh does), so a
# contaminated phase is visible in the log. Every CSV is cmp'd against the existing CPU dump.
set -uo pipefail
# Own target dir: on /mnt/f the source mtimes did not advance with later edits, so cargo judged the 2026-10-16 20:46 binary in
# ~/turmite-target fresh and never rebuilt it (that stale binary is what P2 timed). A fresh dir forces a build from the tree.
export CARGO_TARGET_DIR=$HOME/turmite-target-p4
source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh
EXPECT_SHA=${EXPECT_SHA:?set EXPECT_SHA to the sha256 of the verified build}
E=experiments/active/2026-10-gpu-probe
SPECS=experiments/archive/2026-10-kappa-leadrun-fresh/results/specs.txt
DUMP=experiments/archive/2026-10-kappa-leadrun-fresh/dumps/probe.csv   # CPU `probe 27 8192` output, same specs
T=$CARGO_TARGET_DIR/release
S=$E/scratch; mkdir -p $S
LOG=$E/results/bench_lanes.log
[ -f $E/results/bench_lanes.done ] && { echo already done; exit 0; }
foreign() { ps -eo pid,args | grep -E '/release/|cargo' | grep -v grep | grep -v bench_lanes.sh; }
wait_quiet() {  # $1 = seconds with no foreign process required
  local quiet=0
  while [ $quiet -lt $1 ]; do
    if [ -n "$(foreign)" ]; then quiet=0; else quiet=$((quiet + 10)); fi
    sleep 10
  done
}
wait_quiet 180
# Build after the wait and fail loudly: bench.sh's `cargo build | tail -1` hid whatever kept the P2 binary stale.
cargo build --release --features cuda --bin gpu_probe > $S/bench_lanes_build.txt 2>&1
[ $? -eq 0 ] || { echo "build failed, see $S/bench_lanes_build.txt" >&2; exit 1; }
[ "$(sha256sum $T/gpu_probe | cut -d' ' -f1)" = "$EXPECT_SHA" ] || { echo "gpu_probe is not the verified build" >&2; exit 1; }
echo "git $(git rev-parse --short HEAD) dirty(src,tests,Cargo.toml; filemode ignored)=$(git -c core.filemode=false diff --stat HEAD -- src tests Cargo.toml | wc -l) $(date -Iseconds)" > $LOG
echo "gpu_probe sha256 $(sha256sum $T/gpu_probe | cut -d' ' -f1) mtime $(stat -c %y $T/gpu_probe)" >> $LOG
echo "build: $(tail -1 $S/bench_lanes_build.txt)" >> $LOG
echo "specs: $SPECS ($(wc -l < $SPECS) lines, sha256 $(sha256sum < $SPECS | cut -d' ' -f1))" >> $LOG
echo "dump: $DUMP (sha256 $(sha256sum < $DUMP | cut -d' ' -f1))" >> $LOG
check() {  # $1 = label
  echo "-- $1 $(date -Iseconds) loadavg: $(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
  echo "   foreign procs: $(foreign | tr '\n' ';')" >> $LOG
  echo "   gpu: $(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader | tr '\n' ';')" >> $LOG
}
run() {  # $1 = lanes, $2 = repeat
  local ph=lanes_$1_r$2
  wait_quiet 30   # the other session may start a job between phases; log shows any that overlap
  check "before $ph"
  local t0=$(date +%s.%N)
  $T/gpu_probe 27 8192 --lanes $1 --stats $S/bench_$ph.json < $SPECS > $S/bench_$ph.csv 2> $S/bench_$ph.err
  local rc=$?
  local t1=$(date +%s.%N)
  echo "   $ph exit $rc wall $(echo "$t1 - $t0" | bc) s (whole process); cmp vs dump: $(cmp $S/bench_$ph.csv $DUMP && echo identical)" >> $LOG
  echo "   $ph stats: $(cat $S/bench_$ph.json)" >> $LOG
  cp $S/bench_$ph.json $E/results/bench_$ph.json
  check "after $ph"
}
run 2400 1
run 1024 1
run 1536 1
run 1536 2
run 1024 2
run 2400 2
echo "done $(date -Iseconds)" >> $LOG
touch $E/results/bench_lanes.done
