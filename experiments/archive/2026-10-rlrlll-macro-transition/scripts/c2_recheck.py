"""Task C2d: recheck Task A's base case against the dynamics, with no margin chosen from observation.

usage: python3 c2_recheck.py WINDIR     (WINDIR = scratch/win, ev_<x>.bin dumps of the real run at Task A's events)
Criterion (exact): let V be the set of cells the ideal ant (my ant, started on the family configuration C(m, q) over a blank board)
ever stands on during J consecutive cycles. The real run coincides with the ideal run forever iff the real configuration at the
event has the same colour as the ideal initial configuration on every cell of V (induction on steps: the ant only reads cells it
stands on). J is chosen so that cycles >= J can only stand on columns west of the real run's visited region: the finite runs bound
the reach east of the cycle's front column by 18 (c2_reach.txt), so once x_f(J) + 18 < X_WEST every later cell is in a column the
real run had not visited at the event (X_WEST = -1820, the old blob's west edge: the first global front advance, step 12,676,421,767,
is 184,176 steps after the base event; the dump confirms columns X_WEST .. x-320 are unvisited), where real = ideal = blank.
Also reports the envelope of V outside the base rectangle against Task A's cone (3 rows + s // 3 rows s columns ahead).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from c1_ant import *

X_WEST = -1820
EAST_REACH = 18


def load(path):
    raw = path.read_bytes()
    nl = raw.index(b"\n")
    x, t, ax, ay, h, x0, y0, w, hgt = map(int, raw[:nl].split())
    return dict(x=x, t=t, ax=ax, ay=ay, h=h, x0=x0, y0=y0, w=w, hgt=hgt, a=raw[nl + 1:])


def mq(x):
    d = -2197 - x
    assert d % 3 == 0
    j = d // 3
    return 434 + 2 * j, j % 3


def main():
    win = Path(sys.argv[1])
    ph = parse_canonical()
    print("# C2d: base-case recheck by the exact criterion (colour of the real dump on every cell the ideal ant visits)")
    raw = (win / "ref.bin").read_bytes()
    nl = raw.index(b"\n")
    rt, rx0, ry0, rw, rh = map(int, raw[:nl].split())
    ra = raw[nl + 1:]
    minc = next(rx0 + c for c in range(rw) if any(v != 255 for v in ra[c::rw]))
    print(f"premise check: ref.bin (step {rt}, columns {rx0}..{rx0 + rw - 1}, rows {ry0}..{ry0 + rh - 1}): westmost visited column {minc} "
          f"(premise: nothing visited west of {X_WEST}); rows outside {ry0}..{ry0 + rh - 1} and columns west of {rx0} are not in the snapshot: "
          f"there the premise rests on the tracer's global front record (cycles_early.csv, front -1820 at step 12,676,421,767), not re-verified here")
    bad_windows, cone_viol_windows = [], []
    gmax = dict(above=0, below=0, excess_above=0, excess_below=0)
    for x in range(-1552, -1700, -3):
        e = load(win / f"ev_{x}.bin")
        assert e["ax"] == x and e["x0"] == x - 320 and e["w"] == 384, (x, e["ax"], e["x0"], e["w"])
        m, q = mq(x)
        p = ph[q]
        T, Bt = len(p["top"]), len(p["bottom"])
        n = T + m + Bt
        apron = (e["hgt"] - 1) // 2
        assert e["y0"] == e["ay"] - apron
        J = (x + 1820 + EAST_REACH) // 3 + 3
        cells, pos, h = start_state(p, m)
        init = dict(cells)
        a = Ant("RLRLLL", cells, pos, h)
        V = set()
        xmin = pos[0]
        while xmin > -3 * J:
            V.add(a.pos)
            a.step()
            xmin = min(xmin, a.pos[0])
        V.add(a.pos)
        real = lambda X, Y: (lambda c: 0 if c == 255 else c)(e["a"][(Y - p["dy"] + apron) * e["w"] + (X + 320)])
        mism, uncovered_far, uncovered_other = [], 0, 0
        for (X, Y) in V:
            col = X + x  # absolute column
            row = Y - p["dy"] + apron
            if not (0 <= row < e["hgt"]):
                uncovered_other += 1
                continue
            if not (0 <= X + 320 < e["w"]):
                if col < X_WEST - 0:  # beyond the apron's west edge: only the global-front fact applies
                    uncovered_far += 1
                else:
                    uncovered_other += 1
                continue
            if real(X, Y) != init.get((X, Y), 0):
                mism.append((X, Y, real(X, Y), init.get((X, Y), 0)))
        # the unvisited-ness of columns X_WEST .. x-320 inside the dump (flag 255), over all apron rows
        visited_west = 0
        # unvisited west of X_WEST inside the apron: absolute columns x0 .. X_WEST - 1 (dump columns 0 .. X_WEST - x0 - 1)
        wl = X_WEST - e["x0"]
        if wl > 0:
            for r in range(e["hgt"]):
                row_bytes = e["a"][r * e["w"]: r * e["w"] + wl]
                visited_west += sum(1 for v in row_bytes if v != 255)
        # envelope of V outside the base rectangle vs the cone
        above = below = ex_a = ex_b = viol = 0
        for (X, Y) in V:
            if 0 <= X < 48 and 0 <= Y < n:
                continue
            s = max(0, -X)
            if Y < 0:
                above = max(above, -Y)
                ex_a = max(ex_a, -Y - s // 3)
                if -Y > 3 + s // 3:
                    viol += 1
            elif Y >= n:
                below = max(below, Y - (n - 1))
                ex_b = max(ex_b, Y - (n - 1) - s // 3)
                if Y - (n - 1) > 3 + s // 3:
                    viol += 1
            elif X >= 48:
                viol += 1
        gmax["above"] = max(gmax["above"], above)
        gmax["below"] = max(gmax["below"], below)
        gmax["excess_above"] = max(gmax["excess_above"], ex_a)
        gmax["excess_below"] = max(gmax["excess_below"], ex_b)
        status = "PASS" if not mism and visited_west == 0 and uncovered_other == 0 else "FAIL"
        if status == "FAIL":
            bad_windows.append(x)
        if viol:
            cone_viol_windows.append(x)
        print(f"x={x} m={m:3d} q={q} J={J} |V|={len(V)} mismatches={len(mism)} uncovered_in_apron_gap={uncovered_other} "
              f"beyond_apron_west={uncovered_far} visited_cells_west_of_{X_WEST}_in_dump={visited_west} "
              f"V_out above/below={above}/{below} excess_over_wedge={ex_a}/{ex_b} outside_TaskA_cone={viol} -> {status}"
              + (f" first mismatch (X,Y,real,ideal)={mism[0]}" if mism else ""))
    print(f"SUMMARY: {50 - len(bad_windows)} of 50 windows pass the exact criterion; failing: {bad_windows}")
    print(f"V outside the base rectangle: max rows above {gmax['above']}, below {gmax['below']}; max excess over the wedge s//3: above {gmax['excess_above']}, below {gmax['excess_below']}; "
          f"windows with a visited cell outside Task A's cone (3 + s//3): {cone_viol_windows}")


main()
