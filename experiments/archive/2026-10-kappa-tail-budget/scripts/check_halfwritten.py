"""G2b: deterministic test of the half-written-stem resume path (registered in NOTEBOOK.md).
resume-c2 is a byte copy of resume-t2's manifest (same config), so its payload must equal resume-t2's.
Damage one finished stem (delete .done, truncate bins.csv, stray .tmp) and plant a stray .tmp beside an
intact stem; delete audit + census; rerun through scripts/run.py; compare every payload byte again.
  uv run experiments/archive/2026-10-kappa-tail-budget/scripts/check_halfwritten.py
"""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, time
ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RUN = EXP / "scripts/run.py"
name = "resume-c2"
man = EXP / f"results/{name}.manifest.json"
shutil.copyfile(EXP / "results/resume-t2.manifest.json", man)
def run():
    t = time.monotonic()
    subprocess.run(["uv", "run", str(RUN), "--name", name], cwd=ROOT, check=True)
    return time.monotonic() - t
def payload(n):
    out = {}
    for batch in ("ants", "controls"):
        for f in sorted((EXP / "dumps" / n / batch).glob("*")):
            if f.suffix in (".done", ".tmp"):
                continue
            out[f"{batch}/{f.name}"] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out
ref = payload("resume-t2")
secs = {"first_run": run()}
first = payload(name)
ants = EXP / "dumps" / name / "ants"
stems = sorted({p.name.split(".")[0] for p in ants.glob("*.done")})
damaged, intact = stems[0], stems[1]
(ants / f"{damaged}.done").unlink()
b = ants / f"{damaged}.bins.csv"
b.write_bytes(b.read_bytes()[: len(b.read_bytes()) // 2])
(ants / f"{damaged}.hazards.csv.tmp").write_bytes(b"garbage,half-written\n")
(ants / f"{intact}.age.csv.tmp").write_bytes(b"stray\n")
for p in [EXP / f"results/{name}.audit.json", EXP / f"results/{name}.ants.census.csv", EXP / f"results/{name}.controls.census.csv"]:
    p.unlink()
secs["after_damage"] = run()
second = payload(name)
rep = dict(command="uv run experiments/archive/2026-10-kappa-tail-budget/scripts/check_halfwritten.py",
           source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           manifest_sha256=hashlib.sha256(man.read_bytes()).hexdigest(),
           damaged_stem=damaged, intact_stem_with_stray_tmp=intact, files_compared=len(ref),
           first_run_equals_resume_t2=first == ref, after_damage_equals_resume_t2=second == ref,
           stray_tmp_for_damaged_stem_remaining=(ants / f"{damaged}.hazards.csv.tmp").exists(),
           stray_tmp_for_intact_stem_remaining=(ants / f"{intact}.age.csv.tmp").exists(),
           wall_seconds=secs)
(EXP / "results/halfwritten_resume.json").write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
print(json.dumps(rep, indent=1))
sys.exit(0 if rep["first_run_equals_resume_t2"] and rep["after_damage_equals_resume_t2"] else 1)
