"""P6 analysis (registered in README): classify the last 2^24 steps of each 2^27-step blank-board run.

usage: uv run --frozen experiments/archive/2026-10-square-ring-fillers/scripts/p6_analyse.py
   -> results/p6_classes.csv (per rule), results/p6_analysis.txt (registered tests, then labelled post hoc tables)
ring(k): max read <= 2k+2, each count 0..2k+1 within 5% (relative) of 1/(2k+2), count 2k+2 < 1%, new cells per step within
5% of 1/(2k+2). two-visit: counts 0 and 1 >= 90% of reads. other: the rest. Runs that left the board are flagged.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "scripts"))
from ring import parse_reads, pi_k  # noqa: E402


def classify(row):
    reads = parse_reads(row["reads"])
    W = int(row["win_steps"])
    maxread = max(reads)
    new = int(row["win_new"]) / W
    for k in range(1, 32):
        if maxread > 2 * k + 2:
            continue
        sh = [reads.get(v, 0) / W for v in range(2 * k + 2)]
        if (all(abs(s * (2 * k + 2) - 1) < 0.05 for s in sh) and reads.get(2 * k + 2, 0) / W < 0.01
                and abs(new * (2 * k + 2) - 1) < 0.05):
            return f"ring({k})", k
        break  # the smallest k admitted by the max read is the only candidate with uniform shares up to 2k+1
    if (reads.get(0, 0) + reads.get(1, 0)) / W >= 0.9:
        return "two-visit", None
    return "other", None


def main():
    mem = {r["rule"]: r for r in csv.DictReader(open(EXP / "results/p6_membership.csv"))}
    rows = list(csv.DictReader(open(EXP / "results/p6_footprint.csv")))
    out_rows = []
    for row in rows:
        r = row["spec"]
        cls, k = classify(row)
        m = mem[r]
        reads = parse_reads(row["reads"])
        W = int(row["win_steps"])
        out_rows.append(dict(rule=r, n=len(r), cls=cls, ring_k=k or "", pi_k=m["pi_k"], in_builders=m["in_builders"],
                             stop=row["stop"], steps=row["steps"], visited=row["visited"],
                             spc=f"{int(row['steps'])/int(row['visited']):.4f}", win_new_rate=f"{int(row['win_new'])/W:.5f}",
                             share01=f"{(reads.get(0,0)+reads.get(1,0))/W:.4f}", maxread=row["win_maxread"],
                             sweep_stop=m["sweep_stop"], census_cls=m["census_cls"]))
    with open(EXP / "results/p6_classes.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    ring = [o for o in out_rows if o["cls"].startswith("ring")]
    pis = [o for o in out_rows if o["pi_k"]]
    bld = [o for o in out_rows if o["in_builders"] == "True"]
    nec_fail = [o["rule"] for o in ring if str(o["ring_k"]) != o["pi_k"]]
    suff = sum(o["cls"].startswith("ring") for o in pis) / len(pis)
    b_ring = sum(o["cls"].startswith("ring") for o in bld) / len(bld)
    b_two = sum(o["cls"] == "two-visit" for o in bld) / len(bld)
    t = ["P6: census footprint classification (registered tests)",
         f"runs: {len(out_rows)} (escaped the 16384 board: {sum(o['stop'] == 'escaped' for o in out_rows)})",
         f"classes: {dict(Counter(o['cls'] for o in out_rows))}", "",
         f"(a) necessity: ring(k) rules {len(ring)}, of which not Pi(k) for the same k: {len(nec_fail)} {nec_fail} -> "
         f"{'HELD' if not nec_fail else 'FAILED'}",
         f"(b) sufficiency: Pi rules {len(pis)}, classified ring(k): {sum(o['cls'].startswith('ring') for o in pis)} = {suff:.1%} "
         f"(registered band 30%-90%) -> {'HELD' if 0.3 <= suff <= 0.9 else 'FAILED'}",
         f"(c) Q15: census builders {len(bld)}: ring(k) {b_ring:.1%} (>= 50% registered) -> {'HELD' if b_ring >= 0.5 else 'FAILED'}; "
         f"two-visit {b_two:.1%} (10%-30% registered) -> {'HELD' if 0.1 <= b_two <= 0.3 else 'FAILED'}; "
         f"other {1 - b_ring - b_two:.1%}", "",
         "Post hoc tables (not registered):"]
    t.append("ring(k) count by k: " + str(sorted(Counter(o["ring_k"] for o in ring).items())))
    t.append("Pi rules by k: classified ring / total: " + str(
        {k: (sum(o["cls"].startswith("ring") for o in pis if o["pi_k"] == k), sum(o["pi_k"] == k for o in pis))
         for k in sorted({o["pi_k"] for o in pis}, key=int)}))
    t.append("Pi rules not ring(k), by (class, sweep stop at 1e8, census cls): " + str(sorted(Counter(
        (o["cls"], o["sweep_stop"], o["census_cls"]) for o in pis if not o["cls"].startswith("ring")).items())))
    t.append("Pi rules not ring(k), by length n: " + str(sorted(Counter(o["n"] for o in pis if not o["cls"].startswith("ring")).items())))
    t.append("Pi rules ring(k), by length n: " + str(sorted(Counter(o["n"] for o in pis if o["cls"].startswith("ring")).items())))
    two = [o for o in bld if o["cls"] == "two-visit"]
    t.append(f"two-visit builders by prefix (first 3 letters): {sorted(Counter(o['rule'][:3] for o in two).items())}")
    oth = [o for o in bld if o["cls"] == "other"]
    t.append(f"'other' builders by prefix (first 3 letters): {sorted(Counter(o['rule'][:3] for o in oth).items())}")
    t.append("'other' builders (rule, spc, share of reads 0/1, max read, stop): " + "; ".join(
        f"{o['rule']} {o['spc']} {o['share01']} {o['maxread']} {o['stop']}" for o in oth[:60]))
    (EXP / "results/p6_analysis.txt").write_text("\n".join(t) + "\n")
    print("\n".join(t))


main()
