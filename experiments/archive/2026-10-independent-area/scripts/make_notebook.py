"""Create the shareable notebook; execute it separately with nbconvert."""
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]


def md(s):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': s.splitlines(True)}


def code(s):
    return {'cell_type': 'code', 'metadata': {}, 'source': s.splitlines(True), 'outputs': [], 'execution_count': None}


cells = [md('''# Independent-area replication
## Question and why it matters
Does the excursion-cutoff association survive area matching from separate seeds?
See [registration](README.md) and [scientific context](../../../notes/open-questions-hypotheses.md).
## Assumptions and definitions
Seed modulo 3 defines three disjoint trajectory groups. At least two surviving
seeds per group are required. Independence between seeds is assumed, not tested.
Matching noisy area does not fix true area; escaping trajectories are excluded.
'''), md('## Provenance\nInputs are small results files; no dumps are read.'), code('''import hashlib, json, subprocess, datetime
from pathlib import Path
SEED = 20261015
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'Cargo.toml').exists())
EXP = ROOT / 'experiments/archive/2026-10-independent-area'
INPUTS = [EXP / 'results/analysis.json', ROOT / 'experiments/archive/2026-10-t1-excursion-tomography/results/t1b_cutoff_seeds.csv']
print('git', subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip())
print('UTC', datetime.datetime.now(datetime.timezone.utc).isoformat(), 'seed', SEED)
for p in INPUTS:
    print(p.relative_to(ROOT), hashlib.sha256(p.read_bytes()).hexdigest())
d = json.loads(INPUTS[0].read_text())
assert hashlib.sha256(INPUTS[1].read_bytes()).hexdigest() == d['input_sha256']
print('Producing commit', d['commit'], 'command', d['command'])
'''), md('''## Data and method
Reuse k=22 and 25, excluding escapes. All six permutations assign separate groups
to area matching, kappa and cutoff. Average the six concordance fractions equally.
Bootstrap rules 2000 times with seed 20261016; never bootstrap pairs independently.
Heavy analysis: `scripts/analyse.py`. The bootstrap seed is analysis seed + 1.
## Results
'''), code('''print('Synthetic controls:', d['controls'])
for r in d['windows']:
    print('k', r['k'], 'tolerance', r['tolerance'], 'rules', r['n_rules'],
          'concordance', round(r['concordance'], 3),
          'CI', [round(x, 3) for x in r['bootstrap95']], r['verdict'])
    print('Role pair counts:', [x['pairs'] for x in r['roles']])
'''), md('''The registered concordance threshold and interval criterion hold at both windows.
This does not establish causality or constitute validation on new rules.
## Caveats and controls
Synthetic null and negative-association controls pass. They calibrate signs and
role handling, not scientific confounding. Area is noisy, rules are selected,
and escape exclusion can select outcomes. Windows share trajectories; intervals
are marginal. No rotor or random-walk growth estimator was changed.
## What this changes / next steps
The shared-trajectory area-matching confound cannot suffice to explain this signal.
The earlier seed-noise gate remains failed. Next obtain new trajectories matched
in size and design an intervention with power for the small residual effect.
## Open questions
Does the association persist at truly fixed area? Is the cutoff causal, or a
second response to an unmeasured property of the field?
''')]
nb = {'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}}, 'nbformat': 4, 'nbformat_minor': 5}
for i, cell in enumerate(cells):
    cell['id'] = f'cell-{i}'
(EXP / 'notebook.ipynb').write_text(json.dumps(nb, indent=1) + '\n')
