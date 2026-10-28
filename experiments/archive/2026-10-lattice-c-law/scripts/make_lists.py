# /// script
# dependencies = []
# ///
"""Frozen rule lists for the lattice c-law study (README, 'Rule lists'). seed 20261020.
usage: uv run experiments/archive/2026-10-lattice-c-law/scripts/make_lists.py
Writes results/lists/{ants,controls}.txt: one `LATTICE MOVER` per line."""
import random
from pathlib import Path

SEED, PER_CELL = 20261020, 48
out = Path(__file__).resolve().parents[1] / "results" / "lists"
out.mkdir(parents=True, exist_ok=True)
rng = random.Random(SEED)

ALPHA = {"square": "LR", "tri": "LR", "hex": "rlRL"}
STRATA = {"square": ["R"], "tri": ["R"], "hex": ["r", "R"]}  # canonical first letter (mirror)


def primitive(s):
    n = len(s)
    return not any(n % p == 0 and s[:p] * (n // p) == s for p in range(1, n))


lines = []
for lat in ["square", "tri", "hex"]:
    for s0 in STRATA[lat]:
        for m in range(1, 6):
            seen, got = set(), 0
            while got < PER_CELL:
                n = rng.randint(10, 14)
                other = [c for c in ALPHA[lat] if c != s0]
                rule = s0 * m + rng.choice(other) + "".join(rng.choice(ALPHA[lat]) for _ in range(n - m - 1))
                if rule in seen or not primitive(rule):
                    continue
                seen.add(rule)
                got += 1
                lines.append(f"{lat} ant:{rule}")
(out / "ants.txt").write_text("\n".join(lines) + "\n")

ctl = []
for lat in ["square", "tri", "hex"]:
    ctl += [f"{lat} rw:{s}" for s in range(1, 33)] + [f"{lat} mf:{s}" for s in range(1, 9)]
(out / "controls.txt").write_text("\n".join(ctl) + "\n")
print(len(lines), "ants,", len(ctl), "controls")
