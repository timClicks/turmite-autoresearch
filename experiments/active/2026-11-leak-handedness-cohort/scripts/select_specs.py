"""Write the run specs for the leak-handedness cohort test (no random draw).

usage (repo root): uv run --frozen python experiments/active/2026-11-leak-handedness-cohort/scripts/select_specs.py
Writes results/specs.txt (one probe spec per line), results/spec_roles.csv (spec, cohort, arm, EF, role) and
results/cohorts.csv (rule -> cohort, from the committed wall-vs-memory Stage 3b classes).

Cohorts (from `experiments/active/2026-10-wall-vs-memory/results/stage3b_runs.csv`, classes as committed):
  C = compact under forced R *and* forced L at EF = 0;  E = escape under forced L, compact under forced R.
Rules in neither (13 intermediate under L, 1 intermediate under R) are excluded and listed with the reason.

Both arms go through `FreshSetWalker` (`fs:RULE:SET:SEED`) with a 20-slot SET: k = 10 EF slots hold the minority
turn, so the minority probability is EF/2 (the leak law of `HybridWalker`, as in the leak titration).
Arm R: base R, minority L. Arm L: base L, minority R. At EF = 1 both sets hold 10 R and 10 L (same law; the
letter order differs, so the two arms are independent draws of it). EF = 0 rows are `ft:RULE:R` and `ft:RULE:L`,
byte-identity gates against the committed Stage 3b rows.
"""
from pathlib import Path

import polars as pl

EXP = Path(__file__).resolve().parents[1]
S3B = EXP.parents[1] / "active" / "2026-10-wall-vs-memory" / "results" / "stage3b_runs.csv"
SEEDS = range(2026111201, 2026111205)
GRID_C = (0.1, 0.3, 0.5, 1.0)


def fmt(ef: float) -> str:
    return "1" if ef == 1.0 else str(ef)


def fs_set(base: str, ef: float) -> str:
    k = round(10 * ef)
    other = "L" if base == "R" else "R"
    s = base * (20 - k) + other * k
    assert len(s) == 20 and s.count(other) == k
    return s


d = pl.read_csv(S3B)
cls = {(r["rule"], r["turn"]): r["cls"] for r in d.iter_rows(named=True)}
rules = sorted({r for r, _ in cls})
assert len(rules) == 100
cohort: dict[str, str] = {}
for r in rules:
    cr, cl = cls[(r, "R")], cls[(r, "L")]
    if cr == "compact" and cl == "compact":
        cohort[r] = "C"
    elif cr == "compact" and cl == "escape":
        cohort[r] = "E"
    else:
        cohort[r] = f"excluded (R {cr}, L {cl})"

rows: list[tuple[str, str, str, str, str]] = []  # spec, cohort, arm, ef, role
for r in rules:
    c = cohort[r]
    if c not in ("C", "E"):
        continue
    rows.append((f"ft:{r}:R", c, "R", "0", "gate_s3b"))
    rows.append((f"ft:{r}:L", c, "L", "0", "gate_s3b"))
    grid = GRID_C if c == "C" else (0.1,)
    for ef in grid:
        for arm in ("R", "L"):
            for s in SEEDS:
                rows.append((f"fs:{r}:{fs_set(arm, ef)}:{s}", c, arm, fmt(ef), "new"))

specs = [x[0] for x in rows]
assert len(specs) == len(set(specs)), "duplicate specs"
(EXP / "results/specs.txt").write_text("\n".join(specs) + "\n")
(EXP / "results/spec_roles.csv").write_text(
    "spec,cohort,arm,ef,role\n" + "\n".join(",".join(x) for x in rows) + "\n")
(EXP / "results/cohorts.csv").write_text(
    "rule,cohort\n" + "\n".join(f"{r},{cohort[r]}" for r in rules) + "\n")
n = {k: sum(1 for v in cohort.values() if v == k) for k in ("C", "E")}
print(len(specs), "specs;", n, "; excluded", 100 - n["C"] - n["E"])
