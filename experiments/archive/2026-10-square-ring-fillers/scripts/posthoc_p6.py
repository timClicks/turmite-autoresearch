"""POST HOC (not registered): what are the census builders that P6 did not class as ring(k)?

For every run in results/p6_footprint.csv, v* = round(steps per new cell in the last 2^24 steps). An "integer filler" has new-cell
rate within 2% of 1/v* and every count 0..v*-1 read with share within 5% (relative) of 1/v*, with no condition on counts above v*
(the registered ring(k) also required max read <= 2k+2 and < 1% reads of 2k+2). The turn table T(0..v*-1) is then tabulated.
usage: python3 experiments/archive/2026-10-square-ring-fillers/scripts/posthoc_p6.py   -> results/posthoc_p6.txt
"""
import csv
import sys
from collections import Counter
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "scripts"))
from ring import T, parse_reads  # noqa: E402


def main():
    cls = {r["rule"]: r for r in csv.DictReader(open(EXP / "results/p6_classes.csv"))}
    out = ["POST HOC: integer-cost fillers among the 446 P6 runs (criterion in the docstring; chosen after seeing P6)"]
    tables = Counter()
    rows = []
    for row in csv.DictReader(open(EXP / "results/p6_footprint.csv")):
        r = row["spec"]
        W = int(row["win_steps"])
        new = int(row["win_new"]) / W
        if new == 0:
            continue
        v = round(1 / new)
        reads = parse_reads(row["reads"])
        ok = v >= 2 and abs(new * v - 1) < 0.02 and all(abs(reads.get(c, 0) / W * v - 1) < 0.05 for c in range(v))
        if not ok:
            continue
        above = sum(c for k, c in reads.items() if k >= v) / W
        table = "".join(T(r, c) for c in range(v))
        c = cls[r]
        tables[(v, table, c["cls"].split("(")[0])] += 1
        rows.append(f"{r} v*={v} table={table} reads>=v*: {above:.5f} max={row['win_maxread']} P6class={c['cls']} builder={c['in_builders']}")
    out.append(f"integer fillers: {len(rows)}")
    out.append("by (v*, turn table on counts 0..v*-1, registered P6 class): count")
    for (v, t, k), n in sorted(tables.items()):
        out.append(f"  v*={v:2d} {t:14s} {k:10s} {n}")
    out.append("")
    out += rows
    (EXP / "results/posthoc_p6.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out[:60]))


main()
