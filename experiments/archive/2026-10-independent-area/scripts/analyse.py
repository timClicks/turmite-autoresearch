"""Registered three-way seed split; run under uv from the repository root."""
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'experiments/archive/2026-10-t1-excursion-tomography/results/t1b_cutoff_seeds.csv'
SEED = 20261015
ROLES = list(itertools.permutations(range(3)))


def pairs(v, tol):
    """v is rule x group x (lnA, lnkappa, ln_ratio)."""
    i, j = np.triu_indices(len(v), 1)
    out = []
    for a, b, c in ROLES:
        take = abs(v[i, a, 0] - v[j, a, 0]) <= tol
        ii, jj = i[take], j[take]
        agree = ((v[ii, b, 1] - v[jj, b, 1]) *
                 (v[ii, c, 2] - v[jj, c, 2])) < 0
        out.append((ii, jj, agree))
    return out


def score(ps, weights):
    fractions = []
    for i, j, agree in ps:
        w = weights[i] * weights[j]
        if w.sum() == 0:
            return float('nan')
        fractions.append(float(np.dot(w, agree) / w.sum()))
    return float(np.mean(fractions))


def controls():
    rng = np.random.default_rng(SEED)
    values = {'null': [], 'negative': []}
    for _ in range(200):
        a, k, q = rng.normal(size=(3, 44))
        for name, target in [('null', q), ('negative', -k)]:
            v = np.stack([a, k, target], axis=1)[:, None, :] + rng.normal(0, .1, (44, 3, 3))
            values[name].append(score(pairs(v, .1), np.ones(44)))
    means = {key: float(np.nanmean(x)) for key, x in values.items()}
    assert abs(means['null'] - .5) < .05 and means['negative'] > .8, means
    return means


def main():
    calibration = controls()  # Gate ant analysis on instrument checks.
    print('controls', calibration, flush=True)
    df = pl.read_csv(INPUT).filter(~pl.col('escaped')).with_columns(
        pl.col('area').log().alias('lnA'), (pl.col('seed') % 3).alias('group'))
    result = {'seed': SEED, 'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'command': 'uv run experiments/archive/2026-10-independent-area/scripts/analyse.py',
              'input': str(INPUT.relative_to(ROOT)), 'input_sha256': hashlib.sha256(INPUT.read_bytes()).hexdigest(),
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'controls': calibration, 'windows': []}
    rng = np.random.default_rng(SEED + 1)
    for k in [22, 25]:
        groups = df.filter(pl.col('k') == k).group_by('rule', 'group').agg(
            pl.col('lnA').mean(), pl.col('lnkappa').mean(), pl.col('ln_ratio').mean(), pl.len().alias('n'))
        names, arrays = [], []
        for rule in sorted(groups['rule'].unique()):
            g = groups.filter(pl.col('rule') == rule).sort('group')
            if g.height == 3 and g['n'].min() >= 2:
                names.append(rule)
                arrays.append(g.select('lnA', 'lnkappa', 'ln_ratio').to_numpy())
        v = np.array(arrays)
        # Same bootstrap draws at both tolerances.
        weights = [np.bincount(rng.integers(len(v), size=len(v)), minlength=len(v)) for _ in range(2000)]
        for tol in [.05, .10]:
            ps = pairs(v, tol)
            boot = np.array([score(ps, w) for w in weights])
            ci = np.nanpercentile(boot, [2.5, 97.5]).tolist()
            point = score(ps, np.ones(len(v)))
            enough = len(v) >= 20 and min(len(p[0]) for p in ps) >= 20
            row = {'k': k, 'tolerance': tol, 'rules': names, 'n_rules': len(v),
                   'roles': [{'area_group': a, 'kappa_group': b, 'cutoff_group': c,
                              'pairs': len(p[0]), 'fraction': float(np.mean(p[2]))}
                             for (a,b,c), p in zip(ROLES, ps)],
                   'concordance': point, 'bootstrap95': ci, 'valid_bootstraps': int(np.isfinite(boot).sum()),
                   'verdict': ('held' if point >= .65 and ci[0] > .5 else 'failed') if enough else 'inconclusive'}
            result['windows'].append(row)
            print(k, tol, len(v), point, ci, row['verdict'], flush=True)
    (EXP / 'results').mkdir(exist_ok=True)
    (EXP / 'results/analysis.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
