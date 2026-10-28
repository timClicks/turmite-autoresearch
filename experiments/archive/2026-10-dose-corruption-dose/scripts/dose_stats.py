# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Items 13 and 16: dose-response of the hard rules' hold vs kept fraction F and age.
Input experiments/archive/2026-10-dose-corruption-dose/results/dose_all.csv from tetherlab dose (12 seeds per mode; trial 2^23)."""
import numpy as np, polars as pl
raw = open("experiments/archive/2026-10-dose-corruption-dose/results/dose_all.csv").read().splitlines()
hdr = raw[0].split(","); rows = [l.split(",") for l in raw if not l.startswith("rule,") and l]
d = pl.DataFrame(rows, schema=hdr, orient="row").with_columns(age=pl.col("age").cast(pl.Int64), seed=pl.col("seed").cast(pl.Int64), spread=pl.col("spread").cast(pl.Float64), near=pl.col("near").cast(pl.Float64))
area = {("RRRRRLLLLLL", 1048576): 2907, ("RRRRRLLLLLL", 16777216): 7264, ("RRRRRLLLLLL", 268435456): 14239,
        ("RLLLLRRRRLR", 1048576): 5336, ("RLLLLRRRRLR", 16777216): 11144, ("RLLLLRRRRLR", 268435456): 20712}  # from experiments/archive/2026-10-dose-corruption-dose/results/dose.log
def cross(F, y, frac):
    """F at which the mean curve y (decreasing in F) is `frac` of the way from shuffled (F->0) to real (F=1) value."""
    target = y[0] + frac * (y[-1] - y[0])  # y ordered by increasing F; y[0] = fully shuffled-like, y[-1]=real
    for i in range(len(F) - 1):
        if (y[i] - target) * (y[i + 1] - target) <= 0 and y[i] != y[i + 1]:
            return F[i] + (target - y[i]) / (y[i + 1] - y[i]) * (F[i + 1] - F[i])
    return float("nan")
out = []
for (rule, age), g in d.group_by(["rule", "age"], maintain_order=True):
    modes = {}
    for m, h in g.group_by("mode", maintain_order=True):
        modes[m[0]] = h["spread"].to_numpy()
    Fs = sorted([float(m.split(":")[1]) for m in modes if m.startswith("keep:")])
    F = np.array([0.0] + Fs + [1.0]); y = np.array([modes["shuffle"].mean()] + [modes[f"keep:{f:g}"].mean() for f in Fs] + [modes["real"].mean()])
    f50, f10, f90 = cross(F, y, 0.5), cross(F, y, 0.1), cross(F, y, 0.9)
    A = area[(rule, age)]
    # per-realisation bimodality near the midpoint: share of runs between 25% and 75% of the way real..shuffle
    lo, hi = modes["real"].mean(), modes["shuffle"].mean()
    near_mid = [f for f in Fs if abs(f - f50) <= 0.04] if f50 == f50 else []
    allv = np.concatenate([modes[f"keep:{f:g}"] for f in near_mid]) if near_mid else np.array([])
    frac = (allv - lo) / (hi - lo) if len(allv) else np.array([])
    mid_share = float(((frac > 0.25) & (frac < 0.75)).mean()) if len(frac) else float("nan")
    out.append(dict(rule=rule, age=age, area=A, real=lo, shuffle=hi, f50=f50, f10=f10, f90=f90, N50=(1 - f50) * A, width=f90 - f10, mid_share=mid_share, nrun_mid=len(allv)))
    print(f"{rule} age 2^{int(np.log2(age))}: area {A}, real {lo:.1f}, shuffled {hi:.1f}; mean spread by F:", " ".join(f"{f:g}:{modes[f'keep:{f:g}'].mean():.1f}" for f in Fs))
r = pl.DataFrame(out).sort(["rule", "age"])
pl.Config.set_tbl_cols(14); pl.Config.set_float_precision(3); pl.Config.set_tbl_width_chars(220)
print(r)
for rule, g in r.group_by("rule", maintain_order=True):
    g = g.sort("age")
    print(rule[0], "N50 ratio (2^28 / 2^20): %.2f  area ratio: %.2f  (1-f50) ratio: %.2f" % (g["N50"][2] / g["N50"][0], g["area"][2] / g["area"][0], (1 - g["f50"][2]) / (1 - g["f50"][0])))
# dispersion across seeds at F near f50 for 2^24
for (rule, age), g in d.filter(pl.col("age") == 16777216).group_by(["rule", "age"], maintain_order=True):
    for f in (0.9, 0.94, 0.96):
        v = g.filter(pl.col("mode") == f"keep:{f:g}")["spread"].to_numpy()
        print(rule, "F=%g spreads sorted:" % f, np.round(np.sort(v), 1).tolist())
