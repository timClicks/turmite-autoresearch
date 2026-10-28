"""Numbers for the page's follow-up section on the two open questions.
Writes experiments/archive/2026-10-knockout-maps/results/followup_stats.json. Re-runs the transplant experiments.

Inputs: probe_summary.csv, census.csv, edgestats_sample.csv, c_model.csv,
mixing_stats.json, experiments/archive/2026-10-knockout-maps/dumps/ (from examples/dump.rs), and the transplant binary.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
D = ROOT
sys.path.insert(0, str(ROOT / "experiments/_lib"))  # shared helpers (tether.py)
from tether import density_profile, radial  # noqa: E402

out = {}

# --- Q2: c and the low-colour letters ------------------------------------
s = pl.read_csv(D / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(~pl.col("bursty"))
s = s.with_columns(p3=pl.col("rule").str.slice(1, 3)).filter(pl.col("p3").str.len_chars() == 3)
letters = s.group_by("p3").agg(c=pl.col("c").median(), n=pl.len()).sort("c", descending=True)
out["letters"] = [[r["p3"], round(r["c"], 3), r["n"]] for r in letters.iter_rows(named=True)]
s_all = pl.read_csv(D / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(~pl.col("bursty"))


def r2(cols):
    t = s_all.with_columns([pl.col("rule").str.slice(i, 1).alias(f"r{i}") for i in range(1, 7)])
    if cols == ["r6"]:
        t = t.filter(pl.col("n") >= 8)
    g = t.group_by(cols).agg(m=pl.col("c").mean())
    j = t.join(g, on=cols)
    return round(float(1 - ((j["c"] - j["m"]) ** 2).sum() / ((t["c"] - t["c"].mean()) ** 2).sum()), 3)


out["r2_letters"] = {"r1": r2(["r1"]), "r123": r2(["r1", "r2", "r3"]), "r6": r2(["r6"])}

e = pl.read_csv(D / "experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv")
young = e.filter(pl.col("colour").is_between(1, 3)).group_by("rule").agg(
    L=pl.col("left_fresh").sum() / pl.col("edge_steps").sum(),
    R=pl.col("right_fresh").sum() / pl.col("edge_steps").sum())
pooled = e.with_columns(g=pl.when(pl.col("colour") == 0).then(pl.lit("entered"))
                        .when(pl.col("colour") <= 3).then(pl.concat_str(pl.lit("young "), pl.col("turn")))
                        .otherwise(pl.lit("older"))).group_by("g").agg(
    steps=pl.col("edge_steps").sum(), c=pl.col("new_cells").sum() / pl.col("edge_steps").sum())
tot = pooled["steps"].sum()
out["chiral"] = {
    "rules": e["rule"].n_unique(),
    "left_more": int((young["L"] > young["R"]).sum()),
    "left_med": round(float(young["L"].median()), 2),
    "right_med": round(float(young["R"].median()), 2),
    "pooled": {r["g"]: [round(r["steps"] / tot, 3), round(r["c"], 3)] for r in pooled.iter_rows(named=True)},
}
cm = pl.read_csv(D / "experiments/archive/2026-10-probe-growth-census/results/c_model.csv").filter(pl.col("held_out"))
y, yh = cm["c"].to_numpy(), cm["c_pred"].to_numpy()
out["c_model"] = {
    "n": cm.height,
    "r2": round(float(1 - ((y - yh) ** 2).sum() / ((y - y.mean()) ** 2).sum()), 3),
    "corr": round(float(np.corrcoef(y, yh)[0, 1]), 3),
    "mae_med": round(float(np.median(np.abs(y - yh))), 3),
    "points": [[round(a, 3), round(b, 3)] for a, b in zip(yh, y)],
}

# --- Q1: mixing ----------------------------------------------------------
out["mixing"] = json.loads((D / "experiments/archive/2026-10-mixing/results/mixing_stats.json").read_text())

# --- Tethering -----------------------------------------------------------
teth = []
for rule in ["RRRRRLLLLLL", "RRRRRLRLLLR", "RLLLLLLLRLL", "RRRLLRLLR", "RLR"]:
    prof = density_profile(rule, ROOT / "experiments/archive/2026-10-knockout-maps/dumps")
    obs = float(np.polyfit(prof[:, 0], np.log(prof[:, 1]), 1)[0])
    vd = []
    for tau in (2, 4, 8):
        rad = radial(rule, ROOT / "experiments/archive/2026-10-knockout-maps/dumps", tau)
        vd.append(float(np.average(rad[:, 1] / rad[:, 2], weights=rad[:, 3])))
    teth.append([rule, round(min(vd), 3), round(max(vd), 3), round(obs, 3)])
out["tether"] = teth

c = pl.read_csv(D / "experiments/archive/2026-10-census-sweeps/results/census.csv").filter(pl.col("cls").is_in(["log", "blob"]) & (pl.col("n") == 12))


def circ_run(r):
    return min(max(len(m.group()) for m in re.finditer(r"R+|L+", r + r)), len(r))


c = c.with_columns(run=pl.col("rule").map_elements(circ_run, return_dtype=pl.Int64))
runs = c.group_by("run").agg(frac=(pl.col("cls") == "log").mean(), n=pl.len()).sort("run")
out["runs12"] = [[r["run"], round(r["frac"], 3), r["n"]] for r in runs.iter_rows(named=True)]

T = str(ROOT / "target/release/examples/transplant")


def transplant(rule, mode, x, y, steps, seed=1):
    res = subprocess.run([T, str(ROOT / "experiments/archive/2026-10-knockout-maps/dumps" / f"{rule}.grid"), rule, mode, str(x), str(y), str(steps), str(seed)],
                         capture_output=True, text=True)
    if "left the board" in res.stderr:
        return None
    df = pl.read_csv(res.stdout.encode())
    last = df.tail(16)
    return {"home": round(float(last["near_home"].mean()), 3), "own": round(float(last["near_prev"].mean()), 3),
            "first_own": round(float(df.head(4)["near_prev"].mean()), 3),
            "mean": [round(float(last["mean_x"].mean()), 1), round(float(last["mean_y"].mean()), 1)],
            "spread_of_mean": round(float(np.hypot(df.tail(32)["mean_x"].std(), df.tail(32)["mean_y"].std())), 2)}


STEPS = 1 << 26
tethered = ["RRRRRLLLLLL", "RRRRRLRLLLR", "RLLLLLLLRLL", "RRRLLRLLR", "RLLRRRRRLRLR", "RRRLLLLRRRLL", "RLLLLRRRRLR"]
tp = {}
for r in tethered:
    tp[r] = {f"{x},{y}": transplant(r, "real", x, y, STEPS) for x, y in [(0, 0), (20, 0), (0, -15)]}
    print(r, tp[r], flush=True)
out["transplant"] = tp
sh = {}
for r in ["RRRRRLLLLLL", "RRRLLRLLR", "RLLRRRRRLRLR", "RRRLLLLRRRLL", "RLLLLRRRRLR"]:
    sh[r] = [transplant(r, "shuffled", 0, 0, STEPS, seed) for seed in (1, 2, 3)]
    print(r, "shuffled", [x["own"] if x else None for x in sh[r]], flush=True)
out["shuffled"] = sh
fr = {r: transplant(r, "frozen", 20, 0, 1 << 22) for r in ["RRRRRLLLLLL", "RLLLLLLLRLL"]}
out["frozen"] = fr

(D / "experiments/archive/2026-10-knockout-maps/results/followup_stats.json").write_text(json.dumps(out, separators=(",", ":")))
print({k: v for k, v in out.items() if k not in ("c_model", "mixing", "transplant", "shuffled")})
