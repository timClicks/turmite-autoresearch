#!/bin/bash
# S2: ant alone on a uniform board of colour G, all G and 4 headings, 2^22 steps, 4096 board.
# usage (WSL, repo root): bash experiments/archive/2026-10-crystal-rules/scripts/s2_ground_sweep.sh RULE... > results/s2_ground_sweep.csv
BIN=${CARGO_TARGET_DIR:-$HOME/turmite-target}/release/examples/crystal_s2
echo "rule,G,h0,t_end,x,y,left_board,steps_per_axis_cell"
for r in "$@"; do
  n=${#r}
  for ((g=0; g<n; g++)); do
    for h in 0 1 2 3; do
      $BIN $r $g $h 4194304 | tail -1 | awk -F, -v n=$n 'BEGIN{OFS=","} {l=($4<4194304)?"yes":"no"; m=($5<0?-$5:$5); s=(m>0)?$4/m:0; print $1,$2,$3,$4,$5,$6,l,s}'
    done
  done
done
