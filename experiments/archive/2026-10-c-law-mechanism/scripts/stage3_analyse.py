# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Stage 3 (README, with the 'Stage 3 deviation' restatement): sparse-background dose-response B1'-B5.
usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage3_analyse.py"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import polars as pl

root = Path(__file__).resolve().parents[4]
R = root / "experiments/archive/2026-10-c-law-mechanism/results"
DS = [0.0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0]
DSP = [0.0, 0.02, 0.05, 0.1, 0.2]          # primary densities (>= 94% kept)
lines, res = [], {}


def say(s=""):
    print(s)
    lines.append(s)


def lead(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


def canon(r):
    return r if r[0] == "R" else r.translate(str.maketrans("LR", "RL"))


cen = pl.read_csv(root / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter((pl.col("cls") == "blob") & (pl.col("c") > 0))
inv_cen = {r: 1 / c for r, c in zip(cen["rule"], cen["c"])}
runs = defaultdict(list)           # (rule, d) -> list of (kept, c, escaped)
for l in (R / "trace_sbg.jsonl").read_text().splitlines():
    d = json.loads(l)
    _, rule, seed, dens = d["spec"].split(":")
    kept = (not d["escaped"]) and d["births"] >= 200 and d["area_t0"] > 0 and 1.3 <= d["area"] / d["area_t0"] <= 1.9
    runs[(rule, float(dens))].append((kept, d["births"] / d["boundary_steps"] if d["boundary_steps"] else np.nan, d["escaped"]))
rules = sorted({k[0] for k in runs}, key=lambda r: (lead(r), r))
L = {r: min(lead(r), 5) for r in rules}
inv = {}
for (r, d), v in runs.items():
    ks = [c for kept, c, _ in v if kept]
    if len(ks) >= (1 if d == 0 else 2):
        inv[(r, d)] = float(np.mean(1 / np.array(ks)))
cohort = [r for r in rules if all((r, d) in inv for d in DSP)]
cohort2 = [r for r in cohort if (r, 0.4) in inv]
res["cohort"] = dict(n=len(cohort), n_with_d04=len(cohort2), by_lead={m: sum(1 for r in cohort if L[r] == m) for m in range(1, 6)},
                     by_lead_d04={m: sum(1 for r in cohort2 if L[r] == m) for m in range(1, 6)}, total=len(rules))
say(f"rules {len(rules)}; primary cohort (valid at every d <= 0.2): {len(cohort)}, by lead " + ", ".join(f"{m}:{res['cohort']['by_lead'][m]}" for m in range(1, 6)) +
    f"; with d=0.4 valid too: {len(cohort2)}, by lead " + ", ".join(f"{m}:{res['cohort']['by_lead_d04'][m]}" for m in range(1, 6)))
say("kept fraction of runs by density (rows) and lead (columns 1..5), then escaped fraction:")
for d in DS:
    kf = [np.mean([x[0] for r in rules if L[r] == m for x in runs[(r, d)]]) for m in range(1, 6)]
    ef = [np.mean([x[2] for r in rules if L[r] == m for x in runs[(r, d)]]) for m in range(1, 6)]
    say(f"  d={d:<5}: " + " ".join(f"{x:.2f}" for x in kf) + "   escaped " + " ".join(f"{x:.2f}" for x in ef))

rng = np.random.default_rng(20261019)


def regress(rs, d, table):
    x = np.array([L[r] for r in rs], float)
    y = np.array([table[(r, d)] for r in rs])
    b, a = np.polyfit(x, y, 1)
    bs = []
    for _ in range(2000):
        i = rng.integers(0, len(x), len(x))
        if np.ptp(x[i]) > 0:
            bs.append(np.polyfit(x[i], y[i], 1)[0])
    return a, b, np.percentile(bs, [2.5, 97.5])


# mixture prediction table
mix, nmix = {}, 0
for r in rules:
    rots = [inv_cen[canon(r[j:] + r[:j])] for j in range(1, len(r)) if canon(r[j:] + r[:j]) in inv_cen]
    if r in inv_cen and len(rots) >= (len(r) - 1) / 2:
        ph = float(np.mean(rots))
        for d in DS:
            mix[(r, d)] = (1 - d) * inv_cen[r] + d * ph
        nmix += 1
say(f"mixture predictions available for {nmix} of {len(rules)} rules")
cm = [r for r in cohort if (r, 0.0) in mix]
res["fit"] = {}
fit = {}
for d in DSP:
    a, b, ci = regress(cohort, d, inv)
    am, bm, _ = regress(cm, d, mix)
    fit[d] = (a, b, ci, am, bm)
    res["fit"][str(d)] = dict(a=float(a), b=float(b), ci_b=ci.tolist(), mix_a=float(am), mix_b=float(bm))
    say(f"d={d:<5}: observed 1/c = {a:.3f} + {b:.3f} lead  b CI [{ci[0]:.3f}, {ci[1]:.3f}]; mixture (n={len(cm)}) {am:.3f} + {bm:.3f} lead; "
        f"mean 1/c by lead " + " ".join(f"{np.mean([inv[(r, d)] for r in cohort if L[r] == m]):.2f}" for m in range(1, 6)))
# secondary: d = 0.4 survivors, with d=0 on the same rules for a like-for-like slope
for d in (0.0, 0.4):
    a, b, ci = regress(cohort2, d, inv)
    res["fit"][f"secondary_{d}"] = dict(n=len(cohort2), a=float(a), b=float(b), ci_b=ci.tolist())
    say(f"secondary cohort (n={len(cohort2)}), d={d}: 1/c = {a:.3f} + {b:.3f} lead  b CI [{ci[0]:.3f}, {ci[1]:.3f}]")
res["B1p"] = {str(d): dict(b_obs=float(fit[d][1]), b_mix=float(fit[d][4]), ok=bool(abs(fit[d][1] - fit[d][4]) <= 0.10)) for d in (0.1, 0.2)}
res["B1p"]["passed"] = bool(all(v["ok"] for v in res["B1p"].values()))
res["B2p"] = dict(passed=bool(all(fit[DSP[i + 1]][1] <= fit[DSP[i]][1] + 0.07 for i in range(len(DSP) - 1))),
                  b=[float(fit[d][1]) for d in DSP])
a_all = [fit[d][0] for d in DSP] + [res["fit"]["secondary_0.4"]["a"]]
res["B4p"] = dict(a_range=[float(min(a_all)), float(max(a_all))], passed=bool(all(1.0 <= a <= 2.0 for a in a_all)))
say(f"B1' |b_obs - b_mix|: " + ", ".join(f"d={d}: {fit[d][1]:.3f} vs {fit[d][4]:.3f}" for d in (0.1, 0.2)) + f" -> {'PASS' if res['B1p']['passed'] else 'FAIL'}")
say(f"B2' b(d) along d<=0.2: " + " ".join(f"{fit[d][1]:.3f}" for d in DSP) + f" -> {'PASS' if res['B2p']['passed'] else 'FAIL'}")
say(f"B4' intercepts (d<=0.2 and d=0.4 secondary) range [{min(a_all):.3f}, {max(a_all):.3f}] -> {'PASS' if res['B4p']['passed'] else 'FAIL'}")
# B3'
pred, obs, tag = [], [], []
for r in cm:
    for d in (0.1, 0.2):
        pred.append(mix[(r, d)])
        obs.append(inv[(r, d)])
        tag.append(d)
pred, obs, tag = map(np.array, (pred, obs, tag))
r2 = 1 - ((obs - pred) ** 2).sum() / ((obs - obs.mean()) ** 2).sum()
rel = np.median(np.abs(pred - obs) / obs)
# the null of no density effect: predict 1/c(d) by the observed d=0 value (blank-ground c of the same rule)
nul = np.array([inv[(r, 0.0)] for r in cm for d in (0.1, 0.2)])
r2n = 1 - ((obs - nul) ** 2).sum() / ((obs - obs.mean()) ** 2).sum()
reln = np.median(np.abs(nul - obs) / obs)
res["B3p"] = dict(n_cells=len(pred), r2=float(r2), median_rel=float(rel), null_d0_r2=float(r2n), null_d0_median_rel=float(reln), passed=bool(r2 >= 0.5 and rel <= 0.2))
say(f"B3' mixture on d in {{0.1, 0.2}}: {len(pred)} cells ({len(cm)} rules): R2 {r2:.3f}, median |rel err| of 1/c {rel:.3f} -> {'PASS' if res['B3p']['passed'] else 'FAIL'}; "
    f"no-density-effect null (1/c at d=0): R2 {r2n:.3f}, median rel {reln:.3f}")
for d in (0.1, 0.2):
    s = tag == d
    say(f"   d={d}: mean observed 1/c {obs[s].mean():.3f}, mixture {pred[s].mean():.3f}, d=0 value {nul[s].mean():.3f}")


# B5
def kfrac(ms, d):
    v = [x[0] for r in rules if L[r] in ms for x in runs[(r, d)]]
    return float(np.mean(v)), len(v)


for d in (1.0, 0.4):
    lo, hi = kfrac({1, 2}, d), kfrac({4, 5}, d)
    res[f"B5_d{d}"] = dict(lead12=lo, lead45=hi, diff=lo[0] - hi[0], passed=bool(lo[0] - hi[0] >= 0.10))
    say(f"B5 at d={d}: kept fraction lead<=2 {lo[0]:.2f} (n={lo[1]}), lead>=4 {hi[0]:.2f} (n={hi[1]}) -> {'PASS' if res[f'B5_d{d}']['passed'] else 'FAIL'}")
(R / "stage3_analysis.json").write_text(json.dumps(res, indent=1, default=float))
(R / "stage3_analysis.txt").write_text("\n".join(lines) + "\n")
