"""Calibrate the registered sharpness statistic S on synthetic dose-response curves (no ant data).

usage (repo root): uv run --frozen python experiments/active/2026-10-leak-titration/scripts/calibrate_sharpness.py
Writes results/calibration_sharpness.txt. Seeded (20261028). Pure numpy.

S_r = max over adjacent grid steps of [abar(EF_{i+1}) - abar(EF_i)] / [abar(1) - abar(0)], where abar is the
mean of 8 seed-level early exponents (EF = 0 is the deterministic ant: one run, no seed noise).
The registered statistic is the median of S_r over the 6 rules (one curve per rule, independent noise).
Question: with the observed between-seed sd (0.026 at EF = 1; 0.03 and 0.05 as stress), how often does each
true curve shape give S above the "sharp" cut or below the "smooth" cut? The cuts are chosen from this table
BEFORE the real run and then frozen in the README.
"""
import sys
from pathlib import Path

import numpy as np

EXP = Path(__file__).resolve().parents[1]
GRID = np.round(np.arange(0, 1.0001, 0.1), 2)
DELTA = 0.20          # total rise; Stage 1 saw +0.19..+0.29 per rule
N_SEED = 8
N_SIM = 20000
RNG = np.random.default_rng(20261028)


def logistic(x, c, w):
    f = lambda u: 1 / (1 + np.exp(-(u - c) / w))
    return (f(x) - f(0)) / (f(1) - f(0))


SHAPES = {
    "linear": lambda x: x,
    "logistic c=0.5 w=0.15 (broad)": lambda x: logistic(x, 0.5, 0.15),
    "logistic c=0.5 w=0.05 (sharp)": lambda x: logistic(x, 0.5, 0.05),
    "logistic c=0.3 w=0.05 (sharp, early)": lambda x: logistic(x, 0.3, 0.05),
    "endpoint (all rise in 0.9 -> 1)": lambda x: np.where(x >= 1.0, 1.0, 0.0),
}


def S_stat(abar):
    d = abar[-1] - abar[0]
    return np.max(np.diff(abar)) / d, GRID[np.argmax(np.diff(abar))]


lines = [f"# sharpness calibration; {N_SIM} sims per cell, rise {DELTA}, {N_SEED} seeds per EF > 0, seed 20261028", ""]
SHARP, SMOOTH = 0.40, 0.28   # applied to the MEDIAN of S over the 6 rules
for sd in (0.03, 0.05):
    lines.append(f"## between-seed sd {sd}")
    lines.append(f"{'shape':<40}{'med-of-6 S':>10}{'P(med>=%.2f)' % SHARP:>12}{'P(med<=%.2f)' % SMOOTH:>12}")
    for name, f in SHAPES.items():
        truth = DELTA * f(GRID)
        med = np.empty(N_SIM)
        for i in range(N_SIM):
            S6 = [S_stat(truth + np.concatenate([[0.0], RNG.normal(0, sd / np.sqrt(N_SEED), len(GRID) - 1)]))[0] for _ in range(6)]
            med[i] = np.median(S6)
        lines.append(f"{name:<40}{np.median(med):>9.3f}{np.mean(med >= SHARP):>11.3f}{np.mean(med <= SMOOTH):>11.3f}")
    lines.append("")
out = "\n".join(lines) + "\n"
print(out)
(EXP / "results" / "calibration_sharpness.txt").write_text(out)
