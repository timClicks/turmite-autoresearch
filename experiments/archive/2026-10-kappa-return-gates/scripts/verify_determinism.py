"""Thread-count independence and resume-equals-uninterrupted for the sampler (12 pilot-seed specs)."""
from pathlib import Path
import hashlib, json, shutil, subprocess
import polars as pl
ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
BIN = ROOT / "target/release/examples/kappa_return_gates_sampler"
rules = pl.read_csv(EXP / "results/cohort.csv")["base"].to_list()[::4]
specs = [f"{r}@{s}" for r in rules for s in (2026102001, 2026102002)]
base = EXP / "scratch/determinism"
shutil.rmtree(base, ignore_errors=True)
def run(d, threads):
    subprocess.run([str(BIN), str(d), str(2**29), "4096", "32768-34816,131072-139264", "deterministic-check", str(threads)], input="\n".join(specs) + "\n", text=True, check=True, stderr=subprocess.DEVNULL)
def digest(d):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.glob("*")) if not p.name.endswith(".tmp")}
run(base / "t1", 1); run(base / "t6", 6)
shutil.copytree(base / "t6", base / "resumed")
victims = specs[:4]
for s in victims:
    for p in (base / "resumed").glob(s.replace("@", "_") + ".*"):
        p.unlink()
(base / "resumed" / (specs[4].replace("@", "_") + ".gates.csv.tmp")).write_text("partial")
(base / "resumed" / (specs[4].replace("@", "_") + ".done")).unlink()
(base / "resumed" / (specs[4].replace("@", "_") + ".gates.csv")).unlink()
run(base / "resumed", 3)
d1, d6, dr = digest(base / "t1"), digest(base / "t6"), digest(base / "resumed")
rep = dict(specs=len(specs), files=len(d1), one_vs_six_threads_identical=d1 == d6, interrupted_resumed_identical=d1 == dr,
           note="resumed copy: 4 specs deleted, 1 spec left with a stray .tmp and no .done; rerun with 3 threads; finished specs skipped")
(EXP / "results/determinism.json").write_text(json.dumps(rep, indent=2) + "\n")
print(rep)
assert rep["one_vs_six_threads_identical"] and rep["interrupted_resumed_identical"]
