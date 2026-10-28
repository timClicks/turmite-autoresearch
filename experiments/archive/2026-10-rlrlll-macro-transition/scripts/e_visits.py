"""Task E: visit-count explanation of the period-3 wake (stdlib; uses the second checker's ant and the canonical proposal).

usage: python3 e_visits.py [M=60] [CYCLES=24]
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c1_ant import Ant, parse_canonical, start_state, STRIP

M = int(sys.argv[1]) if len(sys.argv) > 1 else 60
J = int(sys.argv[2]) if len(sys.argv) > 2 else 24
phases = parse_canonical()
p0 = phases[0]
cells, pos, h = start_state(p0, M)
ant = Ant("RLRLLL", cells, pos, h)
top_len = len(p0["top"])
rows_int = range(top_len + 12, top_len + M - 12)   # interior rows of the initial bulk band
visits_cyc = [defaultdict(int) for _ in range(J)]   # per cycle: (x, y) -> visits
tot = defaultdict(int)
xmin = pos[0]
front0 = 0
j = 0
steps_in_cycle = []
start = 0
while j < J:
    x, y = ant.pos
    visits_cyc[j][(x, y)] += 1
    tot[(x, y)] += 1
    ant.step()
    xmin = min(xmin, ant.pos[0])
    assert ant.pos[0] < STRIP
    if xmin <= front0 - 3 * (j + 1):
        steps_in_cycle.append(ant.steps - start)
        start = ant.steps
        j += 1
front_end = -3 * J
out = []
P = lambda *a: (print(*a), out.append(" ".join(str(v) for v in a)))
P(f"M={M} cycles={J} q0=0 steps per cycle (first 6): {steps_in_cycle[:6]}")
# E-a
bad = Counter()
for j in range(J):
    for y in rows_int:
        n = sum(c for (x, yy), c in visits_cyc[j].items() if yy == y)
        if n != 12:
            bad[(j, n)] += 1
P(f"E-a: interior rows {len(rows_int)} x cycles {J}; row-cycles with count != 12: {sum(bad.values())} {dict(list(bad.items())[:5])}")
# E-b
deep_x = range(front_end + 21, 0)           # x in [-51, -1]: >= 21 columns behind the final front, blank at the start
nb = nok = nlt6 = 0
bycls = defaultdict(Counter)
for y in rows_int:
    for x in deep_x:
        v = tot.get((x, y), 0)
        c = ant.cells.get((x, y), 0)
        nb += 1
        nok += (v == c)
        nlt6 += (v < 6)
        bycls[x % 3][v] += 1
P(f"E-b: deep interior cells {nb}; visits == colour: {nok}; visits < 6: {nlt6}")
P("     visits by x mod 3:", {k: dict(v) for k, v in sorted(bycls.items())})
# E-c: profiles a_j(d) of interior rows, d = x - (front before the cycle)
profiles = defaultdict(Counter)
for j in range(2, J - 8):                    # skip the first cycles (end effects) and the last (reach)
    xf = -3 * j
    for y in rows_int:
        prof = tuple(sorted(((x - xf), c) for (x, yy), c in visits_cyc[j].items() if yy == y))
        profiles[(j % 3, y % 2)][prof] += 1
distinct = {k: len(v) for k, v in profiles.items()}
supp = set()
for k, cnt in profiles.items():
    for prof in cnt:
        supp |= {d for d, _ in prof}
P(f"E-c: distinct profiles per (cycle phase, row parity): {distinct}; offsets covered: min {min(supp)} max {max(supp)}")
for k in sorted(profiles):
    prof, n = profiles[k].most_common(1)[0]
    P(f"     phase {k[0]} parity {k[1]}: {n} of {sum(profiles[k].values())} rows have a(d) = {dict(prof)}")
# E-d: predict total visits of a deep cell from the per-phase profiles
pred_ok = pred_n = 0
rep = {}
for k in sorted(profiles):
    rep[k] = dict(profiles[k].most_common(1)[0][0])
for y in rows_int:
    for x in deep_x:
        s = 0
        for jj in range(J):
            d = x + 3 * jj
            s += rep[(jj % 3, y % 2)].get(d, 0)
        pred_n += 1
        pred_ok += (s == tot.get((x, y), 0))
P(f"E-d: total visits predicted from the per-phase profiles equal the measured count for {pred_ok} of {pred_n} deep cells (jj outside 2..{J-9} use the same representative profiles)")
Path(sys.argv[0]).resolve().parent.parent.joinpath("results", "e_visits.txt").write_text("\n".join(out) + "\n")
