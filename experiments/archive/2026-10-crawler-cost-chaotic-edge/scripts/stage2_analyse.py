"""Stage 2 registered scoring (README: S1-S4). -> results/stage2_analysis.txt, stage2_analysis.json, stage2_rules.csv

usage: uv run --frozen experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/stage2_analyse.py
"""
import json
from pathlib import Path

import numpy as np
import polars as pl

RES = Path(__file__).resolve().parents[1] / "results"
SEED, NB = 20261026, 2000
E3, RHO, PSI = 1.121488436069519, 0.6921567990007209, 0.16
out = []


def say(s=""):
    print(s)
    out.append(s)


def k3(r):
    phi = [1.0 if r[j] == r[0] else PSI for j in range(len(r))]
    return E3 + RHO * sum(np.prod(phi[1:k]) for k in range(1, min(len(r) - 1, 12) + 1))


def LL(m):
    return 1.363 + 0.696 * min(m, 8)


def why(d):
    if d["escaped"]:
        return "escaped"
    if d["births"] < 200:
        return "births<200"
    g = d["area"] / d["area_t0"]
    return "ratio>1.9" if g > 1.9 else ("ratio<1.3" if g < 1.3 else "kept")


tr = {d["spec"]: d for d in map(json.loads, (RES / "trace_s2.jsonl").read_text().splitlines())}
coh = pl.read_csv(RES / "lists/s2_cohort.csv")
rows = []
for r, c, m, n in coh.iter_rows():
    d = tr[r]
    rows.append({"rule": r, "control": c or "", "m": m, "n": n, "status": why(d), "inv_c": d["boundary_steps"] / max(d["births"], 1),
                 "k3": k3(r), "c_status": why(tr[c]) if c else "", "c_inv_c": tr[c]["boundary_steps"] / max(tr[c]["births"], 1) if c else None})
df = pl.DataFrame(rows).with_columns(((pl.col("inv_c") - pl.col("m").map_elements(LL, return_dtype=pl.Float64)) /
                                      (pl.col("m") + 1.25 - pl.col("m").map_elements(LL, return_dtype=pl.Float64))).alias("phi"))
df.write_csv(RES / "stage2_rules.csv")
say("Stage 2: fresh Pi(m) rules, n 13..18 (blank 24 4096); filter outcome by m (Pi rules | controls)")
for (m,), g in df.group_by("m", maintain_order=True):
    a = dict(g.group_by("status").len().iter_rows())
    b = dict(g.filter(pl.col("control") != "").group_by("c_status").len().iter_rows())
    say(f"  m={m}: Pi {a} | controls {b}")
k = df.filter(pl.col("status") == "kept")
scored = [m for m in range(2, 7) if k.filter(pl.col("m") == m).height >= 6]
say(f"  scored m (>= 6 kept Pi rules): {scored}")


def slope(x, y):
    return np.polyfit(x, y, 1)[0]


x, y = k["m"].to_numpy().astype(float), k["inv_c"].to_numpy()
s_pi = slope(x, y)
pairs = k.filter((pl.col("control") != "") & (pl.col("c_status") == "kept"))
xp, yp, yc = pairs["m"].to_numpy().astype(float), pairs["inv_c"].to_numpy(), pairs["c_inv_c"].to_numpy()
s_pp, s_c = slope(xp, yp), slope(xp, yc)
rng = np.random.default_rng(SEED)
bs = []
for _ in range(NB):
    i = rng.integers(0, len(xp), len(xp))
    bs.append(slope(xp[i], yp[i]) - slope(xp[i], yc[i]))
lo, hi = np.percentile(bs, [2.5, 97.5])
s1 = 0.85 <= s_pi <= 1.10 and (s_pp - s_c) >= 0.10 and lo > 0
say(f"S1: slope of 1/c on m, kept Pi (n={len(x)}): {s_pi:.3f}; paired subset (n={len(xp)}): Pi {s_pp:.3f}, controls {s_c:.3f}, "
    f"difference {s_pp - s_c:.3f} [{lo:.3f}, {hi:.3f}] -> {'HELD' if s1 else 'FAILED'}")
s2 = True
for m in scored:
    g = k.filter(pl.col("m") == m)
    mp = g["phi"].median()
    s2 &= mp >= 0.5
    cc = pairs.filter(pl.col("m") == m)["c_inv_c"]
    say(f"  m={m}: kept {g.height}, median 1/c {g['inv_c'].median():.3f} (LL {LL(m):.3f}, K3 {g['k3'].median():.3f}, crawler {m + 1.25}), "
        f"median phi {mp:.3f}; paired controls median 1/c {cc.median() if len(cc) else float('nan'):.3f} (n={len(cc)})")
say(f"S2: {'HELD' if s2 else 'FAILED'}")
hi_m = k.filter(pl.col("m").is_in([4, 5, 6]) & pl.col("m").is_in(scored))
r_hi = (hi_m["inv_c"] - hi_m["k3"]).median()
g2 = k.filter(pl.col("m") == 2)
r_2 = (g2["inv_c"] - g2["k3"]).median()
s3 = r_hi >= 0.25 and abs(r_2) <= 0.10
say(f"S3: median 1/c - K3: m in {{4,5,6}} (scored, n={hi_m.height}) {r_hi:+.3f}; m=2 (n={g2.height}) {r_2:+.3f} -> {'HELD' if s3 else 'FAILED'}")
over = k.filter(pl.col("inv_c") > pl.col("m") + 1.35)
s4 = over.height <= 0.10 * k.height
say(f"S4: {over.height} of {k.height} kept Pi rules exceed m + 5/4 + 0.10 -> {'HELD' if s4 else 'FAILED'}")
(RES / "stage2_analysis.txt").write_text("\n".join(out) + "\n")
(RES / "stage2_analysis.json").write_text(json.dumps({"slope_pi": s_pi, "slope_pair_pi": s_pp, "slope_ctrl": s_c, "diff_ci": [lo, hi],
                                                      "S1": bool(s1), "S2": bool(s2), "S3": [r_hi, r_2, bool(s3)], "S4": bool(s4),
                                                      "scored_m": scored}, indent=1) + "\n")
