# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""Registered fit for kappa-cutoff-mixed-effects (../README.md). Seed 20261016. Reads only the committed T1b seeds file."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mixed as M

root = Path(__file__).resolve().parents[1]
src = root.parents[2] / "experiments/archive/2026-10-t1-excursion-tomography" / "results" / "t1b_cutoff_seeds.csv"
rng = np.random.default_rng(20261016)
out, js = [], {}
KS = (22, 25)
B, R, NPERM, NSHUF, BSHUF = 1000, 500, 1000, 200, 200


def P(*a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    print(s, flush=True)


df = pl.read_csv(src).filter(~pl.col("escaped")).with_columns(pl.col("area").log().alias("lnA")).sort("rule", "k", "seed")
P("# fit.py; commit", subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip())
P("# input sha256[:16]", hashlib.sha256(src.read_bytes()).hexdigest()[:16], "| rows", df.height)
rules = []
for name in sorted(df["rule"].unique().to_list()):
    d = df.filter(pl.col("rule") == name)
    rules.append({"name": name, "k": {k: dict(
        seed=d.filter(pl.col("k") == k)["seed"].to_numpy(), lnA=d.filter(pl.col("k") == k)["lnA"].to_numpy(),
        lk=d.filter(pl.col("k") == k)["lnkappa"].to_numpy(), q=d.filter(pl.col("k") == k)["ln_ratio"].to_numpy()) for k in KS}})
P(f"rules {len(rules)}; seeds per rule/k min {min(len(r['k'][k]['seed']) for r in rules for k in KS)} "
  f"max {max(len(r['k'][k]['seed']) for r in rules for k in KS)}")
par = M.parity_split(rules)
P("parity split: X = even seeds, Y = odd seeds; direction A = covariates from X, ln_ratio from Y")


def ci(x):
    return np.percentile(x, [2.5, 97.5])


def report(k, direction):
    f1 = M.fit_direction(rules, par, k, direction, True)
    f0 = M.fit_direction(rules, par, k, direction, False)
    br, se = f1["b"][2], np.sqrt(f1["cov"][2, 2])
    r2_1, r2_0 = M.r2_oos(rules, par, k, f1, True, direction), M.r2_oos(rules, par, k, f0, False, direction)
    return f1, f0, br, se, r2_1, r2_0


results = {}
for k in KS:
    P(f"## k={k}")
    f1, f0, br, se, r2_1, r2_0 = report(k, "A")
    fb1, _, brB, seB, r2_1B, r2_0B = report(k, "B")
    P(f"direction A (parity): br={br:.4f} (REML SE {se:.4f}) bA={f1['b'][1]:.4f} b0={f1['b'][0]:.4f}; "
      f"ysd(rule means)={f1['ysd']:.4f} -> Std={br / f1['ysd']:.3f}")
    P(f"  s_u={np.sqrt(f1['su2']):.4f} s_e={np.sqrt(f1['se2']):.4f}; s_u^2 zA-only {f0['su2']:.4f} -> with zr {f1['su2']:.4f} "
      f"(share removed {1 - f1['su2'] / f0['su2']:.3f})")
    P(f"  out-of-sample R2 (44 rule means, frozen transform): M0 {r2_0:.3f}, M1 {r2_1:.3f}, dR2 {r2_1 - r2_0:+.3f}")
    P(f"direction B (parity, sensitivity): br={brB:.4f} (SE {seB:.4f}) Std={brB / fb1['ysd']:.3f}; dR2 {r2_1B - r2_0B:+.3f}")
    # bootstrap (rules resampled, fresh random split each replicate)
    bb, bs, bd = M.boot_br(rules, k, rng, B, "A", with_oos=True)
    P(f"rule-cluster bootstrap B={B}, fresh split per replicate: br 95% [{ci(bb)[0]:.4f}, {ci(bb)[1]:.4f}]; "
      f"Std 95% [{ci(bs)[0]:.3f}, {ci(bs)[1]:.3f}]; dR2 95% [{ci(bd)[0]:+.3f}, {ci(bd)[1]:+.3f}], frac dR2>0 {np.mean(bd > 0):.3f}")
    # random-split spread at the full rule set
    rb, rs_, rd = [], [], []
    for _ in range(R):
        sp = M.random_split(rules, rng)
        d = "A" if rng.random() < 0.5 else "B"
        g1 = M.fit_direction(rules, sp, k, d, True)
        g0 = M.fit_direction(rules, sp, k, d, False)
        rb.append(g1["b"][2])
        rs_.append(g1["b"][2] / g1["ysd"])
        rd.append(M.r2_oos(rules, sp, k, g1, True, d) - M.r2_oos(rules, sp, k, g0, False, d))
    P(f"random balanced splits R={R} (44 rules fixed): br mean {np.mean(rb):.4f} sd {np.std(rb, ddof=1):.4f} (between-split sd), "
      f"frac<0 {np.mean(np.array(rb) < 0):.3f}; Std mean {np.mean(rs_):.3f} sd {np.std(rs_, ddof=1):.3f}; "
      f"dR2 mean {np.mean(rd):+.3f} sd {np.std(rd, ddof=1):.3f}")
    # permutation of zr across rules
    A_, K_ = M.covariates(rules, par, k, "X")
    zA, zr = M.apply_tf(M.make_tf(A_, K_), A_, K_)
    gi, q = M.response_rows(rules, par, k, "Y")
    pv = []
    for _ in range(NPERM):
        z = zr[rng.permutation(len(zr))]
        pv.append(M.reml(q, np.column_stack([np.ones(len(gi)), zA[gi], z[gi]]), gi)["b"][2])
    p = (1 + np.sum(np.abs(pv) >= abs(br))) / (NPERM + 1)
    P(f"permutation of zr across rules ({NPERM}): null br sd {np.std(pv):.4f}; two-sided p = {p:.4f}")
    results[k] = dict(br=br, se=se, Std=br / f1["ysd"], ci_br=ci(bb).tolist(), ci_Std=ci(bs).tolist(), dR2=r2_1 - r2_0,
                      ci_dR2=ci(bd).tolist(), frac_dR2_pos=float(np.mean(bd > 0)), p_perm=p,
                      brB=brB, StdB=brB / fb1["ysd"], split_sd=float(np.std(rb, ddof=1)))

# pooled
P("## pooled over k=22,25 (k indicator, one random intercept per rule)")
pf = M.pooled_fit(rules, par, KS, "A")
brp, sep = pf["b"][3], np.sqrt(pf["cov"][3, 3])
pb = []
for _ in range(B):
    rs = M.resample_rules(rules, rng)
    sp = M.random_split(rs, rng)
    g = M.pooled_fit(rs, sp, KS, "A")
    pb.append((g["b"][3], g["b"][3] / g["ysd"]))
pb = np.array(pb)
P(f"direction A: br={brp:.4f} (REML SE {sep:.4f}) Std={brp / pf['ysd']:.3f}; s_u={np.sqrt(pf['su2']):.4f} s_e={np.sqrt(pf['se2']):.4f}")
P(f"bootstrap B={B}: br 95% [{ci(pb[:, 0])[0]:.4f}, {ci(pb[:, 0])[1]:.4f}]; Std 95% [{ci(pb[:, 1])[0]:.3f}, {ci(pb[:, 1])[1]:.3f}]")
js["pooled"] = dict(br=brp, Std=brp / pf["ysd"], ci_br=ci(pb[:, 0]).tolist(), ci_Std=ci(pb[:, 1]).tolist())

# whole-pipeline label shuffle: permute (lnA, lnkappa) arrays among rules with identical seed lists (equivalent to shuffling ln_ratio blocks)
P(f"## negative control: whole-pipeline label shuffle ({NSHUF} shuffles, bootstrap B={BSHUF} each; k={KS})")
groups = {}
for i, r in enumerate(rules):
    groups.setdefault(tuple(tuple(r["k"][k]["seed"].tolist()) for k in KS), []).append(i)
P("  groups of rules with identical seed lists (sizes):", sorted(len(v) for v in groups.values()))
excl = {k: 0 for k in KS}
shuf_br = {k: [] for k in KS}
for _ in range(NSHUF):
    perm = list(range(len(rules)))
    for idx in groups.values():
        sh = rng.permutation(idx)
        for a, b_ in zip(idx, sh):
            perm[a] = int(b_)
    new = [{"name": r["name"], "k": {k: dict(seed=r["k"][k]["seed"], lnA=rules[perm[i]]["k"][k]["lnA"],
            lk=rules[perm[i]]["k"][k]["lk"], q=r["k"][k]["q"]) for k in KS}} for i, r in enumerate(rules)]
    for k in KS:
        shuf_br[k].append(M.fit_direction(new, M.parity_split(new), k, "A", True)["b"][2])
        bb, _, _ = M.boot_br(new, k, rng, BSHUF)
        lo, hi = ci(bb)
        excl[k] += not (lo <= 0 <= hi)
for k in KS:
    P(f"  k={k}: shuffled br mean {np.mean(shuf_br[k]):+.4f} sd {np.std(shuf_br[k], ddof=1):.4f}; CI excludes 0 in {excl[k] / NSHUF:.3f} of shuffles")
    results[k]["shuffle_excl_rate"] = excl[k] / NSHUF

# verdicts vs registered criteria
P("## registered criteria")
ok1 = all(results[k]["br"] < 0 and results[k]["Std"] <= -0.30 and results[k]["ci_br"][1] < 0 for k in KS)
ok2 = all(results[k]["dR2"] >= 0.05 and results[k]["frac_dR2_pos"] >= 0.90 for k in KS)
ok3 = all(results[k]["p_perm"] <= 0.01 for k in KS)
ok4 = js["pooled"]["br"] < 0 and js["pooled"]["ci_br"][1] < 0 and js["pooled"]["Std"] <= -0.30
ok5 = all(results[k]["brB"] < 0 for k in KS)
for name, v in [("P1 sign/size/CI", ok1), ("P2 out-of-sample", ok2), ("P3 permutation", ok3), ("P4 pooled", ok4), ("P5 direction B sign", ok5)]:
    P(f"  {name}: {'HELD' if v else 'FAILED'}")
for k in KS:
    r = results[k]
    P(f"  k={k}: Std {r['Std']:.3f} (need <= -0.30); CI br excl 0: {r['ci_br'][1] < 0}; dR2 {r['dR2']:+.3f} (need >= +0.05), "
      f"frac>0 {r['frac_dR2_pos']:.3f} (need >= 0.90); p_perm {r['p_perm']:.4f} (need <= 0.01)")
js.update({str(k): results[k] for k in KS})
(root / "results" / "fit.txt").write_text("\n".join(out) + "\n")
(root / "results" / "fit.json").write_text(json.dumps(js, indent=1, default=float))
