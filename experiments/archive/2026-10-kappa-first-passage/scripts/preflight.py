"""Validate the planning scaffold; never launch a scientific run."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def main():
    required = ["README.md", "NOTEBOOK.md", "HANDOFF.md", "SCHEMA.md", "notebook.ipynb"]
    for name in required:
        path = EXP / name
        if not path.is_file():
            raise SystemExit(f"Missing scaffold file: {path}")
        print(hashlib.sha256(path.read_bytes()).hexdigest(), path.relative_to(ROOT))
    nb = json.loads((EXP / "notebook.ipynb").read_text(encoding="utf-8"))
    assert nb["nbformat"] == 4
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    print("git:", revision)
    print("Scaffold present. Instrument/calibration/pilot/confirmation: NOT RUN.")
    print("This check does not establish scientific readiness.")


if __name__ == "__main__":
    main()
