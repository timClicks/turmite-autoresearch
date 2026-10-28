# /// script
# dependencies = ["nbformat"]
# ///
"""Builds notebook.ipynb for this experiment. usage: uv run experiments/archive/2026-10-highway-decider/scripts/build_notebook.py
Execute: uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace \\
    experiments/archive/2026-10-highway-decider/notebook.ipynb"""
from pathlib import Path

import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# Do the census highways survive a configuration-level check?

## Question
The census calls a rule a highway when the ant's trace repeats. That says nothing about the configuration. A **rectangle translated-cycler certificate** asks for four finite
things: (a) in `P` steps the ant stays inside a window `W` and returns to the same heading displaced by `v`; (b) the configuration afterwards equals the translate of the one before on
`W ∩ (W+v)`; (c) the leading edge of `W` is blank; (d) the strip ahead of `W` is blank. If they hold, the highway continues for every `k` (theorem checked in Lean, below).

## Assumptions
Configurations are dumps of the true state of a plain blank-board simulation at `onset + K*P` steps (K in 3, 10, 30, 100, 300) for the 571 `confirmed_v2` census highways; `W` is the bounding box of the cells the ant stands on during `P` steps.
The decider (`scripts/decide.py`) is stdlib Python with its own ant; its ant is compared with `reference::Ant` on each dump. Everything here reads committed files in `results/`."""),
code("""import csv, collections, hashlib, subprocess
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
R = ROOT / "experiments/archive/2026-10-highway-decider/results"
for n in sorted(p.name for p in R.glob("*") if p.is_file()):
    print(hashlib.sha256((R / n).read_bytes()).hexdigest()[:16], n)
print("git", subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip())"""),
md("## Main result (D1, C4, D4, D5)"),
code("""print((R / "summary.txt").read_text())"""),
code("""rows = list(csv.DictReader(open(R / "decide_all.csv")))
by = collections.defaultdict(list)
for r in rows: by[r["rule"]].append(r)
ok = sum(any(r["ok"] == "True" for r in rs if r["K"] != "pre") for rs in by.values())
print(f"certified at some K: {ok} of {len(by)}")
fails = collections.Counter((r["K"], r["clause"]) for r in rows if r["K"] != "pre" and r["ok"] == "False")
print("failing (K, clause) counts:", dict(fails))
print("an example of a late-clean highway:")
for r in by["RRLLRRLLLRLR"][:6]: print(" ", r["K"], r["ok"], r["clause"], r["detail"][:60])"""),
md("## Controls"),
code("""print((R / "controls_c1_c3.txt").read_text())
c5 = (R / "c5_nonhighway.txt").read_text().splitlines()
print("C5 non-highway rules:", len(c5) - 1, "; last line:", c5[-1])
v = (R / "verify_from_zero.txt").read_text().splitlines()
print("plain loop vs reference::Ant from step 0:", v[-1])"""),
md("""## Lean soundness theorem
`Sweeper.cycler` (file `lean/Cycler.lean` of the sweeper experiment), generic rule, all `k`; axioms from the fresh audit:"""),
code("""for l in (ROOT / "experiments/archive/2026-10-rlrlll-macro-transition/results/c3_l5_axioms.txt").read_text().splitlines():
    if any(w in l for w in ("cycler", "rect_mid", "grun_agree", "forever")): print(l)"""),
md("""## What this shows, and what it does not
- All 571 census highways in `confirmed_v2.csv` receive a certificate at some snapshot (568 at K = 3); no pre-onset snapshot and none of 72,864 candidate periods in 100 non-highway rules does; the controls reject; the Python ant equals `reference::Ant` on every dump.
- The census label is therefore upgraded, for these rules and from the snapshot on, from trace periodicity to configuration-level persistence, *given* the true configuration (plain simulation) and the Lean model of the ant.
- Not shown: entry (reaching the snapshot is simulation), rules outside the 571, that the abstract Lean ant is the Rust ant (only empirical agreement), or that the instance checks (a)-(d) are replayed in Lean (they are computed by Python).
- The certificate is conservative: it also asks the untouched window cells to be shift-periodic, so a failure does not refute a highway (some rules fail at small K and pass later)."""),
]
nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
out = Path(__file__).resolve().parents[1] / "notebook.ipynb"
nbf.write(nb, out)
print("wrote", out)
