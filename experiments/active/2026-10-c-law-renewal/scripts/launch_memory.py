"""Run the registered finite-memory pilot after verified heavy jobs finish."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import time
from launch_support import heavy_jobs

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
FOLDER = EXP / "results/memory_v1"


def wait_idle():
    while jobs := heavy_jobs():
        print("Waiting on live heavy jobs:",jobs,flush=True)
        time.sleep(15)


def worker():
    (FOLDER / "session.pid").write_text(str(os.getpid())+"\n")
    status = 1
    try:
        for stage in ["build","controls","pilot"]:
            wait_idle()
            print("Starting memory stage",stage,flush=True)
            subprocess.run(["uv","run","--frozen",str(EXP / "scripts/run_memory.py"),"--stage",stage],cwd=ROOT,check=True)
        subprocess.run(["uv","run","--frozen",str(EXP / "scripts/analyse_memory.py")],cwd=ROOT,check=True)
        status = 0
    finally:
        (FOLDER / "session.exit").write_text(str(status)+"\n")


if __name__=="__main__":
    FOLDER.mkdir(parents=True,exist_ok=True)
    if "--worker" in sys.argv:
        worker()
    else:
        with (FOLDER / "session.log").open("x") as log:
            p = subprocess.Popen([sys.executable,str(Path(__file__).resolve()),"--worker"],cwd=ROOT,
                stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        print("Queued excluded finite-memory pilot worker PID",p.pid)
