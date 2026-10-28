# /// script
# dependencies = ["polars", "numpy"]
# ///
"""A7-next: which rules have a rising seed-to-seed CV of A/t^(2/3)? Design and prediction: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-a7-rrllllllr-self-averaging/scripts/a7_census.py"""
import numpy as np, polars as pl
rng = np.random.default_rng(20261013)
import os
files = os.environ.get("A7_FILES", "experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv,experiments/archive/2026-10-item21-slow-outliers/results/item21_probe.csv,experiments/archive/2026-10-patched-starts/results/patched.csv,experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_probe.csv,experiments/archive/2026-10-a7-rrllllllr-self-averaging/results/a7_probe.csv").split(",")
d = pl.concat([pl.read_csv(f, columns=["rule", "k", "area", "escaped"]) for f in files]).filter(~pl.col("escaped") & pl.col("k").is_between(20, 26))
d = d.with_columns(base=pl.col("rule").str.split("@").list.first(), seed=pl.col("rule").str.split("@").list.get(1).cast(pl.Int64)).unique(subset=["rule", "k"])
KS = list(range(20, 27))
def slope_cv(piv):
    cv = np.array([piv[:, i].std(ddof=1) / piv[:, i].mean() for i in range(len(KS))]); return float(np.polyfit(KS, cv, 1)[0]), cv
rows = []
for (b,), g in d.group_by("base"):
    ws = g.pivot(on="k", index="seed", values="area").drop_nulls()
    if ws.height < 8 or any(str(k) not in ws.columns for k in KS): continue
    piv = np.column_stack([ws[str(k)].to_numpy().astype(float) / 2.0 ** (2 * k / 3) for k in KS])
    s0, cv = slope_cv(piv)
    bs = [slope_cv(piv[rng.integers(0, len(piv), len(piv))])[0] for _ in range(1000)]
    rows.append((b, ws.height, s0, float(np.std(bs)), float(np.mean(np.array(bs) <= 0)), float(cv[0]), float(cv[-1])))
r = pl.DataFrame(rows, schema=["rule", "seeds", "slope", "se", "p_le0", "cv20", "cv26"], orient="row")
flag = r.filter((pl.col("p_le0") < 0.025) & (pl.col("cv26") > pl.col("cv20")))
print(f"rules with >= 8 usable seeds over k=20..26: {r.height}; mean CV slope {r['slope'].mean():+.4f}, median {r['slope'].median():+.4f}; fraction with positive slope {float((r['slope'] > 0).mean()):.2f}")
print(f"flagged rising (one-sided bootstrap p < 0.025 and CV26 > CV20): {flag.height} ({100*flag.height/r.height:.1f}%; 2.5% expected by chance for rules with zero true slope)")
pl.Config.set_tbl_rows(30); pl.Config.set_float_precision(4)
print(flag.sort("slope", descending=True).head(20))
print("RRLLLLLLR:", r.filter(pl.col("rule") == "RRLLLLLLR").rows())
# rotor reference
try:
    rot = pl.read_csv("experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_rotor_probe.csv", columns=["rule", "k", "area", "escaped"]).filter(~pl.col("escaped") & pl.col("k").is_between(20, 26))
    ws = rot.pivot(on="k", index="rule", values="area").drop_nulls()
    piv = np.column_stack([ws[str(k)].to_numpy().astype(float) / 2.0 ** (2 * k / 3) for k in KS]); s0, cv = slope_cv(piv)
    print(f"rotor ({ws.height} seeds): CV slope {s0:+.4f} per octave, CV20 {cv[0]:.3f} -> CV26 {cv[-1]:.3f}")
except Exception as e:
    print("rotor reference failed:", type(e).__name__, e)
print("distribution of slopes (quantiles 5/25/50/75/95%):", np.round(np.quantile(r["slope"].to_numpy(), [.05, .25, .5, .75, .95]), 4).tolist())
