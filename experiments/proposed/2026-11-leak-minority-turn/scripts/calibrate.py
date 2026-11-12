"""Synthetic calibration of the P1 and P2 decision rules (no held-out ant data is read).

usage (repo root): uv run --frozen python experiments/proposed/2026-11-leak-minority-turn/scripts/calibrate.py
Writes results/calibration.txt.

Development data only: the committed leak-handedness cohort C (results/rules.csv there, 77 rules) gives the slope b_dev
of Lambda on (R fraction - 1/2) by least squares and the residual sd. Held-out R fractions are taken from the drawn
cohort H's rule strings (results/rules.txt; composition only, no outcome). Model per synthetic rule:
Lambda = b (fr - 1/2) + N(0, resid_sd) + N(0, 0.05) seed noise, b in {b_dev, b_dev/2, 0}, n in {50, 70, 90} rules
sampled from H's R fractions with replacement. Decision rules exactly as registered in the README.
"""
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
dev = pl.read_csv(ROOT / "experiments/active/2026-11-leak-handedness-cohort/results/rules.csv").sort("rule")
dev = dev.filter(pl.col("scoreable"))
x = np.array([r.count("R") / len(r) - 0.5 for r in dev["rule"]])
y = dev["lam"].to_numpy()
b_dev = float(np.sum((x - x.mean()) * (y - y.mean())) / np.sum((x - x.mean()) ** 2))
resid = y - (y.mean() + b_dev * (x - x.mean()))
rsd = float(resid.std(ddof=2))
H = [ln.split()[1] for ln in (EXP / "results/rules.txt").read_text().splitlines() if ln.startswith("H ")]
frH = np.array([r.count("R") / len(r) for r in H])
rng = np.random.default_rng(20261113)
DRAWS, B = 1000, 2000



def ranks(v: np.ndarray) -> np.ndarray:
    o = np.argsort(v, kind="stable")
    r = np.empty(v.size)
    r[o] = np.arange(v.size)
    for u in np.unique(v):  # average ties
        m = v == u
        r[m] = r[m].mean()
    return r


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra, rb = ranks(a), ranks(b)
    return float(np.corrcoef(ra, rb)[0, 1])


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    z, p = 1.959964, k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (c - h, c + h)


def rowranks(M: np.ndarray) -> np.ndarray:
    """Average ranks along each row (ties averaged), vectorised by offsetting rows."""
    n = M.shape[1]
    off = (np.arange(M.shape[0])[:, None] * (np.ptp(M) + 1.0) * 4 + M).ravel()
    s = np.sort(off)
    lo = np.searchsorted(s, off, "left")
    hi = np.searchsorted(s, off, "right")
    return ((lo + hi - 1) / 2.0).reshape(M.shape) - (np.arange(M.shape[0]) * n)[:, None]


def boot_spearman(lam: np.ndarray, fr: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    idx = rng.integers(0, lam.size, size=(B, lam.size))
    ra, rb = rowranks(lam[idx]), rowranks(fr[idx])
    ra -= ra.mean(1, keepdims=True)
    rb -= rb.mean(1, keepdims=True)
    den = np.sqrt((ra * ra).sum(1) * (rb * rb).sum(1))
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (ra * rb).sum(1) / den
    return r[~np.isnan(r)]


def p1(lam: np.ndarray, fr: np.ndarray, rng: np.random.Generator) -> str:
    boot = boot_spearman(lam, fr, rng)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    if lo > 0:
        return "replicates"
    if hi < 0.20:
        return "fails"
    return "unresolved"


def p2(lam: np.ndarray, fr: np.ndarray) -> str:
    m = (fr != 0.5) & (np.abs(lam) >= 0.10)
    k = int(np.sum(np.sign(lam[m]) == np.sign(fr[m] - 0.5)))
    lo, hi = wilson(k, int(m.sum()))
    if lo > 0.5:
        return "holds"
    if hi < 0.60:
        return "fails"
    return "unresolved"


out = [f"# dev cohort C (n {y.size}): b_dev {b_dev:+.3f} per unit R fraction, residual sd {rsd:.3f}; "
       f"dev Spearman {spearman(y, x):+.3f}",
       f"# held-out R fractions from {frH.size} drawn rules; {DRAWS} draws, {B} bootstrap resamples, seed 20261113"]
for n in (50, 70, 90):
    for lab, b in (("b_dev", b_dev), ("b_dev/2", b_dev / 2), ("0", 0.0)):
        c1: dict[str, int] = {}
        c2: dict[str, int] = {}
        for _ in range(DRAWS):
            fr = rng.choice(frH, size=n, replace=True)
            lam = b * (fr - 0.5) + rng.normal(0, rsd, n) + rng.normal(0, 0.05, n)
            k1, k2 = p1(lam, fr, rng), p2(lam, fr)
            c1[k1] = c1.get(k1, 0) + 1
            c2[k2] = c2.get(k2, 0) + 1
        line = (f"n {n} slope {lab}: P1 " + ", ".join(f"{k} {v / DRAWS:.3f}" for k, v in sorted(c1.items()))
                + " | P2 " + ", ".join(f"{k} {v / DRAWS:.3f}" for k, v in sorted(c2.items())))
        print(line, flush=True)
        out.append(line)
(EXP / "results/calibration.txt").write_text("\n".join(out) + "\n")
