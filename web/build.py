"""Assemble the explorer page from sweep results, portraits and JS.

usage: python3 web/build.py OUT.html
"""
import base64
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT

v2 = pl.read_csv(DATA / "experiments/archive/2026-10-census-sweeps/results/sweep_v2.csv")
BUDGET = int(v2["steps"].max())
# Keep only highways re-confirmed on two board sizes with identical onsets;
# demote the rest (square-builders whose pass crossed the edge) to unresolved.
confirmed = pl.read_csv(DATA / "experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv")
ok = set(confirmed.filter(pl.col("confirmed"))["rule"])
v2 = v2.with_columns(
    [pl.when(pl.col("rule").is_in(ok)).then(pl.col(c)).otherwise(None).alias(c) for c in ["period", "dx", "dy", "onset"]]
)

highways = v2.filter(pl.col("period").is_not_null())
rows = [
    {"rule": r["rule"], "n": r["n"], "onset": r["onset"], "period": r["period"], "dx": r["dx"], "dy": r["dy"], "late": False}
    for r in highways.iter_rows(named=True)
]

# The one-more-decade test: unresolved rules of length <= 10, run to 1e9.
small = v2.filter(pl.col("n") <= 10)
o = small.filter(pl.col("period").is_not_null())["onset"].to_numpy()
edges = [10**k for k in range(2, 9)]
past = [int(((o > a) & (o <= b)).sum()) for a, b in zip(edges[:-1], edges[1:])]
test = {"rules": int(small.filter(pl.col("period").is_null()).height), "past": past, "lo": min(past), "hi": max(past), "found": None}

big_path = DATA / "experiments/archive/2026-10-census-sweeps/results/sweep_1B.csv"
big = pl.read_csv(big_path)
assert big.height == test["rules"], (big.height, test["rules"])
conf = pl.read_csv(DATA / "experiments/archive/2026-10-census-sweeps/results/confirmed_1B.csv").filter(pl.col("confirmed"))
# A highway that began before 1e8 but only reached the edge after the 1e8
# budget belongs to the earlier decade, so fold it back into "past".
older = conf.filter(pl.col("onset") <= 10**8)
fresh = conf.filter(pl.col("onset") > 10**8)
o_all = np.concatenate([o, older["onset"].to_numpy()])
test["past"] = [int(((o_all > a_) & (o_all <= b_)).sum()) for a_, b_ in zip(edges[:-1], edges[1:])]
test["lo"], test["hi"] = min(test["past"]), max(test["past"])
spc = big["steps"] / (big["width"] * big["height"])
not_hw = ~big["rule"].is_in(list(conf["rule"]))
builders = int((not_hw & ((big["stop"] == "escaped") | (spc < 20))).sum())
test.update(
    found=fresh.height,
    older=older.height,
    builders=builders,
    still=int(big.height - conf.height - builders),
    budget=int(big["steps"].max()),
)
for r in conf.iter_rows(named=True):
    rows.append({"rule": r["rule"], "n": r["n"], "onset": r["onset"], "period": r["period"], "dx": r["dx"], "dy": r["dy"], "late": True})

verdict_path = DATA / "experiments/archive/2026-10-knockout-maps/results/verdict.html"
test["verdict"] = verdict_path.read_text() if verdict_path.exists() else ""

census = pl.read_csv(DATA / "experiments/archive/2026-10-census-sweeps/results/census.csv")
grow = census.filter(pl.col("cls") != "builder")["alpha"].to_numpy()
bins = np.round(np.arange(0.0, 0.625, 0.025), 3)
hist, _ = np.histogram(np.clip(grow, 0, 0.6 - 1e-9), bins=bins)
counts = dict(census.group_by("cls").len().iter_rows())
blob_alpha = census.filter(pl.col("cls") == "blob")["alpha"]
data_census = {
    "highway": len(ok), "builder": counts.get("builder", 0), "log": counts.get("log", 0), "blob": counts.get("blob", 0),
    "bins": bins.tolist(), "hist": hist.tolist(), "blob_median": round(float(blob_alpha.median()), 3),
}
assert sum(data_census[k] for k in ["highway", "builder", "log", "blob"]) == v2.height

cube = json.loads((DATA / "experiments/archive/2026-10-probe-growth-census/results/cube_stats.json").read_text())
occ = json.loads((ROOT / "experiments/archive/2026-10-occupancy-pages/results/page_occ.json").read_text())
data = {"total": v2.height, "budget": BUDGET, "highways": rows, "test": test, "census": data_census, "cube": cube, "occ": occ,
        "follow": json.loads((DATA / "experiments/archive/2026-10-knockout-maps/results/followup_stats.json").read_text()),
        "calib": {"A": json.loads((DATA / "experiments/archive/2026-10-calib-instrument-calibration/results/calib_partA.json").read_text()), "B": json.loads((DATA / "experiments/archive/2026-10-calib-instrument-calibration/results/calib_partB.json").read_text()),
                  "contour": json.loads((DATA / "experiments/archive/2026-10-calib-instrument-calibration/results/calib_contour_page.json").read_text()),
                  "patched": json.loads((DATA / "experiments/archive/2026-10-calib-instrument-calibration/results/calib_patched.json").read_text())}}

imgs = {}
for png in sorted((ROOT / "experiments/archive/2026-10-snapshots/results").glob("*.png")):
    imgs[png.stem] = "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode()
wanted = ["RL", "RLR", "LLRR", "RRRRLL", "RRLRRRRRRLRL", "RRLRLLRRR", "RRRLRLLRRRLR", "RRLRLLRLRRLR"]
imgs = {k: imgs[k] for k in wanted}
for r in ["RRRRRLLLLLL", "RLR", "RLLLLLRRLRR"]:
    imgs["occ_" + r] = "data:image/png;base64," + base64.b64encode((ROOT / "experiments/archive/2026-10-occupancy-pages/results" / f"page_{r}.png").read_bytes()).decode()

page = (ROOT / "web" / "template.html").read_text()
sim = (ROOT / "web" / "sim.js").read_text()
js = (ROOT / "web" / "page.js").read_text()
page = page.replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))
page = page.replace("/*IMGS*/null", json.dumps(imgs))
page = page.replace("/*SIM*/", sim)
page = page.replace("/*PAGE*/", js)
Path(sys.argv[1]).write_text(page)
print(f"{sys.argv[1]}: {len(page)/1024:.0f} KB, {len(rows)} highways, test={ {k: v for k, v in test.items() if k != 'verdict'} }")
