# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "polars"]
# ///
"""Seed-noise floor for the matched pairs (third registration in ../README.md). No simulation; bootstrap seed 20261016."""
import hashlib
import itertools
import subprocess
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[1]
src = root.parents[2] / "experiments/archive/2026-10-t1-excursion-tomography" / "results"
rng = np.random.default_rng(20261016)
out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s)


seeds = pl.read_csv(src / "t1b_cutoff_seeds.csv").filter(~pl.col("escaped")).with_columns(pl.col("area").log().alias("lnA"))
P("# noise floor; commit", subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
P("# input sha256[:16]", hashlib.sha256((src / "t1b_cutoff_seeds.csv").read_bytes()).hexdigest()[:16])


def boot_frac(neg, pi, pj, n, B=2000):
    """Rule-cluster bootstrap of the fraction of pairs with neg=True (pair weight = product of rule multiplicities)."""
    if len(neg) < 2:
        return float("nan"), float("nan")
    neg = np.asarray(neg)
    pi, pj = np.asarray(pi), np.asarray(pj)
    b = []
    for _ in range(B):
        cnt = np.bincount(rng.integers(0, n, n), minlength=n)
        w = cnt[pi] * cnt[pj]
        if w.sum() == 0:
            continue
        b.append((w * neg).sum() / w.sum())
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


for tol in (0.05, 0.10):
    P(f"## tolerance |d ln A| <= {tol}" + ("  (registered)" if tol == 0.05 else "  (sensitivity)"))
    for k in (22, 25):
        d = seeds.filter(pl.col("k") == k)
        g = d.group_by("rule").agg(
            pl.col("lnA").mean(), pl.col("lnkappa").mean(), pl.col("ln_ratio").mean(),
            pl.col("lnkappa").std().alias("sk"), pl.col("ln_ratio").std().alias("sq"), pl.len().alias("n"),
        ).sort("rule")
        n = g.height
        a, kp, q = g["lnA"].to_numpy(), g["lnkappa"].to_numpy(), g["ln_ratio"].to_numpy()
        sk, sq, ns = g["sk"].to_numpy(), g["sq"].to_numpy(), g["n"].to_numpy()
        idx = {r: i for i, r in enumerate(g["rule"].to_list())}
        pr = []
        for i, j in itertools.combinations(range(n), 2):
            if abs(a[i] - a[j]) <= tol:
                if kp[i] < kp[j]:
                    i, j = j, i
                pr.append((i, j))
        pi = [p[0] for p in pr]
        pj = [p[1] for p in pr]
        dk = np.array([kp[i] - kp[j] for i, j in pr])
        dq = np.array([q[i] - q[j] for i, j in pr])
        se = np.array([np.sqrt(sk[i] ** 2 / ns[i] + sk[j] ** 2 / ns[j]) for i, j in pr])
        z = dk / se
        P(f"k={k}: rules={n} seeds/rule median {np.median(ns):.0f} (min {ns.min()}, max {ns.max()}) pairs={len(pr)}")
        P(f"  N1 median seed sd ln kappa {np.nanmedian(sk):.3f} (ln_ratio {np.nanmedian(sq):.3f}); "
          f"median pair SE {np.median(se):.3f}; median |dlnk| {np.median(dk):.3f}; "
          f"frac z>2 {np.mean(z > 2):.3f} (n={int((z > 2).sum())}), z>3 {np.mean(z > 3):.3f}")
        m2 = z > 2
        neg2 = dq[m2] < 0
        lo, hi = boot_frac(neg2, np.array(pi)[m2], np.array(pj)[m2], n)
        P(f"  N2 P-b restricted to z>2: pairs={int(m2.sum())} frac {np.mean(neg2) if m2.any() else float('nan'):.3f} boot95 [{lo:.3f}, {hi:.3f}]")
        m1 = ~m2
        neg1 = dq[m1] < 0
        P(f"     complement z<=2: pairs={int(m1.sum())} frac {np.mean(neg1) if m1.any() else float('nan'):.3f}")
        # N3: kappa from even seeds, ln_ratio from odd seeds (seed index parity), pairs fixed by the full-seed matching
        ev = d.filter(pl.col("seed") % 2 == 0).group_by("rule").agg(pl.col("lnkappa").mean().alias("ke"), pl.len().alias("ne"))
        od = d.filter(pl.col("seed") % 2 == 1).group_by("rule").agg(pl.col("ln_ratio").mean().alias("qo"), pl.len().alias("no"))
        h = ev.join(od, on="rule").filter((pl.col("ne") >= 2) & (pl.col("no") >= 2))
        dropped = n - h.height
        ke = {r: v for r, v in zip(h["rule"], h["ke"])}
        qo = {r: v for r, v in zip(h["rule"], h["qo"])}
        names = g["rule"].to_list()
        neg3, p3i, p3j = [], [], []
        for i, j in pr:
            ri, rj = names[i], names[j]
            if ri in ke and rj in ke:
                hi_, lo_ = (ri, rj) if ke[ri] >= ke[rj] else (rj, ri)
                neg3.append(qo[hi_] - qo[lo_] < 0)
                p3i.append(idx[hi_])
                p3j.append(idx[lo_])
        lo3, hi3 = boot_frac(neg3, p3i, p3j, n)
        P(f"  N3 split-seed (kappa even, ln_ratio odd; rules dropped {dropped}): pairs={len(neg3)} "
          f"frac {np.mean(neg3) if neg3 else float('nan'):.3f} boot95 [{lo3:.3f}, {hi3:.3f}]")
(root / "results" / "noise_floor.txt").write_text("\n".join(out) + "\n")
