"""G2: uninterrupted 1-thread vs 2-thread vs 2-thread SIGKILLed-mid-batch-then-resumed.
All three go through scripts/run.py. Compares every payload byte except .done
(whose marker embeds the thread-bearing config hash) and the derived census CSVs.
Kill is by process group of the launched run.py only (never pkill by name).
Usage: uv run scripts/check_interrupt.py   (needs manifests from prepare_gates.py)
"""
from pathlib import Path
import hashlib, json, os, signal, subprocess, sys, time
ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RUN = EXP / "scripts/run.py"
def run(name):
    t = time.monotonic()
    subprocess.run(["uv", "run", str(RUN), "--name", name], cwd=ROOT, check=True)
    return time.monotonic() - t
def payload(name):
    out = {}
    for batch in ("ants", "controls"):
        for f in sorted((EXP / "dumps" / name / batch).glob("*")):
            if f.suffix in (".done", ".tmp"):
                continue
            out[f"{batch}/{f.name}"] = hashlib.sha256(f.read_bytes()).hexdigest()
    for b in ("ants", "controls"):
        p = EXP / "results" / f"{name}.{b}.census.csv"
        out[f"census/{b}"] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out
secs = {"resume-t1": run("resume-t1"), "resume-t2": run("resume-t2")}
# interrupted run
name = "resume-k2"
ants = EXP / "dumps" / name / "ants"
proc = subprocess.Popen(["uv", "run", str(RUN), "--name", name], cwd=ROOT, start_new_session=True)
killed_at = None
deadline = time.monotonic() + 600
while time.monotonic() < deadline and proc.poll() is None:
    n = len(list(ants.glob("*.done"))) if ants.is_dir() else 0
    if 8 <= n < 28:
        killed_at = n
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        break
    time.sleep(0.05)
proc.wait()
assert killed_at is not None, "run finished before it could be interrupted; enlarge cohort"
partial = sorted(p.name for p in ants.iterdir() if not p.name.endswith(".done"))
stems_done = {p.name[:-5] for p in ants.glob("*.done")}
stems_files = {p.name.split(".")[0] for p in ants.iterdir()}
in_flight = sorted(stems_files - stems_done)
secs["resume-k2-after-kill"] = run(name)
a, b, c = payload("resume-t1"), payload("resume-t2"), payload(name)
rep = dict(
    command="uv run experiments/archive/2026-10-kappa-tail-budget/scripts/check_interrupt.py",
    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    run_wrapper_sha256=hashlib.sha256(RUN.read_bytes()).hexdigest(),
    manifests={n: hashlib.sha256((EXP / f"results/{n}.manifest.json").read_bytes()).hexdigest() for n in ("resume-t1", "resume-t2", "resume-k2")},
    files_compared=len(a), done_markers_at_kill=killed_at, in_flight_stems_at_kill=in_flight,
    one_vs_two_threads_identical=a == b, uninterrupted_vs_resumed_identical=b == c,
    first_difference=next((k for k in a if a[k] != b.get(k) or b[k] != c.get(k)), None),
    wall_seconds=secs,
    scope="8 rules x 4 seeds x 2 bands (+rotor/rw controls). 1 vs 2 threads here; 1 vs 6 threads from results/determinism.json (earlier session). Finished-trajectory resume only; no mid-trajectory state checkpoint exists.",
)
(EXP / "results/interrupt_resume.json").write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n")
print(json.dumps(rep, indent=1))
sys.exit(0 if rep["one_vs_two_threads_identical"] and rep["uninterrupted_vs_resumed_identical"] else 1)
