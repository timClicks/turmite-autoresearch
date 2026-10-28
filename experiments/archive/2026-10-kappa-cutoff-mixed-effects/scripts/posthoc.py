# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""POST HOC, exploratory (not registered; added after fit.py failed P1-P4). Two robustness variants of the same pipeline.
 quiet: per k, drop rules whose all-seed sd of ln_ratio > 0.5 (bursty/censored rules; the cut is on response dispersion, not on its mean).
 rank : ln_ratio replaced by its normal score (rank-based) within each k across all windows.
Seed 20261016. Not used to overturn the registered verdict."""
import copy, hashlib, subprocess, sys
from pathlib import Path
import numpy as np, polars as pl
from scipy.stats import norm, rankdata
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mixed as M

root = Path(__file__).resolve().parents[1]
src = root.parents[2] / "experiments/archive/2026-10-t1-excursion-tomography" / "results" / "t1b_cutoff_seeds.csv"
rng = np.random.default_rng(20261016)
out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s, flush=True)
df = pl.read_csv(src).filter(~pl.col("escaped")).with_columns(pl.col("area").log().alias("lnA")).sort("rule", "k", "seed")
P("# posthoc.py (exploratory); commit", subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
P("# input sha256[:16]", hashlib.sha256(src.read_bytes()).hexdigest()[:16])
KS = (22, 25)
def build(df, k):
    rs = []
    for name in sorted(df["rule"].unique().to_list()):
        d = df.filter((pl.col("rule") == name) & (pl.col("k") == k))
        rs.append({"name": name, "k": {k: dict(seed=d["seed"].to_numpy(), lnA=d["lnA"].to_numpy(), lk=d["lnkappa"].to_numpy(), q=d["ln_ratio"].to_numpy())}})
    return rs
B, NPERM = 1000, 1000
for k in KS:
    base = build(df, k)
    sds = np.array([r["k"][k]["q"].std(ddof=1) for r in base])
    variants = {"quiet": [r for r, s in zip(base, sds) if s <= 0.5]}
    rk = copy.deepcopy(base)
    allq = np.concatenate([r["k"][k]["q"] for r in rk])
    ns = norm.ppf((rankdata(allq) - 0.5) / len(allq)); o = 0
    for r in rk:
        n = len(r["k"][k]["q"]); r["k"][k]["q"] = ns[o:o + n]; o += n
    variants["rank"] = rk
    for name, rules in variants.items():
        par = M.parity_split(rules)
        f1 = M.fit_direction(rules, par, k, "A", True); f0 = M.fit_direction(rules, par, k, "A", False)
        d2 = M.r2_oos(rules, par, k, f1, True) - M.r2_oos(rules, par, k, f0, False)
        fB = M.fit_direction(rules, par, k, "B", True)
        bb, bs, bd = M.boot_br(rules, k, rng, B, "A", True)
        A_, K_ = M.covariates(rules, par, k, "X"); zA, zr = M.apply_tf(M.make_tf(A_, K_), A_, K_)
        gi, q = M.response_rows(rules, par, k, "Y")
        pv = [M.reml(q, np.column_stack([np.ones(len(gi)), zA[gi], zr[rng.permutation(len(zr))][gi]]), gi)["b"][2] for _ in range(NPERM)]
        p = (1 + np.sum(np.abs(pv) >= abs(f1["b"][2]))) / (NPERM + 1)
        c = np.percentile(bs, [2.5, 97.5])
        P(f"k={k} {name}: rules {len(rules)}; A: br={f1['b'][2]:.4f} Std={f1['b'][2]/f1['ysd']:.3f} boot Std95 [{c[0]:.3f},{c[1]:.3f}]; "
          f"s_u={np.sqrt(f1['su2']):.3f} s_e={np.sqrt(f1['se2']):.3f}; dR2 {d2:+.3f} frac>0 {np.mean(bd>0):.3f}; perm p {p:.4f}; B: Std={fB['b'][2]/fB['ysd']:.3f}")
(root / "results" / "posthoc.txt").write_text("\n".join(out) + "\n")
