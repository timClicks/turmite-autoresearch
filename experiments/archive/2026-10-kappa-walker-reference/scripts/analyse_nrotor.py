# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Noisy-rotor scan: ratio = kappa / kappa_unif(a, beta) per EPS, own (a, beta) per seed, plus drift g.

Estimators identical to analyse.py (imported by copy, not by module, to keep scripts standalone).
g = slope of ln(kappa_k) on k over the window set; stationary if |g| < 0.05.
"""
from pathlib import Path
import numpy as np, polars as pl

root = Path(__file__).resolve().parents[1]
ANT_MED = 0.814

def kunif(a, b):
    p = a * (1 - b); return 2 * (1 - 0.5 ** (1 - p)) / (1 - p)

def run_stats(g, lo, hi):
    w = g.filter((pl.col("k") >= lo) & (pl.col("k") <= hi))
    if w.height < hi - lo + 1: return None
    t = w["t"].to_numpy().astype(float); A = w["area"].to_numpy().astype(float); P = w["perimeter"].to_numpy().astype(float)
    kap = (w["boundary_steps"].to_numpy() / (t / 2)) / (P / A)
    a = np.polyfit(np.log(t), np.log(A), 1)[0]; b = np.polyfit(np.log(A), np.log(P), 1)[0]
    drift = np.polyfit(w["k"].to_numpy().astype(float), np.log(kap), 1)[0]
    return dict(a=a, beta=b, kappa=kap.mean(), ku=kunif(a, b), ratio=kap.mean() / kunif(a, b), g=drift)

d = pl.read_csv(root / "results/probe_nrotor.csv")
d = d.with_columns(pl.col("rule").str.split(":").list.get(1).cast(pl.Float64).alias("eps"))
lines = [f"ant median ratio {ANT_MED} (census_spread.txt, baseline expt); nrotor:EPS:SEED, seeds 2026102001..08"]
for lo, hi in [(20, 26), (12, 22), (12, 20)]:
    lines.append(f"\n== windows k={lo}..{hi}: mean (between-seed sd) over runs with all windows in the set complete (esc = runs that left the board later; n = runs usable); stationary = |g|<0.05")
    lines.append(f"{'eps':>5} {'n':>2} {'esc':>3} {'a':>14} {'beta':>14} {'kappa':>14} {'kunif':>7} {'ratio':>14} {'g':>15} {'nstat':>5} {'ratio(stat)':>12}")
    for eps in sorted(d["eps"].unique()):
        rows, esc = [], 0
        for run in sorted(d.filter(pl.col("eps") == eps)["rule"].unique()):
            g = d.filter(pl.col("rule") == run).sort("k")
            esc += int(g["escaped"].sum() > 0)  # escape only truncates the run; complete windows before it are valid
            s = run_stats(g, lo, hi)
            if s: rows.append(s)
        esc = sum(1 for r in d.filter(pl.col("eps") == eps)["rule"].unique() if d.filter(pl.col("rule") == r)["escaped"].any())
        if not rows: lines.append(f"{eps:5.2f}  no usable runs (esc={esc})"); continue
        f = lambda k: np.array([r[k] for r in rows])
        ms = lambda k, p=3: f"{f(k).mean():.{p}f} ({f(k).std(ddof=1) if len(rows) > 1 else float('nan'):.{p}f})"
        st = np.abs(f("g")) < 0.05
        rs = f("ratio")[st]
        lines.append(f"{eps:5.2f} {len(rows):2d} {esc:3d} {ms('a'):>14} {ms('beta'):>14} {ms('kappa'):>14} {f('ku').mean():7.3f} "
                     f"{ms('ratio'):>14} {ms('g'):>15} {int(st.sum()):5d} {(f'{rs.mean():.3f}' if len(rs) else '-'):>12}")
(root / "results/analysis_nrotor.txt").write_text("\n".join(lines) + "\n"); print("\n".join(lines))
