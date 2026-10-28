"""Verify source dumps, figure repeatability and manuscript layout.

uv run --with pypdfium2==5.14.0 scripts/verify_figure.py (use the full repo path).
Only this verification step reads ignored dumps; paper/notebook do not.
"""
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys

import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/archive/2026-10-g1-ribbon-breakout"
PAPER = ROOT / "research-outputs/scholarly-articles/cube-root-growth"
SCRATCH = EXP / "scratch/figure-review"
SCRATCH.mkdir(parents=True, exist_ok=True)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


ext = json.loads((EXP / "results/g1_wake_extract.json").read_text())
for name, digest in ext["inputs_sha256"].items():
    assert sha(EXP / "dumps" / name) == digest, name
compact = sorted((EXP / "results").glob("g1_wake*csv"))
compact += sorted((EXP / "results").glob("g1_sweep_trace*csv"))
before = {p.name: sha(p) for p in compact}
subprocess.run([sys.executable, str(EXP / "scripts/g1_wake_extract.py"), str(EXP / "dumps")], check=True, stdout=subprocess.DEVNULL)
assert before == {p.name: sha(p) for p in compact}
outputs = [PAPER / "fig/late_switch.pdf", PAPER / "fig/late_switch.png"]
before_figure = {p.name: sha(p) for p in outputs}
subprocess.run([sys.executable, str(PAPER / "late_switch_figure.py")], check=True, stdout=subprocess.DEVNULL)
assert before_figure == {p.name: sha(p) for p in outputs}, "Figure output changed on repeat"
doc = pdfium.PdfDocument(str(PAPER / "main.pdf"))
pages = []
for i, page in enumerate(doc):
    text = page.get_textpage().get_text_range()
    if "A late switch to a period-3" in text:
        pages.append(i + 1)
        page.render(scale=1.6).to_pil().save(SCRATCH / f"paper-page-{i+1}.png")
assert pages, "Figure caption missing from compiled manuscript"
summary = dict(raw_hashes_match=True, compact_extracts_repeat=True, figure_bytes_repeat=True,
               compact_sha256=before, figure_sha256=before_figure, manuscript_pages=len(doc),
               figure_caption_pages=pages, rendering_library=f"pypdfium2 {version('pypdfium2')}")
(EXP / "results/figure_verification.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
