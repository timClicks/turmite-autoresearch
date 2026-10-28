"""Independent stdlib check of square_ring_fillers_footprint: read histogram, visited count, window new cells, first_gt,
fronts_after and final position, for short runs including a rule switch. Exit 1 on any mismatch.

Two cases, each one invocation of the binary with RAYON_NUM_THREADS=1 so every run after the first reuses the previous run's
cell buffer (the buffer is cleared by bounding box; a stale cell would change `visited` or the histogram):
  A. 512 board, window 65536: the six specs with `RL` first, which escapes at ~22k steps (shorter than the window) and is then
     followed by five full-length runs, two with a rule switch.
  B. 256 board, window 4096: `RL` escapes at ~15k steps, after the ring buffer has started dropping old reads, and is run again
     after a switched run, so the escape path is exercised with and without an active window and before and after reuse.

usage: python3 experiments/archive/2026-10-square-ring-fillers/scripts/oracle_footprint.py BIN
"""
import os
import subprocess
import sys

CASES = [
    (200000, 512, 65536, ["RL", "RLRRRL", "RRLRRRR", "RLLR", "RLRRRL>RLRRLL@100000#4", "RRLRRRR>RRLRRRL@120000#6"]),
    (200000, 256, 4096, ["RL", "RLRRRL>RLRR@30000#4", "RL", "RRLRRRR#6"]),
]


def ref(spec, steps, grid, win):
    gt = None
    if "#" in spec:
        spec, g = spec.split("#")
        gt = int(g)
    r2, t0 = None, None
    if ">" in spec:
        r1, rest = spec.split(">")
        r2, t0 = rest.split("@")
        t0 = int(t0)
    else:
        r1 = spec
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    vis = {}
    c = grid // 2
    x = y = c
    h = 0
    rule = r1
    reads = []
    newc = []
    visited = 1
    first = None
    fronts = []
    xmax = x
    t = 0
    stop = "budget"
    while t < steps:
        if t0 is not None and t == t0:
            rule = r2
        v = vis.get((x, y), 0)
        h = (h + (1 if rule[v % len(rule)] == "R" else 3)) % 4
        vis[(x, y)] = v + 1
        reads.append(min(v, 64))
        if gt is not None and first is None and t >= (t0 or 0) and v > gt:
            first = t
        x += dirs[h][0]
        y += dirs[h][1]
        t += 1
        if not (0 <= x < grid and 0 <= y < grid):
            stop = "escaped"
            newc.append(0)
            break
        fresh = vis.get((x, y), 0) == 0
        newc.append(1 if fresh else 0)
        visited += fresh
        if x > xmax:
            xmax = x
            if t0 is not None and t > t0 and len(fronts) < 8:
                fronts.append(t)
    w = reads[-win:]
    hist = {}
    for v in w:
        hist[v] = hist.get(v, 0) + 1
    rs = ";".join(f"{v}:{hist[v]}" for v in sorted(k for k in hist if k < 64))
    if 64 in hist:
        rs += (";" if rs else "") + f"64+:{hist[64]}"
    return dict(stop=stop, steps=str(t), visited=str(visited), win_start=str(t - len(w)), win_steps=str(len(w)),
                win_new=str(sum(newc[-win:])), reads=rs, first_gt="" if first is None else str(first),
                fronts_after=";".join(map(str, fronts)))


def main():
    env = dict(os.environ, RAYON_NUM_THREADS="1")
    bad = 0
    for steps, grid, win, specs in CASES:
        out = subprocess.run([sys.argv[1], str(steps), str(grid), str(win)], input="\n".join(specs) + "\n",
                             capture_output=True, text=True, check=True, env=env).stdout.splitlines()
        head = out[0].split(",")
        assert len(out) == len(specs) + 1, "one row per spec expected"
        for line, spec in zip(out[1:], specs):
            row = dict(zip(head, line.split(",")))
            exp = ref(spec, steps, grid, win)
            diffs = [k for k in exp if row[k] != exp[k]]
            print(f"{spec} ({grid} board, window {win}, stop={exp['stop']}, steps={exp['steps']}): "
                  f"{'OK' if not diffs else 'MISMATCH ' + str({k: (row[k], exp[k]) for k in diffs})}")
            bad += bool(diffs)
    sys.exit(1 if bad else 0)


main()
