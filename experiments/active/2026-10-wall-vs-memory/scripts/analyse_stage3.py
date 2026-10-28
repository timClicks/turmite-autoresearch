"""Score Stage 3 (fresh-turn policies `ft:RULE:T`, T in R/L/U) exactly as registered in the README.

usage (repo root): uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3.py [RESULTS_DIR]
Reads RESULTS_DIR/stage3_probe.csv (default: the committed results/) and the committed Stage 1
results/probe.csv (gate T1); writes stage3_runs.csv and stage3_analysis.txt into RESULTS_DIR.
Fits and classes are Stage 1's (`fit`, `classify` copied unchanged from scripts/analyse.py, which
runs its analysis at import), plus the registered "stalled" class.
"""
import sys
from pathlib import Path

import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
RES = Path(sys.argv[1]) if len(sys.argv) > 1 else EXP / "results"
WINDOWS = {"early": (12, 22), "late": (20, 26)}


def fit(g: pl.DataFrame, lo: int, hi: int) -> dict | None:
    w = g.filter((pl.col("k") >= lo) & (pl.col("k") <= hi))
    if w.height < hi - lo + 1:
        return None
    t = w["t"].to_numpy().astype(float)
    A = w["area"].to_numpy().astype(float)
    P = w["perimeter"].to_numpy().astype(float)
    kap = (w["boundary_steps"].to_numpy() / (t / 2)) / (P / A)
    return dict(
        a=np.polyfit(np.log(t), np.log(A), 1)[0],
        beta=np.polyfit(np.log(A), np.log(P), 1)[0],
        kappa=kap.mean(),
        g_k=np.polyfit(np.log(t), np.log(kap), 1)[0],
    )


def classify(c: dict) -> str:
    a, b = c.get("early_a"), c.get("early_beta")
    if a is None or np.isnan(a):
        return "no early fit"
    if a <= 0.78 and b <= 0.65:
        if c["late_n"] >= 6 and not c["late_a"] <= 0.74:
            return "intermediate"
        return "compact"
    if a >= 0.85 and b >= 0.80:
        return "porous"
    return "intermediate"


def stalled(g: pl.DataFrame, early_a: float) -> bool:
    """Registered: early a < 0.45, or the last window's area equals the previous window's."""
    areas = g.sort("k")["area"].to_list()
    return (not np.isnan(early_a) and early_a < 0.45) or (len(areas) >= 2 and areas[-1] == areas[-2])


out: list[str] = []


def P(s: str = "") -> None:
    out.append(s)
    print(s)


df = pl.read_csv(RES / "stage3_probe.csv")
s1 = pl.read_csv(EXP / "results" / "probe.csv")
rules = (EXP / "results" / "rules.txt").read_text().split()
P(f"# Stage 3 scoring; input {RES / 'stage3_probe.csv'}; {df['rule'].n_unique()} specs")

# Gate T1: ft:RULE:R rows equal the Stage 1 deterministic hy:RULE:0:0:0 rows except the label.
t1 = []
for r in rules:
    a = df.filter(pl.col("rule") == f"ft:{r}:R").drop("rule").sort("k")
    b = s1.filter(pl.col("rule") == f"hy:{r}:0:0:0").drop("rule").sort("k")
    t1.append(b.height > 0 and a.equals(b))
P(f"T1 ft:RULE:R == hy:RULE:0:0:0 (all fields but the label): {sum(t1)}/{len(rules)} -> {'PASS' if all(t1) else 'FAIL'}")

rows = []
for r in rules:
    for t in "RLU":
        g = df.filter(pl.col("rule") == f"ft:{r}:{t}")
        e, l = fit(g, *WINDOWS["early"]), fit(g, *WINDOWS["late"])
        c = dict(early_a=e["a"] if e else np.nan, early_beta=e["beta"] if e else np.nan,
                 late_a=l["a"] if l else np.nan, late_n=1 if l else 0)
        cls = "stalled" if stalled(g, c["early_a"]) else classify(c)
        rows.append(dict(rule=r, turn=t, early_a=c["early_a"], early_beta=c["early_beta"], late_a=c["late_a"],
                         late_beta=l["beta"] if l else np.nan, max_k=g["k"].max(), final_area=g.sort("k")["area"][-1],
                         cls=cls))
runs = pl.DataFrame(rows)
runs.write_csv(RES / "stage3_runs.csv", float_precision=4)

P()
P("rule            turn  early a  early beta  late a  late beta  max k  class")
for x in runs.iter_rows(named=True):
    P(f"{x['rule']:<15} {x['turn']:>4}  {x['early_a']:7.3f}  {x['early_beta']:10.3f}  {x['late_a']:6.3f}  {x['late_beta']:9.3f}  {x['max_k']:5d}  {x['cls']}")

P()
verdict = {}
for t in "LU":
    sub = runs.filter(pl.col("turn") == t)
    n_compact = int((sub["cls"] == "compact").sum())
    n_not = sub.height - n_compact
    verdict[t] = "compact" if n_compact >= 5 else "not compact" if n_not >= 5 else "split"
    P(f"arm {t}: compact in {n_compact}/{sub.height}, not compact in {n_not}/{sub.height} -> {verdict[t]}")
    P(f"   classes: {dict(sorted(sub.group_by('cls').len().iter_rows()))}")
    late = sub.filter(pl.col("late_a").is_not_nan())
    P(f"   late a <= 0.74 in {int((late['late_a'] <= 0.74).sum())}/{late.height} runs with a complete late window")

reading = {
    ("compact", "compact"): "H-bound favoured",
    ("compact", "not compact"): "H-chiral favoured",
    ("not compact", "not compact"): "H-match favoured",
    ("not compact", "compact"): "none of the three (unexplained)",
}.get((verdict["L"], verdict["U"]), "no reading (a split arm)")
P(f"READING (L, U) = ({verdict['L']}, {verdict['U']}): {reading}" if all(t1) else "READING not scored: gate T1 failed")

P()
ant = {x["rule"]: x["early_a"] for x in runs.filter(pl.col("turn") == "R").iter_rows(named=True)}
for t, need in (("L", 5), ("U", 4)):
    sub = runs.filter(pl.col("turn") == t)
    d = [x["early_a"] - ant[x["rule"]] for x in sub.iter_rows(named=True)]
    close = sum(abs(v) <= 0.05 for v in d)
    applies = t == "L" or verdict["U"] == "compact"
    P(f"side prediction {t}: |early a - ant| <= 0.05 in {close}/6 (needs >= {need})"
      + ("" if applies else " [not scored: U not compact]") + f"; differences {', '.join(f'{v:+.3f}' for v in d)}")

(RES / "stage3_analysis.txt").write_text("\n".join(out) + "\n")
