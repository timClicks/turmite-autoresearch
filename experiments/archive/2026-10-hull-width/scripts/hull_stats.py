# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "polars"]
# ///
"""Hull-width statistics against the registered predictions in ../README.md.

usage: uv run experiments/archive/2026-10-hull-width/scripts/hull_stats.py
Reads results/hull_{ants,rotor}.csv (+ shape_check.csv), writes results/hull_stats.txt.
Bootstrap seed 20261014. Estimators are those fixed in the README before the run.
"""
import sys
from pathlib import Path
import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[1]
res = root / "results"
rng = np.random.default_rng(20261014)
out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s)

def load(name):
    rows = [l for l in (res / f"hull_{name}.csv").read_text().splitlines() if not l.startswith("#")]
    for l in (res / f"hull_{name}.csv").read_text().splitlines():
        if l.startswith("#"): P("NOTE", name, l)
    df = pl.read_csv(("\n".join(rows)).encode(), schema_overrides={"spec_bands": pl.String, "boxc": pl.String})
    return df.with_columns(
        pl.col("spec").str.split("@").list.first().alias("rule"),
    )

def slope(x, y):
    return float(np.polyfit(x, y, 1)[0])

def runs(df):
    for spec, g in df.group_by("spec", maintain_order=True):
        yield spec[0], g.sort("k")

def per_run(df, kmin=22):
    r = []
    for spec, g in runs(df):
        h = g.filter(pl.col("k") >= kmin)
        if h.height < 4: P("SKIP (too few checkpoints)", spec, g["k"].max()); continue
        k = h["k"].to_numpy().astype(float)
        t = k * np.log(2)
        d = dict(spec=spec, rule=spec.split("@")[0])
        for col in ("Wall", "Wout"):
            d[f"e_{col}"] = slope(t, np.log(h[col].to_numpy()))
        d["beta_all"] = slope(np.log(h["A"].to_numpy()), np.log(h["Pall"].to_numpy()))
        d["beta_out"] = slope(np.log(h["A"].to_numpy()), np.log(h["Pouter"].to_numpy()))
        for kk in (28, 30):
            row = g.filter(pl.col("k") == kk)
            if row.height == 0: continue
            row = row.row(0, named=True)
            d[f"holefrac{kk}"] = row["Phole"] / row["Pall"]
            bands = np.array([float(v) for v in row["spec_bands"].split(";")])
            if np.all(np.isfinite(bands)) and np.all(bands[1:6] > 0):
                d[f"zeta{kk}"] = -slope(np.arange(1, 6), np.log2(bands[1:6])) / 2
            n = np.array([float(v) for v in row["boxc"].split(";")])
            s = 2.0 ** np.arange(7)
            d[f"Dh{kk}"] = -slope(np.log(s[1:6]), np.log(n[1:6]))
        r.append(d)
    return pl.DataFrame(r)

def med_boot(df, col, by_rule=True):
    v = df.drop_nulls(col)
    if v.height == 0: return "n/a"
    x = v[col].to_numpy()
    m = np.median(x)
    rules = sorted(v["rule"].unique().to_list())  # sorted: unique() order varies per process and decides the bootstrap draws
    groups = [v.filter(pl.col("rule") == r)[col].to_numpy() for r in rules]
    bs = []
    for _ in range(2000):
        pick = rng.integers(0, len(groups), len(groups))
        bs.append(np.median(np.concatenate([groups[i] for i in pick])))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return f"median {m:.3f}  sd {np.std(x, ddof=1) if len(x) > 1 else float('nan'):.3f}  n={len(x)}  rule-boot95 [{lo:.3f}, {hi:.3f}]"

ants, rotor = per_run(load("ants")), per_run(load("rotor"))
P("# hull-width stats; commit", (res / "hull.commit").read_text().strip() if (res / "hull.commit").exists() else "?")
for name, df in (("rotor", rotor), ("ants", ants)):
    P(f"\n== {name} ({df.height} runs)")
    for col in ("e_Wall", "e_Wout", "beta_all", "beta_out", "holefrac28", "holefrac30", "zeta28", "zeta30", "Dh28", "Dh30"):
        if col in df.columns: P(f"{col:11s}", med_boot(df, col))
P("\n== registered checks")
re = rotor["e_Wout"].median(); ae = ants["e_Wout"].median()
P(f"1 calibration: rotor W_out exponent {re:.3f} in [0.08,0.14]: {0.08 <= re <= 0.14}")
if "holefrac28" in ants.columns:
    a, r = ants["holefrac28"].median(), rotor["holefrac28"].median()
    P(f"2 hole share k=28: ants {a:.3f} rotor {r:.3f}; ants>=0.10 and >=3x rotor: {a >= 0.10 and a >= 3 * r}")
verdict = "H-rough" if ae >= 0.18 else "H-hole" if ae <= 0.15 else "mixed"
P(f"3 ants W_out exponent {ae:.3f} -> {verdict}; ratio to rotor {ae / re:.2f}; W_all ants {ants['e_Wall'].median():.3f} rotor {rotor['e_Wall'].median():.3f}")
for kk in (28, 30):
    if f"zeta{kk}" in ants.columns:
        dz = ants[f"zeta{kk}"].median() - rotor[f"zeta{kk}"].median()
        dd = ants[f"Dh{kk}"].median() - rotor[f"Dh{kk}"].median()
        P(f"4 spectrum zeta k={kk}: ants-rotor {dz:+.3f} (H-rough if >= 0.10)")
        P(f"5 hull D k={kk}: ants {ants[f'Dh{kk}'].median():.3f} rotor {rotor[f'Dh{kk}'].median():.3f} diff {dd:+.3f} (>=0.05; both in [1.0,1.4])")
for name, df in (("rotor", rotor), ("ants", ants)):
    d = (df["beta_out"] - df["beta_all"]).abs().max()
    P(f"6 {name}: max |beta_out - beta_all| = {d:.3f} (<= 0.03: {d <= 0.03})")
sc = res / "shape_check.csv"
if sc.exists():
    s = pl.read_csv(sc.read_text().replace("\n#", "\n#").splitlines() and "\n".join(l for l in sc.read_text().splitlines() if not l.startswith("#")).encode())
    h = pl.concat([load("ants"), load("rotor")]).select("spec", "k", "Wall")
    j = s.filter(pl.col("kind") == "cp").select("spec", "k", "Wsurf").join(h, on=["spec", "k"])
    P(f"\nrule-1 cross-check vs shape: {j.height} matched rows, max |Wall - Wsurf| = {(j['Wall'] - j['Wsurf']).abs().max():.4f}")
(res / "hull_stats.txt").write_text("\n".join(out) + "\n")
