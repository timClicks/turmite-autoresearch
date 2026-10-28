"""Register the gate-resolution batches (2026-10-16): fresh reserve validation and
the resume/thread-determinism cohort. Feasibility/cost only; no outcome model.
Seeds 2026101701..12 (reserve) and 2026101721..24 (resume) are excluded from confirmation.
Rule selection uses only pilot-v2 final steps (cost), never B/I/B-over-S.
Usage: uv run scripts/prepare_gates.py   (writes manifests; refuses to replace)
"""
from pathlib import Path
import hashlib, json, subprocess
from datetime import datetime, timezone
import numpy as np
import pilot
EXP = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
base = json.loads((EXP / "results/pilot-v2.manifest.json").read_text())
audit = json.loads((EXP / "results/pilot-v2.audit.json").read_text())
by = {}
for r in audit["batches"]["ants"]["runs"]:
    by.setdefault(r["spec"].split("@")[0], []).append(int(r["status"]["t_final"]))
slow = sorted(by, key=lambda r: (-np.mean(by[r]), r))[:4]
spread = sorted(by, key=lambda r: (-np.std(np.log(by[r]), ddof=1), r))
spread = [r for r in spread if r not in slow][:4]
cohort = base["config"]["rules"]
def sources(extra):
    keys = dict(base["config"]["sources"])
    keys.pop("experiments/archive/2026-10-kappa-tail-budget/scripts/prepare_pilot.py", None)
    keys[str(Path(__file__).relative_to(ROOT))] = None
    return {s: hashlib.sha256((ROOT / s).read_bytes()).hexdigest() for s in keys}
def make(name, rules, seeds, cap, bands, threads, note):
    cfg = json.loads(json.dumps(base["config"]))
    cfg.update(rules=rules, strata={}, seeds=seeds, cap=cap, bands=bands, threads=threads,
               decision=note, sources=sources(None), pilot_excluded_from_confirmation=True,
               scope="gate-resolution feasibility only (cost/steps/determinism); no association or model fit",
               checkpoint="per completed trajectory only (atomic .done); see NOTEBOOK 2026-10-16 deviation")
    cfg.pop("profile_cost_seconds", None)
    cfg["gates"] = dict(cfg["gates"], budget="max final step <= cap/4")
    h = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
    m = dict(config=cfg, config_hash=h, git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
             recorded_utc=datetime.now(timezone.utc).isoformat(),
             commands=dict(prepare="uv run experiments/archive/2026-10-kappa-tail-budget/scripts/prepare_gates.py",
                           run=f"uv run experiments/archive/2026-10-kappa-tail-budget/scripts/run.py --name {name}"),
             environment=base["environment"])
    pilot.write_new(EXP / "results" / f"{name}.manifest.json", m)
    print(name, len(rules), "rules", len(seeds), "seeds", h[:12])
b3 = [[32768, 34816], [131072, 139264], [524288, 557056]]
b2 = b3[:2]
make("reserve-v1", slow + spread, list(range(2026101701, 2026101713)), 2 ** 33, b3, 2,
     "Fresh reserve-validation batch: 4 slowest + 4 highest-spread pilot rules; cap 2^33 so reserve gate is 2^31")
res_rules = cohort[::5][:8]
for name, th in (("resume-t1", 1), ("resume-t2", 2), ("resume-k2", 2)):
    make(name, res_rules, list(range(2026101721, 2026101725)), 2 ** 30, b2, th,
         "Resume/thread determinism cohort (uninterrupted 1-thread, 2-thread, 2-thread killed then resumed)")
