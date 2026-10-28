"""Synthetic two-state chains with planted age-conditional return hazards.
The age label is exogenous at each departure, not a physically rejuvenated ant.
Permutation is within departure-state, heading and geometry strata.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
seed=2026101581
rng=np.random.default_rng(seed)
N=400000
age=rng.integers(0,2,N)
heading=rng.integers(0,4,N)
geometry=rng.integers(0,4,N)
u=rng.random(N)
state=np.zeros(N,dtype=np.int8)
transition=np.zeros(N,dtype=np.int8)
z=0
for i in range(N):
    state[i]=z
    p=(.08+.24*age[i]) if z==0 else .2
    transition[i]=int(u[i]<p)
    z^=int(transition[i])
def contrast(labels):
    hazards=[];counts=[]
    for a in [0,1]:
        mask=(state==0)&(labels==a)
        counts.append(int(mask.sum()))
        hazards.append(float(transition[mask].mean()))
    se=float(np.sqrt(sum(p*(1-p)/n for p,n in zip(hazards,counts))))
    return dict(hazards=hazards,counts=counts,contrast=hazards[1]-hazards[0],contrast_se=se)
planted=contrast(age)
permuted=age.copy()
for s in [0,1]:
    for h in range(4):
        for g in range(4):
            idx=np.flatnonzero((state==s)&(heading==h)&(geometry==g))
            permuted[idx]=rng.permutation(age[idx])
null=contrast(permuted)
assert abs(planted["contrast"]-.24)<4*planted["contrast_se"]
assert abs(null["contrast"])<4*null["contrast_se"]
report=dict(seed=seed,N=N,known_return_hazards=[.08,.32],known_contrast=.24,planted=planted,permuted=null,
            passed=True,command=f"uv run {Path(__file__).relative_to(ROOT)}",
            git_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True,cwd=ROOT).strip(),
            source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            scope="Frequency estimator calibration only. Rust reference tests independently validate discovery/visit/phase and rim census. Does not calibrate log-kappa prediction or causal age effects.")
(EXP/"results/calibration.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps(report,indent=2))
