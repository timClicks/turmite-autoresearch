"""Build and execute a small notebook from the committed pilot outputs."""
from pathlib import Path
import nbformat as nb
from nbclient import NotebookClient

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
md, code = nb.v4.new_markdown_cell, nb.v4.new_code_cell
book = nb.v4.new_notebook(cells=[
    md("""# The turn map hides a clock

Can two fields give the ant the same next turn at **every cell**, yet produce
different returns to the boundary? This excluded pilot changes hidden colour
phases once, preserves depth-bin colour counts, and then uses full-memory dynamics.

**Outcome: the registered comparison is unresolved.** P1 failed in two of six
rule/area comparisons; 17 of 24 start/area groups lacked eight long episodes.
The narrower same-map/different-return observation survives. This is not an
occupation forecast or a derivation of cube-root growth."""),
    md("""## Protocol and assumptions

Three rules, four new 5x5-patch seeds each (2026102301–2026102304); area bands
[4096,4352) and [16384,17408). Select the first 16 returns of at least 128 steps,
with the registered gap. Shuffle interior colours within depth/8 bins and shared
future-turn words of length 0, 1, 2, 4, or the entire rule. Four replicas per arm.
Boundary cells and territory stay fixed; cap 2^18.

Preserving k turns prevents path divergence before read k+1 at the first differing
cell. That coupling idea predates this pilot in the c-law renewal record.
The new contribution is a measured histogram-preserving field intervention,
with complete baseline eligibility accounting.

Read README.md for the preregistered thresholds, source links and exact commands."""),
    code("""from pathlib import Path
import hashlib, importlib.util, json
from IPython.display import Markdown, Image, display

root = Path.cwd()
if not (root / 'Cargo.toml').exists():
    root = next(p for p in root.parents if (p / 'Cargo.toml').exists())
here = root / 'experiments/archive/2026-10-hidden-phase-return'
manifest = json.loads((here / 'results/run.done.json').read_text())
for name, digest in manifest['output_hashes'].items():
    assert hashlib.sha256((here / 'results' / name).read_bytes()).hexdigest() == digest
print('Instrument revision:', manifest['revision'])
print('Binary SHA256:', manifest['binary_sha256'])
print('Verified CSV hashes:', len(manifest['output_hashes']))
print(manifest['thread_replication'])
"""),
    code("""spec = importlib.util.spec_from_file_location('pilot_analysis', here / 'scripts/analyze.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
recomputed = module.analyse()
saved = json.loads((here / 'results/analysis.json').read_text())
assert json.loads(json.dumps(recomputed)) == saved
print('Frozen analysis reproduces exactly from saved CSV files.')
display(Markdown((here / 'results/summary.md').read_text()))
"""),
    code("""display(Image(filename=str(here / 'results/phase_effect.png')))
display(Markdown((here / 'results/details.md').read_text()))
"""),
    md("""## What the failed gate means

All 12 starts reached both bands. No baseline overflow, unfinished excursion,
board escape or censored replay occurred. The cap therefore did not truncate
any observed return. The failure is **sparse long-episode support**, not censoring.
Some start means use one episode. Four-start bootstrap intervals have weak
coverage information and no between-rule interpretation. The six area/rule
comparisons are not independent replications.

Each mean gives equal weight to starts, as registered. Long baseline selection
means signed shortening is not an estimate for ordinary departures. Different
prefix lengths change the permitted permutations and their support; ratios are
not fractions of information or additive causal contributions."""),
    code("""witness = json.loads((here / 'results/witness.json').read_text())
row = witness['row']
print(witness['selection'])
print('Rule:', row['rule'], 'seed:', row['seed'], 'departure time:', row['t0'])
print('Return:', row['base_t'], '->', row['arm_t'], 'steps')
print('First split: step', row['split_step'], 'on source visit', row['split_visit'])
print('Source phase words:', witness['split_source_future_turns'])
print('Independent sparse replay:', witness['independent_sparse_replay'])
"""),
    md("""## A counterexample, not a representative effect

The selected 86,030-to-6-step example was checked from the initial patch by a
separate sparse Python implementation (`scripts/check_witness.py`). On the first
read, the relevant phases both say R. On the second, one says L and the other R.
All initial turn directions remain the same. However, 10,418 interior colours
were shuffled; this does not assign the entire effect to one cell.

The exact same-map counterexample concerns edited fields, not necessarily fields
reachable from the natural patched-start distribution. All 640 k=1 replays changed
the path and return tuple, while all 640 full-word controls matched. Whole-field
phase organisation and individual phase values changed together.

## Validation and next decision

The Rust instrument has independent full-path sparse-oracle tests, an equivalent
RLRL-phase control, a known one-step return and a delayed-divergence check.
Live/cropped controls compare exact returns, not every live step. The full CPU
release suite and three known-answer analysis tests passed; all CSV bytes match
at one and three threads. GPU behavior is outside scope.

Stop the pilot as registered. No dead-end signature or family exclusion follows
from a failed support gate. A future design must secure enough long episodes
before confirmation and distinguish single-cell delayed effects from collective
phase organisation. It still needs an independent occupation prediction against
persistence. No such confirmation study is run here."""),
])
book.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
NotebookClient(book, timeout=120, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
nb.write(book, HERE / "notebook.ipynb")
print(HERE / "notebook.ipynb")
