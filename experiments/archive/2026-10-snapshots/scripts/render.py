import sys, numpy as np
from PIL import Image
path, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
g = np.fromfile(path, dtype=np.uint8).reshape(8192, 8192)
ys, xs = np.nonzero(g)
y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
crop = g[y0:y1+1, x0:x1+1]
# downsample by mean of nonzero-ness blended with colour index
f = max(1, max(crop.shape) // 1600)
h, w = crop.shape[0] // f * f, crop.shape[1] // f * f
c = crop[:h, :w].reshape(h // f, f, w // f, f).astype(float).mean(axis=(1, 3)) / (n - 1)
from matplotlib import colormaps
img = (colormaps["magma"](c)[..., :3] * 255).astype(np.uint8)
Image.fromarray(img).save(out)
print(crop.shape, "->", img.shape, "bbox", (x0-4096, y0-4096, x1-4096, y1-4096))
