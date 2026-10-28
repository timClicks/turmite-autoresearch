"""Update the shareable write-up from committed pilot summaries, without execution."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
path = EXP / "notebook.ipynb"
book = json.loads(path.read_text())
cells = [c for c in book["cells"] if c["id"] not in {"pilot-provenance", "pilot-audit", "pilot-interpretation", "memory-method", "memory-audit", "memory-figure", "memory-interpretation", "information-audit", "native-method", "native-audit", "native-limits"}]
cells[0]["source"] = [
    "# What does a new cell cost?\n\n",
    "This experiment asks what process sets births per boundary read. See [the protocol](README.md) and [the append-only log](NOTEBOOK.md). Calibrated recording exposed an unsupported rich lookup; a finite colour-memory closure subsequently failed both registered cost and return-budget tests. The main cohort remains unrun.\n\n",
    "The immediate birth is fixed by the current turn and visited-neighbour mask. The unknown is their distribution. Births are not assumed independent regeneration points, and a pooled cross-rule transition matrix must respect target-rule-compatible successor states."
]
for c in cells:
    if c["id"] == "design-audit":
        c["source"] = [line.replace("Scientific results: none; instrument, calibration and pilot pending.", "This cell audits planned assignments only; pilot outcomes are audited below.") for line in c["source"]]
    if c["id"] == "method":
        c["source"] = [
            "## Method and controls\n",
            "The source recorder is compared event by event to a sparse independent path oracle, plus exact totals against the existing aggregate tracer. The solver is calibrated on known two-state reward chains and challenged by hidden history. Rotor and random-walk controls use eight seeds each. The excluded pilot uses four families, three arms and two interior seeds, with horizons 2^22..2^26. Commands, seeds, thresholds and binary hashes are in the README and result provenance.\n\n",
            "No main transition model is fitted. Draft P1–P4 remain untested; G1's solver calibration does not calibrate an ant state/backoff model. The support repeat at k=26 is a registered feasibility diagnostic after the horizon failure, not a rescue of the gate."
        ]
    if c["id"] == "limits":
        c["source"] = [
            "## What remains unestablished\n",
            "There is no validated local renewal model, no derived intercept or slope, and no new mechanism claim about kappa. The pilot gate failed; no families were replaced and no validation outcomes were opened. Unseen-state mass is only a feasibility check, not a measure of predictive accuracy. Coarsening can improve support while destroying relevant information.\n\n",
            "Next decisions must address both sampling failures and target-rule-compatible transitions. A good total birth rate alone cannot show Markov closure; the hidden-history calibration supplies a counterexample."
        ]
def markdown(identity, text):
    return {"cell_type": "markdown", "id": identity, "metadata": {}, "source": text.splitlines(keepends=True)}
def code(identity, text):
    return {"cell_type": "code", "id": identity, "metadata": {}, "execution_count": None, "outputs": [], "source": text.splitlines(keepends=True)}
cells.extend([
    markdown("pilot-provenance", "## Pilot provenance and results\nOnly committed JSON/CSV summaries are read. Every input is checked for content changes and hashed; ignored event dumps are not notebook inputs. Uncertainty below is between seeds, not a fit standard error.\n"),
    code("pilot-audit", '''files = [EXP / 'results' / name for name in ['calibration.json', 'pilot_report.json', 'pilot_diagnostics.json', 'pilot_diagnostics.csv']]
if (EXP / 'results/support_report.json').exists():
    files.append(EXP / 'results/support_report.json')
for p in files:
    subprocess.run(['git', 'ls-files', '--error-unmatch', str(p.relative_to(ROOT))], cwd=ROOT, check=True, capture_output=True)
    subprocess.run(['git', '-c', 'core.filemode=false', 'diff', '--exit-code', 'HEAD', '--', str(p.relative_to(ROOT))], cwd=ROOT, check=True, capture_output=True)
    print(hashlib.sha256(p.read_bytes()).hexdigest(), p.relative_to(ROOT))
calibration, controls, diagnostic = [json.loads(p.read_text()) for p in files[:3]]
support = json.loads(files[4].read_text()) if len(files) == 5 else None
assert calibration['passed']
print('Synthetic reward solver: maximum |c error|', calibration['max_absolute_error'], 'signed bias', calibration['signed_bias'], 'between-seed sd', calibration['between_seed_sd'])
print('Hidden-history control: pooled c', calibration['negative_control']['pooled_c'], 'conditional contrast', calibration['negative_control']['contrast'])
for walker, result in controls['controls'].items():
    assert result['passed'] and result['n'] == 8
    print(walker, 'c mean', result['mean'], 'between-seed sd', result['between_seed_sd'], 'escapes', result['escapes'])
assert controls['thread_check']['identical']
assert controls['horizon']['selected_log2'] is None
print('Original pilot horizon verdict:', controls['horizon']['status'])
print('Usable k=26 runs:', diagnostic['k26_usable_runs'], '/', diagnostic['k26_n'])
for name, result in (support['models'] if support else {}).items():
    print(name, 'unseen read mass median', result['median_unseen_mass'], 'maximum', result['max_unseen_mass'], 'runs >5%', result['runs_over_5pct'])
if support is None:
    print('Excluded support diagnostic is pending; no support verdict yet.')
print('These outputs are calibration and feasibility evidence; P1-P4 are untested.')
'''),
    markdown("pilot-interpretation", "## Interpretation and next discrimination\nThe controls validate recording and the narrow solver task. They do not validate a model of ant state frequencies. The original pilot failed to supply a common sampling window; its support diagnostic cannot retroactively make that gate pass. Full eight-turn states may encode family identity and lose transfer support. A smaller state still needs a generative transition rule consistent with the target rule and a test against hidden history.\n")
])
if (EXP / 'results/memory_report.json').exists():
    cells.extend([
        markdown('memory-method', '''## Finite colour memory: an exact-rule intervention
Keep the target rule's exact colour clock inside a moving Chebyshev-radius r patch. On a forgotten re-read sample a uniform phase; first reads retain the original phase. The model creates its own path and visited geometry, without target state frequencies. Compare full, r=0/1/2/4/8 and zero-reset r=4 on four excluded base rules and two seeds.

Before measuring, replace the proposed fixed-time window by 2048 warmup boundary reads followed by 8192 measurement reads, capped at 2^28 steps. At most 10240 births can occur before a complete stop, preventing band depletion. Report every cap. This prospectively amended pilot does not rescue the original failed horizon gate.

Exact deduction: a k-step returning quarter-turn path can stray at most k/4 cells in either coordinate. Forgetting at radius r requires return lag at least 4(r+1). Thus r=4 directly resets only >16-step phases. Independent eviction/path/window oracles and exhaustive 16-step turn-word checks precede data; full release tests pass. Calibration and finite-window bias appear below.
'''),
        code('memory-audit', '''import numpy as np
memory_files = [EXP / 'results' / name for name in ['memory_report.json', 'memory_diagnostics.json', 'memory_v1/controls.json', 'memory_pilot.png']]
for p in memory_files:
    subprocess.run(['git', 'ls-files', '--error-unmatch', str(p.relative_to(ROOT))], cwd=ROOT, check=True, capture_output=True)
    subprocess.run(['git', '-c', 'core.filemode=false', 'diff', '--exit-code', 'HEAD', '--', str(p.relative_to(ROOT))], cwd=ROOT, check=True, capture_output=True)
    print(hashlib.sha256(p.read_bytes()).hexdigest(), p.relative_to(ROOT))
memory, memory_diagnostic, memory_controls = [json.loads(p.read_text()) for p in memory_files[:3]]
for walker, result in memory_controls['controls'].items():
    assert result['passed'] and result['n'] == 8
    print(walker, 'boundary-clock c', result['mean'], 'between-seed sd', result['between_seed_sd'], 'difference vs old fixed time', result['difference_from_parent_fixed_time_mean'])
for mode, result in memory['tests'].items():
    pairs = [r for r in memory['comparisons'] if r['mode']==mode and r['eligible']]
    errors = [float('inf') if r['error_infinite'] else r['abs_log_error'] for r in pairs]
    budgets = [float('inf') if r['budget_error_infinite'] else r['max_budget_error'] for r in pairs]
    assert len(pairs) == result['eligible_pairs']
    assert np.isclose(np.median(errors), result['median_abs_log_error'])
    assert np.isclose(max(errors), result['max_abs_log_error'])
    assert np.isclose(np.median(budgets), result['median_max_budget_error'])
    print(mode, 'n', len(pairs), 'median |ln c ratio|', np.median(errors), 'max', max(errors), 'median max budget error', np.median(budgets), 'M1', result['M1'], 'M2', result['M2'])
print('M3', memory['policy']['M3'], 'defined pairs', memory['policy']['eligible_defined_pairs'])
for row in memory_diagnostic['decomposition']:
    if row['lead']==4 and row['mode']=='uniform:4':
        print(row['rule'], row['seed'], 'signed cost change', row['delta_reads_per_birth'], 'first/lag4/short/long', row['signed_budget_delta_first_lag4_short_long'])
print('Max full-ant absolute ln event-clock/fixed-time c:', max(abs(r['ln_event_over_fixed']) for r in memory_diagnostic['clock_audit']))
print('Main P1-P4 untested. Four rules, two seeds each; no confidence interval or universal locality claim.')
'''),
        code('memory-figure', "from IPython.display import Image, display\ndisplay(Image(filename=str(EXP / 'results/memory_pilot.png')))\n"),
        markdown('memory-interpretation', '''## What failed, what we learned, what remains
M1 and M2 fail at both r=4 and r=8; r=8's budget miss is narrow but remains a failure. The lead-4 rule has both paired c estimates roughly 30–35% too high under uniform forgetting. In the lead-2 rule, increased short-loop cost nearly cancels decreased long-return cost, hiding a wrong budget behind a close total. The lead-3 rule has negligible boundary reset exposure and is a weak challenge. Six zero-policy cases never open a measurement window; M3 has only two defined pairs and is uninformative.

Short-loop phase preservation alone with uniform forgotten phases is insufficient here. This is not a general rejection of local mechanisms. Global geometry is retained by the model, the window is early, there are only four pilot rules, and main outcomes remain unopened. The full-ant clock audit is exploratory and not a proof of asymptotic equivalence.

Next proposal: preserve only the old turn bit when scrambling a forgotten phase, then compare preserving two future turns. That distinguishes a directional field from a distant phase clock. It needs a fresh oracle, registration, exposure checks and held-out confirmation; no such result exists yet. The c-law coefficients and later-letter corrections remain unexplained.
''')
    ])
if (EXP / 'results/information_report.json').exists():
    cells.append(code('information-audit', '''# Subsequent read/write-information pilot; original failures stand.
p = EXP / 'results/information_report.json'
subprocess.run(['git', 'ls-files', '--error-unmatch', str(p.relative_to(ROOT))], cwd=ROOT, check=True, capture_output=True)
subprocess.run(['git', '-c', 'core.filemode=false', 'diff', '--exit-code', 'HEAD', '--', str(p.relative_to(ROOT))], cwd=ROOT, check=True, capture_output=True)
print(hashlib.sha256(p.read_bytes()).hexdigest(), p.relative_to(ROOT))
information = json.loads(p.read_text())
print(json.dumps(information['tests'], indent=2))
print('All information candidates fail I2; close total cost does not restore the physical return budget.')
'''))
if (EXP / 'results/native_report.json').exists():
    cells.extend([
        markdown('native-method', '''## Does the boundary birth process differ, or only physical return time?
The next registered audit keeps all earlier failures. A boundary source cannot have been interior on a previous read, since visitation only removes fresh neighbours. Its phase clock therefore counts boundary visits. Compare first/1..4/5..16/>16 native return budgets, the complete empirical inter-birth waiting distribution, and adjacent waiting pairs in fixed bins. Left and right partial waits are retained as censored endpoints.

Same four excluded bases, two seeds, five arms, 2048 warmup plus 8192 measurement reads. No main outcomes, parameter fitting or new treatment. Known synthetic waits calibrate the counters; physical-time stretching must leave native summaries invariant, and reordering equal-marginal waits must change the serial test. The sparse path oracle checks native lags through warmup. Every earlier ant summary must replay exactly.
'''),
        code('native-audit', '''p = EXP / 'results/native_report.json'
subprocess.run(['git', 'ls-files', '--error-unmatch', str(p.relative_to(ROOT))], cwd=ROOT, check=True, capture_output=True)
subprocess.run(['git', '-c', 'core.filemode=false', 'diff', '--exit-code', 'HEAD', '--', str(p.relative_to(ROOT))], cwd=ROOT, check=True, capture_output=True)
print(hashlib.sha256(p.read_bytes()).hexdigest(), p.relative_to(ROOT))
native = json.loads(p.read_text())
print('Synthetic calibration:', native['calibration'])
for name, digest in native['inputs_sha256'].items():
    q = ROOT / name
    subprocess.run(['git', 'ls-files', '--error-unmatch', name], cwd=ROOT, check=True, capture_output=True)
    assert hashlib.sha256(q.read_bytes()).hexdigest() == digest
    r = json.loads(q.read_text())
    s = r['native']
    assert sum(s['native_lag']) == s['reads'] == r['summary']['boundary_reads']
    assert s['births'] == r['summary']['births']
    assert s['left_partial_reads'] + sum(int(k)*v for k,v in s['wait_counts'].items()) + s['right_censored_reads'] == s['reads']
    assert sum(s['wait_counts'].values()) == s['complete_waits']
    assert sum(s['joint_counts'].values()) == max(0, s['complete_waits']-1)
for mode, result in native['tests'].items():
    print(mode, 'N1', result['N1'], 'N2', result['N2'], 'median native budget error', result['median_budget_error'], 'waiting-pass pairs', result['waiting_pass_pairs'])
    for r in result['sensitive']:
        print('  sensitive seed', r['seed'], 'budget', r['native_budget_error'], 'wait TV', r['wait_tv'], 'serial TV', r['joint_tv'])
print('Full-reference between-seed distances:', native['reference_seed_spreads'])
'''),
        markdown('native-limits', '''## Limits of the native-clock comparison
These are descriptive distances between finite early windows, not independent-event significance tests. Complete waits exclude endpoint-censored intervals; the exact endpoint identity checks accounting without assuming their absence. Adjacent-pair agreement would not prove independence or equality of all higher-order history. Two seeds per four previously inspected pilot rules cannot establish general sufficiency. Full-reference seed distances expose sampling variability but do not change registered thresholds. All physical-budget failures remain recorded; main P1–P4 are untested, and the c-law intercept and slope remain unexplained.
''')
    ])
for cell in cells:
    if cell["cell_type"] == "code":
        cell["execution_count"] = None
        cell["outputs"] = []
        cell["metadata"].pop("execution", None)
book["cells"] = cells
path.write_text(json.dumps(book, indent=1, ensure_ascii=False) + "\n")
print(path.relative_to(ROOT))
