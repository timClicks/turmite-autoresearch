# /// script
# dependencies = ["polars", "numpy"]
# ///
"""R1: boundary-width exponent against R_eq = sqrt(A/pi) instead of t. Inputs: shape csvs (see notes R1). Design/predictions: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-r1-width-vs-radius/scripts/r1_stats.py"""
import numpy as np, polars as pl
cols = "kind,spec,k,A,rg2,aniso,rbar,rsd,h2,h4,h8,Wsurf,fill".split(",")
def load(paths):
    rows = [l.strip().split(",") for p in paths for l in open(p) if l.startswith("cp,")]
    return pl.DataFrame(rows, schema=cols, orient="row").with_columns([pl.col(c).cast(pl.Float64) for c in cols[2:]])
def per_run(d, kmin, kmax):
    out = {}
    for (s,), g in d.group_by("spec"):
        g = g.sort("k").filter((pl.col("k") >= kmin) & (pl.col("k") <= kmax))
        if g.height < 3: continue
        k = g["k"].to_numpy(); R = np.sqrt(g["A"].to_numpy() / np.pi); W = g["Wsurf"].to_numpy(); t = k * np.log(2)
        out[s] = (np.polyfit(np.log(R), np.log(W), 1)[0], np.polyfit(t, np.log(R), 1)[0], np.polyfit(t, np.log(W), 1)[0], k.max())
    return out
sets = {
 "rotor a4c+a4 (k 22..32)": (["experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_rotor.csv", "experiments/archive/2026-10-a4-boundary-width/results/a4_shape_rotor.csv"], 22, 32),
 "ants a4c+a4 (k 22..32)": (["experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_ants.csv", "experiments/archive/2026-10-a4-boundary-width/results/a4_shape_ants.csv"], 22, 32),
 "ants w1 blank (k 22..30)": (["experiments/archive/2026-10-w1/results/w1_shape.csv"], 22, 30),
}
for label, (paths, lo, hi) in sets.items():
    r = per_run(load(paths), lo, hi); r = {s: v for s, v in r.items() if v[3] >= hi - 2}
    g = np.array([v[0] for v in r.values()]); rr = np.array([v[1] for v in r.values()]); dw = np.array([v[2] for v in r.values()])
    print(f"{label}: runs {len(r)}; gamma = dlogW/dlogR: mean {g.mean():.3f} sd {g.std(ddof=1):.3f} SE {g.std(ddof=1)/np.sqrt(len(g)):.3f}; R-exponent in t: {rr.mean():.3f}; W-exponent in t: {dw.mean():.3f}")
    if "w1" in label or "ants a4c" in label:
        by = {}
        for s, v in r.items(): by.setdefault(s.split("@")[0], []).append(v[0])
        m = np.array([np.mean(v) for v in by.values()]); print(f"   between-rule sd of gamma (rule means, {len(m)} rules): {m.std(ddof=1):.3f}")
