"""Frozen class definition for the 702 survivors of the 1e11 census (uses 1e10 and 1e11 boxes only).

side(t) = max(width, height) of the bounding box at t steps (32768 board census CSVs).
g11 = log10(side(1e11) / side(1e10)). Class "slow" if g11 < 0.2, else "growing".
Cube-root growth of the side predicts g11 = 1/3; a bounded rule gives 0.
Writes results/classes.csv and results/p3_sample.txt (first 8 slow rules by sha256("survivor-slow:" + rule)).
Stdlib only:  python3 experiments/proposed/2026-11-survivor-slow-growers/scripts/classes.py
"""
import csv, glob, hashlib, math, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(HERE, "../../archive/2026-10-highways-unresolved-rules-1e10-1e11/results")
CUT = 0.2

def load(d):
    rows = {}
    for f in sorted(glob.glob(os.path.join(SRC, d, "chunk_*.csv"))):
        for r in csv.DictReader(open(f)):
            rows[r["rule"]] = r
    return rows

a, b = load("h1e10"), load("h1e11")
surv = sorted(k for k, v in b.items() if v["stop"] == "budget")
assert len(surv) == 702, len(surv)
out = []
for k in surv:
    s0 = max(int(a[k]["width"]), int(a[k]["height"]))
    s1 = max(int(b[k]["width"]), int(b[k]["height"]))
    g = math.log10(s1 / s0)
    out.append((k, s0, s1, round(g, 4), "slow" if g < CUT else "growing"))
with open(os.path.join(HERE, "results/classes.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["rule", "side_1e10", "side_1e11", "g11", "cls"]); w.writerows(out)
slow = [r[0] for r in out if r[4] == "slow"]
order = sorted(slow, key=lambda r: hashlib.sha256(("survivor-slow:" + r).encode()).hexdigest())
open(os.path.join(HERE, "results/p3_sample.txt"), "w").write("\n".join(order[:8]) + "\n")
print(f"survivors {len(out)}  slow {len(slow)}  growing {len(out) - len(slow)}")
print("p3 sample:", " ".join(order[:8]))
