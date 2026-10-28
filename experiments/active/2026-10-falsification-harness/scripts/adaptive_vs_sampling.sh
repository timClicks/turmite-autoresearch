#!/usr/bin/env bash
# P7: per claim, the longest escape delay among adaptive candidates vs among random patch starts.
# usage: adaptive_vs_sampling.sh results/C1-RL-highway.csv ...
# Columns: class,index,seed,outcome,period,dx,dy,steps,... ; unresolved starts count as the horizon.
for f in "$@"; do
  awk -F, -v name="$(basename "$f" .csv)" '
    /^#/ || $1 == "class" { next }
    { s = ($4 == "unresolved") ? 1e18 : $8
      if (s > best[$1]) best[$1] = s }
    END { printf "%s patch_max=%s adaptive_max=%s adaptive_beats_sampling=%s\n", name, best["patch"], best["adaptive"], (best["adaptive"] > best["patch"]) ? "yes" : "no" }' "$f"
done
