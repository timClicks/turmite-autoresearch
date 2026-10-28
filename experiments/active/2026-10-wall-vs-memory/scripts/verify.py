"""Check a probe output against the registered specs before it is analysed.

usage (repo root):
  uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/verify.py [RESULTS_DIR] [--against COMMITTED_DIR]
RESULTS_DIR defaults to the committed results/. For each stage present it checks that
  1. the specs file hashes to the specs_sha256 recorded in that directory's provenance;
  2. the CSV hashes to the sha256 recorded in the provenance;
  3. the CSV has exactly the specs listed, no more and no fewer, each once, with the CSV header;
  4. each spec has the contiguous windows k = 9..max_log2 (probe reports k = log2 of the window's
     END t, so k=22 is the window (2^21, 2^22]), or stops early only if the run escaped the board (escaped = true);
and, with --against, that the CSV is byte-identical to the committed one (the runs are
deterministic and independent of thread count, so a fresh rerun must match).
Exits non-zero on any failure.
"""
import hashlib
import sys
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
COMMITTED = EXP / "results"
STAGES = [("probe.csv", "specs.txt", "provenance.txt", 27, "probe_csv_sha256"),
          ("stage2_probe.csv", "stage2_specs.txt", "stage2_provenance.txt", 31, "stage2_probe.csv_sha256")]
HEADER = "rule,k,t,area,perimeter,new_cells,boundary_steps,fresh_nbrs,escaped,rg2,ant_r2,ant_var,width,height"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prov(p: Path) -> dict[str, str]:
    return dict(line.split(" ", 1) for line in p.read_text().splitlines() if " " in line)


args = sys.argv[1:]
against = None
if "--against" in args:
    i = args.index("--against")
    against = Path(args[i + 1])
    del args[i : i + 2]
res = Path(args[0]) if args else COMMITTED
bad = 0


def check(ok: bool, msg: str) -> None:
    global bad
    print(("ok   " if ok else "FAIL ") + msg)
    bad += not ok


seen = 0
for csv_name, specs_name, prov_name, max_log2, sha_key in STAGES:
    csv, pv = res / csv_name, res / prov_name
    if not csv.exists():
        print(f"skip {csv_name}: not present in {res}")
        continue
    seen += 1
    specs_file = COMMITTED / specs_name
    specs = specs_file.read_text().split()
    p = prov(pv) if pv.exists() else {}
    check(p.get("specs_sha256") == sha(specs_file), f"{specs_name} sha256 matches provenance")
    check(p.get(sha_key) == sha(csv), f"{csv_name} sha256 matches provenance")
    lines = csv.read_text().splitlines()
    if not lines:
        check(False, f"{csv_name} is empty (run still in progress?)")
        continue
    check(lines[0] == HEADER, f"{csv_name} header")
    ks: dict[str, list[int]] = {}
    esc: dict[str, bool] = {}
    for line in lines[1:]:
        f = line.split(",")
        ks.setdefault(f[0], []).append(int(f[1]))
        esc[f[0]] = esc.get(f[0], False) or f[8] == "true"
    check(sorted(ks) == sorted(specs) and len(specs) == len(set(specs)),
          f"{csv_name} has exactly the {len(specs)} registered specs ({len(ks)} found)")
    short = [s for s, k in ks.items() if k != list(range(9, 9 + len(k))) or (k[-1] != max_log2 and not esc[s])]
    check(not short, f"{csv_name} windows contiguous from k=9 to {max_log2} unless escaped ({len(short)} incomplete)")
    print(f"note {csv_name}: {sum(esc.values())} runs flagged escaped (kept; analyse*.py reports them)")
    if against is not None:
        check(csv.read_bytes() == (against / csv_name).read_bytes(), f"{csv_name} byte-identical to {against / csv_name}")
check(seen > 0, "at least one stage present")
sys.exit(1 if bad else 0)
