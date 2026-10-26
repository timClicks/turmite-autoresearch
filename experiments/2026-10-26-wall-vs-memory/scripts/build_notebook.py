"""Builds notebook.ipynb for this experiment. usage: uv run --frozen experiments/2026-10-26-wall-vs-memory/scripts/build_notebook.py
Execute (reads committed results only), from the experiment folder:
    uv run --frozen python -c "import nbformat; from nbclient import NotebookClient; nb = nbformat.read('notebook.ipynb', 4); \\
    NotebookClient(nb, timeout=120, kernel_name='python3').execute(); nbformat.write(nb, 'notebook.ipynb')"
"""
from pathlib import Path

import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# Wall or memory: where does the ant's cube root live?

*Claude (AI research agent), 2026-10-26. Shareable write-up of `experiments/2026-10-26-wall-vs-memory/`. The README holds the
registration (committed at `086c1ac` before any code or run) and the lab notebook holds the timeline.*

## Question
Chaotic generalised Langton's ants grow compact territories whose area goes as t^(2/3). The project's original mechanism has
two ingredients: **blank cells repel** (every canonical rule turns R on colour 0, so an ant stepping onto fresh ground curls
back) and **the interior is well mixed**. The ant also has a third property the mechanism did not use: its colour field is a
deterministic memory of past visits, like a rotor router. A memoryless walker with the ant's turn statistics grows as t^0.93
with a porous territory; the rotor and the ant reach 2/3. Which ingredient does the work?

## Design
The walker `hy:RULE:EV:EF:SEED` is the ant with turn noise split by cell type: on a cell the walker stands on for the first
time (fresh) its turn is replaced by a fair R/L coin with probability EF, elsewhere with probability EV. The colour advances
as usual. The four corners:

| | EF = 0 (wall kept) | EF = 1 (wall removed) |
|---|---|---|
| EV = 0 (memory kept) | the ant | **F1**: memory, no wall |
| EV = 1 (memory removed) | **V1**: the hybrid wall walker | memoryless walker `pw:0.5` (exactly) |

Two explanations were registered. H-wall: the reflecting fresh ground plus any diffusive interior gives the cube root (V1
compact, F1 porous). H-memory: the deterministic memory balances local times, so the wall is incidental (V1 porous, F1
compact). **My registered prior was H-memory, about 70%.**

## Assumptions and instrument
Blank board, 16384 cells square, start at the centre heading north. `bin/probe` octave windows; a = slope of ln area against
ln t, beta = slope of ln perimeter against ln area, fitted per run over k = 12..22 (early) and k = 20..26 (late), then
averaged. Classes as registered: compact if early a <= 0.78, beta <= 0.65 (and late a <= 0.74 when available); porous if
early a >= 0.85, beta >= 0.80. Six rules drawn at random (seed 20261026) from the census core class, 8 seeds per noisy
condition. The walker is checked against an independent sparse reference and three exact identities
(`tests/hybrid_walker.rs`). Everything below reads committed `results/` only; nothing is simulated here."""),
code("""import hashlib, subprocess
from pathlib import Path
import polars as pl
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
R = ROOT / "experiments/2026-10-26-wall-vs-memory/results"
for n in sorted(p.name for p in R.iterdir() if p.suffix in (".txt", ".csv")):
    print(hashlib.sha256((R / n).read_bytes()).hexdigest()[:16], n)
print("git", subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
print((R / "provenance.txt").read_text())"""),
md("""## Calibration gates (Stage 1)
G1: the rotor reproduces its earlier exponents. G2: the EV = EF = 1 corner reproduces the memoryless walker. G3: every
noise-free run reproduces its census row exactly."""),
code("""txt = (R / "analysis.txt").read_text().splitlines()
print("\\n".join(l for l in txt if l.startswith(("G1", "G2", "G3", "gates"))))"""),
md("""## The four corners
Condition means over runs. `esc` counts runs that later reached the board edge; the early window is complete for every run."""),
code("""c = pl.read_csv(R / "conditions.csv")
corner = pl.when((pl.col("ev") == 0) & (pl.col("ef") == 0)).then(pl.lit("ant")) \\
    .when((pl.col("ev") == 0) & (pl.col("ef") == 1)).then(pl.lit("F1: memory, no wall")) \\
    .when((pl.col("ev") == 1) & (pl.col("ef") == 0)).then(pl.lit("V1: wall, no memory")) \\
    .when((pl.col("ev") == 1) & (pl.col("ef") == 1)).then(pl.lit("pw:0.5")).otherwise(None)
pl.Config.set_tbl_rows(40); pl.Config.set_tbl_cols(12); pl.Config.set_float_precision(3); pl.Config.set_tbl_width_chars(160)
print(c.with_columns(corner=corner).filter(pl.col("corner").is_not_null())
       .select("corner", "group", "runs", "escaped", "early_a", "early_beta", "late_a", "late_beta", "class")
       .sort("corner", "group"))
print("\\n".join(l for l in txt if l.startswith(("V1", "F1", "corner"))))"""),
md("""**What this shows.** Removing the wall while keeping the memory makes every one of the six ants porous, close to the
memoryless walker: the forced turn on fresh ground is *necessary* here, and my prior was wrong. Keeping the wall with a
memoryless interior lands between the memoryless walker and the ant, an "intermediate" class, so no registered corner
reading applies to the pair.

## Dose arms: low-rate noise on one cell type
Shifts of the early area exponent above each rule's noise-free run, at 10% noise on revisited cells (Delta_V) or fresh cells
(Delta_F), and 1% on revisited cells. Both registered dose predictions (one per explanation) failed."""),
code("""print("\\n".join(l for l in txt if "|" in l and l.count("|") == 4 or l.startswith(("dose", "(0.1,0.1)"))))"""),
md("""## Stage 2: does the wall alone reach the cube root?
Registered after Stage 1 (and informed by it): V1 for 16 seeds and the rotor for 8, to 2^31 steps; fit k = 24..30, and the
trend of the local exponent over k = 22..31 with a seed bootstrap."""),
code("""print((R / "stage2_analysis.txt").read_text())"""),
md("""The frozen rule reads "separate exponent", but by 0.002 against a between-seed sd of 0.021, and the trend interval
includes both a flat line and a slow decline. I read Stage 2 as **unresolved**: at 2^31 steps the hybrid sits about 0.05 above
the rotor, with no resolved trend.

![local exponents](results/fig_local_exponents.png)

*Local area exponent per octave (mean, standard error). Late points for F1 and pw:0.5 come from fewer runs, since porous runs
escape the board; the early window used for scoring is complete for all of them. Regenerate with `scripts/figure.py`.*

## Caveats
- Six rules from one class (blob, width exponent 0.30-0.37, not bursty); not the census.
- Finite windows: the early window ends at 2^23 steps, Stage 2 at 2^31. D3 showed exponent crossovers can be slow.
- "Wall" means exactly the ant's fresh-cell turn (R for canonical rules). Other ways of weakening it (partial bias, forced L,
  intermediate rates between 0.1 and 1) were not run.
- The hybrid is not the ant: its interior is memoryless. That the wall is necessary for the ant does not mean the ant's
  mechanism is the hybrid's.
- Timestamps in the README written by hand at registration were estimates; git commit times are authoritative (README
  correction, 23:15 NZDT). The order registration -> code -> run holds.

## Next steps (none registered)
- Q30: a dose curve in EF between 0.1 and 1, to find where the reflecting edge fails and whether the loss is sharp.
- Q31: what memory adds on top of the wall. Compare neighbour discrepancies of visit counts (local times) in the ant, the
  rotor and the hybrid.
- Whether V1 converges to 2/3 needs a longer horizon or an argument, not more seeds at 2^31."""),
]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
nbf.write(nb, Path(__file__).resolve().parents[1] / "notebook.ipynb")
print("wrote notebook.ipynb")
