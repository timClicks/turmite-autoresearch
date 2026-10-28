"""Append/refresh the archival figure section, preserving the existing study.

uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/update_figure_notebook.py
Then execute with uv run --with nbconvert --with ipykernel jupyter nbconvert
--to notebook --execute --inplace experiments/archive/2026-10-g1-ribbon-breakout/notebook.ipynb
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
path = ROOT / "experiments/archive/2026-10-g1-ribbon-breakout/notebook.ipynb"
nb = json.loads(path.read_text())
nb["cells"] = [c for c in nb["cells"] if not c.get("id", "").startswith("figure-")]


def cell(kind, name, source):
    c = dict(cell_type=kind, id="figure-" + name, metadata={}, source=source.splitlines(keepends=True))
    if kind == "code":
        c.update(execution_count=None, outputs=[])
    nb["cells"].append(c)


cell("markdown", "intro", """## Archival figure: question and assumptions (2026-10-16)
Can one figure show the late efficiency switch, the period-3 wake and the
quantitative sweep check? This is a presentation of existing measurements,
not a new experiment. See README.md and ../../notes/g1-builder-structure-2026-10-14.md.
One deterministic blank-board RLRLLL trajectory; no random seed, no independent
replication. Wake snapshots are taken after each 400,000-step dump.
""")
cell("code", "provenance", """from pathlib import Path
import hashlib, json, subprocess
import numpy as np
import polars as pl
import matplotlib.pyplot as plt
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / 'Cargo.toml').is_file())
G1 = ROOT / 'experiments/archive/2026-10-g1-ribbon-breakout/results'
names = ['g1_ribbon.csv', 'g1_wake_extract.json', 'g1_wake_crop_12800000000.csv', 'g1_sweep_trace_12800000000.csv']
print('commit:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
print('section date: 2026-10-16 NZDT; seed: none (deterministic blank board)')
for name in names:
    print(name, hashlib.sha256((G1 / name).read_bytes()).hexdigest())
ext = json.loads((G1 / 'g1_wake_extract.json').read_text())['dumps']
""")
cell("markdown", "method", """### Data, method and results
Original simulation: recovered `examples/g1_ribbon_breakout_builder_dump.rs`.
`scripts/g1_wake_extract.py` makes these compact results; the notebook reads
only committed results. The original post-hoc check fits |x| in a strict
±20,000,000-step window around each dump, then multiplies by 2|x(t0)|.
The model uses 3 columns per 12L steps, hence d|x|²/dt = |x|/(2L).
""")
cell("code", "rates", """d = pl.read_csv(G1 / 'g1_ribbon.csv').filter(pl.col('t_end') > 12_000_000_000)
rows = []
for t0 in (12_800_000_000, 12_900_000_000):
    e = ext[str(t0)]
    w = d.filter((pl.col('t_end') - t0).abs() < 20_000_000)
    t, x = w['t_end'].to_numpy(), np.abs(w['x'].to_numpy())
    pred = (abs(e['x_start']) + abs(e['x_end'])) / (4 * e['L_traj'])
    measured = 2 * np.interp(t0, t, x) * np.polyfit(t - t0, x, 1)[0]
    rows.append({'t0': t0, 'L': e['L_traj'], 'predicted': pred, 'measured': measured, 'windows': w.height})
print(pl.DataFrame(rows))
e = ext['12800000000']
crop = pl.read_csv(G1 / 'g1_wake_crop_12800000000.csv')['colour'].to_numpy().reshape(80, 36)[:48]
from matplotlib.colors import ListedColormap
palette = ['#e3e3e3', '#1fa187', '#e8a33d', '#7a3b8f', '#5fb3d9', '#8c6d31', '#ffffff']
fig, ax = plt.subplots(figsize=(2, 2.8))
ax.imshow(np.where(crop == 255, 6, crop), cmap=ListedColormap(palette), vmin=0, vmax=6, origin='lower', interpolation='nearest')
ax.set_title('Actual period-3 wake crop'); ax.set_axis_off(); plt.show()
""")
cell("markdown", "caveats", """### Caveats, controls and next steps
The wake has a strong three-column repeat, and the two local rates agree
with the sweep picture. These observations do not explain period 3 or the
trigger. The two heights and positions come from one trajectory; this is not
an independent test of L proportional to |x|, and no between-seed error bar
is available. Exporter trajectories and all wake bytes were checked against
an independent obvious ant loop for all 28 rule strings of lengths 2–4;
the Rust release suite is a separate simulator check. No estimator changed,
so no new rotor calibration is implied. See results/builder_oracle_check.log.
Next: obtain a third sweep-height sample and investigate the switching trigger.
""")
path.write_text(json.dumps(nb, indent=1) + "\n")
