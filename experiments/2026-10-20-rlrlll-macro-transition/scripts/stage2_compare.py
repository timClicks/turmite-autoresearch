# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "polars"]
# ///
"""Stage 2 consequence check: do the checked cycle lengths T_q(m) = 12 m + b_q reproduce every measured cycle?

usage: uv run experiments/2026-10-20-rlrlll-macro-transition/scripts/stage2_compare.py
Inputs: results/cycles.csv (tracer) and results/check_k0.txt (checker). Snapshot k is taken at the end of cycle k, so
cycle k + 1 starts from C(m_k, k mod 3) with m_k = m_0 + 2k.
"""
import re
from pathlib import Path

import numpy as np
import polars as pl

here = Path(__file__).resolve().parents[1]
check = (here / "results/check_k0.txt").read_text()
laws = re.findall(r"C\(m, (\d)\) -> C\(m \+ (\d+), \d\) in (\d+)/2 m \+ (\d+) steps", check)
assert len(laws) == 3 and "CLOSED" in check
a = {int(q): int(a2) // 2 for q, _, a2, _ in laws}
b = {int(q): int(b0) for q, _, _, b0 in laws}
g = {int(q): int(d) for q, d, _, _ in laws}
m0 = int(re.search(r"phase 0 k 0 m (\d+)", (here / "results/canonical_k0.txt").read_text()).group(1))
print(f"checked laws: T_q(m) = {a} m + {b}, growth {g}; m_0 = {m0}")

T = pl.read_csv(here / "results/cycles.csv")["steps"].to_numpy()
k = np.arange(len(T) - 1)
m = m0 + 2 * k
pred = np.array([a[q % 3] * mm + b[q % 3] for q, mm in zip(k, m)])
print(f"cycles compared: {len(k)}; exact matches: {int((T[1:] == pred).sum())}")
print(f"cycle 0 (from the arming step to snapshot 0, not covered): {T[0]} steps")

# Asymptote: per three cycles x moves 9 columns and m grows by 6; t ~ sum 12 m ~ 12 K^2 cycles, |x|^2 ~ 9 K^2.
mean_b = np.mean(list(b.values()))
print(f"mean b over phases {mean_b:.4f}; asymptotic d|x|^2/dt = 9 / 12 = {9 / 12:.4f}")
