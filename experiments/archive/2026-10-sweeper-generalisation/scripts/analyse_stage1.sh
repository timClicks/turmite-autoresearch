#!/bin/bash
# Registered Stage 1 analysis: exact-clock test and window signature S in two windows per rule
# (last 2e8 steps before the census escape step; last 2e8 steps of the run). Run from the experiment directory.
set -e
S=scratch
an() { # name t_lo t_hi label
  echo "=== $1 [$2, $3] $4"
  python3 scripts/clock.py $S/$1 $2 $3 | tail -3
  python3 scripts/windows.py $S/$1 $2 $3
}
echo "# commit $(git rev-parse HEAD)"
an ctl_pos_RLRLLL 12677100000 12974495927 "positive control, post-switch part"
an ctl_neg_RRLLLLRRL 2800000000 3000000000 "negative control (log growth)"
an RLLLLRRL 12401085717 12601085717 "census-escape window"
an RLLLLRRL 20045062163 20245062163 "last 2e8 of run"
an RLLLRLRLLL 28227043780 28427043780 "census-escape window"
an RLLLRLRLLL 34663498538 34863498538 "last 2e8 of run"
an RLLLLRLRRL 39419909558 39619909558 "census-escape window"
an RLLLLRLRRL 59800000000 60000000000 "last 2e8 of run"
