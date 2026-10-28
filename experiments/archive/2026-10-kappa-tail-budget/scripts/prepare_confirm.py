"""Freeze (NOT run) the confirmation manifest confirm-v1. Writes only results/confirm-v1.manifest.json.
Launch (later, by a session that has the user's go-ahead): uv run scripts/run.py --name confirm-v1
Seeds 2026101801..32 verified absent from every other manifest/note on 2026-10-16.
"""
from pathlib import Path
import hashlib, json, subprocess
from datetime import datetime, timezone
import pilot
EXP = Path(__file__).resolve().parents[1]; ROOT = Path(__file__).resolve().parents[4]
base = json.loads((EXP / "results/pilot-v2.manifest.json").read_text())
cfg = json.loads(json.dumps(base["config"]))
seeds = list(range(2026101801, 2026101833))
keys = [k for k in cfg["sources"] if not k.endswith("prepare_pilot.py")] + [str(Path(__file__).relative_to(ROOT))]
cfg.update(strata={}, seeds=seeds, cap=2 ** 32, threads=2, bands=[[32768, 34816], [131072, 139264], [524288, 557056]],
           sources={k: hashlib.sha256((ROOT / k).read_bytes()).hexdigest() for k in keys},
           scope="CONFIRMATION (T1/T2) - registered in README 2026-10-16; this manifest only freezes inputs",
           pilot_excluded_from_confirmation=True,
           roles={"predictor": seeds[0::2], "outcome": seeds[1::2]},
           estimator="empirical binned E[T] from entry-conditioned log2 bin time sums (family F not frozen; sensitivity only)",
           decision="confirmation inputs frozen after gates G1-G4; see README registration",
           checkpoint="per completed trajectory (atomic .done); no mid-trajectory checkpoint (deviation, README)")
cfg["gates"] = dict(cfg["gates"], budget="max final step <= cap/4 = 2^30", rules_with_12_seeds_per_role_per_band=0.8)
cfg.pop("profile_cost_seconds", None)
h = hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()
m = dict(config=cfg, config_hash=h, git_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
         recorded_utc=datetime.now(timezone.utc).isoformat(),
         commands=dict(prepare="uv run experiments/archive/2026-10-kappa-tail-budget/scripts/prepare_confirm.py",
                       run="uv run experiments/archive/2026-10-kappa-tail-budget/scripts/run.py --name confirm-v1"), environment=base["environment"])
pilot.write_new(EXP / "results/confirm-v1.manifest.json", m)
print("frozen", len(cfg["rules"]), "rules x", len(seeds), "seeds; cap", cfg["cap"], h)
