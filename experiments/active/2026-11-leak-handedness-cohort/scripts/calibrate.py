"""Synthetic calibration of the P1 decision rule (no ant data).

usage (repo root): uv run --frozen python experiments/active/2026-11-leak-handedness-cohort/scripts/calibrate.py
Writes results/calibration.txt.

Model: per rule, early a at EF = 0 (one deterministic run per arm, no noise), EF = 1 pooled over 8 runs, and
EF = 0.3, 0.5 means over 4 seeds; per-seed sd SD (0.025 = median within-rule sd in the committed leak-titration
runs at EF 0.1..0.9, 0.04 as a stress value). Shared EF = 1 level ~ U(0.84, 0.92); each arm's EF = 0 level sits U(0.12, 0.30) below it. True rise fractions
F_R(0.3), F_R(0.5) ~ U(0.3, 0.6), U(0.6, 0.9); the L arm subtracts a true lag LAG (same for every rule) plus a
rule-level spread N(0, 0.05). Decision rule exactly as registered in the README.
"""
from pathlib import Path

import numpy as np

EXP = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(20261112)
N_RULES, DRAWS, B = 70, 1000, 2000


def decide(lam: np.ndarray, rng: np.random.Generator) -> str:
    med = np.median(lam)
    boot = np.median(rng.choice(lam, size=(B, lam.size), replace=True), axis=1)
    lo, hi = np.quantile(boot, [0.025, 0.975])
    if lo > 0 and med >= 0.05:
        return "lag"
    if hi < 0:
        return "reversed"
    if lo >= -0.05 and hi <= 0.05:
        return "no lag"
    return "unresolved"


out = []
for sd in (0.025, 0.04):
    for lag in (0.0, 0.05, 0.10, 0.20, -0.10):
        counts: dict[str, int] = {}
        for _ in range(DRAWS):
            lam = np.empty(N_RULES)
            for i in range(N_RULES):
                a1t = rng.uniform(0.84, 0.92)  # shared EF = 1 law (both arms draw R/L with probability 1/2)
                a0r, a0l = a1t - rng.uniform(0.12, 0.30), a1t - rng.uniform(0.12, 0.30)
                dr, dl = a1t - a0r, a1t - a0l
                a1 = a1t + rng.normal(0, sd / np.sqrt(8))
                fr = np.array([rng.uniform(0.3, 0.6), rng.uniform(0.6, 0.9)])
                fl = fr - lag + rng.normal(0, 0.05)
                ar = a0r + fr * dr + rng.normal(0, sd / 2, 2)
                al = a0l + fl * dl + rng.normal(0, sd / 2, 2)
                Fr = (ar - a0r) / (a1 - a0r)
                Fl = (al - a0l) / (a1 - a0l)
                lam[i] = np.mean(Fr - Fl)
            k = decide(lam, rng)
            counts[k] = counts.get(k, 0) + 1
        line = f"sd {sd:.3f} true lag {lag:+.2f}: " + ", ".join(f"{k} {v / DRAWS:.3f}" for k, v in sorted(counts.items()))
        print(line)
        out.append(line)
(EXP / "results/calibration.txt").write_text(
    "# P1 decision-rule calibration, synthetic, seed 20261112, 70 rules, 1000 draws, 2000 bootstrap resamples\n"
    "# both arms share one EF = 1 level per rule (same law); EF = 0 levels differ by arm\n"
    + "\n".join(out) + "\n")
