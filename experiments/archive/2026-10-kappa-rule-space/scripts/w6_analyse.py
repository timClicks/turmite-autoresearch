# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""W6 pilot analysis (predictions P6.1-P6.6 in README, registered before the run).
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w6_analyse.py"""
import sys, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from scipy.stats import spearmanr
from kcommon import *

raw = pl.read_csv(EXP / "dumps" / "w6_probe.csv")
r = per_rule(raw).with_columns(seed=pl.col("rule").str.split("@").list.last().cast(int), base=pl.col("rule").str.split("@").list.first())
a22 = raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log())
r = r.join(a22, on="rule", how="left")
core = r.filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0)).with_columns(lk=pl.col("kappa").log())
n_specs = raw["rule"].n_unique(); esc = raw.filter(pl.col("escaped"))["rule"].n_unique()
out = [header("uv run scripts/w6_analyse.py"), f"runs in csv: {n_specs}; runs that escaped: {esc}; fitted: {r.height}; core-band: {core.height}"]
R = {}
for rule, g in core.group_by("base"):
    if g.height >= 4:
        R[rule[0]] = dict(lk=dict(zip(g["seed"], g["lk"])), A=dict(zip(g["seed"], g["lnA22"])))

def stats(d, key="lk"):
    v = np.array(list(d[key].values())); return v.mean(), v.std(ddof=1), len(v)

pairs = pl.read_csv(EXP / "results" / "w6_pairs.csv")
rows = []; tot = {"early": [0, 0], "late": [0, 0]}
for b, j, m in pairs.iter_rows():
    k = "early" if j <= 3 else "late"
    if b not in R: continue
    tot[k][1] += 1
    if m not in R: continue
    tot[k][0] += 1
    mb, sb, nb = stats(R[b]); mm, sm, nm = stats(R[m]); ab = stats(R[b], "A")[0]; am = stats(R[m], "A")[0]
    se = np.sqrt(sb ** 2 / nb + sm ** 2 / nm)
    rows.append(dict(base=b, pos=j, mutant=m, k=k, d=mm - mb, ad=abs(mm - mb), se=se, big=abs(mm - mb) > 3 * se, dA=am - ab,
                     letter="R->L" if b[j] == "R" else "L->R"))
P = pl.DataFrame(rows)
P.write_csv(EXP / "results" / "w6_pairs_scored.csv")
out.append(f"usable bases: {len(set(P['base']))} of 40 (rule needs >= 4 core-band runs); usable pairs: {P.height} of {pairs.height}")
for k in ("early", "late"):
    out.append(f"  {k}: usable mutants {tot[k][0]} of {tot[k][1]} (with usable base) = {tot[k][0] / max(tot[k][1], 1):.3f}")
us_all = (tot["early"][0] + tot["late"][0]) / (tot["early"][1] + tot["late"][1]); us_diff = abs(tot["early"][0] / tot["early"][1] - tot["late"][0] / tot["late"][1])
p66 = us_all >= 0.70 and us_diff < 0.15
out.append(f"P6.6 usable share overall {us_all:.3f} (>= 0.70), early-late difference {us_diff:.3f} (< 0.15): {'HELD' if p66 else 'FAILED'}")

brng = rng(21)
per_base = []
for b, g in P.group_by("base"):
    e = g.filter(pl.col("k") == "early")["ad"].to_numpy(); l = g.filter(pl.col("k") == "late")["ad"].to_numpy()
    ea = g.filter(pl.col("k") == "early")["dA"].abs().to_numpy(); la = g.filter(pl.col("k") == "late")["dA"].abs().to_numpy()
    if len(e) and len(l):
        per_base.append((np.median(e), np.median(l), np.median(ea), np.median(la)))
pb = np.array(per_base)
ratios = pb[:, 0] / pb[:, 1]
def boot(x, f, B=2000):
    return np.percentile([f(x[brng.integers(0, len(x), len(x))]) for _ in range(B)], [2.5, 97.5])
ci = boot(ratios, np.median)
out.append(f"P6.1 per-base median(early |d|)/median(late |d|): median ratio {np.median(ratios):.3f} (95% bootstrap CI over {len(ratios)} bases {ci[0]:.3f}..{ci[1]:.3f}); bar >= 1.3: {'HELD' if np.median(ratios) >= 1.3 else 'FAILED'}")
med_e = P.filter(pl.col("k") == "early")["ad"].median(); med_l = P.filter(pl.col("k") == "late")["ad"].median()
out.append(f"  pooled median |d|: early {med_e:.3f} (n={int((P['k']=='early').sum())}), late {med_l:.3f} (n={int((P['k']=='late').sum())})")

# replicate-noise null: two disjoint 3-seed halves of the same base (all 10 splits), matched pairing
null_meds = []
BASES = set(pairs["base"])
for b, d in R.items():
    if b not in BASES: continue
    if len(d["lk"]) < 6: continue
    seeds = sorted(d["lk"]); ds = []
    for h in itertools.combinations(seeds, 3):
        if seeds[0] not in h: continue
        o = [s for s in seeds if s not in h]
        ds.append(abs(np.mean([d["lk"][s] for s in h]) - np.mean([d["lk"][s] for s in o])))
    null_meds.append(np.median(ds))
nm_raw = float(np.median(null_meds)); nm_scaled = nm_raw / np.sqrt(2)
out.append(f"P6.2 replicate-noise null (3-vs-3 halves of the same base, {len(null_meds)} BASES (not mutants) with 6 core-band runs; the first run of this script wrongly used all 280 rules): median |d| {nm_raw:.3f}; scaled to 6-vs-6 pairs (x 1/sqrt2) {nm_scaled:.3f}")
out.append(f"  late median |d| / scaled null = {med_l / nm_scaled:.2f} (bar >= 1.5): {'HELD' if med_l / nm_scaled >= 1.5 else 'FAILED'}; vs raw null {med_l / nm_raw:.2f}; early / scaled null {med_e / nm_scaled:.2f}")
se_e = P.filter(pl.col("k") == "early")["se"].median(); se_l = P.filter(pl.col("k") == "late")["se"].median()
out.append(f"  median SE_diff: early {se_e:.3f}, late {se_l:.3f}")
be = P.filter(pl.col("k") == "early")["big"].mean(); bl = P.filter(pl.col("k") == "late")["big"].mean()
out.append(f"P6.3 share with |d| > 3 SE_diff: early {be:.3f}, late {bl:.3f}, difference {be - bl:+.3f} (bar >= +0.10): {'HELD' if be - bl >= 0.10 else 'FAILED'}")
out.append("P6.4 signed d (no bar): " + "; ".join(f"{k}/{L}: mean {g['d'].mean():+.3f} (n={g.height})" for (k, L), g in sorted(P.group_by(["k", "letter"]), key=lambda x: x[0])))
mae = P.filter(pl.col("k") == "early")["dA"].abs().median(); mal = P.filter(pl.col("k") == "late")["dA"].abs().median()
out.append(f"P6.5 median |d lnA(22)|: early {mae:.3f}, late {mal:.3f}; kappa contrast {med_e / med_l:.2f} vs area contrast {mae / mal:.2f} (ratio of contrasts {(med_e / med_l) / (mae / mal):.2f}; < 1 means area explains it). Spearman(|d ln kappa|, |d ln A|) = {spearmanr(P['ad'], P['dA'].abs())[0]:+.3f}")
out.append("Exploratory, by position j (median |d|, n): " + "; ".join(f"j={j}: {g['ad'].median():.3f} (n={g.height})" for (j,), g in sorted(P.group_by(["pos"]), key=lambda x: x[0]) if j <= 11))
by = P.group_by("pos").agg(m=pl.col("ad").median(), n=pl.len()).filter(pl.col("n") >= 8).sort("pos")
if by.height >= 4:
    out.append(f"  Spearman(position, median |d|) over j with >= 8 pairs: {spearmanr(by['pos'], by['m'])[0]:+.3f}")
# exploratory control: relative position (j/n) to separate "early letters" from "positions near the start of a short rule"
P2 = P.with_columns(rel=pl.col("pos") / pl.col("base").str.len_chars())
out.append(f"  Spearman(j/n, |d|) over all pairs: {spearmanr(P2['rel'], P2['ad'])[0]:+.3f}; Spearman(j, |d|): {spearmanr(P2['pos'], P2['ad'])[0]:+.3f}")
(EXP / "results" / "w6_stats.txt").write_text("\n".join(out) + "\n"); print("\n".join(out))
