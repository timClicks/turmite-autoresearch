# /// script
# dependencies = ["numpy"]
# ///
"""Stage 2 POST HOC (unregistered): split boundary reads per birth into first reads, lag-4 returns (2x2 loops) and other returns,
and regress each on min(lead, 6). usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/stage2_decompose.py"""
import json
from pathlib import Path

import numpy as np

root = Path(__file__).resolve().parents[4]
R = root / "experiments/archive/2026-10-c-law-mechanism/results"
rows = [json.loads(l) for l in (R / "trace_sample.jsonl").read_text().splitlines()]
lines = []


def say(s):
    print(s)
    lines.append(s)


def lead(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


M, F, L4, LO = [], [], [], []
for d in rows:
    B = d["births"]
    S = d["boundary_steps"]
    lag = np.array(d["lag"])
    l4 = lag[:, 4].sum()
    lall = lag.sum()          # lags capped at 40 in the output; the capped tail is in column 40
    M.append(min(lead(d["spec"]), 6))
    L4.append(l4 / B)
    LO.append((lall - l4) / B)
    F.append((S - lall) / B)
M, F, L4, LO = map(np.array, (M, F, L4, LO))
tot = F + L4 + LO
say(f"{len(M)} sample rules (stationary blob), lead capped at 6")
for nm, v in (("first reads", F), ("lag-4 returns", L4), ("other returns", LO), ("total = 1/c", tot)):
    b, a = np.polyfit(M, v, 1)
    say(f"  {nm:14s} per birth = {a:.3f} + {b:.3f} lead   (share of the lead slope: {b / np.polyfit(M, tot, 1)[0]:.2f})")
for m in range(1, 7):
    s = M == m
    say(f"  lead {m} (n={s.sum()}): first {F[s].mean():.3f}  lag4 {L4[s].mean():.3f}  other {LO[s].mean():.3f}  total {tot[s].mean():.3f}")
(R / "stage2_decompose.txt").write_text("\n".join(lines) + "\n")
