"""Compile the three editorial drafts; record actual inputs without rerunning science."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SLUGS = ('growth-census', 'boundary-transport', 'ant-rotor-boundaries')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--font-path', type=Path, default=Path('/mnt/c/Windows/Fonts'))
    args = parser.parse_args()
    version = subprocess.check_output(['typst', '--version'], text=True).strip()
    records = {}
    for slug in SLUGS:
        folder = HERE / slug
        command = ['typst', 'compile', '--root', str(ROOT)]
        if args.font_path.is_dir():
            command += ['--font-path', str(args.font_path)]
        command += [str(folder/'main.typ'), str(folder/'main.pdf')]
        run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        (folder/'compile.log').write_text(run.stdout+run.stderr, encoding='utf-8')
        if run.returncode:
            raise RuntimeError(f'{slug}: compilation failed: {run.stderr}')
        source = (folder/'main.typ').read_text(encoding='utf-8-sig')
        paths = {folder/'main.typ', HERE/'editorial.typ', HERE/'provenance/synthesis-source.typ.txt'}
        if slug == 'boundary-transport':
            paths.add(ROOT/'experiments/archive/2026-10-kappa-prefix-family-holdout/README.md')
            paths.add(ROOT/'experiments/archive/2026-10-kappa-prefix-family-holdout/results/holdout.json')
        for value in re.findall(r'(?:json|image|bibliography)\("([^"]+)"', source):
            paths.add((folder/value).resolve())
        # The hero path is relative to Typst's project root.
        for value in re.findall(r'hero: "([^"]+)"', source):
            paths.add(ROOT/value.lstrip('/'))
        inputs = {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)}
        font_hashes = {}
        if args.font_path.is_dir():
            for p in sorted(args.font_path.glob('georg*.ttf')):
                font_hashes[p.name] = sha(p)
        records[slug] = {'command': command, 'inputs_sha256': inputs,
                         'georgia_fonts_sha256': font_hashes,
                         'pdf_sha256': sha(folder/'main.pdf'),
                         'diagnostics': run.stderr}
        provenance = json.loads((folder/'provenance.json').read_text())
        provenance['draft_sha256'] = sha(folder/'main.typ')
        provenance['additional_qualification'] = ('The transport draft also references the 2026-10-20 family hold-out README and ACTIVE.md; no new result was computed.')
        (folder/'provenance.json').write_text(json.dumps(provenance, indent=2)+'\n')
        print(f'{slug}: compiled', flush=True)
    manifest = {'typst': version, 'git_commit_at_build': subprocess.check_output(
        ['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'note': 'Sources may be uncommitted; content hashes identify actual inputs.', 'papers': records}
    (HERE/'build.json').write_text(json.dumps(manifest, indent=2)+'\n')

if __name__ == '__main__':
    main()

