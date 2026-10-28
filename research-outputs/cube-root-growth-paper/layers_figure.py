"""Layer profiles rho(d): crust vs ordinary ant rules, rotor and persistent-walk references (audits 22-24).

Run: uv run research-outputs/cube-root-growth-paper/layers_figure.py
Recomputes rho(d) from the committed layer counts with the same formula and window (k >= 22) as
experiments/archive/2026-10-layers-colours/scripts/layers_stats.py; the crust label is read from results/layers_classes.txt.
d = Manhattan distance to never-visited ground minus one; rho(d) = visits per cell relative to the territory mean; rho(0) = kappa.
The last layer (index 5) pools all depths >= 5. No fits. Numbers go to fig/layers_numbers.json.
"""
import hashlib
import json
from pathlib import Path
import re

import numpy as np
import polars as pl
import matplotlib.pyplot as plt

import style as st

ROOT = Path(__file__).resolve().parents[2]
R = ROOT / "experiments/archive/2026-10-layers-colours/results"
OUT = Path(__file__).resolve().parent / "fig"
NL = 6


def rho_profiles(csv):
    d = pl.read_csv(csv).filter(pl.col("k") >= 22)
    out = {}
    for (w,), g in d.group_by("walker", maintain_order=True):
        acc = []
        for r in g.iter_rows(named=True):
            s = np.array([r[f"sn{i}"] for i in range(NL)], float)
            n = (np.array([r[f"bn{i}"] for i in range(NL)], float) + np.array([r[f"en{i}"] for i in range(NL)], float)) / 2
            acc.append((s / n) / (s.sum() / n.sum()))
        out[w] = np.mean(acc, axis=0)
    return out


def crust_labels():
    lab = {}
    for line in (R / "layers_classes.txt").read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\W*([RL]{5,})\s*\W+\s*(true|false)\b", line)
        if m:
            lab[m.group(1)] = m.group(2) == "true"
    return lab


def main():
    st.apply()
    OUT.mkdir(exist_ok=True)
    ext, typ = rho_profiles(R / "layers.csv"), rho_profiles(R / "layers_typical.csv")
    lab = crust_labels()
    ants = {w: p for src in (ext, typ) for w, p in src.items() if re.fullmatch(r"[RL]+", w)}
    missing = [w for w in ants if w not in lab]
    assert not missing, f"no crust label for {missing}"
    rotors = np.array([p for w, p in ext.items() if w.startswith("rotor")])
    pws = np.array([p for w, p in ext.items() if w.startswith("pw")])
    x = np.arange(NL)
    fig, ax = plt.subplots(figsize=(st.W_HALF * 1.45, 2.9))
    for w, p in ants.items():
        ax.plot(x, p, color=st.LOG if lab[w] else st.ANT, lw=.7, alpha=.55)
    ax.plot(x, rotors.mean(0), color=st.ROTOR, lw=2, marker="o", ms=3, label=f"rotor (mean of {len(rotors)})")
    ax.plot(x, pws.mean(0), color=st.RANDOM, lw=1.6, ls="--", label=f"persistent walk (mean of {len(pws)})")
    ax.plot([], [], color=st.LOG, lw=1.2, label=f"ants with crust ({sum(lab[w] for w in ants)})")
    ax.plot([], [], color=st.ANT, lw=1.2, label=f"ants without crust ({sum(not lab[w] for w in ants)})")
    ax.axhline(1, **st.GUIDE)
    ax.set_yscale("log")
    ax.set_xticks(x, ["0", "1", "2", "3", "4", "≥5"])
    ax.set_xlabel("layer depth d (0 = edge cells)")
    ax.set_ylabel(r"$\rho(d)$ = visits per cell / territory mean")
    ax.tick_params(labelsize=7)
    ax.legend(frameon=False, fontsize=6.5, loc="upper right")
    fig.tight_layout()
    st.save(fig, OUT / "layers.pdf")
    nums = dict(n_ants=len(ants), n_crust=sum(lab[w] for w in ants), window="k>=22",
                rho_ant_crust_median=np.median([p for w, p in ants.items() if lab[w]], axis=0).tolist(),
                rho_ant_plain_median=np.median([p for w, p in ants.items() if not lab[w]], axis=0).tolist(),
                rho_rotor_mean=rotors.mean(0).tolist(), rho_pw_mean=pws.mean(0).tolist(),
                input_sha256={f: hashlib.sha256((R / f).read_bytes()).hexdigest() for f in ("layers.csv", "layers_typical.csv", "layers_classes.txt")})
    (OUT / "layers_numbers.json").write_text(json.dumps(nums, indent=2) + "\n")
    print(json.dumps({k: v for k, v in nums.items() if k != "input_sha256"}, indent=1))


if __name__ == "__main__":
    main()
