# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Lattice c law, colours and circulations: tests T2 and P1-P6 of the README.
usage: uv run experiments/archive/2026-10-lattice-c-law-colours/scripts/analyse.py
Reads results/traces.jsonl and the parent's results/ants.csv (kept set, same filter as the parent's analyse.py), writes
results/analysis.txt. Deterministic (no randomness)."""
import json
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import theilslopes

HERE = Path(__file__).resolve().parents[1]
PAR = HERE.parents[2] / "experiments/archive/2026-10-lattice-c-law" / "results"
lines = []


def say(s=""):
    print(s)
    lines.append(s)


def slope(x, y):
    return float(np.polyfit(np.log(x), np.log(y), 1)[0])


def lead_of(rule):
    k = 1
    while k < len(rule) and rule[k] == rule[0]:
        k += 1
    return k


# ---- kept set, as the parent's analyse.py (windows 20..26, c>0, |g_k|<0.05, alpha_w in [0.28,0.40], not escaped)
ants = pl.read_csv(PAR / "ants.csv")
kept_specs = set()
csv26 = {}
for (lat, spec), g in ants.group_by(["lattice", "spec"], maintain_order=True):
    if g["escaped"][0]:
        continue
    g26 = g.filter(pl.col("k") == 26)
    if g26.height:
        csv26[(lat, spec[4:])] = (int(g26["new_cells"][0]), int(g26["boundary_steps"][0]))
    g = g.filter((pl.col("k") >= 20) & (pl.col("k") <= 26)).sort("k")
    if g.height < 7 or (g["new_cells"] == 0).any() or (g["boundary_steps"] == 0).any():
        continue
    t = 2.0 ** (g["k"].to_numpy() + 1)
    area, per = g["area"].to_numpy().astype(float), g["perimeter"].to_numpy().astype(float)
    B = g["boundary_steps"].to_numpy() / (t / 2)
    kap = B / (per / area)
    wmax = np.maximum(g["width"].to_numpy(), g["height"].to_numpy()).astype(float)
    c = float(g["new_cells"][-1] / g["boundary_steps"][-1])
    if c > 0 and abs(slope(t, kap)) < 0.05 and 0.28 <= slope(t, wmax) <= 0.40:
        kept_specs.add((lat, spec[4:]))

rows = []
for ln in (HERE / "results" / "traces.jsonl").read_text().splitlines():
    d = json.loads(ln)
    rule, lat = d["rule"], d["lattice"]
    ell = d["loop_len"]
    births, bsteps = d["births"], d["boundary_steps"]
    rc, rb = np.array(d["run_count"], float), np.array(d["run_boundary"], float)
    ln_idx = np.arange(len(rc))
    full = ln_idx >= ell
    n_circ = rc[full].sum()
    steps = (rc[full] * ln_idx[full]).sum()
    kill = next((ch for ch in rule if ch != rule[0]), "?")
    rows.append(dict(lattice=lat, rule=rule, stratum=rule[0], lead=lead_of(rule), ell=ell, esc=d["escaped"], births=births,
                     bsteps=bsteps, edge_sum=sum(d["edge"]), inv_c=bsteps / births if births else np.nan,
                     eps=n_circ / births if births else np.nan, R=steps / n_circ if n_circ else np.nan,
                     Cb=rb[full].sum() / births if births else np.nan, C=steps / births if births else np.nan,
                     hole=d["hole_births"] / births if births else np.nan, kill=kill,
                     kept=(lat, rule) in kept_specs))
df = pl.DataFrame(rows)

say("# Lattice c law, colours and circulations: analysis (scripts/analyse.py)")
say()
say("## T2 gate: births and boundary steps equal the parent's ants.csv window k=26; sum of per-colour edge steps equals boundary steps")
bad, n_cmp, n_skip = [], 0, 0
for r in df.iter_rows(named=True):
    key = (r["lattice"], r["rule"])
    if r["esc"] or key not in csv26:
        n_skip += 1
        continue
    n_cmp += 1
    if csv26[key] != (r["births"], r["bsteps"]) or r["edge_sum"] != r["bsteps"]:
        bad.append((key, csv26[key], (r["births"], r["bsteps"])))
say(f"compared {n_cmp} rules, skipped {n_skip} (escaped in tracer or parent); mismatches: {len(bad)}  ->  {'PASS' if not bad and n_cmp > 0 else 'FAIL'}")
for b in bad[:10]:
    say(f"  {b}")
if bad:
    say("T2 FAILED: no further claims.")
    Path(HERE / "results" / "analysis.txt").write_text("\n".join(lines) + "\n")
    raise SystemExit(1)

K = df.filter(pl.col("kept"))
STRATA = [("square", "R"), ("tri", "R"), ("hex", "R"), ("hex", "r")]
say()
say("## Kept rules per stratum and lead")
for lat, s0 in STRATA:
    g = K.filter((pl.col("lattice") == lat) & (pl.col("stratum") == s0))
    say(f"{lat}/{s0} ell={g['ell'][0]}  n per lead 1..5: " + " ".join(str(g.filter(pl.col('lead') == m).height) for m in range(1, 6)))


def med_by_lead(g, col, leads):
    out = []
    for m in leads:
        v = g.filter(pl.col("lead") == m)[col].drop_nans().drop_nulls().to_numpy()
        out.append(float(np.median(v)) if len(v) else np.nan)
    return np.array(out)


def lead_slope(g, col, leads):
    y = med_by_lead(g, col, leads)
    ok = ~np.isnan(y)
    return float(np.polyfit(np.array(leads)[ok], y[ok], 1)[0]) if ok.sum() >= 2 else np.nan


res = {}
say()
say("## Per-lead medians (kept rules) and slopes of the per-lead medians (primary) / Theil-Sen over rules (secondary)")
par = json.loads((PAR / "analysis.json").read_text())
for lat, s0 in STRATA:
    g = K.filter((pl.col("lattice") == lat) & (pl.col("stratum") == s0))
    ell = g["ell"][0]
    key = f"{lat}/{s0}"
    r = dict(ell=ell)
    for col in ["inv_c", "Cb", "C", "eps", "R", "hole"]:
        meds = med_by_lead(g, col, range(1, 6))
        say(f"{key:10} median {col:5} by lead 1..5: " + " ".join(f"{x:8.4f}" for x in meds))
        r[col + "_meds"] = meds.tolist()
    r["b_med"] = lead_slope(g, "inv_c", range(1, 6))
    r["Cb_slope"] = lead_slope(g, "Cb", range(1, 6))
    r["R_slope"] = lead_slope(g, "R", range(2, 6))
    r["eps3"] = med_by_lead(g, "eps", [3])[0]
    L, y = g["lead"].to_numpy().astype(float), g["inv_c"].to_numpy()
    r["b_ts"] = float(theilslopes(y, L)[0])
    r["b_ols"] = par["fits"][key]["b"] if "fits" in par and key in par["fits"] else None
    res[key] = r
    say(f"{key:10} b_med={r['b_med']:.3f}  b_TheilSen={r['b_ts']:.3f}  Cb slope={r['Cb_slope']:.3f}  R slope={r['R_slope']:.3f}  "
        f"R slope/ell={r['R_slope'] / ell:.3f}  eps(lead3)={r['eps3']:.4f}")

say()
say("## P1: Cb slope / b_med within [0.8, 1.2] in all four strata")
ok1 = True
for k, r in res.items():
    q = r["Cb_slope"] / r["b_med"]
    ok1 &= 0.8 <= q <= 1.2
    say(f"{k:10} {q:.3f}")
say(f"P1 {'HELD' if ok1 else 'FAILED'}")

say()
say("## P2: R slope / ell within [0.5, 1.1] in all four strata")
ok2 = True
for k, r in res.items():
    q = r["R_slope"] / r["ell"]
    ok2 &= 0.5 <= q <= 1.1
    say(f"{k:10} {q:.3f}")
say(f"P2 {'HELD' if ok2 else 'FAILED'}")

say()
say("## P3: eps (circulations per birth, lead 3, stratum median): ratios")
e = {k: r["eps3"] for k, r in res.items()}
r_ts = e["square/R"] / e["tri/R"]
r_hx = e["hex/R"] / e["hex/r"]
say(f"eps: square {e['square/R']:.4f}  tri {e['tri/R']:.4f}  hexR {e['hex/R']:.4f}  hexr {e['hex/r']:.4f}")
say(f"eps square / tri = {r_ts:.2f} (need >= 2.0)   eps hexR / hexr = {r_hx:.2f} (need >= 3.0)")
if r_ts >= 2.0 and r_hx >= 3.0:
    v3 = "SUPPORTED (eps carries the drop)"
elif 0.7 <= r_ts <= 1.4 and 0.7 <= r_hx <= 1.4:
    v3 = "RIVAL (eps flat; lambda carries it)"
else:
    v3 = "UNDECIDED"
say(f"P3 {v3}")

say()
say("## P4: Theil-Sen b vs the parent's OLS bootstrap CI")
for k, r in res.items():
    f = par.get("fits", par).get(k) if isinstance(par, dict) else None
    ci = f["b_ci"] if f else None
    if k == "hex/r":
        ok = 0.15 <= r["b_ts"] <= 0.45
        say(f"{k:10} TS b={r['b_ts']:.3f} in [0.15,0.45]: {ok}")
    else:
        ok = ci is not None and ci[0] <= r["b_ts"] <= ci[1]
        say(f"{k:10} TS b={r['b_ts']:.3f} parent CI {ci}: {ok}")

say()
say("## P5: hole births per birth (median over kept rules; hex r-lead vs R-lead)")
h_r = float(np.median(K.filter((pl.col("lattice") == "hex") & (pl.col("stratum") == "r"))["hole"].drop_nans().to_numpy()))
h_R = float(np.median(K.filter((pl.col("lattice") == "hex") & (pl.col("stratum") == "R"))["hole"].drop_nans().to_numpy()))
say(f"hex r {h_r:.5f}  hex R {h_R:.5f}  ratio r/R = {h_r / h_R if h_R else float('inf'):.2f} (need >= 2.0)")
for lat, s0 in STRATA:
    g = K.filter((pl.col("lattice") == lat) & (pl.col("stratum") == s0))
    say(f"  {lat}/{s0}: median hole/birth {float(np.median(g['hole'].to_numpy())):.5f}")

say()
say("## P6: hex R-lead split by killing letter, 1/c ~ a + b*lead per type")
g = K.filter((pl.col("lattice") == "hex") & (pl.col("stratum") == "R"))


def r2(L, y):
    X = np.column_stack([np.ones(len(L)), L])
    co = np.linalg.lstsq(X, y, rcond=None)[0]
    p = X @ co
    return co, 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()


co0, r20 = r2(g["lead"].to_numpy().astype(float), g["inv_c"].to_numpy())
say(f"pooled: n={g.height} a={co0[0]:.3f} b={co0[1]:.3f} R2={r20:.3f}")
num = den = 0.0
for kl in sorted(set(g["kill"].to_list())):
    gg = g.filter(pl.col("kill") == kl)
    if gg.height < 8 or len(set(gg["lead"].to_list())) < 3:
        say(f"  kill {kl}: n={gg.height} (too few / too few leads)")
        continue
    co, r2k = r2(gg["lead"].to_numpy().astype(float), gg["inv_c"].to_numpy())
    say(f"  kill {kl}: n={gg.height} a={co[0]:.3f} b={co[1]:.3f} R2={r2k:.3f}")
    num += gg.height * r2k
    den += gg.height
if den:
    say(f"weighted mean R2 = {num / den:.3f} (need >= 0.80)  ->  P6 {'HELD' if num / den >= 0.8 else 'FAILED'}")

Path(HERE / "results" / "analysis.txt").write_text("\n".join(lines) + "\n")
(HERE / "results" / "analysis.json").write_text(json.dumps(res, indent=1, default=float))
