"""Rebuild presentation assets only; existing measurements are never rerun.

Run from the repository root: uv run research-outputs/working-papers/cube-root-growth/rebuild_figures.py
Logs and input/source hashes are written beside the figures.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from recent_findings_numbers import FILES as RECENT_INPUTS

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "research-outputs/working-papers/cube-root-growth/fig"
SCRIPTS = ["figures.py", "gallery.py", "textbook_figs.py", "memory_figures.py", "late_switch_figure.py", "prefix_figure.py", "edge_gap_figure.py", "layers_figure.py", "walker_map_figure.py"]
CENSUS_TABLE = "research-outputs/data-papers/rule-census/build_rule_census.py"
INPUTS = [
    "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv", "experiments/archive/2026-10-calib-instrument-calibration/results/calib_rotor.csv", "experiments/archive/2026-10-probe-growth-census/results/cube_stats.json",
    "experiments/archive/2026-10-probe-growth-census/results/c_model.csv", "experiments/archive/2026-10-probe-growth-census/results/probe_all.csv", "experiments/archive/2026-10-calib-instrument-calibration/results/calib_rw.csv",
    "experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv", "experiments/archive/2026-10-census-sweeps/results/census.csv", "experiments/archive/2026-10-memory-walkers/dumps/memory_paths.csv",
    "experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot/combined.csv", "experiments/_lib/analyse_probe.py",
    "research-outputs/working-papers/cube-root-growth/style.py", "research-outputs/working-papers/cube-root-growth/main.typ", "research-outputs/working-papers/cube-root-growth/numbers.json", "research-outputs/working-papers/cube-root-growth/refs.bib",
    "experiments/archive/2026-10-transport-forecast/results/transport_forecast.json",
    "research-outputs/working-papers/cube-root-growth/kappa_prediction.json",
    "research-outputs/working-papers/cube-root-growth/kappa_prediction_numbers.py",
    "research-outputs/working-papers/cube-root-growth/tail_budget.json",
    "research-outputs/working-papers/cube-root-growth/tail_budget_numbers.py",
    "research-outputs/working-papers/cube-root-growth/recent_findings.json",
    "research-outputs/working-papers/cube-root-growth/recent_findings_numbers.py",
    "experiments/archive/2026-10-kappa-tail-budget/results/confirm-v1.analysis.json",
    "experiments/archive/2026-10-kappa-tail-budget/results/confirm-v1.decomposition.json",
    "experiments/archive/2026-10-kappa-rule-space/results/w3c_stats.txt",
    "experiments/archive/2026-10-kappa-rule-space/results/w3c_cross.txt",
    "experiments/archive/2026-10-kappa-rule-space/results/prefix_audit_predictions.csv",
    "experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot/summary.json",
    "experiments/archive/2026-10-arm-kappa-depletion-arms/results/armb_probe.csv",
    "experiments/archive/2026-10-layers-colours/results/layers.csv",
    "experiments/archive/2026-10-layers-colours/results/layers_typical.csv",
    "experiments/archive/2026-10-layers-colours/results/layers_classes.txt",
    "experiments/archive/2026-10-a4-boundary-width/results/a4_shape_ants.csv",
    "experiments/archive/2026-10-a4-boundary-width/results/a4_shape_rotor.csv",
    "experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_ants.csv",
    "experiments/archive/2026-10-a4-boundary-width/results/a4c_shape_rotor.csv",
    CENSUS_TABLE, CENSUS_TABLE.replace("build_rule_census.py", "rule_census.csv"),
] + list(RECENT_INPUTS.values()) + ["research-outputs/working-papers/cube-root-growth/audit.typ", "research-outputs/working-papers/cube-root-growth/supplementary/reproducibility-audit.typ"] + [f"experiments/archive/2026-10-g1-ribbon-breakout/results/{name}" for name in
     ("g1_ribbon.csv", "g1_wake_extract.json", "g1_wake_crop_12800000000.csv", "g1_sweep_trace_12800000000.csv")
] + [f"research-outputs/working-papers/cube-root-growth/{name}" for name in SCRIPTS]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    os.chdir(ROOT)
    subprocess.run([sys.executable, "research-outputs/working-papers/cube-root-growth/kappa_prediction_numbers.py"], check=True)
    subprocess.run([sys.executable, "research-outputs/working-papers/cube-root-growth/tail_budget_numbers.py"], check=True)
    subprocess.run([sys.executable, "research-outputs/working-papers/cube-root-growth/recent_findings_numbers.py", "--check"], check=True)
    # Regenerate the supplementary per-rule table; exits non-zero if it disagrees with numbers.json.
    subprocess.run([sys.executable, CENSUS_TABLE], check=True)
    gal = Path(os.environ.get("GAL", Path.home() / "gal")).resolve()
    snapshots = [gal / f"{r}.bin" for r in
                 ("RL", "RLL", "RLR", "RRLL", "RLLR", "RRLRLLRLRRLR", "RRLRLRLLLLLL")]
    snapshots += [gal / f"RLL_k{k}.bin" for k in (14, 17, 20, 23)]
    paths = [ROOT / p for p in INPUTS] + snapshots
    recipe = {
        "command": "uv run research-outputs/working-papers/cube-root-growth/rebuild_figures.py",
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "working_tree": "Source hashes identify uncommitted edits.",
        "python": sys.version,
        "snapshot_directory": str(gal),
        "seeds": {"rotor_illustration": 1, "memory_paths": 301,
                  "gallery": "deterministic blank board"},
        "sha256": {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): digest(p)
                   for p in paths},
    }
    with (OUT / "rebuild.log").open("w") as log:
        for script in SCRIPTS:
            log.write(f"uv run research-outputs/working-papers/cube-root-growth/{script}\n")
            log.flush()
            subprocess.run([sys.executable, f"research-outputs/working-papers/cube-root-growth/{script}"], check=True,
                           stdout=log, stderr=subprocess.STDOUT)
        command = ["typst", "compile", "--root", ".", "research-outputs/working-papers/cube-root-growth/main.typ", "research-outputs/working-papers/cube-root-growth/main.pdf"]
        log.write(" ".join(command) + "\n")
        log.flush()
        subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
        supplement = "research-outputs/working-papers/cube-root-growth/supplementary/reproducibility-audit"
        command = ["typst", "compile", "--root", ".", supplement + ".typ", supplement + ".pdf"]
        log.write(" ".join(command) + "\n")
        log.flush()
        subprocess.run(command, check=True, stdout=log, stderr=subprocess.STDOUT)
    recipe["outputs_sha256"] = {p.name: digest(p) for p in sorted(OUT.glob("*.pdf"))}
    recipe["outputs_sha256"]["main.pdf"] = digest(ROOT / "research-outputs/working-papers/cube-root-growth/main.pdf")
    recipe["outputs_sha256"]["supplementary/reproducibility-audit.pdf"] = digest(ROOT / "research-outputs/working-papers/cube-root-growth/supplementary/reproducibility-audit.pdf")
    (OUT / "rebuild_recipe.json").write_text(json.dumps(recipe, indent=2) + "\n")


if __name__ == "__main__":
    main()
