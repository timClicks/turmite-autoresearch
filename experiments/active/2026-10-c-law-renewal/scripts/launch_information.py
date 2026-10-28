"""Run frozen information-preserving policies after verified heavy jobs finish."""
import os
from pathlib import Path
import subprocess
import sys
import time
from launch_support import heavy_jobs

ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
OUT=EXP / "results/information_v1"


def worker():
    (OUT / "session.pid").write_text(str(os.getpid())+"\n")
    status=1
    try:
        for stage in ["build","replay","pilot"]:
            while jobs:=heavy_jobs():
                print("Waiting on live jobs:",jobs,flush=True)
                time.sleep(15)
            print("Information stage",stage,flush=True)
            subprocess.run(["uv","run","--frozen",str(EXP / "scripts/run_information.py"),"--stage",stage],cwd=ROOT,check=True)
        subprocess.run(["uv","run","--frozen",str(EXP / "scripts/analyse_information.py")],cwd=ROOT,check=True)
        status=0
    finally:
        (OUT / "session.exit").write_text(str(status)+"\n")


if __name__=="__main__":
    OUT.mkdir(parents=True,exist_ok=True)
    if "--worker" in sys.argv: worker()
    else:
        with (OUT / "session.log").open("x") as log:
            p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),"--worker"],cwd=ROOT,stdin=subprocess.DEVNULL,
                stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        print("Queued information pilot PID",p.pid)
