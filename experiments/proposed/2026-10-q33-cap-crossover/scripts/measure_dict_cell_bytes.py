# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Measure CPython dict[(x,y)]=colour bytes/cell via tracemalloc.

Planning figure for the Q33 Python sparse simulator only (not the tiled Rust
backend). Not a candidate for uncapped arms at N=2^31.

Run:
  UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy \\
    uv run --offline --script experiments/proposed/2026-10-q33-cap-crossover/scripts/measure_dict_cell_bytes.py
"""
from __future__ import annotations

import platform
import tracemalloc


def measure(n: int, base: int = 10**9) -> tuple[float, float]:
    """Return (current_B_per_cell, peak_B_per_cell) for n cells outside small-int cache."""
    tracemalloc.start()
    # Coordinates well above the small-int cache so each int is a real object.
    d = {(base + i, base + (i % 997)): (i % 256) for i in range(n)}
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del d
    return current / n, peak / n


def main() -> int:
    print(f"python={platform.python_version()}")
    for n in (10**5, 10**6):
        current, peak = measure(n)
        print(f"n={n} current_B_per_cell={current:.1f} peak_B_per_cell={peak:.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
