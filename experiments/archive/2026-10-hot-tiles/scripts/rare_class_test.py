# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Open question Q4 / item 14 generalisation: are the rarest colours of other rules also critical?
For 12 random rules from the spread ~14.5 cluster (13.7-15.6) and 12 from the ~7.0 cluster (6.8-7.3) (numpy seed 20261013):
grow 2^24, find the 3 rarest colours, swap-test each (class:K) against the matched random control (ctrlclass:K), 6 seeds, trial 2^22.
Reports the ratio class/control for rare colours and for the three most abundant colours. Run: uv run experiments/archive/2026-10-hot-tiles/scripts/rare_class_test.py"""
import os, subprocess, numpy as np, polars as pl
T = os.path.expanduser("~/turmite-target-frontier/release/examples/tetherlab")
d = pl.read_csv("experiments/archive/2026-10-tether-rules/results/tether_screen.csv").filter(pl.col("spread_real").is_not_null())
rng = np.random.default_rng(20261013)
def pick(lo, hi, k): 
    r = d.filter((pl.col("spread_real") >= lo) & (pl.col("spread_real") <= hi))["rule"].to_list(); return list(rng.choice(r, k, replace=False))
groups = {"home~14.5": pick(13.69, 15.6, 12), "home~7.0": pick(6.83, 7.25, 12)}
env = dict(os.environ, RAYON_NUM_THREADS="2")
for gname, rules in groups.items():
    rare_ratio, ab_ratio = [], []
    for r in rules:
        desc = subprocess.run([T, "describe", r, "16777216"], capture_output=True, text=True, env=env).stdout.strip().splitlines()[1:]
        cnt = {int(l.split(",")[1]): int(l.split(",")[2]) for l in desc}
        order = sorted(cnt, key=lambda k: cnt[k]); rare, abund = order[:3], order[-3:]
        modes = ["real", "shuffle"] + [f"{m}:{k}" for k in rare + abund for m in ("class", "ctrlclass")]
        out = subprocess.run([T, "dose", r, "16777216", "4194304", "6"] + modes, capture_output=True, text=True, env=env).stdout.strip().splitlines()[1:]
        sp = {}
        for l in out:
            p = l.split(","); sp.setdefault(p[2], []).append(float(p[4]))
        m = lambda k: np.mean(sp[k])
        rr = [m(f"class:{k}") / m(f"ctrlclass:{k}") for k in rare]; aa = [m(f"class:{k}") / m(f"ctrlclass:{k}") for k in abund]
        rare_ratio += rr; ab_ratio += aa
        print(f"{gname} {r:13s} real {m('real'):5.1f} shuf {m('shuffle'):5.1f} rare colours {rare} counts {[cnt[k] for k in rare]} ratios {np.round(rr, 2).tolist()} | abundant {abund} ratios {np.round(aa, 2).tolist()}", flush=True)
    print(f"== {gname}: class/control ratio, rare colours: median {np.median(rare_ratio):.2f} (share > 1.3: {np.mean(np.array(rare_ratio) > 1.3):.2f}); abundant: median {np.median(ab_ratio):.2f} (share < 0.9: {np.mean(np.array(ab_ratio) < 0.9):.2f})\n")
