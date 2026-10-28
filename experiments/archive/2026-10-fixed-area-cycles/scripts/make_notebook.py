"""Build the shareable scaffold from the repository notebook template."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def main():
    nb = json.loads((ROOT / 'experiments/_template/notebook.ipynb').read_text())
    target = EXP / 'notebook.ipynb'
    if target.exists():
        raise SystemExit('Notebook already exists; edit it in place rather than overwriting work.')
    texts = [
        ('markdown', '''# Fixed-area sampling with cycle accounting

## Question and why it matters
Does the interior excursion tail predict boundary activity at matched visited
area, and does interior return time carry the difference? This notebook is a
scaffold, not a report of measurements. See [README](README.md), [PLAN](PLAN.md),
[lab notebook](NOTEBOOK.md), and [research context](../../../notes/cutoff-research-avenues-2026-10-15.md).

## Assumptions and definitions
Boundary labels are measured before each step on the evolving ever-visited
region. Area bands begin/end at first area hits. Clipped episode intersections
must cover every measured step. The selected T1b cohort is not representative
of all rules; proposed seed freshness, runtime and tail precision are untested.
'''),
        ('markdown', '## Provenance\nPrint committed context and hashes of all inputs read below. No raw dumps are read.'),
        ('code', '''from pathlib import Path
import datetime, hashlib, json, subprocess

SEED = 20261016  # candidate analysis seed; no random operations in this scaffold
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents]
            if (p / 'Cargo.toml').exists() and (p / 'experiments').is_dir())
EXP = ROOT / 'experiments/archive/2026-10-fixed-area-cycles'
CONFIG = EXP / 'config.draft.json'
RESULT = EXP / 'results/analysis.json'
INPUTS = [CONFIG] + ([RESULT] if RESULT.exists() else [])
print('git', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
print('UTC', datetime.datetime.now(datetime.timezone.utc).isoformat(), 'candidate seed', SEED)
for p in INPUTS:
    print(p.relative_to(ROOT), hashlib.sha256(p.read_bytes()).hexdigest())
cfg = json.loads(CONFIG.read_text())
print('Protocol status:', cfg['status'])
'''),
        ('markdown', '''## Data and method
Implementation, controls, pilot and preregistration are pending. Candidate bands,
seeds and budgets appear below; they are not a frozen protocol. Heavy computation
will live in the sampler and scripts, not this notebook. The final notebook must
read only small committed results and list their hashes in the provenance cell.
'''),
        ('code', '''print('Candidate area bands:', cfg['area_bands'])
print('Step cap:', cfg['step_cap'], '| grid side:', cfg['grid_side'])
print('Unresolved primary estimand:', cfg['primary_tail_estimand'])
'''),
        ('markdown', '''## Results
No measurements have been made for this experiment. Do not interpret scaffold
settings as observations, or substitute prior experiments' results here.
'''),
        ('code', '''if not RESULT.exists():
    print('NOT RUN: results/analysis.json does not exist.')
else:
    raise RuntimeError('Results now exist: replace this scaffold cell with schema-validated tables and interpretations.')
'''),
        ('markdown', '''## Caveats and controls
Area-band censoring can preferentially omit long excursions. Fixed area does not
fix shape or age. Exact cycle reconstruction is an identity, not an explanatory
fit. Repeated bands share trajectories. Prior typical-excursion and edge-dwell
nulls must be reconciled, and the earlier noise-floor gate remains failed.
Oracle comparisons, synthetic episode strings, rotor and random-walk controls,
and a precision/coverage pilot are required before ant outcome analysis.

## What this changes / next steps
This scaffold makes definitions and unresolved decisions explicit; it establishes
no new scientific result. Follow [HANDOFF](HANDOFF.md) in order: instrument and
oracle tests, controls, pilot, frozen registration, production, analysis.

## Open questions
Can narrow area bands support reliable tail estimates within budget? Is the
association still present at fixed area? Does interior tail time carry predictive
information beyond geometry and boundary residence on independent trajectories?
'''),
    ]
    cells = []
    for i, (kind, text) in enumerate(texts):
        cell = {'cell_type': kind, 'id': f'fixed-area-{i}', 'metadata': {},
                'source': text.splitlines(True)}
        if kind == 'code':
            cell.update(execution_count=None, outputs=[])
        cells.append(cell)
    nb['cells'] = cells
    nb['nbformat_minor'] = 5
    target.write_text(json.dumps(nb, indent=1) + '\n')


if __name__ == '__main__':
    main()
