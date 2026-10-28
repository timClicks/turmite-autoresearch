"""Control C5: no certificate for non-highway rules.

usage: python3 c5_nonhighway.py DUMPER OUT_TXT [--first 50] [--extra 50] [--t1 10000000]

Rules: the first --first lines of non_highway.txt (registered), and --extra further rules of length 8..10 drawn from the same file with a fixed
seed (added after registration, labelled as such). For each rule, dump the configuration at t1, then test every period P <= 3000 for which the ant
is back at its starting heading with a non-zero displacement after P steps (a necessary condition for clause a), with v = that displacement.
Expected: zero certificates.
"""
import random
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import decide

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
NH = ROOT / "experiments/archive/2026-10-census-sweeps/results/non_highway.txt"


def candidates(rule, cells, ant, pmax):
    n = len(rule)
    turn = [1 if ch == "R" else 3 for ch in rule]
    cells = dict(cells)
    x, y, h = ant
    h0 = h
    out = []
    for p in range(1, pmax + 1):
        c = cells.get((x, y), 0)
        h = (h + turn[c]) & 3
        c2 = (c + 1) % n
        if c2:
            cells[(x, y)] = c2
        else:
            cells.pop((x, y), None)
        dx, dy = decide.DIRS[h]
        x += dx
        y += dy
        if h == h0 and (x - ant[0], y - ant[1]) != (0, 0):
            out.append((p, (x - ant[0], y - ant[1])))
    return out


def main():
    dumper, outp = sys.argv[1], sys.argv[2]
    opt = lambda name, default: int(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default
    first, extra, t1 = opt("--first", 50), opt("--extra", 50), opt("--t1", 10_000_000)
    rules = [ln.strip() for ln in open(NH) if ln.strip()]
    sel = [("registered", r) for r in rules[:first]]
    pool = [r for r in rules[first:] if 8 <= len(r) <= 10]
    random.Random(20261023).shuffle(pool)
    sel += [("extra", r) for r in pool[:extra]]
    out = open(outp, "w")
    total_cand = total_cert = 0
    for tag, rule in sel:
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run([dumper, rule, str(t1), "1", "8192", td], capture_output=True, text=True)
            path = Path(td) / f"dump_{t1}.txt"
            if not path.exists():
                print(f"{tag} {rule}: no dump ({r.stderr.strip()[:80]})", file=out)
                continue
            d = decide.load(path)
        cands = candidates(rule, d["cells"], d["ant"], 3000)
        certs = []
        for p, v in cands:
            res = decide.decide(d, p, v)
            if res["ok"]:
                certs.append((p, v))
        total_cand += len(cands)
        total_cert += len(certs)
        print(f"{tag} {rule}: candidates {len(cands)}, certificates {len(certs)} {certs[:3]}", file=out)
        out.flush()
    print(f"TOTAL candidates {total_cand}, certificates {total_cert}", file=out)
    print(f"TOTAL candidates {total_cand}, certificates {total_cert}")


main()
