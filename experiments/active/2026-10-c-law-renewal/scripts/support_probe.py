"""Diagnostic repeats at k=26 on excluded pilots after the horizon gate failed."""
from __future__ import annotations
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time
from pilot_report import projection

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    old = EXP / "results/pilot_v1"
    assert (old / "session.exit").read_text().strip() == "0"
    assert json.loads((old / "horizon.json").read_text())["selected_log2"] is None
    build = json.loads((old / "build.json").read_text())
    binary = Path(build["binary"])
    assert sha(binary) == build["binary_sha256"]
    # Source edits in tests/documentation do not change this recorded binary.
    for name in ["src/edge_renewal.rs", "src/edge_trace.rs", "src/walkers.rs", "src/rule.rs", "examples/c_law_renewal_trace.rs"]:
        assert sha(ROOT / name) == build["sources_sha256"][name]
    with (EXP / "results/design/families.csv").open() as f:
        design = [r for r in csv.DictReader(f) if r["split"] == "pilot"]
    results = EXP / "results/pilot_support"
    dump = EXP / "dumps/pilot_support"
    results.mkdir(parents=True, exist_ok=True)
    dump.mkdir(parents=True, exist_ok=True)
    per_run = {}
    family_of = {}
    inputs = [old / "build.json", old / "horizon.json", EXP / "results/design/families.csv"]
    for d in design:
        for seed in d["interior_seeds"].split(";"):
            name = f"{d['family']}-{d['arm']}-{seed}-k26"
            path = results / (name + ".json")
            done = path.with_suffix(".done")
            compressed = dump / (name + ".csv.gz")
            baseline = old / (name + ".json")
            expected = json.loads(baseline.read_text())["summary"]
            argv = ["band", d["rule"], seed, "26", "256", "4096", "2048", "counts"]
            if done.exists():
                record = json.loads(path.read_text())
                assert done.read_text().strip() == sha(path)
                assert record["counts_sha256"] == sha(compressed)
                assert record["argv"] == argv and record["binary_sha256"] == sha(binary)
            else:
                if path.exists() or compressed.exists():
                    raise RuntimeError(f"unmarked output exists for {name}; inspect before resuming")
                raw = dump / (name + ".partial.csv")
                if raw.exists():
                    raise RuntimeError(f"partial dump exists: {raw}; inspect before restart")
                start = time.monotonic()
                with raw.open("x") as out:
                    completed = subprocess.run([str(binary), *argv], cwd=ROOT, stdout=out, stderr=subprocess.PIPE, text=True, check=True)
                summary = json.loads(completed.stderr)
                assert summary == expected
                with compressed.open("xb") as out, gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0) as zipped:
                    zipped.write(raw.read_bytes())
                raw.unlink()
                record = {"argv": argv, "binary_sha256": sha(binary), "summary": summary,
                    "counts_sha256": sha(compressed), "counts_file": str(compressed.relative_to(EXP)),
                    "driver_sha256": sha(Path(__file__)), "baseline_sha256": sha(baseline),
                    "seconds": time.monotonic() - start}
                path.write_text(json.dumps(record, indent=2) + "\n")
                done.write_text(sha(path) + "\n")
            states = Counter()
            outgoing = Counter()
            incoming = Counter()
            terminal = Counter()
            with gzip.open(compressed, "rt") as f:
                for row in csv.DictReader(f):
                    source = tuple(map(int, row["source"].split(":")))
                    count = int(row["count"])
                    if row["kind"] == "state":
                        states[source] += count
                        direction = 1 if source[1] & 1 else 3
                        assert int(row["births"]) == count * int(source[2] & (1 << direction) == 0)
                    elif row["kind"] == "edge":
                        outgoing[source] += count
                        incoming[tuple(map(int, row["target"].split(":")))] += count
                    elif row["kind"] == "censored":
                        terminal[source] += count
            assert states == outgoing + terminal
            assert sum((states - incoming).values()) == 1
            assert sum(states.values()) == expected["boundary_reads"] > 0
            per_run[name] = states
            family_of[name] = d["family"]
            inputs.extend([baseline, path])
            print(name, "distinct states", len(states), flush=True)
    support = {}
    for model in ["S0", "S1", "S2", "C0", "C1", "C2", "C4", "C8"]:
        families = defaultdict(Counter)
        projected = {}
        for name, counts in per_run.items():
            c = Counter()
            for source, value in counts.items():
                c[projection(model, source)] += value
            projected[name] = c
            families[family_of[name]].update(c)
        details = []
        for name, counts in projected.items():
            train = set().union(*(set(c) for f, c in families.items() if f != family_of[name]))
            unseen = sum(value for source, value in counts.items() if source not in train) / sum(counts.values())
            details.append({"run": name, "unseen_mass": unseen, "states": len(counts)})
        masses = sorted(r["unseen_mass"] for r in details)
        support[model] = {"median_unseen_mass": (masses[11] + masses[12]) / 2,
            "max_unseen_mass": max(masses), "runs_over_5pct": sum(v > 0.05 for v in masses), "runs": details}
    record = {"scope": "excluded pilot support only; original horizon failure stands",
        "command": "uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/support_probe.py",
        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "script_sha256": sha(Path(__file__)), "projection_script_sha256": sha(EXP / "scripts/pilot_report.py"),
        "models": support, "feasibility_prediction_held": support["S1"]["runs_over_5pct"] >= 12,
        "inputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs}}
    path = EXP / "results/support_report.json"
    if path.exists():
        raise RuntimeError("refusing to replace existing support report")
    path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({k: {a: b for a, b in v.items() if a != "runs"} for k, v in support.items()}, indent=2), flush=True)


if __name__ == "__main__":
    main()
