"""P4 step 3: compare the committed predictions with the new sweep_lean exits (8192, 16384, 32768) and the census record
(32768 board, all chunks of experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10/).

usage: python3 experiments/archive/2026-10-square-ring-fillers/scripts/p4_compare.py   -> results/p4_analysis.txt
"""
import csv
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
CENSUS = ROOT / "experiments/archive/2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10"


def main():
    lines = (EXP / "results/p4_predictions.txt").read_text().splitlines()[1:]
    pred = {r["rule"]: r for r in csv.DictReader(lines)}
    census = {}
    for f in sorted(CENSUS.glob("chunk_*.csv")):
        for r in csv.DictReader(open(f)):
            if r["rule"] in pred:
                census[r["rule"]] = dict(r, source=f"census h1e10/{f.name}")
    out = ["P4: predicted vs observed exit steps (exact integers)", "rule,G,predicted,observed,source,match"]
    ok = tot = 0
    for g in (8192, 16384, 32768):
        runs = {r["rule"]: r for r in csv.DictReader(open(EXP / f"results/p4_board_{g}.csv"))}
        for rule, p in pred.items():
            srcs = [("sweep_lean rerun", runs[rule])]
            if g == 32768:
                srcs.append((census[rule]["source"], census[rule]))
            for name, row in srcs:
                e = int(p[f"E{g}"])
                o = int(row["steps"])
                m = e == o and row["stop"] == "escaped"
                ok += m
                tot += 1
                out.append(f"{rule},{g},{e},{o},{name},{'EXACT' if m else 'MISS by %d' % (o - e)}")
    alpha_ok = all(p["alpha==2(k+1)"] == "True" for p in pred.values())
    out += ["", f"(i) alpha = 2(k+1) exactly: {alpha_ok}", f"(ii) exact predictions: {ok}/{tot}",
            "VERDICT: P4 HELD" if alpha_ok and ok == tot else "VERDICT: P4 FAILED"]
    (EXP / "results/p4_analysis.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


main()
