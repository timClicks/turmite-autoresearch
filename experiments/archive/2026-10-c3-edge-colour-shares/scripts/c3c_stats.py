# /// script
# dependencies = ["polars", "numpy"]
# ///
"""C3c: edge-share constancy over k = 29..31 with ~10x larger boundary sets, versus the binomial sampling floor for the same counts. Rule: notes/frontier-2026-10-13-results.md."""
import numpy as np, polars as pl
m = pl.read_csv("experiments/archive/2026-10-colourstats/results/colourstats_mix31.csv", schema_overrides={"k": pl.Utf8})
esc = m.filter(pl.col("k") == "escaped")["rule"].unique().to_list(); m = m.filter(pl.col("k") != "escaped").with_columns(pl.col("k").cast(pl.Int64))
rng = np.random.default_rng(20261013); obs, floor05, floor10, ratios, simr = [], [], [], [], []; nb = []
for (rule,), g in m.group_by("rule"):
    g = g.sort("k"); 
    if g["k"].to_list()[-3:] != [29, 30, 31]: continue
    hb = np.array([[int(v) for v in s.split(":")] for s in g["hist_boundary"].to_list()[-3:]]); N = hb.sum(1); nb.append(N.min())
    for c in range(hb.shape[1]):
        s = hb[:, c] / N
        if s.max() < 0.05: continue
        ratios.append(s.max() / s.min()); p = hb[:, c].sum() / N.sum()
        dr = rng.binomial(N[None, :], p, size=(4000, 3)) / N[None, :]; r = dr.max(1) / np.maximum(dr.min(1), 1e-12)
        floor05.append((r < 1.05).mean()); floor10.append((r < 1.10).mean()); simr.append(np.median(r))
ratios = np.array(ratios)
print(f"rules analysed {len(nb)} (escaped before 2^31: {len(set(esc))}); pairs {len(ratios)}; boundary cells at k=29..31: median of per-rule min {int(np.median(nb))}")
o05, o10 = (ratios < 1.05).mean(), (ratios < 1.10).mean(); f05, f10 = np.mean(floor05), np.mean(floor10)
print(f"max/min < 1.05: observed {o05:.3f}, sampling floor {f05:.3f} (observed/floor {o05/f05:.2f}); < 1.10: observed {o10:.3f}, floor {f10:.3f}; median ratio observed {np.median(ratios):.3f}, floor {np.median(simr):.3f}")
print("rule: constant to 5%% if observed/floor >= 0.9; real drift if < 0.7 ->", "constant" if o05 / f05 >= 0.9 else "drift" if o05 / f05 < 0.7 else "inconclusive")
