"""Compress the RLRLLL snapshot frames (scratch/, ~3.5 GB) into small committed results.

Run: uv run experiments/archive/2026-10-rlrlll-portrait/scripts/render.py
Inputs: scratch/frames/frame_T.bin, crop_T.bin from scripts/run_frames.sh (format in examples/rlrlll_portrait_frames.rs).
Outputs (results/):
  arrival_b16.png  8-bit map over the final territory's bounding box, one pixel per 16x16 block: value k >= 1 means
                   the block first had at least half its cells visited in frame k-1 (frames.json order); 0 = never.
  crop_<name>.png  raw cell colours (255 = unvisited) of two 256x256 windows around the ant, one inside the blob
                   before the switch and one in the sweeper's wake.
  frames.json      per frame: t, ant position, exact visited-cell count, front x; plus bbox and crop provenance.
No randomness, fits or statistics: counts and pictures only.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
FRAMES = HERE / "scratch/frames"
OUT = HERE / "results"
HALF = 0.5          # a block counts as reached once half its cells are visited
MARGIN = 2          # blocks of empty border kept around the final territory


def read_frame(path):
    raw = path.read_bytes()
    head, body = raw.split(b"\n", 1)
    t, ax, ay, size, block, n = map(int, head.split())
    nb = size // block
    counts = np.frombuffer(body, dtype="<u2").reshape(nb, nb, n)
    return dict(t=t, ant=(ax, ay), size=size, block=block, n=n), counts


def read_crop(path):
    raw = path.read_bytes()
    head, body = raw.split(b"\n", 1)
    t, x0, y0, w, h = map(int, head.split())
    return dict(t=t, x0=x0, y0=y0), np.frombuffer(body, dtype=np.uint8).reshape(h, w)


def main():
    paths = sorted(FRAMES.glob("frame_*.bin"), key=lambda p: int(p.stem.split("_")[1]))
    assert len(paths) == 59, f"expected 58 listed frames + the exit frame, found {len(paths)}"
    meta, frac, frames = None, [], []
    for p in paths:
        m, counts = read_frame(p)
        meta = meta or m
        visited = counts.sum(axis=2, dtype=np.int64)
        cols = np.flatnonzero(visited.any(axis=0))
        frames.append(dict(t=m["t"], ant_x=m["ant"][0], ant_y=m["ant"][1], visited_cells=int(visited.sum()),
                           front_block_x=int(cols[0] * m["block"] - m["size"] // 2)))
        frac.append(visited / m["block"] ** 2)
        print(p.name, frames[-1])
    frac = np.stack(frac)
    reached = frac >= HALF
    arrival = np.where(reached.any(axis=0), reached.argmax(axis=0) + 1, 0)
    ys, xs = np.nonzero(frac[-1] > 0)
    y0, y1 = max(ys.min() - MARGIN, 0), ys.max() + MARGIN + 1
    x0, x1 = max(xs.min() - MARGIN, 0), xs.max() + MARGIN + 1
    assert arrival.max() < 256
    OUT.mkdir(exist_ok=True)
    Image.fromarray(arrival[y0:y1, x0:x1].astype(np.uint8), mode="L").save(OUT / "arrival_b16.png", optimize=True)

    # Blob texture just before the switch; wake texture from a late frame with the ant mid-column, away from the
    # wedge's top and bottom motifs.
    ts = [f["t"] for f in frames]
    picks = {"blob": 12_600_000_000, "wake": 12_900_000_000}
    crops = {}
    for name, t in picks.items():
        assert t in ts
        c, img = read_crop(FRAMES / f"crop_{t}.bin")
        Image.fromarray(img, mode="L").save(OUT / f"crop_{name}.png", optimize=True)
        crops[name] = c

    c = meta["size"] // 2
    out = dict(command="uv run experiments/archive/2026-10-rlrlll-portrait/scripts/render.py",
               rule="RLRLLL", board=meta["size"], block=meta["block"], reached_fraction=HALF,
               bbox_blocks=dict(x0=int(x0), x1=int(x1), y0=int(y0), y1=int(y1)),
               bbox_cells=dict(x0=int(x0 * meta["block"] - c), y0=int(y0 * meta["block"] - c),
                               w=int((x1 - x0) * meta["block"]), h=int((y1 - y0) * meta["block"])),
               crops=crops, frames=frames,
               sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in [HERE / "results/run_frames.log", HERE / "scripts/times.txt", Path(__file__)]})
    (OUT / "frames.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "frames"}, indent=1))


if __name__ == "__main__":
    main()
