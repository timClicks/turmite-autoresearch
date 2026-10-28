"""Every number the "Why a cube root" section quotes, computed from the probe
runs. Writes experiments/archive/2026-10-probe-growth-census/results/cube_stats.json for web/build.py.

Inputs: probe_all.csv (all growing rules, 2^27 steps), probe_summary.csv (per
rule fits + burst flags), long.csv (six typical rules to 2^32), census.csv.
"""
import json
from pathlib import Path

import numpy as np
import polars as pl

D = Path(__file__).resolve().parents[4]


def q(x, ps=(25, 50, 75)):
    return [round(float(v), 3) for v in np.percentile(np.asarray(x, float), ps)]


summary = pl.read_csv(D / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
census = pl.read_csv(D / "experiments/archive/2026-10-census-sweeps/results/census.csv")
growing = census.filter(pl.col("cls") != "builder").height
steady = summary.filter(~pl.col("bursty"))
blob = steady.filter(pl.col("cls") == "blob")
logs = steady.filter(pl.col("cls") == "log")
fast = blob.filter(pl.col("alpha_w") > 0.37)
core = blob.filter(pl.col("alpha_w").is_between(0.30, 0.37))

# Edge visits per octave, slope against time, k = 18..26.
probe = pl.read_csv(D / "experiments/archive/2026-10-probe-growth-census/results/probe_all.csv").filter(pl.col("k").is_between(18, 26))


def edge_slopes(rules):
    out = []
    for (_,), g in probe.filter(pl.col("rule").is_in(list(rules))).group_by("rule"):
        g = g.sort("k")
        b = g["boundary_steps"].to_numpy().astype(float)
        if (b == 0).any():
            continue
        out.append(np.polyfit(np.log2(g["t"].to_numpy().astype(float)), np.log2(b), 1)[0])
    return out


stats = {
    "growing": growing,
    "analysed": summary.height,
    "unanalysed": growing - summary.height,
    "bursty": int(summary["bursty"].sum()),
    "blob_n": blob.height,
    "log_n": logs.height,
    "fast_n": fast.height,
    "core_n": core.height,
    "alpha": q(blob["alpha_w"]),
    "c": q(blob["c"]),
    "g_c": q(blob["g_c"]),
    "kappa": q(blob["kappa"]),
    "g_k": q(blob["g_k"]),
    "beta": q(blob["beta"]),
    "fill": q(blob["fill"]),
    "corr": {k: round(float(np.corrcoef(blob["alpha_w"], blob[k])[0, 1]), 2) for k in ["g_k", "g_c", "beta"]},
    "log": {"kappa": q(logs["kappa"]), "g_k": q(logs["g_k"]), "c": q(logs["c"]), "beta": q(logs["beta"]), "alpha": q(logs["alpha_w"])},
    "fast": {"kappa": q(fast["kappa"]), "g_k": q(fast["g_k"]), "alpha": q(fast["alpha_w"])},
    "edge_slope_blob": round(float(np.median(edge_slopes(core["rule"]))), 2),
    "edge_slope_log": round(float(np.median(edge_slopes(logs["rule"]))), 2),
}

stats["identity_err"] = round(float(np.median(np.abs(blob["a"] - blob["a_pred"]))), 3)

# Spread of where the fastest ants spend their time: slope of sqrt(ant_var).
fastest = blob.filter(pl.col("alpha_w") > 0.45)["rule"]
core_slopes = []
for (_,), g in probe.filter(pl.col("rule").is_in(list(fastest)) & pl.col("k").is_between(20, 26)).group_by("rule"):
    g = g.sort("k")
    core_slopes.append(np.polyfit(np.log(g["t"].to_numpy().astype(float)), 0.5 * np.log(g["ant_var"].to_numpy()), 1)[0])
stats["fastest_n"] = len(core_slopes)
stats["fastest_core"] = round(float(np.median(core_slopes)), 2)

# Long runs: six typical rules from 2^17 to 2^32.
long = pl.read_csv(D / "experiments/archive/2026-10-probe-growth-census/results/long.csv").filter(pl.col("k") >= 17).sort("rule", "k").with_columns(
    c=pl.col("new_cells") / pl.col("boundary_steps"),
    kappa=(pl.col("boundary_steps") / (pl.col("t") // 2)) / (pl.col("perimeter") / pl.col("area")),
    w=pl.max_horizontal("width", "height"),
)
assert not long["escaped"].any()
stats["long"] = {
    r: {"k": g["k"].to_list(), "c": [round(v, 4) for v in g["c"]], "kappa": [round(v, 4) for v in g["kappa"]]}
    for (r,), g in long.group_by("rule", maintain_order=True)
}
lw = []
for (r,), g in long.group_by("rule"):
    lw.append(np.polyfit(np.log(g["t"].to_numpy().astype(float)), np.log(g["w"].to_numpy().astype(float)), 1)[0])
stats["long_alpha"] = [round(float(min(lw)), 3), round(float(max(lw)), 3)]
lc = long.group_by("rule").agg(pl.col("c").min().alias("lo"), pl.col("c").max().alias("hi"))
stats["long_c"] = [round(float(lc["lo"].min()), 2), round(float(lc["hi"].max()), 2)]
lk = long.group_by("rule").agg(pl.col("kappa").min().alias("lo"), pl.col("kappa").max().alias("hi"))
stats["long_kappa"] = [round(float(lk["lo"].min()), 2), round(float(lk["hi"].max()), 2)]

# Isotropic-heading check (c vs fresh neighbours / 4) on the pilot + long rules.
iso = pl.read_csv(D / "experiments/archive/2026-10-probe-growth-census/results/iso.csv").filter(pl.col("k") == 26).join(
    summary.select("rule", "alpha_w", "cls"), on="rule"
).with_columns(
    ratio=(pl.col("new_cells") / pl.col("boundary_steps")) / (pl.col("fresh_nbrs") / (4 * pl.col("boundary_steps"))),
    fresh=pl.col("fresh_nbrs") / pl.col("boundary_steps"),
)
typical = iso.filter(pl.col("alpha_w").is_between(0.30, 0.37))
stats["iso"] = {
    "fresh": [round(float(iso["fresh"].min()), 2), round(float(iso["fresh"].max()), 2)],
    "iso_c": [round(float(iso["fresh"].min()) / 4, 2), round(float(iso["fresh"].max()) / 4, 2)],
    "typical_ratio": [round(float(typical["ratio"].min()), 2), round(float(typical["ratio"].max()), 2)],
    "all_ratio": [round(float(iso["ratio"].min()), 2), round(float(iso["ratio"].max()), 2)],
}

# Scatter: every steady rule.
cls_code = {"blob": 0, "log": 1}
stats["scatter"] = [
    [round(r["alpha_w"], 3), round(r["g_c"], 3), round(r["g_k"], 3), cls_code[r["cls"]]]
    for r in steady.iter_rows(named=True)
]

(D / "experiments/archive/2026-10-probe-growth-census/results/cube_stats.json").write_text(json.dumps(stats, separators=(",", ":")))
print(json.dumps({k: v for k, v in stats.items() if k not in ("scatter", "long")}, indent=1))
