"""Q25: do cyclic rotations of a rule share bounding boxes more often than chance? Uses committed census CSVs only.

Unconditional design (the earlier 19-of-42 statistic conditioned on equal boxes and so cannot measure enrichment):
for the 702 survivors at 1e11, take every pair of rules of equal length; compare P(equal (width, height) at horizon H)
for pairs that are cyclic rotations (or rotations of the mirror image) of each other against all other equal-length pairs.
Horizons: 1e8 (sweep_v2), 1e9 (sweep_1B), 1e10 and 1e11 (h1e10, h1e11 chunks).
Run: uv run --frozen experiments/archive/2026-10-rotation-boxes/scripts/rotation_boxes.py
"""
import csv, glob, itertools, pathlib
from scipy.stats import fisher_exact

ROOT = pathlib.Path(__file__).resolve().parents[4]
X = ROOT / "experiments"
C = X / "2026-10-census-sweeps/results"
U = X / "2026-10-highways-unresolved-rules-1e10-1e11/results"


def load(paths):
    d = {}
    for p in paths:
        for r in csv.DictReader(open(p)):
            d[r["rule"]] = r
    return d


H = {"1e8": load([C / "sweep_v2.csv"]), "1e9": load([C / "sweep_1B.csv"]),
     "1e10": load(sorted(glob.glob(str(U / "h1e10/chunk_*.csv")))), "1e11": load(sorted(glob.glob(str(U / "h1e11/chunk_*.csv"))))}
surv = [r for r, v in H["1e11"].items() if v["stop"] == "budget"]
mirror = lambda r: r.translate(str.maketrans("LR", "RL"))
rots = lambda r: {r[i:] + r[:i] for i in range(len(r))}
is_rot = lambda a, b: b in rots(a) or b in rots(mirror(a))
box = lambda h, r: (H[h][r]["width"], H[h][r]["height"]) if r in H[h] and H[h][r]["stop"] == "budget" else None

pairs = [(a, b) for a, b in itertools.combinations(surv, 2) if len(a) == len(b) and a != b]
rot = [p for p in pairs if is_rot(*p)]
oth = [p for p in pairs if not is_rot(*p)]
# Control: rotations keep the number of R's, so also compare against non-rotation pairs with the same length AND number of R's.
same_comp = lambda a, b: a.count("R") == b.count("R") or a.count("R") == b.count("L")  # mirror swaps R and L
oth_c = [p for p in oth if same_comp(*p)]
print(f"{len(surv)} survivors; equal-length pairs {len(pairs)}: {len(rot)} rotation-related, {len(oth)} other")
print(f"{len(oth_c)} of the other pairs have matching composition (control).")
print(f"{'horizon':>8} {'rot equal':>10} {'rot n':>6} {'other equal':>12} {'other n':>8}  odds ratio  Fisher p   | composition-matched: equal/n  odds ratio  p")
out = []
for h in ("1e8", "1e9", "1e10", "1e11"):
    def eq(ps):
        v = [(box(h, a), box(h, b)) for a, b in ps]
        v = [(x, y) for x, y in v if x is not None and y is not None]
        return sum(x == y for x, y in v), len(v)
    (re, rn), (oe, on) = eq(rot), eq(oth)
    orr, p = fisher_exact([[re, rn - re], [oe, on - oe]])
    (ce, cn) = eq(oth_c)
    oc, pc = fisher_exact([[re, rn - re], [ce, cn - ce]])
    print(f"{h:>8} {re:>10} {rn:>6} {oe:>12} {on:>8}  {orr:>10.1f}  {p:.2g}   | {ce:>5}/{cn:<7} {oc:>10.1f}  {pc:.2g}")
    out.append((h, re, rn, oe, on, orr, p))
# among rotation pairs that share a box at 1e11, did they share it at every earlier horizon?
both = [p for p in rot if box("1e11", p[0]) == box("1e11", p[1])]
print(f"\nrotation pairs sharing a box at 1e11: {len(both)}")
for h in ("1e10", "1e9", "1e8"):
    k = [(box(h, a), box(h, b)) for a, b in both]
    print(f"  also equal at {h}: {sum(x is not None and x == y for x, y in k)} of {sum(x is not None and y is not None for x, y in k)} with data")
sizes = sorted(int(box('1e11', a)[0]) for a, b in both)
print("  widths at 1e11:", sizes)

# Pairs inside one rotation class are not independent: count classes (connected components of the "shares a box at 1e11" relation).
import collections
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
for a, b in both:
    parent[find(a)] = find(b)
comp = collections.defaultdict(set)
for a, b in both:
    comp[find(a)] |= {a, b}
print(f"\nthe {len(both)} pairs form {len(comp)} independent groups of sizes {sorted(len(v) for v in comp.values())}")
n_classes = len({min(rots(r) | rots(mirror(r))) for r in surv})
print(f"rotation/mirror classes among the survivors: {n_classes}; classes with >= 2 survivors: "
      f"{sum(1 for c in collections.Counter(min(rots(r) | rots(mirror(r))) for r in surv).values() if c > 1)}")

(pathlib.Path(__file__).resolve().parents[1] / "results/rotation_pairs_1e11.txt").write_text("".join(f"{a} {b}\n" for a, b in sorted(both)))
