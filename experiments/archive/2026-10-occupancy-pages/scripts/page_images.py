"""Theme-safe occupancy portraits for the page: unvisited transparent, visited
but idle in a translucent neutral, time per cell on a shared log ramp."""
import json, numpy as np
from PIL import Image
from matplotlib import colormaps
S = 4096
RULES = ["RRRRRLLLLLL", "RLR", "RLLLLLRRLRR"]
cmap = colormaps["inferno"]
LO, HI = -2.0, 2.0       # log10 of time per cell relative to the mean
RAMP = (0.28, 0.97)      # skip inferno's near-black end so it reads on dark pages
out = {}
for r in RULES:
    raw = np.fromfile(f"experiments/archive/2026-10-occupancy-pages/results/{r}.bin", dtype="<u4")
    time = raw[:S * S].reshape(S, S).astype(float)
    vis = raw[S * S:].reshape(S, S).astype(bool)
    ys, xs = np.nonzero(vis)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    side = max(y1 - y0, x1 - x0) + 1
    cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
    sl = (slice(cy - side // 2, cy - side // 2 + side), slice(cx - side // 2, cx - side // 2 + side))
    T, V = time[sl], vis[sl]
    mean = time[vis].mean()
    f = max(1, -(-side // 420))
    s = side // f * f
    T = T[:s, :s].reshape(s // f, f, s // f, f).mean(axis=(1, 3))
    V = V[:s, :s].reshape(s // f, f, s // f, f).mean(axis=(1, 3))
    rel = np.where(T > 0, np.log10(np.maximum(T, 1e-9) / mean), -np.inf)
    u = np.clip((rel - LO) / (HI - LO), 0, 1)
    rgba = cmap(RAMP[0] + u * (RAMP[1] - RAMP[0]))
    alpha = np.where(T > 0, 1.0, 0.0) * V
    idle = (T == 0) & (V > 0)
    rgba[idle] = (0.55, 0.58, 0.62, 1)
    alpha = np.where(idle, 0.35 * V, alpha)
    rgba[..., 3] = alpha
    Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(f"experiments/archive/2026-10-occupancy-pages/results/page_{r}.png", optimize=True)
    out[r] = {"area": int(vis.sum()), "side": int(side)}
# Legend stops, as CSS colours
stops = [cmap(RAMP[0] + q * (RAMP[1] - RAMP[0])) for q in np.linspace(0, 1, 6)]
out["legend"] = ["rgb(%d,%d,%d)" % tuple(int(255 * c) for c in s[:3]) for s in stops]
prof = np.load("experiments/archive/2026-10-occupancy-pages/results/profiles.npy", allow_pickle=True).item()
out["profiles"] = {r: [[round(float(x), 3), None if not np.isfinite(y) else round(float(y), 5)] for x, y in zip(*prof[r])] for r in RULES}
json.dump(out, open("experiments/archive/2026-10-occupancy-pages/results/page_occ.json", "w"))
print({k: v for k, v in out.items() if k in RULES})
