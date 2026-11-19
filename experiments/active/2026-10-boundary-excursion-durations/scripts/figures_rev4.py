# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Revision 4 figure: mean excursion duration vs mean max depth, per kind, for the retained windows of
results/rev4_analysis.json (d-bins inside the fitted range [4, floor L], count >= 20), normalised by
the bin nearest d = 4. Dashed guides: slopes 2 (area) and 1 (line). Writes results/figures/rev4_depth_duration.png."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import depth_score as ds  # noqa: E402

RES = Path(__file__).resolve().parents[1] / "results"
KINDS = ("eden", "idla", "idlar", "rotor", "mf", "bal")


def main():
    rep = json.loads((RES / "rev4_analysis.json").read_text())
    dh = ds.load_dhist(RES / "rev4_calib_dhist.csv")
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.5), sharex=True, sharey=True)
    for ax, kind in zip(axes.flat, KINDS):
        s = rep[kind]
        for w in s["windows"]:
            rows = dh[(f"{kind}:{w['seed']}", w["k"])]["d"]
            sel = [r for r in rows if r[0] >= ds.D_LO and r[1] <= math.floor(w["L"]) and r[2] >= ds.BIN_MIN]
            md = np.array([r[4] / r[2] for r in sel])
            mt = np.array([r[3] / r[2] for r in sel])
            ax.loglog(md / md[0], mt / mt[0], "-", lw=0.8, alpha=0.5, color="C0")
        x = np.logspace(0, 1.3, 10)
        ax.loglog(x, x**2, "k--", lw=1, label="slope 2")
        ax.loglog(x, x, "k:", lw=1, label="slope 1")
        b = s["beta"]
        ax.set_title(f"{kind}: β = {b:.2f} ({s['call']}), {s['n_windows']} windows" if b is not None else kind, fontsize=10)
        ax.grid(alpha=0.3, which="both")
    for ax in axes[1]:
        ax.set_xlabel("mean max depth d / first fitted bin")
    for ax in axes[:, 0]:
        ax.set_ylabel("mean duration τ / first fitted bin")
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Rev4 depth–duration readout on walkers (calibration only; no ant data)")
    fig.tight_layout()
    out = RES / "figures" / "rev4_depth_duration.png"
    fig.savefig(out, dpi=110)
    print("wrote", out)


if __name__ == "__main__":
    main()
