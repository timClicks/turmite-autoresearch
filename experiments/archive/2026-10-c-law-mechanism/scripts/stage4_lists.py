# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Stage 4 lists (README, registered before running): tracer rules (bases + Part B mutants + P1/P2 mutants) and the P1/P2 probe specs.
usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage4_lists.py"""
from pathlib import Path

import polars as pl

root = Path(__file__).resolve().parents[4]
R = root / "experiments/archive/2026-10-c-law-mechanism/results"
(R / "p1").mkdir(exist_ok=True)
LR = root / "experiments/archive/2026-10-kappa-leadrun-fresh/results"


def lead(s):
    k = 1
    while k < len(s) and s[k] == s[0]:
        k += 1
    return k


def primitive(s):
    n = len(s)
    return not any(n % d == 0 and s == s[:d] * (n // d) for d in range(1, n))


def flip(s, i):
    return s[:i] + ("R" if s[i] == "L" else "L") + s[i + 1:]


fresh = pl.read_csv(LR / "fresh_rules.csv").filter(pl.col("stationary") & (pl.col("lead") <= 5)).sort("rule")
partb = pl.read_csv(LR / "mutants.csv")
bases = fresh["rule"].to_list()
seen = set(bases) | set(partb["mutant"].to_list())
rows = []
for base, k in zip(bases, fresh["lead"]):
    assert lead(base) == k
    for arm, idx in (("P1", k + 1), ("P2", k + 2)):
        if idx >= len(base) - 1:
            continue
        m = flip(base, idx)
        if not primitive(m) or m in seen:
            continue
        assert lead(m) == k
        seen.add(m)
        rows.append(dict(mutant=m, base=base, arm=arm, idx=idx, base_lead=int(k), new_lead=lead(m)))
df = pl.DataFrame(rows)
df.write_csv(R / "p1/p1_mutants.csv")
(R / "p1/p1_specs.txt").write_text("\n".join(f"{r}@{sd}" for r in df["mutant"] for sd in range(601, 609)) + "\n")
trace = list(dict.fromkeys(bases + partb["mutant"].to_list() + df["mutant"].to_list()))
(R / "lists/s4_trace_rules.txt").write_text("\n".join(trace) + "\n")
print(f"{len(bases)} stationary fresh bases (lead<=5); Part B mutants {partb.height}; P mutants {df.height} "
      f"(P1 {int((df['arm'] == 'P1').sum())}, P2 {int((df['arm'] == 'P2').sum())}); tracer rules {len(trace)}; probe runs {8 * df.height}")
