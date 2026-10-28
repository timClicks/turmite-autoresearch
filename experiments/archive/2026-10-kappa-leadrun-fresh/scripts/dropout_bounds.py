# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Proposal 2 (README): bound arm-E/S/C attrition bias in mutant mean d = dln kappa. No new runs; reads committed results only.
Post hoc / unregistered. Dropped-mutant reasons are NOT recoverable from committed files (need gitignored dumps), so all dropped
mutants are treated alike. Bounds: (i) IPW by base lead x rule length within arm, (ii) Manski worst case imputing the dropped
at the 5th/95th percentile (and min/max) of kept d from the same arm. Denominator: mutants whose base is stationary-fresh.
usage (repo root): uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/dropout_bounds.py"""
from pathlib import Path
import numpy as np, polars as pl

EXP = Path(__file__).resolve().parents[1]
SEED, NB = 20261016, 2000
rng = np.random.default_rng(SEED + 31)
mut = pl.read_csv(EXP / "results/mutants.csv")
fr = pl.read_csv(EXP / "results/fresh_rules.csv")
pr = pl.read_csv(EXP / "results/mutant_pairs.csv").filter(pl.col("kept")).select("mutant", "d")
base_ok = mut.join(fr.select("rule"), left_on="base", right_on="rule", how="inner")
allm = (base_ok.join(pr, on="mutant", how="left")
        .with_columns(got=pl.col("d").is_not_null(), len=pl.col("mutant").str.len_chars()))
out = [f"# cmd: uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/dropout_bounds.py  seed {SEED}  (post hoc, unregistered)",
       f"mutants with fresh base {allm.height}; observed pairs {int(allm['got'].sum())}"]


def boot(x, f):
    x = np.asarray(x)
    return [float(q) for q in np.quantile([f(x[rng.integers(0, len(x), len(x))]) for _ in range(NB)], [.025, .975])]


for arm in "ESC":
    a = allm.filter(pl.col("arm") == arm)
    k = a.filter(pl.col("got"))
    d = k["d"].to_numpy()
    n, nk = a.height, k.height
    # IPW: weight n/nk within (base_lead, len) cell; cells with no observed pairs cannot be reweighted and are reported
    cells = a.group_by("base_lead", "len").agg(n=pl.len(), nk=pl.col("got").sum())
    kk = k.join(cells, on=["base_lead", "len"]).with_columns(w=pl.col("n") / pl.col("nk"))
    ipw = float((kk["d"] * kk["w"]).sum() / kk["w"].sum())
    lost = int(cells.filter(pl.col("nk") == 0)["n"].sum())
    dw, ww = kk["d"].to_numpy(), kk["w"].to_numpy()
    idx = np.arange(len(dw))
    ipw_ci = boot(idx, lambda i: float((dw[i.astype(int)] * ww[i.astype(int)]).sum() / ww[i.astype(int)].sum()))
    nci = boot(d, np.mean)
    m = float(d.mean())
    lo, hi = np.quantile(d, [.05, .95])
    f = (n - nk) / n
    out.append(f"arm {arm}: n={n} kept={nk} retention={nk/n:.2f} naive mean d={m:+.3f} CI [{nci[0]:+.3f},{nci[1]:+.3f}]"
               f" | IPW(lead x len) {ipw:+.3f} CI [{ipw_ci[0]:+.3f},{ipw_ci[1]:+.3f}] (mutants in cells with 0 kept: {lost})")
    out.append(f"   Manski: dropped at kept 5th/95th pct ({lo:+.2f}/{hi:+.2f}): mean d in [{(1-f)*m+f*lo:+.3f}, {(1-f)*m+f*hi:+.3f}];"
               f" at kept min/max ({d.min():+.2f}/{d.max():+.2f}): [{(1-f)*m+f*d.min():+.3f}, {(1-f)*m+f*d.max():+.3f}]")
    out.append(f"   break-even: dropped mutants would need mean d = {-(1-f)*m/f:+.3f} to bring the full-population mean to 0 (kept mean {m:+.3f})")
(EXP / "results/dropout_bounds.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
