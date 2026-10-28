# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""Arm A statistics. Input experiments/archive/2026-10-layers-colours/results/layers.csv (examples/layers.rs 26 8192 < experiments/archive/2026-10-layers-colours/results/layers_specs.txt); windows k >= 22 (the run
stops at k = 25, so the design's k = 26 window is not available)."""
import numpy as np, polars as pl
from scipy.stats import spearmanr
d = pl.read_csv("experiments/archive/2026-10-layers-colours/results/layers.csv").filter(pl.col("k") >= 22)
NL = 6
rows = []
for (w,), g in d.group_by("walker", maintain_order=True):
    rho, kp, ve, cc = [], [], [], []
    for r in g.iter_rows(named=True):
        s = np.array([r[f"sn{i}"] for i in range(NL)], float); S = s.sum()
        n = (np.array([r[f"bn{i}"] for i in range(NL)], float) + np.array([r[f"en{i}"] for i in range(NL)], float)) / 2
        rho.append((s / n) / (S / n.sum()))
        assert r["en0"] == r["perimeter"], "census layer 0 must equal probe perimeter"
        kp.append((s[0] / S) / (r["perimeter"] / r["area"]))
        ve.append(r["fin_sum"] / r["fin_n"]); cc.append(r["new_cells"] / s[0])
    kind = "rotor" if w.startswith("rotor") else "pw" if w.startswith("pw") else "ant"
    rows.append(dict(walker=w, kind=kind, nk=g.height, **{f"rho{i}": float(np.mean(np.array(rho)[:, i])) for i in range(NL)},
                     kappa_probe=float(np.mean(kp)), v_e=float(np.mean(ve)), c=float(np.mean(cc))))
t = pl.DataFrame(rows)
pl.Config.set_float_precision(2); pl.Config.set_tbl_rows(60); pl.Config.set_tbl_cols(20)
print(t)
print("\nmedian by kind:"); print(t.group_by("kind").agg([pl.col(c).median() for c in [f"rho{i}" for i in range(NL)] + ["kappa_probe", "v_e", "c"]] + [pl.len().alias("n")]))
a = t.filter(pl.col("kind") == "ant")
print("\nA1: max |rho(d)-1| over d>=2 per kind (median over walkers):")
for k in ["ant", "rotor", "pw"]:
    s = t.filter(pl.col("kind") == k)
    if s.height == 0: continue
    m = np.max(np.abs(s.select([f"rho{i}" for i in range(2, 5)]).to_numpy() - 1), axis=1)
    print(k, "median", round(float(np.median(m)), 3), "max", round(float(m.max()), 3), "walkers with max dev < 0.15:", int((m < 0.15).sum()), "of", len(m))
if a.height > 3:
    print("A3: Spearman(rho0, v_e) over ants:", spearmanr(a["rho0"], a["v_e"]), " Spearman(rho0, 1/c):", spearmanr(a["rho0"], 1 / a["c"]))
    print("    Spearman(rho0, rho1) over ants:", spearmanr(a["rho0"], a["rho1"]))
