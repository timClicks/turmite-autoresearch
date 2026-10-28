"""Random-sample mixing test. Usage (repo root, WSL):
  uv run research-outputs/scholarly-articles/cube-root-growth/mixing_random.py   (needs a built release `dump` example; see notes/mixing-random-sample.md)
"""
import subprocess, sys
from pathlib import Path
import numpy as np, polars as pl

R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / "experiments" / "_lib"))
import mixing  # noqa: E402

s = pl.read_csv(R / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(
    ~pl.col("bursty") & (pl.col("cls") == "blob") & pl.col("alpha_w").is_between(0.30, 0.37)).sort("rule")
rng = np.random.default_rng(20261012)
rules = sorted(rng.choice(s["rule"].to_numpy(), 40, replace=False).tolist())
out = Path.home() / "mixdumps"; out.mkdir(exist_ok=True)
for r in rules:
    if not (out / f"{r}.traj").exists():
        subprocess.run(["cargo", "run", "--release", "--example", "dump", "--", r, "24", str(out)], check=True, cwd=R)
rows = [mixing.analyse(r, out) for r in rules]
pl.DataFrame(rows).write_csv(R / "experiments/archive/2026-10-mixing/results/mixing_random.csv")
(R / "experiments/archive/2026-10-mixing/results/mixing_random_rules.txt").write_text("\n".join(rules) + "\n")
print("done", len(rows))
