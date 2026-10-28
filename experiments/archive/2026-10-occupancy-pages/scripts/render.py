import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
S = 4096
rules = sys.argv[1:]
fig, axes = plt.subplots(2, len(rules), figsize=(4 * len(rules), 8))
profiles = {}
for j, r in enumerate(rules):
    raw = np.fromfile(f"experiments/archive/2026-10-occupancy-pages/results/{r}.bin", dtype="<u4")
    time, vis = raw[:S * S].reshape(S, S).astype(float), raw[S * S:].reshape(S, S).astype(bool)
    ys, xs = np.nonzero(vis)
    cy, cx = ys.mean(), xs.mean()
    A = vis.sum(); R = np.sqrt(A / np.pi)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    crop = time[y0:y1 + 1, x0:x1 + 1]; vc = vis[y0:y1 + 1, x0:x1 + 1]
    img = np.where(vc, np.log10(crop + 1), np.nan)
    axes[0, j].imshow(img, cmap="magma", interpolation="nearest")
    axes[0, j].set_title(f"{r}  A={A}"); axes[0, j].axis("off")
    rr = np.hypot(ys - cy, xs - cx) / R
    t = time[ys, xs]
    bins = np.linspace(0, 1.6, 33)
    idx = np.digitize(rr, bins)
    prof = np.array([t[idx == i].mean() if (idx == i).any() else np.nan for i in range(1, len(bins))])
    prof /= t.mean()
    profiles[r] = (bins[:-1] + 0.025, prof)
    axes[1, j].plot(bins[:-1] + 0.025, prof); axes[1, j].axhline(1, ls=":", c="k")
    axes[1, j].set_yscale("log"); axes[1, j].set_xlabel("r / R"); axes[1, j].set_ylim(1e-3, 1e2)
    print(r, "A", A, "R", round(R), "time on visited", int(t.sum()), "profile", np.round(prof[::4], 3))
plt.tight_layout(); plt.savefig("experiments/archive/2026-10-occupancy-pages/results/panel.png", dpi=70)
np.save("experiments/archive/2026-10-occupancy-pages/results/profiles.npy", profiles, allow_pickle=True)
