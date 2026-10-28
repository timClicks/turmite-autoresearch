#!/usr/bin/env bash
# V2-D: the radius-4 rerun (bands 0,1 only, ctx recorder on) must reproduce the v1 trajectories: compare the band-0 and band-1 rows of every
# kernel-role bands.csv with the v1 confirmation. usage (repo root): bash experiments/archive/2026-10-kappa-first-passage/scripts/v2_identity.sh
set -uo pipefail
E=experiments/archive/2026-10-kappa-first-passage
n=0; same=0; diff_list=""
for f in $E/results/confirm_v2/*.bands.csv; do
  b=$(basename $f); g=$E/results/confirm/$b
  n=$((n+1))
  if [ "$(head -3 $f | md5sum)" = "$(head -3 $g | md5sum)" ]; then same=$((same+1)); else diff_list="$diff_list $b"; fi
done
cat > $E/results/v2_identity.json <<J
{"checked": "$(date -Iseconds)", "git": "$(git rev-parse --short HEAD)", "kernel_runs_compared": $n, "band0_band1_rows_identical": $same, "differing": "$(echo $diff_list | cut -c1-400)"}
J
cat $E/results/v2_identity.json
