# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W4 analysis of experiments/archive/2026-10-knockout-maps/dumps/w4_colourflux.csv (examples/kappa_rs_colourflux). Predictions: README W4 + 'W4 implementation notes'.
Analysis choices fixed before the run: runs whose area log-log slope over k=20..26 is outside [0.55, 0.85] are excluded from rule-level
statistics (the core-band alpha_w filter is not available without box sizes); stationary flag is the pool's independent |median g_k| < 0.05.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w4_stats.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from scipy.stats import spearmanr
from kcommon import *

df = pl.read_csv(EXP / "dumps" / "w4_colourflux.csv", infer_schema_length=0)
esc_runs = set(df.filter(pl.col("k") == "escaped")["rule"].to_list())
df = df.filter(pl.col("k") != "escaped")
vec = lambda s: np.array([int(x) for x in s.split(":")], dtype=np.int64)
runs = {}
for row in df.iter_rows(named=True):
    d = dict(k=int(row["k"]), area=int(row["area"]), per=int(row["perimeter"]), new=int(row["new_cells"]), B=int(row["boundary_steps"]),
             m=vec(row["steps_by_colour"]), b=vec(row["boundary_by_colour"]), nw=vec(row["new_by_colour"]), ha=vec(row["hist_all"]), hb=vec(row["hist_boundary"]))
    runs.setdefault(row["rule"], {})[d["k"]] = d
pool = pl.read_csv(EXP / "results" / "rules_pool.csv")
stat = {b: abs(g) < 0.05 for b, g in zip(pool["base"], pool["g_k"])}
out = [f"specs with windows: {len(runs)}; specs that escaped the board (some windows missing): {len(esc_runs)}"]

def kappa(w):
    steps = w["m"].sum()
    return (w["B"] / steps) / (w["per"] / w["area"])

# ---- identity checks -------------------------------------------------------------------------
bad_kappa = 0; tot = 0
for r, ws in runs.items():
    for k, w in ws.items():
        steps = w["m"].sum(); n = len(w["m"]); mk = w["m"] / steps
        kk = np.where(w["m"] > 0, (w["b"] / np.maximum(w["m"], 1)) / (w["per"] / w["area"]), 0.0)
        tot += 1
        if abs((mk * kk).sum() - kappa(w)) > 0.01 * abs(kappa(w)): bad_kappa += 1
out.append(f"P4.2 identity kappa = sum_k m_k kappa_k within 1%: violations {bad_kappa}/{tot} windows")

ant_runs = [r for r in runs if not r.startswith(("rotor:", "pw:"))]
viol = 0; chk = 0; worst = 0.0
for r in ant_runs:
    ws = runs[r]
    for k in sorted(ws):
        if k - 1 not in ws: continue
        a, b_ = ws[k - 1], ws[k]; n = len(b_["m"])
        dN = b_["ha"] - a["ha"]
        V = b_["m"]
        for j in range(n):
            pred = V[(j - 1) % n] - dN[j] + (b_["new"] if j == 0 else 0)  # V_j = V_{j-1} - dN_j (+ arrivals of fresh cells at colour 0)
            chk += 1
            if pred != V[j]:
                viol += 1; worst = max(worst, abs(pred - V[j]) / max(V[j], 1))
out.append(f"accounting identity V_j = V_(j-1) - dN_j (+ new cells for j=0), ants, consecutive windows: violations {viol}/{chk} colour-window pairs (worst relative gap {worst:.2e})")

# ---- conservation: delta = max_k |n m_k - 1| ----------------------------------------------------
rows = []
for r in ant_runs:
    for k, w in runs[r].items():
        n = len(w["m"]); steps = w["m"].sum()
        rows.append((r, r.split("@")[0], n, k, np.abs(n * w["m"] / steps - 1).max(), w["new"] / steps))
D = pl.DataFrame(rows, schema=["spec", "rule", "n", "k", "delta", "adot"], orient="row")
def blob_spec(ws):
    if not all(k in ws for k in range(20, 27)): return False
    a = np.polyfit(np.log([2.0 ** k for k in range(20, 27)]), np.log([ws[k]["area"] for k in range(20, 27)]), 1)[0]
    return 0.55 <= a <= 0.85
blob = {r for r in ant_runs if blob_spec(runs[r])}
hi = D.filter(pl.col("k") >= 24)
out.append(f"P4.1 delta=max_k|n m_k - 1| at k=24..26, ALL ant runs: share of run-windows below 0.03: {(hi['delta'] < 0.03).mean():.3f} ({hi.height} run-windows; includes highway builders and escapers)")
hb = hi.filter(pl.col("spec").is_in(list(blob)))
out.append(f"P4.1 same, BLOB runs only (area slope 0.55..0.85 over k=20..26, the registered 'blob-rule runs'): {(hb['delta'] < 0.03).mean():.3f} ({hb.height} run-windows, {len(blob)} runs); worst delta {hb['delta'].max():.3f}")
out.append("   (the script first printed only the ALL-runs line; the blob-runs line was added after seeing that the large deltas are highway builders with dA/dt = 0.25 per step)")
by_n = D.filter((pl.col("k") == 26) & pl.col("spec").is_in(list(blob))).group_by("n").agg(med=pl.col("delta").median(), mx=pl.col("delta").max(), frac=(pl.col("delta") < 0.03).mean(), cnt=pl.len()).sort("n")
out.append("   at k=26 by n, BLOB runs (median delta, max, share<0.03, runs): " + "; ".join(f"n={r['n']}: {r['med']:.3f}, {r['mx']:.3f}, {r['frac']:.2f}, {r['cnt']}" for r in by_n.iter_rows(named=True)))
sl = []
for spec in [x for x in D["spec"].unique().to_list() if x in blob]:
    d = D.filter((pl.col("spec") == spec) & (pl.col("k") >= 20)).sort("k")
    if d.height >= 5: sl.append(np.polyfit(d["k"].to_numpy() * np.log(2), np.log(d["delta"].to_numpy()), 1)[0])
sl = np.array(sl)
out.append(f"   delta vs t log-log slope per run (k=20..26): median {np.median(sl):+.3f}, IQR {np.percentile(sl, 25):+.3f}..{np.percentile(sl, 75):+.3f}; share within -0.33+-0.15: {np.mean(np.abs(sl + 0.33) <= 0.15):.2f}")
ad = D.filter((pl.col("k") == 26) & pl.col("spec").is_in(list(blob)))
out.append(f"   delta / (n * dA/dt per step) at k=26: median {np.median(ad['delta'].to_numpy() / (ad['n'].to_numpy() * ad['adot'].to_numpy())):.3f} (1.0 would mean delta is just the new-cell rate)")

# ---- rule-level table -----------------------------------------------------------------------------
rule_rows = []
for r in set(x.split("@")[0] for x in ant_runs):
    seeds = [x for x in ant_runs if x.split("@")[0] == r]
    kap = []; ks = []; e0 = []; e1 = []; er = []; lead = []; leadsh = []; kh = []; lnc = []; lnpa = []; lnadot = []; ok = 0
    for s in seeds:
        ws = runs[s]
        if 26 not in ws or any(k not in ws for k in range(20, 27)): continue
        t = np.array([2.0 ** k for k in range(20, 27)]); A = np.array([ws[k]["area"] for k in range(20, 27)], float)
        a = np.polyfit(np.log(t), np.log(A), 1)[0]
        if not (0.55 <= a <= 0.85): continue
        w = ws[26]; n = len(w["m"]); steps = w["m"].sum(); ok += 1
        kap.append(kappa(w)); new = w["new"]
        e0.append(w["b"][0] / new); e1.append(w["b"][1] / new if n > 1 else 0); er.append(w["b"][2:].sum() / new)
        lead.append(int(np.argmax(w["b"]))); leadsh.append(w["b"].max() / w["b"].sum())
        pi = w["ha"] / w["ha"].sum(); e = w["hb"] / w["hb"].sum()
        with np.errstate(divide="ignore", invalid="ignore"):
            khat = np.nansum(np.where(pi > 0, e / pi, 0.0)) / n
        kh.append(khat)
        c = new / w["B"]; lnc.append(np.log(c)); lnpa.append(np.log(w["per"] / w["area"])); lnadot.append(np.log(new / steps))
    if ok >= 4:
        rule_rows.append(dict(rule=r, n=len(r), nseeds=ok, kappa=np.mean(kap), lnk=np.mean(np.log(kap)), e0=np.mean(e0), e1=np.mean(e1), erest=np.mean(er),
                              lead=int(np.round(np.mean(lead))), leadshare=np.mean(leadsh), khat=np.mean(kh), lnc=np.mean(lnc), lnpa=np.mean(lnpa), lnadot=np.mean(lnadot),
                              stat=bool(stat.get(r, False))))
R = pl.DataFrame(rule_rows).sort("rule"); R.write_csv(EXP / "results" / "w4_rules.csv")
S = R.filter(pl.col("stat"))
out.append(f"\nrule-level: {R.height} pool/census ant rules with >= 4 usable seeds; stationary (pool flag): {S.height}; pool rules only: {int(R['rule'].is_in(pool['base'].to_list()).sum())}")

lead_le2 = (S["lead"] <= 2).mean()
out.append(f"recorded earlier: stationary rules whose leading boundary colour has index <= 2: {lead_le2:.3f} (prediction >= 0.60; near-trivial, see README)")
lk = R.filter(pl.col("kappa") > 3)
out.append(f"P4.3 rules with kappa>3: {lk.height}; leading colour supplies >= 60% of boundary steps in {(lk['leadshare'] >= 0.6).sum() if lk.height else 0} of them "
           f"(prediction: >= 80% of them); leading colour index counts: {dict(zip(*np.unique(lk['lead'].to_numpy(), return_counts=True))) if lk.height else {}}")
e = R.filter(pl.col("kappa") > 0)
rho = spearmanr(np.log(e["khat"].to_numpy()), e["lnk"].to_numpy())[0]; rho_s = spearmanr(np.log(S["khat"].to_numpy()), S["lnk"].to_numpy())[0] if S.height > 5 else float("nan")
lam = e["kappa"].to_numpy() / e["khat"].to_numpy()
out.append(f"P4.4 Spearman(ln khat, ln kappa): all {rho:+.3f}; stationary {rho_s:+.3f} -> {'HELD' if rho >= 0.4 else 'FAILED'} (all-rules reading)")
out.append(f"P4.5 lambda = kappa/khat: mean {lam.mean():.3f}, CV {lam.std() / lam.mean():.3f} (prediction CV >= 0.3) -> {'HELD' if lam.std() / lam.mean() >= 0.3 else 'FAILED'}")

# ---- bookkeeping decomposition (exploratory) ------------------------------------------------------
out.append("\nEXPLORATORY bookkeeping: ln kappa = ln(newcells/step) - ln c - ln(P/A) per rule (mean over seeds); share of var(ln kappa) carried by each term (cov(term, ln kappa)/var):")
for lab, sub in (("stationary", S), ("all", R)):
    v = sub["lnk"].to_numpy()
    terms = {"ln(newcells/step)": sub["lnadot"].to_numpy(), "-ln c": -sub["lnc"].to_numpy(), "-ln(P/A)": -sub["lnpa"].to_numpy()}
    out.append(f"  {lab}: var(ln kappa) {v.var():.4f}; " + "; ".join(f"{k}: {np.cov(t, v)[0, 1] / v.var():+.2f}" for k, t in terms.items()))
out.append("EXPLORATORY boundary-step budget per new cell (mean over rules): " +
           "; ".join(f"{lab}: e0 {sub['e0'].mean():.3f}, e1 {sub['e1'].mean():.3f}, e_rest {sub['erest'].mean():.3f}, sum {(sub['e0'] + sub['e1'] + sub['erest']).mean():.3f}" for lab, sub in (("stationary", S), ("all", R))))
for lab, sub in (("stationary", S), ("all", R)):
    v = sub["lnk"].to_numpy()
    out.append(f"  {lab}: corr(ln kappa, ln e1) {np.corrcoef(v, np.log(sub['e1'].to_numpy() + 1e-9))[0, 1]:+.3f}; corr(ln kappa, ln(1+e_rest)) {np.corrcoef(v, np.log(1 + sub['erest'].to_numpy()))[0, 1]:+.3f}; corr(ln kappa, -ln c) {np.corrcoef(v, -sub['lnc'].to_numpy())[0, 1]:+.3f}")

# ---- controls ---------------------------------------------------------------------------------------
rot = [kappa(runs[r][26]) for r in runs if r.startswith("rotor:") and 26 in runs[r]]
pw = [kappa(runs[r][26]) for r in runs if r.startswith("pw:") and 26 in runs[r]]
out.append(f"\nP4.6 controls at k=26: rotor kappa {np.mean(rot):.3f} +- {np.std(rot):.3f} (n={len(rot)}; prediction 2.00 +- 0.01); pw:0.5 kappa {np.mean(pw):.3f} +- {np.std(pw):.3f} (n={len(pw)})")
if rot:
    w = runs[[r for r in runs if r.startswith("rotor:")][0]][26]; n = 4; pi = w["ha"] / w["ha"].sum(); e_ = w["hb"] / w["hb"].sum()
    out.append(f"   rotor colour-class closure khat = {np.sum(e_ / pi) / n:.3f} (expected 1 against measured 2)")

txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/w4_stats.py") + "\n".join(out) + "\n"
(EXP / "results" / "w4_stats.txt").write_text(txt); print(txt)
