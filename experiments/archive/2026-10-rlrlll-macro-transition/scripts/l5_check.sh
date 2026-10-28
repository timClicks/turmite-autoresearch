#!/usr/bin/env bash
# L5: fresh build and axiom audit of the whole Lean project including the infinite-plane multi-cycle closure
# (Plane.lean, PlaneChain.lean, PlaneForever.lean). Does not regenerate L4Data.lean and does not overwrite the L4 logs.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../../../.." && pwd)
E="$ROOT/experiments/archive/2026-10-rlrlll-macro-transition"
cd "$ROOT"
mkdir -p "$E/scratch"
BUILD=$(mktemp -d "$E/scratch/l5-check.XXXXXX")
cp "$E"/lean/*.lean "$E"/lean/lean-toolchain "$E"/lean/lakefile.toml "$E"/lean/lake-manifest.json "$BUILD/"
{
  echo '# Command: bash experiments/archive/2026-10-rlrlll-macro-transition/scripts/l5_check.sh'
  echo "# Source commit: $(git rev-parse HEAD); working-tree dirty files under lean/: $(git status --porcelain "$E/lean" | wc -l)"
  sha256sum "$E"/lean/*.lean "$E/lean/lakefile.toml" "$E/lean/lean-toolchain"
  cd "$BUILD"
  lake env lean --version
  lake build
} > "$E/results/c3_l5_build.txt" 2>&1
cd "$BUILD"
lake env lean Check.lean > "$E/results/c3_l5_axioms.txt" 2>&1
if grep -E 'sorryAx|Lean.ofReduceBool|error:' "$E/results/c3_l5_axioms.txt"; then
  echo 'Unexpected axiom or checker error' >&2
  exit 1
fi
echo 'Fresh L5 build and axiom audit passed.'
