"""uv run research-outputs/working-papers/cube-root-growth/memory_figures.py; seed-301 paths from examples/memory_paths.rs.
Inputs: experiments/archive/2026-10-memory-walkers/dumps/memory_paths.csv and experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot/combined.csv.
Outputs and recipes are recorded in research-outputs/working-papers/cube-root-growth/fig/memory_recipe.json.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import polars as pl
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import style

style.apply()
names = {"ant:RLR": "Ant RLR", "rotor": "Rotor", "rw": "Random walk",
         "cookie:0.25": "East cookie B=0.25", "cookie:0.75": "East cookie B=0.75",
         "rcookie:0.25": "Random cookie B=0.25", "rcookie:0.75": "Random cookie B=0.75",
         "errw:1": "Reinforced edge I=1", "errw:4": "Reinforced edge I=4"}
paths = pl.read_csv("experiments/archive/2026-10-memory-walkers/dumps/memory_paths.csv")
assert set(paths["spec"].unique()) == set(names), "missing illustration model"
for spec in names:
    steps = paths.filter(pl.col("spec") == spec)["t"].to_numpy()
    assert np.array_equal(steps, np.arange(65537)), f"incomplete path: {spec}"
fig, axes = plt.subplots(3, 3, figsize=(style.W, 6.0), layout="constrained")
for ax, (spec, title) in zip(axes.flat, names.items()):
    g = paths.filter(pl.col("spec") == spec)
    xy = g.select("x", "y").to_numpy()
    pts, counts = np.unique(xy, axis=0, return_counts=True)
    dots = ax.scatter(pts[:, 0], -pts[:, 1], c=counts, norm=LogNorm(1, 65536), cmap="viridis", s=2, rasterized=True)
    tail = xy[-1025:]
    ax.plot(tail[:, 0], -tail[:, 1], color="#c85136", lw=.4, alpha=.8)
    ax.scatter([0], [0], s=9, marker="+", color="#111111", zorder=5)
    ax.set_aspect("equal", adjustable="box")
    if spec.startswith("cookie:"):
        ax.set_aspect("auto")
        ax.set_box_aspect(1)
        ax.text(.03, .96, "y-axis expanded", transform=ax.transAxes, va="top", fontsize=6,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": .8})
        ax.locator_params(axis="x", nbins=3)
        ax.locator_params(axis="y", nbins=3)
    ax.set_title(title)
    ax.tick_params(labelsize=6)
    ax.set_xlabel("x (cells)", fontsize=6)
    ax.set_ylabel("y (cells)", fontsize=6)
fig.colorbar(dots, ax=axes.ravel().tolist(), shrink=.55, label="Position samples per site (log scale)")
style.save(fig, "research-outputs/working-papers/cube-root-growth/fig/memory_paths.pdf")

plt.close(fig)

d = pl.read_csv("experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot/combined.csv")
colours = {"rotor": style.ROTOR, "rw": style.RANDOM, "cookie:0.25": "#dca02c",
           "cookie:0.75": "#8c6d31", "rcookie:0.25": "#1fa187", "rcookie:0.75": "#317873",
           "errw:1": "#7a3b8f", "errw:4": "#3b4cc0"}
fig, axes = plt.subplots(1, 2, figsize=(style.W, 3.25))
for spec, color in colours.items():
    g = d.filter(pl.col("rule").str.starts_with(spec + ":")).filter(pl.col("k") >= 12)
    means = []
    for k in sorted(g["k"].unique()):
        rows = g.filter(pl.col("k") == k)
        t = float(rows["t"][0])
        a = rows["area"].to_numpy().astype(float)
        kap = rows["boundary_steps"].to_numpy() / (t / 2) * a / rows["perimeter"].to_numpy()
        means.append((t, np.exp(np.mean(np.log(a))), np.mean(kap), len(rows)))
    m = np.array(means)
    for (_,), seed in g.group_by("rule", maintain_order=True):
        seed = seed.sort("k")
        t = seed["t"].to_numpy()
        a = seed["area"].to_numpy()
        axes[0].plot(t, a, color=color, alpha=.16, lw=.6)
        axes[1].plot(t, seed["boundary_steps"].to_numpy() / (t / 2) * a / seed["perimeter"].to_numpy(), color=color, alpha=.16, lw=.6)
    label = names[spec].replace("East cookie", "East").replace("Random cookie", "Random arrow").replace("Reinforced edge", "Edge")
    for ax, col in zip(axes, (1, 2)):
        ax.plot(m[:, 0], m[:, col], color=color, lw=1.4, label=label,
                ls="--" if spec.startswith("cookie:") else "-")
    if spec.startswith("cookie:"):
        axes[0].annotate(f"n={int(m[-1, 3])}", (m[-1, 0], m[-1, 1]), fontsize=6, color=color, xytext=(3, 0), textcoords="offset points")
t = np.exp2(np.arange(12, 21))
axes[0].plot(t, 21384.5 * (t / 2**18) ** (2/3), **style.GUIDE)
axes[0].text(2**19, 37000, r"$t^{2/3}$", fontsize=7, color="#777777")
for ax in axes:
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("Steps t")
axes[0].set_ylabel("Visited area A")
axes[1].set_ylabel(r"Boundary occupancy ratio $\kappa$")
axes[1].axhline(1, **style.GUIDE)
axes[0].set_title("Visited area")
axes[1].set_title("Boundary occupancy")
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=6)
fig.tight_layout(rect=(0, .17, 1, 1))
style.save(fig, "research-outputs/working-papers/cube-root-growth/fig/memory_growth.pdf")

plt.close(fig)
inputs = ["experiments/archive/2026-10-memory-walkers/dumps/memory_paths.csv", "experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot/combined.csv", "research-outputs/working-papers/cube-root-growth/memory_figures.py", "research-outputs/working-papers/cube-root-growth/style.py", "examples/memory_paths.rs"]
Path("research-outputs/working-papers/cube-root-growth/fig/memory_recipe.json").write_text(json.dumps({"command": "uv run research-outputs/working-papers/cube-root-growth/memory_figures.py",
    "path_command": "cargo run --release --example memory_paths -- 301 16 > experiments/archive/2026-10-memory-walkers/dumps/memory_paths.csv",
    "path_seed": 301, "path_steps": 65536,
    "sha256": {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in inputs}}, indent=2) + "\n")

