"""Edge gap: surface width W(t), ants vs rotor (audits 34, 35; A4/A4c).

Run: uv run research-outputs/cube-root-growth-paper/edge_gap_figure.py
Reads the committed pooled A4 + A4c shape files only (checkpoints at t = 2^k, one row per run and k). No refits beyond the
same finite-difference local exponent d(k) between k and k+2 that experiments/archive/2026-10-a4-boundary-width/scripts/a4c_stats.py
reports, so panel b should reproduce its 'pooled' lines; numbers go to fig/edge_gap_numbers.json.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import polars as pl
import matplotlib.pyplot as plt

import style as st

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "experiments/archive/2026-10-a4-boundary-width/results"
OUT = Path(__file__).resolve().parent / "fig"
FILES = {"ants": ["a4_shape_ants.csv", "a4c_shape_ants.csv"], "rotor": ["a4_shape_rotor.csv", "a4c_shape_rotor.csv"]}
COL = {"ants": st.ANT, "rotor": st.ROTOR}
KAPRI = .13  # alpha/3 reported by Kapri and Dhar, as quoted in the paper


def load(kind):
    return pl.concat([pl.read_csv(R / f).select("spec", "k", "Wsurf") for f in FILES[kind]]).filter(pl.col("Wsurf") > 0)


def local_exponents(d):
    """Per run, exponent between checkpoints k and k+2 (same definition as a4_stats/a4c_stats)."""
    out = {}
    for spec, g in d.group_by("spec"):
        g = g.sort("k")
        k, w = g["k"].to_numpy().astype(int), g["Wsurf"].to_numpy()
        for i in range(len(k) - 1):
            out.setdefault(int(k[i]), []).append((np.log(w[i + 1]) - np.log(w[i])) / ((k[i + 1] - k[i]) * np.log(2)))
    return out


def main():
    st.apply()
    OUT.mkdir(exist_ok=True)
    fig, (a, b) = plt.subplots(1, 2, figsize=(st.W, 2.7))
    nums = {}
    for kind in FILES:
        d = load(kind)
        ks = sorted(d["k"].unique().to_list())
        lnw = {k: np.log(d.filter(pl.col("k") == k)["Wsurf"].to_numpy()) for k in ks}
        m = np.array([lnw[k].mean() for k in ks])
        lo = np.array([np.quantile(lnw[k], .16) for k in ks])
        hi = np.array([np.quantile(lnw[k], .84) for k in ks])
        t = 2.0 ** np.array(ks)
        a.plot(t, np.exp(m), color=COL[kind], lw=1.3, label=f"{kind} (n = {d['spec'].n_unique()} runs)")
        a.fill_between(t, np.exp(lo), np.exp(hi), color=COL[kind], alpha=.18, lw=0)
        loc = local_exponents(d)
        kk = sorted(loc)
        mean = np.array([np.mean(loc[k]) for k in kk])
        sem = np.array([np.std(loc[k], ddof=1) / np.sqrt(len(loc[k])) if len(loc[k]) > 1 else np.nan for k in kk])
        b.errorbar(2.0 ** (np.array(kk) + 1), mean, yerr=sem, color=COL[kind], marker="o", ms=3, lw=1, capsize=1.5)
        big = [x for k in kk if k >= 22 for x in loc[k]]
        nums[kind] = dict(runs=d["spec"].n_unique(), k_max=max(ks), mean_d_k_ge_22=float(np.mean(big)),
                          local={str(k): [float(np.mean(loc[k])), len(loc[k])] for k in kk})
    a.set_xscale("log", base=2)
    a.set_yscale("log")
    a.set_xlabel("t (steps)")
    a.set_ylabel("surface width W (shaded: 16-84% over runs)")
    a.set_title("(a) W(t)", fontsize=8, color=st.INK)
    a.legend(frameon=False, fontsize=7)
    b.axhline(KAPRI, **st.GUIDE)
    b.text(b.get_xlim()[0] if False else 2.0 ** 13.2, KAPRI + .012, "Kapri–Dhar ≈ 0.13", fontsize=6.5, color="#666666")
    b.set_xscale("log", base=2)
    b.set_xlabel("t (midpoint of k, k+2)")
    b.set_ylabel("local exponent d ln W / d ln t")
    b.set_title("(b) local exponent (mean ± s.e. over runs)", fontsize=8, color=st.INK)
    for ax in (a, b):
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    st.save(fig, OUT / "edge_gap.pdf")
    nums["input_sha256"] = {f: hashlib.sha256((R / f).read_bytes()).hexdigest() for fs in FILES.values() for f in fs}
    (OUT / "edge_gap_numbers.json").write_text(json.dumps(nums, indent=2) + "\n")
    print(json.dumps({k: (v if k == "input_sha256" else {x: v[x] for x in v if x != "local"}) for k, v in nums.items()}, indent=1))


if __name__ == "__main__":
    main()
