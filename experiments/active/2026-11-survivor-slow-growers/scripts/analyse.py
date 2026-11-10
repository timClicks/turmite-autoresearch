"""P1, P2 and growing-only yields for the slow-grower registration (stdlib; reads committed CSVs only).

uv run --frozen experiments/active/2026-11-survivor-slow-growers/scripts/analyse.py
"""
import csv, glob, math, os, re
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.path.join(HERE, "../../archive")
CUT = 0.2

def chunks(d):
    rows = {}
    for f in sorted(glob.glob(os.path.join(ARCH, "2026-10-highways-unresolved-rules-1e10-1e11/results", d, "chunk_*.csv"))):
        for r in csv.DictReader(open(f)):
            rows[r["rule"]] = r
    return rows

def flat(path):
    return {r["rule"]: r for r in csv.DictReader(open(os.path.join(ARCH, "2026-10-census-sweeps/results", path)))}

side = lambda r: max(int(r["width"]), int(r["height"]))
s8, s9, s10, s11 = flat("sweep_v2.csv"), flat("sweep_1B.csv"), chunks("h1e10"), chunks("h1e11")
for name, d, steps in [("1e8", s8, "100000000"), ("1e9", s9, "1000000000")]:
    pass
cls = {r["rule"]: r for r in csv.DictReader(open(os.path.join(HERE, "results/classes.csv")))}
g = lambda a, b, k: math.log10(side(b[k]) / side(a[k]))

def budget_at(d, k, steps):
    return k in d and d[k]["stop"] == "budget" and d[k]["steps"] == steps

out = []
P = out.append
P("== P1: class persistence (g10 = log10 side(1e10)/side(1e9))")
for c in ("slow", "growing"):
    ks = [k for k, v in cls.items() if v["cls"] == c]
    missing = [k for k in ks if not budget_at(s9, k, "1000000000")]
    ok = [k for k in ks if k not in missing]
    same = sum((g(s9, s10, k) < CUT) == (c == "slow") for k in ok)
    P(f"{c}: n={len(ks)} with 1e9 box {len(ok)}; same class in previous decade {same}/{len(ok)} = {same/len(ok):.3f} "
      f"(registered: >= 0.90) -> {'HOLD' if same/len(ok) >= 0.9 else 'FAIL'}")
    if missing: P(f"  no 1e9 budget row: {' '.join(missing)}")
P("  g10 of slow rules that were growing in (1e9,1e10]:")
for k in sorted(k for k, v in cls.items() if v["cls"] == "slow" and budget_at(s9, k, "1000000000") and g(s9, s10, k) >= CUT):
    P(f"    {k} side 1e9 {side(s9[k])} 1e10 {side(s10[k])} 1e11 {side(s11[k])} g10 {g(s9, s10, k):.3f} g11 {float(cls[k]['g11']):.3f}")

txt = open(os.path.join(ARCH, "2026-10-late-highway-board-check/results/classify.txt")).read()
led = txt.split("== Ledger")[1]
conf = re.findall(r"│ (\(1e\d+,1e\d+\]) +┆ ([RL]+) +┆.*┆ confirmed │", led)
P("\n== P2: slow class in the decade before onset, genuine late highways")
X = 0; tot = 0
for coh, (a, b, steps_a) in [("(1e9,1e10]", (s8, s9, "100000000")), ("(1e10,1e11]", (s9, s10, "1000000000"))]:
    rs = [r for c, r in conf if c == coh]
    for r in rs:
        tot += 1
        gg = g(a, b, r)
        X += gg < CUT
        P(f"  {coh} {r}: side {side(a[r])} -> {side(b[r])}, g {gg:.3f} {'SLOW' if gg < CUT else ''}")
P(f"slow-before-onset X = {X}/{tot} (registered: X <= 1) -> {'HOLD' if X <= 1 else 'FAIL'}")

P("\n== Pools at decade start and growing-only genuine yields")
for coh, pool, (a, b) in [("(1e9,1e10]", s10, (s8, s9)), ("(1e10,1e11]", s11, (s9, s10))]:
    ks = sorted(pool)
    ns = sum(g(a, b, k) < CUT for k in ks)
    hi = [r for c, r in conf if c == coh]
    hg = sum(g(a, b, r) >= CUT for r in hi)
    ng = len(ks) - ns
    P(f"{coh}: pool {len(ks)}, slow {ns} ({ns/len(ks):.1%}), growing {ng}; genuine {len(hi)}/{len(ks)} = {len(hi)/len(ks):.2%}; "
      f"from growing {hg}/{ng} = {hg/ng:.2%}")
ns11 = sum(v["cls"] == "slow" for v in cls.values())
P(f"1e11 survivors: 702, slow {ns11}, growing {702-ns11} (Q19 at-risk pool if P1 and P2 hold)")
s = "\n".join(out); print(s)
open(os.path.join(HERE, "results/analysis.txt"), "w").write(s + "\n")
