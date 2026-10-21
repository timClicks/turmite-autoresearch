"""Homepage portrait of RLRLLL's late switch: where the ant has been, coloured by when it got there.

Run: uv run experiments/2026-10-21-rlrlll-portrait/scripts/figure.py
Reads only results/ (from render.py) and the shared paper style; writes results/portrait.png and
results/territory_map.png (the map alone, used as the card's no-JavaScript image).
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research-outputs/cube-root-growth-paper"))
import style as st  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
RES = HERE / "results"
# The switch, as dated by the macro-transition trace: the first front advance past the old blob edge.
SWITCH = 12_676_421_767
BLOB = LinearSegmentedColormap.from_list("blob", ["#1d2a7a", st.ANT, "#9aa5ea", "#dfe3fa"])
WEDGE = LinearSegmentedColormap.from_list("wedge", ["#f3c06b", "#d9822b", "#8c4a1c"])


def arrival_rgba(arrival, times):
    """RGBA image: blob blocks by arrival time on a blue ramp, sweeper blocks on an orange ramp, rest clear."""
    t = np.zeros(arrival.shape)
    seen = arrival > 0
    t[seen] = np.asarray(times)[arrival[seen] - 1]
    rgba = np.zeros(arrival.shape + (4,))
    blob = seen & (t <= SWITCH)
    wedge = seen & (t > SWITCH)
    # Area grows ~ t^(2/3), so sqrt-ish spacing in time keeps the blob's rings evenly spread in radius.
    rgba[blob] = BLOB((t[blob] / SWITCH) ** (2 / 3))
    t_end = max(times)
    rgba[wedge] = WEDGE((t[wedge] - SWITCH) / (t_end - SWITCH))
    return rgba


def main():
    st.apply()
    meta = json.loads((RES / "frames.json").read_text())
    frames = meta["frames"]
    times = [f["t"] for f in frames]
    arrival = np.asarray(Image.open(RES / "arrival_b16.png"))
    rgba = arrival_rgba(arrival, times)
    bb, block = meta["bbox_cells"], meta["block"]
    extent = (bb["x0"], bb["x0"] + bb["w"], bb["y0"], bb["y0"] + bb["h"])
    Image.fromarray((rgba[::-1] * 255).round().astype(np.uint8), "RGBA").save(RES / "territory_map.png", optimize=True)

    t_end = times[-1]
    pre = next(f for f in reversed(frames) if f["t"] <= SWITCH)
    end = frames[-1]
    frac_time = (t_end - SWITCH) / t_end

    # Explicit axes positions (inches): the card column is ~380 px wide, so text is sized for that.
    W, H = 3.3, 6.75
    fig = plt.figure(figsize=(W, H))

    def axes(left, top, w, h):
        return fig.add_axes([left / W, 1 - (top + h) / H, w / W, h / H])

    xlim, ylim = (-16700, 2300), (-7700, 4700)
    mw = W - .1
    mh = mw * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
    ax = axes(.05, .42, mw, mh)
    ax.imshow(rgba, extent=extent, origin="lower", interpolation="nearest")
    st.clean(ax)
    ax.set(xlim=xlim, ylim=ylim)
    fig.text(.12 / W, 1 - .06 / H, f"(a) Every cell RLRLLL visits in {t_end / 1e9:.2f} billion\nsteps, coloured by when it was reached",
             va="top", fontsize=8)
    ax.text(-10500, 300, f"{(t_end - SWITCH) / 1e9:.2f} billion steps\nof sweeping", ha="center", va="center",
            fontsize=7.5, color="white", fontweight="bold")
    ax.annotate(f"{SWITCH / 1e9:.1f} billion\nsteps of blob", (300, 1500), (-2200, 3500), ha="center", va="center",
                fontsize=7.5, color=st.ANT, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=st.ANT, lw=.6, shrinkA=7))
    ax.annotate("", (-16450, -6900), (-15000, -6900), arrowprops=dict(arrowstyle="->", color="#a65a1f", lw=.8))
    ax.text(-14800, -6900, "stopped by the board's edge", va="center", fontsize=6.5, color="#a65a1f")
    ax.plot([-3000, 2000], [-6900, -6900], color=st.INK, lw=1)
    ax.text(-500, -6500, "5,000 cells", ha="center", va="bottom", fontsize=6.5)

    top = .42 + mh + .5
    ax = axes(.68, top, W - .8, .95)
    t = np.array(times) / 1e9
    v = np.array([f["visited_cells"] for f in frames]) / 1e6
    before = np.array(times) <= SWITCH
    ax.plot(np.r_[0, t[before]], np.r_[0, v[before]], color=st.ANT, lw=1.5)
    ax.plot(np.r_[t[before][-1], t[~before]], np.r_[v[before][-1], v[~before]], color="#d9822b", lw=1.5)
    ax.set(xlim=(0, 13.3), ylim=(0, 90), xticks=[0, 4, 8, 12], yticks=[0, 40, 80],
           xlabel="step $t$ (billions)", ylabel="cells visited\n(millions)")
    growth = (end["visited_cells"] - pre["visited_cells"]) / pre["visited_cells"]
    fig.text(.12 / W, 1 - (top - .38) / H, f"(b) The last {100 * frac_time:.1f}% of the steps reach\n"
             f"{growth:.1f}× as many new cells as all the rest", va="top", fontsize=8)

    # 40 x 40 cells, small enough to see single cells. The wake window includes the front (blank to the west).
    top += .95 + .9
    windows = {"blob": (slice(108, 148), slice(108, 148)), "wake": (slice(108, 148), slice(112, 152))}
    fig.text(.12 / W, 1 - (top - .38) / H, "(c) 40 × 40 cells near the ant", va="top", fontsize=8)
    for i, (name, label) in enumerate([("blob", "inside the blob:\nno visible order"),
                                       ("wake", "in the wake: rows identical,\ncolumns repeat every 3")]):
        ax = axes(.12 + i * 1.62, top + .02, 1.36, 1.36)
        crop = np.asarray(Image.open(RES / f"crop_{name}.png"))[windows[name]]
        vis = crop != 255
        ax.imshow(st.cells_img(np.where(vis, crop, 0), vis, 6), origin="lower", interpolation="nearest")
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(True); sp.set_color("#aaa9a2"); sp.set_linewidth(.5)
        ax.text(0, -.05, label, transform=ax.transAxes, va="top", fontsize=6.5)
    fig.text(.12 / W, .06 / H, "One deterministic blank-board run, 32,768² board. White: never visited.",
             fontsize=5.8, color="#666")
    fig.savefig(RES / "portrait.png", dpi=300, facecolor="white", metadata={"Software": None})
    digests = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [RES / "portrait.png", RES / "territory_map.png"]}
    (RES / "figure.json").write_text(json.dumps(dict(
        command="uv run experiments/2026-10-21-rlrlll-portrait/scripts/figure.py", switch_t=SWITCH,
        end_t=t_end, last_fraction_of_time=frac_time, visited_at_switch_frame=pre["visited_cells"],
        visited_at_end=end["visited_cells"], outputs_sha256=digests), indent=1) + "\n")
    print(digests)


if __name__ == "__main__":
    main()
