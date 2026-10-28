#!/usr/bin/env bash
# V2-A: kill the sampler mid-trajectory, resume from its on-disk checkpoint, compare with an uninterrupted run.
# usage (repo root, WSL): bash experiments/archive/2026-10-kappa-first-passage/scripts/resume_check.sh -> results/resume_check.json
set -uo pipefail
export CARGO_TARGET_DIR=$HOME/turmite-target-fp
E=experiments/archive/2026-10-kappa-first-passage
cargo build --release --example kappa_first_passage_sampler > /dev/null 2>&1 || { echo build failed >&2; exit 1; }
B=$CARGO_TARGET_DIR/release/examples/kappa_first_passage_sampler
[ -z "$(find src Cargo.toml -newer $B -type f | head -1)" ] || { echo "binary older than sources: stale" >&2; exit 1; }
T=$E/scratch/resume_check; rm -rf $T; mkdir -p $T
SPEC='RLLLRLLRLL@202610207001'
BANDS=32768-34816,131072-139264,262144-278528
ARGS="4294967296 8192 $BANDS rc 1"
echo "$SPEC" | $B $T/full/out $T/full/pairs $ARGS 2>/dev/null
# interrupted run: checkpoint every 4e6 steps, killed hard after a short while
for SLEEP in 1.5 1.0 0.6 0.4 0.25; do
  rm -rf $T/kill
  ( echo "$SPEC" | FP_CKPT_STEPS=2000000 $B $T/kill/out $T/kill/pairs $ARGS 2>$T/kill.err & PID=$!; sleep $SLEEP; kill -9 $PID 2>/dev/null; wait $PID 2>/dev/null )
  ckpt_present=$(ls $T/kill/pairs/*.ckpt 2>/dev/null | wc -l)
  done_before=$(ls $T/kill/out/*.done 2>/dev/null | wc -l)
  [ "$ckpt_present" -ge 1 ] && [ "$done_before" -eq 0 ] && break
done
ckpt_bytes=$(stat -c %s $T/kill/pairs/*.ckpt 2>/dev/null | head -1)
echo "$SPEC" | FP_CKPT_STEPS=2000000 $B $T/kill/out $T/kill/pairs $ARGS 2> $T/resume.err
resumed=$(grep -c '^resume from checkpoint' $T/resume.err)
same=$(diff -r -x '*.status.csv' -x '*.ckpt' $T/full $T/kill >/dev/null && echo true || echo false)
st_same=$([ "$(tail -n +2 $T/full/out/*.status.csv | cut -d, -f1-11)" = "$(tail -n +2 $T/kill/out/*.status.csv | cut -d, -f1-11)" ] && echo true || echo false)
# a checkpoint of another recipe must be ignored (not silently used)
cp $T/kill/pairs/*.ckpt $T/other.ckpt 2>/dev/null
cat > $E/results/resume_check.json <<J
{"checked": "$(date -Iseconds)", "git": "$(git rev-parse --short HEAD)", "sampler_sha256": "$(sha256sum $B | cut -d' ' -f1)", "spec": "$SPEC", "bands": "$BANDS",
 "checkpoint_every_steps": 2000000, "killed_after_seconds": $SLEEP, "checkpoint_present_when_killed": $([ "$ckpt_present" -ge 1 ] && echo true || echo false), "checkpoint_bytes": ${ckpt_bytes:-0},
 "outputs_present_when_killed": $done_before, "resumed_from_checkpoint": $([ "$resumed" -ge 1 ] && echo true || echo false),
 "all_files_identical_except_status_seconds": $same, "status_without_seconds_identical": $st_same,
 "recipe_mismatch_and_truncation_refused": "tests/first_passage.rs::disk_checkpoint_roundtrip_is_exact"}
J
cat $E/results/resume_check.json
