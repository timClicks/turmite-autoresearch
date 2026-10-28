# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "scipy"]
# ///
"""Synthetic calibration of the REML + split-seed pipeline (registered in ../README.md, criterion C). Seed 20261016."""
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mixed as M

root = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(20261016)
out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s, flush=True)


def synth(br_true, sK=0.0, sA=0.0, su=0.30, se=0.13, sr=0.20, bA=0.3, nrules=44):
    """Latent rule residual r_true (sd sr); response = bA*zA + br*r_true/sr + u + e; covariates observed with per-seed noise."""
    A = rng.normal(0, 0.8, nrules)
    r = rng.normal(0, sr, nrules)
    K = 0.5 + 1.2 * A + r
    u = rng.normal(0, su, nrules)
    rules = []
    for i in range(nrules):
        n = int(rng.integers(6, 9))
        seed = np.arange(n)
        mu = bA * (A[i] / 0.8) + br_true * (r[i] / sr) + u[i]
        rules.append({"name": str(i), "k": {22: dict(
            seed=seed, lnA=A[i] + rng.normal(0, sA, n), lk=K[i] + rng.normal(0, sK, n), q=mu + rng.normal(0, se, n))}})
    return rules


P("# calibrate.py; commit", subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
NS, B = 300, 200
for label, br_true, sK, sA in [("noise-free covariates, br=-0.5", -0.5, 0.0, 0.0),
                               ("noise-free covariates, br=0 (null)", 0.0, 0.0, 0.0),
                               ("noisy covariates (seed sd lnk 0.089, lnA 0.10), br=-0.5", -0.5, 0.089, 0.10)]:
    est, std_, su, se, cover, rej, two = [], [], [], [], [], [], []
    for s in range(NS):
        rules = synth(br_true, sK, sA)
        sp = M.random_split(rules, rng)
        f = M.fit_direction(rules, sp, 22, "A", True)
        est.append(f["b"][2])
        su.append(np.sqrt(f["su2"]))
        se.append(np.sqrt(f["se2"]))
        br, _, _ = M.boot_br(rules, 22, rng, B)
        lo, hi = np.percentile(br, [2.5, 97.5])
        cover.append(lo <= br_true <= hi)
        rej.append(not (lo <= 0 <= hi))
    est = np.array(est)
    P(f"## {label}: {NS} datasets, bootstrap B={B}")
    P(f"  br estimate mean {est.mean():.3f} (truth {br_true}), sd {est.std(ddof=1):.3f}; ratio est/truth "
      + (f"{est.mean()/br_true:.3f}" if br_true else "n/a"))
    P(f"  s_u mean {np.mean(su):.3f} (truth 0.30), s_e mean {np.mean(se):.3f} (truth 0.13)")
    P(f"  bootstrap 95% CI covers the true br: {np.mean(cover):.3f};  CI excludes 0: {np.mean(rej):.3f}")

(root / "results" / "calibration.txt").write_text("\n".join(out) + "\n")
