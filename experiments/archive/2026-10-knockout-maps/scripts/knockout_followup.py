"""Checks after the coarse/refine maps (notes/knockout-map-results.md, 'Follow-up').

1. Tile distance measured from the intact run's mean position (the tether
   centre) instead of the start cell: ring table, hot-tile geometry, and the
   partial rho with the centred distance as an extra control.
2. P4 redone with full tiles only (nvis == 25) against the 25-cell swaps.
3. Fresh permutations (seeds 4-6) for the top 5 refined 5x5 and 3x3 windows.

usage (WSL, repo root): KNOCK=... uv run experiments/archive/2026-10-knockout-maps/scripts/knockout_followup.py
"""
import os
import subprocess
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[2 if lib else 3]
K = os.environ.get("KNOCK", str(ROOT / "target/release/examples/knock"))


def partial(y, x, controls):
    def res(v):
        A = np.column_stack([np.ones(len(v))] + [rankdata(c) for c in controls])
        r = rankdata(v)
        return r - A @ np.linalg.lstsq(A, r, rcond=None)[0]
    return float(np.corrcoef(res(y), res(x))[0, 1])


for rule in ("RRRRRLLLLLL", "RLLLLRRRRLR"):
    d = ROOT
    b = np.genfromtxt(d / f"knockout_{rule}_base.csv", delimiter=",", names=True)
    B, mx, my = float(b["near_home"]), float(b["mx"]), float(b["my"])
    T = np.genfromtxt(d / f"knockout_{rule}_tiles.csv", delimiter=",", names=True)
    cx, cy = T["x"] + 2.5, T["y"] + 2.5
    dc = np.hypot(cx - mx, cy - my)
    hot = T["hot"] == 1
    print(f"\n{rule}: tether centre ({mx:.2f},{my:.2f}); hot tiles {hot.sum()}")
    print("  hot tile centre mean offset from tether centre: (%.1f, %.1f); from start: (%.1f, %.1f)" % (
        (cx[hot] - mx).mean(), (cy[hot] - my).mean(), cx[hot].mean(), cy[hot].mean()))
    ang = np.degrees(np.arctan2(cy[hot] - my, cx[hot] - mx)) % 360
    print("  hot tiles by octant around tether centre (0=east, 90=south):",
          np.histogram(ang, bins=np.arange(0, 361, 45))[0].tolist())
    print("  hot tiles by octant around start cell:",
          np.histogram(np.degrees(np.arctan2(cy[hot], cx[hot])) % 360, bins=np.arange(0, 361, 45))[0].tolist())
    rings = [(0, 10), (10, 15), (15, 20), (20, 30), (30, 80)]
    print("  mean loss by ring about start :", [(a, bb, round(T["loss"][(T["dist"] >= a) & (T["dist"] < bb)].mean(), 4)) for a, bb in rings])
    print("  mean loss by ring about centre:", [(a, bb, round(T["loss"][(dc >= a) & (dc < bb)].mean(), 4)) for a, bb in rings])
    print("  hot tiles by ring about centre :", [int((hot & (dc >= a) & (dc < bb)).sum()) for a, bb in rings])
    ctrl = [np.log1p(T["occ"]), T["dist"], T["dose"]]
    print("  partial rho(route), origin dist (primary): %.3f" % partial(T["loss"], T["route"], ctrl))
    print("  partial rho(route), + centred dist       : %.3f" % partial(T["loss"], T["route"], ctrl + [dc]))
    print("  partial rho(route), centred dist replaces: %.3f" % partial(T["loss"], T["route"], [ctrl[0], dc, ctrl[2]]))
    # P4 with full tiles
    R = np.genfromtxt(d / f"knockout_{rule}_coarse.csv", delimiter=",", names=True, dtype=None, encoding=None)
    sw = B - R["near_home"][R["kind"] == "swap"]
    print("  tiles: mean nvis %.1f, full (nvis==25) %d of %d; mean loss full tiles %.4f vs swaps %.4f (swap dose %.2f, full-tile dose %.2f)" % (
        T["nvis"].mean(), (T["nvis"] == 25).sum(), len(T), T["loss"][T["nvis"] == 25].mean(), sw.mean(),
        R["changed"][R["kind"] == "swap"].mean(), T["dose"][T["nvis"] == 25].mean()))
    # fresh permutations for the top windows
    out = {}
    for nm, w in (("refine5", 5), ("refine3", 3)):
        P = np.genfromtxt(d / f"knockout_{rule}_{nm}.csv", delimiter=",", names=True, dtype=None, encoding=None)
        P = P[P["kind"] == "patch"]
        L = {}
        for r in P:
            L.setdefault((int(r["x"]), int(r["y"])), []).append(B - float(r["near_home"]))
        top = sorted(L, key=lambda k: -np.mean(L[k]))[:5]
        jobs = ROOT / "experiments/archive/2026-10-knockout-maps/knock" / rule / f"fresh{w}.jobs"
        jobs.write_text("\n".join(f"patch,{x},{y},{w},{w},{s}" for (x, y) in top for s in (4, 5, 6)) + "\n")
        csv = jobs.with_suffix(".csv")
        subprocess.run([K, str(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid"), rule, str(1 << 26), "jobs", str(jobs), str(csv)], check=True)
        F = np.genfromtxt(csv, delimiter=",", names=True, dtype=None, encoding=None)
        print(f"  top {w}x{w} windows: selected loss -> fresh-permutation loss")
        for (x, y) in top:
            f = [B - float(r["near_home"]) for r in F if int(r["x"]) == x and int(r["y"]) == y]
            print(f"    ({x},{y}): {np.mean(L[(x, y)]):.3f} -> {np.mean(f):.3f}  ({', '.join(f'{v:.3f}' for v in f)})")
