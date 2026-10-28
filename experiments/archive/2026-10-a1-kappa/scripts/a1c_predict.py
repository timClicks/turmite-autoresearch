# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A1c (exploratory, after A1b): predict the rule-mean kappa (core band, b2_probe + item21 + patched rules, >= 6 runs) from the rule string.
Models, leave-one-rule-out R^2 on log kappa: (1) ridge on one-hot letter-by-position (<= 12 positions) + n; (2) prefix nearest-neighbour (first 5 letters match); (3) ridge on counts of 2-letter and 3-letter substrings (cyclic).
usage: uv run experiments/archive/2026-10-a1-kappa/scripts/a1c_predict.py"""
import sys, itertools
sys.path.insert(0, "experiments/_lib")
import numpy as np, polars as pl
from analyse_probe import per_rule
rs = []
for p in ("experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv", "experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv", "experiments/archive/2026-10-patched-starts/results/patched.csv"):
    r = per_rule(pl.read_csv(p)).with_columns(base=pl.col("rule").str.split("@").list.first()); rs.append(r.select("base", "alpha_w", "kappa"))
r = pl.concat(rs).filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0)).group_by("base").agg(k=pl.col("kappa").log().mean(), n=pl.len()).filter(pl.col("n") >= 6)
rules = r["base"].to_list(); y = r["k"].to_numpy(); N = len(rules)
def onehot(s):
    v = np.zeros(12 * 2 + 2); 
    for i, ch in enumerate(s[:12]): v[2 * i + (ch == "R")] = 1
    v[24] = len(s); v[25] = s.count("R") / len(s); return v
def subs(s, L):
    t = s + s[:L - 1]; keys = ["".join(p) for p in itertools.product("RL", repeat=L)]
    return np.array([sum(t[i:i + L] == k for i in range(len(s))) for k in keys], float)
def loo_ridge(X, lam):
    X = (X - X.mean(0)) / (X.std(0) + 1e-9); pred = np.zeros(N)
    for i in range(N):
        tr = np.arange(N) != i; A = X[tr]; b = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ (y[tr] - y[tr].mean())); pred[i] = X[i] @ b + y[tr].mean()
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
print(f"rules with >= 6 core-band runs: {N}; sd of rule-mean log kappa {y.std():.3f}")
for lam in (1, 10, 30):
    print(f"ridge lam={lam}: letter-by-position LOO R^2 {loo_ridge(np.array([onehot(s) for s in rules]), lam):+.3f}; 2-/3-letter substring counts {loo_ridge(np.array([np.r_[subs(s,2), subs(s,3)] for s in rules]), lam):+.3f}")
pred = np.zeros(N)
for i in range(N):
    m = [j for j in range(N) if j != i and rules[j][:5] == rules[i][:5]]
    pred[i] = y[m].mean() if m else y[np.arange(N) != i].mean()
print(f"prefix-5 neighbour mean LOO R^2 {1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum():+.3f}")
