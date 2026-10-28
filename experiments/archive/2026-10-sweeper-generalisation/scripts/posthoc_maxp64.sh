#!/bin/bash
# POST HOC (not registered): the clock test with phase period up to 64, with a guard of at least 8 cycles per phase class so that
# large p cannot fit a short window trivially. Run from the experiment directory in WSL; output results/stage1_posthoc_maxp64.txt.
set -e
echo "# POST HOC: clock.py --maxp 64 --minper 8 (registered limit was p <= 6, no guard); commit $(git rev-parse --short HEAD)"
for spec in "RLLLLRRL 12401085717 12601085717" "RLLLLRRL 20045062163 20245062163" "RLLLRLRLLL 34663498538 34863498538" "RLLLLRLRRL 58000000000 60000000000" "RLLLLRLRRL 39419909558 39619909558"; do
  set -- $spec
  echo "=== $1 [$2, $3]"
  python3 scripts/clock.py scratch/$1 $2 $3 --maxp 64 --minper 8 --maxP 2 | tail -2
done
