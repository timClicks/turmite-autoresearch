"""Prediction P8: tile-free laws versus the confirmed highways of the census.

  uv run --no-project experiments/archive/2026-10-invariant-mining-snf/scripts/highways.py

A highway repeats every `period` steps with the heading restored and the ant displaced by (dx, dy).
A law whose cell weights are all zero does not see the laid tile, so over one period
  a*dx + b*dy + e*period + Phi(h, s_end) - Phi(h, s_start) = 0  (mod m)
must hold.  For F1 (no site class) the Phi term cancels, so the test is exact.  For F2/F3 the class
at the reference time is unknown, so the test is existential over the reachable (h, s): weaker.
Reads only committed census results.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments" / "_lib"))
import lawmod as lm  # noqa: E402

EXP = Path(__file__).resolve().parents[1]
SRC = ROOT / "experiments/archive/2026-10-census-sweeps" / "results"


def load() -> list[dict]:
    rows = {}
    for name in ("confirmed_v2.csv", "confirmed_1B.csv"):
        with open(SRC / name) as f:
            for r in csv.DictReader(f):
                if r["confirmed"].strip().lower() == "true":
                    rows[r["rule"]] = {"rule": r["rule"], "period": int(r["period"]), "dx": int(r["dx"]), "dy": int(r["dy"])}
    return list(rows.values())


def tile_free_generators(fam: lm.Family, rule: str, m: int):
    """Generators of the laws with every cell weight zero (columns of M restricted to non-w unknowns)."""
    n = len(rule)
    lay = lm.Layout(fam, n)
    k = lay.size()
    n_nonw = k - len(fam.classes()) * (n - 1)
    M = [row[:n_nonw] for row in lm.rule_rows(fam, rule)]
    sn = lm.snf(M, n_nonw)
    return sn, n_nonw, sn.generators(m)


def holds(fam: lm.Family, n: int, g: list[int], m: int, p: int, dx: int, dy: int) -> bool:
    vec = g + [0] * (lm.Layout(fam, n).size() - len(g))
    law = lm.unpack(fam, n, vec, m)
    base = law["a"] * dx + law["b"] * dy + law["e"] * p
    if fam.name in ("A0", "F1"):
        return base % m == 0
    # existential over the reachable (h, s): Phi(h, s_end) - Phi(h, s)
    for h, s in fam.reachable():
        s_end = s
        # displacement (dx, dy) changes the class by the same rule as unit steps, summed
        for _ in range(abs(dx)):
            s_end = fam.step_class(s_end, 1 if dx > 0 else -1, 0)
        for _ in range(abs(dy)):
            s_end = fam.step_class(s_end, 0, 1 if dy > 0 else -1)
        if (h, s_end) not in law["phi"]:
            continue
        if (base + law["phi"][(h, s_end)] - law["phi"][(h, s)]) % m == 0:
            return True
    return False


def main() -> None:
    hw = load()
    out = {"n_highways": len(hw), "violations": {}, "tile_free_group_orders_m2_m4_m8": {}}
    for fname in ("F1", "F2", "F3"):
        fam = lm.Family(fname)
        viol = []
        orders = Counter()
        for r in hw:
            rule, p, dx, dy = r["rule"], r["period"], r["dx"], r["dy"]
            n = len(rule)
            sn, _, _ = tile_free_generators(fam, rule, 2)
            orders[(sn.order(2), sn.order(4), sn.order(8))] += 1
            for m in sorted({2, 3, 4, 6, 8, 12, 16, n, 2 * n, 4 * n}):
                for g in tile_free_generators(fam, rule, m)[2]:
                    if not holds(fam, n, g, m, p, dx, dy):
                        viol.append({"rule": rule, "m": m, "period": p, "dx": dx, "dy": dy})
        out["violations"][fname] = {"count": len(viol), "examples": viol[:5]}
        out["tile_free_group_orders_m2_m4_m8"][fname] = {str(k): v for k, v in sorted(orders.items())}
    # Is the per-rule tile-free group the universal one?  Compare orders with the tile-free part of the universal
    # system for every n that occurs (equal orders of nested groups imply equal groups: universal <= rule's).
    out["universal_tile_free_orders_m2_m4_m8"] = {}
    out["rule_tile_free_equals_universal_for_all"] = {}
    for fname in ("F1", "F2", "F3"):
        fam = lm.Family(fname)
        ns = sorted({len(r["rule"]) for r in hw})
        uni = {}
        for n in ns:
            k = lm.Layout(fam, n).size()
            n_nonw = k - len(fam.classes()) * (n - 1)
            sn = lm.snf([row[:n_nonw] for row in lm.universal_rows(fam, n)], n_nonw)
            uni[n] = (sn.order(2), sn.order(4), sn.order(8))
        out["universal_tile_free_orders_m2_m4_m8"][fname] = {str(n): list(v) for n, v in uni.items()}
        ok = True
        for r in hw:
            n = len(r["rule"])
            sn, _, _ = tile_free_generators(fam, r["rule"], 2)
            ok &= (sn.order(2), sn.order(4), sn.order(8)) == uni[n]
        out["rule_tile_free_equals_universal_for_all"][fname] = ok
    (EXP / "results" / "highways_tilefree.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"n": out["n_highways"], "violations": {k: v["count"] for k, v in out["violations"].items()},
                      "orders": out["tile_free_group_orders_m2_m4_m8"],
                      "equals_universal": out["rule_tile_free_equals_universal_for_all"]}))


if __name__ == "__main__":
    main()
