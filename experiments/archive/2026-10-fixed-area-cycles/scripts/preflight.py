"""Validate frozen inputs (or the initial draft); no simulations or writes."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def main():
    config_path = EXP / 'config.frozen.json'
    if not config_path.exists():
        config_path = EXP / 'config.draft.json'
    cfg = json.loads(config_path.read_text())
    frozen = cfg['status'] == 'frozen_before_production'
    if frozen:
        cohort = EXP / cfg['cohort_file']
        assert hashlib.sha256(cohort.read_bytes()).hexdigest() == cfg['cohort_sha256']
        expected_hash = (EXP / 'results/config.frozen.sha256').read_text().split()[0]
        assert hashlib.sha256(config_path.read_bytes()).hexdigest() == expected_hash
        groups = [set(range(lo, hi + 1)) for lo, hi in cfg['seed_groups'].values()]
        assert sum(map(len, groups)) == len(set.union(*groups))
        assert not set.union(*groups) & set(range(701, 705))
        assert not set.union(*groups) & set(range(801, 929))
        bands = cfg['primary_bands']
    else:
        assert cfg['status'] == 'draft_not_registered'
        assert not set(cfg['pilot_seeds']) & set(cfg['candidate_production_seeds'])
        bands = cfg['area_bands']
    assert all(0 < lo < hi for lo, hi in bands)
    assert all(a[1] <= b[0] for a, b in zip(bands, bands[1:]))
    paths = [config_path, cohort if frozen else ROOT / cfg['cohort_input'], ROOT / 'src/probe.rs',
             ROOT / 'examples/excursions.rs', ROOT / 'src/walkers.rs',
             ROOT / 'tests/probe.rs', EXP / 'PLAN.md', EXP / 'SCHEMA.md',
             EXP / 'HANDOFF.md', EXP / 'notebook.ipynb']
    if frozen:
        paths.extend([ROOT / 'src/fixed_area.rs', ROOT / 'tests/fixed_area.rs',
                      ROOT / 'examples/fixed_area_cycles_sampler.rs'])
    print('STATUS:', cfg['status'])
    print('git', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
    for path in paths:
        assert path.is_file(), f'Missing required source: {path}'
        print(hashlib.sha256(path.read_bytes()).hexdigest(), path.relative_to(ROOT))
    print('Input checks passed; this command does not validate production outcomes.')


if __name__ == '__main__':
    main()
