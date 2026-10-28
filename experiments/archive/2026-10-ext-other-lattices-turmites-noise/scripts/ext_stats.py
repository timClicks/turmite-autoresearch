# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Items 26 and 27: analyse experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_many.csv, ext_noise.csv, ext_bg.csv (made by experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_specs_26_27.sh).
Run: uv run experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_stats.py"""
import numpy as np, polars as pl

def load(p):
    d = pl.read_csv(p).filter(pl.col("k") > 0)
    return d.with_columns(parts=pl.col("spec").str.split(":"))

def slope(k, y, lo, hi):
    s = (k >= lo) & (k <= hi)
    return np.polyfit(k[s] * np.log(2), np.log(y[s]), 1)[0]

print("== H27 many ants: area exponent over k=18..26 (per tick), and A_m(t)/A_1(m t)")
d = load("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_many.csv")
for rule in ["RLR", "RLL", "RLRLRRRLLR", "RRRLR"]:
    base = d.filter(pl.col("spec") == f"sq:{rule}:m=1").sort("k")
    A1 = dict(zip(base["k"].to_list(), base["area"].to_list()))
    line = []
    for m in (1, 2, 4, 8):
        g = d.filter(pl.col("spec") == f"sq:{rule}:m={m}").sort("k")
        k = g["k"].to_numpy().astype(float); A = g["area"].to_numpy().astype(float)
        j = int(np.log2(m))
        ratios = [a / A1[kk + j] for kk, a in zip(g["k"].to_list(), g["area"].to_list()) if kk + j in A1 and kk >= 16]
        line.append(f"m={m}: a={slope(k, A, 18, 26):.3f} ratio(k16..26) {min(ratios):.2f}-{max(ratios):.2f} last {ratios[-1]:.2f} first {ratios[0]:.2f}")
    print(rule, " | ".join(line))

print("\n== H26b noise: local area exponent (mean over rules and seeds) and extent exponent")
d = load("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_noise.csv").with_columns(
    rule=pl.col("parts").list.get(1), eps=pl.col("parts").list.get(2).str.replace("eps=", "").cast(pl.Float64))
for eps in sorted(d["eps"].unique().to_list()):
    out = []
    for lo, hi in [(14, 18), (18, 22), (22, 26), (24, 27)]:
        vals, ev = [], []
        for (sp,), g in d.filter(pl.col("eps") == eps).group_by("spec", maintain_order=True):
            g = g.sort("k"); k = g["k"].to_numpy().astype(float)
            if k.max() < hi: continue
            vals.append(slope(k, g["area"].to_numpy().astype(float), lo, hi)); ev.append(slope(k, g["extent"].to_numpy().astype(float), lo, hi))
        out.append(f"k{lo}-{hi}: a={np.mean(vals):.3f} w={np.mean(ev):.3f} (n={len(vals)})")
    print(f"eps={eps:g}: " + " | ".join(out))
print("area/t^(2/3) at k=24 (mean over seeds/rules) by eps:", {e: round(float((d.filter((pl.col('eps') == e) & (pl.col('k') == 24))['area'] / 2.0 ** 16).mean()), 1) for e in sorted(d['eps'].unique().to_list())})

print("\n== H26a random background: exponents over k=16..24 (area, extent)")
d = load("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_bg.csv")
res = []
for (sp,), g in d.group_by("spec", maintain_order=True):
    g = g.sort("k"); k = g["k"].to_numpy().astype(float)
    if k.max() < 24: print("escaped/short:", sp, k.max()); continue
    res.append((sp.split(":")[1], slope(k, g["area"].to_numpy().astype(float), 16, 24), slope(k, g["extent"].to_numpy().astype(float), 16, 24), slope(k, g["extent"].to_numpy().astype(float), 20, 24)))
a = np.array([r[1:] for r in res])
print(f"{len(res)} runs: area exponent mean {a[:,0].mean():.3f} sd {a[:,0].std():.3f}; extent exponent mean {a[:,1].mean():.3f} sd {a[:,1].std():.3f}; extent exp k20-24 mean {a[:,2].mean():.3f}")
for r in sorted(set(x[0] for x in res)):
    v = np.array([x[1:] for x in res if x[0] == r]); print("  ", r, "area %.3f extent %.3f" % (v[:, 0].mean(), v[:, 1].mean()))

print("\n== H26b high noise (experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_noise_high.csv), exponents over k=14..26 and k=22..26")
d = load("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_noise_high.csv").with_columns(eps=pl.col("parts").list.get(2).str.replace("eps=", "").cast(pl.Float64))
for eps in sorted(d["eps"].unique().to_list()):
    v = []
    for (sp,), g in d.filter(pl.col("eps") == eps).group_by("spec", maintain_order=True):
        g = g.sort("k"); k = g["k"].to_numpy().astype(float)
        if k.max() < 26: continue
        v.append((slope(k, g["area"].to_numpy().astype(float), 14, 26), slope(k, g["area"].to_numpy().astype(float), 22, 26), slope(k, g["extent"].to_numpy().astype(float), 14, 26), slope(k, g["extent"].to_numpy().astype(float), 22, 26)))
    if not v:
        print(f"eps={eps:g}: all runs escaped the 8192 board; max k reached", int(d.filter(pl.col("eps") == eps)["k"].max())); continue
    v = np.array(v); print(f"eps={eps:g}: n={len(v)} area a(14-26)={v[:,0].mean():.3f} a(22-26)={v[:,1].mean():.3f} width w(14-26)={v[:,2].mean():.3f} w(22-26)={v[:,3].mean():.3f}")
