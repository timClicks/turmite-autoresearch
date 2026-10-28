#!/bin/bash
# Oracle for square_ring_fillers_footprint (AGENTS rule 4): (1) final colour fingerprint equals fast::run (via
# rlrlll_macro_transition_resim) at 1e6 and 1e7 steps on a 4096 board for five rules; (2) an independent stdlib Python ant
# reproduces the read histogram, visited/new-cell counts, first_gt and fronts_after for 2e5-step runs, including rule switches.
# Run from the repository root. Output: results/oracle.txt
set -euo pipefail
E=experiments/archive/2026-10-square-ring-fillers
cargo build --release --locked --example square_ring_fillers_footprint --example rlrlll_macro_transition_resim
FP=target/release/examples/square_ring_fillers_footprint
RS=target/release/examples/rlrlll_macro_transition_resim
{
echo "# commit $(git rev-parse --short HEAD) dirty=$(git status --porcelain --untracked-files=no | wc -l)"
sha256sum $FP $RS
for R in RLRRRL RRLRRRR RLLR RRLLLRLLLRR RLRR; do
  for T in 1000000 10000000; do
    a=$(echo $R | $FP $T 4096 65536 --fingerprint | tail -1 | awk -F, '{print $(NF-2)" "$(NF-1)}')
    b=$($RS $R $T 4096 | grep '^fast' | sed 's/.*hash=\([0-9a-f]*\) nonzero=\([0-9]*\).*/\1 \2/')
    [ "$a" == "$b" ] && echo "FINGERPRINT $R $T identical ($a)" || { echo "FINGERPRINT $R $T MISMATCH [$a] [$b]"; exit 1; }
  done
done
python3 $E/scripts/oracle_footprint.py $FP
echo "ORACLE PASSED"
} | tee "$E/results/oracle.txt.new"
# Written via a temporary name so the header's dirty count does not see the output file itself being rewritten.
mv "$E/results/oracle.txt.new" "$E/results/oracle.txt"
