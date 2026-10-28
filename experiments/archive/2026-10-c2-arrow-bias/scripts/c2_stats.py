# /// script
# dependencies = ["polars", "numpy"]
# ///
"""C2: rotor with north-biased initial arrows. Input experiments/archive/2026-10-c2-arrow-bias/results/c2_probe.csv. Decision rule in notes/frontier-2026-10-13-results.md.
usage: uv run experiments/archive/2026-10-c2-arrow-bias/scripts/c2_stats.py"""
import sys
sys.path.insert(0, "experiments/_lib")
import polars as pl, numpy as np
from analyse_probe import per_rule
raw = pl.read_csv("experiments/archive/2026-10-c2-arrow-bias/results/c2_probe.csv")
esc = raw.group_by("rule").agg(esc=pl.col("escaped").first()).filter(pl.col("esc"))["rule"].to_list()
print("escaped runs:", esc)
pr = per_rule(raw)
pr = pr.with_columns(bias=pl.col("rule").map_elements(lambda s: float(s.split(":")[2]) if s.startswith("brotor") else 0.0, return_dtype=pl.Float64),
                     seed=pl.col("rule").map_elements(lambda s: int(s.split(":")[1]), return_dtype=pl.Int64))
g = pr.group_by("bias").agg(n=pl.len(), w=pl.col("alpha_w").mean(), w_sd=pl.col("alpha_w").std(), a=pl.col("a").mean(), a_sd=pl.col("a").std(),
                            c=pl.col("c").mean(), c_sd=pl.col("c").std(), kappa=pl.col("kappa").mean(), k_sd=pl.col("kappa").std(),
                            beta=pl.col("beta").mean(), g_k=pl.col("g_k").mean(), spread=pl.col("spread").mean()).sort("bias")
pl.Config.set_tbl_cols(20); pl.Config.set_float_precision(4); pl.Config.set_tbl_width_chars(220)
print(g)
rk = lambda v: np.argsort(np.argsort(v))
b = g["bias"].to_numpy(); k = g["kappa"].to_numpy()
print("Spearman(kappa, bias) over conditions:", round(float(np.corrcoef(rk(b), rk(k))[0, 1]), 2))
r0 = pr.filter(pl.col("bias") == 0.0); r9 = pr.filter(pl.col("bias") == pr["bias"].max())
for col in ("kappa", "c", "alpha_w"):
    d = r9[col].mean() - r0[col].mean(); se = np.hypot(r9[col].std() / np.sqrt(r9.height), r0[col].std() / np.sqrt(r0.height))
    print(f"  {col}: bias 0.9 minus control = {d:+.4f} ({d/se:.1f} SE of the mean, between-seed)")
