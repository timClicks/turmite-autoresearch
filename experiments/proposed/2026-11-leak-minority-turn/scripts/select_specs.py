"""Draw the held-out cohort for the leak minority-turn test and write its run specs (one seeded draw).

usage (repo root): uv run --frozen python experiments/proposed/2026-11-leak-minority-turn/scripts/select_specs.py
Writes results/rules.txt, results/specs.txt and results/spec_roles.csv (spec, cohort, arm, ef, role).

Held-out cohort H: 110 rules drawn uniformly without replacement (numpy default_rng(20261113)) from the census core
class (cls == blob, 0.30 < alpha_w < 0.37, not bursty; as wall-vs-memory Stage 1/3b) sorted by rule, after removing
the six Stage 1 / leak-titration rules and the 100 Stage 3b rules (whose cohort C produced the post hoc lead).
Eligibility (compact under ft:RULE:R and ft:RULE:L at EF = 0) is decided by the frozen classifier in analyse.py.
Anchor cohort A: 6 cohort-C rules of the leak-handedness test (default_rng(20261113) draw from its 77, sorted), run
with byte-identical specs to that test (EF 0, 0.3, 0.5, 1; seeds 2026111201..04): gate G1.
Arms and sets exactly as the leak-handedness test: fs:RULE:SET:SEED with a 20-slot SET, k = 10 EF minority slots.
"""
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
WVM = ROOT / "experiments/active/2026-10-wall-vs-memory/results"
LHC = ROOT / "experiments/active/2026-11-leak-handedness-cohort/results"
SEEDS_H = range(2026111301, 2026111305)
SEEDS_A = range(2026111201, 2026111205)  # the leak-handedness seeds, for byte identity
GRID = (0.3, 0.5, 1.0)


def fmt(ef: float) -> str:
    return "1" if ef == 1.0 else str(ef)


def fs_set(base: str, ef: float) -> str:
    k = round(10 * ef)
    other = "L" if base == "R" else "R"
    s = base * (20 - k) + other * k
    assert len(s) == 20 and s.count(other) == k
    return s


census = pl.read_csv(ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
core = census.filter(
    (pl.col("cls") == "blob") & (pl.col("alpha_w") > 0.30) & (pl.col("alpha_w") < 0.37) & ~pl.col("bursty")
)
stage1 = set((WVM / "rules.txt").read_text().split())
s3b = set((WVM / "stage3b_rules.txt").read_text().split())
assert len(stage1) == 6 and len(s3b) == 100
pool = sorted(set(core["rule"].to_list()) - stage1 - s3b)
rng = np.random.default_rng(20261113)
H = sorted(pool[int(i)] for i in rng.choice(len(pool), size=110, replace=False))
# cohorts.csv has unquoted commas in its exclusion reasons; split on the first comma only
C = sorted(ln.split(",", 1)[0] for ln in (LHC / "cohorts.csv").read_text().splitlines()[1:] if ln.split(",", 1)[1] == "C")
assert len(C) == 77
A = sorted(C[int(i)] for i in rng.choice(len(C), size=6, replace=False))

rows: list[tuple[str, str, str, str, str]] = []
for co, rules, seeds in (("A", A, SEEDS_A), ("H", H, SEEDS_H)):
    for r in rules:
        rows.append((f"ft:{r}:R", co, "R", "0", "base"))
        rows.append((f"ft:{r}:L", co, "L", "0", "base"))
        for ef in GRID:
            for arm in ("R", "L"):
                for s in seeds:
                    rows.append((f"fs:{r}:{fs_set(arm, ef)}:{s}", co, arm, fmt(ef), "leak"))
specs = [x[0] for x in rows]
assert len(specs) == len(set(specs)), "duplicate specs"
(EXP / "results/rules.txt").write_text("".join(f"{co} {r}\n" for co, rr in (("A", A), ("H", H)) for r in rr))
(EXP / "results/specs.txt").write_text("\n".join(specs) + "\n")
(EXP / "results/spec_roles.csv").write_text(
    "spec,cohort,arm,ef,role\n" + "\n".join(",".join(x) for x in rows) + "\n")
print(f"pool {len(pool)}; H {len(H)}; A {len(A)}; {len(specs)} specs")
