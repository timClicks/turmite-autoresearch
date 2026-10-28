"""Evaluate predictions P1, P3, P4, P6, P7 from results/*.csv and write results/summary.json.

  uv run --no-project experiments/archive/2026-10-invariant-mining-snf/scripts/summarize.py
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

RES = Path(__file__).resolve().parents[1] / "results"


def rows(name):
    with open(RES / name) as f:
        return list(csv.DictReader(f))


def main() -> None:
    fp = rows("fingerprints.csv")
    uni = rows("universal.csv")
    p4 = rows("p4.csv")
    out: dict = {}

    # P1: fingerprint function of (family, n, nR); and the symmetry corollaries.
    key = {(r["family"], r["rule"]): (r["free"], r["factors"]) for r in fp}
    groups = defaultdict(set)
    for r in fp:
        groups[(r["family"], r["n"], r["nR"])].add((r["free"], r["factors"]))
    out["P1_exceptions"] = sum(1 for v in groups.values() if len(v) > 1)
    out["P1_rules_per_family"] = len({r["rule"] for r in fp})
    comp = lambda s: s.translate(str.maketrans("RL", "LR"))
    rot = lambda s, k: s[k:] + s[:k]
    sym = {"complement": 0, "reverse": 0, "rotations": 0, "checked": 0}
    for (fam, rule), v in key.items():
        sym["checked"] += 1
        sym["complement"] += key[(fam, comp(rule))] != v
        sym["reverse"] += key[(fam, rule[::-1])] != v
        sym["rotations"] += sum(key[(fam, rot(rule, k))] != v for k in range(1, len(rule)))
    out["P1_symmetry_differences"] = sym
    out["distinct_fingerprints_per_family_n"] = {
        f"{fam} n={n}": len({fp_ for (f2, n2, nr), fp_set in groups.items() if f2 == fam and n2 == str(n) for fp_ in fp_set})
        for fam in ("A0", "F1", "F2", "F3") for n in range(2, 9)
    }

    # P1b (post hoc, noticed in the by_counts table after P1 held): coarser still, (n, +-D mod 4, trivial)
    g = defaultdict(set)
    for r in fp:
        nR, n = int(r["nR"]), int(r["n"])
        D = (2 * nR - n) % 4
        g[(r["family"], n, min(D, (-D) % 4), nR in (0, n))].add((r["free"], r["factors"]))
    out["P1b_posthoc_groups"] = len(g)
    out["P1b_posthoc_groups_with_more_than_one_fingerprint"] = sum(1 for v in g.values() if len(v) > 1)

    # P3: universal F1
    u = {(r["family"], int(r["n"]), int(r["m"])): int(r["order"]) for r in uni}
    p3 = {}
    ok = True
    for n in range(2, 9):
        want2 = 8 if n % 2 == 0 else 4
        p3[f"n={n} m=2"] = (u[("F1", n, 2)], want2)
        ok &= u[("F1", n, 2)] == want2
        for p in (3, 5, 7):
            if ("F1", n, p) in u:
                want = p if n % p == 0 else 1
                p3[f"n={n} m={p}"] = (u[("F1", n, p)], want)
                ok &= u[("F1", n, p)] == want
    out["P3_all_as_predicted"] = ok
    out["P3_cells"] = p3

    # P6/P7: sublattice accounting at modulus n
    out["P6_orders_at_m_eq_n"] = {n: {f: u[(f, n, n)] for f in ("F1", "F2", "F3")} for n in range(2, 9)}
    out["P6_F2_gt_F1_all_n"] = all(u[("F2", n, n)] > u[("F1", n, n)] for n in range(2, 9))
    out["P7_F3_gt_F2_some_n"] = any(u[("F3", n, n)] > u[("F2", n, n)] for n in range(2, 9))
    out["P7_ns_where_F3_gt_F2"] = [n for n in range(2, 9) if u[("F3", n, n)] > u[("F2", n, n)]]

    # P4 (registered) and the post hoc refinement
    out["P4_registered_mismatches"] = sum(1 for r in p4 if r["pure_tape_heading_law"] != r["predicted"])
    out["P4_mismatch_D_values"] = sorted({r["D_mod4"] for r in p4 if r["pure_tape_heading_law"] != r["predicted"]})
    out["P4_mismatch_all_n_even"] = all(int(r["n"]) % 2 == 0 for r in p4 if r["pure_tape_heading_law"] != r["predicted"])
    out["P4_posthoc_mismatches"] = sum(1 for r in p4 if r["posthoc_faithful_law"] != r["predicted"])
    out["P4_rules"] = len(p4)
    out["P4_rules_with_D0"] = sum(int(r["predicted"]) for r in p4)

    # fingerprint table for F1 by (n, nR) with extra index over universal at m = 2, 4, 8
    f1 = {}
    for r in fp:
        if r["family"] == "F1":
            f1[(int(r["n"]), int(r["nR"]))] = r
    table = []
    for (n, nr), r in sorted(f1.items()):
        table.append({"n": n, "nR": nr, "D_mod4": (2 * nr - n) % 4, "free": r["free"], "factors": r["factors"],
                      **{f"extra_m{m}": int(r[f"order_m{m}"]) // u[("F1", n, m)] for m in (2, 4, 8)}})
    out["F1_by_counts"] = table
    (RES / "summary.json").write_text(json.dumps(out, indent=1))
    keys = ("P1_exceptions", "P1b_posthoc_groups", "P1b_posthoc_groups_with_more_than_one_fingerprint", "P1_symmetry_differences", "P3_all_as_predicted", "P6_F2_gt_F1_all_n", "P7_F3_gt_F2_some_n",
            "P7_ns_where_F3_gt_F2", "P4_registered_mismatches", "P4_mismatch_D_values", "P4_mismatch_all_n_even",
            "P4_posthoc_mismatches", "P4_rules")
    print(json.dumps({k: out[k] for k in keys}))


if __name__ == "__main__":
    main()
