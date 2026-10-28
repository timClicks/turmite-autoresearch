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


CUP_GROUPS = [(f"p={p}", f"cup:{p}:") for p in ("0.05", "0.10", "0.25")]


def plot_compactness(windows, out_stem, groups=CUP_GROUPS, title="Revision-1 cup compactness diagnostics"):
    """A/P^2 and L vs k, seed-averaged per group (label, spec prefix)."""
    rows = [w for w in windows if any(w["spec"].startswith(pre) for _, pre in groups) and w["escaped"] == "false"]
    if not rows:
        return
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for label, pre in groups:
        sub = [w for w in rows if w["spec"].startswith(pre)]
        by_k = {}
        for w in sub:
            k = int(w["k"])
            A, P, L = int(w["area"]), int(w["perimeter"]), float(w["L"])
            by_k.setdefault(k, []).append((A / (P * P) if P else float("nan"), L, A))
        ks = sorted(by_k)
        ap2 = [sum(x[0] for x in by_k[k]) / len(by_k[k]) for k in ks]
        Ls = [sum(x[1] for x in by_k[k]) / len(by_k[k]) for k in ks]
        axes[0].plot(ks, ap2, "o-", label=label)
        axes[1].plot(ks, Ls, "o-", label=label)
    axes[0].axhline(0.04, color="k", ls="--", lw=1, label="threshold 0.04")
    axes[0].set_xlabel("k"); axes[0].set_ylabel(r"$A/P^2$")
    axes[0].set_title("isoperimetric proxy")
    axes[1].set_xlabel("k"); axes[1].set_ylabel("L = A/P")
    axes[1].set_title("linear size")
    for ax in axes:
        ax.grid(True, alpha=0.3); ax.legend(fontsize=8)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(FIG / f"{out_stem}.png", dpi=120)
    plt.close(fig)


def main():
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "stage1"
    if mode == "stage1":
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
    elif mode == "rev1":
        w = load_windows(RES / "rev1_calib_windows.csv")
        h = load_hist(RES / "rev1_calib_hist.csv")
        for p in ("0.05", "0.10", "0.25"):
            plot_group(f"cup p={p}", w, h, lambda s, pp=p: s.startswith(f"cup:{pp}:"), f"ccdf_cup_{p.replace('.', '')}")
        plot_group("mean-field (rev1)", w, h, lambda s: s.startswith("mf:"), "ccdf_mf_rev1")
        plot_group("rotor (rev1)", w, h, lambda s: s.startswith("rotor:"), "ccdf_rotor_rev1")
        plot_compactness(w, "cup_compactness")
    elif mode == "rev2":
        w = load_windows(RES / "rev2_calib_windows.csv")
        h = load_hist(RES / "rev2_calib_hist.csv")
        plot_group("Eden-style walker", w, h, lambda s: s.startswith("eden:"), "ccdf_eden")
        plot_group("internal DLA", w, h, lambda s: s.startswith("idla:"), "ccdf_idla")
        plot_group("internal DLA, restart excursions dropped", w, h, lambda s: s.startswith("idlar:"), "ccdf_idlar")
        plot_group("mean-field (rev2)", w, h, lambda s: s.startswith("mf:"), "ccdf_mf_rev2")
        plot_group("rotor (rev2)", w, h, lambda s: s.startswith("rotor:"), "ccdf_rotor_rev2")
        plot_compactness(w, "rev2_compactness", groups=[("Eden-style", "eden:"), ("internal DLA", "idla:")],
                         title="Revision-2 compactness diagnostics (seed means)")
    elif mode == "confirm" and (RES / "confirm_windows.csv").exists():
        w = load_windows(RES / "confirm_windows.csv")
        h = load_hist(RES / "confirm_hist.csv")
        plot_group("confirmation ants", w, h, lambda s: "@" in s, "ccdf_confirm")
        for rule in sorted({r["spec"].split("@")[0] for r in w}):
            plot_group(f"confirm {rule}", w, h, lambda s, r=rule: s.startswith(r + "@"), f"ccdf_confirm_{rule}")
    print("wrote", sorted(FIG.glob("*.png")))


if __name__ == "__main__":
    main()
