# /// script
# dependencies = []
# ///
"""Frozen rule lists for follow-up B (Moore lattice). Same recipe as make_lists.py, seed 20261021.
usage: uv run experiments/archive/2026-10-lattice-c-law/scripts/make_lists_moore.py -> results/lists/moore_{ants,controls}.txt"""
import random
from pathlib import Path

SEED, PER_CELL = 20261021, 48
out = Path(__file__).resolve().parents[1] / "results" / "lists"
rng = random.Random(SEED)
ALPHA = "rlRL"


def primitive(s):
    n = len(s)
    return not any(n % p == 0 and s[:p] * (n // p) == s for p in range(1, n))


lines = []
for s0 in ["r", "R"]:
    for m in range(1, 6):
        seen, got = set(), 0
        while got < PER_CELL:
            n = rng.randint(10, 14)
            rule = s0 * m + rng.choice([c for c in ALPHA if c != s0]) + "".join(rng.choice(ALPHA) for _ in range(n - m - 1))
            if rule in seen or not primitive(rule):
                continue
            seen.add(rule)
            got += 1
            lines.append(f"moore ant:{rule}")
(out / "moore_ants.txt").write_text("\n".join(lines) + "\n")
ctl = [f"moore rw:{s}" for s in range(1, 33)] + [f"moore mf:{s}" for s in range(1, 9)]
(out / "moore_controls.txt").write_text("\n".join(ctl) + "\n")
print(len(lines), "ants,", len(ctl), "controls")
