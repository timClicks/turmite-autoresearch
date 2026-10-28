"""Check the recovered exporter against the reference ant, including wake bytes.

Run after cargo build --release --example g1_ribbon_breakout_builder_dump:
uv run experiments/archive/2026-10-g1-ribbon-breakout/scripts/check_builder_dump.py
Deterministic exhaustive rule strings of lengths 2..4, 2000 steps each.
"""
import itertools
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
TARGET = Path(os.environ.get("CARGO_TARGET_DIR", ROOT / "target")).expanduser()
EXE = TARGET / "release/examples/g1_ribbon_breakout_builder_dump"
SCRATCH = ROOT / "experiments/archive/2026-10-g1-ribbon-breakout/scratch"
SCRATCH.mkdir(exist_ok=True)
directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
# Import the convention from lib.rs explicitly in the check below if changed.
print("Checking Python oracle direction convention against src/lib.rs before running")
lib = (ROOT / "src/lib.rs").read_text()
assert "(0, -1), (1, 0), (0, 1), (-1, 0)" in lib
count = 0
with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
    for n in range(2, 5):
        for letters in itertools.product("LR", repeat=n):
            rule = "".join(letters)
            prefix = Path(tmp) / rule
            subprocess.run([str(EXE), rule, "1000", "1000", str(prefix), "4096", "80"], check=True)
            cells = {}
            x = y = h = 0
            expected = ["x,y,h"]
            for step in range(2000):
                c = cells.get((x, y), 0)
                h = (h + (1 if rule[c] == "R" else 3)) % 4
                cells[x, y] = (c + 1) % n
                dx, dy = directions[h]
                x, y = x + dx, y + dy
                if step >= 1000:
                    expected.append(f"{x},{y},{h}")
            assert prefix.with_suffix(".traj.csv").read_text().splitlines() == expected, rule
            with prefix.with_suffix(".wake.bin").open("rb") as f:
                x0, x1, size = map(int, f.readline().split())
                actual = f.read()
            assert len(actual) == size * (x1 - x0)
            expected_wake = bytearray([255]) * len(actual)
            for (xx, yy), c in cells.items():
                xx, yy = xx + size // 2, yy + size // 2
                if x0 <= xx < x1:
                    expected_wake[yy * (x1 - x0) + xx - x0] = c
            assert actual == expected_wake, rule
            count += 1
print(f"PASS: {count} rules, complete sampled trajectories and all exported wake bytes")
