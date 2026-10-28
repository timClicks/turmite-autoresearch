"""Check deterministic analysis replay without changing the recorded commit."""
from pathlib import Path
import hashlib
import subprocess
import sys

EXP=Path(__file__).resolve().parents[1]
ROOT=Path(__file__).resolve().parents[4]
paths=[EXP/'results'/name for name in ['analysis.json','analysis.txt','windows.csv',
       'seed_status.csv','rule_means_k21.csv','rule_means_k22.csv','rule_means_k23.csv']]
before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
subprocess.run([sys.executable,str(EXP/'scripts/analyse.py')],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
assert before=={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
print('Analysis replay: all seven published outputs byte-identical')
