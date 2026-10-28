"""Create the shareable notebook; execute it separately under uv/nbconvert."""
from pathlib import Path
import json

EXP=Path(__file__).resolve().parents[1]
cells=[]


def md(s):
    cells.append(dict(cell_type='markdown',metadata={},source=s.splitlines(True)))


def code(s):
    cells.append(dict(cell_type='code',metadata={},execution_count=None,outputs=[],source=s.splitlines(True)))


md('''# Question and why it matters
Does opening-run length predict late boundary occupation after adjusting for the
area reached in that same window? Earlier area is a post-treatment variable and
may leave growth-history confounding. See [registration and results](README.md)
and [mechanism context](../../../notes/kappa-mechanisms-2026-10-15.md).
''')
md('''## Assumptions and definitions
Kappa = (B/S)/(P/A), where B counts steps starting on visited boundary cells and
P counts visited cells with an unvisited four-neighbour. All quantities use the
probe's octave windows. Conditioning on area is descriptive and cannot estimate
a causal direct effect. Constant composition does not distinguish leading-run
length from first-L position. CPU/GPU equivalence is checked before the sweep.
''')
code('''from pathlib import Path
import hashlib, json
SEED = 2026101608
root = Path.cwd().resolve()
while not (root / 'Cargo.toml').exists():
    if root == root.parent:
        raise RuntimeError('Repository root not found')
    root = root.parent
exp = root / 'experiments/archive/2026-10-kappa-growth-clock'
paths = [exp / 'results' / s for s in ['analysis.json', 'cohort.csv', 'windows.csv', 'registration.md', 'spot-check.txt']]
for p in paths:
    assert p.is_file(), p
    print(str(p.relative_to(root)), hashlib.sha256(p.read_bytes()).hexdigest())
report = json.loads(paths[0].read_text())
print('Seed:', SEED, 'Simulation base commit:', report['git'])
print('Run commit:', (exp / 'results/run-commit.txt').read_text().strip())
print('Date: 2026-10-16 +13:00; exact raw/source hashes are in analysis.json and run-sources.sha256')
''')
md('''## Data and method
Sixteen nine-letter suffixes each supply four 14-letter rules with leading runs
1..4; all rules in a family have equal composition. Four patch seeds per rule,
2^24 steps, grid 4096. Primary k=23, secondary k=21,22; early area is A18.
No stationarity or exponent filtering. Require three completed seeds per rule
and twelve complete families. OLS area controls use training-fitted spline
hinges. Prediction uses leave-one-family-out folds. Uncertainty resamples whole
families. The heavy computation lives in scripts/run.sh and scripts/analyse.py;
this notebook reads only published results and makes no new estimates.
''')
code('''print('Runs:', report['runs'], 'Escaped:', report['escaped'])
print((exp / 'results/spot-check.txt').read_text().strip())
print((exp / 'results/cpu-replay-check.txt').read_text().strip())
print(json.dumps(report['calibration'], indent=2))
print('Attrition:', report['status_counts'])
''')
md('''## Results
The early and current slopes use the same response and rules, changing only the
area-control window. P1 requires the current slope to retain half the early slope
and have a positive interval. P2 requires gain >=0.05 and a positive interval.
''')
code('''for r in report['windows']:
    print('Window', r['k'], 'families', r['complete_families'], 'retention', r['qualifying_by_lead'])
    if not r['gate_passed']:
        print(r['verdict']); continue
    print('Early slope %.4f %s; current %.4f %s' % (r['early_slope'], r['early_ci'], r['current_slope'], r['current_ci']))
    print('Held-out gain %.4f %s; P1 %s; P2 %s' % (r['gain'], r['gain_ci'], r['P1'], r['P2']))
    print('Accounting: boundary %.4f - edge fraction %.4f = kappa %.4f' % (r['boundary_log_slope'], r['edge_fraction_log_slope'], r['current_slope']))
    print('Both-area linear slope %.4f; median between-seed sd(log kappa) %.4f' % (r['both_area_linear_slope'], r['between_seed_sd_median']))
''')
md('''These tables show whether the registered association survives a different
growth-clock control. They do not separate cause from response to growth history.
''')
md('''**Final verdict: UNINFORMATIVE.** All three windows retain seven complete
families, below the registered twelve-family gate. P1/P2 were not fitted or
scored. Of 256 starts, 45 eventually escape; 40 miss the early window and four
more miss the targets. The 212 valid starts do not supply balanced families.
This does not support or reject the lead association.
''')
md('''## Caveats and controls
Synthetic exact-spline and correlated-noise controls calibrate the regression;
the coefficient decomposition is an identity. CPU/GPU outputs are compared byte
for byte on all 256 specs and release tests recorded. The cohort has only sixteen independent
suffix families and uses a shorter horizon than the previous 2^27 study. Area
and perimeter are measured on the response trajectories; neither is an
independent causal control. Gain intervals condition on fitted folds. Support
failure means uninformative, and failed thresholds remain failed.
''')
md('''## What this changes / next steps
Read the frozen primary verdict in results/analysis.json together with the final
README interpretation. If current-area adjustment removes the association, early
area alone was insufficient at this horizon; if it survives, test transport with
independent pre-window predictors before interventions. Longer-horizon and
fixed-area replication are needed in either case.

Open questions: how much is survivor selection, which field history matters,
and can first-L position be separated from opening-run length?
''')
notebook=dict(cells=cells,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.12')),nbformat=4,nbformat_minor=5)
for i,c in enumerate(cells):
    c['id']=f'cell-{i:02d}'
(EXP/'notebook.ipynb').write_text(json.dumps(notebook,indent=1)+'\n')
