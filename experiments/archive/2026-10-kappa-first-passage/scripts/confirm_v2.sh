#!/usr/bin/env bash
# V2-D rerun: kernel-role runs (8 seeds x 48 rules) with the radius-4 context recorder, bands 0 and 1 only.
# Trajectories are unchanged (checked against confirm/ by scripts/v2_identity.sh).
# usage (repo root, WSL): THREADS=3 bash experiments/archive/2026-10-kappa-first-passage/scripts/confirm_v2.sh
set -uo pipefail
export CARGO_TARGET_DIR=$HOME/turmite-target-fp
E=experiments/archive/2026-10-kappa-first-passage
R=$E/results/confirm_v2; S=$E/scratch/confirm_v2; mkdir -p $R $S
LOG=$E/results/confirm_v2.log
cargo build --release --example kappa_first_passage_sampler > $S/build.txt 2>&1 || { echo "build failed, see $S/build.txt" >&2; exit 1; }
B=$CARGO_TARGET_DIR/release/examples/kappa_first_passage_sampler
[ -z "$(find src Cargo.toml -newer $B -type f | head -1)" ] || { echo "binary older than sources: stale" >&2; exit 1; }
BANDS=32768-34816,131072-139264
{
echo "== start $(date -Iseconds) git $(git rev-parse --short HEAD) dirty(src,tests,Cargo.toml)=$(git -c core.filemode=false diff --stat HEAD -- src tests Cargo.toml | wc -l)"
echo "sha256 $(sha256sum $B | cut -d' ' -f1)"
echo "specs sha256 $(sha256sum < $E/results/confirm_v2_specs.txt | cut -d' ' -f1)"
echo "loadavg: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "cmd: FP_CTX4_ROWS=400000 $B $R $S/pairs 4294967296 8192 $BANDS confirm-v2 ${THREADS:-3} < confirm_v2_specs.txt"
} >> $LOG
FP_CTX4_ROWS=400000 /usr/bin/time -v $B $R $S/pairs 4294967296 8192 $BANDS confirm-v2 ${THREADS:-3} < $E/results/confirm_v2_specs.txt 2> $S/run.err
echo "exit $? $(date -Iseconds)" >> $LOG
grep -E "Elapsed|Maximum resident" $S/run.err >> $LOG
