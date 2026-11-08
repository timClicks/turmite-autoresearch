# /// script
# dependencies = ["scipy"]
# ///
"""Corrected per-decade genuine late-highway yields after this check, and Fisher exact tests between decades.
Counts: (1e8,1e9] from results/classify.txt (this experiment); (1e9,1e10] and (1e10,1e11] from
experiments/archive/2026-10-late-highway-board-check (16/807, 12/732).
uv run --script experiments/active/2026-11-late-highway-1e8-board-check/scripts/yields.py > .../results/yields.txt"""
from scipy.stats import fisher_exact

rows = [("(1e8,1e9] found by 1e9 rerun", 11, 854), ("(1e8,1e9] by onset", 10, 854),
        ("(1e9,1e10]", 16, 807), ("(1e10,1e11]", 12, 732)]
for name, k, n in rows:
    print(f"{name}: {k}/{n} = {k / n:.2%}")
for a, b in [(0, 2), (1, 2), (2, 3), (0, 3)]:
    (na, ka, Na), (nb, kb, Nb) = rows[a], rows[b]
    p = fisher_exact([[ka, Na - ka], [kb, Nb - kb]])[1]
    print(f"Fisher exact {na} vs {nb}: p = {p:.2f}")
