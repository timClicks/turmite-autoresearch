# /// script
# dependencies = ["numpy", "polars", "scipy"]
# ///
"""Post hoc: mean ln-kappa residual (after ln A(22) spline) by leading-run length, census vs pool.
usage: uv run experiments/archive/2026-10-kappa-prefix-decode/scripts/leadrun_table.py"""
import sys
from pathlib import Path
import numpy as np, polars as pl

HERE = Path(__file__).resolve().parent
KR = HERE.parents[3] / "experiments/archive/2026-10-kappa-rule-space/scripts"
sys.path.insert(0, str(KR))
from kcommon import census, per_rule, rule_means  # noqa: E402
from prefix_audit import basis, predict  # noqa: E402

raw = pl.read_csv(KR.parent / "dumps/w3c_probe.csv")
runs = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
runs = runs.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
fresh = rule_means(runs.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0)), 6)
cen = census().filter((pl.col("kappa") > 0) & pl.col("lnA22").is_not_null()).sort("rule")
tr = cen.filter(pl.col("g_k").abs() < .05)
te = fresh.filter(pl.col("g_k").abs() < .05)
y, v = np.log(tr["kappa"].to_numpy()), te["lnk"].to_numpy()
xa, za = basis(tr["lnA22"].to_numpy(), te["lnA22"].to_numpy(), True)
rtr, rte = y - predict(xa, y, xa), v - predict(xa, y, za)
lead = lambda s: len(s) - len(s.lstrip(s[0]))
ltr = np.array([lead(s) for s in tr["rule"]]); lte = np.array([lead(s) for s in te["base"]])
print(f"{'lead':>4} {'n_census':>8} {'mean_res':>9} {'sd':>6} {'n_pool':>6} {'mean_res':>9} {'sd':>6}")
for k in range(1, 9):
    m1, m2 = ltr == k, lte == k
    f = lambda r, m: (f"{r[m].mean():+9.3f} {r[m].std():6.2f}" if m.sum() > 1 else f"{'':>16}")
    print(f"{k:>4} {m1.sum():>8} {f(rtr, m1)} {m2.sum():>6} {f(rte, m2)}")
m1, m2 = ltr >= 9, lte >= 9
print(f">=9  {m1.sum():>8} {rtr[m1].mean() if m1.sum() else float('nan'):+9.3f}        {m2.sum():>6}")
print("corr(lead, residual): census %.3f pool %.3f" % (np.corrcoef(ltr, rtr)[0, 1], np.corrcoef(lte, rte)[0, 1]))
print("corr(lead, ln A22): census %.3f" % np.corrcoef(ltr, tr["lnA22"].to_numpy())[0, 1])
