"""Prefix lookup: predicted vs measured ln kappa on the fresh rules (audit 12 / W3c).

Run: uv run research-outputs/working-papers/cube-root-growth/prefix_figure.py
Reads only experiments/archive/2026-10-kappa-rule-space/results/prefix_audit_predictions.csv (leave-one-out encoding, linear area
term: the row behind the headline gain). No refits; R^2 is recomputed from the CSV and printed to fig/prefix_numbers.json.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import polars as pl
import matplotlib.pyplot as plt

import style as st

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "experiments/archive/2026-10-kappa-rule-space/results/prefix_audit_predictions.csv"
OUT = Path(__file__).resolve().parent / "fig"


def r2(y, p):
    return float(1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def panel(ax, y, p, title, colour):
    ax.scatter(p, y, s=7, color=colour, alpha=.65, lw=0)
    lo, hi = min(p.min(), y.min()), max(p.max(), y.max())
    ax.plot([lo, hi], [lo, hi], **st.GUIDE)
    ax.set_title(f"{title}\n$R^2$ = {r2(y, p):.2f}, n = {len(y)}", fontsize=7.5, color=st.INK)
    ax.set_xlabel("predicted ln κ")


def main():
    st.apply()
    OUT.mkdir(exist_ok=True)
    d = pl.read_csv(SRC).filter((pl.col("encoding") == "loo") & (pl.col("area") == "linear"))
    s, a = d.filter(pl.col("cohort") == "stationary"), d.filter(pl.col("cohort") == "all")
    fig, axes = plt.subplots(1, 3, figsize=(st.W, 2.4), sharey=False)
    panel(axes[0], s["target"].to_numpy(), s["baseline"].to_numpy(), "(a) stationary: ln A(2²²) only", st.RANDOM)
    panel(axes[1], s["target"].to_numpy(), s["prediction"].to_numpy(), "(b) stationary: + 8-letter prefix", st.ANT)
    panel(axes[2], a["target"].to_numpy(), a["prediction"].to_numpy(), "(c) all retained: + 8-letter prefix", st.ROTOR)
    axes[0].set_ylabel("measured ln κ (fresh rules)")
    for ax in axes:
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    st.save(fig, OUT / "prefix_lookup.pdf")
    nums = dict(
        stationary=dict(n=s.height, r2_baseline=r2(s["target"].to_numpy(), s["baseline"].to_numpy()),
                        r2_prefix=r2(s["target"].to_numpy(), s["prediction"].to_numpy())),
        all=dict(n=a.height, r2_baseline=r2(a["target"].to_numpy(), a["baseline"].to_numpy()),
                 r2_prefix=r2(a["target"].to_numpy(), a["prediction"].to_numpy())),
        input_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest())
    (OUT / "prefix_numbers.json").write_text(json.dumps(nums, indent=2) + "\n")
    print(json.dumps(nums, indent=2))


if __name__ == "__main__":
    main()
