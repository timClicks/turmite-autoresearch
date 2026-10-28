"""Repeat analysis byte-for-byte and render changed paper pages.

uv run --with pymupdf experiments/archive/2026-10-chirality-baselines/scripts/verify_artifacts.py
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import fitz

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
RESULTS = HERE / "results"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


paths = [RESULTS / name for name in ["comparison.json", "groups.json", "groups.csv", "held_out_predictions.csv"]]
before = {p.name: sha(p) for p in paths}
with (RESULTS / "repeat-analysis.log").open("w") as log:
    subprocess.run([sys.executable, str(HERE / "scripts/compare.py")], cwd=ROOT, stdout=log, check=True)
after = {p.name: sha(p) for p in paths}
assert before == after, "Repeated analysis changed bytes"
with (RESULTS / "controls.log").open("w") as log:
    subprocess.run([sys.executable, str(HERE / "scripts/check_controls.py")], cwd=ROOT,
                   stdout=log, stderr=subprocess.STDOUT, check=True)
notebook = json.loads((HERE / "notebook.ipynb").read_text())
cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
assert all(c["execution_count"] is not None for c in cells)
assert not any(o["output_type"] == "error" for c in cells for o in c["outputs"])
paper = ROOT / "research-outputs/scholarly-articles/cube-root-growth/main.pdf"
doc = fitz.open(paper)
pages = {0, 1}
for i, page in enumerate(doc):
    if any(s in page.get_text() for s in ["Comparison with letter-group baselines", "Three-letter group mean", "76.7%", "essentially no additional residual"]):
        pages.add(i)
        if i + 1 < len(doc):
            pages.add(i + 1)
scratch = HERE / "scratch"
scratch.mkdir(exist_ok=True)
for i in sorted(pages):
    doc[i].get_pixmap(matrix=fitz.Matrix(1.2, 1.2)).save(scratch / f"paper-page-{i+1:02d}.png")
release_log = (RESULTS / "release-tests.log").read_text()
assert "test result: FAILED" not in release_log
assert "Doc-tests" in release_log and "test result: ok" in release_log
verification = {"analysis_repeated_identical": True, "result_sha256": after,
                "synthetic_controls": "3 passed", "notebook_code_cells_executed": len(cells),
                "cargo_release_tests": "passed; see release-tests.log", "pdf_pages": len(doc),
                "rendered_pages": [i + 1 for i in sorted(pages)], "pdf_sha256": sha(paper),
                "command": "uv run --with pymupdf experiments/archive/2026-10-chirality-baselines/scripts/verify_artifacts.py"}
(RESULTS / "verification.json").write_text(json.dumps(verification, indent=2) + "\n")
print(json.dumps(verification, indent=2))
