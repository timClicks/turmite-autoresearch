# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W6 exploratory checks (NOT registered; run after seeing w6_stats): (a) escape vs out-of-core-band by early/late, (b) P6.1-P6.3 restricted to
mutants that are also stationary, (c) consistency of W6 per-rule ln kappa with census kappa.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w6_checks.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from scipy.stats import spearmanr
from kcommon import *

raw = pl.read_csv(EXP / "dumps" / "w6_probe.csv")
r = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
esc = raw.filter(pl.col("escaped")).group_by(pl.col("rule").str.split("@").list.first().alias("base")).agg(pl.col("rule").n_unique().alias("n_esc"))
core = r.filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0))
rl = core.group_by("base").agg(n=pl.len(), lk=pl.col("kappa").log().mean(), g=pl.col("g_k").median()).filter(pl.col("n") >= 4)
esc_d = dict(zip(esc["base"], esc["n_esc"])); corec = dict(zip(*core.group_by("base").agg(pl.len()).to_dict(as_series=False).values()))
pairs = pl.read_csv(EXP / "results" / "w6_pairs.csv"); scored = pl.read_csv(EXP / "results" / "w6_pairs_scored.csv")
usable = set(rl["base"]); out = [header("uv run scripts/w6_checks.py")]
out.append("(a) mutants with usable base, by early/late: usable / >=4 escaped runs (of 6) / other (fewer than 4 core-band runs without mass escape)")
for k, sel in (("early", pl.col("pos") <= 3), ("late", pl.col("pos") > 3)):
    tot = hi = us = 0
    for b, j, m in pairs.filter(sel).iter_rows():
        if b not in usable: continue
        tot += 1
        if m in usable: us += 1
        elif esc_d.get(m, 0) >= 3: hi += 1
    out.append(f"  {k}: n={tot}, usable {us}, mutant escaped in >= 3 of 6 runs {hi}, other unusable {tot - us - hi}  (note: escaped-in-3 is a proxy; per-run escapes counted from the csv)")
g = dict(zip(rl["base"], rl["g"]))
S = scored.with_columns(mst=pl.col("mutant").map_elements(lambda m: abs(g[m]) < 0.05, return_dtype=pl.Boolean))
out.append(f"(b) mutants also stationary: {int(S['mst'].sum())} of {S.height} usable pairs ({S.filter(pl.col('k')=='early')['mst'].mean():.3f} early, {S.filter(pl.col('k')=='late')['mst'].mean():.3f} late)")
T = S.filter(pl.col("mst")); brng = rng(22); rat = []
for b, gg in T.group_by("base"):
    e = gg.filter(pl.col("k") == "early")["ad"].to_numpy(); l = gg.filter(pl.col("k") == "late")["ad"].to_numpy()
    if len(e) and len(l): rat.append(np.median(e) / np.median(l))
rat = np.array(rat); ci = np.percentile([np.median(rat[brng.integers(0, len(rat), len(rat))]) for _ in range(2000)], [2.5, 97.5])
out.append(f"  P6.1 restricted: median per-base ratio {np.median(rat):.2f} (CI {ci[0]:.2f}..{ci[1]:.2f}, {len(rat)} bases); pooled median |d| early {T.filter(pl.col('k')=='early')['ad'].median():.3f}, late {T.filter(pl.col('k')=='late')['ad'].median():.3f}")
out.append(f"  P6.3 restricted: share |d|>3SE early {T.filter(pl.col('k')=='early')['big'].mean():.3f}, late {T.filter(pl.col('k')=='late')['big'].mean():.3f}")
cen = census().filter(pl.col("kappa") > 0); ck = dict(zip(cen["rule"], np.log(cen["kappa"].to_numpy())))
pairs_c = [(ck[x], v) for x, v in zip(rl["base"], rl["lk"]) if x in ck]
a = np.array(pairs_c)
out.append(f"(c) consistency with census kappa (single long run, k-window of the census): {len(a)} of {rl.height} W6-usable rules are in the census blob list; Spearman {spearmanr(a[:,0], a[:,1])[0]:+.3f}, Pearson {np.corrcoef(a[:,0], a[:,1])[0,1]:+.3f}")
(EXP / "results" / "w6_checks.txt").write_text("\n".join(out) + "\n"); print("\n".join(out))
