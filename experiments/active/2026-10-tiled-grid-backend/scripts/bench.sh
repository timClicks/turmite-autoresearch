#!/usr/bin/env bash
# Interleaved repetitions of every (workload, backend) pair. Run from the repository root in WSL/Linux.
# usage: bench.sh BENCHDIR OUTDIR     (BENCHDIR from build_bench.sh; OUTDIR e.g. experiments/active/2026-10-tiled-grid-backend/results/runs)
set -euo pipefail
bench=$1
out=$2
bin="$bench/target/release/sweep_lean"
here="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$out"
: > "$out/identity.tsv"
tmp="$(mktemp -d)"

# config id -> environment (word-split on purpose)
declare -A ENVOF=(
  [A]=""
  [B6]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=unlimited"
  [B5]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=5 TURMITE_CACHE_TILES=unlimited"
  [B7]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=7 TURMITE_CACHE_TILES=unlimited"
  [R64]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=64 TURMITE_INACTIVE=raw"
  [C16]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=16 TURMITE_INACTIVE=packed"
  [C64]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=64 TURMITE_INACTIVE=packed"
  [C1024]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=1024 TURMITE_INACTIVE=packed"
  [C4096]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=4096 TURMITE_INACTIVE=packed"
  [T2c2p]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=2 TURMITE_CACHE_TILES=2 TURMITE_INACTIVE=packed"
  [T3c2p]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=3 TURMITE_CACHE_TILES=2 TURMITE_INACTIVE=packed"
  [L64]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=64 TURMITE_INACTIVE=lz4"
  [L1024]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=1024 TURMITE_INACTIVE=lz4"
  [L4096]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=4096 TURMITE_INACTIVE=lz4"
  [T3c2r]="TURMITE_GRID=tiled TURMITE_TILE_LOG2=3 TURMITE_CACHE_TILES=2 TURMITE_INACTIVE=raw"
)
declare -A CONFIGS=(
  [W1]="A B6 B5 B7 R64 C16 C64 C1024 L64 L1024"
  [W2]="A B6 R64 C64"
  [W3]="A B6 B5 B7 R64 C64 C1024 C4096 L64 L1024 L4096"
  [W4a]="A B6 C64"
  [W4b]="A B6 C64"
  [W5]="A B6 T2c2p T3c2p T3c2r"
)

{
  echo "date: $(date -Is)"
  echo "uname: $(uname -srvm)"
  echo "cpu: $(lscpu | grep -E 'Model name' | sed 's/  */ /g')"
  echo "mem: $(grep -E 'MemTotal|MemAvailable' /proc/meminfo | tr '\n' ' ')"
  echo "rustc: $(rustc --version)  cargo: $(cargo --version)"
  echo "bench commit: $(cat "$bench/commit.txt")"
  echo "sha256:"; cat "$bench/sha256.txt"
  echo "loadavg at start: $(cat /proc/loadavg)"
  echo "top cpu at start:"; ps -eo pid,pcpu,args --sort=-pcpu | head -6 | cut -c1-160
  echo "command: $0 $*"
} > "${out}_provenance.txt"

tail -n +2 "$here/workloads.tsv" | { if [ -n "${ONLYWL:-}" ]; then grep -E "^(${ONLYWL})	"; else cat; fi; } | while IFS=$'\t' read -r wl rule board steps reps; do
  for rep in $(seq 1 "$reps"); do
    for cfg in ${CONFIGS[$wl]}; do
      if [ -n "${ONLY:-}" ] && [[ " $ONLY " != *" $cfg "* ]]; then continue; fi
      base="$out/${wl}__${cfg}__r${rep}"
      loadbefore="$(cut -d' ' -f1 /proc/loadavg)"
      # shellcheck disable=SC2086
      echo "$rule" | env RAYON_NUM_THREADS=1 TURMITE_GRID_STATS="$base.json" ${ENVOF[$cfg]} \
        /usr/bin/time -f '{"wall_s":%e,"user_s":%U,"sys_s":%S,"maxrss_kb":%M}' -o "$base.time" \
        "$bin" - - "$steps" "$board" > "$tmp/${wl}__${cfg}__r${rep}.csv" 2> "$base.err"
      echo "{\"load1_before\":$loadbefore,\"load1_after\":$(cut -d' ' -f1 /proc/loadavg)}" > "$base.load"
      if [ "$cfg" = A ]; then
        cp "$tmp/${wl}__A__r${rep}.csv" "$out/${wl}__A__r${rep}.csv"   # the dense CSVs are small; tiled ones are compared, not kept
      fi
      if cmp -s "$tmp/${wl}__${cfg}__r${rep}.csv" "$tmp/${wl}__A__r${rep}.csv"; then same=1; else same=0; fi
      printf '%s\t%s\t%s\t%s\n' "$wl" "$cfg" "$rep" "$same" >> "$out/identity.tsv"
      if [ "$cfg" != A ]; then rm -f "$tmp/${wl}__${cfg}__r${rep}.csv"; fi   # keep the dense reference for the next configs
    done
    rm -f "$tmp/${wl}__A__r${rep}.csv"
  done
done
echo "loadavg at end: $(cat /proc/loadavg)" >> "${out}_provenance.txt"
echo "top cpu at end:" >> "${out}_provenance.txt"; ps -eo pid,pcpu,args --sort=-pcpu | head -6 | cut -c1-160 >> "${out}_provenance.txt"
rm -rf "$tmp"
