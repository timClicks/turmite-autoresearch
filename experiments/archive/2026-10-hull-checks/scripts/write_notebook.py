"""Build the shareable write-up; execution is a separate clean-kernel step."""
import json
from checks import EXP


def md(s):
    return dict(cell_type="markdown", metadata={}, source=s.splitlines(keepends=True))


def code(s):
    return dict(cell_type="code", metadata={}, source=s.splitlines(keepends=True), execution_count=None, outputs=[])


cells = [md("""# Hull checks: persistent shape or local roughening?

## Question and why it matters
Does the wider ant hull reflect persistent shape or shorter-wavelength variation?
The [registered README](README.md) fixes hypotheses before measurement. See also
[research avenue 5](../../../notes/paper-gaps-research-avenues-2026-10-15.md).
This write-up covers calibration and the bounded pilot. The full run is pending.

## Assumptions and definitions
The outermost visited-cell radius in each of 512 angular bins can miss overhangs.
The exterior is 4-connected. These are definitions, not validated physical-interface
assumptions. The unresolved census sample is not certified chaotic. Modes 3–8 are
the registered shape band, 9–64 the local band. Coarsening tests resolution.

## Provenance
Inputs below live in results/ and are intended to be committed with this experiment.
They are currently uncommitted working outputs. No raw dumps are read.
"""), code("""from pathlib import Path
import hashlib, json
SEED = 20261015
root = next(p for p in (Path.cwd(), *Path.cwd().parents) if (p/'Cargo.toml').exists())
exp = root/'experiments/archive/2026-10-hull-checks'
res = exp/'results'
manifest = json.loads((res/'pilot/manifest.json').read_text())
analysis = json.loads((res/'pilot/analysis.json').read_text())
print('producing commit:', manifest['commit'], '(dirty tree recorded in manifest)')
print('registered date: 2026-10-15 NZDT; seed:', SEED)
paths = [res/'calibration.json', res/'validation.json', res/'pilot/manifest.json', res/'pilot/analysis.json']
paths += sorted((res/'pilot').glob('*.csv'))
for p in paths:
    assert p.exists(), p
    print(p.relative_to(root), hashlib.sha256(p.read_bytes()).hexdigest())
"""), md("""## Data and method
Heavy computation is in `examples/hull_checks.rs` and `scripts/run.py`.
The pilot consists of two ant rules and one rotor, each at seeds 331 and 332,
k=16..20. It checks acquisition, exclusions and analysis. It has insufficient
rotors for the registered minimum of eight radius matches and cannot test H-shape/H-local.

## Results
"""), code("""for name in ('calibration.json', 'validation.json'):
    d = json.loads((res/name).read_text())
    print(name, d['status'])
print('Valid profiles:', len(analysis['profiles']))
print('Excluded profiles/escape records:', len(analysis['exclusions']))
print('Missing files:', analysis['missing_files'])
print('Exclusion reasons:')
for s in analysis['exclusions']: print(' ', s)
print('Decisions:', {k:v['decision'] for k,v in analysis['verdicts'].items()})
"""), md("""The estimator calibration passes and the pilot retains populated profiles while
listing sparse-bin failures explicitly. This validates plumbing; it does not
show whether the ants' residual hull fluctuations exceed matched rotors.

## Caveats and controls
The small pilot has sparse angular bins, so invalid profiles must not be silently
interpolated. Synthetic controls check mode assignment, Parseval including Nyquist,
the exact sinusoid structure function and persistence of lobes versus orthogonal
local modes. Compatibility validation checks nine original-instrument rows and
byte equality with one versus six Rayon threads. The resume log records six skips.
The full run uses absolute power, matched radii and bin coarsening, addressing the
normalisation problem in the earlier hull analysis. No scientific prediction has
been tested by this pilot.

## What this changes / next steps
Run the registered full cohort and evaluate the matching/resolution gates before
interpreting either hypothesis. The pilot demonstrates a reproducible instrument.
No new empirical claim about asymptotic roughening is warranted.

## Open questions
Do low modes persist? Is there residual local excess at equal radii? Does the
estimated correlation length have adequate resolution and a reproducible scaling?
The unresolved-rule sample may contain transient builders or highways.
""")]
notebook = dict(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                     "language_info": {"name": "python", "version": "3.12"}}, nbformat=4, nbformat_minor=5)
for i, cell in enumerate(cells):
    cell['id'] = f'hull-checks-{i}'
(EXP/'notebook.ipynb').write_text(json.dumps(notebook, indent=1) + '\n')
