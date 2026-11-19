"""Write and execute notebook.ipynb (reads committed results/ only).
uv run --frozen experiments/active/2026-11-late-highway-1e8-board-check/scripts/build_notebook.py"""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

EXP = Path(__file__).resolve().parents[1]
md, code = nbformat.v4.new_markdown_cell, nbformat.v4.new_code_cell
cells = [
    md("""# Late-highway board check for the (1e8, 1e9] decade

## Question and why it matters
The per-decade late-highway yield (Q19 in `notes/open-questions-hypotheses.md`) compares three decades. The two later ones
were rechecked on a 65536 board in October and lost 26 artefacts; the (1e8, 1e9] decade (12/854 = 1.41%) had not been.
This notebook re-runs its 12 highways on bigger boards and scores them by a criterion registered first.
Links: `README.md` (registration, results), `NOTEBOOK.md` (lab notebook), `experiments/archive/2026-10-late-highway-board-check/`.

## Assumptions and definitions
* A highway is *confirmed* on a board iff the run reports the census period, drift (dx, dy) and onset exactly (B2 criterion).
* *Board filler*: escape footprint >= 0.99 G in both directions (frozen from the earlier `classify.py`).
* The tiled backend's CSV equals the dense backend's (tests; checked here by the control `RRLRLR`). Status: held."""),
    md("## Provenance\nPrints the git commit, date and a SHA-256 for every input file. No seeds: blank-board deterministic runs."),
    code("""import hashlib, subprocess, datetime
from pathlib import Path
import polars as pl

ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
EXP = ROOT / "experiments/active/2026-11-late-highway-1e8-board-check"
INPUTS = [EXP / "results/census_rows.csv", EXP / "results/recheck_specs.txt", EXP / "results/classify.txt",
          EXP / "results/yields.txt", ROOT / "experiments/archive/2026-10-late-highway-board-check/results/control_65536.csv",
          *sorted((EXP / "results/recheck_65536").glob("*.csv")), *sorted((EXP / "results/recheck_32768").glob("*.csv")),
          *sorted((EXP / "results/explore").glob("*.csv"))]
assert all(p.exists() for p in INPUTS)
sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
print("git", sha, "| run", datetime.datetime.now().isoformat(timespec="minutes"))
for p in INPUTS:
    print(hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.relative_to(ROOT))"""),
    md("""## Data and method
Rules: the 12 rows with an onset in `experiments/archive/2026-10-census-sweeps/results/sweep_1B.csv` (16384 board),
plus the control `RRLRLR`. Each ran alone from a blank board with budget census onset + 1e8, on a tiled 65536 board
(primary) and a dense 32768 board (cross-check): `bash scripts/recheck.sh` (binary sha256 in the `recheck.log` files)."""),
    code("""KEY = ["period", "dx", "dy", "onset"]
def load(d):
    return pl.concat([pl.read_csv(f, infer_schema_length=None) for f in sorted((EXP / d).glob("*.csv"))], how="vertical_relaxed") \\
        .cast({k: pl.Int64 for k in KEY}, strict=False)
census = pl.read_csv(EXP / "results/census_rows.csv")
r65, r32 = load("results/recheck_65536"), load("results/recheck_32768")
t = census.select("rule", *KEY, "decade", "filler").join(
    r65.select("rule", *[pl.col(k).alias(k + "_65536") for k in KEY], pl.col("width").alias("w_65536")), on="rule", how="left")
t = t.with_columns(confirmed_65536=pl.all_horizontal([pl.col(k).eq_missing(pl.col(k + "_65536")) for k in KEY]))
t = t.join(r32.select("rule", *[pl.col(k).alias(k + "_32768") for k in KEY]), on="rule", how="left").with_columns(
    confirmed_32768=pl.all_horizontal([pl.col(k).eq_missing(pl.col(k + "_32768")) for k in KEY]))
with pl.Config(tbl_rows=20, tbl_width_chars=200, tbl_cols=20):
    print(t.select("rule", "decade", "period", "onset", "onset_65536", "w_65536", "filler", "confirmed_65536", "confirmed_32768"))
print("confirmed on 65536:", t["confirmed_65536"].sum(), "of", t.height)"""),
    md("""## Results
The table shows 11 of 12 census highways reproduce exactly on both new boards; `RLLRRLRLR` has no highway within the budget
on either. It does not show that the 11 are highways on every board (only 16384, 32768, 65536 and, from `confirm`, 8192)."""),
    code("""ctrl = r65.filter(pl.col("rule") == "RRLRLR").select(KEY).row(0)
ref = pl.read_csv(ROOT / "experiments/archive/2026-10-late-highway-board-check/results/control_65536.csv") \\
    .filter(pl.col("rule") == "RRLRLR").select(KEY).row(0)
print("control RRLRLR tiled 65536:", ctrl, "| earlier dense 65536:", ref, "| equal:", ctrl == ref)
print((EXP / "results/yields.txt").read_text())"""),
    md("""The control reproduces exactly, so the tiled run is a valid stand-in for dense here. The corrected yield 11/854 = 1.29%
(10/854 by onset binning) does not differ from the next decades (Fisher p = 0.33, 0.67); it does not exclude a slow decline."""),
    code("""ex = pl.concat([pl.read_csv(f, infer_schema_length=None).cast({k: pl.Int64 for k in KEY}, strict=False).with_columns(board=pl.lit(f.stem.split("_")[-1])) for f in sorted((EXP / "results/explore").glob("*.csv"))], how="vertical_relaxed")
print(ex.select("board", "stop", "steps", "period", "dx", "dy", "onset", "width", "height", "tail_period"))
print("RLLRRLRLR census onsets by board: 8192 -> 763,443,858 (confirm_1B), 16384 -> 822,854,955 (census)")"""),
    md("""`RLLRRLRLR`'s period-4 'highway' has a different onset on every board (8192, 16384, 65536) and does not occur by 1e10 on
262144 or 1048576 (the last two were an unregistered exploratory follow-up). It looks like a ray emitter whose straight
runs end, read as highways only when one reaches the board edge. This is an interpretation, not tested.

## Caveats and controls
* Positive control `RRLRLR` reproduced; `cargo test --release --locked` passed (227 tests).
* P1 (11/11 confirmed) and P2 (RLLRRLRLR not reproduced) held as registered. The artefact had already been flagged by the
  2026-10 `confirm` run (`confirmed_1B.csv`); the 12/854 yield had ignored that flag.
* One extra board size for the score; dependence that appears only above 65536 would not be caught.

## Pruning decisions and reusable negative results
Index revision `6fba1c8`: no matching signatures (README). No new signature: a corrected count is not a dead end.

## What this changes, next steps, open questions
The (1e8, 1e9] yield becomes 11/854 = 1.29% (10/854 by onset). Q19's flat reading stands. Open: what `RLLRRLRLR`'s period-4
runs travel over and why they stop; whether it is the same class as `RLLLRLRRR`."""),
]
nb = nbformat.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                                     "language_info": {"name": "python"}})
NotebookClient(nb, timeout=120, kernel_name="python3", resources={"metadata": {"path": str(EXP)}}).execute()
nbformat.write(nb, EXP / "notebook.ipynb")
print("wrote", EXP / "notebook.ipynb")
