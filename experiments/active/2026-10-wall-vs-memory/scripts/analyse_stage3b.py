"""Score Stage 3b (ft:RULE:T, T in R/L/U, 100 new core-class rules) exactly as registered in the README.

usage (repo root): uv run --frozen python experiments/active/2026-10-wall-vs-memory/scripts/analyse_stage3b.py [RESULTS_DIR]
Reads RESULTS_DIR/stage3b_probe.csv (default: the committed results/); writes stage3b_runs.csv and
stage3b_analysis.txt there. `fit` and `classify` are Stage 1's, copied unchanged from scripts/analyse.py
(which runs its analysis at import); `stalled` as Stage 3.
"""
import hashlib
import sys
from pathlib import Path

import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
RES = Path(sys.argv[1]) if len(sys.argv) > 1 else EXP / "results"
WINDOWS = {"early": (12, 22), "late": (20, 26)}
BOOT_SEED, BOOT_N = 20261028, 10_000


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


df = pl.read_csv(RES / "stage3b_probe.csv")
rules = sorted((EXP / "results" / "stage3b_rules.txt").read_text().split())
P(f"# Stage 3b scoring; {df['rule'].n_unique()} specs, {len(rules)} rules")

rows = []
for r in rules:
    for t in "RLU":
        g = df.filter(pl.col("rule") == f"ft:{r}:{t}").sort("k")
        e, l = fit(g, *WINDOWS["early"]), fit(g, *WINDOWS["late"])
        c = dict(early_a=e["a"] if e else np.nan, early_beta=e["beta"] if e else np.nan, late_a=l["a"] if l else np.nan, late_n=1 if l else 0)
        escaped = bool(g["escaped"].any())
        if e is None and escaped:
            cls = "escape"
        elif stalled(g, c["early_a"]):
            cls = "stalled"
        else:
            cls = classify(c)
        # a trajectory fingerprint, to count rules whose runs coincide (as two forced-L runs did in Stage 3)
        fp = hashlib.sha256(g.drop("rule").write_csv().encode()).hexdigest()
        rows.append(dict(rule=r, turn=t, early_a=c["early_a"], early_beta=c["early_beta"], late_a=c["late_a"],
                         late_beta=l["beta"] if l else np.nan, max_k=int(g["k"].max()), escaped=escaped, cls=cls, fp=fp))
runs = pl.DataFrame(rows)
runs.drop("fp").write_csv(RES / "stage3b_runs.csv", float_precision=4)

P()
for t in "RLU":
    sub = runs.filter(pl.col("turn") == t)
    counts = dict(sorted(sub.group_by("cls").len().iter_rows()))
    P(f"arm {t}: classes {counts}; distinct trajectories {sub['fp'].n_unique()} of {sub.height}")
r_arm = runs.filter(pl.col("turn") == "R")
n_esc_r, n_comp_r = int((r_arm["cls"] == "escape").sum()), int((r_arm["cls"] == "compact").sum())
t2 = n_esc_r == 0 and n_comp_r >= 90
P(f"T2 R arm: escapes {n_esc_r} (need 0), compact {n_comp_r}/100 (need >= 90) -> {'PASS' if t2 else 'FAIL'}")

P()
f = {}
for t in "LU":
    sub = runs.filter(pl.col("turn") == t)
    esc = int((sub["cls"] == "escape").sum())
    rest = sub.filter(pl.col("cls") != "escape")
    k = int((rest["cls"] == "compact").sum())
    f[t] = k / rest.height
    lo, hi = wilson(k, rest.height)
    elo, ehi = wilson(esc, sub.height)
    P(f"arm {t}: f = compact / non-escape = {k}/{rest.height} = {f[t]:.3f} [Wilson95 {lo:.3f}, {hi:.3f}]; "
      f"escape rate {esc}/{sub.height} = {esc / sub.height:.3f} [{elo:.3f}, {ehi:.3f}] (predicted 0.02-0.20)")
    if rest.filter(pl.col("cls") != "compact").height:
        P("   non-compact, non-escape runs: " + ", ".join(f"{x['rule']} {x['cls']} (a {x['early_a']:.3f}, beta {x['early_beta']:.3f})"
                                                       for x in rest.filter(pl.col("cls") != "compact").iter_rows(named=True)))


def band(v: float) -> str:
    return "high" if v >= 0.90 else "low" if v <= 0.50 else "mid"


reading = {("high", "high"): "weak H-bound survives (bounded fresh runs suffice whenever no highway forms)",
           ("high", "low"): "H-chiral", ("low", "low"): "H-match"}.get((band(f["L"]), band(f["U"])), "unresolved / rule-dependent")
P(f"READING (f_L {f['L']:.3f}, f_U {f['U']:.3f}): {reading}" if t2 else "READING not scored: gate T2 failed")

P()
w = runs.pivot(on="turn", index="rule", values="late_a").drop_nulls().filter(~pl.col("R").is_nan() & ~pl.col("U").is_nan()).sort("rule")
lr, lu = w["R"].to_numpy(), w["U"].to_numpy()
ratio = np.std(lu, ddof=1) / np.std(lr, ddof=1)
rng = np.random.default_rng(BOOT_SEED)
bs = []
for _ in range(BOOT_N):
    i = rng.integers(0, len(lr), len(lr))
    bs.append(np.std(lu[i], ddof=1) / np.std(lr[i], ddof=1))
blo, bhi = np.percentile(bs, [2.5, 97.5])
P(f"late a, rules with both R and U complete (n = {len(lr)}): R mean {lr.mean():.3f} sd {np.std(lr, ddof=1):.3f}; "
  f"U mean {lu.mean():.3f} sd {np.std(lu, ddof=1):.3f}")
P(f"sd_U / sd_R = {ratio:.3f}, rule-bootstrap 95% [{blo:.3f}, {bhi:.3f}] -> prediction (interval below 1) "
  f"{'HELD' if bhi < 1 else 'FAILED'}; U mean late a in [0.67, 0.72]: {'HELD' if 0.67 <= lu.mean() <= 0.72 else 'FAILED'}")

(RES / "stage3b_analysis.txt").write_text("\n".join(out) + "\n")
