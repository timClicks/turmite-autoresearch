"""Frozen run lists (README): P0b fillers, P1/P3 Pi cohort and composition-matched controls, P2 parents and mutants.
Reads rule strings and class filters only (no c). Writes results/lists/*.txt and results/lists/cohorts.csv.

usage: uv run --frozen experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/make_lists.py
"""
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/archive/2026-10-square-ring-fillers/scripts"))
from ring import pi_k  # noqa: E402

SEED = 20261025
OUT = EXP / "results/lists"


def lead(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


def primitive(r):
    n = len(r)
    return all(r != r[:d] * (n // d) for d in range(1, n) if n % d == 0)


def flip(r, p):
    return r[:p] + ("L" if r[p] == "R" else "R") + r[p + 1:]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    cen = pl.read_csv(ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(
        (pl.col("cls") == "blob") & (pl.col("c") > 0) & (pl.col("g_k").abs() < 0.05))
    rules = sorted(cen["rule"].to_list(), key=lambda r: (len(r), r))
    info = {r: (len(r), lead(r), r.count("R"), pi_k(r)) for r in rules}
    rows = []

    # P0b: the 25 census board fillers
    fillers = (ROOT / "experiments/archive/2026-10-square-ring-fillers/results/board_fillers.txt").read_text().split()
    (OUT / "p0_fillers.txt").write_text("\n".join(fillers) + "\n")
    rows += [(r, "p0_filler", "", pi_k(r) or 0, 0) for r in fillers]

    # P1/P3: Pi blobs with m >= 2, and up to 3 composition-matched controls each
    pis = [r for r in rules if info[r][3] is not None and info[r][1] >= 2]
    nonpi = [r for r in rules if info[r][3] is None]
    ctrl_all = []
    for r in pis:
        n, m, nr, _ = info[r]
        pool = []
        for dn, dr in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            pool = [q for q in nonpi if info[q][1] == m and info[q][0] == n + dn and info[q][2] == nr + dr]
            if pool:
                break
        pick = sorted(rng.choice(pool, size=min(3, len(pool)), replace=False).tolist()) if pool else []
        rows.append((r, "p1_pi", "", m, 0))
        rows += [(q, "p1_ctrl", r, m, 0) for q in pick]
        ctrl_all += pick
    (OUT / "p3_pi.txt").write_text("\n".join(pis) + "\n")
    (OUT / "p3_ctrl.txt").write_text("\n".join(sorted(set(ctrl_all), key=lambda r: (len(r), r))) + "\n")

    # P2: 30 non-Pi parents per m in {1,2,3}, n in 10..12; all single flips at p in [m+1, n-1]
    parents, mutants = [], []
    for m in (1, 2, 3):
        pool = [r for r in nonpi if info[r][1] == m and 10 <= info[r][0] <= 12]
        pick = sorted(rng.choice(pool, size=30, replace=False).tolist(), key=lambda r: (len(r), r))
        for r in pick:
            parents.append(r)
            rows.append((r, "p2_parent", "", m, 0))
            for p in range(m + 1, len(r)):
                q = flip(r, p)
                if primitive(q) and lead(q) == m:
                    mutants.append(q)
                    rows.append((q, "p2_mutant", r, m, p))
    (OUT / "p2_parents.txt").write_text("\n".join(parents) + "\n")
    (OUT / "p2_mutants.txt").write_text("\n".join(dict.fromkeys(mutants)) + "\n")
    pl.DataFrame(rows, schema=["rule", "role", "parent", "m", "pos"], orient="row").write_csv(OUT / "cohorts.csv")
    print(f"fillers {len(fillers)}; pi {len(pis)}; controls {len(ctrl_all)} ({len(set(ctrl_all))} distinct); "
          f"parents {len(parents)}; mutants {len(mutants)} ({len(set(mutants))} distinct)")


if __name__ == "__main__":
    main()
