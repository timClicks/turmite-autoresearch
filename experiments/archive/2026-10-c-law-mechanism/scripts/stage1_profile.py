# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Stage 1 (README): G0 calibration of edgestats_sample.csv against census c, then D1-D5, the per-colour profile r_k
of boundary steps per birth. usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage1_profile.py"""
import json
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
out = root / "experiments/archive/2026-10-c-law-mechanism/results"
es = pl.read_csv(root / "experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv")
cen = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
stat = cen.filter((pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))
res, lines = {}, []


def say(s=""):
    print(s)
    lines.append(s)


def run0(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


# per-rule aggregates
rules = es["rule"].unique(maintain_order=True).to_list()
prof = {}
for r in rules:
    g = es.filter(pl.col("rule") == r).sort("colour")
    prof[r] = dict(edge=g["edge_steps"].to_numpy().astype(float), new=g["new_cells"].to_numpy().astype(float))
say(f"edgestats sample: {len(rules)} rules")

# ---- G0
c_edge = {r: prof[r]["new"].sum() / prof[r]["edge"].sum() for r in rules}
cm = dict(zip(cen["rule"], cen["c"]))
cls = dict(zip(cen["rule"], cen["cls"]))
common = [r for r in rules if r in cm and cm[r] > 0 and cls[r] == "blob"]
x = np.array([c_edge[r] for r in common])
y = np.array([cm[r] for r in common])
corr = np.corrcoef(x, y)[0, 1]
rel = np.abs(x - y) / y
res["G0"] = dict(n=len(common), corr=corr, median_rel=float(np.median(rel)), median_ratio=float(np.median(x / y)),
                 passed=bool(corr >= 0.95 and np.median(rel) <= 0.06))
say(f"G0: {len(common)} sample rules in census (blob): corr {corr:.4f}, median |rel diff| {np.median(rel):.4f}, "
    f"median c_edge/c_census {np.median(x / y):.4f} -> {'PASS' if res['G0']['passed'] else 'FAIL'}")

# ---- profile sets
sset = set(stat["rule"].to_list())
use = [r for r in rules if r in sset]
say(f"stationary blob sample rules: {len(use)}")
rows = []
for r in use:
    p = prof[r]
    B = p["new"].sum()
    if B == 0:
        continue
    rk = p["edge"] / B
    rows.append(dict(rule=r, n=len(r), m=run0(r), r=rk, edge=p["edge"], new=p["new"], B=B))
say("lead distribution (n rules): " + ", ".join(f"{m}:{sum(1 for q in rows if q['m'] == m)}" for m in range(1, 12)
                                              if any(q['m'] == m for q in rows)))

# D1, D4, D5
sub = [q for q in rows if 2 <= q["m"] < q["n"]]
f_circ = np.array([q["new"][1:q["m"]].sum() / q["B"] for q in sub])
f_0m = np.array([(q["new"][0] + q["new"][q["m"]]) / q["B"] for q in sub])
p_kill = np.array([q["new"][q["m"]] / q["edge"][q["m"]] for q in sub if q["edge"][q["m"]] > 0])
p0 = np.array([q["new"][0] / q["edge"][0] for q in rows])
res["D1"] = dict(n=len(sub), median_frac_circulating=float(np.median(f_circ)), median_frac_0m=float(np.median(f_0m)),
                 passed=bool(np.median(f_circ) <= 0.05 and np.median(f_0m) >= 0.70))
res["D4"] = dict(n=len(p_kill), median=float(np.median(p_kill)), passed=bool(np.median(p_kill) >= 0.85))
res["D5"] = dict(n=len(p0), median=float(np.median(p0)), iqr=[float(np.percentile(p0, 25)), float(np.percentile(p0, 75))],
                 passed=bool(0.45 <= np.median(p0) <= 0.55))
say(f"D1 (2<=m<n, n={len(sub)}): births at colours 1..m-1: median {np.median(f_circ):.4f}; at {{0,m}}: median {np.median(f_0m):.4f} "
    f"-> {'PASS' if res['D1']['passed'] else 'FAIL'}")
say(f"D4 births/edge_steps at colour m: median {np.median(p_kill):.4f} -> {'PASS' if res['D4']['passed'] else 'FAIL'}")
say(f"D5 births/edge_steps at colour 0: median {np.median(p0):.4f} IQR [{np.percentile(p0, 25):.3f}, {np.percentile(p0, 75):.3f}] "
    f"-> {'PASS' if res['D5']['passed'] else 'FAIL'}")

# D2
sub4 = [q for q in rows if q["m"] >= 4 and q["m"] < q["n"]]
ratios = np.array([q["r"][1:q["m"]].max() / q["r"][1:q["m"]].min() for q in sub4 if q["r"][1:q["m"]].min() > 0])
pooled = np.concatenate([q["r"][1:q["m"]] for q in sub4])
res["D2"] = dict(n=len(sub4), median_max_over_min=float(np.median(ratios)), pooled_mean=float(pooled.mean()),
                 passed=bool(np.median(ratios) <= 1.35 and 0.55 <= pooled.mean() <= 0.85 and abs(pooled.mean() - 0.696) <= 0.10))
say(f"D2 (m>=4, n={len(sub4)}): median max/min of r_k over k=1..m-1 {np.median(ratios):.3f}; pooled mean r_k {pooled.mean():.3f} "
    f"(census b 0.696) -> {'PASS' if res['D2']['passed'] else 'FAIL'}")
# r_k by (m, k), descriptive
say("mean r_k by lead m (columns k = 0..): ")
res["rk_by_lead"] = {}
for m in range(1, 9):
    qs = [q for q in rows if q["m"] == m and q["m"] < q["n"]]
    if not qs:
        continue
    K = min(min(q["n"] for q in qs), m + 4)
    mat = np.array([q["r"][:K] for q in qs])
    res["rk_by_lead"][m] = dict(n=len(qs), mean=mat.mean(0).tolist(), sd=mat.std(0).tolist())
    say(f"  m={m} (n={len(qs)}): " + " ".join(f"{v:.2f}" for v in mat.mean(0)))

# D3
M = np.array([min(q["m"], 6) for q in rows], float)
Lp = np.array([q["r"][:q["m"]].sum() for q in rows])
Tp = np.array([q["r"][q["m"]:].sum() if q["m"] < q["n"] else 0 for q in rows])
tot = Lp + Tp


def slope(xv, yv):
    X = np.column_stack([np.ones(len(xv)), xv])
    b = np.linalg.lstsq(X, yv, rcond=None)[0]
    return b


rng = np.random.default_rng(20261019)
fits = {nm: slope(M, v) for nm, v in (("Lpart", Lp), ("Tpart", Tp), ("total", tot))}
boot = {nm: [] for nm in fits}
for _ in range(2000):
    i = rng.integers(0, len(M), len(M))
    for nm, v in (("Lpart", Lp), ("Tpart", Tp), ("total", tot)):
        boot[nm].append(slope(M[i], v[i])[1])
ci = {nm: [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))] for nm, b in boot.items()}
res["D3"] = dict(n=len(rows), fits={nm: dict(a=float(f[0]), b=float(f[1]), ci_b=ci[nm]) for nm, f in fits.items()},
                 passed=bool(0.55 <= fits["Lpart"][1] <= 0.85 and abs(fits["Tpart"][1]) <= 0.15))
say(f"D3 (n={len(rows)}, lead capped 6): Lpart = {fits['Lpart'][0]:.3f} + {fits['Lpart'][1]:.3f} m  CI_b {ci['Lpart']}; "
    f"Tpart = {fits['Tpart'][0]:.3f} + {fits['Tpart'][1]:.3f} m  CI_b {ci['Tpart']}; total = {fits['total'][0]:.3f} + {fits['total'][1]:.3f} m "
    f"-> {'PASS' if res['D3']['passed'] else 'FAIL'}")
# identity check
idc = np.array([abs(q["r"].sum() - q["edge"].sum() / q["new"].sum()) for q in rows]).max()
say(f"identity sum_k r_k = 1/c (max abs error {idc:.2e})")
(out / "stage1_profile.json").write_text(json.dumps(res, indent=1, default=float))
(out / "stage1_profile.txt").write_text("\n".join(lines) + "\n")
