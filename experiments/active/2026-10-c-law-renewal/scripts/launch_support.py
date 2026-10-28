"""Queue the registered excluded diagnostic until existing heavy WSL jobs finish."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
FOLDER = EXP / "results/pilot_support"


def heavy_jobs():
    jobs = []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            words = (p / "cmdline").read_bytes().decode().split("\0")
            executable = words[0]
            if "/release/" in executable or Path(executable).name == "cargo":
                jobs.append((int(p.name), " ".join(words).strip()))
        except (OSError, UnicodeDecodeError):
            continue
    return sorted(jobs)


def worker():
    (FOLDER / "session.pid").write_text(str(os.getpid()) + "\n")
    status = 1
    try:
        while jobs := heavy_jobs():
            print("Waiting on live heavy jobs:", jobs, flush=True)
            time.sleep(15)
        print("No existing release/cargo processes; starting excluded support diagnostic.", flush=True)
        subprocess.run(["uv", "run", "--frozen", str(EXP / "scripts/support_probe.py")], cwd=ROOT, check=True)
        status = 0
    finally:
        (FOLDER / "session.exit").write_text(str(status) + "\n")


if __name__ == "__main__":
    FOLDER.mkdir(parents=True, exist_ok=True)
    if "--worker" in sys.argv:
        worker()
    else:
        with (FOLDER / "session.log").open("x") as log:
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--worker"], cwd=ROOT,
                stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        print("Queued excluded support diagnostic, worker PID", child.pid)
