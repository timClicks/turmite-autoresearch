#!/usr/bin/env bash
# Confirmation run (README "Freeze"): 48 rules x (8 kernel + 8 outcome) seeds from results/confirm_specs.txt.
# Resumable: finished specs have .done markers and are skipped; rerunning yields the same bytes.
# usage (repo root, WSL): THREADS=3 bash experiments/archive/2026-10-kappa-first-passage/scripts/confirm.sh
set -uo pipefail
export CARGO_TARGET_DIR=$HOME/turmite-target-fp
E=experiments/archive/2026-10-kappa-first-passage
R=$E/results/confirm; S=$E/scratch/confirm; mkdir -p $R $S
LOG=$E/results/confirm.log
cargo build --release --example kappa_first_passage_sampler > $S/build.txt 2>&1 || { echo "build failed, see $S/build.txt" >&2; exit 1; }
B=$CARGO_TARGET_DIR/release/examples/kappa_first_passage_sampler
[ -z "$(find src Cargo.toml -newer $B -type f | head -1)" ] || { echo "binary older than sources: stale" >&2; exit 1; }
BANDS=32768-34816,131072-139264,524288-557056
{
echo "== start $(date -Iseconds) git $(git rev-parse --short HEAD) dirty(src,tests,Cargo.toml)=$(git -c core.filemode=false diff --stat HEAD -- src tests Cargo.toml | wc -l)"
echo "sha256 $(sha256sum $B | cut -d' ' -f1)"
echo "specs sha256 $(sha256sum < $E/results/confirm_specs.txt | cut -d' ' -f1)"
echo "loadavg: $(cut -d' ' -f1-3 /proc/loadavg); foreign: $(ps -eo pid,args | grep -E '/release/|cargo' | grep -v grep | grep -v confirm.sh | cut -c1-90 | tr '\n' ';')"
echo "cmd: $B $R $S/pairs 4294967296 8192 $BANDS confirm-v1 ${THREADS:-3} < confirm_specs.txt"
} >> $LOG
/usr/bin/time -v $B $R $S/pairs 4294967296 8192 $BANDS confirm-v1 ${THREADS:-3} < $E/results/confirm_specs.txt 2> $S/run.err
echo "exit $? $(date -Iseconds)" >> $LOG
grep -E "Elapsed|Maximum resident" $S/run.err >> $LOG
