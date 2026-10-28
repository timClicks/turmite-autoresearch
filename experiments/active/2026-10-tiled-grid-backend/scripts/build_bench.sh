#!/usr/bin/env bash
# Build the benchmark binaries from a clean export of COMMIT into a fresh target directory (AGENTS.md "stale-build trap").
# usage: build_bench.sh COMMIT OUTDIR      (run from the repository root; OUTDIR is created and must not exist)
set -euo pipefail
commit=$1
out=$2
[ ! -e "$out" ] || { echo "$out exists; use a fresh directory" >&2; exit 1; }
mkdir -p "$out/src"
git archive "$commit" | tar -x -C "$out/src"
(cd "$out/src" && CARGO_TARGET_DIR="$out/target" cargo build --release --locked --bin sweep_lean --example tiled_grid_backend_codec)
echo "build exit status 0 for $commit"
sha256sum "$out/target/release/sweep_lean" "$out/target/release/examples/tiled_grid_backend_codec" | tee "$out/sha256.txt"
echo "$commit" > "$out/commit.txt"
