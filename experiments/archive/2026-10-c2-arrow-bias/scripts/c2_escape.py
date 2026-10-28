# /// script
# dependencies = ["polars", "numpy"]
# ///
"""C2 follow-up: all biased-arrow runs left the 8192 board, so per-run exponents over k=20..26 do not exist.
Report instead, per bias, the last completed octave and the width / area local exponents over the windows that exist (k=10..last).
usage: uv run experiments/archive/2026-10-c2-arrow-bias/scripts/c2_escape.py"""
import polars as pl, numpy as np
d = pl.read_csv("experiments/archive/2026-10-c2-arrow-bias/results/c2_probe.csv").with_columns(bias=pl.col("rule").map_elements(lambda s: float(s.split(":")[2]) if s.startswith("brotor") else 0.0, return_dtype=pl.Float64),
                                                   w=pl.max_horizontal("width", "height"))
for b in sorted(d["bias"].unique()):
    g = d.filter(pl.col("bias") == b)
    last = g.group_by("rule").agg(kmax=pl.col("k").max(), esc=pl.col("escaped").first())
    sl = []
    for (rule,), r in g.group_by("rule"):
        r = r.filter((pl.col("k") >= 10)).sort("k")
        if r.height >= 3: sl.append((np.polyfit(np.log2(r["t"].to_numpy().astype(float)), np.log2(r["w"].to_numpy().astype(float)), 1)[0], np.polyfit(np.log2(r["t"].to_numpy().astype(float)), np.log2(r["area"].to_numpy().astype(float)), 1)[0], r["w"][-1], r["ant_r2"][-1]))
    sl = np.array(sl)
    if sl.ndim < 2: print(f"bias {b:4.2f}: too few windows before escape (runs {last.height}, kmax median {last['kmax'].median()})"); continue
    print(f"bias {b:4.2f}: runs {last.height}, escaped {int(last['esc'].sum())}, last completed octave k: median {last['kmax'].median():.0f} (min {last['kmax'].min()}, max {last['kmax'].max()}); "
          f"width exponent (k>=10, over existing windows) median {np.median(sl[:,0]):.3f}, area exponent {np.median(sl[:,1]):.3f}; median final width {np.median(sl[:,2]):.0f}")
