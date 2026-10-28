"""Native-clock audit: exact empirical waits, censoring and serial counts."""
from collections import Counter
import json
from pathlib import Path
import numpy as np
from run_memory import sha, write_new

EXP = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
OUT = EXP / "results/native_v1"


def wait_bin(w):
    return next((i for i, edge in enumerate([1, 2, 3, 4, 8, 16, 32]) if w <= edge), 7)


def summarize(rows):
    # Rows: physical timestamp, native return lag, physical lag class, birth, phase.
    assert all(b[0] > a[0] for a, b in zip(rows, rows[1:]))
    native = [0] * 4
    births = []
    for i, (_, lag, physical, born, _) in enumerate(rows, 1):
        assert (lag == 0) == (physical == 0)
        native[0 if lag == 0 else 1 if lag <= 4 else 2 if lag <= 16 else 3] += 1
        if born:
            births.append(i)
    waits = [b - a for a, b in zip(births, births[1:])]
    left = births[0] if births else len(rows)
    right = len(rows) - births[-1] if births else 0
    assert left + sum(waits) + right == len(rows)
    joint = Counter(f"{wait_bin(a)},{wait_bin(b)}" for a, b in zip(waits, waits[1:]))
    return {"reads": len(rows), "births": len(births), "native_lag": native,
            "wait_counts": dict(sorted(Counter(map(str, waits)).items(), key=lambda p: int(p[0]))),
            "joint_counts": dict(sorted(joint.items())), "complete_waits": len(waits),
            "left_partial_reads": left, "right_censored_reads": right,
            "no_birth_window": not births}


def tv(a, b):
    na, nb = sum(a.values()), sum(b.values())
    if not na or not nb:
        return None
    return sum(abs(a.get(k, 0) / na - b.get(k, 0) / nb) for k in a.keys() | b.keys()) / 2


def distance(a, b):
    return {"native_budget_error": max(abs(x / a['births'] - y / b['births'])
            for x, y in zip(a['native_lag'], b['native_lag'])) if a['births'] and b['births'] else None,
            "wait_tv": tv(a['wait_counts'], b['wait_counts']),
            "joint_tv": tv(a['joint_counts'], b['joint_counts'])}


def calibration():
    rng = np.random.default_rng(2026102071)
    def sequence(waits):
        birth_indices = set(np.cumsum([1, *waits]).tolist())
        return [[i, 0, 0, int(i in birth_indices), 0] for i in range(1, max(birth_indices) + 4)]
    rows = sequence([1, 2, 4, 8] * 100)
    a = summarize(rows)
    assert a['wait_counts'] == {'1': 100, '2': 100, '4': 100, '8': 100}
    assert a['left_partial_reads'] == 1 and a['right_censored_reads'] == 3
    stretched = [r.copy() for r in rows]
    for row, t in zip(stretched, np.cumsum(rng.integers(1, 100, len(rows)))):
        row[0] = int(t)
    assert summarize(stretched) == a
    b, c = summarize(sequence([1, 8] * 200)), summarize(sequence([1] * 200 + [8] * 200))
    assert tv(b['wait_counts'], c['wait_counts']) == 0
    serial_tv = tv(b['joint_counts'], c['joint_counts'])
    assert serial_tv > .20
    assert summarize([])['no_birth_window']
    return {'seed': 2026102071, 'known_wait_counts_exact': True,
            'time_stretch_invariant': True, 'same_marginal_serial_tv': serial_tv,
            'empty_window_accounting': True}


def main():
    calibration_result = calibration()
    records = {}
    for p in sorted(OUT.glob('pilot*.json')):
        assert p.with_suffix('.done').read_text().strip() == sha(p)
        records[p.stem] = json.loads(p.read_text())
    assert len(records) == 40
    comparisons = []
    spreads = []
    families = sorted({r['family'] for r in records.values()})
    for family in families:
        refs = [r for r in records.values() if r['family'] == family and r['mode'] == 'full']
        assert len(refs) == 2
        spreads.append({'family': family, 'rule': refs[0]['rule'], **distance(refs[0]['native'], refs[1]['native'])})
        for ref in refs:
            for r in records.values():
                if r['family'] != family or r['seed'] != ref['seed'] or r['mode'] == 'full':
                    continue
                eligible = ref['summary']['window_complete'] and ref['summary']['births'] >= 500 and r['summary']['window_complete'] and not (ref['summary']['escaped'] or r['summary']['escaped'])
                d = distance(ref['native'], r['native'])
                comparisons.append({'family': family, 'rule': r['rule'], 'seed': r['seed'], 'mode': r['mode'],
                                    'eligible': eligible, **d})
    tests = {}
    for mode in ['uniform:4', 'turn:4', 'next:4', 'word2:4']:
        pairs = [r for r in comparisons if r['mode'] == mode and r['eligible']]
        sensitive = [r for r in pairs if r['rule'] == 'RRRRLLRRLLLLRR']
        def value(r, k):
            return float('inf') if r[k] is None else r[k]
        budget = [value(r, 'native_budget_error') for r in pairs]
        wait_ok = lambda r: value(r, 'wait_tv') <= .05 and value(r, 'joint_tv') <= .075
        gate = len(pairs) >= 6 and len(sensitive) == 2
        n1 = gate and np.median(budget) <= .20 and all(value(r, 'native_budget_error') <= .20 for r in sensitive)
        n2 = gate and sum(map(wait_ok, pairs)) >= 6 and all(map(wait_ok, sensitive))
        tests[mode] = {'eligible': len(pairs), 'N1': 'HELD' if n1 else 'FAILED' if gate else 'UNINFORMATIVE',
                       'N2': 'HELD' if n2 else 'FAILED' if gate else 'UNINFORMATIVE',
                       'median_budget_error': float(np.median(budget)) if all(np.isfinite(budget)) else None,
                       'waiting_pass_pairs': sum(map(wait_ok, pairs)), 'sensitive': sensitive}
    report = {'calibration': calibration_result, 'tests': tests, 'comparisons': comparisons, 'reference_seed_spreads': spreads,
              'inputs_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(OUT.glob('pilot*.json'))},
              'command': 'uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/analyse_native.py',
              'script_sha256': sha(Path(__file__)), 'git_revision': __import__('subprocess').check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    write_new(EXP / 'results/native_report.json', report)
    print(json.dumps(tests, indent=2))


if __name__ == '__main__':
    main()
