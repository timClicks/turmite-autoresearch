"""Figure: local area exponent per octave for the factorial's corners and the controls.

usage (repo root): uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/figure.py [RESULTS_DIR]
Reads results/probe.csv and results/stage2_probe.csv; writes results/fig_local_exponents.png.
Local exponent at octave k = log2 A(2^k) - log2 A(2^(k-1)), averaged over runs (and rules).
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
# Optional first argument: a results directory (e.g. a fresh rerun); default is the committed one.
RES = Path(sys.argv[1]) if len(sys.argv) > 1 else EXP / "results"
s1 = pl.read_csv(RES / "probe.csv")
s2 = pl.read_csv(RES / "stage2_probe.csv")


def local(df: pl.DataFrame, pattern: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    per_run = []
    for spec in df.filter(pl.col("rule").str.contains(pattern))["rule"].unique().sort():
        g = df.filter(pl.col("rule") == spec).sort("k")
        k = g["k"].to_numpy()
        per_run.append(dict(zip(k[1:], np.diff(np.log2(g["area"].to_numpy().astype(float))))))
    ks = np.array(sorted(set().union(*per_run)))
    ks = ks[ks >= 12]
    vals = [[r[k] for r in per_run if k in r] for k in ks]
    return ks, np.array([np.mean(v) for v in vals]), np.array([np.std(v) / np.sqrt(len(v)) for v in vals])


series = [
    ("ant, deterministic (6 rules)", s1, r"^hy:[RL]+:0:0:0$", "#1b6ca8", "o"),
    ("F1: memory, no wall (6 rules x 8)", s1, r"^hy:[RL]+:0:1:", "#c0392b", "s"),
    ("V1 hybrid: wall, no memory (16)", s2, r"^hy:RL:1:0:", "#8e44ad", "^"),
    ("memoryless walker, pw:0.5 (8)", s1, r"^hy:RL:1:1:", "#7f8c8d", "v"),
    ("rotor (8)", s2, r"^rotor:", "#27ae60", "D"),
]
fig, ax = plt.subplots(figsize=(7.5, 4.6), dpi=150)
for label, df, pat, colour, marker in series:
    k, m, se = local(df, pat)
    ax.errorbar(k, m, yerr=se, label=label, color=colour, marker=marker, ms=4, lw=1.2, capsize=2)
ax.axhline(2 / 3, color="black", lw=0.8, ls="--")
ax.text(12.2, 2 / 3 - 0.025, "a = 2/3", fontsize=8)
ax.set_xlabel("octave k (window ends at 2^k steps)")
ax.set_ylabel("local area exponent  (log2 A ratio per octave)")
ax.set_ylim(0.45, 1.05)
ax.set_title("Removing the wall makes the ant porous; the wall alone gets most of the way", fontsize=10)
ax.legend(fontsize=7.5, loc="upper right", frameon=False)
fig.tight_layout()
fig.savefig(RES / "fig_local_exponents.png")
print("wrote results/fig_local_exponents.png")
