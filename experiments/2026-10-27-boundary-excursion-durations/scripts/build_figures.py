# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26", "matplotlib>=3.8"]
# ///
"""CCDFs of completed excursion durations under tau/L and tau/L^2 scalings."""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

EXP = Path(__file__).resolve().parents[1]
RES = EXP / "results"
FIG = RES / "figures"
FIG.mkdir(exist_ok=True)
K_LO, K_HI = 16, 24


def load_windows(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def load_hist(path):
    h = defaultdict(dict)
    with path.open() as f:
        for r in csv.DictReader(f):
            b = int(r["log2_tau"])
            if b < 0:
                continue
            h[(r["spec"], int(r["k"]))][b] = int(r["count"])
    return h


def expand(bins):
    xs = []
    for b, c in bins.items():
        tau = 1.0 if b == 0 else (2**b + 2 ** (b - 1))
        xs.extend([tau] * c)
    return np.asarray(xs, float)


def ccdf(taus):
    if len(taus) == 0:
        return np.array([]), np.array([])
    t = np.sort(taus)
    s = 1.0 - np.arange(1, len(t) + 1) / len(t)
    return t, s


def plot_group(title, windows, hist, specs_filter, out_stem):
    rows = [w for w in windows if specs_filter(w["spec"]) and K_LO <= int(w["k"]) <= K_HI and w["escaped"] == "false"]
    if not rows:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    # colour by L
    Ls = [float(w["L"]) for w in rows]
    vmin, vmax = min(Ls), max(Ls)
    cmap = plt.cm.viridis
    for w in rows:
        L = float(w["L"])
        taus = expand(hist.get((w["spec"], int(w["k"])), {}))
        if len(taus) < 50:
            continue
        t, s = ccdf(taus)
        color = cmap((np.log(L) - np.log(vmin)) / max(1e-9, np.log(vmax) - np.log(vmin))) if vmax > vmin else "C0"
        axes[0].loglog(t / L, s, color=color, alpha=0.55, lw=1.0)
        axes[1].loglog(t / (L * L), s, color=color, alpha=0.55, lw=1.0)
    axes[0].set_xlabel(r"$\tau / L$")
    axes[1].set_xlabel(r"$\tau / L^2$")
    axes[0].set_ylabel(r"$S(\tau)$")
    axes[0].set_title(f"{title}: scale $L$")
    axes[1].set_title(f"{title}: scale $L^2$")
    for ax in axes:
        ax.grid(True, which="both", alpha=0.3)
        ax.set_ylim(1e-4, 1.05)
    fig.suptitle(title + " (completed only; exploratory if ant)")
    fig.tight_layout()
    fig.savefig(FIG / f"{out_stem}.png", dpi=120)
    plt.close(fig)


def main():
    calib_w = load_windows(RES / "calib_windows.csv")
    calib_h = load_hist(RES / "calib_hist.csv")
    plot_group("random walk", calib_w, calib_h, lambda s: s.startswith("rw:"), "ccdf_rw")
    plot_group("mean-field", calib_w, calib_h, lambda s: s.startswith("mf:"), "ccdf_mf")
    plot_group("rotor", calib_w, calib_h, lambda s: s.startswith("rotor:"), "ccdf_rotor")
    if (RES / "pilot_windows.csv").exists():
        pilot_w = load_windows(RES / "pilot_windows.csv")
        pilot_h = load_hist(RES / "pilot_hist.csv")
        plot_group("pilot ants (EXCLUDED)", pilot_w, pilot_h, lambda s: "@" in s, "ccdf_pilot")
        for rule in sorted({w["spec"].split("@")[0] for w in pilot_w}):
            plot_group(f"pilot {rule} (EXCLUDED)", pilot_w, pilot_h, lambda s, r=rule: s.startswith(r + "@"), f"ccdf_pilot_{rule}")
    print("wrote", list(FIG.glob("*.png")))


if __name__ == "__main__":
    main()
