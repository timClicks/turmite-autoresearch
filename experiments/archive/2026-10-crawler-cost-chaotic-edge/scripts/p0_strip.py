"""P0a (README): edge accounting of the square-ring crawler C_k on an unbounded strip, by direct simulation.

Independent of the Rust tracer: own ant, own boundary/birth/chain bookkeeping, same definitions as src/edge_trace.rs
(boundary read: the cell stepped from has an unvisited 4-neighbour; birth: step onto a never-visited cell; chain:
maximal run of consecutive births). C_k is the configuration of the square-ring-fillers README (y south, crawler on the
north side heading N, moving west). Exact rationals; stdlib only.

usage: python3 experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/p0_strip.py > .../results/p0_strip.txt
"""
from fractions import Fraction

DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N E S W; R = +1


def initial(k, x, y):
    """Visit count of C_k at (x, y); 0 = never visited."""
    a, b, c, d = k, k + 1, 2 * k + 1, 2 * k + 2
    m = x % 4
    if y <= -2:
        return 0
    if y >= 2:
        return d
    if x < 0:
        return {-1: 0, 0: a if m in (2, 3) else 0, 1: c if m in (2, 3) else b}[y]
    if x == 0:
        return {-1: 0, 0: a, 1: d}[y]
    return {-1: a if m in (1, 2) else 0, 0: c if m in (1, 2) else b, 1: d}[y]


def run(k, periods=64, skip=2):
    rule = "R" * k + "L" + "R" * (k + 1)
    n = len(rule)
    cnt = {}
    get = lambda p: cnt[p] if p in cnt else initial(k, *p)
    pos, h = (0, 0), 0
    period = 8 * (k + 1)
    r = [0] * n
    births, chains, run_len = 0, {}, 0
    ok = True
    for t in range(periods * period):
        rec = t >= skip * period
        v = get(pos)
        boundary = any(get((pos[0] + dx, pos[1] + dy)) == 0 for dx, dy in DIRS)
        if rec and boundary:
            r[v % n] += 1
        h = (h + (1 if rule[v % n] == "R" else 3)) % 4
        cnt[pos] = v + 1
        nxt = (pos[0] + DIRS[h][0], pos[1] + DIRS[h][1])
        born = get(nxt) == 0
        if rec:
            if born:
                births += 1
                run_len += 1
            elif run_len:
                chains[run_len] = chains.get(run_len, 0) + 1
                run_len = 0
        pos = nxt
        if (t + 1) % period == 0:  # translation check: ant at (-4p, 0) heading N
            p = (t + 1) // period
            ok &= pos == (-4 * p, 0) and h == 0
    rj = [Fraction(x, births) for x in r]
    nch = sum(chains.values())
    return rule, ok, births, rj, sum(rj), {L: Fraction(c, nch) for L, c in sorted(chains.items())}


def main():
    allpass = True
    print("P0a: crawler C_k on a strip, 64 periods, first 2 skipped; r_j = boundary reads at colour j per birth")
    for k in range(1, 9):
        rule, ok, b, rj, inv, ch = run(k)
        want = [Fraction(1)] * (k + 1) + [Fraction(1, 4)] + [Fraction(0)] * (len(rule) - k - 2)
        chain_ok = ch == {1: Fraction(1, 2), 3: Fraction(1, 2)}
        p = ok and rj == want and inv == k + Fraction(5, 4) and chain_ok
        allpass &= p
        print(f"k={k} {rule}: translation {ok}; births {b}; 1/c = {inv} (k+5/4 = {k + Fraction(5, 4)}); "
              f"r = {[str(x) for x in rj]}; chains {dict((L, str(f)) for L, f in ch.items())} -> {'PASS' if p else 'FAIL'}")
    print("P0a", "HELD" if allpass else "FAILED")


if __name__ == "__main__":
    main()
