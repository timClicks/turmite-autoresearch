# /// script
# dependencies = ["numpy", "pillow", "matplotlib"]
# ///
"""view.py PREFIX OUT.png [x0 y0 w h] : visit-count and colour views of a dump (bbox auto-cropped)."""
import sys, numpy as np
from PIL import Image
pre, out = sys.argv[1], sys.argv[2]
S = 8192
vis = np.fromfile(pre + ".vis", dtype=np.uint16).reshape(S, S)
col = np.fromfile(pre + ".col", dtype=np.uint8).reshape(S, S)
ys, xs = np.nonzero(vis)
y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
print("bbox", x1 - x0, y1 - y0, "max visits", vis.max(), "frac visited", (vis[y0:y1, x0:x1] > 0).mean())
if len(sys.argv) > 3:
    cx, cy, w, h = map(int, sys.argv[3:7]); x0, y0, x1, y1 = x0 + cx, y0 + cy, x0 + cx + w, y0 + cy + h
v = vis[y0:y1, x0:x1].astype(float); c = col[y0:y1, x0:x1]
from matplotlib import colormaps
vi = (colormaps["inferno"](np.clip(np.log1p(v) / np.log1p(300), 0, 1))[..., :3] * 255).astype(np.uint8)
ci = (colormaps["tab20"]((c % 20) / 20.0)[..., :3] * 255).astype(np.uint8)
Image.fromarray(np.concatenate([vi, ci], axis=1)).save(out)
