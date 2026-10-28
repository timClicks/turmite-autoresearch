# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "polars"]
# ///
"""Matched-area pairs of ../README.md (second registration). No simulation; bootstrap seed 20261015."""
import hashlib
import itertools
import subprocess
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[1]
src = root.parents[2] / "experiments/archive/2026-10-t1-excursion-tomography" / "results"
rng = np.random.default_rng(20261015)
out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s)


seeds = pl.read_csv(src / "t1b_cutoff_seeds.csv").filter(~pl.col("escaped")).with_columns(pl.col("area").log().alias("lnA"))
P("# matched pairs; commit", subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
P("# input sha256[:16]", hashlib.sha256((src / "t1b_cutoff_seeds.csv").read_bytes()).hexdigest()[:16])


def pairs(m, tol):
    r, a, kp, q = m["rule"].to_list(), m["lnA"].to_numpy(), m["lnkappa"].to_numpy(), m["ln_ratio"].to_numpy()
    res = []
    for i, j in itertools.combinations(range(len(r)), 2):
        if abs(a[i] - a[j]) <= tol:
            if kp[i] < kp[j]:
                i, j = j, i
            res.append((i, j, kp[i] - kp[j], q[i] - q[j]))
    return res


def frac(pr, idx_draw=None):
    if not pr:
        return float("nan")
    return float(np.mean([d[3] < 0 for d in pr]))


for tol in (0.05, 0.10):
    P(f"## tolerance |d ln A| <= {tol}" + ("  (registered)" if tol == 0.05 else "  (sensitivity)"))
    for k in (22, 25):
        m = seeds.filter(pl.col("k") == k).group_by("rule").agg(pl.col("lnA").mean(), pl.col("lnkappa").mean(), pl.col("ln_ratio").mean()).sort("rule")
        n = m.height
        allp = [abs(m["lnkappa"][i] - m["lnkappa"][j]) for i, j in itertools.combinations(range(n), 2)]
        pr = pairs(m, tol)
        med_m = float(np.median([d[2] for d in pr])) if pr else float("nan")
        med_a = float(np.median(allp))
        f = frac(pr)
        boots = []
        if len(pr) >= 2:
            for _ in range(2000):
                draw = rng.integers(0, n, n)
                cnt = np.bincount(draw, minlength=n)
                w = np.array([cnt[i] * cnt[j] for i, j, _, _ in pr])
                if w.sum() == 0:
                    continue
                neg = np.array([d[3] < 0 for d in pr])
                boots.append((w * neg).sum() / w.sum())
        lo, hi = (np.percentile(boots, 2.5), np.percentile(boots, 97.5)) if boots else (float("nan"),) * 2
        P(f"k={k} rules={n} pairs={len(pr)}: median|dlnk| matched {med_m:.3f} vs all {med_a:.3f} (ratio {med_m / med_a:.2f}); "
          f"frac higher-kappa has smaller cutoff {f:.3f} cluster-boot95 [{lo:.3f}, {hi:.3f}]")
(root / "results" / "matched_pairs.txt").write_text("\n".join(out) + "\n")
