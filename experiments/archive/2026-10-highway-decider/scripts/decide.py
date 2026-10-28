"""Rectangle translated-cycler decider (stdlib only; no import from src/).

usage: python3 decide.py DUMP P DX DY      -> prints one JSON line

Checks clauses (a)-(d) of the theorem in README.md on the configuration in DUMP (written by examples/highway_decider_dump.rs) with the
period P and drift (DX, DY). The Python ant here is written from the rule semantics: heading 0 = north (y - 1), 1 = east, 2 = south,
3 = west; colour c turns right (+1) if the rule letter is R, left (+3) if L; the cell becomes (c + 1) mod n; then the ant steps forward.
"""
import json
import sys

M = (1 << 64) - 1
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]


def mix(x, y, c):
    z = ((x & M) * 0x9E3779B97F4A7C15 & M) ^ ((y & M) * 0xC2B2AE3D27D4EB4F & M) ^ (c * 0x165667B19E3779F9 & M)
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M
    return z ^ (z >> 31)


def load(path):
    with open(path) as f:
        rule, t, p = f.readline().split()
        _, ax, ay, ah = f.readline().split()
        ref = f.readline().split()
        ch = f.readline().split()
        cells = {}
        for ln in f:
            x, y, c = ln.split()
            cells[(int(x), int(y))] = int(c)
    return {"rule": rule, "t": int(t), "p": int(p), "ant": (int(ax), int(ay), int(ah)),
            "ref": (int(ref[1]), int(ref[2]), int(ref[3]), ref[4], int(ref[5])),
            "cells_hash": (ch[1], int(ch[2])), "cells": cells}


def run_ant(rule, cells, ant, steps):
    """Returns (cells_after, ant_after, stood) where stood lists the cells the ant stood on (and read) at each of the `steps` steps."""
    n = len(rule)
    turn = [1 if ch == "R" else 3 for ch in rule]
    cells = dict(cells)
    x, y, h = ant
    stood = []
    for _ in range(steps):
        stood.append((x, y))
        c = cells.get((x, y), 0)
        h = (h + turn[c]) & 3
        c2 = (c + 1) % n
        if c2:
            cells[(x, y)] = c2
        else:
            cells.pop((x, y), None)
        dx, dy = DIRS[h]
        x += dx
        y += dy
    return cells, (x, y, h), stood


def cells_hash(cells):
    s = 0
    for (x, y), c in cells.items():
        s = (s + mix(x, y, c)) & M
    return s


def in_strip(z, W, v):
    """True if z lies in W + k v for some integer k >= 1 (W = (x0, x1, y0, y1))."""
    lo, hi = 1, 1 << 60
    for (zc, d, a, b) in ((z[0], v[0], W[0], W[1]), (z[1], v[1], W[2], W[3])):
        # need a <= zc - k d <= b
        if d == 0:
            if not (a <= zc <= b):
                return False
        elif d > 0:
            lo = max(lo, -((-(zc - b)) // d))     # ceil((zc - b) / d)
            hi = min(hi, (zc - a) // d)           # floor((zc - a) / d)
        else:
            e = -d
            lo = max(lo, -((-(a - zc)) // e))     # k >= ceil((a - zc) / e)
            hi = min(hi, (b - zc) // e)
        if lo > hi:
            return False
    return lo <= hi


def decide(d, P, v):
    """Returns a dict with `ok` and, on failure, the first failing clause."""
    rule, cells, ant = d["rule"], d["cells"], d["ant"]
    after, ant1, stood = run_ant(rule, cells, ant, P)
    out = {"rule": rule, "t": d["t"], "P": P, "v": list(v)}
    # Oracle against the reference ant (D4): same configuration, same P steps.
    rx, ry, rh, rhash, rnz = d["ref"]
    out["oracle"] = (ant1 == (rx, ry, rh)) and (f"{cells_hash(after):016x}" == rhash) and (len(after) == rnz)
    xs = [p[0] for p in stood]
    ys = [p[1] for p in stood]
    W = (min(xs), max(xs), min(ys), max(ys))
    out["W"] = list(W)
    out["area"] = (W[1] - W[0] + 1) * (W[3] - W[2] + 1)
    # (a)
    if (ant1[0] - ant[0], ant1[1] - ant[1]) != tuple(v) or ant1[2] != ant[2]:
        out.update(ok=False, clause="a", detail=f"ant ends at displacement {(ant1[0] - ant[0], ant1[1] - ant[1])} heading {ant1[2]} (start heading {ant[2]})")
        return out
    # (b): C1(z) = C0(z - v) on W cap (W + v)
    bx0, bx1 = max(W[0], W[0] + v[0]), min(W[1], W[1] + v[0])
    by0, by1 = max(W[2], W[2] + v[1]), min(W[3], W[3] + v[1])
    for zy in range(by0, by1 + 1):
        for zx in range(bx0, bx1 + 1):
            if after.get((zx, zy), 0) != cells.get((zx - v[0], zy - v[1]), 0):
                out.update(ok=False, clause="b", detail=f"cell {(zx, zy)}: after {after.get((zx, zy), 0)} vs shifted {cells.get((zx - v[0], zy - v[1]), 0)}")
                return out
    # (c): C0 blank on W \ (W - v), i.e. at w in W with w + v outside W
    for wy in range(W[2], W[3] + 1):
        for wx in range(W[0], W[1] + 1):
            if not (W[0] <= wx + v[0] <= W[1] and W[2] <= wy + v[1] <= W[3]) and cells.get((wx, wy), 0) != 0:
                out.update(ok=False, clause="c", detail=f"leading cell {(wx, wy)} = {cells[(wx, wy)]}")
                return out
    # (d): C0 blank on the strip outside W
    for z, c in cells.items():
        if not (W[0] <= z[0] <= W[1] and W[2] <= z[1] <= W[3]) and in_strip(z, W, v):
            out.update(ok=False, clause="d", detail=f"strip cell {z} = {c}")
            return out
    out["ok"] = True
    return out


def main():
    d = load(sys.argv[1])
    P, v = int(sys.argv[2]), (int(sys.argv[3]), int(sys.argv[4]))
    print(json.dumps(decide(d, P, v)))


if __name__ == "__main__":
    main()
