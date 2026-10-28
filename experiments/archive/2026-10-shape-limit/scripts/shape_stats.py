# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Items 5 and 7: summarise examples/shape.rs output.
usage: uv run experiments/archive/2026-10-shape-limit/scripts/shape_stats.py experiments/archive/2026-10-shape-limit/results/shape_rotor.csv [experiments/archive/2026-10-shape-limit/results/shape_ants.csv]"""
import sys
import numpy as np
import polars as pl


def load(path):
    rows = [l for l in open(path) if l.startswith("cp,")]
    cols = "kind,spec,k,A,rg2,aniso,rbar,rsd,h2,h4,h8,Wsurf,fill".split(",")
    df = pl.DataFrame([r.strip().split(",") for r in rows], schema=cols, orient="row")
    df = df.with_columns([pl.col(c).cast(pl.Float64) for c in cols[2:]]).with_columns(
        rule=pl.col("spec").str.split("@").list.get(0))
    prof = [l.strip().split(",") for l in open(path) if l.startswith("prof,")]
    return df, prof


def summarise(df, label):
    print(f"\n=== {label}: {df['spec'].n_unique()} runs, {df['rule'].n_unique()} walker types")
    t = 2.0 ** df["k"]
    df = df.with_columns(coef=pl.col("A") / t ** (2 / 3))
    g = df.group_by("k", maintain_order=True).agg(
        n=pl.len(), aniso=pl.col("aniso").median(), h2=pl.col("h2").median(), h4=pl.col("h4").median(),
        h8=pl.col("h8").median(), rsd=pl.col("rsd").median(), fill=pl.col("fill").median(),
        W=pl.col("Wsurf").mean(), coef=pl.col("coef").mean(), cv=pl.col("coef").std() / pl.col("coef").mean()).sort("k")
    pl.Config.set_tbl_rows(40); pl.Config.set_float_precision(4)
    print(g)
    W = g["W"].to_numpy(); k = g["k"].to_numpy().astype(float)
    # local exponent of W against t (a window of two checkpoints = 4 octaves)
    loc = np.diff(np.log(W)) / (np.diff(k) * np.log(2))
    print("local exponent of Wsurf vs t between checkpoints:", " ".join(f"{a:.0f}-{b:.0f}:{e:.3f}" for a, b, e in zip(k[:-1], k[1:], loc)))
    sel = k >= 18
    print("fit Wsurf ~ t^d over k>=18: d = %.3f" % np.polyfit(k[sel] * np.log(2), np.log(W[sel]), 1)[0])
    return df


def per_rule(df):
    # per rule: CV of coef across seeds at the first and last checkpoints; median aniso / h4 at last
    kmax = int(df["k"].max())
    rows = []
    for (r,), g in df.group_by("rule", maintain_order=True):
        t = 2.0 ** g["k"]
        a = g.filter(pl.col("k") == 16)["A"].to_numpy() / 2 ** (16 * 2 / 3)
        b = g.filter(pl.col("k") == kmax)["A"].to_numpy() / 2 ** (kmax * 2 / 3)
        last = g.filter(pl.col("k") == kmax)
        W = g.group_by("k", maintain_order=True).agg(pl.col("Wsurf").mean()).sort("k")
        kk, ww = W["k"].to_numpy().astype(float), W["Wsurf"].to_numpy()
        s = kk >= 18
        rows.append(dict(rule=r, n=len(b), cv16=a.std(ddof=1) / a.mean(), cvmax=b.std(ddof=1) / b.mean(), coef=b.mean(),
                         aniso=last["aniso"].median(), h4=last["h4"].median(), fill=last["fill"].median(),
                         d_W=np.polyfit(kk[s] * np.log(2), np.log(ww[s]), 1)[0]))
    out = pl.DataFrame(rows).sort("rule")
    pl.Config.set_tbl_rows(40)
    print(out)
    print("rules with CV falling by >= 2x from 2^16 to 2^%d: %d of %d" % (kmax, ((out["cv16"] / out["cvmax"]) >= 2).sum(), out.height))
    print("median aniso %.3f, median h4 %.3f; Wsurf exponent (k>=18): median %.3f range %.3f..%.3f" % (
        out["aniso"].median(), out["h4"].median(), out["d_W"].median(), out["d_W"].min(), out["d_W"].max()))
    return out


def profiles(prof, label):
    P = np.array([[float(x) for x in p[3].split(";")] for p in prof])
    print(f"\n{label} density profile (mean visits per cell / (t/A)), shells of 0.075 R_eq; mean over runs:")
    print(" ".join(f"{v:.2f}" for v in P.mean(0)))
    return P


if __name__ == "__main__":
    dr, pr = load(sys.argv[1])
    summarise(dr, "rotor")
    prr = profiles(pr, "rotor")
    if len(sys.argv) > 2:
        da, pa = load(sys.argv[2])
        summarise(da, "ants")
        per_rule(da)
        # profile collapse across rules: mean profile per rule
        by = {}
        for p in pa:
            by.setdefault(p[1].split("@")[0], []).append([float(x) for x in p[3].split(";")])
        M = np.array([np.mean(v, 0) for v in by.values()])
        print("\nant mean profile (all rules):", " ".join(f"{v:.2f}" for v in M.mean(0)))
        print("relative sd across rules per shell:", " ".join(f"{s/m:.2f}" if m > 0.05 else "  - " for s, m in zip(M.std(0, ddof=1), M.mean(0))))
        print("shell 6 (0.45-0.525 R_eq): across-rule rel sd %.3f; rotor mean %.2f ant mean %.2f" % (M[:, 6].std(ddof=1) / M[:, 6].mean(), prr.mean(0)[6], M.mean(0)[6]))
