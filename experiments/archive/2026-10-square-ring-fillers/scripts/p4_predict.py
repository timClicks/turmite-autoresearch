"""P4 step 1 (registered in README): exact quadratic E(G) = alpha G^2 + beta G + gamma through the committed exit steps on
boards 1024, 2048, 4096 (late-highway board check), and its predictions for 8192, 16384, 32768. Written before the new runs.

usage: python3 experiments/archive/2026-10-square-ring-fillers/scripts/p4_predict.py   -> results/p4_predictions.txt
"""
import csv
from fractions import Fraction
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
BC = ROOT / "experiments/archive/2026-10-late-highway-board-check/results"
RULES = {"RLRRRRL": 1, "RRLRR": 2, "RRRLRRRRR": 3}
GS = [1024, 2048, 4096]


def solve(points):
    m = [[Fraction(g * g), Fraction(g), Fraction(1), Fraction(e)] for g, e in points]
    for i in range(3):
        m[i] = [v / m[i][i] for v in m[i]]
        for j in range(3):
            if j != i:
                f = m[j][i]
                m[j] = [a - f * b for a, b in zip(m[j], m[i])]
    return [m[i][3] for i in range(3)]


def main():
    exits = {g: {r["rule"]: r for r in csv.DictReader(open(BC / f"board_{g}.csv"))} for g in GS}
    out = ["P4 predictions: exact quadratic through exit steps on boards 1024, 2048, 4096", "rule,k,alpha,beta,gamma,alpha==2(k+1),E8192,E16384,E32768"]
    for r, k in RULES.items():
        pts = []
        for g in GS:
            row = exits[g][r]
            assert row["stop"] == "escaped"
            pts.append((g, int(row["steps"])))
        a, b, c = solve(pts)
        pred = [a * g * g + b * g + c for g in (8192, 16384, 32768)]
        out.append(f"{r},{k},{a},{b},{c},{a == 2 * (k + 1)}," + ",".join(str(p) for p in pred))
    (EXP / "results/p4_predictions.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


main()
