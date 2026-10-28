"""Oracle for the front log: an independent pure-Python ant recomputes the four event files for the first N steps and compares
them with the Rust example's output. usage: python3 oracle_log.py RULE N OUTDIR  (OUTDIR from frontlog with STEPS=N)."""
import sys
from pathlib import Path

rule, n_steps, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
turn = [1 if ch == "R" else -1 for ch in rule]
cells, x, y, h = {}, 0, 0, 0
front = [0, 0, 0, 0]
pr = [[0, 0] for _ in range(4)]
events = [[], [], [], []]
for t in range(1, n_steps + 1):
    col = cells.get((x, y), 0)
    h = (h + turn[col]) % 4
    cells[(x, y)] = (col + 1) % len(rule)
    dx, dy = dirs[h]
    x += dx
    y += dy
    for d in range(4):
        p = y if d < 2 else x
        pr[d][0] = min(pr[d][0], p)
        pr[d][1] = max(pr[d][1], p)
    cur = [x, x, y, y]
    adv = [x < front[0], x > front[1], y < front[2], y > front[3]]
    for d in range(4):
        if adv[d]:
            front[d] = cur[d]
            events[d].append((t, cur[d], pr[d][0], pr[d][1]))
            p = y if d < 2 else x
            pr[d] = [p, p]
names = ["xmin", "xmax", "ymin", "ymax"]
ok = True
for d in range(4):
    rows = [tuple(map(int, ln.split(","))) for ln in (out / f"events_{names[d]}.csv").read_text().splitlines()[1:]]
    same = rows == events[d]
    ok &= same
    print(f"{names[d]}: {len(rows)} rust events, {len(events[d])} python events, identical={same}")
print("ORACLE_LOG", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
