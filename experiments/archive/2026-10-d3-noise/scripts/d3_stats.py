# /// script
# dependencies = ["polars", "numpy"]
# ///
"""D3: area exponent vs turn noise eps. Inputs experiments/archive/2026-10-d3-noise/results/d3_noise.csv (new eps), experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_noise.csv (eps 0..0.1), experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_noise_high.csv (0.3, 0.6, 1.0).
Fit: log2(area) vs k over k=18..24 per run, runs with all 7 windows only; report escaped fraction (k=-1 marker or missing windows).
Hypotheses and decision rule: notes/frontier-2026-10-13-results.md. usage: uv run experiments/archive/2026-10-d3-noise/scripts/d3_stats.py"""
import polars as pl, numpy as np
fr = []
for p in ("experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_noise.csv", "experiments/archive/2026-10-d3-noise/results/d3_noise.csv", "experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_noise_high.csv"):
    fr.append(pl.read_csv(p))
d = pl.concat(fr).unique()
d = d.with_columns(rule=pl.col("spec").str.split(":").list.get(1), eps=pl.col("spec").str.split("eps=").list.get(1).str.split(":").list.get(0).cast(pl.Float64))
runs = []
for (spec,), g in d.group_by("spec"):
    esc = (g["k"] == -1).any(); g = g.filter(pl.col("k") > 0).sort("k"); w = g.filter(pl.col("k").is_between(18, 24))
    e = float(g["spec"][0].split("eps=")[1].split(":")[0]); rule = spec.split(":")[1]
    if w.height < 7: runs.append((rule, e, None, esc, g["k"].max() if g.height else 0)); continue
    a = np.polyfit(w["k"].to_numpy().astype(float), np.log2(w["area"].to_numpy().astype(float)), 1)[0]
    ex = np.polyfit(w["k"].to_numpy().astype(float), np.log2(w["extent"].to_numpy().astype(float)), 1)[0]
    runs.append((rule, e, (a, ex), esc, g["k"].max()))
print("eps | runs | escaped | fitted | median area exp (iqr) | median extent exp | between-run sd area")
meds = {}
for e in sorted({r[1] for r in runs}):
    rr = [r for r in runs if r[1] == e]; fit = [r for r in rr if r[2] is not None]
    if fit:
        a = np.array([r[2][0] for r in fit]); x = np.array([r[2][1] for r in fit]); meds[e] = np.median(a)
        print(f"{e:5.2f} | {len(rr):3d} | {sum(r[3] for r in rr):3d} | {len(fit):3d} | {np.median(a):.3f} ({np.quantile(a,.25):.3f}-{np.quantile(a,.75):.3f}) | {np.median(x):.3f} | {a.std(ddof=1) if len(a)>1 else float('nan'):.3f}")
    else:
        print(f"{e:5.2f} | {len(rr):3d} | {sum(r[3] for r in rr):3d} | 0 fitted (all escaped before k=24)")
es = sorted(meds); m = [meds[e] for e in es]
steps = [(es[i], es[i + 1], m[i + 1] - m[i]) for i in range(len(es) - 1)]
print("adjacent steps in the median area exponent:", [(a, b, round(s, 3)) for a, b, s in steps])
print("any step >= 0.08 between eps values <= 0.05 apart:", any(s >= 0.08 and b - a <= 0.05 for a, b, s in steps), "; monotone:", all(s > -0.02 for _, _, s in steps))
