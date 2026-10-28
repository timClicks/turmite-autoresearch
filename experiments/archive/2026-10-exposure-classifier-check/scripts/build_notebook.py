"""Build and execute notebook.ipynb for 2026-10-exposure-classifier-check from committed results.
Run (repo root): uv run experiments/archive/2026-10-exposure-classifier-check/scripts/build_notebook.py
The notebook does not rerun z3 (7 minutes); it re-hashes inputs, re-reads results/check.txt and does a
fast pure-Python re-check of the truth table against the spec.
"""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

EXP = Path(__file__).resolve().parents[1]
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
cells = [
    md("""# Is the exposure classifier of `kappa_exposure_classes.rs` what its docs say?

**Question.** The 2026-10-20 experiment classified boundary cells by exposure u (unvisited 4-neighbours; "flat" u = 1,
"corners, bays, tips" u >= 2). Does the instrument compute exactly that, consistently with `src/probe.rs`?
Links: `README.md` (registered P1-P7, N1-N5, results), `NOTEBOOK.md`, `scripts/check_classifier.py` (z3 checker),
`../2026-10-kappa-exposure-classes/`, `notes/proof-track-2026-10-20.md`.

**Assumptions.** The spec is taken from the docs, not the code. The harness runs a verbatim copy of the instrument's
`Region`/`run` (asserted at run time). Deterministic: no random seeds except the harness's fixed splitmix walk seeds."""),
    md("## Provenance"),
    code("""import csv, hashlib, subprocess
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
EXP = ROOT / "experiments/archive/2026-10-exposure-classifier-check"
print("commit", subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
for p in ["results/table.csv", "results/walks.csv", "results/paths.csv", "results/dump.log", "results/check.txt", "scripts/check_classifier.py"]:
    print(p, hashlib.sha256((EXP / p).read_bytes()).hexdigest())
print((EXP / "results/dump.log").read_text())"""),
    md("## Checker verdicts (from `results/check.txt`)"),
    code("""lines = (EXP / "results/check.txt").read_text().splitlines()
verdicts = [l for l in lines if l.startswith(("ok", "FAIL"))]
print(len(verdicts), "checks;", sum(l.startswith("ok") for l in verdicts), "as expected")
for l in verdicts:
    if " N" in l[:8] or l[5:8] in ("P5 ", "P7 ", "P4b"):
        print(l)
assert lines[-1].strip() == "65/65 checks as expected" """),
    md("## Fast re-check of the truth table (pure Python, independent of z3)"),
    code("""CELLS = [(w % 3 - 1, w // 3 - 1) for w in range(9)]
NBR = [(0, -1), (1, 0), (0, 1), (-1, 0)]
rows = list(csv.DictReader((EXP / "results/table.csv").open()))
bad = 0
for r in rows:
    m = int(r["mask"]); V = {c for w, c in enumerate(CELLS) if m >> w & 1}
    for w, (x, y) in enumerate(CELLS):
        exp = sum((x + dx, y + dy) not in V for dx, dy in NBR) if (x, y) in V else 255
        bad += int(r[f"u{w}"]) != exp
print("table entries disagreeing with spec:", bad, "of", 512 * 9)
dist = {}
for r in rows:
    if r["u4"] != "255": dist[int(r["u4"])] = dist.get(int(r["u4"]), 0) + 1
print("centre class over visited-centre patterns:", dict(sorted(dist.items())))"""),
    md("""## Conclusion

P1-P7 held, N1-N6 were rejected (README Results). The 2026-10-20 P3/P4 verdicts stand; the class labels are exposure
counts, not shapes: u = 2 includes one-cell strips, u = 1 includes T-junction cells, and u = 4 never occurs after the
first step. **Next:** none required for this instrument; a shape-resolved split of u = 2 (corner vs strip) would be a
new registered measurement."""),
]
nb = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(EXP)}}).execute()
nbformat.write(nb, EXP / "notebook.ipynb")
print("wrote", EXP / "notebook.ipynb")
