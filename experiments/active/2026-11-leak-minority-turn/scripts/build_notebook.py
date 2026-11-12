"""Write and execute notebook.ipynb (reads committed results/ only).
uv run --frozen python experiments/active/2026-11-leak-minority-turn/scripts/build_notebook.py"""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

EXP = Path(__file__).resolve().parents[1]
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
cells = [
    md("""# Leak minority turn: does composition predict the handedness lag?

## Question and why it matters
On a compact ant, a partial leak of random turns on fresh ground pushes growth from compact towards porous. The leak-handedness
cohort (`experiments/active/2026-11-leak-handedness-cohort/`, 77 rules) found that whether the forced fresh-ground turn is R or L
changes how much leak a rule tolerates, strongly and rule by rule, in both directions. After the fact, the direction seemed to track
composition: the forced turn did better when it was the rule's *minority* letter (Spearman +0.40). This notebook scores that pattern
as a registered prediction on 81 new rules. Registration, gates and predictions: `README.md`; lab record: `NOTEBOOK.md`.

## Assumptions and definitions
* Leak EF: on a never-departed cell the forced base turn is replaced by R or L with probability 1/2 each (20-slot `fs:` set).
  Arm R = base R (the ant's colour-0 turn), arm L = base L.
* Early a: slope of log area on log t over k = 12..22 (probe, board 16384).
* Rise fraction F(EF) = (a(EF) - a(0)) / (a(1) - a(0)) per arm; lag Lambda = mean over EF 0.3, 0.5 of F_R - F_L.
  Positive: base L tolerates the leak better.
* R fraction fr = share of R letters in the rule string."""),
    md("## Provenance\nGit commit, date and SHA-256 of every input. Seeds 2026111301..04 (held-out), 2026111201..04 (anchor)."),
    code("""import hashlib, subprocess, datetime
from pathlib import Path
import numpy as np
import polars as pl

ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
EXP = ROOT / "experiments/active/2026-11-leak-minority-turn"
INPUTS = [EXP / f"results/{n}" for n in ("rules.txt", "specs.txt", "probe.csv", "runs.csv", "rules.csv",
                                         "analysis.txt", "calibration.txt", "posthoc.txt", "provenance.txt")]
sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
print("git", sha, "| run", datetime.date.today().isoformat())
for p in INPUTS:
    print(hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.relative_to(ROOT))"""),
    md("## Calibration (synthetic, before the run)"),
    code("""print((EXP / "results/calibration.txt").read_text())"""),
    md("""If the development slope were real, the registered rule would essentially never say "fails"; under no slope it says
"replicates" about 2-3% of the time.

## Gates and registered scores\nThe frozen scorer's output, unedited."""),
    code("""print((EXP / "results/analysis.txt").read_text())"""),
    md("""Both gates pass. **P1, P2 and P3 all fail.** The held-out correlation is slightly negative and its interval excludes the
development value.

## Composition against lag, held-out rules"""),
    code("""r = pl.read_csv(EXP / "results/rules.csv").filter(pl.col("scoreable")).sort("fr")
for lo, hi in [(0, .4), (.4, .45), (.45, .55), (.55, .6), (.6, .7), (.7, 1.01)]:
    m = r.filter((pl.col("fr") >= lo) & (pl.col("fr") < hi))
    if m.height:
        lam = m["lam"].to_numpy()
        print(f"fr [{lo:.2f}, {min(hi, 1):.2f}): n {m.height:2d}  median Lambda {np.median(lam):+.3f}  " + "".join("+" if v > 0 else "-" for v in lam))"""),
    md("## Post hoc (not registered): the spread itself replicates"),
    code("""print((EXP / "results/posthoc.txt").read_text())"""),
    md("""The lag is as large and as rule-specific as in the development cohort (sd 0.38 against ~0.06 seed noise), so handedness
matters; what failed is the explanation of its sign by letter counts.

## Caveats
* Finite window (k = 12..22), board 16384, 4 seeds per cell, two leak levels.
* Core class only; 26 of 110 drawn rules were ineligible (a forced-L base already escapes, fills or is intermediate).
* "Fails" covers R fraction and the two prefix groups as registered, not every feature of the rule table.

## Next steps
Look for a predictor of the sign in the dynamics rather than the letters (registered on the 77 + 81 rules, scored on a fresh draw),
or permute letters within one rule's table to hold composition fixed."""),
]
nb = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
NotebookClient(nb, timeout=300, kernel_name="python3", resources={"metadata": {"path": str(EXP)}}).execute()
nbformat.write(nb, EXP / "notebook.ipynb")
print("wrote", EXP / "notebook.ipynb")
