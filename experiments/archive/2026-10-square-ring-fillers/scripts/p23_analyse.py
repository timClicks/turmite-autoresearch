"""P2/P3 analysis (registered in README). Reads scratch/frontlog/RULE/ (front logs) and results/p3_footprint.csv.

usage: python3 experiments/archive/2026-10-square-ring-fillers/scripts/p23_analyse.py   -> results/p23_analysis.txt
P2: clock.py (2026-10-sweeper-generalisation, registered criterion) with cycle P = 1 in each of the four directions on the
window [2^26, 2^27]; holds for a rule if every direction is EXACT (>= 95% zero residual, p <= 6) with a = 8(k+1); p <= 2 noted.
P3: last 2^26 steps: max read 2k+2; each count 0..2k+1 within 2% (relative) of 1/(2k+2); count 2k+2 < 0.5%; new cells per
step within 2% of 1/(2k+2).
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(EXP / "scripts"))
from ring import parse_reads, pi_k  # noqa: E402

CLOCK = ROOT / "experiments/archive/2026-10-sweeper-generalisation/scripts/clock.py"
LO, HI = 2**26, 2**27
LINE = re.compile(r"^(xmin|xmax|ymin|ymax) P=1: cycles=(\d+) distinct_swing=(\d+) best p=(\d+) a=(-?\d+) exact=([0-9.]+) b=\[(.*)\]")


def main():
    rules = (EXP / "results/board_fillers.txt").read_text().split()
    fp = {r["spec"]: r for r in csv.DictReader(open(EXP / "results/p3_footprint.csv"))}
    out = ["P2/P3 analysis: 25 census board fillers, blank 8192 board, 2^27 steps; window [2^26, 2^27]", ""]
    p2_ok = p2_p2 = p3_ok = 0
    for r in rules:
        k = pi_k(r)
        res = subprocess.run([sys.executable, str(CLOCK), str(EXP / "scratch/frontlog" / r), str(LO), str(HI), "--maxP", "1"],
                             capture_output=True, text=True, check=True).stdout
        dirs = {}
        for ln in res.splitlines():
            m = LINE.match(ln)
            if m:
                d, cyc, ds, p, a, ex, b = m.groups()
                dirs[d] = (int(cyc), int(p), int(a), float(ex), b)
        exact_all = len(dirs) == 4 and all(v[3] >= 0.95 and v[2] == 8 * (k + 1) for v in dirs.values())
        p_le2 = exact_all and all(v[1] <= 2 for v in dirs.values())
        p2_ok += exact_all
        p2_p2 += p_le2
        row = fp[r]
        reads = parse_reads(row["reads"])
        W = int(row["win_steps"])
        shares = [reads.get(v, 0) / W for v in range(2 * k + 2)]
        dev = max(abs(s * (2 * k + 2) - 1) for s in shares)
        top = reads.get(2 * k + 2, 0) / W
        newrate = int(row["win_new"]) / W * (2 * k + 2)
        maxread = max(reads)
        p3 = maxread == 2 * k + 2 and dev < 0.02 and top < 0.005 and abs(newrate - 1) < 0.02
        p3_ok += p3
        out.append(f"{r} k={k} stop={row['stop']} visited={row['visited']} steps/visited={int(row['steps'])/int(row['visited']):.4f}")
        for d in ("xmin", "xmax", "ymin", "ymax"):
            if d in dirs:
                cyc, p, a, ex, b = dirs[d]
                out.append(f"   {d}: cycles={cyc} p={p} a={a} (8(k+1)={8*(k+1)}) exact={ex:.4f} b=[{b}]")
            else:
                out.append(f"   {d}: no P=1 result")
        out.append(f"   P2 {'HELD' if exact_all else 'FAILED'} (p<=2: {p_le2}); footprint: max read {maxread}, max rel dev of "
                   f"shares 0..2k+1 = {dev:.5f}, share of 2k+2 = {top:.6f}, new-cell rate x(2k+2) = {newrate:.5f} -> P3 "
                   f"{'HELD' if p3 else 'FAILED'}")
    out += ["", f"P2 (exact clock, a = 8(k+1), all four directions): {p2_ok}/{len(rules)}; of these with p <= 2: {p2_p2}",
            f"P3 (footprint): {p3_ok}/{len(rules)}"]
    (EXP / "results/p23_analysis.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


main()
