# /// script
# dependencies = ["nbformat"]
# ///
"""Builds notebook.ipynb for this experiment. usage: uv run experiments/archive/2026-10-sweeper-generalisation/scripts/build_notebook.py
Execute: uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace \\
    experiments/archive/2026-10-sweeper-generalisation/notebook.ipynb"""
from pathlib import Path

import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# Are the other three "no-highway escapes" sweepers?

## Question
`RLLLLRRL`, `RLLLRLRLLL` and `RLLLLRLRRL` are the only rules of the 1e11 census that "escaped" without a highway. The parent experiment turned the column sweeper
of `RLRLLL` into a checked macro-transition. Do these three run the same kind of sweeper, so that the same checker can be generalised? "Escaped" only means the
ant touched the edge of a 32768 board, and the three final boxes are nearly square, so a board-filling growth is an equally good reading. The registration (README)
therefore treats sweeper, missed highway, filler and inconclusive as competing outcomes.

## Assumptions
Blank board, ant at the centre heading north, plain loop of the other tracers. Exact-clock criterion: `dt = a * swing + b[k mod p]` with zero residual on >= 95% of the
cycles of a window, cycles defined by the front advancing P columns in one of four directions (P <= 8), phase period p <= 6 (registered). Windows: the last 2e8 steps
before the census exit step, and the last 2e8 steps of the run. Instrument accepted only after an oracle (below). Everything here reads committed files in `results/`."""),
code("""import hashlib, subprocess
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
R = ROOT / "experiments/archive/2026-10-sweeper-generalisation/results"
for n in sorted(p.name for p in R.glob("*.txt")):
    print(hashlib.sha256((R / n).read_bytes()).hexdigest()[:16], n)
print("git", subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip())"""),
md("## Instrument oracle\nFingerprint (position, heading, hash of every cell) of the front-log tool equals `fast::run` at 1e7 and 1e8 steps for five rules, and an independent Python ant reproduces all four event logs for 2e5 steps."),
code("""print("\\n".join(l for l in (R / "oracle.txt").read_text().splitlines() if not l.startswith("   Compiling")))"""),
md("## Registered Stage 1 analysis\nPositive control `RLRLLL` should be found; the three targets are the subject. Lines are the best candidate per window, the fraction of cycles with an exactly zero residual, and the new-cell window signature S of the parent (steps per new cell below 8 and box aspect at least 20)."),
code("""print((R / "stage1_analysis.txt").read_text())"""),
md("""## Post hoc: the registered phase-period cap was too small for RLLLLRRL
The registered test fixed p <= 6. For `RLLLLRRL` the residual `dt - 8 swing` is exactly periodic with period 19 once the run is past about 1.47e10 steps."""),
code("""print((R / "stage1_posthoc_rlllrrl.txt").read_text()[-2600:])
print((R / "stage1_posthoc_maxp64.txt").read_text()[:1800])"""),
md("## `RLLLRLRLLL`: onset of the exact clock and board independence (G5)"),
code("""print((R / "stage1_onset.txt").read_text())
print((R / "g5_compare.txt").read_text())"""),
md("## Stage 2 feasibility look (unregistered)\nTrace over five revolutions of the square spiral of `RLLLRLRLLL` at swing about 6055, and the steady-state test of its outer band."),
code("""print((R / "spiral_probe_analysis.txt").read_text()[:2400])
print((R / "spiral_steady.txt").read_text()[:1400])"""),
md("""## What this shows, and what it does not
- Two of the three escapes (`RLLLRLRLLL`, `RLLLLRRL`) become square spirals with exact affine clocks after late onsets (2.635e10 and about 1.47e10 steps); the third is still a blob at 6e10. None is a column sweeper: the parent's window signature S fires in 0% of their windows.
- Registered predictions failed or were only partly right: G1 (p <= 6 cap), G2's onset range, G3, G4 (S does not track the clock); G5 and the positive control held; the registered negative control was vacuous.
- Not shown: that either spiral persists forever. The cell-level test says the outer band is a steady profile (99.2-99.7% of sampled cells equal after five revolutions) but the ant reads 76 cells deep and the path has about eight segment kinds, so the three-stage sweeper checker does not transfer and Stage 2 was not started.
- Next step if pursued: a registered pipeline with a periodic *ahead* background (generalising the rectangle cycler of the highway-decider experiment) and seam blocks."""),
]
nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
out = Path(__file__).resolve().parents[1] / "notebook.ipynb"
nbf.write(nb, out)
print("wrote", out)
