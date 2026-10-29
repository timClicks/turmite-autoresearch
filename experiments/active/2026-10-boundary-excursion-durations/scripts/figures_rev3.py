# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""Revision 3 figures: time-weighted survival S_tw vs s/L and s/L^2 per kind (retained windows),
from committed results/rev3_calib_*.csv. Writes results/figures/rev3_tw_<kind>.png."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyse as A  # noqa: E402
import analyse_rev3 as R  # noqa: E402
import tw_score as tw  # noqa: E402

FIG = R.RES / "figures"
U = np.logspace(-8, 8, 400, base=2)


def main():
    FIG.mkdir(exist_ok=True)
    W = A.load_windows(R.RES / "rev3_calib_windows.csv")
    fh = R.load_fhist(R.RES / "rev3_calib_fhist.csv")
    for kind in R.KINDS:
        kept, _ = R.retained_tw(kind, W, fh)
        if not kept:
            continue
        Ls = np.array([w["L"] for w in kept])
        norm = matplotlib.colors.LogNorm(Ls.min(), Ls.max())
        fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
        for ax, p, lab in ((axes[0], 1, "s / L"), (axes[1], 2, "s / L²")):
            for w in kept:
                M = tw.mass_above(w["fbins"], U * w["L"] ** p)
                ax.plot(U, M / w["total"], color=plt.cm.viridis(norm(w["L"])), lw=0.8, alpha=0.8)
            ax.set_xscale("log", base=2)
            ax.set_xlabel(lab)
            ax.axhspan(0.05, 0.95, color="0.92", zorder=-1)
        axes[0].set_ylabel("time-weighted survival S_tw")
        fig.suptitle(f"Rev3 {kind}: time-weighted survival, {len(kept)} retained windows (colour = L)")
        fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap="viridis"), ax=axes, label="L = A/P")
        fig.savefig(FIG / f"rev3_tw_{kind}.png", dpi=90)
        plt.close(fig)
        print("wrote", FIG / f"rev3_tw_{kind}.png")


if __name__ == "__main__":
    main()
