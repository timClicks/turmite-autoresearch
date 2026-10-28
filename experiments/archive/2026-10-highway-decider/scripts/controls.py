"""Controls C1-C3 for the decider (stdlib only), on the dumps kept by run_all.py (the first --keep rules).

usage: python3 controls.py OUT_TXT [--sample 50]

C1: change one cell of C0 inside W cap (W + v)      -> must be rejected (clause b, or a if the changed cell is read).
C2: put a non-zero cell ahead of the window (strip)  -> must be rejected at clause d (or earlier).
C3: wrong drift (dx + 1)                              -> must be rejected at clause a.
Plus a unit test of `in_strip` against brute force. Each control is applied to the first K=30 dump of up to --sample certified rules.
"""
import csv
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decide

EXP = Path(__file__).resolve().parent.parent
DUMPS = EXP / "scratch" / "dumps"


def brute_in_strip(z, W, v, kmax=400):
    return any(W[0] <= z[0] - k * v[0] <= W[1] and W[2] <= z[1] - k * v[1] <= W[3] for k in range(1, kmax))


def main():
    out = open(sys.argv[1], "w")
    P = lambda *a: (print(*a), print(*a, file=out))
    sample = int(sys.argv[sys.argv.index("--sample") + 1]) if "--sample" in sys.argv else 50
    rng = random.Random(20261023)
    # unit test of in_strip
    bad = 0
    for _ in range(20000):
        W = sorted((rng.randint(-5, 5), rng.randint(-5, 5)))
        W2 = sorted((rng.randint(-5, 5), rng.randint(-5, 5)))
        Wt = (W[0], W[1], W2[0], W2[1])
        v = (rng.randint(-4, 4), rng.randint(-4, 4))
        if v == (0, 0):
            continue
        z = (rng.randint(-60, 60), rng.randint(-60, 60))
        if decide.in_strip(z, Wt, v) != brute_in_strip(z, Wt, v):
            bad += 1
    P(f"in_strip vs brute force: {bad} mismatches in 20000 random cases")
    # census rows
    census = {}
    for r in csv.DictReader(open(EXP.parents[2] / "experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv")):
        if r["confirmed"] == "true":
            census[r["rule"]] = r
    n_tested = {"C1": 0, "C2": 0, "C3": 0}
    n_rejected = {"C1": 0, "C2": 0, "C3": 0}
    escapes = []
    dirs = sorted(DUMPS.glob("*_*"))
    used = 0
    for d in dirs:
        rule = d.name.split("_", 1)[1]
        r = census[rule]
        Pn, dx, dy, onset = int(r["period"]), int(r["dx"]), int(r["dy"]), int(r["onset"])
        path = d / f"dump_{onset + 30 * Pn}.txt"
        if not path.exists():
            continue
        dump = decide.load(path)
        base = decide.decide(dump, Pn, (dx, dy))
        if not base["ok"]:
            continue
        used += 1
        if used > sample:
            break
        W = base["W"]
        v = (dx, dy)
        cells = dump["cells"]
        # C1: flip a cell in W cap (W+v)
        x0, x1 = max(W[0], W[0] + dx), min(W[1], W[1] + dx)
        y0, y1 = max(W[2], W[2] + dy), min(W[3], W[3] + dy)
        z = (rng.randint(x0, x1), rng.randint(y0, y1))
        c1 = dict(cells)
        c1[z] = (cells.get(z, 0) + 1) % len(rule)
        if c1[z] == 0:
            del c1[z]
        res = decide.decide(dict(dump, cells=c1), Pn, v)
        n_tested["C1"] += 1
        if not res["ok"]:
            n_rejected["C1"] += 1
        else:
            escapes.append(("C1", rule, z))
        # C2: a stray cell in the strip, outside W, k = 2 steps ahead of the window's centre
        cx, cy = (W[0] + W[1]) // 2 + 2 * dx, (W[2] + W[3]) // 2 + 2 * dy
        if not (W[0] <= cx <= W[1] and W[2] <= cy <= W[3]):
            c2 = dict(cells)
            c2[(cx, cy)] = 1
            res = decide.decide(dict(dump, cells=c2), Pn, v)
            n_tested["C2"] += 1
            if not res["ok"]:
                n_rejected["C2"] += 1
            else:
                escapes.append(("C2", rule, (cx, cy)))
        # C3: wrong drift
        res = decide.decide(dump, Pn, (dx + 1, dy))
        n_tested["C3"] += 1
        if not res["ok"] and res["clause"] == "a":
            n_rejected["C3"] += 1
        else:
            escapes.append(("C3", rule, res.get("clause")))
    P(f"certified rules used: {min(used, sample)}")
    for k in ("C1", "C2", "C3"):
        P(f"{k}: tested {n_tested[k]}, rejected {n_rejected[k]}")
    P(f"escapes: {escapes}")


main()
