# /// script
# dependencies = ["polars", "numpy"]
# ///
"""POST HOC, unregistered. Where does the lead slope of 1/c live, by colour and by return lag?
usage: uv run experiments/archive/2026-10-lattice-c-law-colours/scripts/explore.py   (after analyse.py; reads results/traces.jsonl)
For kept rules (kept list = rules with a row in results/kept.txt written by analyse.py is not used; the kept set is rebuilt by
importing nothing: this script uses all non-escaped rules with births>0 and lead 2..5 and says so)."""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
out = []


def say(s=""):
    print(s)
    out.append(s)


def lead_of(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


rows = [json.loads(l) for l in (HERE / "results" / "traces.jsonl").read_text().splitlines()]
rows = [d for d in rows if not d["escaped"] and d["births"] > 0 and d["boundary_steps"] > 0]
say(f"non-escaped rules with births>0: {len(rows)} (NOT the kept set: no blob filter; medians below are robust to the odd rule)")
for lat, s0 in [("square", "R"), ("tri", "R"), ("hex", "R"), ("hex", "r")]:
    g = [d for d in rows if d["lattice"] == lat and d["rule"][0] == s0]
    ell = g[0]["loop_len"]
    say(f"\n== {lat}/{s0}  ell={ell}  n={len(g)}")
    say("lead  n  | per-birth boundary reads by colour group: c0   circ(1..m-1)  kill(m)  later(>m) | total | lag-ell share of circ reads | lag-ell share of all colour>=1 reads")
    tab = {}
    for m in range(1, 6):
        gm = [d for d in g if lead_of(d["rule"]) == m]
        if len(gm) < 3:
            continue
        c0, circ, kill, later, tot, lagf, lagall = [], [], [], [], [], [], []
        for d in gm:
            b = d["births"]
            e = np.array(d["edge"], float)
            c0.append(e[0] / b)
            circ.append(e[1:m].sum() / b)
            kill.append(e[m] / b)
            later.append(e[m + 1:].sum() / b)
            tot.append(e.sum() / b)
            lag = np.array(d["lag"], float)  # [colour bucket 0..7][lag 0..40]
            if m >= 2:
                cc = lag[1:min(m, 8)].sum()
                lagf.append(lag[1:min(m, 8), ell].sum() / cc if cc else np.nan)
            ca = lag[1:].sum()
            lagall.append(lag[1:, ell].sum() / ca if ca else np.nan)
        md = lambda v: float(np.nanmedian(v)) if len(v) else float("nan")
        tab[m] = [md(c0), md(circ), md(kill), md(later), md(tot)]
        say(f"{m:3d} {len(gm):3d}  | {md(c0):6.3f} {md(circ):8.3f} {md(kill):8.3f} {md(later):8.3f} | {md(tot):6.3f} | {md(lagf):6.3f} | {md(lagall):6.3f}")
    ms = sorted(tab)
    if len(ms) >= 3:
        for j, name in enumerate(["c0", "circ", "kill", "later", "total"]):
            sl = np.polyfit(ms, [tab[m][j] for m in ms], 1)[0]
            say(f"   slope of median {name:5} vs lead: {sl:7.3f}")
Path(HERE / "results" / "explore.txt").write_text("\n".join(out) + "\n")
