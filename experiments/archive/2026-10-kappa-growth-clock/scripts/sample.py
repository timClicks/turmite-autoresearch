"""Generate the registered cohort; refuses to replace a different manifest."""
from pathlib import Path
import csv
import hashlib
import io
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SEED = 2026101607
OUT = EXP / 'results'
OUT.mkdir(exist_ok=True)
previous = ROOT / 'experiments/archive/2026-10-kappa-leadrun-fresh/results'
inputs = [previous / 'rules.txt', previous / 'mutant_specs.txt']
excluded = {s.split('@')[0] for p in inputs for s in p.read_text().split()}
rng = np.random.default_rng(SEED)
rows, seen = [], set()
while len(seen) < 16:
    suffix = ''.join(rng.choice(list('LR'), 9))
    rules = ['R' * k + 'L' + 'R' * (4-k) + suffix for k in range(1,5)]
    if suffix in seen or any(r in excluded for r in rules):
        continue
    family = len(seen)
    seen.add(suffix)
    for k, rule in enumerate(rules, 1):
        rows.append(dict(family=family, suffix=suffix, lead=k, rule=rule))
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=list(rows[0]), lineterminator='\n')
w.writeheader(); w.writerows(rows)
specs = [f"{r['rule']}@{seed}" for r in rows for seed in range(202610160701,202610160705)]
outputs = {'cohort.csv': buf.getvalue(), 'specs.txt': '\n'.join(specs)+'\n',
           'spot_specs.txt': '\n'.join(specs[:4])+'\n'}
outputs['sampling.json'] = json.dumps(dict(seed=SEED, patch_seeds=[202610160701,202610160704],
    excluded_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}), indent=2)+'\n'
for name, value in outputs.items():
    p = OUT / name
    if p.exists() and p.read_text() != value:
        raise RuntimeError(f'Refusing to replace different {p}')
    p.write_text(value)
print(f'{len(rows)} rules, {len(specs)} specs; seed {SEED}')
