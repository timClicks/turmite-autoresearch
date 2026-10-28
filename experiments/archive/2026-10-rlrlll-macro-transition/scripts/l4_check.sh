#!/usr/bin/env bash
# A fresh build avoids stale olean artifacts on /mnt/f. No existing data are removed.
set -euo pipefail
export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/turmite" UV_LINK_MODE=copy
ROOT=$(cd "$(dirname "$0")/../../../.." && pwd)
E="$ROOT/experiments/archive/2026-10-rlrlll-macro-transition"
cd "$ROOT"
uv run --frozen "$E/scripts/l4_gen.py"
mkdir -p "$E/scratch"
BUILD=$(mktemp -d "$E/scratch/l4-check.XXXXXX")
cp "$E"/lean/*.lean "$E"/lean/lean-toolchain "$E"/lean/lakefile.toml "$E"/lean/lake-manifest.json "$BUILD/"
{
  echo '# Command: bash experiments/archive/2026-10-rlrlll-macro-transition/scripts/l4_check.sh'
  echo "# Source commit: $(git rev-parse HEAD); working source hashes below"
  echo '# Deterministic finite certificates; no randomness; n universally quantified.'
  sha256sum "$E/results/canonical_k0.txt" "$E"/scripts/{l4_gen.py,c1b.py,c1_ant.py,l4_check.sh} "$E"/lean/*.{lean,toml,json} "$E/lean/lean-toolchain"
  cd "$BUILD"
  lake env lean --version
  lake build
} > "$E/results/c3_l4_build.txt" 2>&1
cd "$BUILD"
lake env lean Check.lean > "$E/results/c3_l4_axioms.txt" 2>&1
if grep -E 'sorryAx|Lean.ofReduceBool|^.*error:' "$E/results/c3_l4_axioms.txt"; then
  echo 'Unexpected axiom or checker error' >&2
  exit 1
fi
echo 'Fresh L4 build and axiom audit passed.'
