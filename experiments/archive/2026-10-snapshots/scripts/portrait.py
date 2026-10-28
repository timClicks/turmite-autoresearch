"""portrait.py GRID.bin N OUT.png [MAXPX]: RGBA portrait, colour 0 transparent."""
import sys, numpy as np
from PIL import Image
path, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
maxpx = int(sys.argv[4]) if len(sys.argv) > 4 else 520
g = np.fromfile(path, dtype=np.uint8).reshape(8192, 8192)
ys, xs = np.nonzero(g)
y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
pad = max(4, (max(y1 - y0, x1 - x0)) // 40)
y0, x0 = max(0, y0 - pad), max(0, x0 - pad)
y1, x1 = min(8191, y1 + pad), min(8191, x1 + pad)
side = max(y1 - y0, x1 - x0) + 1          # square crop centred on the bbox
cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
big = np.zeros((side, side), np.uint8)
sy, sx = cy - side // 2, cx - side // 2
ya, xa = max(sy, 0), max(sx, 0)
yb, xb = min(sy + side, 8192), min(sx + side, 8192)
big[ya - sy:yb - sy, xa - sx:xb - sx] = g[ya:yb, xa:xb]
f = max(1, -(-side // maxpx))
s = side // f * f
b = big[:s, :s].reshape(s // f, f, s // f, f)
nz = (b > 0)
alpha = nz.mean(axis=(1, 3))
t = np.where(nz, (b.astype(float) - 1) / max(1, n - 2), 0).sum(axis=(1, 3)) / np.maximum(nz.sum(axis=(1, 3)), 1)
stops = np.array([[59, 76, 192], [31, 161, 135], [232, 163, 61], [209, 73, 91]], float)
pos = t * (len(stops) - 1)
i = np.clip(pos.astype(int), 0, len(stops) - 2)
fr = (pos - i)[..., None]
rgb = stops[i] * (1 - fr) + stops[i + 1] * fr
a = np.clip(np.sqrt(alpha) * 1.25, 0, 1) * 255
img = np.dstack([rgb, a]).astype(np.uint8)
Image.fromarray(img, "RGBA").save(out, optimize=True)
print(out, img.shape, f"crop {side}px, factor {f}")
