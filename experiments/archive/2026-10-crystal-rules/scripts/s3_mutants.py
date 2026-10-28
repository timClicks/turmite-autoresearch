# /// script
# dependencies = ["polars"]
# ///
"""S3 mutation map. `gen` writes results/s3_rules.txt (all Hamming-1 and -2 mutants of the seeds + controls, plus the seeds);
`tab` reads results/s3_census.csv (examples/crystal_s4 on that list) and tabulates by position.
usage: s3_mutants.py gen | tab"""
import sys
from itertools import combinations
from pathlib import Path

root = Path(__file__).resolve().parents[1]
SEEDS = ["RLLLLRRL", "RLLLLLRRL", "RLLLLLLLRRLRR"]
CONTROLS = ["RRRRRLLLLLL", "RLLLLRRRRLR", "RLRLLL"]
flip = {"L": "R", "R": "L"}

def mutants(r):
    out = {}
    for i in range(len(r)):
        out[(i,)] = r[:i] + flip[r[i]] + r[i + 1:]
    for i, j in combinations(range(len(r)), 2):
        s = list(r); s[i] = flip[s[i]]; s[j] = flip[s[j]]
        out[(i, j)] = "".join(s)
    return out

if sys.argv[1] == "gen":
    rules = []
    for r in SEEDS + CONTROLS:
        rules.append(r)
        rules += list(mutants(r).values())
    seen, uniq = set(), []
    for r in rules:
        if r not in seen:
            seen.add(r); uniq.append(r)
    (root / "results" / "s3_rules.txt").write_text("\n".join(uniq) + "\n")
    print(len(uniq), "rules")
else:
    import polars as pl
    df = pl.read_csv(root / "results" / "s3_census.csv")
    d = {r: row for r, row in zip(df["rule"], df.iter_rows(named=True))}
    def is_crystal(row):
        # proxy registered in README/NOTEBOOK: box filled, ground state 2x, ground fraction < 0.95
        return (row["steps_per_visited"] < 10 and row["visited_over_bbox"] >= 0.9 and not row["left_board"]
                and row["Gv"] == 2 and row["ground_frac"] < 0.95)
    for r in SEEDS + CONTROLS:
        m1 = mutants(r)
        base = is_crystal(d[r])
        print(f"\n{r}: crystal-proxy={base}  steps/visited={d[r]['steps_per_visited']:.2f} ground_frac={d[r]['ground_frac']:.3f}")
        line = []
        for i in range(len(r)):
            row = d[m1[(i,)]]
            tag = "C" if is_crystal(row) else ("F" if (row["steps_per_visited"] < 10 and row["visited_over_bbox"] >= 0.9) else ("H" if row["left_board"] else "."))
            line.append(f"{r[i]}{tag}")
        print("Hamming-1 (letter + class of the mutant; C crystal-proxy, F filled flat/other, H left board, . other):", " ".join(line))
        two = [is_crystal(d[v]) for k, v in mutants(r).items() if len(k) == 2]
        print(f"Hamming-2: {sum(two)}/{len(two)} crystal-proxy")
