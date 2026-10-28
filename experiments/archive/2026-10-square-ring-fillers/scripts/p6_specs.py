"""P6 run list (registered in README): union of the census builders (census.csv, cls == builder) and every rule of
sweep_2_12_100M.csv satisfying Pi(k) for some k >= 1. Writes results/p6_specs.txt (sorted by length, then rule) and
results/p6_membership.csv (rule, n, in_builders, pi_k, sweep stop/period at 1e8, census cls/spc).

usage: python3 experiments/archive/2026-10-square-ring-fillers/scripts/p6_specs.py
"""
import csv
import sys
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(EXP / "scripts"))
from ring import pi_k  # noqa: E402

CS = ROOT / "experiments/archive/2026-10-census-sweeps/results"


def main():
    census = {r["rule"]: r for r in csv.DictReader(open(CS / "census.csv"))}
    sweep = {r["rule"]: r for r in csv.DictReader(open(CS / "sweep_2_12_100M.csv"))}
    builders = {r for r, row in census.items() if row["cls"] == "builder"}
    pis = {r for r in sweep if pi_k(r) is not None}
    union = sorted(builders | pis, key=lambda r: (len(r), r))
    with open(EXP / "results/p6_membership.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["rule", "n", "in_builders", "pi_k", "sweep_stop", "sweep_period", "census_cls", "census_spc"])
        for r in union:
            s, c = sweep.get(r, {}), census.get(r, {})
            w.writerow([r, len(r), r in builders, pi_k(r) or "", s.get("stop", ""), s.get("period", ""), c.get("cls", ""), c.get("spc", "")])
    (EXP / "results/p6_specs.txt").write_text("\n".join(union) + "\n")
    print(f"builders {len(builders)}, Pi rules {len(pis)}, union {len(union)}, overlap {len(builders & pis)}")
    print("Pi rules missing from sweep enumeration check: canonical rules of length <= 12 with Pi:",
          sum(1 for n in range(2, 13) for i in range(2 ** (n - 1)) if pi_k("R" + format(i, f"0{n-1}b").replace("0", "R").replace("1", "L") if n > 1 else "R")))


main()
