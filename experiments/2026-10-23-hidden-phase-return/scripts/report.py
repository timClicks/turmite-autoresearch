"""Post-run reporting only: expose signed effects and whole-field edit support."""
import json
from pathlib import Path
import numpy as np
from analyze import load_results

HERE = Path(__file__).resolve().parents[1]
result = json.loads((HERE / "results/analysis.json").read_text())
rows, _, _ = load_results()
lines = ["# Supplementary descriptive results", "",
    "Added after the frozen primary analysis. Equal start weights for effects and outcome rates;",
    "pooled replica medians for fractions of edited cells. No new hypothesis test.", "",
    "| Rule | Area | k=1 signed log2 ratio | Factor-two change | Whole-field edits | Baseline-read edits |",
    "|---|---:|---:|---:|---:|---:|"]
for cell in result["cells"]:
    arm = cell["arms"]["1"]
    data = [r for r in rows if (r["rule"], int(r["band"]), r["k"]) == (cell["rule"], cell["band"], "1")]
    whole = np.median([int(r["changed"]) / int(r["interior"]) for r in data])
    lines.append(f'| {cell["rule"]} | {[4096,16384][cell["band"]]} | {arm["signed"]:.3f} | {arm["factor_two"]:.3f} | {whole:.3f} | {cell["median_read_changed"]:.3f} |')
failed = sum(int(a["sampled"]) < 8 for a in result["audit"])
lines += ["", f"Minimum episode gate failed in {failed}/24 start/area groups.",
    "All 640 k=1 paths and return tuples differ; all 640 k=n shams match.",
    "Whole-field edits count colour labels, not instructions that the trajectory actually reads.",
    "Negative signed effects describe these selected long baselines; they do not estimate the effect on ordinary departures.",
    "", "## Episode support by start", "", "| Rule | Seed | Area | Sampled long episodes |", "|---|---:|---:|---:|"]
for a in result["audit"]:
    lines.append(f'| {a["rule"]} | {a["seed"]} | {[4096,16384][int(a["band"])]} | {a["sampled"]} |')
(HERE / "results/details.md").write_text("\n".join(lines) + "\n")
