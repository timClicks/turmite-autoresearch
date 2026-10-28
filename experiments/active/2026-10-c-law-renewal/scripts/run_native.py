"""Fresh native-event audit and exact replay of all 40 inspected pilot cases."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from analyse_native import summarize, calibration
from launch_support import heavy_jobs
from run_memory import sha, write_new

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
OUT = EXP / 'results/native_v1'


def worker():
    (OUT / 'session.pid').write_text(str(os.getpid()) + '\n')
    status = 1
    try:
        while jobs := heavy_jobs():
            print('Waiting on live jobs', jobs, flush=True)
            time.sleep(15)
        build_path = OUT / 'build.json'
        if not build_path.exists():
            target = Path(tempfile.mkdtemp(prefix='turmite-renewal-native-', dir=Path.home()))
            env = {**os.environ, 'CARGO_TARGET_DIR': str(target), 'CARGO_BUILD_JOBS': '2'}
            for label, argv in [('release-tests', ['cargo', 'test', '--release']),
                                ('build', ['cargo', 'build', '--release', '--example', 'c_law_renewal_memory'])]:
                with (OUT / (label + '.log')).open('x') as log:
                    subprocess.run(argv, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
            binary = target / 'release/examples/c_law_renewal_memory'
            names = ['src/edge_renewal.rs', 'src/local_memory.rs', 'src/edge_trace.rs', 'src/walkers.rs', 'src/rule.rs',
                     'examples/c_law_renewal_memory.rs', 'tests/edge_renewal.rs', 'tests/local_memory.rs', 'Cargo.toml', 'Cargo.lock',
                     'experiments/active/2026-10-c-law-renewal/information_design.json',
                     'experiments/active/2026-10-c-law-renewal/scripts/run_native.py',
                     'experiments/active/2026-10-c-law-renewal/scripts/analyse_native.py']
            write_new(build_path, {'git_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                       'binary': str(binary), 'binary_sha256': sha(binary), 'sources_sha256': {n: sha(ROOT / n) for n in names},
                       'release_test_exit': 0, 'build_exit': 0, 'fresh_target': str(target),
                       'command': 'uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/run_native.py',
                       'rustc': subprocess.check_output(['rustc', '--version'], text=True).strip()})
        build = json.loads(build_path.read_text())
        binary = Path(build['binary'])
        assert sha(binary) == build['binary_sha256']
        for n, h in build['sources_sha256'].items():
            assert sha(ROOT / n) == h, n
        cal = calibration()
        if not (OUT / 'calibration.json').exists():
            write_new(OUT / 'calibration.json', {'checks': cal, 'analysis_sha256': sha(EXP / 'scripts/analyse_native.py')})
        else:
            assert json.loads((OUT / 'calibration.json').read_text())['checks'] == cal
        print('Fresh build, release tests and synthetic calibration pass', flush=True)
        # Old summaries are immutable trajectory fingerprints, never native targets.
        old_files = sorted((EXP / 'results/information_v1').glob('pilot*.json'))
        old_files = [p for p in old_files if 'summary' in json.loads(p.read_text())]
        assert len(old_files) == 40, len(old_files)

        def run(p):
            prior = json.loads(p.read_text())
            argv = prior['recipe']['argv']
            path = OUT / p.name
            recipe = {'argv': argv, 'binary_sha256': sha(binary), 'build_sha256': sha(build_path),
                      'baseline': str(p.relative_to(ROOT)), 'baseline_sha256': sha(p)}
            if path.with_suffix('.done').exists():
                assert path.with_suffix('.done').read_text().strip() == sha(path)
                record = json.loads(path.read_text())
                assert record['recipe'] == recipe
                return
            assert not path.exists(), f'Inspect unmarked output {path}'
            started = time.monotonic()
            result = subprocess.run([str(binary), *argv], cwd=ROOT, capture_output=True, text=True, check=True,
                                    env={**os.environ, 'TURMITE_NATIVE_EVENTS': '1'})
            summary = json.loads(result.stdout)
            assert all(summary[k] == v for k, v in prior['summary'].items()), p.name
            rows = [list(map(int, line.split(','))) for line in result.stderr.splitlines()]
            native = summarize(rows)
            assert native['reads'] == summary['boundary_reads'] and native['births'] == summary['births']
            assert sum(native['native_lag']) == native['reads']
            physical = [sum(r[2] == i for r in rows) for i in range(4)]
            assert physical == summary['lag']
            record = {'family': '-'.join(p.name.split('-')[:3]), 'rule': argv[1], 'seed': argv[2], 'mode': argv[3],
                      'recipe': recipe, 'summary': summary, 'native': native}
            write_new(path, record)
            path.with_suffix('.done').write_text(sha(path) + '\n')
            print(p.stem, 'exact replay; native events', len(rows), 'seconds', round(time.monotonic() - started, 2), flush=True)

        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(run, old_files))
        if not (OUT / 'complete.json').exists():
            write_new(OUT / 'complete.json', {'cases': 40, 'all_old_fields_exact': True, 'build_sha256': sha(build_path)})
        if not (EXP / 'results/native_report.json').exists():
            subprocess.run(['uv', 'run', '--frozen', str(EXP / 'scripts/analyse_native.py')], cwd=ROOT, check=True)
        status = 0
    finally:
        (OUT / 'session.exit').write_text(str(status) + '\n')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    if '--worker' in sys.argv:
        worker()
    else:
        with (OUT / 'session.log').open('x') as log:
            p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker'], cwd=ROOT,
                                 stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        print('Queued native audit PID', p.pid)
