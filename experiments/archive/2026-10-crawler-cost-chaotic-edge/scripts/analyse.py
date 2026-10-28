"""Registered scoring of P0b, P1, P2 (N0, W1-W3) and P3 (R1-R3), exactly as in the README.

usage: uv run --frozen experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/analyse.py
   -> results/analysis.txt, results/analysis.json, results/p2_effects.csv, results/p1p3_rules.csv
"""
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RES = EXP / "results"
sys.path.insert(0, str(ROOT / "experiments/archive/2026-10-square-ring-fillers/scripts"))
from ring import pi_k  # noqa: E402

SEED, NB = 20261025, 2000
SEEN = {"RRLRRR", "RRRLRRRR", "RRRRLRRRRR"}
out, J = [], {}


def say(s=""):
    print(s)
    out.append(s)


def load(name):
    return {d["spec"]: d for d in map(json.loads, (RES / name).read_text().splitlines())}


def inv_c(d):
    return d["boundary_steps"] / d["births"] if d["births"] else float("nan")


def kept(d):
    return (not d["escaped"]) and d["births"] >= 200 and 1.3 <= d["area"] / d["area_t0"] <= 1.9


def chain2(d):
    ch = d["chain"]
    return ch[2] / sum(ch[1:]) if sum(ch[1:]) else float("nan")


def LL(m):
    return 1.363 + 0.696 * min(m, 8)


def phi(ic, m):
    return (ic - LL(m)) / (m + 1.25 - LL(m))


def verdict(ok):
    return "HELD" if ok else "FAILED"


coh = pl.read_csv(RES / "lists/cohorts.csv")
census = dict(pl.read_csv(ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
              .select("rule", "c").iter_rows())

# ---------------- P0b
say("P0b: edge tracer on the 25 census board fillers (blank 27 8192, window [2^26, 2^27])")
p0 = load("trace_p0_fillers.jsonl")
ok0 = True
for r in coh.filter(pl.col("role") == "p0_filler")["rule"]:
    d, k = p0[r], pi_k(r)
    ic, c2 = inv_c(d), chain2(d)
    ok = (not d["escaped"]) and abs(ic - (k + 1.25)) <= 0.05 and c2 <= 0.02
    ok0 &= ok
    say(f"  {r:12s} k={k} 1/c={ic:.4f} (k+5/4={k + 1.25}) chain2={c2:.4f} escaped={d['escaped']} {'ok' if ok else 'MISS'}")
say(f"P0b {verdict(ok0)}")
J["P0b"] = ok0

# ---------------- P1 (census c)
say()
say("P1: crawler limit on census c (probe_summary.csv); phi = (1/c - LL(m)) / (m + 5/4 - LL(m))")
pis = coh.filter(pl.col("role") == "p1_pi")
ctr = coh.filter(pl.col("role") == "p1_ctrl")
pi_rows = [(r, m, 1 / census[r], phi(1 / census[r], m)) for r, m in pis.select("rule", "m").iter_rows()]
ph = np.array([x[3] for x in pi_rows])
ph_unseen = np.array([x[3] for x in pi_rows if x[0] not in SEEN])
say(f"  n = {len(ph)}; median phi = {np.median(ph):.3f}; without the 3 seen rules (n = {len(ph_unseen)}): {np.median(ph_unseen):.3f}")
p1a = np.median(ph) >= 0.5 and np.median(ph_unseen) >= 0.5
say(f"P1a {verdict(p1a)}")
ctrl_of = {}
for q, par, m in ctr.select("rule", "parent", "m").iter_rows():
    ctrl_of.setdefault(par, []).append(phi(1 / census[q], m))
with_c = [(r, p) for r, m, ic, p in pi_rows if r in ctrl_of]
a_pi = np.array([p for _, p in with_c])
a_ct = np.concatenate([ctrl_of[r] for r, _ in with_c])
diff = np.median(a_pi) - np.median(a_ct)
rng = np.random.default_rng(SEED)
bs = []
for _ in range(NB):
    idx = rng.integers(0, len(with_c), len(with_c))
    bs.append(np.median(a_pi[idx]) - np.median(np.concatenate([ctrl_of[with_c[i][0]] for i in idx])))
lo, hi = np.percentile(bs, [2.5, 97.5])
p1b = diff >= 0.3 and lo > 0
say(f"  Pi with controls n = {len(with_c)}, control draws {len(a_ct)}: median phi Pi {np.median(a_pi):.3f}, "
    f"controls {np.median(a_ct):.3f}, difference {diff:.3f}, 95% CI [{lo:.3f}, {hi:.3f}]")
say(f"P1b {verdict(p1b)}")
over = [r for r, m, ic, p in pi_rows if ic > m + 1.25 + 0.10]
p1c = len(over) <= 0.10 * len(pi_rows)
say(f"  1/c > m + 5/4 + 0.10: {len(over)} of {len(pi_rows)} {over}")
say(f"P1c {verdict(p1c)}")
J["P1"] = {"median_phi": float(np.median(ph)), "median_phi_unseen": float(np.median(ph_unseen)), "P1a": bool(p1a),
           "diff": float(diff), "ci": [float(lo), float(hi)], "P1b": bool(p1b), "over": over, "P1c": bool(p1c)}

# ---------------- P2
say()
say("P2: single-letter flips (blank 24 4096, window [2^23, 2^24]); e = |1/c_mut - 1/c_par| / (1/c_par)")
par24, par25, mut = load("trace_p2_parents_24.jsonl"), load("trace_p2_parents_25.jsonl"), load("trace_p2_mutants.jsonl")
noise = [abs(inv_c(par25[r]) - inv_c(par24[r])) / inv_c(par24[r])
         for r in par24 if kept(par24[r]) and not par25[r]["escaped"] and par25[r]["births"] >= 200]
rows = []
for q, par, m, p in coh.filter(pl.col("role") == "p2_mutant").select("rule", "parent", "m", "pos").iter_rows():
    cls = "W" if m + 1 <= p <= 2 * m + 1 else ("corner" if p == 2 * m + 2 else "F")
    dp, dm = par24[par], mut[q]
    k_ = kept(dp) and kept(dm)
    ip, im = inv_c(dp), inv_c(dm)
    rows.append({"mutant": q, "parent": par, "m": m, "pos": p, "q": p - m, "cls": cls, "to_s0": par[p] != par[0],
                 "kept": k_, "parent_kept": kept(dp), "inv_c_par": ip, "inv_c_mut": im, "delta": im - ip,
                 "e": abs(im - ip) / ip})
eff = pl.DataFrame(rows)
eff.write_csv(RES / "p2_effects.csv")
k = eff.filter(pl.col("kept"))
eW = k.filter(pl.col("cls") == "W")["e"].to_numpy()
n0 = np.median(noise) <= 0.5 * np.median(eW)
say(f"  N0: parents kept at 24 and usable at 25: {len(noise)}; median relative 1/c change 2^24 -> 2^25 = {np.median(noise):.4f}; "
    f"median e(W) = {np.median(eW):.4f}; gate (noise <= 0.5 e(W)) {'PASSES' if n0 else 'FAILS'}")
say("  kept fraction (mutant and parent kept) by m and class:")
for m in (1, 2, 3):
    s = []
    for c in ("W", "corner", "F"):
        g = eff.filter((pl.col("m") == m) & (pl.col("cls") == c))
        s.append(f"{c} {g['kept'].sum()}/{len(g)}")
    say(f"    m={m}: " + ", ".join(s))
w1 = {}
for m in (1, 2, 3):
    rat = []
    for par, g in k.filter(pl.col("m") == m).group_by("parent"):
        w, f = g.filter(pl.col("cls") == "W")["e"], g.filter(pl.col("cls") == "F")["e"]
        if len(w) and len(f):
            rat.append(w.mean() / f.mean() if f.mean() > 0 else np.inf)
    med = float(np.median(rat)) if rat else float("nan")
    w1[m] = {"n_parents": len(rat), "median_ratio": med, "held": bool(rat) and med >= 2}
    say(f"  W1 m={m}: parents {len(rat)}, median mean e(W)/mean e(F) = {med:.3f} -> {verdict(w1[m]['held'])}")
e3 = k.filter((pl.col("m") == 3) & pl.col("q").is_in([3, 4]))["e"].to_numpy()
e1 = k.filter((pl.col("m") == 1) & pl.col("q").is_in([3, 4]))["e"].to_numpy()
w2r = np.median(e3) / np.median(e1)
w2 = w2r >= 1.5
say(f"  W2: q in {{3,4}}: median e m=3 {np.median(e3):.4f} (n={len(e3)}), m=1 {np.median(e1):.4f} (n={len(e1)}); ratio {w2r:.3f} -> {verdict(w2)}")
w3s = k.filter(pl.col("m").is_in([2, 3]) & (pl.col("cls") == "W"))
up = w3s.filter(pl.col("to_s0"))
dn = w3s.filter(~pl.col("to_s0"))
fu, fd = (up["delta"] > 0).mean(), (dn["delta"] < 0).mean()
w3 = fu >= 0.7 and fd >= 0.7
say(f"  W3: s_bar->s_0 flips with Delta>0: {fu:.3f} (n={len(up)}); s_0->s_bar with Delta<0: {fd:.3f} (n={len(dn)}) -> {verdict(w3)}")
if not n0:
    say("  (N0 failed: P2 is unresolved, finite-window noise; W verdicts above are not verdicts)")
say("  reported: median e and mean signed Delta by m and q (kept):")
for m in (1, 2, 3):
    g = k.filter(pl.col("m") == m).group_by("q").agg(pl.col("e").median().alias("med_e"), pl.col("delta").mean().alias("mean_d"),
                                                     pl.len().alias("n"), pl.col("cls").first()).sort("q")
    say(f"    m={m}: " + "; ".join(f"q={q} {c} e={e:.3f} d={d:+.3f} n={n}" for q, e, d, n, c in g.iter_rows()))
J["P2"] = {"noise": float(np.median(noise)), "eW": float(np.median(eW)), "N0": bool(n0), "W1": w1, "W2_ratio": float(w2r),
           "W2": bool(w2), "W3": [float(fu), float(fd)], "W3_held": bool(w3)}

# ---------------- P3
say()
say("P3: tracer on the Pi cohort and its controls (blank 24 4096); kept filter as P2")
tp, tc = load("trace_p3_pi.jsonl"), load("trace_p3_ctrl.jsonl")


def rbar(d, m):
    return float(np.mean([d["edge"][j] / d["births"] for j in range(1, m)]))


pr = [(r, m, tp[r]) for r, m in pis.select("rule", "m").iter_rows() if kept(tp[r])]
cr = [(q, m, tc[q]) for q, par, m in ctr.select("rule", "parent", "m").iter_rows() if kept(tc[q])]
rb_p, rb_c = np.array([rbar(d, m) for _, m, d in pr]), np.array([rbar(d, m) for _, m, d in cr])
c2_p, c2_c = np.array([chain2(d) for *_, d in pr]), np.array([chain2(d) for *_, d in cr])
r1 = np.median(rb_p) - np.median(rb_c) >= 0.05
r2 = np.median(c2_c) - np.median(c2_p) >= 0.05
ph_t = np.array([phi(inv_c(d), m) for _, m, d in pr])
r3 = np.median(ph_t) >= 0.5
say(f"  kept: Pi {len(pr)}/{len(pis)}, control draws {len(cr)}/{len(ctr)}")
say(f"  R1: median rbar Pi {np.median(rb_p):.3f}, controls {np.median(rb_c):.3f}, diff {np.median(rb_p) - np.median(rb_c):.3f} -> {verdict(r1)}")
say(f"  R2: median chain-2 share Pi {np.median(c2_p):.3f}, controls {np.median(c2_c):.3f} -> {verdict(r2)}")
say(f"  R3: median phi (tracer 1/c) Pi {np.median(ph_t):.3f} -> {verdict(r3)}")
J["P3"] = {"rbar": [float(np.median(rb_p)), float(np.median(rb_c))], "R1": bool(r1), "chain2": [float(np.median(c2_p)), float(np.median(c2_c))],
           "R2": bool(r2), "phi_tracer": float(np.median(ph_t)), "R3": bool(r3)}
pl.DataFrame([{"rule": r, "role": "pi", "m": m, "inv_c_census": 1 / census[r], "phi_census": phi(1 / census[r], m),
               "tracer_kept": kept(tp[r]), "inv_c_tracer": inv_c(tp[r]), "rbar": rbar(tp[r], m), "chain2": chain2(tp[r])}
              for r, m in pis.select("rule", "m").iter_rows()] +
             [{"rule": q, "role": f"ctrl:{par}", "m": m, "inv_c_census": 1 / census[q], "phi_census": phi(1 / census[q], m),
               "tracer_kept": kept(tc[q]), "inv_c_tracer": inv_c(tc[q]), "rbar": rbar(tc[q], m), "chain2": chain2(tc[q])}
              for q, par, m in ctr.select("rule", "parent", "m").iter_rows()]).write_csv(RES / "p1p3_rules.csv")

(RES / "analysis.txt").write_text("\n".join(out) + "\n")
(RES / "analysis.json").write_text(json.dumps(J, indent=1) + "\n")
