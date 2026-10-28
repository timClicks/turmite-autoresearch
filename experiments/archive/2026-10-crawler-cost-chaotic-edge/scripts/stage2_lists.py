"""Stage 2 run list (README): fresh Pi(m) rules, n in 13..18, m in 2..6, up to 60 per m, plus one composition-matched
non-Pi control each. Rule strings only. -> results/lists/s2_cohort.csv, s2_specs.txt

usage: uv run --frozen experiments/archive/2026-10-crawler-cost-chaotic-edge/scripts/stage2_lists.py
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1] / "results/lists"
sys.path.insert(0, str(ROOT / "experiments/archive/2026-10-square-ring-fillers/scripts"))
from ring import pi_k  # noqa: E402

SEED = 20261026


def lead(r):
    k = 1
    while k < len(r) and r[k] == r[0]:
        k += 1
    return k


def primitive(r):
    n = len(r)
    return all(r != r[:d] * (n // d) for d in range(1, n) if n % d == 0)


def main():
    rng = np.random.default_rng(SEED)
    rows = []
    for m in range(2, 7):
        pis, by_key = [], {}
        for n in range(13, 19):
            # every primitive rule with lead m: R^m L + free suffix
            for suf in itertools.product("LR", repeat=n - m - 1):
                r = "R" * m + "L" + "".join(suf)
                if not primitive(r):
                    continue
                if pi_k(r) == m:
                    pis.append(r)
                elif pi_k(r) is None:
                    by_key.setdefault((n, r.count("R")), []).append(r)
        pis.sort(key=lambda r: (len(r), r))
        pick = pis if len(pis) <= 60 else [pis[i] for i in sorted(rng.choice(len(pis), 60, replace=False))]
        for r in pick:
            pool = sorted(by_key.get((len(r), r.count("R")), []))
            c = pool[rng.integers(len(pool))] if pool else ""
            rows.append((r, c, m, len(r)))
        print(f"m={m}: Pi available {len(pis)}, sampled {len(pick)}, without control {sum(1 for x in rows if x[2] == m and not x[1])}")
    df = pl.DataFrame(rows, schema=["rule", "control", "m", "n"], orient="row")
    df.write_csv(OUT / "s2_cohort.csv")
    specs = list(dict.fromkeys(df["rule"].to_list() + [c for c in df["control"] if c]))
    (OUT / "s2_specs.txt").write_text("\n".join(specs) + "\n")


if __name__ == "__main__":
    main()
