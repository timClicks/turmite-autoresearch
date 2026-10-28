"""Walker map in the (area exponent a, kappa) plane: ants vs rotor, random walk, memory walkers and the noisy-rotor path.

Run: uv run research-outputs/scholarly-articles/cube-root-growth/walker_map_figure.py
Inputs (all committed): probe_summary.csv (ants, 3055 rules, per-rule fits over k = 20..26), memory_walkers_pilot/summary.json
(per-seed fits, window k = 16..20, kappa at 2^20) and arm-kappa-depletion-arms/armb_probe.csv (noisy rotor, fitted with the same
experiments/_lib/analyse_probe.per_rule as armb_stats.py; median by eps). No new fits except that re-grouping.
Caveat (also in the caption): the three sources use different windows, so the rotor sits at a ~ 0.69-0.72 in all of them
but kappa differs with the window (the memory pilot's kappa is read at 2^20, the others are window means).
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import polars as pl
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/_lib"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import style as st  # noqa: E402
from analyse_probe import per_rule  # noqa: E402

OUT = Path(__file__).resolve().parent / "fig"
ANTS = ROOT / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv"
MEM = ROOT / "experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot/summary.json"
NOISE = ROOT / "experiments/archive/2026-10-arm-kappa-depletion-arms/results/armb_probe.csv"
FAMILIES = {"rw": ("random walk", st.RANDOM, "o"), "rotor": ("rotor", st.ROTOR, "s"),
            "rcookie:0.25": ("random cookie B=.25", "#9aa5ea", "^"), "rcookie:0.75": ("random cookie B=.75", "#5fb3d9", "v"),
            "errw:1": ("edge reinf. I=1", st.BUILDER, "D"), "errw:4": ("edge reinf. I=4", "#444444", "P")}


def main():
    st.apply()
    OUT.mkdir(exist_ok=True)
    ants = pl.read_csv(ANTS).filter(pl.col("a").is_finite() & (pl.col("kappa") > 0))
    mem = json.loads(MEM.read_text())
    noise = per_rule(pl.read_csv(NOISE)).with_columns(eps=pl.col("rule").str.split(":").list.get(1).cast(pl.Float64))
    path = noise.group_by("eps").agg(n=pl.len(), a=pl.col("a").median(), kappa=pl.col("kappa").median()).sort("eps")

    fig, ax = plt.subplots(figsize=(st.W, 3.5))
    for cls, col, lab in (("log", st.LOG, "ants, log-growth rules"), ("blob", st.ANT, "ants, blob rules")):
        s = ants.filter(pl.col("cls") == cls)
        ax.scatter(s["a"], s["kappa"], s=3, color=col, alpha=.25, lw=0, label=f"{lab} ({s.height})", rasterized=True)
    nums = {"ants": {"n": ants.height}}
    for fam, (lab, col, mk) in FAMILIES.items():
        fits = mem[fam]["windows"]["16..20"]["fits"]
        if not fits:
            continue
        a = np.array([f["area_slope"] for f in fits])
        k = np.array([f["kappa"] for f in fits])
        ax.scatter(a, k, s=9, color=col, marker=mk, alpha=.5, lw=0)
        ax.scatter([a.mean()], [k.mean()], s=34, color=col, marker=mk, edgecolor="k", lw=.6, label=f"{lab} (n={len(fits)})", zorder=5)
        nums[fam] = dict(n=len(fits), a=float(a.mean()), kappa=float(k.mean()))
    ax.plot(path["a"], path["kappa"], color=st.ROTOR, lw=1, ls="-", marker="o", ms=3.5, mfc="white", zorder=4,
            label="rotor with arrow noise (path)")
    for r in path.iter_rows(named=True):
        ax.annotate(f"{r['eps']:g}", (r["a"], r["kappa"]), textcoords="offset points", xytext=(4, 3), fontsize=5.5, color=st.ROTOR)
    nums["noise_path"] = {f"{r['eps']:g}": dict(n=r["n"], a=r["a"], kappa=r["kappa"]) for r in path.iter_rows(named=True)}
    ax.axhline(1, **st.GUIDE)
    ax.axvline(2 / 3, **st.GUIDE)
    ax.set_yscale("log")
    ax.set_xlim(.45, 1.06)
    ax.set_ylim(.04, 30)
    nums["ants"]["log_class_total"] = int((ants["cls"] == "log").sum())
    nums["ants"]["outside_view"] = int(((ants["a"] < .45) | (ants["a"] > 1.06) | (ants["kappa"] < .04) | (ants["kappa"] > 30)).sum())
    ax.set_xlabel("area exponent $a$")
    ax.set_ylabel(r"boundary occupation $\kappa$")
    ax.tick_params(labelsize=7)
    leg = ax.legend(frameon=False, fontsize=6, loc="upper left", ncol=1, markerscale=.9, labelcolor=st.INK)
    for h in leg.legend_handles:
        h.set_alpha(1)
    fig.tight_layout()
    st.save(fig, OUT / "walker_map.pdf")
    nums["input_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ANTS, MEM, NOISE)}
    (OUT / "walker_map_numbers.json").write_text(json.dumps(nums, indent=2) + "\n")
    print(json.dumps({k: v for k, v in nums.items() if k != "input_sha256"}, indent=1))


if __name__ == "__main__":
    main()
