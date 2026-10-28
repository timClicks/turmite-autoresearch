#!/usr/bin/env bash
# Readiness checks that need no new science: thread-count byte identity and run-level resume of the sampler.
# usage (repo root, WSL): bash experiments/archive/2026-10-kappa-first-passage/scripts/readiness.sh  -> results/readiness.json
set -uo pipefail
E=experiments/archive/2026-10-kappa-first-passage
B=$HOME/turmite-target-fp/release/examples/kappa_first_passage_sampler
T=$E/scratch/readiness; rm -rf $T; mkdir -p $T
SPECS=$'RRLLLRLLLRRR@202610207001\nRLLRLR@202610207002\nrotor:3\nrw:4\nLRRRLL@9'
BANDS=2048-2176,8192-8704
for n in 1 4; do printf '%s\n' "$SPECS" | $B $T/t$n/out $T/t$n/pairs 100000000 4096 $BANDS rd $n 2>/dev/null; done
# status.csv carries wall-clock seconds, the one nondeterministic field: compare everything else
cmp_other=$(diff -r -x '*.status.csv' $T/t1 $T/t4 >/dev/null && echo true || echo false)
cut_status=$(for n in 1 4; do for f in $T/t$n/out/*.status.csv; do tail -n +2 $f | cut -d, -f1-11; done | sha256sum | cut -d' ' -f1; done | uniq | wc -l)
# resume: rerun with the same marker must skip everything and leave bytes unchanged
before=$(cat $T/t1/out/*.bands.csv | sha256sum | cut -d' ' -f1)
rerun=$(printf '%s\n' "$SPECS" | $B $T/t1/out $T/t1/pairs 100000000 4096 $BANDS rd 1 2>&1 | grep -c '^skip')
after=$(cat $T/t1/out/*.bands.csv | sha256sum | cut -d' ' -f1)
# changed recipe must refuse to resume
refuse=$(printf 'rotor:3\n' | $B $T/t1/out $T/t1/pairs 100000000 4096 $BANDS OTHER 1 2>&1 | grep -c 'different config' )
cat > $E/results/readiness.json <<J
{"checked": "$(date -Iseconds)", "git": "$(git rev-parse --short HEAD)", "sampler_sha256": "$(sha256sum $B | cut -d' ' -f1)",
 "threads_1_vs_4_files_identical_except_status": $cmp_other,
 "threads_1_vs_4_status_without_seconds_identical": $([ "$cut_status" = 1 ] && echo true || echo false),
 "resume_skipped_specs": $rerun, "resume_bytes_unchanged": $([ "$before" = "$after" ] && echo true || echo false),
 "changed_recipe_refused": $([ "$refuse" -ge 1 ] && echo true || echo false),
 "in_memory_checkpoint_test": "tests/first_passage.rs::checkpoint_by_clone_is_exact",
 "on_disk_mid_trajectory_checkpoint": "implemented in stage V2; see results/resume_check.json and tests/first_passage.rs::disk_checkpoint_roundtrip_is_exact",
 "full_release_tests": "results/release-tests-v2.log (155 passed, 0 failed)"}
J
cat $E/results/readiness.json
