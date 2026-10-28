# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A1 proxy (NOT the half-plane model): how much of the across-rule variance of kappa is carried by the rule string alone?
Linear model on q = #R/n, n, letters 1..6 (R=1), run count, trained on a random half (seed 20261013) of the non-bursty blob rules of
probe_summary.csv, scored on the other half. Compare the c model's held-out R^2 = 0.66 (experiments/archive/2026-10-probe-growth-census/scripts/c_model.py).
usage: uv run experiments/archive/2026-10-a1-kappa/scripts/a1_kappa_proxy.py"""
import re, numpy as np, polars as pl
s = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter((~pl.col("bursty")) & (pl.col("cls") == "blob")).select("rule", "n", "c", "kappa", "g_k")
rules = s["rule"].to_list()
def feat(r):
    f = [1.0, r.count("R") / len(r), len(r), len(re.findall(r"R+|L+", r))]
    f += [1.0 if (len(r) > k and r[k] == "R") else 0.0 for k in range(1, 7)]
    return f
X = np.array([feat(r) for r in rules]); out = {}
rng = np.random.default_rng(20261013); idx = rng.permutation(len(rules)); h = len(idx) // 2; tr, te = idx[:h], idx[h:]
for col in ("kappa", "c", "g_k"):
    y = s[col].to_numpy(); beta = np.linalg.lstsq(X[tr], y[tr], rcond=None)[0]; yh = X[te] @ beta
    r2 = 1 - ((y[te] - yh) ** 2).sum() / ((y[te] - y[te].mean()) ** 2).sum()
    print(f"{col}: n_train {len(tr)}, n_test {len(te)}; held-out R^2 of the letter model = {r2:.3f}; sd of y {y.std():.3f}")
q = X[:, 1]; k = s["kappa"].to_numpy()
print("Spearman(kappa, q) =", round(float(np.corrcoef(np.argsort(np.argsort(q)), np.argsort(np.argsort(k)))[0, 1]), 3), "; kappa median", round(float(np.median(k)), 3), "iqr", np.round(np.quantile(k, [.25, .75]), 3).tolist())
