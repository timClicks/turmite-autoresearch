#!/usr/bin/env bash
# Feasibility pilot (README stage 2): 8 rules x 4 starts from results/pilot_specs.txt. Feasibility only.
# usage (repo root, WSL): bash experiments/archive/2026-10-kappa-first-passage/scripts/pilot.sh
set -uo pipefail
export CARGO_TARGET_DIR=$HOME/turmite-target-fp   # fresh dir: forces a build from the tree
E=experiments/archive/2026-10-kappa-first-passage
R=$E/results/pilot; S=$E/scratch/pilot; mkdir -p $R $S
LOG=$E/results/pilot.log
cargo build --release --example kappa_first_passage_sampler > $S/build.txt 2>&1 || { echo "build failed, see $S/build.txt" >&2; exit 1; }
B=$CARGO_TARGET_DIR/release/examples/kappa_first_passage_sampler
[ -z "$(find src Cargo.toml -newer $B -type f | head -1)" ] || { echo "binary older than sources: stale" >&2; exit 1; }
BANDS=32768-34816,131072-139264,524288-557056
echo "git $(git rev-parse --short HEAD) dirty(src,tests,Cargo.toml)=$(git -c core.filemode=false diff --stat HEAD -- src tests Cargo.toml | wc -l) $(date -Iseconds)" > $LOG
echo "sha256 $(sha256sum $B | cut -d' ' -f1)" >> $LOG
echo "specs sha256 $(sha256sum < $E/results/pilot_specs.txt | cut -d' ' -f1)" >> $LOG
echo "loadavg before: $(cut -d' ' -f1-3 /proc/loadavg); foreign: $(ps -eo pid,args | grep -E '/release/|cargo' | grep -v grep | grep -v pilot.sh | cut -c1-90 | tr '\n' ';')" >> $LOG
CMD="$B $R $S/pairs 4294967296 8192 $BANDS pilot-v1 2"
echo "cmd: $CMD < pilot_specs.txt" >> $LOG
/usr/bin/time -v $CMD < $E/results/pilot_specs.txt 2> $S/run.err
echo "exit $? ; loadavg after: $(cut -d' ' -f1-3 /proc/loadavg)" >> $LOG
grep -E "Elapsed|Maximum resident" $S/run.err >> $LOG
