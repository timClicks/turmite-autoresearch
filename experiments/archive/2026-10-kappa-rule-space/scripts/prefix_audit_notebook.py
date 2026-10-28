"""Build the small shareable audit notebook from result files only."""
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
cells = []


def md(text):
    cells.append(dict(cell_type="markdown", metadata={}, source=text.splitlines(True)))


def code(text):
    cells.append(dict(cell_type="code", metadata={}, source=text.splitlines(True), outputs=[], execution_count=None))


md("""# Prefix robustness audit
## Question and why it matters
Does the W3c prefix-8 result survive cross-fitting and nonlinear area adjustment?
This audits the surviving rule-space lead; it does not identify a mechanism.
See [registration and results](../README.md) and [research questions](../../../../notes/open-questions-hypotheses.md).
## Assumptions and definitions
Stationary means |g_k| < 0.05; rules need six core-band runs. Rule means are the units.
Cross-fitting holds out rules, allowing shared prefixes; this tests new suffixes of known prefixes.
Only ln A(22) is controlled, not the full growth history. This assumption limits the interpretation.
""")
code("""from pathlib import Path
import json, hashlib
import numpy as np
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'Cargo.toml').exists())
EXP = ROOT / 'experiments/archive/2026-10-kappa-rule-space'
paths = [EXP / 'results/prefix_audit.json', EXP / 'results/prefix_audit_predictions.csv']
for p in paths:
    assert p.exists(), p
    print(p.relative_to(ROOT), hashlib.sha256(p.read_bytes()).hexdigest())
report = json.loads(paths[0].read_text())
SEED = report['seed']
np.random.seed(SEED)
print('git', report['git'], 'seed', SEED)
print('analysis input/source hashes:', json.dumps(report['sha256'], indent=2))
print(report['calibration'])
""")
md("""## Data and method
The producing script is scripts/prefix_audit.py; raw trajectories stay outside this notebook.
Five-fold training lookup or historical LOO lookup; final lookup uses full census training.
OLS compares area alone to area plus lookup. Flexible area control has five training-quantile hinge knots.
Intervals resample 2000 test-rule sets, conditioning on training. Model choices were frozen before this audit.
Results were uncommitted when prepared; source and input hashes are recorded. Repository policy defers commits to user request.
## Results
""")
code("""print('cohort     encoding   area    N   baseline R2  model R2  gain   CI             without top5')
for r in report['rows']:
    print(f\"{r['cohort']:10} {r['encoding']:10} {r['area']:6} {r['n_test']:3} {r['baseline_r2']:11.3f} {r['model_r2']:9.3f} {r['gain']:6.3f} [{r['ci'][0]:.3f},{r['ci'][1]:.3f}] {r['without_top5']:.3f}\")
print('Frozen expectations:', report['expectations'])
print('All prefix8 support:', all(r['prefix8_share'] == 1 for r in report['rows']))
print('Test areas outside training range:', [r['area_outside_training'] for r in report['rows']])
""")
md("""The stationary gain survives cross-fitting and a flexible area baseline; the all-rules estimate remains weak.
This does not establish a transport mechanism, asymptotic law, or independence from growth history.
## Caveats and controls
Known area-only and planted-signal calibration passes; original W3c point estimate is reproduced.
The existing letters-to-c positive control passed in W5; this audit does not repeat it or a label-permutation test.
No new trajectories, stationarity calibration, or noise-ceiling estimate were made here.
Bootstrap rules share prefixes, so the intervals describe rule resampling rather than transfer to unseen prefix families.
The five-largest-contributor removal is a diagnostic selected from test outcomes.
Both the test cohort and the prefix were previously inspected: this is robustness, not fresh confirmation.
## What this changes / next steps
Retain the stationary prefix lead. A causal next experiment should compare mutations at fixed area,
and distinguish early-colour exposure from changes to the entire self-organised field.
Open questions: why stationary training is essential, whether area measurement noise leaves a residual size effect,
and whether prefix influence persists in longer-time, matched-area mutation runs.
""")
target = EXP / "notebooks/prefix-audit.ipynb"
target.parent.mkdir(exist_ok=True)
for i, cell in enumerate(cells):
    cell["id"] = f"prefix-audit-{i:02d}"
target.write_text(json.dumps(dict(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}, nbformat=4, nbformat_minor=5), indent=1) + "\n")
