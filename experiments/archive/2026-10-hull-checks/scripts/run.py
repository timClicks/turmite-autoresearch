"""Resumable per-spec profile acquisition. Default is the registered full run."""
import argparse
import json
import os
import subprocess
from pathlib import Path

from checks import ROOT, EXP, digest

p = argparse.ArgumentParser()
p.add_argument("--pilot", action="store_true")
args = p.parse_args()
out = EXP / "results" / ("pilot" if args.pilot else "full")
out.mkdir(parents=True, exist_ok=True)
legacy = ["RLR", "RLRLRRRLLR", "RLLLRLLRRLR", "RLRLLRRLL", "RLRLRRRRLR", "RLLRLLRLRRRL"]
pool = ROOT / "experiments/archive/2026-10-census-sweeps/results/unresolved_le10.txt"
import hashlib
sampled = sorted(set(pool.read_text().split()) - set(legacy),
                 key=lambda r: (hashlib.sha256(f"20261015:{r}".encode()).hexdigest(), r))[:12]
rules = legacy[:2] if args.pilot else legacy + sampled
seeds = range(331, 333 if args.pilot else 335)
specs = [f"{r}@{s}" for r in rules for s in seeds]
specs += [f"rotor:{s}" for s in range(331, 333 if args.pilot else 343)]
target = Path(os.environ.get("CARGO_TARGET_DIR", ROOT / "target")).expanduser()
binary = target / "release/examples/hull_checks"
if not binary.exists():
    raise SystemExit("Build first: cargo build --release --example hull_checks")
sources = [ROOT / "examples/hull_checks.rs", ROOT / "Cargo.lock", ROOT / "Cargo.toml", pool, Path(__file__)]
sources += sorted((ROOT / "src").rglob("*.rs"))
manifest = {"commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "dirty_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
            "sources": {str(f.relative_to(ROOT)): digest(f) for f in sources},
            "binary_sha256": digest(binary), "selection_seed": 20261015,
            "legacy": legacy, "sampled": sampled, "specs": specs,
            "commands": {}, "profile_bins": 512}
for spec in specs:
    maximum = 20 if args.pilot else (32 if spec.startswith("rotor:") else 30)
    manifest["commands"][spec] = [str(binary), str(maximum), "1024" if args.pilot else "8192", "16" if args.pilot else "24"]
mf = out / "manifest.json"
if mf.exists():
    old = json.loads(mf.read_text())
    # Dirty status changes when this job writes its own outputs.
    if {k: v for k, v in old.items() if k != "dirty_status"} != {k: v for k, v in manifest.items() if k != "dirty_status"}:
        raise SystemExit("Resume refused: recipe/source/binary changed; preserve results and choose a fresh run directory.")
else:
    mf.write_text(json.dumps(manifest, indent=2) + "\n")
for spec in specs:
    stem = spec.replace(":", "_").replace("@", "_")
    csv = out / f"{stem}.csv"
    done = out / f"{stem}.done"
    if done.exists():
        if not csv.exists() or done.read_text().strip() != digest(csv):
            raise SystemExit(f"Corrupt completed output: {csv}")
        print(f"skip {spec}", flush=True)
        continue
    partial = out / f"{stem}.partial"
    with partial.open("w") as f, (out / f"{stem}.log").open("w") as log:
        subprocess.run(manifest["commands"][spec], cwd=ROOT, input=spec + "\n", text=True, stdout=f, stderr=log, check=True)
    partial.replace(csv)
    done.write_text(digest(csv) + "\n")
    print(f"finished {spec}", flush=True)
