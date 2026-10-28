"""Resumable seeded pilot; run under uv in WSL. See registered note.

uv run experiments/archive/2026-10-memory-walkers/scripts/memory_walkers_pilot.py /path/to/release/probe
uv run experiments/archive/2026-10-memory-walkers/scripts/memory_walkers_pilot.py --analyse
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path("experiments/archive/2026-10-memory-walkers/results/memory_walkers_pilot")
FAMILIES = ["cookie:0.25", "cookie:0.75", "rcookie:0.25", "rcookie:0.75",
            "errw:1", "errw:4", "rw", "rotor"]
SPECS = [f"{family}:{seed}" for family in FAMILIES for seed in range(301, 309)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def simulate(binary):
    ROOT.mkdir(exist_ok=True)
    recipe = {"command": f"uv run experiments/archive/2026-10-memory-walkers/scripts/memory_walkers_pilot.py {binary}",
              "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
              "source_hashes": {p: sha(p) for p in ["src/walkers.rs", "src/probe.rs", "src/bin/probe.rs",
                                                    "experiments/archive/2026-10-memory-walkers/scripts/memory_walkers_pilot.py", "Cargo.lock", "uv.lock"]},
              "binary_sha256": sha(binary), "seeds": list(range(301, 309)), "max_log2": 20,
              "grid": 8192, "rayon_threads": 1, "specs": SPECS}
    meta = ROOT / "recipe.json"
    if meta.exists():
        assert json.loads(meta.read_text()) == recipe, "recipe changed; use a new output directory"
    else:
        meta.write_text(json.dumps(recipe, indent=2) + "\n")
    for spec in SPECS:
        stem = ROOT / spec.replace(":", "_")
        marker = Path(str(stem) + ".done")
        path = Path(str(stem) + ".csv")
        if marker.exists():
            assert marker.read_text().strip() == sha(path), f"changed checkpoint {path}"
            continue
        print("running", spec, flush=True)
        with path.open("w") as out, Path(str(stem) + ".log").open("w") as log:
            subprocess.run([binary, "20", "8192"], input=spec + "\n", text=True,
                           stdout=out, stderr=log, env={**os.environ, "RAYON_NUM_THREADS": "1"}, check=True)
        marker.write_text(sha(path) + "\n")
    analyse()


def analyse():
    rows = []
    for spec in SPECS:
        stem = ROOT / spec.replace(":", "_")
        path = Path(str(stem) + ".csv")
        assert Path(str(stem) + ".done").read_text().strip() == sha(path)
        with path.open() as f:
            rows.extend(csv.DictReader(f))
    fields = list(rows[0])
    with (ROOT / "combined.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(rows)
    result = {}
    for family in FAMILIES:
        runs = {spec: [r for r in rows if r["rule"] == spec] for spec in SPECS if spec.rsplit(":", 1)[0] == family}
        summary = {"escaped_seeds": [s for s, rs in runs.items() if not rs or rs[-1]["escaped"] == "true"],
                   "last_complete_k": {s: int(rs[-1]["k"]) if rs else None for s, rs in runs.items()},
                   "windows": {}}
        for lo, hi in [(14, 18), (16, 20)]:
            fits = []
            for spec, rs in runs.items():
                selected = [r for r in rs if lo <= int(r["k"]) <= hi]
                if [int(r["k"]) for r in selected] != list(range(lo, hi + 1)):
                    continue
                t = np.array([float(r["t"]) for r in selected])
                a = np.array([float(r["area"]) for r in selected])
                radius = np.sqrt([float(r["rg2"]) for r in selected])
                last = selected[-1]
                kappa = (float(last["boundary_steps"]) / (float(last["t"]) / 2)) * float(last["area"]) / float(last["perimeter"])
                fits.append({"spec": spec, "area_slope": float(np.polyfit(np.log(t), np.log(a), 1)[0]),
                             "radius_slope": float(np.polyfit(np.log(t), np.log(radius), 1)[0]),
                             "kappa": kappa, "area_end": float(last["area"]),
                             "box_aspect": max(float(last["width"]), float(last["height"])) / min(float(last["width"]), float(last["height"]))})
            stats = {key: {"mean": float(np.mean([r[key] for r in fits])),
                           "seed_sd": float(np.std([r[key] for r in fits], ddof=1)) if len(fits) > 1 else None}
                     for key in ("area_slope", "radius_slope", "kappa", "area_end", "box_aspect")} if fits else {}
            summary["windows"][f"{lo}..{hi}"] = {"n": len(fits), "fits": fits, "stats": stats}
        result[family] = summary
        print(family, "escaped", len(summary["escaped_seeds"]), flush=True)
        for window, s in summary["windows"].items():
            print(" ", window, "n", s["n"], s["stats"], flush=True)
    (ROOT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    if sys.argv[1] == "--analyse":
        analyse()
    else:
        simulate(sys.argv[1])
