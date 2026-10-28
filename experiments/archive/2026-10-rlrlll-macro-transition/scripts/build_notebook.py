# /// script
# dependencies = ["nbformat"]
# ///
"""Builds notebook.ipynb. usage: uv run experiments/archive/2026-10-rlrlll-macro-transition/scripts/build_notebook.py
Execute: uv run --with nbconvert --with ipykernel --with nbformat jupyter nbconvert --to notebook --execute --inplace \\
    experiments/archive/2026-10-rlrlll-macro-transition/notebook.ipynb"""
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
R = ROOT / "experiments/archive/2026-10-rlrlll-macro-transition/results"
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
md("""## Entry probe (2026-10-21; registered in the README before measuring, but committed together with the results)
`results/entry_backtrack.txt` is the ant's turnaround log (swing >= 40 rows) walked backwards from the first front advance.
Registered outcome: E1a failed (column counts include the old blob) and E1b failed on its swing = L(x) clause, so E1 is
rejected as registered. Post hoc: the ant is on the sweeper clock well before the edge."""),
code("""print(chr(10).join(l for l in (R / "entry_backtrack.txt").read_text().splitlines()
                 if l.startswith(("maxima", "run starts", "all cycles", "swing increments"))))"""),
md("""## Task A: cell-level family membership (2026-10-21; registration committed first as f67d3f4)
Windows of 48 columns at the ant's own front (minimum x since step 12,676,233,000), x = 2 (mod 3), compared with `C(m(x), q(x))`
from `canonical_k0.txt`, `m(x) = 434 + 2(-2197 - x)/3`. Controls (events at -2197..-2203 reproduce `cycles.csv`, match
C(434..438, 0..2) exactly, wrong (q, m) and one-cell perturbations fail) all pass."""),
code("""print(chr(10).join((R / "window_controls.txt").read_text().splitlines()[:2] + (R / "window_controls.txt").read_text().splitlines()[-1:]))
print(chr(10).join(l for l in (R / "window_scan.txt").read_text().splitlines() if l.startswith(("A1", "A2", "A3", "A4", "primary", "secondary"))))
print(chr(10).join(l for l in (R / "window_cone.txt").read_text().splitlines() if l.startswith(("rect", "-1549", "-1552", "-1600"))))"""),
md("""Scored as registered: A1 (clock) held on 51 of 51 pairs; A2 **failed** (0 of 36 pass the registered whole-apron test, because
old blob cells lie outside the rectangle); A3 held, for a different reason than predicted. Post hoc (labelled as such): the
rectangle itself, ant offset and heading match exactly (colour and visited flag, zero nonzero cells in a 3-row light cone out to
320 columns) at 50 of 51 targets, every x <= -1552 (m >= 4); x = -1549 (m = 2) fails on 17 old blob cells inside the rectangle.
**The sweeper is on the closed family from step 12,676,237,591 (C(4, 1), x = -1552), 769,586 steps before the original base
case and 184,176 before the front crosses the blob edge.**

## Task B: below the family (registered before the run)
Same tool from step 12,676,223,500, targets x = -1471 .. -1537."""),
code("""print((R / "window_seed.txt").read_text())"""),
md("""B1 held (21 of 23 targets fire, monotone). **B2 failed**: the clock formula `12 m + c_q`, evaluated at negative `m`, holds exactly
on 9 pairs with m <= -6, down to x = -1510 (m = -24, column height 19, step 12,676,226,047) and fails at x = -1507. The column
heights are 3 (x = -1504), 19 (-1507), 21 (-1510), 23 (-1513): the wedge starts abruptly at height ~19, not at zero, so the
backward extrapolation to an apex at x ~ -1474 was wrong. The "swing 41" floor was my zigzag filter. B3 (sd of dt - 12 L > 10) is
numerically true but uninformative because the pooled pairs include the exact ones. B4 was not run. No cell-level statement is
made for m < 4: the family is undefined there.

Snapshot 0 is `C(434, 0)`, so given that one 1.27e10-step simulation, the blank-board `RLRLLL` ant never builds a
highway: it sweeps forever, with `|x|^2 / t -> 9/12 = 3/4`."""),
md("""## Task C: assurance (2026-10-21; registered in the README first, with a dated correction of two registration errors)
**C1, a second checker.** `scripts/c1b.py` is written from the rule definition and the proposal text only (no `src/`, none of the first
checker's code), with its own ant (`c1_ant.py`) and a different proof architecture: five explicit finite runs (top block -> descent frame,
descent lemma^n, bottom turnaround, return lemma^n, top block -> new front) composed by row bookkeeping. `c1a.py` compares its ant with
`reference::Ant` through a thin Rust driver (a per-step hash of position, colour read and heading)."""),
code("""for n in ["c1a_conventions.txt", "c1a_semantics.txt", "c1b_verify.txt"]:
    print("== " + n)
    print(chr(10).join(l[:230] for l in (R / n).read_text().splitlines()))"""),
md("""The conventions test finds that two of four heading conventions close the cycle (the same ant under two labelings) and the mirror ants close
none. My ant agrees with `reference::Ant` at every one of 1,000 checkpoints of a 1e6-step blank-board run and on 12 window cycles; two
deliberately wrong rules (`RLRRLL`, `LLRLLL`) disagree from the first checkpoint. The second checker reproduces the first one's constants
exactly: `12 m + 934 / 1058 / 898`, descent lemma 20 steps per 2 rows, return lemma 4 steps per 2 rows, valid for every even `m >= 2`, and
150 brute-force cycles (m = 2..100, three phases) agree. It uses smaller frames (H = 1) because it cuts at the ant's arrival on a row."""),
code("""for n in ["c1b_control_mut46.txt", "c1b_control_rlrllr.txt", "c1_controls.txt"]:
    print("== " + n)
    print(chr(10).join(l[:200] for l in (R / n).read_text().splitlines() if not l.startswith("  S5 with")))"""),
md("""Controls: a bulk cell changed in a column the ant never reads (trajectories identical) is rejected in all three phases at the composition
equality, like the first checker. `RLRLLR` is rejected in all three phases, but at a different place (the finite top-block run leaves its patch)
than the first checker's "left the strip" / "segment counts differ"; I score that control as split, not held (README).

**C2, the cone margin.** Per-cycle reach of the family's ant, from the finite runs and from 150 brute-force cycles, then the exact base-case
criterion: the real configuration at each of Task A's 50 events must equal the ideal initial configuration on every cell the ideal ant ever
stands on."""),
code("""print((R / "c2_reach.txt").read_text())
print(chr(10).join(l[:330] for l in (R / "c2_recheck.txt").read_text().splitlines()[:4] + (R / "c2_recheck.txt").read_text().splitlines()[-2:]))
print((R / "c2_control.txt").read_text())"""),
md("""Registered C2a (at most 1 row per side) **failed**: a cycle visits up to 2 rows above its rectangle (phase 0). The rectangle's top moves up
2, 0, 1 rows per phase and its bottom down 1 per phase, so the wedge is 1 row per cycle per side. The exact criterion passes in all 50
windows (about 3e4 to 4.5e4 visited cells each, no mismatch), which confirms the base case without any observed margin. But **Task A's cone
(3 + s//3 rows) was too small**: every window has visited cells outside it, by up to 7 rows above, because a cycle's rows are visited up to 18
columns east of its front. Task A's cone test was not a sufficient certificate; the exact criterion is. One premise is not re-derived
here: nothing the real run visited lies west of x = -1820 (checked in the dumps for rows -2000..-1 and the apron, taken from the tracer's front
record elsewhere).

**C3, Lean 4.** `lean/` (core library only, no Mathlib): a list-of-rows model of the ant, a frame lemma (a run inside a patch extends to any
surrounding rows), and the two shift lemmas as iteration theorems for all `n`, instantiated for q = 0, 1, 2 from six finite certificates checked by
`decide +kernel`. No `sorry`; axioms propext and Quot.sound only."""),
code("""print((R / "c3_axioms.txt").read_text())
print(chr(10).join(l for l in (R / "c3_build.txt").read_text().splitlines() if l.startswith(("Build", "BUILD", "Lean", "#"))))"""),
md("""**L4 continuation, 2026-10-22.** The earlier C3 log above is preserved. The end runs and composition are now checked too,
at implementation `f90733c412c95029da2eafeaa8923a69339bc2a6`. `Bounded.lean` checks every pre-step x in [-2,47], while permitting
the final arrival at -3. `IterB.lean` proves the bounded band inductions. `L4Data.lean` contains nine kernel-decided S1/S3/S5
certificates (387/383/383, 216 each, 355/483/323 steps) and six bounded descent/return certificates. `Cycle.lean` composes the five
stages for all n; `cycle0/1/2` and `cycle_runN0/1/2` prove the clocks 12m + 934/1058/898 for every m = 2+2n.
`composition0/1/2` prove the next-phase grid identity for all n by list algebra, and `first_arrival0/1/2` plus `target_ant0/1/2`
give first arrival at column -3 and the next ant state. These are single-cycle theorems in the finite list-of-rows model.

Reproduce: `bash experiments/archive/2026-10-rlrlll-macro-transition/scripts/l4_check.sh` under WSL, with the uv environment in the README.
The script regenerates proposed rows, uses a fresh build directory, and records hashes and the axiom audit. No new measurements or seeds."""),
code("""for name in ["c3_l4_build.txt", "c3_l4_axioms.txt"]:
    raw = (R / name).read_bytes()
    print(name, "sha256", hashlib.sha256(raw).hexdigest())
    lines = raw.decode().splitlines()
    if name.endswith("build.txt"):
        print(chr(10).join(lines[:4] + lines[-3:]))
    else:
        assert "sorryAx" not in raw.decode() and "Lean.ofReduceBool" not in raw.decode()
        print(chr(10).join(line for line in lines if any(
            key in line for key in ["s1_cert", "s3_cert", "s5_cert", "composition", "cycle0", "cycle1", "cycle2", "first_arrival", "target_ant"])))"""),
md("""**Multi-cycle padding remains open.** The output comparison has 12/14/13 blank rows above the target rectangle and 13 below,
where the next input asks for 14 on both sides. Shifting/cutting the finite rows and adding new western blank context is a defined
comparison operation, not a proved infinite-board extension. No Lean proof of padding replenishment or indefinitely many cycles exists here.

## What this does not show (caveats)
- **Entry.** The cell-level family holds from step 12,676,237,591 (x = -1552, m = 4); the clock formula extends exactly to x = -1510 (m = -24, column height 19, step 12,676,226,047); before that the log is irregular. The wedge starts at height ~19-21, not zero (the apex extrapolation was wrong). Not shown: what inside the blob corner produces that first column, and a cell-level description for m < 4. The old-blob cells outside the rectangle are excluded by a 3-row light-cone margin chosen from the observed growth, not derived from the checker. E1 (registered) was rejected as scored; A2 and B2 also failed as registered.
- **Trust.** The base case is one run of an uncertified plain loop (consistent with an independent run's exit step); the second checker
  did not re-run it. Two checkers (Rust, Python) by one author agree on every constant. Lean now checks bounded single cycles and composition
  for all `n`; infinite-plane lifting, multi-cycle padding and a model-correspondence theorem to Rust remain open.
- **Explanation.** The check certifies the period-3 wake and the bulk row `14435435...`; it does not say why they arise.
- P4 was tested on 373 sampled boundaries, not all 4,729 (the checker then covers all of them).

## Next
Lean cycle-to-cycle padding and infinite-plane lifting; the same propose-then-check loop on the other
no-highway escapes and on census highways (a "sweeper decider"); an explanation of the clock at m < 2, and what at the NW blob corner seeds the first column."""),
]
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
Path(__file__).resolve().parents[1].joinpath("notebook.ipynb").write_text(nbf.writes(nb))
