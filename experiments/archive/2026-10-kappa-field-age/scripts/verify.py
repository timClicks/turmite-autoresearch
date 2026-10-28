"""Sampled thread replay and finished-trajectory resume verification."""
from pathlib import Path
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
m=json.loads((EXP/"results/profile-v1.manifest.json").read_text())
cfg=m["config"]
# This verifies the CURRENT binary; source hashes are recorded explicitly,
# since the unrelated crate module export changed after the profile.
sources={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in cfg["sources"]}
specs=[f"{r}@{cfg['seeds'][0]}" for r in cfg["rules"]]+[f"{w}:{s}" for w in ["rotor","rw"] for s in cfg["control_seeds"]]
paths=[]
for threads in [1,6]:
    dest=EXP/"scratch"/f"thread-{threads}"
    cmd=[str(ROOT/"target/release/examples"/cfg["example"]),str(dest),str(cfg["cap"]),str(cfg["grid"]),
         ",".join(f"{l}-{h}" for l,h in cfg["bands"]),"thread-check-v1",str(threads)]
    subprocess.run(cmd,input="\n".join(specs)+"\n",text=True,check=True)
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.iterdir())}
    paths.append(hashes)
    subprocess.run(cmd,input="\n".join(specs)+"\n",text=True,check=True)
    assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.iterdir())}
assert paths[0]==paths[1]
report=dict(passed=True,specs=specs,threads=[1,6],files_compared=len(paths[0]),finished_trajectory_resume_byte_equal=True,
            mid_trajectory_checkpoint_tested=False, sources=sources,
            command=f"uv run {Path(__file__).relative_to(ROOT)}",scope="8-spec sample, two profile bands; not all pilot seeds or third-band replay")
(EXP/"results/determinism.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps(report,indent=2))
