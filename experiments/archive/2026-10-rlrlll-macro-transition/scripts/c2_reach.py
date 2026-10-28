"""Task C2 (derive the cone margin), part 1: per-cycle reach, brute force and symbolic.

usage: python3 c2_reach.py  (output saved as results/c2_reach.txt)
(a) brute force, m = 2..100 step 2, q = 0..2 (150 cycles), my ant: rows VISITED (ant position at the start of some step, plus the
    final position) above the rectangle's first row and below its last row, the min/max column, and the visit counts of the
    visited cells outside the rectangle (a cell visited 6 times returns to colour 0 and looks blank in a snapshot).
(b) symbolic: the same quantities from the finite runs of c1b.py (S1, S3, S5; the lemma runs stay inside their patches), which
    do not depend on m, plus the exact growth of the rectangle per cycle (top row, bottom row) from the verified composition.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from c1_ant import *
import c1b

ph = parse_canonical()
print("# (a) brute force, my ant; coordinates: rectangle top row y = 0, bottom row y = T + m + Bt - 1, front column x = 0")
worst = {"above": (-1, None), "below": (-1, None), "east": (-1, None)}
per_q = {q: dict(above=0, below=0, east=0) for q in range(3)}
n6 = 0
maxvis_out = 0
first_x3 = []
for q in range(3):
    p = ph[q]
    T, Bt = len(p["top"]), len(p["bottom"])
    for m in range(2, 101, 2):
        cells, pos, h = start_state(p, m)
        a = Ant("RLRLLL", cells, pos, h)
        bottom = T + m + Bt - 1
        vis = {}
        xmin = pos[0]
        reached_before_last = False
        while xmin > -3:
            vis[a.pos] = vis.get(a.pos, 0) + 1
            a.step()
            xmin = min(xmin, a.pos[0])
        vis[a.pos] = vis.get(a.pos, 0) + 1
        first_x3.append(min(x for x, y in vis) == -3 and sum(1 for (x, y) in vis if x == -3) == 1 and a.pos[0] == -3)
        above = max(0, -min(y for x, y in vis))
        below = max(0, max(y for x, y in vis) - bottom)
        east = max(x for x, y in vis)
        for k, v in (("above", above), ("below", below), ("east", east)):
            per_q[q][k] = max(per_q[q][k], v)
            if v > worst[k][0]:
                worst[k] = (v, (q, m))
        out = [(c, k) for c, k in vis.items() if c[1] < 0 or c[1] > bottom]
        if out:
            maxvis_out = max(maxvis_out, max(k for c, k in out))
        # cells outside the rectangle rows that were visited and ended at colour 0
        n6 += sum(1 for c, k in vis.items() if (c[1] < 0 or c[1] > bottom) and a.cells.get(c, 0) == 0)
print("per phase max over m = 2..100 of rows visited above the top row / below the bottom row / max column visited:")
for q in range(3):
    print(f"  q={q}: above {per_q[q]['above']}, below {per_q[q]['below']}, max column {per_q[q]['east']}")
print(f"overall: above {worst['above']}, below {worst['below']}, east {worst['east']}  (value, (q, m) first attaining it)")
print(f"C2b: in all 150 cycles column -3 is visited only by the final position (and nothing further west): {all(first_x3)}")
print(f"visited cells outside the rectangle rows that end at colour 0 (visited 6 times): {n6}; max visits to any such cell: {maxvis_out}")

print("# (b) symbolic: finite runs of c1b.verify_phase (independent of m)")
sym = {}
for q in range(3):
    lines = []
    r = c1b.verify_phase("RLRLLL", ph, q, lines, 100)
    sym[q] = r
    rc = r["reach"]
    NB, T, Bt, H, e, K1 = rc["NB"], rc["T"], rc["Bt"] if "Bt" in rc else None, rc["H"], rc["e"], rc["K1"]
    # S1 and S5 frames: the rectangle's top row is patch row NB; S3 frame: bottom block is rows H + e .. H + e + Bt - 1
    Bt = len(ph[q]["bottom"])
    above_s1 = max(0, NB - rc["s1"]["miny"])
    above_s5 = max(0, NB - rc["s5"]["miny"])
    below_s3 = max(0, rc["s3"]["maxy"] - (H + e + Bt - 1))
    east = max(rc["s1"]["maxx"], rc["s3"]["maxx"], rc["s5"]["maxx"])
    print(f"  q={q}: S1 above {above_s1}, S5 above {above_s5}, S3 below {below_s3}, S1/S3/S5 max column {rc['s1']['maxx']}/{rc['s3']['maxx']}/{rc['s5']['maxx']}"
          f" (lemma runs: descent x {r['_std']['minx']}..{r['_std']['maxx']}, return x {r['_strr']['minx']}..{r['_strr']['maxx']}); S1 min column {rc['s1']['minx']}, S3 {rc['s3']['minx']}, S5 {rc['s5']['minx']}")
    sym[q].update(above=max(above_s1, above_s5), below=below_s3, east=east)
print("symbolic maxima over q: above", max(s["above"] for s in sym.values()), "below", max(s["below"] for s in sym.values()),
      "east", max(s["east"] for s in sym.values()))
