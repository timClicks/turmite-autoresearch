"""Exact-clock test on a front log (stdlib only).

usage: python3 clock.py OUTDIR T_LO T_HI [--maxp 6] [--maxP 8]

For each direction d and cycle period P (1..maxP), cycle k ends when the front first reaches f0 +- P (k + 1); its length is dt_k,
its swing is the range of the perpendicular coordinate over the cycle (inclusive count of rows). Registered criterion: there are
an integer a and constants b_0..b_{p-1} (p <= maxp) with dt_k = a swing_k + b_{k mod p} for >= 95% of the cycles whose end time
lies in [T_LO, T_HI], with zero residual. Also reported: "constant swing" (highway-like) when the swing takes one value, and
then the criterion is exact periodicity of dt with period p.
"""
import sys
from collections import Counter
from pathlib import Path

NAMES = ["xmin", "xmax", "ymin", "ymax"]


def read_events(path):
    rows = [tuple(map(int, ln.split(","))) for ln in path.read_text().splitlines()[1:]]
    return rows


def cycles(rows, P):
    """Returns list of (end_time, dt, swing)."""
    out = []
    nb = len(rows) // P
    prev_t = None
    for k in range(nb):
        chunk = rows[k * P:(k + 1) * P]
        t_end = chunk[-1][0]
        lo = min(r[2] for r in chunk)
        hi = max(r[3] for r in chunk)
        if prev_t is not None:
            out.append((t_end, t_end - prev_t, hi - lo + 1))
        prev_t = t_end
    return out


def exact_fraction(cyc, p):
    """Best (a, fraction) for phase period p. Candidate a from within-class ratios (mode), then residual mode per class."""
    classes = [[c for i, c in enumerate(cyc) if i % p == r] for r in range(p)]
    ratios = Counter()
    for cl in classes:
        base = cl[0]
        for c in cl[1:200]:
            if c[2] != base[2] and (c[1] - base[1]) % (c[2] - base[2]) == 0:
                ratios[(c[1] - base[1]) // (c[2] - base[2])] += 1
    cands = [a for a, _ in ratios.most_common(3)]
    if len({c[2] for c in cyc}) == 1:
        cands = [0]
    best = (None, 0.0, None)
    for a in cands:
        exact, bs = 0, []
        for cl in classes:
            res = Counter(c[1] - a * c[2] for c in cl)
            b, cnt = res.most_common(1)[0]
            exact += cnt
            bs.append(b)
        frac = exact / len(cyc)
        if frac > best[1]:
            best = (a, frac, bs)
    return best


def main():
    out = Path(sys.argv[1])
    t_lo, t_hi = int(float(sys.argv[2])), int(float(sys.argv[3]))
    maxp = int(sys.argv[sys.argv.index("--maxp") + 1]) if "--maxp" in sys.argv else 6
    maxP = int(sys.argv[sys.argv.index("--maxP") + 1]) if "--maxP" in sys.argv else 8
    minper = int(sys.argv[sys.argv.index("--minper") + 1]) if "--minper" in sys.argv else 0  # post hoc guard: need >= minper cycles per phase class
    tried = 0
    results = []
    for d, name in enumerate(NAMES):
        path = out / f"events_{name}.csv"
        if not path.exists():
            continue
        rows = read_events(path)
        for P in range(1, maxP + 1):
            cyc = [c for c in cycles(rows, P) if t_lo <= c[0] <= t_hi]
            if len(cyc) < 30:
                print(f"{name} P={P}: only {len(cyc)} cycles in window, skipped")
                continue
            distinct_swing = len({c[2] for c in cyc})
            best = None
            for p in range(1, maxp + 1):
                if len(cyc) < minper * p:
                    break
                tried += 1
                a, frac, bs = exact_fraction(cyc, p)
                if a is None:
                    continue
                if best is None or frac > best[2] + 1e-12:
                    best = (p, a, frac, bs)
                if frac >= 0.95:
                    best = (p, a, frac, bs)
                    break
            if best is None:
                print(f"{name} P={P}: {len(cyc)} cycles, no candidate slope")
                continue
            p, a, frac, bs = best
            results.append((frac, name, P, p, a, bs, len(cyc), distinct_swing))
            print(f"{name} P={P}: cycles={len(cyc)} distinct_swing={distinct_swing} best p={p} a={a} exact={frac:.4f} b={bs}")
    results.sort(key=lambda r: -r[0])
    print(f"candidates tried (direction x P x p): {tried}")
    if results:
        f, name, P, p, a, bs, n, ds = results[0]
        verdict = "EXACT_CLOCK" if f >= 0.95 else "NO_EXACT_CLOCK"
        kind = "constant-swing (highway-like)" if ds == 1 else "swing-dependent"
        print(f"BEST {verdict}: dir={name} P={P} p={p} a={a} exact_fraction={f:.4f} cycles={n} b={bs} kind={kind}")
    else:
        print("BEST NO_DATA")


main()
