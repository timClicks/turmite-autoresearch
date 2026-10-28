# /// script
# dependencies = ["nbformat"]
# ///
"""Writes notebook.ipynb (unexecuted); execute with the nbconvert command in experiments/README.md.
usage (repo root): uv run experiments/archive/2026-10-kappa-square-loop/scripts/build_notebook.py"""
from pathlib import Path
import nbformat as nbf

EXP = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# kappa and the square-loop trap (H-loop): a test that failed

## Question and why it matters
Why does a longer opening same-letter run ("lead") raise kappa = (B/S)/(P/A) at fixed area? Hypothesis H-loop: an all-R lead traces 2x2 loops on young (colour < lead) frontier cells, so the ant spends more frontier time circling at the boundary. Parent: `../2026-10-kappa-leadrun-fresh/` (lead effect +0.152 ln-kappa per step on 176 stationary fresh rules). See `README.md` (registered predictions P1-P4, C1-C3) and `NOTEBOOK.md`.

## Assumptions and definitions
- Loop step: the ant's position equals its position 4 steps earlier and the last four turns are the same letter (a 2x2 lap). Lead-colour loop: all four cells read had colour < lead. Boundary/interior: the probe's boundary step. Window: probe-CSV k = 26 (t_end 2^26), the window of the parent's kappa.
- Frozen before any loop data (NOTEBOOK 21:58): the deciding mediator is the *interior-only* loop-step rate (a boundary-based mediator is nearly an identity with B/S); pass = b1/b0 <= 0.5, ratio CI upper < 0.8, g > 0; reliability rule ICC(1) >= 0.5.
- **This cohort is the one in which the lead effect was found**: mediation here is legitimate but not a replication."""),
md("## Provenance"),
code("""import hashlib, subprocess, datetime, json
from pathlib import Path
import numpy as np, polars as pl
SEED = 20261016; np.random.seed(SEED)
root = Path.cwd()
while not (root / "AGENTS.md").exists():
    assert root != root.parent, "repo root not found"; root = root.parent
R = root / "experiments/archive/2026-10-kappa-square-loop/results"
for f in ["analysis.txt", "analysis.json", "loops_per_rule.csv", "c3_pairs.csv", "run_cohort.log", "run_mutants.log"]:
    print(f"{f:20s} {hashlib.sha256((R / f).read_bytes()).hexdigest()[:16]}")
print("git", subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip(), "seed", SEED, datetime.date.today())
print((R / "run_cohort.log").read_text())"""),
md("""## Method
Rust sampler `examples/kappa_square_loop_sampler.rs` (copy of the `probe_walker` stepping loop plus loop counters), tested against `probe_walker` and a store-the-whole-path reference (`tests/kappa_square_loop.rs`: 300 ant + 256 walker proptest cases, blank-board traps, PersistentWalk against exact q^4+(1-q)^4, rotor = exactly 0, 1 vs 6 threads byte-identical). Cohort: 300 rules x seeds 601..608 to 2^27; analysis `scripts/analyse_loops.py` (run once). This notebook reads only the committed outputs."""),
md("## Results 1: P2 (loops vs lead) and retention"),
code("""txt = (R / "analysis.txt").read_text()
print(txt.split("=== Reliability")[0])"""),
md("""**Shows:** the total loop-step fraction is large (16-26% of all steps) but is not monotone in lead (lead 3 < lead 2) and its within-area-tertile Spearman with lead is +0.50, +0.40, +0.17 (registered: > 0.5 in each). P2 failed, so by the registered logic H-loop is dead at this scale. **Does not show:** that the lead-colour laps are absent: they rise monotonically with lead (1e-5 to 1.6% of steps) but are too rare to matter in this window."""),
md("## Results 2: reliability, P3 and C1 mediation"),
code("""print("=== Reliability" + txt.split("=== Reliability")[1].split("=== C2")[0])"""),
md("""**Shows:** the loop rate is a nearly deterministic property of the rule (ICC 1.0), so the null mediation is not a noise artefact. Adding the interior loop rate leaves the lead coefficient at 0.957 of its value (needed <= 0.5), also on leads 1-4 (0.98), under log/rank transforms, and for the lead-colour loops alone the sign is wrong (ratio 1.13). Only the boundary-based loop rate (accounting: nearly B/S by construction) removes part of it (0.73). **Does not show:** that no loops of another shape (period 6/8) matter; the lead effect itself remains unexplained."""),
md("## Results 3: P4 (boundary concentration) and C3 (mutants)"),
code("""print("=== C2" + txt.split("=== C2")[1])
p = pl.read_csv(R / "c3_pairs.csv")
print(p.group_by("arm").agg(n=pl.len(), mean_dM=pl.col("dM").mean(), mean_d=pl.col("d").mean()).sort("arm"))"""),
md("""**Shows:** loops are not concentrated on boundary steps (median ratio 0.78, registered >= 2) and the mutant link is weak (Spearman 0.22 < 0.3, 154 pairs, unpowered). **Does not show:** anything causal; the surgery experiment was not run because P2 failed."""),
code("""t = pl.read_csv(R / "loops_per_rule.csv", comment_prefix="#").filter(pl.col("stationary"))
print(t.group_by("lead").agg(n=pl.len(), frac_all=pl.col("frac_all").mean(), frac_lead=pl.col("frac_lead").mean(), M_int=pl.col("M_int").mean(), P4=pl.col("p4").median()).sort("lead"))
a = json.loads((R / "analysis.json").read_text())
assert not a["P2"]["held"] and not a["P3"]["pass_main"] and not a["C1"]["held"] and not a["P4"]["held"] and not a["C3"]["held"]
print("verdicts agree with README: P2, P3, C1, C2, P4, C3 all FAILED; reliability ICC", round(a["reliability"]["icc"], 3))"""),
md("""## Caveats and controls
- Same cohort that produced the lead effect; retention falls with lead (kept 37, 32, 35, 31, 28, 20 of 50), so leads 5-6 are the most selected; P3 on leads 1-4 gives the same answer.
- Window labelling: the probe CSV's k is log2(t_end); the analysis uses that convention (NOTEBOOK 22:36).
- Positive controls: the sampler reproduces the parent's probe rows on all 14509 rows and the exact PersistentWalk values; negative control: rotor has exactly zero loop steps (a theorem).
- Registered thresholds are my design choices; none were changed after seeing data. Mutant C3 is unpowered.

## What this changes / next steps
H-loop (as stated) is rejected for this cohort and window. Remaining open: mixed-turn period-6/8 loops, loops in the opening transient, a different outcome than B/S (e.g. kappa's P/A factor), and whether the lead effect is a rule-composition effect the loop statistic only proxies.

## Open questions
Why is the generic same-turn loop rate 16-26% at every lead and nearly seed-independent? What does carry the lead effect, given that the interior loop rate, lead-colour laps and (by earlier work) R-count do not?"""),
]
nb = nbf.v4.new_notebook(); nb.cells = cells
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbf.write(nb, EXP / "notebook.ipynb")
