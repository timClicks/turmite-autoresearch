# /// script
# dependencies = ["nbformat"]
# ///
"""Builds notebook.ipynb. usage: uv run experiments/2026-10-20-rlrlll-macro-transition/scripts/build_notebook.py
Execute: uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace \\
    experiments/2026-10-20-rlrlll-macro-transition/notebook.ipynb"""
from pathlib import Path

import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# RLRLLL's column sweeper is a checked macro-transition

## Question
After ~1.27e10 steps from a blank board, `RLRLLL` stops growing as a blob and sweeps up and down, laying a period-3 wake and
moving west. Simulation can only show that this continues for a finite time. Is there a finite family of configurations
`C(m, q)` (bulk height `m`, phase `q`) that the rule maps into itself, `C(m, q) -> C(m + g, q + 1)`, for **every** `m`?
If so, the sweeper is proved to continue forever and its asymptotics become exact.

## Assumptions and definitions
Blank board, ant at the centre heading north, update order of `src/reference.rs`. Front = minimum visited x; a cycle ends
each time the front has moved 3 more columns west. Predictions P1-P5 were registered in the README (commit `4bc029a`)
before any run. The proof claim is judged by a separate checker (`examples/rlrlll_macro_transition_check.rs`) whose
every concrete step is a `reference::Ant` step; a symbolic band of identical rows is crossed only by a *shift lemma*,
a finite run on the band's block plus a few neighbouring rows that must reproduce itself one block further on."""),
code("""import hashlib, subprocess
from pathlib import Path
import numpy as np
import polars as pl
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
R = ROOT / "experiments/2026-10-20-rlrlll-macro-transition/results"
for n in ["cycles.csv", "cycles_early.csv", "canonical_k0.txt", "check_k0.txt", "check_negative_controls.txt"]:
    print(hashlib.sha256((R / n).read_bytes()).hexdigest()[:16], n)
print("git", subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip())"""),
md("## Stage 1: the measured cycle law (P1-P3, P5)"),
code("""d = pl.read_csv(R / "cycles.csv")
T, L, reach = d["steps"].to_numpy(), d["L_prev_col"].to_numpy(), d["reach"].to_numpy()
beta = T - 12 * L
print("cycles:", d.height)
print("T - 12 L values:", dict(zip(*np.unique(beta, return_counts=True))), " period 3:", bool(np.all(beta[3:] == beta[:-3])))
print("growth L_(k+1) - L_k values:", dict(zip(*np.unique(np.diff(L), return_counts=True))))
print("max reach behind the front:", reach.max())
ax = np.abs(d["x_f"].to_numpy()).astype(float)
slope = np.diff(ax**2) / T[1:]
for idx in np.array_split(np.arange(len(slope)), 5):
    print(f"  |x| ~ {ax[1:][idx].mean():7.0f}: d|x|^2/dt = {slope[idx].mean():.4f}")"""),
md("""Every cycle obeys `T = 12 L + beta` exactly with `beta` cycling through three values; every cycle adds exactly 2 rows;
the ant never reads more than 20 columns behind the front. The local slope of `|x|^2` against `t` is still falling at
the board edge: the earlier fit of 0.8634 was not an asymptote.

## The proposed family
Read off snapshots 0-2 (cells: colour digits, `.` never visited; the ant is at the front column, 6 or 7 rows below the
top). Only phase 0 is shown, cropped to 26 columns."""),
code("""txt = (R / "canonical_k0.txt").read_text().splitlines()
start = next(i for i, l in enumerate(txt) if l.startswith("phase 0"))
for l in txt[start:start + 50]:
    print(l[:26] if not l.startswith(("phase", "top", "bulk", "bottom")) else l)"""),
md("## Stage 2: the checker's verdict"),
code("""print((R / "check_k0.txt").read_text())"""),
code("""print((R / "check_negative_controls.txt").read_text())"""),
md("""For each phase, `C(m, q)` maps to `C(m + 2, q + 1)` in `12 m + b_q` steps for every even `m >= 2`. Two lemmas carry the
induction over the bulk: down at 20 steps per 2 rows, up at 4 steps per 2 rows, so 12 steps per bulk row. The 27
brute-force runs agree, and both negative controls are rejected (one changed bulk cell, and the wrong rule).

## Consequence for the actual run"""),
code("""m0 = 434
b = np.array([934, 1058, 898])
k = np.arange(len(T) - 1)
pred = 12 * (m0 + 2 * k) + b[k % 3]
print("measured cycles reproduced exactly:", int((T[1:] == pred).sum()), "of", len(k))
e = pl.read_csv(R / "cycles_early.csv")
print("early probe: first cycle at front x =", e["x_f"][0], "with column height", e["L_prev_col"][0],
      "; T - 12 L values", sorted(set((e["steps"] - 12 * e["L_prev_col"]).to_list())))"""),
md("""Snapshot 0 is `C(434, 0)`, so given that one 1.27e10-step simulation, the blank-board `RLRLLL` ant never builds a
highway: it sweeps forever, with `|x|^2 / t -> 9/12 = 3/4`.

## What this does not show (caveats)
- **Entry.** Why the blob produces the sweeper is open. The early probe shows the law already holds when the front first
  passes the old blob edge (height 226); extrapolating puts the wedge's apex inside the blob, where the background is not
  blank and the family does not apply.
- **Trust.** The base case is one run of an uncertified plain loop (consistent with an independent run's exit step).
  The checker is ~640 lines of Rust, not a proof assistant; brute force and negative controls test it but do not prove it.
- **Explanation.** The check certifies the period-3 wake and the bulk row `14435435...`; it does not say why they arise.
- P4 was tested on 373 sampled boundaries, not all 4,729 (the checker then covers all of them).

## Next
An independent second checker or a Lean/Coq statement of the two lemmas; the same propose-then-check loop on the other
no-highway escapes and on census highways (a "sweeper decider"); a moving-frame trace of where the wedge begins inside the blob."""),
]
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
Path(__file__).resolve().parents[1].joinpath("notebook.ipynb").write_text(nbf.writes(nb))
