"""Describe the excluded horizon pilot without fitting scientific predictions."""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RUNS = EXP / "results/pilot_v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert (RUNS / "session.exit").read_text().strip() == "0", "pilot must finish before diagnosis"
    with (EXP / "results/design/families.csv").open() as f:
        design = [r for r in csv.DictReader(f) if r["split"] == "pilot"]
    inputs = [EXP / "results/design/families.csv", RUNS / "horizon.json"]
    rows = []
    gates = {}
    for k in range(22, 27):
        good = {}
        for d in design:
            good.setdefault(d["family"], True)
            for seed in d["interior_seeds"].split(";"):
                path = RUNS / f"{d['family']}-{d['arm']}-{seed}-k{k}.json"
                if not path.exists():
                    continue
                inputs.append(path)
                assert path.with_suffix(".done").read_text().strip() == sha(path)
                s = json.loads(path.read_text())["summary"]
                assert sum(s["lag"]) == s["boundary_reads"]
                assert s["births"] <= s["boundary_reads"]
                assert s["steps"] == 2**k and not s["escaped"]
                consumed = (s["area"] - 256 * 2048) / (256 * 2048)
                enough = s["births"] >= 5000
                in_band = 0.1 <= consumed <= 0.8
                good[d["family"]] &= enough and in_band
                reads = s["boundary_reads"]
                row = {"family": d["family"], "arm": d["arm"], "rule": d["rule"], "lead": d["lead"], "seed": seed,
                    "log2": k, "births": s["births"], "boundary_reads": reads,
                    "c": s["births"] / reads if reads else None,
                    "boundary_fraction": reads / 2**(k - 1), "band_consumed": consumed,
                    "birth_gate": enough, "band_gate": in_band, "usable": enough and in_band}
                for label, value in zip(["first", "lag4", "other_short", "long"], s["lag"]):
                    row[f"{label}_reads_per_birth"] = value / s["births"] if s["births"] else None
                rows.append(row)
        gates[str(k)] = good
    final = [r for r in rows if r["log2"] == 26]
    report = {"scope": "excluded pilot feasibility; no main outcomes scored",
        "command": "uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/pilot_diagnose.py",
        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "script_sha256": sha(Path(__file__)), "families_passing_by_log2": gates,
        "k26_n": len(final), "k26_usable_runs": sum(r["usable"] for r in final),
        "k26_birth_gate_failures": sum(not r["birth_gate"] for r in final),
        "k26_band_gate_failures": sum(not r["band_gate"] for r in final),
        "k26_boundary_fraction_range": [min(r["boundary_fraction"] for r in final), max(r["boundary_fraction"] for r in final)],
        "k26_birth_range": [min(r["births"] for r in final), max(r["births"] for r in final)],
        "inputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs}}
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    output = {"pilot_diagnostics.csv": buf.getvalue(), "pilot_diagnostics.json": json.dumps(report, indent=2) + "\n"}
    for name in output:
        if (EXP / "results" / name).exists():
            raise RuntimeError(f"refusing to replace {name}")
    for name, data in output.items():
        (EXP / "results" / name).write_text(data)
    print(json.dumps({k: v for k, v in report.items() if k != "inputs_sha256"}, indent=2))


if __name__ == "__main__":
    main()
