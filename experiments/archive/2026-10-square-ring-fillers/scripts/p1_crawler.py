"""P1: does the explicit crawler configuration C_k translate for k = 1..64? (registered in README)

usage: uv run --frozen experiments/archive/2026-10-square-ring-fillers/scripts/p1_crawler.py

Needs `cargo build --release --locked --example square_ring_fillers_crawler`. For each k: the minimal rule R^k L R^(k+1),
four rules with the same letters 0..2k+1 and a random suffix (seed 20261025), every single-letter flip at v in [0, 2k+1] of
the minimal rule (control: must fail), and every single-letter flip in the suffix of the first suffixed rule (control: must
be unchanged). An independent stdlib ant (below) re-checks k <= 10 for the minimal rule and its flips.
Writes results/p1_crawler.txt (summary) and results/p1_crawler_runs.txt (one line per run).
"""
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
BIN = ROOT / "target" / "release" / "examples" / "square_ring_fillers_crawler"
PERIODS = 16
KMAX = 64


def ck(k, wall, x, y):
    """C_k from the README table, written independently of the Rust example."""
    a, b, c, d = k, k + 1, 2 * k + 1, 2 * k + 2
    u = x - wall
    m = u % 4
    if y <= -2:
        return 0
    if y == -1:
        return a if (u >= 1 and m in (1, 2)) else 0
    if y == 0:
        if u < 0:
            return a if m in (2, 3) else 0
        if u == 0:
            return a
        return c if m in (1, 2) else b
    if y == 1:
        if u < 0:
            return c if m in (2, 3) else b
        return d
    return d


def py_check(k, rule, periods=PERIODS):
    """Dict-based ant on an unbounded plane: returns number of periods after which state == C_k shifted."""
    n = len(rule)
    turn = [1 if t == "R" else 3 for t in rule]
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    xs = range(-4 * periods - 16, 17)
    ys = range(-4, 6)
    grid = {(x, y): ck(k, 0, x, y) for x in xs for y in ys}
    x, y, h = 0, 0, 0
    for p in range(1, periods + 1):
        for _ in range(8 * (k + 1)):
            v = grid.get((x, y), ck(k, 0, x, y))
            h = (h + turn[v % n]) % 4
            grid[(x, y)] = v + 1
            x, y = x + dirs[h][0], y + dirs[h][1]
        if (x, y, h) != (-4 * p, 0, 0):
            return p - 1
        if any(grid[(xx, yy)] != ck(k, -4 * p, xx, yy) for xx in xs for yy in ys):
            return p - 1
    return periods


def flip(rule, i):
    return rule[:i] + ("L" if rule[i] == "R" else "R") + rule[i + 1:]


def run(k, rule):
    out = subprocess.run([str(BIN), str(k), rule, str(PERIODS)], capture_output=True, text=True, check=True).stdout.strip()
    f = dict(kv.split("=", 1) for kv in out.split(" "))
    return int(f["periods_ok"]), f["first_fail"], f["reads"], out


def main():
    if not BIN.exists():
        sys.exit(f"missing {BIN}; build the example first")
    rng = random.Random(20261025)
    lines, fails = [], []
    n_main = n_flip_bad = n_flip_ok = n_py = 0
    for k in range(1, KMAX + 1):
        base = "R" * k + "L" + "R" * (k + 1)
        suffixed = [base + "".join(rng.choice("LR") for _ in range(rng.randint(1, 8))) for _ in range(4)]
        expect_reads = ",".join(f"{v}:{4 * PERIODS}" for v in range(2 * k + 2))
        for r in [base] + suffixed:
            ok, ff, reads, out = run(k, r)
            lines.append(f"main k={k} rule={r} periods_ok={ok} first_fail={ff} reads_as_expected={reads == expect_reads}")
            n_main += 1
            if ok != PERIODS or reads != expect_reads:
                fails.append(f"main k={k} rule={r}: {out}")
        for i in range(2 * k + 2):  # control: each letter read by the crawler must matter
            r = flip(base, i)
            ok, ff, reads, out = run(k, r)
            lines.append(f"flip_read k={k} v={i} rule={r} periods_ok={ok} first_fail={ff}")
            n_flip_bad += 1
            if ok != 0:
                fails.append(f"flip_read k={k} v={i} rule={r} survived {ok} periods")
        s = suffixed[0]
        for i in range(2 * k + 2, len(s)):  # control: letters never read must not matter
            r = flip(s, i)
            ok, ff, reads, out = run(k, r)
            lines.append(f"flip_unread k={k} v={i} rule={r} periods_ok={ok} first_fail={ff} reads_as_expected={reads == expect_reads}")
            n_flip_ok += 1
            if ok != PERIODS or reads != expect_reads:
                fails.append(f"flip_unread k={k} v={i} rule={r}: {out}")
        if k <= 10:  # independent oracle
            for r in [base] + [flip(base, i) for i in range(2 * k + 2)]:
                rust_ok = run(k, r)[0]
                py_ok = py_check(k, r)
                n_py += 1
                if rust_ok != py_ok:
                    fails.append(f"oracle k={k} rule={r}: rust {rust_ok} python {py_ok}")
    (EXP / "results" / "p1_crawler_runs.txt").write_text("\n".join(lines) + "\n")
    summary = [
        "P1: explicit crawler C_k, k = 1..%d, %d periods each (registered in README)" % (KMAX, PERIODS),
        f"main runs (minimal + 4 random-suffix rules per k, seed 20261025): {n_main}",
        f"control flips of letters 0..2k+1 (must fail within one period): {n_flip_bad}",
        f"control flips of unread suffix letters (must be unchanged): {n_flip_ok}",
        f"independent Python oracle comparisons (k <= 10): {n_py}",
        f"failures: {len(fails)}",
    ] + fails
    summary.append("VERDICT: P1 HELD" if not fails else "VERDICT: P1 FAILED")
    (EXP / "results" / "p1_crawler.txt").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))


main()
