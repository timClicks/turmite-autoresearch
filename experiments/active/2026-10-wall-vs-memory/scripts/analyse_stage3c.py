"""Score Stage 3c (fs:RULE:SET:SEED, random fresh turns from a set) exactly as registered in the README.

usage (repo root): uv run --frozen python experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3c.py [RESULTS_DIR]
Reads RESULTS_DIR/stage3c_probe.csv (default: the committed results/) and the committed Stage 1
results/probe.csv (gate T3); writes stage3c_runs.csv and stage3c_analysis.txt into RESULTS_DIR.
`fit` and `classify` are Stage 1's (copied unchanged from scripts/analyse.py); `stalled` as Stage 3;
`filler` as registered for Stage 3c.
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
    return dict(a=np.polyfit(np.log(t), np.log(A), 1)[0], beta=np.polyfit(np.log(A), np.log(P), 1)[0])


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
    areas = g.sort("k")["area"].to_list()
    return (not np.isnan(early_a) and early_a < 0.45) or (len(areas) >= 2 and areas[-1] == areas[-2])


def filler(g: pl.DataFrame, early_a: float, early_beta: float) -> bool:
    """Registered: early a >= 0.90, early beta <= 0.62, A/t over the last three windows within 3% of their mean."""
    last = g.sort("k").tail(3)
    at = (last["area"] / last["t"]).to_numpy()
    return early_a >= 0.90 and early_beta <= 0.62 and len(at) == 3 and bool(np.all(np.abs(at / at.mean() - 1) <= 0.03))


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (np.nan, np.nan)
    z, p = 1.959964, k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (c - h, c + h)


out: list[str] = []


def P(s: str = "") -> None:
    out.append(s)
    print(s)


df = pl.read_csv(RES / "stage3c_probe.csv")
s1 = pl.read_csv(EXP / "results" / "probe.csv")
a_rules = sorted((EXP / "results" / "rules.txt").read_text().split())
b_rules = set((EXP / "results" / "stage3b_rules.txt").read_text().split())
P(f"# Stage 3c scoring; {df['rule'].n_unique()} specs")

t3 = []
for r in a_rules:
    x = df.filter(pl.col("rule") == f"fs:{r}:RL:2026102601").drop("rule").sort("k")
    y = s1.filter(pl.col("rule") == f"hy:{r}:0:1:2026102601").drop("rule").sort("k")
    t3.append(y.height > 0 and x.equals(y))
P(f"T3 fs:RULE:RL:2026102601 == hy:RULE:0:1:2026102601 (all fields but the label): {sum(t3)}/{len(t3)} -> {'PASS' if all(t3) else 'FAIL'}")

rows = []
for spec in sorted(df["rule"].unique().to_list()):
    _, rule, s, seed = spec.split(":")
    if s == "RL":
        continue
    g = df.filter(pl.col("rule") == spec).sort("k")
    e, l = fit(g, *WINDOWS["early"]), fit(g, *WINDOWS["late"])
    ea, eb = (e["a"], e["beta"]) if e else (np.nan, np.nan)
    c = dict(early_a=ea, early_beta=eb, late_a=l["a"] if l else np.nan, late_n=1 if l else 0)
    if e is None and bool(g["escaped"].any()):
        cls = "escape"
    elif stalled(g, ea):
        cls = "stalled"
    elif e is not None and filler(g, ea, eb):
        cls = "filler"
    else:
        cls = classify(c)
    cohort = "A" if seed != "2026102801" else "B"
    assert (cohort == "A") == (rule in a_rules) and (cohort == "B") == (rule in b_rules)
    rows.append(dict(cohort=cohort, rule=rule, set=s, seed=int(seed), early_a=ea, early_beta=eb, late_a=c["late_a"], cls=cls))
runs = pl.DataFrame(rows).sort("cohort", "set", "rule", "seed")
runs.write_csv(RES / "stage3c_runs.csv", float_precision=4)

P()
res = {}
for (cohort, s), sub in sorted(runs.group_by("cohort", "set"), key=lambda kv: kv[0]):
    counts = dict(sorted(sub.group_by("cls").len().iter_rows()))
    base = sub.filter(~pl.col("cls").is_in(["escape", "filler"]))
    k_c, k_p, n = int((base["cls"] == "compact").sum()), int((base["cls"] == "porous").sum()), base.height
    esc = int((sub["cls"] == "escape").sum())
    f, p = k_c / n, k_p / n
    res[(cohort, s)] = (f, p)
    (flo, fhi), (plo, phi), (elo, ehi) = wilson(k_c, n), wilson(k_p, n), wilson(esc, sub.height)
    P(f"cohort {cohort} {s:>3}: {counts}")
    P(f"      f = {k_c}/{n} = {f:.3f} [{flo:.3f}, {fhi:.3f}]; p = {k_p}/{n} = {p:.3f} [{plo:.3f}, {phi:.3f}]; "
      f"escape {esc}/{sub.height} = {esc / sub.height:.3f} [{elo:.3f}, {ehi:.3f}]")

P()
for cohort in "AB":
    bounded = ["RU", "LU"] if cohort == "A" else ["RU"]
    fb = [res[(cohort, s)][0] for s in bounded]
    p_rlu = res[(cohort, "RLU")][1]
    if all(v >= 0.90 for v in fb) and p_rlu >= 0.50:
        reading = "H-bound supported"
    elif all(v <= 0.50 for v in fb):
        reading = "H-random supported"
    else:
        reading = "unresolved"
    P(f"READING cohort {cohort}: bounded f {', '.join(f'{s} {v:.3f}' for s, v in zip(bounded, fb))}; RLU p {p_rlu:.3f} -> "
      + (reading if all(t3) else "not scored: gate T3 failed"))

P()
ant = {}
for r in a_rules:
    g = s1.filter(pl.col("rule") == f"hy:{r}:0:0:0").sort("k")
    ant[r] = fit(g, *WINDOWS["early"])["a"]
f1 = {}
for r in a_rules:
    v = [fit(s1.filter(pl.col("rule") == f"hy:{r}:0:1:{s}").sort("k"), *WINDOWS["early"]) for s in range(2026102601, 2026102609)]
    f1[r] = np.mean([x["a"] for x in v if x])
P("cohort A condition means (early a over complete runs): rule, ant, F1 (hy:0:1), RU, LU, RLU")
n_ru = 0
for r in a_rules:
    m = {}
    for s in ("RU", "LU", "RLU"):
        sub = runs.filter((pl.col("cohort") == "A") & (pl.col("rule") == r) & (pl.col("set") == s) & pl.col("early_a").is_not_nan())
        m[s] = sub["early_a"].mean() if sub.height else np.nan
    n_ru += m["RU"] <= 0.78
    P(f"   {r:<13} {ant[r]:.3f}  {f1[r]:.3f}  {m['RU']:.3f}  {m['LU']:.3f}  {m['RLU']:.3f}")
P(f"side prediction: RU condition-mean early a <= 0.78 in {n_ru}/6 rules (needs >= 5) -> {'HELD' if n_ru >= 5 else 'FAILED'}")
for cohort in "AB":
    sub = runs.filter((pl.col("cohort") == cohort) & (pl.col("set") == "RU"))
    esc = int((sub["cls"] == "escape").sum()) / sub.height
    P(f"side prediction: cohort {cohort} RU escape rate {esc:.3f} < 0.05 -> {'HELD' if esc < 0.05 else 'FAILED'}; "
      f"RLU p {res[(cohort, 'RLU')][1]:.3f} >= 0.7 -> {'HELD' if res[(cohort, 'RLU')][1] >= 0.7 else 'FAILED'}")

(RES / "stage3c_analysis.txt").write_text("\n".join(out) + "\n")
