"""Prediction P5: every mined generator is conserved by the reference ant; non-laws are not.

  uv run --no-project experiments/archive/2026-10-invariant-mining-snf/scripts/oracle.py \\
      --exe PATH/TO/invariant_mining_snf_verify[.exe] [--nmax 6] [--steps 2000] [--starts 16] [--seed 20261022]

Generates scratch/laws.csv (gitignored), runs the Rust oracle example, writes results/oracle_summary.json.
Control: for n <= --control-nmax, --controls random vectors per (rule, family, m) that are NOT in the kernel.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments" / "_lib"))
import lawmod as lm  # noqa: E402

EXP = Path(__file__).resolve().parents[1]


def line(rule, fam, m, expect, vec, n, family):
    law = lm.unpack(family, n, vec, m)
    phi = ";".join(f"{h}:{s}:{v % m}" for (h, s), v in law["phi"].items())
    w = ";".join(f"{s}:{c}:{ws[c] % m}" for s, ws in law["w"].items() for c in range(1, n))
    return f"{rule},{fam},{m},{expect},{law['a'] % m},{law['b'] % m},{law['e'] % m},{law['d'] % m},{phi},{w}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--nmax", type=int, default=6)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--starts", type=int, default=16)
    ap.add_argument("--seed", type=int, default=20261022)
    ap.add_argument("--control-nmax", type=int, default=4)
    ap.add_argument("--controls", type=int, default=10)
    args = ap.parse_args()
    scratch = EXP / "scratch"
    scratch.mkdir(exist_ok=True)

    lines, meta = [], []
    for fname in lm.FAMILIES:
        fam = lm.Family(fname)
        for n in range(2, args.nmax + 1):
            k = lm.Layout(fam, n).size()
            mods = sorted({2, 3, 4, 6, 8, n, 2 * n, 4 * n})
            for bits in itertools.product("RL", repeat=n):
                rule = "".join(bits)
                M = lm.rule_rows(fam, rule)
                sn = lm.snf(M, k)
                for m in mods:
                    for g in sn.generators(m):
                        lines.append(line(rule, fname, m, 1, g, n, fam))
                        meta.append((fname, n, m, 1))
                    if n <= args.control_nmax:
                        rng = random.Random(f"{args.seed}-{rule}-{fname}-{m}")
                        made = 0
                        while made < args.controls:
                            u = [rng.randrange(m) for _ in range(k)]
                            if not lm.check_vector(fam, M, u, m):
                                lines.append(line(rule, fname, m, 0, u, n, fam))
                                meta.append((fname, n, m, 0))
                                made += 1
    laws = scratch / "laws.csv"
    laws.write_text("rule,family,m,expect,a,b,e,d,phi,w\n" + "\n".join(lines) + "\n")
    res = subprocess.run([args.exe, str(laws), str(args.steps), str(args.starts), str(args.seed)],
                         capture_output=True, text=True, check=True)
    out = [r.split(",") for r in res.stdout.strip().splitlines()[1:]]
    assert len(out) == len(lines)
    stat = defaultdict(lambda: [0, 0, 0])  # (family, expect) -> [lines, lines with a violation, applications]
    worst = []
    for (fname, n, m, expect), (idx, ex, applied, viol) in zip(meta, out):
        s = stat[(fname, expect)]
        s[0] += 1
        s[1] += int(int(viol) > 0)
        s[2] += int(applied)
        if expect == 1 and int(viol) > 0:
            worst.append(lines[int(idx) - 1][:120])
    summary = {
        "command": " ".join(sys.argv),
        "exe_sha256": hashlib.sha256(Path(args.exe).read_bytes()).hexdigest(),
        "laws_csv_sha256": hashlib.sha256(laws.read_bytes()).hexdigest(),
        "git_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
        "steps": args.steps, "starts_per_rule": args.starts, "seed": args.seed,
        "by_family": {f"{f}:{'law' if e else 'control'}": {"lines": s[0], "lines_with_violation": s[1], "applications": s[2]}
                      for (f, e), s in sorted(stat.items())},
        "law_violations_total": sum(s[1] for (f, e), s in stat.items() if e == 1),
        "control_detection_rate": (sum(s[1] for (f, e), s in stat.items() if e == 0) /
                                   max(1, sum(s[0] for (f, e), s in stat.items() if e == 0))),
        "violating_law_examples": worst[:10],
    }
    (EXP / "results" / "oracle_summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps({k: summary[k] for k in ("law_violations_total", "control_detection_rate")}))


if __name__ == "__main__":
    main()
