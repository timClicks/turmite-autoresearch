"""Wait for this experiment's running pilot, then build the compact reports."""
from pathlib import Path
import subprocess
import time
EXP=Path(__file__).resolve().parents[1]
ROOT=Path(__file__).resolve().parents[4]
deadline=time.monotonic()+1800
while not (EXP/"results/pilot-v2.audit.json").is_file():
    assert time.monotonic()<deadline, "Pilot did not finish within registered budget; inspect log"
    time.sleep(5)
for script in ["summarize.py","report.py"]:
    with (EXP/"results"/f"{script[:-3]}.log").open("w") as log:
        subprocess.run(["uv","run",str(EXP/"scripts"/script)],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
with (EXP/"results/notebook.log").open("w") as log:
    subprocess.run(["uv","run","--with","nbconvert","--with","ipykernel","--with","nbformat","jupyter","nbconvert","--to","notebook","--execute","--inplace",str(EXP/"notebook.ipynb")],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
print("Report and clean-kernel notebook complete:",EXP.name,flush=True)
