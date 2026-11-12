"""Write and execute notebook.ipynb (reads committed results/ only).
uv run --frozen python experiments/active/2026-11-leak-handedness-cohort/scripts/build_notebook.py"""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

EXP = Path(__file__).resolve().parents[1]
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
cells = [
    md("""# Leak handedness on a cohort

## Question and why it matters
The compact ant keeps its territory compact when the turn on fresh ground is bounded (forced R, forced L, reversal) and goes
porous when that turn is random R/L (`experiments/active/2026-10-wall-vs-memory/`). The leak titration
(`experiments/active/2026-10-leak-titration/`) raised the random share EF gradually and, on three rules, found that a forced-L
base seemed to need more leak than forced R before compactness was lost. If that holds, the bound on fresh runs is not the whole
story: the two arms have the same fresh-run law at every EF. This notebook scores that lead on 77 + 9 rules (Q42).
Registration, gates and predictions: `README.md`; lab record: `NOTEBOOK.md`.

## Assumptions and definitions
* Leak EF: on a never-departed cell the forced base turn is replaced by R or L with probability 1/2 each, so the minority turn
  has probability EF/2 (20-slot `fs:` set). Arm R = base R (the ant's own colour-0 turn), arm L = base L.
* Early a: slope of log area on log t over windows k = 12..22 (probe, board 16384); classes as in wall-vs-memory.
* Rise fraction F(EF) = (a(EF) - a(0)) / (a(1) - a(0)) per arm, with a shared EF = 1 level (same law in both arms; gate G2).
* Lag Lambda = mean over EF 0.3, 0.5 of F_R - F_L. Positive: arm L has risen less (tolerates the leak better)."""),
    md("## Provenance\nGit commit, date and SHA-256 of every input. Seeds 2026111201..04 (in the specs)."),
    code("""import hashlib, subprocess, datetime
from pathlib import Path
import numpy as np
import polars as pl

ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
EXP = ROOT / "experiments/active/2026-11-leak-handedness-cohort"
INPUTS = [EXP / f"results/{n}" for n in ("specs.txt", "cohorts.csv", "probe.csv", "runs.csv", "rules.csv",
                                         "analysis.txt", "calibration.txt", "posthoc.txt", "provenance.txt")]
sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
print("git", sha, "| run", datetime.date.today().isoformat())
for p in INPUTS:
    print(hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.relative_to(ROOT))"""),
    md("## Gates and registered scores\nThe frozen scorer's output, unedited."),
    code("""print((EXP / "results/analysis.txt").read_text())"""),
    md("""Both gates pass: the EF = 0 rows replicate Stage 3b byte for byte, and the two arms agree at EF = 1 (same law).
**P1 is unresolved** and **P2 failed** (3 of the 9 forced-L escaping rules collapse at a 10% leak, not most of them).

## Why P1 is unresolved: the per-rule lags are large and of both signs"""),
    code("""r = pl.read_csv(EXP / "results/rules.csv").sort("lam")
lam = r["lam"].to_numpy()
print(f"Lambda across 77 rules: sd {lam.std(ddof=1):.3f}, quartiles {np.quantile(lam, .25):+.3f} / {np.quantile(lam, .75):+.3f}")
hist, edges = np.histogram(lam, bins=np.arange(-0.9, 1.0, 0.1))
for h, e in zip(hist, edges):
    print(f"{e:+.1f} .. {e + 0.1:+.1f} | " + "#" * h)
print((EXP / "results/calibration.txt").read_text())"""),
    md("""Seed noise on one rule's Lambda is about 0.05 (see the post hoc file below), so a spread of 0.38 is real rule-to-rule
variation. The calibration assumed one shared lag (spread 0.05) and therefore expected a narrow interval; that assumption
was wrong, and a cohort median cannot see a lag whose sign depends on the rule. This does not show that handedness is
irrelevant; it shows the opposite for most rules, with the sign varying.

## Post hoc (not registered): the sign tracks rule composition"""),
    code("""print((EXP / "results/posthoc.txt").read_text())
r2 = r.with_columns(fracR=pl.col("rule").map_elements(lambda s: s.count("R") / len(s), return_dtype=pl.Float64))
with pl.Config(tbl_rows=12):
    print(r2.select("rule", "fracR", "lam").head(6))
    print(r2.select("rule", "fracR", "lam").tail(6))"""),
    md("""Read literally: the leak does less damage when the forced fresh-ground turn is the rule's minority turn. This was found by
looking at the data after the registered test failed to resolve, composition and prefix are confounded, and it rests on one
cohort. It is a hypothesis for a new registration with a per-rule sign prediction on new rules, not a result.

## Caveats
* Finite window (k = 12..22) on a 16384 board, 4 seeds per cell, two EF points per arm (no EF_50 curve).
* Cohort: Stage 3b's core-class sample; 14 rules excluded because a base was intermediate.
* Escapes at EF = 1 (62 of 616 runs) have no early fit; every rule kept at least 3 of 4 fits where required.

## Next steps
Register a test of "minority forced turn tolerates more leak" with the sign fixed per rule from its table, on rules outside this
cohort, scored by per-rule sign agreement. Q41 (fresh-run lengths in the ant) stays relevant: the run-length law is the same for
both arms, so any lag points beyond the bound."""),
]
nb = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
NotebookClient(nb, timeout=300, kernel_name="python3", resources={"metadata": {"path": str(EXP)}}).execute()
nbformat.write(nb, EXP / "notebook.ipynb")
print("wrote", EXP / "notebook.ipynb")
