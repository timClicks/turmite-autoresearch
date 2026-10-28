"""Run/resume the registered paired phase reset and write a deterministic summary.
Run from repo root: uv run experiments/archive/2026-10-crystal-rules/scripts/phase_reset.py
No third-party Python dependencies. Source hashes invalidate stale checkpoints.
"""
import csv
import hashlib
import json
import os
from pathlib import Path
import statistics as st
import subprocess

ROOT = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parents[1]
RESULTS = E / "results"
RULES = ["RLLLLRRL", "LRRRRRLLR", "RLLLLLLLRRLRR"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.chdir(ROOT)
    subprocess.run(["cargo", "build", "--release", "--example", "crystal_rules_phase"], check=True)
    target = Path(os.environ.get("CARGO_TARGET_DIR", ROOT / "target"))
    binary = target / "release/examples/crystal_rules_phase"
    recipe = {
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "sources": {str(p.relative_to(ROOT)): sha(p) for p in [
            ROOT / "examples/crystal_rules_phase.rs", Path(__file__),
            ROOT / "src/rule.rs", ROOT / "src/lib.rs", ROOT / "Cargo.lock"]},
        "seed": None, "scan_limit": 2**25, "size": 8192,
        "trials": 16, "radius": 128, "horizon": 2048,
        "command": "uv run experiments/archive/2026-10-crystal-rules/scripts/phase_reset.py",
        "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(),
        "uv": subprocess.check_output(["uv", "--version"], text=True).strip(),
        "binary_sha256": sha(binary),
    }
    all_rows = []
    for rule in RULES:
        output = RESULTS / f"phase_{rule}.csv"
        marker = output.with_suffix(".done")
        metadata = output.with_suffix(".json")
        spec = dict(recipe, argv=[str(binary), rule])
        if marker.exists():
            assert json.loads(metadata.read_text()) == spec, "stale recipe; archive explicitly before rerun"
            assert marker.read_text().strip() == sha(output), "checkpoint hash mismatch"
        else:
            assert not output.exists(), "existing data without marker; inspect before replacing"
            partial = output.with_suffix(".partial")
            with partial.open("w") as stream:
                subprocess.run([str(binary), rule], stdout=stream, check=True)
            partial.rename(output)
            metadata.write_text(json.dumps(spec, indent=2) + "\n")
            marker.write_text(sha(output) + "\n")
        with output.open() as stream:
            all_rows.extend(csv.DictReader(stream))
    lines = ["S2 phase-reset paired results", json.dumps(recipe, sort_keys=True)]
    for rule in RULES:
        rows = [r for r in all_rows if r["rule"] == rule]
        sham = {r["trial"]: r for r in rows if r["phase"] == "2"}
        assert all(int(r["prefix"]) == 2048 and int(r["edited"]) == 0 for r in sham.values())
        lines.append(f"\n{rule}: n={len(sham)} paired trials, one blank-start trajectory; no independent seeds")
        for phase in ["2", "0", "3"]:
            arm = [r for r in rows if r["phase"] == phase]
            lines.append(f" phase {phase}: censored={sum(r['censored']=='true' for r in arm)}/{len(arm)}; "
                         f"mean edited={st.mean(int(r['edited']) for r in arm):.1f}; "
                         f"mean outside steps={st.mean(int(r['outside']) for r in arm):.1f}; "
                         f"mean alt={st.mean(float(r['alt_fraction']) for r in arm):.6f}; "
                         f"mean termination={st.mean(int(r['termination']) for r in arm):.1f}")
            if phase == "2":
                continue
            da = [float(r["alt_fraction"])-float(sham[r["trial"]]["alt_fraction"]) for r in arm]
            de = [float(r["early_alt_fraction"])-float(sham[r["trial"]]["early_alt_fraction"]) for r in arm]
            dt = [int(r["termination"])-int(sham[r["trial"]]["termination"]) for r in arm]
            a = sum(d <= -0.10 for d in da)
            b = sum(d < 0 for d in dt)
            verdict = "NOT EVALUABLE" if len(arm)!=16 else ("HELD" if a>=12 and b>=12 else "FAILED")
            lines.append(f"  alternating drop>=0.10: {a}/{len(arm)}; earlier termination: {b}/{len(arm)}; "
                         f"termination ties: {sum(d==0 for d in dt)}; joint prediction {verdict}")
            for name, values in [("alt delta", da), ("early alt delta", de), ("restricted termination delta",dt)]:
                lines.append(f"  {name}: mean={st.mean(values):.6f}, between-trial SD={st.stdev(values):.6f}")
    (RESULTS / "phase_summary.txt").write_text("\n".join(lines)+"\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
