"""One-thread replay of seed 1001 for every production rule, both widths.

This is a 44/2816-spec check per batch, not an all-seed replay of P3.
"""
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def main():
    cfg = json.loads((EXP / "config.frozen.json").read_text())
    rules = (EXP / cfg["cohort_file"]).read_text().split()
    binary = Path(os.environ.get("CARGO_TARGET_DIR", str(Path.home() / "turmite-target"))) / "release/examples/fixed_area_cycles_sampler"
    specs = "".join(f"{r}@1001\n" for r in rules)
    report = {"command": "uv run experiments/archive/2026-10-fixed-area-cycles/scripts/check_determinism.py",
              "seed": 1001, "rules": len(rules), "production_threads": 5, "replay_threads": 1,
              "scope": "all rules, one of 64 production seeds, both widths; full P3 determinism not established",
              "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "runs": {}}
    for run, bands in [("prod16", cfg["primary_bands"]), ("prod8", cfg["sensitivity_bands_not_primary"])]:
        out = EXP / "scratch" / f"determinism_{run}"
        subprocess.run([str(binary), str(out), str(cfg["step_cap"]), str(cfg["grid_side"]),
                        ",".join(f"{lo}-{hi}" for lo, hi in bands)], input=specs, text=True,
                       env={**os.environ, "RAYON_NUM_THREADS": "1"}, check=True, cwd=ROOT)
        count = 0
        for rule in rules:
            marker = EXP / "dumps" / run / f"{rule}_1001.done"
            deadline = time.monotonic() + 7200
            while not marker.exists():
                if time.monotonic() > deadline:
                    raise TimeoutError(f"Waiting for production {marker}")
                time.sleep(5)
            for suffix in ["bands.csv", "status.csv", "idur0.u32", "idur1.u32", "done"]:
                name = f"{rule}_1001.{suffix}"
                assert (out / name).read_bytes() == (EXP / "dumps" / run / name).read_bytes(), (run, name)
                count += 1
        report["runs"][run] = {"specs": len(rules), "files_compared": count, "byte_identical": True}
    (EXP / "results/determinism.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
