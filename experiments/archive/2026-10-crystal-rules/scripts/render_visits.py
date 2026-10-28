# /// script
# dependencies = ["numpy", "pillow"]
# ///
"""Render a visit-count dump (crystal_s0 .visits) as a PNG heat map, cropped to the
visited bounding box and downsampled by max-pooling. usage: render_visits.py RULE [OUT_PX]"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
rule = sys.argv[1]
px = int(sys.argv[2]) if len(sys.argv) > 2 else 1100
v = np.fromfile(root / "dumps" / f"{rule}.visits", dtype=np.uint8)
S = int(round(v.size ** 0.5))
v = v.reshape(S, S)
ys, xs = np.nonzero(v)
v = v[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
f = max(1, int(np.ceil(max(v.shape) / px)))
H, W = (v.shape[0] // f) * f, (v.shape[1] // f) * f
p = v[:H, :W].reshape(H // f, f, W // f, f).max(axis=(1, 3)).astype(float)
g = np.clip(np.log1p(p) / np.log1p(max(p.max(), 1)), 0, 1)
img = np.zeros(p.shape + (3,), np.uint8)
img[..., 0] = (60 + 195 * g)
img[..., 1] = (20 + 160 * g ** 1.5)
img[..., 2] = 30
Image.fromarray(img).save(root / "results" / f"{rule}_visits.png")
print(rule, v.shape, "pool", f, "max", int(v.max()))
