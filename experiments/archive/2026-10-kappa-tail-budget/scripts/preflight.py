from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
for name in ('README.md', 'PLAN.md', 'SCHEMA.md', 'HANDOFF.md', 'NOTEBOOK.md', 'notebook.ipynb'):
    path = EXP / name
    assert path.is_file(), path
    print(hashlib.sha256(path.read_bytes()).hexdigest(), path.relative_to(ROOT))
notebook = json.loads((EXP / 'notebook.ipynb').read_text(encoding='utf-8-sig'))
assert notebook['nbformat'] == 4
assert len(notebook['cells']) >= 7
print('Scaffold complete. Scientific status: NOT RUN. No results written.')
