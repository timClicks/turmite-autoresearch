# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Pilot on DEVELOPMENT bases only (4 pilot seeds): instrument cost, attainment, replicate noise,
and whether exposure of the altered colour carries information beyond its position. Nothing here
is a registered test; it fixes the resolution threshold and decides what is identifiable.

usage (repo root): uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/pilot_analyse.py
"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).parent))
from kpe_lib import EXP, RES, ROOT, WS, colour_exposure, load_bands, load_reads, pooled  # noqa: E402

D = EXP / "dumps" / "pilot"
PILOT = [2026101570001 + i for i in range(4)]
arms = pl.read_csv(RES / "arms.csv").filter(pl.col("side") == "dev")
bands = load_bands(D)
reads = load_reads(D)
out = []
git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
out.append(f"# cmd: uv run experiments/archive/2026-10-kappa-prefix-exposure/scripts/pilot_analyse.py\n# git: {git} (working tree dirty)  inputs: dumps/pilot ({bands['spec'].n_unique()} specs), results/arms.csv")

# ---- 1. cost and attainment
log = (RES / "pilot_run.log").read_text()
secs = [float(m) for m in re.findall(r"([0-9.]+)s$", log, flags=re.M)]
out.append(f"\n[cost] specs run: {len(secs)}; wall seconds per spec: median {np.median(secs):.2f}, mean {np.mean(secs):.2f}, max {max(secs):.1f}, sum {sum(secs):.0f} s (6 threads)")
b0 = bands.filter(pl.col("band_id") == 0)
out.append("[stop] " + ", ".join(f"{r['stop']}={r['len']}" for r in b0.group_by("stop").len().sort("stop").iter_rows(named=True)) + f" of {b0.height} runs; "
           f"attained band0 {int(b0['attained'].sum())}, band1 {int(bands.filter(pl.col('band_id') == 1)['attained'].sum())}; valid band1 {int(bands.filter(pl.col('band_id') == 1)['valid'].sum())}")
ba = bands.join(arms.select("rule", "arm", "base"), on="rule")  # a mutant reached from two bases is credited to both
grp = ba.with_columns(grp=pl.when(pl.col("arm") == "base").then(pl.lit("base")).when(pl.col("arm").is_in(["a1", "a2"])).then(pl.lit("lead")).when(pl.col("arm") == "m1").then(pl.lit("mid"))
                      .when(pl.col("arm").is_in(["l1", "l2"])).then(pl.lit("late")).otherwise(pl.lit("p0")))
att = grp.group_by("grp", "band_id").agg(runs=pl.len(), valid=pl.col("valid").mean(), escaped=(pl.col("stop") == "escaped").mean(), budget=(pl.col("stop") == "budget").mean()).sort("grp", "band_id")
out.append("[attainment by arm group and band]\n" + str(att))

# ---- 2. replicate noise: within-rule seed sd, and disjoint halves
runs = grp.filter(pl.col("valid")).with_columns(
    lnbs=(pl.col("b_dep") / pl.col("steps")).log(), lnL64=((pl.col("epl_64") + .5) / pl.col("new_cells")).log(), lnL256=((pl.col("epl_256") + .5) / pl.col("new_cells")).log(),
    lntau256=((pl.col("tail_256") + .5) / pl.col("steps")).log())
sd = runs.group_by("rule", "band_id").agg(m=pl.len(), s=pl.col("lnbs").std(), s64=pl.col("lnL64").std(), s256=pl.col("lnL256").std(), st=pl.col("lntau256").std()).filter(pl.col("m") >= 3)
pool = {}
for col, name in (("s", "ln(B/S)"), ("s64", "ln Lam_64"), ("s256", "ln Lam_256"), ("st", "ln tau_256")):
    pool[col] = {k: float(np.sqrt(sd.filter(pl.col("band_id") == k)[col].pow(2).mean())) for k in (0, 1)}
    out.append(f"[replicate noise] pooled within-rule between-seed sd of {name}: band0 {pool[col][0]:.3f}, band1 {pool[col][1]:.3f} (rules with >=3 valid seeds: "
               f"{sd.filter(pl.col('band_id') == 0).height}, {sd.filter(pl.col('band_id') == 1).height})")
half = []
for (rule, k), g in runs.group_by("rule", "band_id"):
    a, b = g.filter(pl.col("seed").is_in(PILOT[:2])), g.filter(pl.col("seed").is_in(PILOT[2:]))
    if a.height == 2 and b.height == 2:
        half.append((k, a["lnbs"].mean() - b["lnbs"].mean()))
for k in (0, 1):
    v = np.array([x for kk, x in half if kk == k])
    out.append(f"[replicate halves, seeds (1,2) vs (3,4)] band{k}: n={len(v)} rules, sd of the half-difference {v.std(ddof=1):.3f} (= pooled sd {pool['s'][k]:.3f} if seeds are iid), median |diff| {np.median(np.abs(v)):.3f}")
for m in (8, 32):
    out.append(f"[resolution threshold, 3*s_pool*sqrt(2/m) on ln B/S] m={m} target seeds per arm: band0 {3 * pool['s'][0] * np.sqrt(2 / m):.3f}, band1 {3 * pool['s'][1] * np.sqrt(2 / m):.3f}; "
               f"se of one paired effect {pool['s'][0] * np.sqrt(2 / m):.3f} / {pool['s'][1] * np.sqrt(2 / m):.3f}")

# ---- 3. pilot effects and exposure vs position
pb = pooled(runs.filter(pl.col("seed").is_in(PILOT)).drop("base", "arm", "grp").unique(subset=["spec", "band_id"]), ["rule", "band_id"])
rows = []
for r in arms.filter(pl.col("arm") != "base").iter_rows(named=True):
    for k in (0, 1):
        bb = pb.filter((pl.col("rule") == r["base"]) & (pl.col("band_id") == k))
        mm = pb.filter((pl.col("rule") == r["rule"]) & (pl.col("band_id") == k))
        if bb.height == 0 or mm.height == 0 or bb["n_seeds"][0] < 3 or mm["n_seeds"][0] < 3:
            continue
        j = int(r["pos"])
        ex = colour_exposure(reads, bands, r["base"], PILOT, k, j)
        rows.append(dict(base=r["base"], arm=r["arm"], pos=j, band=k, d_lnbs=mm["lnbs"][0] - bb["lnbs"][0],
                         **{f"d_lnLam{w}": float(np.log(mm[f"Lam_{w}"][0] / bb[f"Lam_{w}"][0])) for w in (16, 64, 256, 1024)},
                         **{f"d_lntau{w}": float(np.log((mm[f"tail_{w}"][0] + .5) / mm["steps"][0]) - np.log((bb[f"tail_{w}"][0] + .5) / bb["steps"][0])) for w in (64, 256)},
                         d_lnkappa=float(np.log(mm["kappa_end"][0] / bb["kappa_end"][0])), ln_share=np.log(ex["share"]) if ex["reads"] else np.nan,
                         boundary_share=ex["boundary_share"], near_share=ex["near_share"], mean_depth=ex["mean_depth"], reads=ex["reads"]))
pairs = pl.DataFrame(rows)
pairs.write_csv(RES / "pilot_pairs.csv")
out.append(f"\n[pilot pairs] {pairs.height} (base, mutant, band) rows with >=3 valid seeds on both sides; per band: {pairs.group_by('band').len().sort('band').rows()}")
for k in (0, 1):
    thr = 3 * pool["s"][k] * np.sqrt(2 / 8)
    p = pairs.filter((pl.col("band") == k) & (pl.col("arm") != "p0"))
    e, l = p.filter(pl.col("pos") < 8), p.filter(pl.col("pos") >= 8)
    lead, mid = p.filter(pl.col("pos") <= 2), p.filter((pl.col("pos") >= 3) & (pl.col("pos") < 8))
    out.append(f"\n-- band {k}: early (positions 1..7) n={e.height} [lead 1-2: {lead.height}, mid 3-7: {mid.height}], late n={l.height}")
    for name, g in (("lead", lead), ("mid", mid), ("late", l)):
        v = g["d_lnbs"].to_numpy()
        out.append(f"   {name}: median |d ln(B/S)| {np.median(np.abs(v)):.3f}, share above the m=8 threshold {(np.abs(v) > thr).mean():.2f}; ln(exposure share): "
                   f"min {np.nanmin(g['ln_share']):.2f} med {np.nanmedian(g['ln_share']):.2f} max {np.nanmax(g['ln_share']):.2f}; "
                   f"boundary share of reads: min {np.nanmin(g['boundary_share']):.3f} med {np.nanmedian(g['boundary_share']):.3f} max {np.nanmax(g['boundary_share']):.3f}; "
                   f"mean depth class of reads: min {np.nanmin(g['mean_depth']):.2f} med {np.nanmedian(g['mean_depth']):.2f} max {np.nanmax(g['mean_depth']):.2f}")
    lo, hi = np.nanmin(l["mean_depth"]), np.nanmax(l["mean_depth"])
    ee = e["mean_depth"].to_numpy()
    out.append(f"   overlap of early and late mean read depth: {((ee >= lo) & (ee <= hi)).mean():.2f} of early values lie inside the late range [{lo:.2f}, {hi:.2f}]")
    for col in ("ln_share", "boundary_share", "near_share", "mean_depth"):
        ok = p.filter(pl.col(col).is_finite())
        out.append(f"   {col}: Spearman with position {spearmanr(ok['pos'], ok[col]).statistic:+.2f}, R^2 of OLS on position {np.corrcoef(ok['pos'], ok[col])[0, 1] ** 2:.2f} (n={ok.height})")
    ok = p.filter(pl.col("d_lnbs").is_finite())
    for col in ("d_lnLam16", "d_lnLam64", "d_lnLam256", "d_lnLam1024", "d_lntau256"):
        out.append(f"   [exploratory, dev pilot only] Spearman({col}, d ln B/S) = {spearmanr(ok[col], ok['d_lnbs']).statistic:+.2f} over {ok.height} pairs")
    out.append(f"   [exploratory] Spearman(position, |d ln B/S|) = {spearmanr(ok['pos'], ok['d_lnbs'].abs()).statistic:+.2f}; Spearman(mean_depth, |d ln B/S|) = {spearmanr(ok.filter(pl.col('mean_depth').is_finite())['mean_depth'], ok.filter(pl.col('mean_depth').is_finite())['d_lnbs'].abs()).statistic:+.2f}")
p0 = pairs.filter(pl.col("arm") == "p0")
out.append(f"\n[position-0 anchor, descriptive] n={p0.height}; median |d ln(B/S)| band0 {np.median(np.abs(p0.filter(pl.col('band') == 0)['d_lnbs'])):.3f}, band1 {np.median(np.abs(p0.filter(pl.col('band') == 1)['d_lnbs'])):.3f}")

# ---- 4. episode budget in the base arms (descriptive)
bb = pooled(runs.filter(pl.col("arm") == "base").drop("base", "arm", "grp").unique(subset=["spec", "band_id"]), ["band_id"])
for r in bb.sort("band_id").iter_rows(named=True):
    out.append(f"[base arms pooled] band{r['band_id']}: B/S {r['bs']:.4f}, kappa_end {r['kappa_end']:.2f}, episodes per discovered cell {r['ep_n'] / r['new_cells']:.3f}; "
               + "; ".join(f"w={w}: Lam {r[f'Lam_{w}']:.4f} tau {r[f'tau_{w}']:.3f}" for w in WS[1:])
               + f"; fresh-window mean forward displacement {r['mean_fwd']:.2f} (windows {r['launch_n']})")
(RES / "pilot_stats.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
