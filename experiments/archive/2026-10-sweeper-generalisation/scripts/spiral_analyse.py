"""Stage 2 probe analysis: depth profile, side structure and per-side periods of the square-spiral trace (stdlib only).
usage: python3 spiral_analyse.py DIR T0 T1"""
import struct
import sys
from collections import Counter
from pathlib import Path

d = Path(sys.argv[1])
T0, T1 = int(sys.argv[2]), int(sys.argv[3])
raw = (d / "trace.bin").read_bytes()
n = len(raw) // 8
pos = [struct.unpack_from("<ii", raw, 8 * i) for i in range(n)]
hdr = lambda p: list(map(int, p.read_text().split("\n", 1)[0].split()))
A = hdr(d / f"band_{T0}.txt")
B = hdr(d / f"band_{T1}.txt")
print(f"steps in trace {n}; bbox at T0 (x0 x1 y0 y1): {A[1:5]}, at T1: {B[1:5]}; ant at T0 {A[5:8]}, at T1 {B[5:8]}")
x0, x1, y0, y1 = A[1:5]
# depth profile: distance inside the T0 bounding box (negative = outside it, i.e. in a new layer)
depth = Counter()
for (x, y) in pos:
    depth[min(x - x0, x1 - x, y - y0, y1 - y)] += 1
ks = sorted(depth)
print("depth (distance from the T0 bbox edge, negative = outside) range:", ks[0], ks[-1])
print("depth histogram (first 20 depths from the outside):", [(k, depth[k]) for k in ks[:20]])
deepest = [k for k in ks if depth[k] > 0]
print("deepest depth visited:", deepest[-1], "; steps at depth >= 8:", sum(v for k, v in depth.items() if k >= 8))
# side segmentation: moving average of the velocity over 2000-step blocks
blk = 2000
sides = []
for i in range(0, n - blk, blk):
    vx = pos[i + blk][0] - pos[i][0]
    vy = pos[i + blk][1] - pos[i][1]
    sides.append((i, vx, vy))
print("velocity per 2000-step block, first 60 blocks (i, vx, vy):")
print(sides[:60])
# smallest period of the position sequence in a middle stretch of the longest straight run
def best_period(start, length, pmax=64):
    for p in range(1, pmax + 1):
        v0 = (pos[start + p][0] - pos[start][0], pos[start + p][1] - pos[start][1])
        if v0 == (0, 0):
            continue
        if all((pos[start + k + p][0] - pos[start + k][0], pos[start + k + p][1] - pos[start + k][1]) == v0 for k in range(length)):
            return p, v0
    return None
for i, vx, vy in sides[:60:4]:
    r = best_period(i + 200, 1000)
    print(f"block at {i}: v=({vx},{vy}) smallest exact period over 1000 steps: {r}")
