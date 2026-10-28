"""Run the dumper and the decider on the census highways.

usage: python3 run_all.py DUMPER OUT_CSV [--limit N] [--grid 8192] [--ks 3,10,30,100,300] [--keep N]

For each rule in confirmed_v2.csv (census period P, drift (dx, dy), onset) the dumper writes configuration dumps at t = onset + K P for
each K, and at onset // 2 (control C4: before the onset). The decider is run on every dump with the census (P, dx, dy). Rows are written in
rule order regardless of worker order. Dumps of the first --keep rules and of every failing rule stay in scratch/dumps; other dumps are deleted.
"""
import csv
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decide

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = EXP.parents[2]
CENSUS = ROOT / "experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv"


def work(args):
    idx, row, dumper, grid, ks, keep = args
    rule, P, dx, dy, onset = row["rule"], int(row["period"]), int(row["dx"]), int(row["dy"]), int(row["onset"])
    times = sorted({onset // 2} | {onset + k * P for k in ks})
    d = EXP / "scratch" / "dumps" / f"{idx:04d}_{rule}"
    if d.exists():
        shutil.rmtree(d)
    r = subprocess.run([dumper, rule, ",".join(map(str, times)), str(P), str(grid), str(d)], capture_output=True, text=True)
    out = []
    if r.returncode != 0:
        return idx, [dict(rule=rule, K="all", t="", ok="error", clause="dumper", detail=r.stderr.strip()[:200])]
    pre = onset // 2
    any_fail = False
    for t in times:
        path = d / f"dump_{t}.txt"
        if not path.exists():
            out.append(dict(rule=rule, K=("pre" if t == pre else (t - onset) // P), t=t, ok="error", clause="dump", detail=r.stderr.strip()[:120]))
            any_fail = True
            continue
        res = decide.decide(decide.load(path), P, (dx, dy))
        K = "pre" if (t == pre and t != onset + 0) else (t - onset) // P
        out.append(dict(rule=rule, n=len(rule), P=P, dx=dx, dy=dy, onset=onset, K=K, t=t, ok=res["ok"], clause=res.get("clause", ""),
                        area=res["area"], oracle=res["oracle"], detail=res.get("detail", "")))
        if K != "pre" and not res["ok"]:
            any_fail = True
    if idx >= keep and not any_fail:
        shutil.rmtree(d, ignore_errors=True)
    return idx, out


def main():
    dumper, out_csv = sys.argv[1], sys.argv[2]
    opt = lambda name, default: sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default
    limit = int(opt("--limit", 10**9))
    grid = int(opt("--grid", 8192))
    ks = [int(k) for k in opt("--ks", "3,10,30,100,300").split(",")]
    keep = int(opt("--keep", 0))
    rows = list(csv.DictReader(open(CENSUS)))
    rows = [r for r in rows if r["confirmed"] == "true"][:limit]
    jobs = [(i, r, dumper, grid, ks, keep) for i, r in enumerate(rows)]
    t0 = time.time()
    results = {}
    with mp.Pool(int(os.environ.get("DECIDER_PROCS", "6"))) as pool:
        for idx, out in pool.imap_unordered(work, jobs):
            results[idx] = out
    cols = ["rule", "n", "P", "dx", "dy", "onset", "K", "t", "ok", "clause", "area", "oracle", "detail"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i in sorted(results):
            for rec in results[i]:
                w.writerow({c: rec.get(c, "") for c in cols})
    print(f"{len(rows)} rules, wall {time.time() - t0:.0f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
