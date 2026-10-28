"""Builds notebook.ipynb for this experiment. usage: uv run --frozen experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/build_notebook.py
Execute (reads committed results only), from the experiment folder:
    uv run --frozen python -c "import nbformat; from nbclient import NotebookClient; nb = nbformat.read('notebook.ipynb', 4); \\
    NotebookClient(nb, timeout=120, kernel_name='python3').execute(); nbformat.write(nb, 'notebook.ipynb')"
"""
from pathlib import Path

import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# Is a chaotic edge a broken crawler?

*Kea (AI research agent, Claude), 2026-10-25. This is the shareable write-up of
`experiments/archive/2026-10-crawler-cost-chaotic-edge/`. The README holds both registrations (Stage 1 at `a387d27`, Stage 2
at `be07015`, each committed before its runs), and `NOTEBOOK.md` holds the timeline, including the timestamp corrections.*

## Question
Chaotic generalised Langton's ants obey an empirical edge law. The number of boundary reads per new cell is
`1/c = 1.36 + 0.70 m`, where `m` is the rule's opening same-letter run (the lead). It is calibrated, it transfers to fresh
rules, and it does not depend on the interior's colours, but its coefficients are unexplained. The square-ring board
fillers have an edge that has been *solved*: a periodic crawler made of 2x2 square loops. Does the crawler's exact
accounting say anything about the chaotic edge?

## Idea under test (H-crawl)
The crawler spends exactly `k + 5/4` boundary reads per birth (derived below). Chaotic edges might be fragments of that
crawler, with circulation lost whenever a shared cell of a plaquette reads the wrong letter. That predicts (1) rules
with the crawler's full turn table `Pi(m)` sit near the crawler line, and (2) a letter window `[m+1, 2m+1]` that matters
most and moves outward with `m`.

## Assumptions
Blank board, one ant, turn = `rule[visits mod n]`. The edge tracer (`src/edge_trace.rs`) defines a boundary read as a
step from a visited cell with an unvisited 4-neighbour, and a birth as a step onto a never-visited cell. Census `c`
values come from the committed probe census. This notebook reads committed `results/` only and runs no simulation."""),
code("""import hashlib, json, subprocess
from pathlib import Path
import polars as pl
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
R = ROOT / "experiments/archive/2026-10-crawler-cost-chaotic-edge/results"
for n in sorted(p.name for p in R.iterdir() if p.suffix in (".txt", ".csv", ".log", ".json", ".jsonl")):
    print(hashlib.sha256((R / n).read_bytes()).hexdigest()[:16], n)
print("git", subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip())"""),
md("""## P0: the crawler's edge cost is exact
Each period of the crawler has `8(k+1)` steps and 4 births: a chain of three fresh cells and a chain of one. Every new
cell is read at counts `0..k` while it still touches unvisited ground. It is read at `k+1..2k+1` later, as the shared
cell of the next pass, and by then only one read in four is still on the boundary. So `r_j = 1, ..., 1, 1/4` and
`1/c = k + 5/4`. P0a checks this with exact rationals on a strip; P0b runs the real edge tracer on all 25 census board
fillers."""),
code("""print((R / "p0_strip.txt").read_text())
print("\\n".join((R / "analysis.txt").read_text().split("\\n\\n")[0].splitlines()[-6:]))"""),
md("""## Stage 1: registered results
P1 uses census `c` for the 40 stationary blobs with the crawler's table and `m >= 2`. `phi = 0` means on the lead law,
and `phi = 1` means on the crawler line. P2 flips single letters in 90 parents. P3 traces the P1 cohort and its
composition-matched controls."""),
code("""print("\\n".join((R / "analysis.txt").read_text().split("\\n\\n")[1:]))"""),
md("""![figure](results/fig_crawler_ceiling.png)

*(a) Every point is one rule: census crawler-table blobs (blue circles), composition-matched controls (orange
squares), and kept fresh crawler-table rules from Stage 2 (green triangles). The solid line is the crawler's exact
cost and the dashed line is the chaotic lead law. Crawler-table rules sit between the two, and almost never above
the crawler line. Points are jittered horizontally. (b) Median relative change in `1/c` when one letter at relative
position `q = p - m` is flipped. Near letters matter most for every lead, but the effect does not stretch over the
registered windows (bars below zero) as `m` grows.*"""),
md("""## A post hoc check: does the fitted K3 kernel already know this?
This check was written after reading Stage 1 and was not registered. K3, a three-parameter survival kernel fitted
earlier on the census, predicts the crawler-table rules' census `c` with a median residual of +0.03. At m = 2-3 the
crawler limit is therefore not new predictive information. The high-lead pattern motivated Stage 2."""),
code("""print((R / "posthoc_k3.txt").read_text())"""),
md("""## Stage 2: does full support push the lead slope toward 1?
Registered before its run: fresh crawler-table rules of lengths 13-18 (never in the census), each with a
composition-matched control."""),
code("""print((R / "stage2_analysis.txt").read_text())
s2 = pl.read_csv(R / "stage2_rules.csv")
print(s2.group_by("m").agg(pl.len().alias("rules"), (pl.col("status") == "kept").sum().alias("kept"),
                           (pl.col("status") == "ratio>1.9").sum().alias("filler_like")).sort("m"))"""),
md("""## What this shows, and what it does not
- **Shows.** The crawler's cost `k + 5/4` is an exact calibration point for the edge-cost instruments, and it is
  reproduced to 0.1%. The crawler line works as a ceiling: 6 of 129 crawler-table chaotic rules exceed it by more than
  0.1. Those rules recover about half to two-thirds of the gap between the lead law and the crawler, while
  composition-matched controls recover about 15% (census).
- **Does not show.** A positional mechanism. There is no letter window that moves with `m`, and a single added `s_0`
  letter in the window more often *lowers* the cost. Nor does it show a steeper lead slope specific to support: fresh
  R-rich controls climb almost as fast. At `m <= 4` the earlier K3 kernel predicts these rules as well as the crawler
  picture does.

## Caveats
One blank start per rule; tracer horizon 2^24 steps on a 4096 board. Two thirds of fresh crawler-table rules became
filler-like within that horizon and were filtered out, so the kept rules are selected. Three census rules were seen
in exploration before registration (results unchanged without them). The K3 comparison is post hoc. The README header
timestamps ran ahead of the clock; git commit times govern (see `NOTEBOOK.md`).

## Next
Why is support collective? If circulation is an all-or-nothing chain, `phi` should follow the *product* of the window
letters. The proposed test is a gap-dose design (0, 1 or 2 gaps in an otherwise complete window) on the flat band. Not
yet registered."""),
]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
nbf.write(nb, Path(__file__).resolve().parents[1] / "notebook.ipynb")
