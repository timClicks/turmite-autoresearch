"""Validate all frozen production payloads and record deterministic input hashes.

Run under uv after both batches complete. Does not change raw payloads.
"""
import csv
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", choices=["prod16", "prod8"])
    args = parser.parse_args()
    tag = f".{args.run}" if args.run else ""
    cfg = json.loads((EXP / "config.frozen.json").read_text())
    assert sha(EXP / "results/cohort_rules.txt") == cfg["cohort_sha256"]
    rules = (EXP / cfg["cohort_file"]).read_text().split()
    seeds = [s for lo, hi in cfg["seed_groups"].values() for s in range(lo, hi + 1)]
    report = {"command": "uv run experiments/archive/2026-10-fixed-area-cycles/scripts/audit.py" + (" " + " ".join(sys.argv[1:]) if sys.argv[1:] else ""),
              "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "config_sha256": sha(EXP / "config.frozen.json"), "dirty_workspace": True,
              "source_sha256": {p: sha(ROOT / p) for p in [
                  "src/fixed_area.rs", "src/walkers.rs", "src/rule.rs", "src/lib.rs",
                  "examples/fixed_area_cycles_sampler.rs", "Cargo.lock",
                  "experiments/archive/2026-10-fixed-area-cycles/scripts/audit.py"]}, "runs": {}}
    hashes = []
    statuses = []
    for run, bands in [("prod16", cfg["primary_bands"]), ("prod8", cfg["sensitivity_bands_not_primary"])]:
        if args.run and run != args.run:
            continue
        directory = EXP / "dumps" / run
        marker = f'fixed_area_v1 cap={cfg["step_cap"]} grid={cfg["grid_side"]} bands={[(lo, hi) for lo, hi in bands]}\n'
        expected = {f"{r}_{s}" for r in rules for s in seeds}
        assert {p.stem for p in directory.glob("*.done")} == expected, f"Incomplete/unexpected {run} cohort"
        max_censor = 0.0
        not_complete = 0
        for rule in rules:
            for seed in seeds:
                name = f"{rule}_{seed}"
                done = directory / f"{name}.done"
                assert done.read_text() == marker, done
                paths = [done, directory / f"{name}.bands.csv", directory / f"{name}.status.csv"]
                with paths[2].open() as f:
                    status, = list(csv.DictReader(f))
                assert status["spec"] == f"{rule}@{seed}"
                assert int(status["grid"]) == cfg["grid_side"] and int(status["cap"]) == cfg["step_cap"]
                not_complete += status["stop"] != "complete"
                statuses.append({"run": run, **status})
                with paths[1].open() as f:
                    rows = list(csv.DictReader(f))
                assert len(rows) == len(bands)
                for band, ((lo, hi), row) in enumerate(zip(bands, rows)):
                    n = lambda col: int(row[col])
                    assert row["spec"] == status["spec"] and n("band_id") == band
                    assert (n("lo"), n("hi")) == (lo, hi)
                    # Coverage failures must be repaired/reported before inference, not silently removed.
                    assert n("reached_hi") == 1, (run, name, band, status)
                    assert n("area_start") == lo and n("area_end") == hi
                    assert n("new_cells") == hi - lo
                    assert n("t_end") - n("t_start") == n("steps")
                    assert n("fresh_from_interior") == 0
                    assert n("b_dep") + n("i_dep") == n("steps")
                    for label in ("b", "i"):
                        assert n(f"{label}_complete_steps") + n(f"{label}_clip_steps") == n(f"{label}_dep")
                        assert sum(map(int, row[f"{label}_bin_n"].split(";"))) == n(f"{label}_complete")
                        assert sum(map(int, row[f"{label}_bin_steps"].split(";"))) == n(f"{label}_complete_steps")
                    max_censor = max(max_censor, (n("i_clip_steps") + n("i_clip_max")) / n("i_dep"))
                    duration_path = directory / f"{name}.idur{band}.u32"
                    paths.append(duration_path)
                    durations = [x[0] for x in struct.iter_unpack("<I", duration_path.read_bytes())]
                    assert len(durations) == n("i_complete")
                    assert sum(durations) == n("i_complete_steps")
                for path in paths:
                    hashes.append(f"{sha(path)}  {path.relative_to(EXP).as_posix()}\n")
        report["runs"][run] = {"specs": len(expected), "band_rows": len(expected) * len(bands),
                               "not_complete": not_complete, "max_censor_gate_ratio": max_censor,
                               "accounting_pass": True}
    manifest = EXP / f"results/production{tag}.sha256"
    manifest.write_text("".join(hashes))
    report["payload_manifest_sha256"] = sha(manifest)
    with (EXP / f"results/run_status{tag}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(statuses[0]))
        writer.writeheader()
        writer.writerows(statuses)
    (EXP / f"results/audit{tag}.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
