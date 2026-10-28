"""Highway hazard per at-risk rule, per decade of onset time, from the whole length<=10 census (1e1 .. 1e11).

At risk at the start of decade k: rules not yet resolved, i.e. no highway onset and no board escape before 10^k.
Event: a highway whose onset lies in decade k. A rule leaves the risk set at its onset (highway) or at its escape step
(escape without highway). Rules still running at the last horizon they were run to are censored there.
Outcome of a rule = its row in the longest sweep that contains it (h1e11 > h1e10 > sweep_1B > sweep_v2).
Board fillers and the board-truncated ray of experiments/archive/2026-10-late-highway-board-check are treated as escapes, not highways.
Population: rules of length <= 10 (the 854 unresolved at 1e8 are the budget rows of that population).
Caveats: sweep_v2 / sweep_1B boards were never put through the second-board confirm test (board-check README); decades are by
highway ONSET time here, whereas the board-check README bins by the horizon at which the highway was found (one onset, 98,645,078, is
found by the 1e9 run but lies in 1e7-1e8); the 1e11 sweep covers 732 of the 807 survivors of 1e10 (the other 75 resolved earlier).
Run: uv run --frozen experiments/proposed/2026-10-late-highway-fourth-decade/scripts/hazard_all_decades.py
"""
import pathlib, math
import polars as pl

ROOT = pathlib.Path(__file__).resolve().parents[4]
X = ROOT / "experiments"
SRC = [  # lowest priority first
    ("v2", X / "2026-10-census-sweeps/results/sweep_v2.csv", 1e8),
    ("1B", X / "2026-10-census-sweeps/results/sweep_1B.csv", 1e9),
    ("1e10", sorted((X / "2026-10-highways-unresolved-rules-1e10-1e11/results/h1e10").glob("chunk_*.csv")), 1e10),
    ("1e11", sorted((X / "2026-10-highways-unresolved-rules-1e10-1e11/results/h1e11").glob("chunk_*.csv")), 1e11),
]
out = {}
for tag, paths, horizon in SRC:
    for p in ([paths] if isinstance(paths, pathlib.Path) else paths):
        for r in pl.read_csv(p, infer_schema_length=0).iter_rows(named=True):
            if int(r["n"]) <= 10:  # sweep_v2 also holds lengths 11-12, which were never carried past 1e8
                out[r["rule"]] = dict(src=tag, horizon=horizon, **r)

bad = set()  # fillers and the ray, from classify.txt
for line in (X / "2026-10-late-highway-board-check/results/classify.txt").read_text().splitlines():
    c = [x.strip() for x in line.strip("│ ").split("┆")]
    if len(c) >= 8 and c[0].startswith("(1e") and (c[-1] == "true" or c[1] == "RLLLRLRRR"):
        bad.add(c[1])

ev = []  # (rule, time, kind) kind in highway / escape / censored
for r, v in out.items():
    if v["stop"] == "escaped" and v["onset"] and r not in bad:
        ev.append((r, float(v["onset"]), "highway"))
    elif v["stop"] == "escaped":
        ev.append((r, float(v["steps"]), "escape"))
    else:
        ev.append((r, v["horizon"], "censored"))
df = pl.DataFrame(ev, schema=["rule", "t", "kind"], orient="row")
print(f"{df.height} rules (length<=10 census); kinds: {dict(df.group_by('kind').len().iter_rows())}; excluded as artefacts: {len(bad)}")
print(f"{'decade':>11} {'at risk':>8} {'highways':>9} {'hazard %':>9} {'escapes':>8}   95% Poisson")
rows = []
for k in range(1, 11):
    lo, hi = 10.0 ** k, 10.0 ** (k + 1)
    risk = df.filter(((pl.col("kind") != "censored") & (pl.col("t") >= lo)) | ((pl.col("kind") == "censored") & (pl.col("t") >= hi))).height
    hw = df.filter((pl.col("kind") == "highway") & (pl.col("t") >= lo) & (pl.col("t") < hi)).height
    es = df.filter((pl.col("kind") == "escape") & (pl.col("t") >= lo) & (pl.col("t") < hi)).height
    # normal approx on the rate, fine for hw >= 10; for small counts it is only indicative
    se = math.sqrt(max(hw, 1)) / max(risk, 1)
    print(f"1e{k}-1e{k+1:<3} {risk:>8} {hw:>9} {100*hw/max(risk,1):>9.2f} {es:>8}   +-{100*1.96*se:.2f}")
    rows.append((k, risk, hw))
pl.DataFrame(rows, schema=["k", "at_risk", "highways"], orient="row").write_csv(ROOT / "experiments/proposed/2026-10-late-highway-fourth-decade/results/hazard_by_decade.csv")
