"""Extract published numbers from the kappa tail-budget confirm-v1 result files; no simulations or refits.

uv run research-outputs/working-papers/cube-root-growth/tail_budget_numbers.py
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
E = ROOT / "experiments/archive/2026-10-kappa-tail-budget/results"
a = json.loads((E / "confirm-v1.analysis.json").read_text())
d = json.loads((E / "confirm-v1.decomposition.json").read_text())
files = [E / "confirm-v1.analysis.json", E / "confirm-v1.decomposition.json", Path(__file__)]
result = dict(
    n_rules=a["gate"]["0"]["n_rules"],
    t1_band0=a["T1"]["0"], t1_band1=a["T1"]["1"], t1_pass=a["T1_pass"],
    t1_q999_band0=a["T1_q999"]["0"], t1_q999_band1=a["T1_q999"]["1"],
    t2=a["T2"], t2_pass=a["T2_pass"],
    decomp_tail_share=d["64"]["median_tail_share_p_plus_tm"],
    decomp_corr=d["64"]["corr_model_obs_delta"],
    provenance=dict(command="uv run research-outputs/working-papers/cube-root-growth/tail_budget_numbers.py",
                    commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                    input_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))
(OUT / "tail_budget.json").write_text(json.dumps(result, indent=2) + "\n")
