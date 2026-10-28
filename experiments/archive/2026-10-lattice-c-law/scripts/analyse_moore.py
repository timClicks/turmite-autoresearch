# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Follow-up B (README): Moore lattice c law, b(l) models, B1-B6. usage: uv run .../analyse_moore.py -> results/analysis_moore.txt. Seed 20261020."""
from pathlib import Path
import numpy as np
import polars as pl

R = Path(__file__).resolve().parents[1] / "results"
SEED, NB, LO, HI, RW_LO, RW_HI = 20261020, 2000, 20, 26, 16, 22
lines = []


def say(s=""):
    print(s)
    lines.append(s)


def slope(x, y):
    return float(np.polyfit(np.log(x), np.log(y), 1)[0])


def kappa_unif(a, beta):
    p = a * (1 - beta)
    return 2 * (1 - 2 ** -(1 - p)) / (1 - p)


def per_run(df, lo, hi, need_unescaped):
    out = []
    for spec, g in df.group_by("spec", maintain_order=True):
        spec = spec[0] if isinstance(spec, tuple) else spec
        if need_unescaped and g["escaped"][0]:
            continue
        g = g.filter((pl.col("k") >= lo) & (pl.col("k") <= hi)).sort("k")
        if g.height < hi - lo + 1 or (g["new_cells"] == 0).any() or (g["boundary_steps"] == 0).any():
            continue
        t = 2.0 ** (g["k"].to_numpy() + 1)
        area, per = g["area"].to_numpy().astype(float), g["perimeter"].to_numpy().astype(float)
        kap = (g["boundary_steps"].to_numpy() / (t / 2)) / (per / area)
        wmax = np.maximum(g["width"].to_numpy(), g["height"].to_numpy()).astype(float)
        a, beta = slope(t, area), slope(area, per)
        out.append(dict(spec=spec, a=a, beta=beta, alpha_w=slope(t, wmax), g_k=slope(t, kap),
                        c=float(g["new_cells"][-1] / g["boundary_steps"][-1]), kappa=float(kap[-1]), kratio=float(kap[-1] / kappa_unif(a, beta))))
    return pl.DataFrame(out)


def lead_of(rule):
    k = 1
    while k < len(rule) and rule[k] == rule[0]:
        k += 1
    return k


def fit(L, y):
    return np.linalg.lstsq(np.column_stack([np.ones(len(L)), L]), y, rcond=None)[0]


ants = pl.read_csv(R / "moore_ants.csv")
ctl = pl.read_csv(R / "moore_controls.csv")
specs = [l.split(" ", 1)[1] for l in (R / "lists" / "moore_ants.txt").read_text().splitlines() if l.strip()]
cand = pl.DataFrame({"spec": specs}).with_columns(rule=pl.col("spec").str.slice(4), stratum=pl.col("spec").str.slice(4, 1)).with_columns(
    lead=pl.col("rule").map_elements(lead_of, return_dtype=pl.Int64))
j = cand.join(per_run(ants, LO, HI, True), on="spec", how="left")
j = j.with_columns(ran=pl.col("c").is_not_null(),
                   kept=(pl.col("c").is_not_null() & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05) & pl.col("alpha_w").is_between(0.28, 0.40) & (pl.col("beta") < 0.8)))
say("# Follow-up B: Moore lattice (scripts/analyse_moore.py; seed 20261020)")
say("\n## Retention (kept by F2 / 48) and alive (ran to 2^27)")
under = False
for s0, g in j.group_by("stratum", maintain_order=True):
    s0 = s0[0] if isinstance(s0, tuple) else s0
    kp = [int(g.filter(pl.col("lead") == m)["kept"].sum()) for m in range(1, 6)]
    al = [int(g.filter(pl.col("lead") == m)["ran"].sum()) for m in range(1, 6)]
    under |= any(x < 8 for x in kp)
    say(f"{s0}-lead kept {kp} alive {al}")
kept = j.filter(pl.col("kept"))
rng = np.random.default_rng(SEED)
say("\n## 1/c = a + b*lead, kept rules, 2000-draw rule bootstrap")
F, BS = {}, {}
for s0 in ["r", "R"]:
    g = kept.filter(pl.col("stratum") == s0)
    L, y = g["lead"].to_numpy().astype(float), 1 / g["c"].to_numpy()
    a_, b_ = fit(L, y)
    bs = np.array([fit(L[ix], y[ix]) for ix in (rng.integers(0, len(L), len(L)) for _ in range(NB)) if len(set(L[ix])) > 1])
    r2 = 1 - ((y - (a_ + b_ * L)) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    ci = np.percentile(bs, [2.5, 97.5], axis=0)
    F[s0] = dict(n=len(L), a=a_, b=b_, r2=r2, aci=ci[:, 0], bci=ci[:, 1])
    BS[s0] = bs
    med = [float(np.median(y[L == m])) if (L == m).any() else float("nan") for m in range(1, 6)]
    say(f"{s0}-lead (loop {8 if s0 == 'r' else 4}) n={len(L)} a={a_:.3f} [{ci[0, 0]:.3f},{ci[1, 0]:.3f}] b={b_:.3f} [{ci[0, 1]:.3f},{ci[1, 1]:.3f}] R2={r2:.3f}; per-lead median 1/c {[round(x, 2) for x in med]}")
n = min(len(BS["r"]), len(BS["R"]))
lo, hi = np.percentile(BS["r"][:n, 1] / BS["R"][:n, 1], [2.5, 97.5])
say(f"b_r/b_R = {F['r']['b'] / F['R']['b']:.3f} [{lo:.3f},{hi:.3f}]")
say("\n## Scorecard")
bR, bR_ci, br, br_ci = F["R"]["b"], F["R"]["bci"], F["r"]["b"], F["r"]["bci"]
say(f"B1 R-lead b in [0.55,0.85]: {bR:.3f} -> {0.55 <= bR <= 0.85}")
lin = (br < 0.12) and not (br_ci[0] <= 0.31 <= br_ci[1])
inv = 0.20 <= br <= 0.42
say(f"B2 r-lead b={br:.3f} [{br_ci[0]:.3f},{br_ci[1]:.3f}]: M-lin supported {lin}; M-inv supported {inv}")
say(f"   B1 consistency: M-lin l=4 pred 0.70 (dev {abs(bR - 0.70):.3f}); M-inv l=4 pred 0.62 (dev {abs(bR - 0.62):.3f}); rule: dev <= 0.15")
say(f"B3 b_r<b_R with ratio CI below 1: {hi < 1}")
say(f"B4 R2>=0.5 both: {F['r']['r2'] >= 0.5 and F['R']['r2'] >= 0.5}; >=8 kept per cell: {not under}")
say(f"B5 intercepts within 0.5 of 1.3: r {abs(F['r']['a'] - 1.3) <= 0.5}, R {abs(F['R']['a'] - 1.3) <= 0.5}")
mf = per_run(ctl.filter(pl.col("spec").str.starts_with("mf")), LO, HI, True)
rw = per_run(ctl.filter(pl.col("spec").str.starts_with("rw")), RW_LO, RW_HI, False)
ak = kept["kratio"].to_numpy()
say(f"B6 mean-field ratio {mf['kratio'].mean():.3f} (sd {mf['kratio'].std():.3f}, n={mf.height}) within 0.05 of 1: {abs(mf['kratio'].mean() - 1) <= 0.05}; rw ratio {rw['kratio'].mean():.3f} (n={rw.height}) >=1.10: {rw['kratio'].mean() >= 1.10}")
say(f"ant kappa ratio median {np.median(ak):.3f} (n={len(ak)}); rw c {rw['c'].mean():.3f}; ant median c {kept['c'].median():.3f}")
(R / "analysis_moore.txt").write_text("\n".join(lines) + "\n")
