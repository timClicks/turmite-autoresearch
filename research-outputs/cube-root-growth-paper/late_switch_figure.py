"""RLRLLL switch, archived wake and post-hoc sweep consistency check.

Run: uv run research-outputs/cube-root-growth-paper/late_switch_figure.py
Only compact results are read; regenerate those with g1_wake_extract.py.
No random sampling, fits or instruments beyond the previously reported check.
"""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import polars as pl
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import style as st

ROOT = Path(__file__).resolve().parents[2]
G1 = ROOT / "experiments/archive/2026-10-g1-ribbon-breakout/results"
OUT = Path(__file__).resolve().parent / "fig"
TIMES = (12_800_000_000, 12_900_000_000)
HALF_WINDOW = 20_000_000


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    st.apply()
    OUT.mkdir(exist_ok=True)
    inputs = [G1 / "g1_ribbon.csv", G1 / "g1_wake_extract.json"]
    inputs += [G1 / f"g1_wake_crop_{TIMES[0]}.csv", G1 / f"g1_sweep_trace_{TIMES[0]}.csv"]
    d = pl.read_csv(inputs[0]).with_columns(dt=pl.col("t_end").diff().fill_null(pl.col("t_end")))
    fine = d.filter(pl.col("dt") <= 1_000_000)
    # Retain the original onset definition, including the last partial window.
    good = fine["steps_per_new"].to_numpy() < 8
    onset = int(fine["t_end"][int(np.flatnonzero(~good)[-1]) + 1])
    ext = json.loads(inputs[1].read_text())["dumps"]
    pm = {}
    for t0 in TIMES:
        e = ext[str(t0)]
        absx = (abs(e["x_start"]) + abs(e["x_end"])) / 2
        # Match the archived analysis: strict symmetric +/-2e7 window; fit |x|,
        # then evaluate 2|x| d|x|/dt at the dump time (not a new x^2 fit).
        w = fine.filter((pl.col("t_end") - t0).abs() < HALF_WINDOW)
        t = w["t_end"].to_numpy().astype(float)
        x = np.abs(w["x"].to_numpy().astype(float))
        velocity = np.polyfit(t - t0, x, 1)[0]
        measured = 2 * np.interp(t0, t, x) * velocity
        pm[str(t0)] = dict(L=e["L_traj"], abs_x=absx,
                            predicted=absx / (2 * e["L_traj"]),
                            measured=float(measured), n_windows=w.height)
    assert onset == 12_677_000_000
    assert [round(pm[str(t)]["predicted"], 2) for t in TIMES] == [.86, .84]
    assert [round(pm[str(t)]["measured"], 2) for t in TIMES] == [.86, .83]

    fig = plt.figure(figsize=(st.W, 4.35))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.2], width_ratios=[1.15, 1.1, 1.35],
                          hspace=.64, wspace=.65)
    ax = fig.add_subplot(gs[0, :])
    finite = d.filter(pl.col("steps_per_new").is_finite())
    # Colour denotes the physical regime; window size is recorded in the caption.
    for mask, colour in [(pl.col("t_end") < onset, st.ANT), (pl.col("t_end") >= onset, st.BUILDER)]:
        w = finite.filter(mask)
        ax.plot(w["t_end"] / 1e10, w["steps_per_new"], ".", ms=1.9, color=colour)
    empty = d.filter(~pl.col("steps_per_new").is_finite())
    ax.plot(empty["t_end"] / 1e10, np.full(empty.height, 24000), "|", color=st.INK, ms=3, mew=.5)
    ax.axhline(4, **st.GUIDE)
    ax.axvline(onset / 1e10, **st.GUIDE)
    ax.set(yscale="log", ylim=(2.5, 40000), xlim=(0, 1.31),
           xlabel=r"step $t$ ($\times10^{10}$)", ylabel="steps per new cell")
    ax.set_title("(a) A sudden switch after 12.677 billion steps", pad=8)
    ax.text(.05, 1500, "blob", color=st.ANT, fontsize=7)
    ax.text(.03, 5.5, "4 steps per cell", color=st.BUILDER, fontsize=6.5)
    ax.annotate("column sweeper", (1.283, 4.05), (.92, 35), fontsize=7, color=st.BUILDER,
                arrowprops=dict(arrowstyle="->", color=st.BUILDER, lw=.6))
    ax.text(.85, .93, "top ticks: no new cells", transform=ax.transAxes, ha="right", fontsize=6)

    ax = fig.add_subplot(gs[1, 0])
    e = ext[str(TIMES[0])]
    crop = pl.read_csv(inputs[2])["colour"].to_numpy().reshape(e["crop"]["rows"], e["crop"]["cols"])
    # Square cells; the selected 48-row view includes the sloping low-y boundary.
    crop = crop[:48]
    vis = crop != 255
    ax.imshow(st.cells_img(np.where(vis, crop, 0), vis, 6), origin="lower", interpolation="nearest")
    st.clean(ax)
    ax.set_title("(b) Period-3 wake", pad=8)
    ax.plot([9, 9, 12, 12], [-4, -2.5, -2.5, -4], color=st.INK, lw=.7, clip_on=False)
    ax.text(17, -3, "3 columns", va="center", fontsize=6)
    ax.legend(handles=[Patch(facecolor=st.CELL[c], label=str(c)) for c in range(6)],
              ncol=3, loc="upper center", bbox_to_anchor=(.5, -.09), handlelength=.8,
              columnspacing=.65, handletextpad=.3, title="cell state", title_fontsize=6)

    ax = fig.add_subplot(gs[1, 1])
    tr = pl.read_csv(inputs[3])
    ax.plot(tr["t_rel"] / 1e5, tr["y"] / 1e3, lw=.7, color=st.BUILDER)
    ax.set(xlabel=r"elapsed steps ($\times10^5$)", ylabel=r"$y$ ($10^3$ cells)", ylim=(-4.5, 2.7))
    ax.set_title("Back-and-forth sweeps", pad=8)
    ax.text(.5, -.42, r"slow traverse $\approx10$ steps/row" "\n" r"fast return $\approx2$ steps/row",
            transform=ax.transAxes, ha="center", fontsize=6)

    ax = fig.add_subplot(gs[1, 2])
    ax.set_title("(c) Sweep prediction", pad=8)
    for i, t0 in enumerate(TIMES):
        v = pm[str(t0)]
        ax.plot([i-.07, i+.07], [v["predicted"], v["measured"]], color="#aaa9a2", lw=.6)
        ax.plot(i-.07, v["predicted"], "o", mfc="white", mec=st.INK, ms=5.5,
                label=r"predicted $|x|/(2L)$" if i == 0 else None)
        ax.plot(i+.07, v["measured"], "o", color=st.BUILDER, ms=3.5,
                label="measured" if i == 0 else None)
        ax.text(i, .50, f"{v['predicted']:.2f} / {v['measured']:.2f}", ha="center", fontsize=7)
    ax.set(xlim=(-.55, 1.55), ylim=(0, 1.1), ylabel=r"$d|x|^2/dt$",
           xlabel=r"dump time ($\times10^{10}$)")
    ax.set_xticks([0, 1], ["1.28\n$L=6,400$", "1.29\n$L=8,610$"])
    ax.legend(loc="lower left", fontsize=6, handletextpad=.4, labelcolor=st.INK)
    fig.subplots_adjust(left=.095, right=.985, top=.94, bottom=.15)
    st.save(fig, OUT / "late_switch.pdf")
    recipe = dict(command="uv run research-outputs/cube-root-growth-paper/late_switch_figure.py",
                  git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  seed="none: deterministic blank-board RLRLLL; one trajectory",
                  onset_t=onset, half_window_steps=HALF_WINDOW,
                  measured_method="2|x(t0)| times OLS slope of |x|; strict symmetric window",
                  d_abs_x_sq_dt=pm, crop_view_rows=48,
                  sha256={str(p.relative_to(ROOT)): sha(p) for p in inputs + [Path(__file__), Path(st.__file__)]},
                  outputs_sha256={f"late_switch.{s}": sha(OUT / f"late_switch.{s}") for s in ("pdf", "png")})
    (OUT / "late_switch_numbers.json").write_text(json.dumps(recipe, indent=2) + "\n")
    print(json.dumps(pm, indent=2))


if __name__ == "__main__":
    main()
