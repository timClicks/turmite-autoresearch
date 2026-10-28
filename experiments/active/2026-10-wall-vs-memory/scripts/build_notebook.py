"""Builds notebook.ipynb for this experiment. usage: uv run --frozen experiments/active/2026-10-wall-vs-memory/scripts/build_notebook.py
Execute (reads committed results only), from the experiment folder:
    uv run --frozen python -c "import nbformat; from nbclient import NotebookClient; nb = nbformat.read('notebook.ipynb', 4); \\
    NotebookClient(nb, timeout=120, kernel_name='python3').execute(); nbformat.write(nb, 'notebook.ipynb')"
"""
from pathlib import Path

import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# Wall or memory: where does the ant's cube root live?

*Claude (AI research agent), 2026-10-26. Shareable write-up of `experiments/active/2026-10-wall-vs-memory/`. The README holds the
registration (committed at `086c1ac` before any code or run) and the lab notebook holds the timeline.*

## Question
Chaotic generalised Langton's ants grow compact territories whose area goes as t^(2/3). The project's original mechanism has
two ingredients: **blank cells repel** (every canonical rule turns R on colour 0, so an ant stepping onto fresh ground curls
back) and **the interior is well mixed**. The ant also has a third property the mechanism did not use: its colour field is a
deterministic memory of past visits, like a rotor router. A memoryless walker with the ant's turn statistics grows as t^0.93
with a porous territory; the rotor and the ant reach 2/3. Which ingredient does the work?

## Design
The walker `hy:RULE:EV:EF:SEED` is the ant with turn noise split by cell type: on a cell the walker stands on for the first
time (fresh) its turn is replaced by a fair R/L coin with probability EF, elsewhere with probability EV. The colour advances
as usual. The four corners:

| | EF = 0 (wall kept) | EF = 1 (wall removed) |
|---|---|---|
| EV = 0 (memory kept) | the ant | **F1**: memory, no wall |
| EV = 1 (memory removed) | **V1**: the hybrid wall walker | memoryless walker `pw:0.5` (exactly) |

Two explanations were registered. H-wall: the reflecting fresh ground plus any diffusive interior gives the cube root (V1
compact, F1 porous). H-memory: the deterministic memory balances local times, so the wall is incidental (V1 porous, F1
compact). **My registered prior was H-memory, about 70%.**

## Assumptions and instrument
Blank board, 16384 cells square, start at the centre heading north. `bin/probe` octave windows; a = slope of ln area against
ln t, beta = slope of ln perimeter against ln area, fitted per run over k = 12..22 (early) and k = 20..26 (late), then
averaged. Classes as registered: compact if early a <= 0.78, beta <= 0.65 (and late a <= 0.74 when available); porous if
early a >= 0.85, beta >= 0.80. Six rules drawn at random (seed 20261026) from the census core class, 8 seeds per noisy
condition. The walker is checked against an independent sparse reference and three exact identities
(`tests/hybrid_walker.rs`). Everything below reads committed `results/` only; nothing is simulated here."""),
code("""import hashlib, subprocess
from pathlib import Path
import polars as pl
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
R = ROOT / "experiments/active/2026-10-wall-vs-memory/results"
for n in sorted(p.name for p in R.iterdir() if p.suffix in (".txt", ".csv")):
    print(hashlib.sha256((R / n).read_bytes()).hexdigest()[:16], n)
print("git", subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip())
print((R / "provenance.txt").read_text())"""),
md("""## Calibration gates (Stage 1)
G1: the rotor reproduces its earlier exponents. G2: the EV = EF = 1 corner reproduces the memoryless walker. G3: every
noise-free run reproduces its census row exactly."""),
code("""txt = (R / "analysis.txt").read_text().splitlines()
print("\\n".join(l for l in txt if l.startswith(("G1", "G2", "G3", "gates"))))"""),
md("""## The four corners
Condition means over runs. `esc` counts runs that later reached the board edge; the early window is complete for every run."""),
code("""c = pl.read_csv(R / "conditions.csv")
corner = pl.when((pl.col("ev") == 0) & (pl.col("ef") == 0)).then(pl.lit("ant")) \\
    .when((pl.col("ev") == 0) & (pl.col("ef") == 1)).then(pl.lit("F1: memory, no wall")) \\
    .when((pl.col("ev") == 1) & (pl.col("ef") == 0)).then(pl.lit("V1: wall, no memory")) \\
    .when((pl.col("ev") == 1) & (pl.col("ef") == 1)).then(pl.lit("pw:0.5")).otherwise(None)
pl.Config.set_tbl_rows(40); pl.Config.set_tbl_cols(12); pl.Config.set_float_precision(3); pl.Config.set_tbl_width_chars(160)
print(c.with_columns(corner=corner).filter(pl.col("corner").is_not_null())
       .select("corner", "group", "runs", "escaped", "early_a", "early_beta", "late_a", "late_beta", "class")
       .sort("corner", "group"))
print("\\n".join(l for l in txt if l.startswith(("V1", "F1", "corner"))))"""),
md("""**What this shows.** Randomising the first-departure turn while keeping the colour memory makes the condition mean of every
one of the six ants porous, close to the memoryless walker. The forced turn on fresh ground matters under this
intervention, and my prior was wrong. **What it does not show:** that reflection is the mechanism (a coin flip on first
departure also breaks coherent first-visit loops and heading-colour correlations), or that deterministic R is the only
compact-preserving policy (forced L is untested). Keeping the forced turn with a memoryless interior lands between the
memoryless walker and the ant, an "intermediate" class, so no registered corner reading applies to the pair. The
classification is of condition means: 39 of the 48 individual F1 runs meet the porous thresholds (see the post hoc
section). Seeds are shared across rules, so the independent units are the six rules.

## Dose arms: low-rate noise on one cell type
Shifts of the early area exponent above each rule's noise-free run, at 10% noise on revisited cells (Delta_V) or fresh cells
(Delta_F), and 1% on revisited cells. Both registered dose predictions (one per explanation) failed. Low noise does move the exponent (mean +0.047 revisit, +0.028 fresh at 10%); what did not change is the registered compact classification for fresh-cell noise."""),
code("""print("\\n".join(l for l in txt if "|" in l and l.count("|") == 4 or l.startswith(("dose", "(0.1,0.1)"))))"""),
md("""## Stage 2: does the wall alone reach the cube root?
Registered after Stage 1 (and informed by it): V1 for 16 seeds and the rotor for 8, to 2^31 steps; fit k = 24..30, and the
trend of the local exponent over k = 22..31 with a seed bootstrap."""),
code("""print((R / "stage2_analysis.txt").read_text())"""),
code("""print((R / "posthoc_review.txt").read_text())"""),
md("""The frozen rule reads "separate exponent", but by 0.002 against a between-seed sd of 0.021. A trend interval containing zero
is a failure to resolve a trend, not evidence of a plateau, and a significantly negative trend would not by itself identify
2/3 as the limit. I read Stage 2 as **unresolved**: a finite-window separation of about 0.05 from the rotor, no asymptotic
verdict.

## Post hoc checks added after review (not registered)
Individual-run counts against the porous thresholds, the 10% noise shifts, and the window sensitivity of Stage 2
(`scripts/posthoc_review.py`; refitting V1 over k = 27..31 gives 0.717 against 0.732 at k = 24..30).

![local exponents](results/fig_local_exponents.png)

*Local area exponent per octave (mean, standard error). Late points for F1 and pw:0.5 come from fewer runs, since porous runs
escape the board; the early window used for scoring is complete for all of them. Regenerate with `scripts/figure.py`.*"""),
md("""## Stages 3-3c: what about the fresh-ground turn matters? (registered 2026-10-28, before each run)
Under any deterministic quarter-turn fresh policy a *fresh run* (consecutive steps from never-departed cells) closes a 2x2
block within 4 cells; a reversal U returns at once. Random R/L (F1) is unbounded. Three explanations of Stage 1's result were
registered: **H-bound** (bounded fresh runs are what matter), **H-chiral** (a consistent loop sense) and **H-match** (the
fresh turn must equal the rule's colour-0 turn); Stage 3c added **H-random** (randomness on fresh ground breaks the regime by
itself). Walkers: `ft:RULE:T` (deterministic T in R, L, U on fresh cells) and `fs:RULE:SET:SEED` (uniform draw from SET).
Cohorts: the six Stage 1 rules (3, 3c-A) and 100 new core-class rules (3b, 3c-B). Gates: oracle tests
(`tests/fresh_turn.rs`, `tests/fresh_set.rs`), `ft:RULE:R` equals the ant and `fs:RULE:RL` equals F1, field for field."""),
code("""for n in ("stage3_analysis.txt", "stage3b_analysis.txt", "stage3c_analysis.txt"):
    print(f"==== {n}"); print((R / n).read_text())"""),
code("""b = pl.read_csv(R / "stage3b_runs.csv").select(pl.lit("deterministic").alias("policy"), pl.col("turn").alias("set"), "cls")
c = pl.read_csv(R / "stage3c_runs.csv").select(pl.lit("random").alias("policy"), "set", "cls")
t = pl.concat([b, c]).with_columns(bounded=~(pl.col("set").str.contains("R") & pl.col("set").str.contains("L")))
print(t.group_by("bounded", "policy", "set").agg(runs=pl.len(), compact=(pl.col("cls") == "compact").sum(),
      porous=(pl.col("cls") == "porous").sum(), ordered_or_escape=pl.col("cls").is_in(["escape", "filler"]).sum(),
      intermediate=(pl.col("cls") == "intermediate").sum()).sort("bounded", "policy", "set", descending=[True, False, False]))"""),
md("""**What this shows.** Registered readings: Stage 3 none (forced L split: two runs became one highway), Stage 3b unresolved
(f_L 0.857), Stage 3c unresolved in both cohorts. Per-arm facts that are clean: reversal (no handedness, no colour-0 match)
was compact in 63/63 runs that did not escape, rejecting H-chiral and H-match as registered; bounded random sets were compact in
175/196 with one porous run, rejecting H-random's prediction (f <= 0.5). Unbounded random RLU was compact in 2/148. Note that the
deterministic table above counts Stage 3b's 13 forced-L "intermediate" runs; post hoc they are ordered square-spiral fillers
(A/t constant at 1/10, 1/8, 1/6 or 1/4), not porous walks.

**What it does not show.** That the bound *causes* compactness in general (one class of rules, finite windows), or why the bounded
regime sits at a ~ 0.69-0.74 here. Bounded randomness is not free: it raises early a by about 0.056 over the deterministic ant.
Dead end, exact scope only: `NR-20261028-wall-vs-memory-bounded-random-fresh-compact`."""),
md("""## Caveats
- Six rules from one class (blob, width exponent 0.30-0.37, not bursty); not the census.
- Finite windows: the CSV's k is log2 of the window end, so the early fit (k = 12..22) ends at 2^22 (corrected from 2^23), the late fit at 2^26, Stage 2 at 2^30 with a last window ending at 2^31. Late fits are censored by escapes (18 of 270 stage 1 runs). D3 showed exponent crossovers can be slow.
- In Stages 1-2, "wall" means exactly the ant's fresh-cell turn (R for canonical rules). Stages 3-3c vary it (forced L,
  reversal, random bounded sets); intermediate EF rates between 0.1 and 1 were not run.
- Stages 3-3c: all registered readings were unresolved (thresholds narrowly missed); the summary table is an interpretation.
  The 100 new rules and the six are from one class, selected for compact growth under R, so only the R arm is filtered
  against highways.
- The hybrid is not the ant: its interior is memoryless (it keeps a `departed` flag, so "interior colour-dependent turns
  removed" is more precise than "memory removed"). That randomising the fresh-cell turn breaks the ant does not mean the ant's
  mechanism is the hybrid's, nor that reflection is the cause.
- Six selected rules, 8 shared seeds: 48 trajectories are not 48 independent rule-level replications.
- Timestamps in the README written by hand at registration were estimates; git commit times are authoritative (README
  correction, 23:15 NZDT). The order registration -> code -> run holds.

## Next steps
From the README review addendum (item 9): F-a (forced L) ran as Stage 3, below; F-b is deferred (its excursion length is
bounded by 4 for every deterministic arm); F-c (longer V1/rotor with frozen windows) and F-d (fresh versus colour-zero noise)
are registered, not run. Proposed, not registered (Q33, Q38 and Q39 in `notes/open-questions-hypotheses.md`): a dose curve in the
bound itself (fresh runs bounded by m cells); why forced L crystallises some rules into square-spiral fillers; why the
bounded regime sits at a ~ 0.69-0.74. Older proposals:
- Q30: a dose curve in EF between 0.1 and 1, to find where the reflecting edge fails and whether the loss is sharp.
- Q31: what memory adds on top of the wall. Compare neighbour discrepancies of visit counts (local times) in the ant, the
  rotor and the hybrid.
- Whether V1 converges to 2/3 needs a longer horizon or an argument, not more seeds at 2^31."""),
]
for i, c in enumerate(cells):
    c.id = f"cell-{i:02d}"  # fixed ids: nbformat's random ids make every rebuild differ
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
nbf.write(nb, Path(__file__).resolve().parents[1] / "notebook.ipynb")
print("wrote notebook.ipynb")
