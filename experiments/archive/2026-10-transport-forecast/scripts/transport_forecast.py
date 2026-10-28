"""Run the registered discrete transport forecast; see the sibling research note."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import polars as pl


def budget(a, new, t):
    return (a ** 1.5 - (a - new) ** 1.5) / (t / 2)


def instrument_check():
    t = 2.0 ** np.arange(10, 18)
    for power in [2 / 3, 1.0]:
        a = 3 * t ** power
        q = budget(a, a - 3 * (t / 2) ** power, t)
        p = np.polyfit(np.log(t[:3]), np.log(q[:3]), 1)
        np.testing.assert_allclose(np.exp(np.polyval(p, np.log(t[3:]))), q[3:], rtol=1e-12)
        if power == 2 / 3:
            np.testing.assert_allclose(q, q[0], rtol=1e-12)
        else:
            assert np.all(q[3:] > q[:3].mean())


def cohort(path, lo):
    df = pl.read_csv(path)
    runs, excluded = [], []
    for (name,), group in df.group_by('rule', maintain_order=True):
        rows = group.filter(pl.col('k').is_between(lo, lo + 6)).sort('k').to_dicts()
        if len(rows) != 7 or [r['k'] for r in rows] != list(range(lo, lo + 7)) or any(
            r['escaped'] or r['new_cells'] <= 0 or r['area'] <= r['new_cells'] or r['boundary_steps'] <= 0
            for r in rows
        ):
            excluded.append(name)
            continue
        a = np.array([r['area'] for r in rows], float)
        new = np.array([r['new_cells'] for r in rows], float)
        t = np.array([r['t'] for r in rows], float)
        np.testing.assert_array_equal(a[1:] - new[1:], a[:-1])
        q = budget(a, new, t)
        c = new / np.array([r['boundary_steps'] for r in rows])
        perimeter = np.array([r['perimeter'] for r in rows])
        kappa = new / c / (t / 2) * a / perimeter
        geometry = perimeter / np.sqrt(a)
        endpoint = 1.5 * c * kappa * geometry
        drift = np.polyfit(np.log(t[:3]), np.log(q[:3]), 1)
        runs.append(dict(name=name, rule=name.split('@')[0], a=a, t=t, q=q,
                         constant=q[:3].mean(), drift=np.exp(np.polyval(drift, np.log(t[3:]))),
                         factors=np.array([c, kappa, geometry]), endpoint=endpoint))
    rules = sorted({r['rule'] for r in runs})
    train = {rule: np.mean([r['constant'] for r in runs if r['rule'] == rule]) for rule in rules}
    records = []
    for r in runs:
        baseline = np.median([v for rule, v in train.items() if rule != r['rule']])
        record = dict(name=r['name'], rule=r['rule'])
        for model, prediction in [('constant', np.repeat(r['constant'], 4)), ('drift', r['drift']),
                                  ('baseline', np.repeat(baseline, 4))]:
            record[model] = float(np.median(np.abs(prediction / r['q'][3:] - 1)))
            final = (r['a'][2] ** 1.5 + np.sum(prediction * r['t'][3:] / 2)) ** (2 / 3)
            record[model + '_final'] = float(abs(final / r['a'][-1] - 1))
        siblings = [other['constant'] for other in runs if other['rule'] == r['rule'] and other['name'] != r['name']]
        if siblings:
            record['other_seeds'] = float(np.median(np.abs(np.median(siblings) / r['q'][3:] - 1)))
        changes = np.log(r['factors'][:, 3:] / r['factors'][:, 2, None])
        np.testing.assert_allclose(changes.sum(axis=0), np.log(r['endpoint'][3:] / r['endpoint'][2]), atol=1e-12)
        for label, values in zip(['c', 'kappa', 'geometry'], changes):
            record[label + '_change'] = float(np.median(np.abs(values)))
        record['endpoint_over_exact'] = float(np.median(r['endpoint'] / r['q']))
        records.append(record)
    keys = [k for k in records[0] if k not in ['name', 'rule']]
    means = {k: np.array([np.mean([r[k] for r in records if r['rule'] == rule]) for rule in rules]) for k in keys}
    rng = np.random.default_rng(20261013)
    gains = []
    for _ in range(2000):
        idx = rng.integers(0, len(rules), len(rules))
        gains.append(1 - np.median(means['constant'][idx]) / np.median(means['baseline'][idx]))
    return dict(input=path, sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                train=[lo, lo + 2], test=[lo + 3, lo + 6], runs=len(runs), rules=len(rules),
                excluded=excluded, rule_medians={k: float(np.median(v)) for k, v in means.items()},
                reduction=float(1 - np.median(means['constant']) / np.median(means['baseline'])),
                reduction_ci=np.quantile(gains, [.025, .975]).tolist(),
                rms_seed_sd={k: float(np.sqrt(np.mean([np.var([r[k] for r in records if r['rule'] == rule], ddof=1)
                              for rule in rules if sum(r['rule'] == rule for r in records) > 1])))
                             for k in ['constant', 'drift', 'baseline']} if any('@' in r['name'] for r in runs) else {},
                records=records)


if __name__ == '__main__':
    instrument_check()
    result = dict(commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                  command='uv run experiments/archive/2026-10-transport-forecast/scripts/transport_forecast.py', bootstrap_seed=20261013,
                  synthetic_checks='passed', cohorts={})
    for label, path, lo in [('ants', 'experiments/archive/2026-10-b2-between-rule-variance/results/b2_probe.csv', 20), ('rotor', 'experiments/archive/2026-10-calib-instrument-calibration/results/calib_rotor.csv', 20),
                            ('random_walk', 'experiments/archive/2026-10-calib-instrument-calibration/results/calib_rw.csv', 17)]:
        result['cohorts'][label] = cohort(path, lo)
        summary = {k: v for k, v in result['cohorts'][label].items() if k not in ['records', 'excluded']}
        print(label, json.dumps(summary, sort_keys=True))
    Path('experiments/archive/2026-10-transport-forecast/results/transport_forecast.json').write_text(json.dumps(result, indent=2) + '\n')
