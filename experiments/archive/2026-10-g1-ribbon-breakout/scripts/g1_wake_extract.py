# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Small committed extract of the two RLRLLL builder dumps, so the paper figure never reads dumps/.

Inputs (gitignored, bulk; made by examples/g1_ribbon_breakout_builder_dump.rs, see scripts/g1_builder_run.sh and
notes/g1-builder-structure-2026-10-14.md):  <DUMPS>/g1_<T0>.traj.csv and g1_<T0>.wake.bin for T0 = 12800000000, 12900000000.
usage: uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_wake_extract.py <DUMPS_DIR>
Outputs (results/): g1_wake_extract.json (L, |x|, cycle timing, column-lag agreement, input sha256),
g1_wake_shape_<T0>.csv (per wake column: first/last visited row, count), g1_wake_crop_<T0>.csv (colour crop, y-major),
g1_sweep_trace_<T0>.csv (y(t) every 100 steps). Deterministic: no randomness, same bytes on rerun."""
import hashlib, json, sys
from pathlib import Path
import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "experiments/archive/2026-10-g1-ribbon-breakout/results"
DUMPS = Path(sys.argv[1])
T0S = (12800000000, 12900000000)
BOARD_C = 16384            # builder_dump writes offsets from the centre of the 32768 board
CROP_COLS, CROP_ROWS = 36, 80  # 12 colour periods x 80 rows, anchored at the low-y end of the wake


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


res = {"command": "uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_wake_extract.py <DUMPS_DIR>",
       "raw_source_worktree_commit": "c82030e",
       "raw_recipe": "cargo run --release --example g1_ribbon_breakout_builder_dump -- RLRLLL T0 400000 OUTPREFIX 32768 800; T0=12800000000,12900000000",
       "seed": "none: one deterministic blank-board trajectory",
       "source_sha256": {"extractor": sha(Path(__file__)),
                         "exporter": sha(ROOT / "examples/g1_ribbon_breakout_builder_dump.rs")},
       "inputs_sha256": {}, "dumps": {}}
for t0 in T0S:
    traj_p, wake_p = DUMPS / f"g1_{t0}.traj.csv", DUMPS / f"g1_{t0}.wake.bin"
    res["inputs_sha256"][traj_p.name], res["inputs_sha256"][wake_p.name] = sha(traj_p), sha(wake_p)
    tr = pl.read_csv(traj_p)
    x, y = tr["x"].to_numpy(), tr["y"].to_numpy()
    with open(wake_p, "rb") as f:
        x0, x1, size = map(int, f.readline().split())
        w = np.frombuffer(f.read(), dtype=np.uint8).reshape(size, x1 - x0)
    vis = w != 255
    rows = np.flatnonzero(vis.any(axis=1))
    cnt = vis.sum(axis=0)
    ant_col = int(x[-1]) + BOARD_C - x0               # the ant's column index inside the wake array
    # wake columns are "complete" where they span the full sweep height (count >= 0.9 x max)
    full = np.flatnonzero(cnt >= 0.9 * cnt.max())
    ymin = np.where(vis.any(axis=0), vis.argmax(axis=0), -1)
    ymax = np.where(vis.any(axis=0), size - 1 - vis[::-1].argmax(axis=0), -1)
    pl.DataFrame({"col": np.arange(x1 - x0), "dx_from_ant": np.arange(x1 - x0) - ant_col,
                  "ymin": ymin - BOARD_C, "ymax": ymax - BOARD_C, "count": cnt}).write_csv(OUT / f"g1_wake_shape_{t0}.csv")
    # lag agreement over cells visited in both columns
    lag = {}
    for p in (1, 2, 3, 4, 5, 6, 12, 24):
        a, b = w[:, :-p], w[:, p:]
        m = (a != 255) & (b != 255)
        lag[p] = float(((a == b) & m).sum() / m.sum())
    h = np.bincount(w[vis], minlength=6); h = h / h.sum()
    # crop: CROP_COLS complete columns starting mid-wake, CROP_ROWS rows from the wake's low-y end
    # anchored 8 rows below the median first-visited row of those columns so the wake's low-y boundary is in frame
    c0 = int(full[len(full) // 2]); r0 = int(np.median(ymin[c0:c0 + CROP_COLS])) - 8
    crop = w[r0:r0 + CROP_ROWS, c0:c0 + CROP_COLS]
    pl.DataFrame({"row": np.repeat(np.arange(CROP_ROWS), CROP_COLS), "col": np.tile(np.arange(CROP_COLS), CROP_ROWS),
                  "colour": crop.ravel().astype(int)}).write_csv(OUT / f"g1_wake_crop_{t0}.csv")
    # Sweep trace: y every 100 steps; these samples are not smoothed.
    pl.DataFrame({"t_rel": np.arange(0, len(y), 100), "y": y[::100]}).write_csv(OUT / f"g1_sweep_trace_{t0}.csv")
    res["dumps"][str(t0)] = {
        "steps": int(len(x)), "x_start": int(x[0]), "x_end": int(x[-1]), "distinct_x": int(len(np.unique(x))),
        "traj_y_range": [int(y.min()), int(y.max())], "L_traj": int(y.max() - y.min() + 1),
        "wake_rows": [int(rows.min()) - BOARD_C, int(rows.max()) - BOARD_C], "L_wake": int(rows.max() - rows.min() + 1),
        "ant_col": ant_col, "wake_x0": x0, "wake_x1": x1, "complete_cols": [int(full[0]), int(full[-1])],
        "colour_share": [round(float(v), 4) for v in h], "col_lag_agreement": lag,
        "crop": {"col0": c0, "row0": r0, "cols": CROP_COLS, "rows": CROP_ROWS, "file": f"g1_wake_crop_{t0}.csv"},
    }
(OUT / "g1_wake_extract.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res["dumps"], indent=1))
