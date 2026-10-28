# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Item 17: summarise the 1e10-step rerun of the primitive length<=10 rules unresolved at 1e9 (experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_NN.csv; only chunks with a .done marker).
Chunks hold a fixed-seed random shuffle of the 807 rules, so any set of finished chunks is an unbiased sample."""
import glob, os
import numpy as np, polars as pl
from scipy.stats import poisson
files = [f for f in sorted(glob.glob("experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_*.csv")) if os.path.exists(f[:-4] + ".done")]
d = pl.concat([pl.read_csv(f, infer_schema_length=0).with_columns([pl.col(c).cast(pl.Int64, strict=False) for c in ["steps", "period", "dx", "dy", "onset", "width", "height", "tail_period"]]) for f in files])
tot_rules = sum(len(open(f).read().split()) for f in glob.glob("experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_*.txt"))
print(f"finished chunks: {len(files)} of {len(glob.glob('experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/chunk_*.txt'))}; rules run: {d.height} of {tot_rules} ({d.height / tot_rules:.1%})")
hw = d.filter(pl.col("period").is_not_null()); blobesc = d.filter((pl.col("stop") == "escaped") & pl.col("period").is_null())
print(f"stop: budget {int((d['stop'] == 'budget').sum())}, escaped with highway {hw.height}, escaped without highway (blob reached the 32768 board) {blobesc.height}")
print("highways found:", hw.select(["rule", "steps", "period", "dx", "dy", "onset"]).rows())
f = d.height / tot_rules
print(f"onsets in (1e9, 1e10]: {hw.height} in {d.height} rules = {hw.height / max(d.height, 1):.2%} of survivors -> scaled to all {tot_rules}: {hw.height / f:.1f}")
o = hw["onset"].to_numpy() if hw.height else np.array([])
print("onset values:", sorted(int(x) for x in o))
prev = [13, 17, 14, 17, 26, 11]  # decades (1e3..1e9] from experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/highway_stats.txt (length<=10, primitive)
lam_full = 17.4 * (tot_rules / 807)
print(f"previous decades mean {np.mean(prev[:5]):.1f} per decade (last 11); expectation for (1e9,1e10] if flat: ~{np.mean(prev):.1f} (of ~854 survivors), observed scaled {hw.height / f:.1f}")
if d.height:
    print("Poisson P(X <= observed) with mean = flat expectation x sampled fraction: %.3f ; P(X <= observed) with mean = last decade (11): %.3f" % (
        poisson.cdf(hw.height, np.mean(prev) * f * 807 / 854), poisson.cdf(hw.height, 11 * f * 807 / 854)))
