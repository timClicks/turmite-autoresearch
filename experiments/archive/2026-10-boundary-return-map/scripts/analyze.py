# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "polars"]
# ///
"""ICC_r, G(r), r*, identity accounting for experiments/archive/2026-10-boundary-return-map.

usage: analyze.py RAWDIR OUTPREFIX [--null-seed N]
RAWDIR holds <spec>.dep.csv / .rep.csv / .hist.csv from examples/boundary_return_map_sampler.rs.
Definitions are in the experiment README (Statistics). Population estimates reweight each
stratum of baseline episode length (T<=3, 4..31, 32..511, >=512) by its share of ALL departures
in the band (from .hist.csv); `--` raw (unweighted) ICC is also written.
"""
import glob, json, os, sys
import numpy as np
import polars as pl

raw, outp = sys.argv[1], sys.argv[2]
NULL_SEED = 20261021
STR_OF_BUCKET = lambda k: 0 if k <= 2 else 1 if k <= 5 else 2 if k <= 9 else 3  # bucket k = bit length of T


def load(kind):
    fs = sorted(glob.glob(os.path.join(raw, f"*.{kind}.csv")))
    return pl.concat([pl.read_csv(f) for f in fs]) if fs else None


dep, rep, hist = load("dep"), load("rep"), load("hist")
rep = rep.join(dep.select(["spec", "band", "dep", "stratum", "area", "perim", "maxdepth", "base_t", "live_ok"]), on=["spec", "band", "dep"])
rep = rep.with_columns((pl.col("t") + 1).log(2).alias("y"))  # log2(1+T)
rep = rep.with_columns(pl.col("spec").str.replace(r"@.*", "").alias("rule"))
hist = hist.with_columns(pl.col("spec").str.replace(r"@.*", "").alias("rule"), pl.col("bucket").map_elements(STR_OF_BUCKET, return_dtype=pl.Int64).alias("stratum"))
shares = hist.group_by(["rule", "band", "stratum"]).agg(pl.col("n").sum().alias("N"))
taken = dep.with_columns(pl.col("spec").str.replace(r"@.*", "").alias("rule")).group_by(["rule", "band", "stratum"]).agg(pl.len().alias("n_taken"))
w = shares.join(taken, on=["rule", "band", "stratum"], how="inner").with_columns((pl.col("N") / pl.col("n_taken")).alias("w"))
rep = rep.join(w.select(["rule", "band", "stratum", "w"]), on=["rule", "band", "stratum"], how="left").with_columns(pl.col("w").fill_null(0.0))


def icc(y, g, wt, M):
    """weighted one-way ANOVA ICC; y: (groups, M)"""
    gm = y.mean(1)
    sw = (wt * ((y - gm[:, None]) ** 2).sum(1) / (M - 1)).sum() / wt.sum()
    mu = (wt * gm).sum() / wt.sum()
    vb = (wt * (gm - mu) ** 2).sum() / wt.sum() - sw / M
    tot = max(vb, 0) + sw
    return max(vb, 0) / tot if tot > 0 else float("nan")


def groups(df, r):
    d = df.filter(pl.col("r") == r).sort(["spec", "band", "dep", "rep"])
    keys = d.select(["spec", "band", "dep"]).unique(maintain_order=True)
    M = d["rep"].n_unique()
    y = d["y"].to_numpy().reshape(-1, M)
    wt = d["w"].to_numpy().reshape(-1, M)[:, 0]
    bt = d["base_t"].to_numpy().reshape(-1, M)[:, 0].astype(float)
    return y, wt, bt, M


def rstar(rs, G, thr=0.8):
    x = np.log2(np.array(rs) + 1.0)
    for i in range(1, len(rs)):
        if G[i] >= thr and not np.isnan(G[i]):
            if G[i - 1] >= thr:
                return float(rs[i - 1])
            f = (thr - G[i - 1]) / (G[i] - G[i - 1])
            return float(2 ** (x[i - 1] + f * (x[i] - x[i - 1])) - 1)
    return float("inf")


rows, rng = [], np.random.default_rng(NULL_SEED)
radii = sorted(rep["r"].unique().to_list())
BIG = radii[-1]
for (rule, band), df in rep.group_by(["rule", "band"], maintain_order=True):
    L = float((df.unique(["spec", "band", "dep"]).select(pl.col("area") / pl.col("perim")))["area"].mean())
    for label, sub in [("all", df), ("shallow", df.filter(pl.col("maxdepth") <= 8)), ("deep", df.filter(pl.col("maxdepth") > 8))]:
        if sub.height == 0 or sub.filter(pl.col("r") == 0).height == 0:
            continue
        out = dict(rule=rule, band=int(band), subset=label, L=L, n_dep=int(sub.filter(pl.col("r") == 0).height // sub["rep"].n_unique()))
        for weighted in (True, False):
            icc_r, icc_t = [], []
            for r in radii:
                y, wt, bt, M = groups(sub, r)
                icc_r.append(icc(y, None, wt if weighted else np.ones_like(wt), M))
                icc_t.append(icc(y, None, wt * bt, M))
            i0 = icc_r[0]
            G = [(v - i0) / (1 - i0) if i0 < 1 else float("nan") for v in icc_r]
            k = "w" if weighted else "u"
            out[f"icc_{k}"] = icc_r
            out[f"G_{k}"] = G
            out[f"rstar_{k}"] = rstar(radii[:-1], G[:-1])
            if weighted:  # P5 (amendment): weight each departure by its baseline duration = share of interior time
                Gt = [(v - icc_t[0]) / (1 - icc_t[0]) if icc_t[0] < 1 else float("nan") for v in icc_t]
                out["icc_t"], out["G_t"], out["rstar_t"] = icc_t, Gt, rstar(radii[:-1], Gt[:-1])
        # identity accounting (unweighted over replicas)
        d2 = sub.group_by("r").agg(pl.col("ident").mean().alias("ID"), pl.col("unexposed").mean().alias("U"), pl.col("coarse").mean().alias("coarse")).sort("r")
        out["ID"], out["U"], out["coarse"] = d2["ID"].to_list(), d2["U"].to_list(), d2["coarse"].to_list()
        out["E"] = [a - b for a, b in zip(out["ID"], out["U"])]
        # C3: ICC null (replicas reassigned across departures)
        if label == "all":
            nulls = []
            for r in radii[1:-1]:
                y, wt, bt, M = groups(sub, r)
                yp = rng.permutation(y.ravel()).reshape(y.shape)
                nulls.append(icc(yp, None, wt, M))
            out["icc_null"] = nulls
        rows.append(out)
        rep_ok = sub.unique(["spec", "band", "dep"])
json.dump(dict(radii=radii, rows=rows), open(outp + ".json", "w"), indent=1)
live = dep["live_ok"].mean()
print(f"departures: {dep.height}, live_ok fraction {live:.4f}")
for o in rows:
    if o["subset"] == "all":
        print(f"{o['rule']:>14} band{o['band']} L={o['L']:.0f} n={o['n_dep']} r*_w={o['rstar_w']:.1f} r*/L={o['rstar_w']/o['L']:.3f} "
              f"G_w={[round(g, 2) for g in o['G_w']]} E_med={np.median([e for e, u in zip(o['E'], o['U']) if u < 0.9] or [float('nan')]):.3f}")
