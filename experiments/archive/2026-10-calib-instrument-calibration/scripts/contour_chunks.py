"""Contour radius of nbar = 1 at N = 1e6, per chunk of seeds, with two
interpolations: bilinear along rays, and Kapri & Dhar's scheme (add diagonal
bonds, interpolate linearly within triangles), using marching triangles."""
import glob
import json
import sys

import numpy as np

sys.path.insert(0, "experiments/_lib")
from calib_kd import CROP, contour_radius  # noqa: E402


def triangle_contour_radius(nbar, level=1.0):
    """Marching triangles: split each grid square by the diagonal from (x,y) to
    (x+1,y+1); within each triangle the field is linear, so the contour is a
    straight segment. Return the arc-length-weighted mean radius of the outer
    contour (segments whose midpoint lies outside r = 100)."""
    c = CROP // 2
    v = nbar - level
    lo, hi = c - 260, c + 260
    tot_len, tot_r = 0.0, 0.0
    for y in range(lo, hi):
        for x in range(lo, hi):
            for tri in (((x, y), (x + 1, y), (x + 1, y + 1)), ((x, y), (x, y + 1), (x + 1, y + 1))):
                vals = [v[py, px] for px, py in tri]
                pts = []
                for i in range(3):
                    (x1, y1), (x2, y2) = tri[i], tri[(i + 1) % 3]
                    a, b = vals[i], vals[(i + 1) % 3]
                    if (a < 0) != (b < 0):
                        f = a / (a - b)
                        pts.append((x1 + f * (x2 - x1), y1 + f * (y2 - y1)))
                if len(pts) == 2:
                    (ax, ay), (bx, by) = pts
                    mx, my = (ax + bx) / 2 - c, (ay + by) / 2 - c
                    r = np.hypot(mx, my)
                    if r < 100:
                        continue
                    L = np.hypot(bx - ax, by - ay)
                    tot_len += L
                    tot_r += L * r
    return tot_r / tot_len


def chunk_nbar(path):
    seed0 = path.split("_")[-1].split(".")[0]
    n = sum(1 for _ in open(path.replace(f"visits_1e6_{seed0}.f64", f"exactly4_{seed0}.txt")))
    return np.fromfile(path, dtype="<f8").reshape(CROP, CROP), n


src = sys.argv[1] if len(sys.argv) > 1 else "experiments/archive/2026-10-calib-instrument-calibration/results/short"
dst = sys.argv[2] if len(sys.argv) > 2 else "experiments/archive/2026-10-calib-instrument-calibration/results/calib_contour.json"
files = sorted(glob.glob(f"{src}/visits_1e6_*.f64"))
rows = []
tot, ntot = None, 0
for f in files:
    s, n = chunk_nbar(f)
    nbar = s / n
    r_ray = contour_radius(nbar)[0]
    rows.append((f.split("_")[-1].split(".")[0], n, r_ray))
    tot = s if tot is None else tot + s
    ntot += n
    print(f"chunk {rows[-1][0]}: {n} seeds, radius (rays) {r_ray:.3f}", flush=True)
rr = np.array([r[2] for r in rows])
nbar = tot / ntot
pooled_ray = contour_radius(nbar)[0]
pooled_tri = triangle_contour_radius(nbar)
se = rr.std(ddof=1) / np.sqrt(len(rr))
out = {"chunks": len(rows), "seeds": ntot, "pooled_ray": round(pooled_ray, 3), "pooled_triangles": round(pooled_tri, 3),
       "chunk_radii": [round(x, 3) for x in rr], "se": round(float(se), 3), "kapri_dhar": 145.436}
json.dump(out, open(dst, "w"), indent=1)
print(json.dumps(out, indent=1))
