"""Start the frozen pilot sequence as an observable detached WSL job."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
folder = EXP / "results/pilot_v1"
folder.mkdir(parents=True, exist_ok=True)
with (folder / "session.log").open("x") as log:
    process = subprocess.Popen(["bash", str(EXP / "scripts/run_pilot_all.sh")], cwd=ROOT,
        stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
print(f"Started excluded pilot PID {process.pid}; log {folder / 'session.log'}")
