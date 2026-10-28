"""Analyse the coarse knockout map (see notes/knockout-map-hypotheses.md).

usage: python3 -I experiments/archive/2026-10-knockout-maps/scripts/knockout_analyse.py RULE
Reads experiments/archive/2026-10-knockout-maps/knock/RULE/{coarse.csv,base.csv,occ.u32,route.u32}; writes
experiments/archive/2026-10-knockout-maps/knock/RULE/{tiles.csv,hot.csv,summary.json} and prints the summary.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr, rankdata

ROOT = Path(__file__).resolve().parents[2 if lib else 3]
S, C = 4096, 2048


def load(rule):
    d = ROOT / "experiments/archive/2026-10-knockout-maps/knock" / rule
    rows = np.genfromtxt(d / "coarse.csv", delimiter=",", names=True, dtype=None, encoding=None)
    b = np.genfromtxt(d / "base.csv", delimiter=",", names=True)
    occ = np.fromfile(d / "occ.u32", dtype="<u4").reshape(S, S).astype(float)
    route = np.fromfile(d / "route.u32", dtype="<u4").reshape(S, S).astype(float)
    return d, rows, b, occ, route


def partial_spearman(y, x, controls):
    """Spearman partial correlation: rank everything, regress controls out of both."""
    def res(v):
        A = np.column_stack([np.ones(len(v))] + [rankdata(c) for c in controls])
        r = rankdata(v)
        return r - A @ np.linalg.lstsq(A, r, rcond=None)[0]
    return float(np.corrcoef(res(y), res(x))[0, 1])


def main(rule):
    d, rows, b, occ, route = load(rule)
    B = float(b["near_home"])
    kind = rows["kind"]
    ok = rows["ok"] == 1
    loss = B - rows["near_home"]
    out = {"rule": rule, "baseline_near_home": B, "baseline_own": float(b["own"]), "baseline_spread": float(b["spread"]),
           "failed_runs": int((~ok).sum())}

    # controls
    bl = kind == "patch"
    swap = (kind == "swap") & ok
    blank = bl & (rows["nvis"] == 0)
    out["blank_tiles"] = int(blank.sum())
    out["blank_max_abs_loss"] = float(np.abs(loss[blank]).max()) if blank.any() else None
    null = loss[swap]
    p95 = float(np.quantile(null, 0.95))
    rng = np.random.default_rng(0)
    m3 = rng.choice(null, size=(20000, 3)).mean(axis=1)
    p95m3 = float(np.quantile(m3, 0.95))
    out["swap"] = {"n": int(swap.sum()), "mean_loss": float(null.mean()), "sd": float(null.std()),
                   "p95_single": p95, "p95_mean_of_3": p95m3, "mean_dose": float(rows["changed"][swap].mean())}

    # tiles
    pt = bl & (rows["nvis"] > 0) & ok
    keys = sorted({(int(x), int(y)) for x, y in zip(rows["x"][pt], rows["y"][pt])})
    recs = []
    for (x, y) in keys:
        m = pt & (rows["x"] == x) & (rows["y"] == y)
        l = loss[m]
        if len(l) < 3:
            continue
        cx, cy = x + 2.5, y + 2.5
        recs.append({
            "x": x, "y": y, "loss": l.mean(), "l1": l[0], "l2": l[1], "l3": l[2],
            "n_exceed": int((l > p95).sum()), "dose": rows["changed"][m].mean(), "nvis": int(rows["nvis"][m][0]),
            "occ": occ[C + y:C + y + 5, C + x:C + x + 5].mean(), "route": route[C + y:C + y + 5, C + x:C + x + 5].mean(),
            "dist": float(np.hypot(cx, cy)),
            "own_loss": float(b["own"]) - rows["own"][m].mean(), "spread": rows["spread"][m].mean(),
        })
    T = {k: np.array([r[k] for r in recs]) for k in recs[0]}
    nt = len(recs)
    hot = (T["loss"] > p95m3) & (T["n_exceed"] >= 2)
    out["tiles"] = nt
    out["frac_tiles_loss_le_null_p95_mean3"] = float((T["loss"] <= p95m3).mean())
    out["hot_tiles"] = int(hot.sum())
    out["hot_frac"] = float(hot.mean())
    out["max_tile_loss"] = float(T["loss"].max())
    out["mean_tile_loss"] = float(T["loss"].mean())
    out["patch_vs_swap_mean_loss"] = [float(T["loss"].mean()), float(null.mean())]
    out["patch_vs_swap_dose"] = [float(T["dose"].mean()), float(rows["changed"][swap].mean())]

    # reproducibility across independent permutations
    pairs = [("l1", "l2"), ("l1", "l3"), ("l2", "l3")]
    out["repro_pearson"] = float(np.mean([np.corrcoef(T[a], T[c])[0, 1] for a, c in pairs]))
    out["repro_spearman"] = float(np.mean([spearmanr(T[a], T[c])[0] for a, c in pairs]))

    # route density
    rf = T["route"] / np.maximum(T["occ"], 1e-9)
    ctrl = [np.log1p(T["occ"]), T["dist"], T["dose"]]
    out["rho_loss_route"] = float(spearmanr(T["loss"], T["route"])[0])
    out["rho_loss_occ"] = float(spearmanr(T["loss"], T["occ"])[0])
    out["rho_loss_dist"] = float(spearmanr(T["loss"], T["dist"])[0])
    out["rho_route_occ"] = float(spearmanr(T["route"], T["occ"])[0])
    out["partial_rho_route"] = partial_spearman(T["loss"], T["route"], ctrl)
    out["rho_loss_routefrac"] = float(spearmanr(T["loss"], rf)[0])
    out["partial_rho_routefrac"] = partial_spearman(T["loss"], rf, ctrl)
    boot = []
    for _ in range(1000):
        i = rng.integers(0, nt, nt)
        boot.append(partial_spearman(T["loss"][i], T["route"][i], [c[i] for c in ctrl]))
    out["partial_rho_route_ci95"] = [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]
    # loss that moves the tether instead of removing it
    out["hot_mean_own_loss"] = float(T["own_loss"][hot].mean()) if hot.any() else None
    out["hot_mean_spread"] = float(T["spread"][hot].mean()) if hot.any() else None

    with open(d / "tiles.csv", "w") as f:
        f.write(",".join(T) + ",hot\n")
        for i in range(nt):
            f.write(",".join(f"{T[k][i]:.5g}" for k in T) + f",{int(hot[i])}\n")
    with open(d / "hot.csv", "w") as f:
        f.write("x,y,loss,route,occ,dist\n")
        for i in np.argsort(-T["loss"]):
            if hot[i]:
                f.write(f"{T['x'][i]:.0f},{T['y'][i]:.0f},{T['loss'][i]:.4f},{T['route'][i]:.2f},{T['occ'][i]:.2f},{T['dist'][i]:.1f}\n")
    (d / "summary.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
