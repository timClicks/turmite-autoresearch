# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Build walker_reference.csv: one row per (walker, seed, window set) of kappa against the walker's own
uniform reference. Reads only committed results of experiments/archive/2026-10-kappa-walker-reference.

  uv run research-outputs/cube-root-growth-paper/supplementary/walker-reference/build_walker_reference.py [--check]

Estimators are those of that experiment's scripts/analyse.py (log-log fits of area vs t_end and perimeter vs
area; kappa = mean over windows of (boundary_steps / (t/2)) / (perimeter/area), t = window end).
Deterministic; --check fails if the committed CSV or build JSON differ from a rebuild.
"""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np, polars as pl

here = Path(__file__).resolve().parent
root = here.parents[3]
exp = root / "experiments/archive/2026-10-kappa-walker-reference/results"
ANT = dict(q05=0.443, q25=0.664, med=0.814, q75=0.957, q95=1.332)  # 2026-10-kappa-uniform-baseline census_spread.txt
WALKERS = [("probe_mem.csv", p, "k12-22", 12, 22) for p in ("rw", "pw:0.25", "pw:0.5", "pw:0.75")] + \
          [("probe_rotor.csv", "rotor", "k12-22", 12, 22), ("probe_rotor.csv", "rotor", "k20-26", 20, 26)]

def kunif(a, b):
    p = a * (1 - b); return 2 * (1 - 0.5 ** (1 - p)) / (1 - p)

def rows():
    out = []
    for fn, walker, wset, lo, hi in WALKERS:
        d = pl.read_csv(exp / fn)
        for run in sorted(r for r in d["rule"].unique() if r.startswith(walker + ":")):
            g = d.filter(pl.col("rule") == run).sort("k")
            w = g.filter((pl.col("k") >= lo) & (pl.col("k") <= hi))
            if w.height < hi - lo + 1: continue
            t, A, P = (w[c].to_numpy().astype(float) for c in ("t", "area", "perimeter"))
            kap = (w["boundary_steps"].to_numpy() / (t / 2)) / (P / A)
            a = np.polyfit(np.log(t), np.log(A), 1)[0]; b = np.polyfit(np.log(A), np.log(P), 1)[0]
            ku = kunif(a, b)
            out.append(dict(walker=walker, seed=int(run.split(":")[-1]), window_set=wset, k_lo=lo, k_hi=hi,
                            n_escaped_windows=int(g["escaped"].sum()), a=a, beta=b, kappa=kap.mean(),
                            kappa_unif=ku, ratio=kap.mean() / ku))
    return pl.DataFrame(out).with_columns(pl.col(c).round(6) for c in ("a", "beta", "kappa", "kappa_unif", "ratio"))

def build():
    df = rows()
    csv = df.write_csv()
    summ = {"rows": df.height, "ant_census_ratio": ANT,
            "inputs_sha256": {f: hashlib.sha256((exp / f).read_bytes()).hexdigest() for f in ("probe_mem.csv", "probe_rotor.csv")},
            "walker_mean_ratio": {f"{r['walker']}|{r['window_set']}": round(r["ratio"], 4) for r in
                                  df.group_by(["walker", "window_set"], maintain_order=True).agg(pl.col("ratio").mean()).iter_rows(named=True)}}
    return csv, json.dumps(summ, indent=1, sort_keys=True) + "\n"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    csv, js = build()
    if a.check:
        ok = (here / "walker_reference.csv").read_text() == csv and (here / "walker_reference.build.json").read_text() == js
        print("walker_reference check", "ok" if ok else "STALE"); sys.exit(0 if ok else 1)
    (here / "walker_reference.csv").write_text(csv); (here / "walker_reference.build.json").write_text(js); print(js)
