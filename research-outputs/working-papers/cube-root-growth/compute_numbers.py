"""Every number quoted in main.typ, computed from data/* (none typed by hand).

Run from the repo root:  uv run research-outputs/working-papers/cube-root-growth/compute_numbers.py   ->  research-outputs/working-papers/cube-root-growth/numbers.json
Bootstrap resampling uses a fixed seed (20261012).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl

R = Path(__file__).resolve().parents[3]
D = R  # inputs are addressed by repo-relative path (they live in experiments/*/*/results)

# Fail loudly (before computing anything) if an input file named in this script is missing or empty.
_missing = [
    f for f in sorted(set(re.findall(r'(?:D / |jl\()"([^"]+\.(?:csv|json|txt))"', Path(__file__).read_text())))
    if not (D / f).exists() or (D / f).stat().st_size == 0
]
if _missing:
    sys.exit(f"compute_numbers.py: missing or empty inputs: {_missing}")
rng = np.random.default_rng(20261012)


def jl(name):
    return json.loads((D / name).read_text())


def med_ci(x, B=4000):
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), (B, len(x)))
    m = np.median(x[idx], axis=1)
    return [float(np.median(x)), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def q(x):
    return [float(v) for v in np.percentile(np.asarray(x, float), [25, 50, 75])]


census = pl.read_csv(D / "experiments/archive/2026-10-census-sweeps/results/census.csv")
summ = pl.read_csv(D / "experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv")
steady = summ  # bursty rules are kept (flag retained as a column; see sensitivity in main.typ)
blob = steady.filter(pl.col("cls") == "blob")
logs = steady.filter(pl.col("cls") == "log")
core = blob.filter(pl.col("alpha_w").is_between(0.30, 0.37))

N = {}
N["census"] = {
    "rules": census.height,
    "builders": int((census["cls"] == "builder").sum()),
    "blob": int((census["cls"] == "blob").sum()),
    "log": int((census["cls"] == "log").sum()),
    "n_min": int(census["n"].min()), "n_max": int(census["n"].max()),
}
N["probe"] = {
    "analysed": summ.height,
    "unanalysed": N["census"]["blob"] + N["census"]["log"] - summ.height,
    "bursty": int(summ["bursty"].sum()),
    "blob": blob.height, "log": logs.height, "core": core.height,
    "fast": int((blob["alpha_w"] > 0.37).sum()),
    "slow": int((blob["alpha_w"] < 0.30).sum()),
}
for name, df in [("blob", blob), ("core", core)]:
    N[f"alpha_w_{name}"] = med_ci(df["alpha_w"])
    N[f"alpha_rg_{name}"] = med_ci(df["alpha_rg"])
    N[f"a_{name}"] = med_ci(df["a"])
    N[f"iqr_alpha_w_{name}"] = q(df["alpha_w"])
N["by_n"] = {
    str(n): {"N": g.height, "med": float(g["alpha_w"].median()), "iqr": q(g["alpha_w"]),
             "rg_med": float(g["alpha_rg"].median())}
    for (n,), g in blob.group_by("n") if g.height >= 10
} if False else {
    str(r["n"]): r for r in blob.group_by("n").agg(
        pl.len().alias("N"), pl.col("alpha_w").median().alias("med"),
        pl.col("alpha_rg").median().alias("rg_med")).sort("n").iter_rows(named=True)
}
N["spearman_alpha_n"] = float(
    pl.DataFrame({"a": blob["alpha_w"].rank(), "n": blob["n"].rank()}).select(pl.corr("a", "n")).item())

# Mean-field decomposition.
for name, df in [("blob", blob), ("core", core), ("log", logs)]:
    N[f"mf_{name}"] = {k: q(df[k]) for k in ["c", "kappa", "beta", "g_c", "g_k", "fill", "alpha_w"]}
N["identity"] = {
    "median_abs_err_blob": float(np.median(np.abs(blob["a"] - blob["a_pred"]))),
    "corr_blob": float(np.corrcoef(blob["a"], blob["a_pred"])[0, 1]),
    "corr_alpha_gk": float(np.corrcoef(blob["alpha_w"], blob["g_k"])[0, 1]),
    "corr_alpha_gc": float(np.corrcoef(blob["alpha_w"], blob["g_c"])[0, 1]),
    "corr_alpha_beta": float(np.corrcoef(blob["alpha_w"], blob["beta"])[0, 1]),
    "frac_core_gk_small": float((core["g_k"].abs() < 0.05).mean()),
    "frac_blob_gk_small": float((blob["g_k"].abs() < 0.05).mean()),
    "frac_blob_gc_small": float((blob["g_c"].abs() < 0.05).mean()),
    "frac_core_gc_small": float((core["g_c"].abs() < 0.05).mean()),
}
N["cube"] = jl("experiments/archive/2026-10-probe-growth-census/results/cube_stats.json")
N["cube"].pop("scatter", None)
for v in N["cube"].get("long", {}).values():
    pass
fu = jl("experiments/archive/2026-10-knockout-maps/results/followup_stats.json")
fu["c_model"].pop("points", None)
N["followup"] = {k: fu[k] for k in ["letters", "r2_letters", "chiral", "c_model"]}
mx = jl("experiments/archive/2026-10-mixing/results/mixing_stats.json")
mx.pop("points", None)
N["mixing"] = mx

# Calibration.
pa = jl("experiments/archive/2026-10-calib-instrument-calibration/results/calib_partA.json")
N["calib_A"] = {k: pa[k] for k in ["rotor", "random_walk", "ants_core", "ants_blob", "sd_ratio_alpha_w", "sd_ratio_alpha_rg"]}
N["calib_A_keys"] = list(pa["rotor"].keys())
N["calib_B"] = jl("experiments/archive/2026-10-calib-instrument-calibration/results/calib_partB.json")
N["calib_B"].pop("contour_all", None)
N["calib_C"] = jl("experiments/archive/2026-10-calib-instrument-calibration/results/calib_patched.json")

# Rotor c and kappa per seed from the raw probe windows (k in 20..26).
def ck(path):
    df = pl.read_csv(path).filter((pl.col("k") >= 20) & (pl.col("k") <= 26) & ~pl.col("escaped"))
    df = df.with_columns(
        c=pl.col("new_cells") / pl.col("boundary_steps"),
        kappa=(pl.col("boundary_steps") / (pl.col("t") // 2)) / (pl.col("perimeter") / pl.col("area")))
    return {"c": med_ci(df["c"], 1000), "kappa": med_ci(df["kappa"], 1000), "seeds": df["rule"].n_unique()}
N["rotor_ck"] = ck(D / "experiments/archive/2026-10-calib-instrument-calibration/results/calib_rotor.csv")
N["rw_ck"] = ck(D / "experiments/archive/2026-10-calib-instrument-calibration/results/calib_rw.csv")

(R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").write_text(json.dumps(N, indent=1, default=float))
print("wrote research-outputs/working-papers/cube-root-growth/numbers.json")

# ---- additions after review ----
def is_repeat(r):
    n = len(r)
    return any(n % d == 0 and r == r[:d] * (n // d) for d in range(1, n))


N2 = json.loads((R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").read_text())
allb = summ.filter(pl.col("cls") == "blob")
N2["with_bursty"] = {"blob_n": allb.height, "alpha_w": med_ci(allb["alpha_w"], 1000)}
reps = set(r for r in census["rule"] if is_repeat(r))
N2["repeats"] = {
    "n": len(reps),
    "blob_median_alpha_w_primitive": float(blob.filter(~pl.col("rule").is_in(list(reps)))["alpha_w"].median()),
    "blob_median_alpha_w_all": float(blob["alpha_w"].median()),
}
rot, ant = N2["calib_A"]["rotor"], N2["calib_A"]["ants_blob"]
truth = {"alpha_w": 1 / 3, "alpha_rg": 1 / 3, "a": 2 / 3}
N2["bias"] = {
    k: {"ant_minus_rotor": ant[k]["median"] - rot[k]["median"],
        "rotor_bias": rot[k]["median"] - truth[k],
        "ant_corrected": ant[k]["median"] - (rot[k]["median"] - truth[k])}
    for k in truth
}
N2["mix_sample"] = {"listed": sum(1 for l in open(D / "experiments/archive/2026-10-mixing/results/mix_rules.txt") if l.strip())}
(R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").write_text(json.dumps(N2, indent=1, default=float))
print("added review fields")

# bursty flag reconstruction: the flag separates cleanly on max_jump
N3 = json.loads((R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").read_text())
bu = summ.filter(pl.col("bursty")); nb = summ.filter(~pl.col("bursty"))
N3["bursty_rule"] = {"flagged_min_jump": float(bu["max_jump"].min()), "unflagged_max_jump": float(nb["max_jump"].max()),
                     "separates": bool(bu["max_jump"].min() > nb["max_jump"].max())}
(R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").write_text(json.dumps(N3, indent=1, default=float))

# random-sample mixing replication (notes/mixing-random-sample.md)
N4 = json.loads((R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").read_text())
mr = pl.read_csv(D / "experiments/archive/2026-10-mixing/results/mixing_random.csv").with_columns(ratio=pl.col("msd_slope") / pl.col("pred_slope"))
ur, nr = mr.filter(pl.col("colour_tv") < 0.05), mr.filter(pl.col("colour_tv") >= 0.05)
N4["mixing_random"] = {
    "n": mr.height, "uni_n": ur.height, "non_n": nr.height,
    "uni_ratio": [float(v) for v in np.percentile(ur["ratio"], [0, 50, 100])],
    "non_ratio_med": float(nr["ratio"].median()),
    "uni_expo_med": float(ur["msd_expo"].median()),
}
(R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").write_text(json.dumps(N4, indent=1, default=float))

# ---- long-run ensembles produced by other scripts (parsed from their outputs / CSVs) ----
import re
N5 = json.loads((R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").read_text())


def shape(path):
    lines = [l.strip().split(",") for l in open(path) if l.startswith(("cp,", "prof,"))]
    cp = [l for l in lines if l[0] == "cp"]
    cols = "kind,spec,k,A,rg2,aniso,rbar,rsd,h2,h4,h8,Wsurf,fill".split(",")
    df = pl.DataFrame(cp, schema=cols, orient="row").with_columns([pl.col(c).cast(pl.Float64) for c in cols[2:]])
    prof = {}
    for l in lines:
        if l[0] == "prof":
            prof.setdefault(l[1].split("@")[0], []).append([float(x) for x in l[3].split(";")])
    P = np.array([np.mean(v, 0) for v in prof.values()])  # one mean profile per walker type
    W = df.group_by("k", maintain_order=True).agg(pl.col("Wsurf").mean()).sort("k")
    k, w = W["k"].to_numpy(), W["Wsurf"].to_numpy()
    s = k >= 18
    dW = float(np.polyfit(k[s] * np.log(2), np.log(w[s]), 1)[0])
    kmax = int(df["k"].max())
    last = df.filter(pl.col("k") == kmax)
    return {"runs": df["spec"].n_unique(), "kmax": kmax, "profile": P.mean(0).tolist(), "profile_rel_sd_shell6": float(P[:, 6].std(ddof=1) / P[:, 6].mean()) if len(P) > 1 else None,
            "dW": dW, "aniso": float(last["aniso"].median()), "h4": float(last["h4"].median()), "fill": float(last["fill"].median())}


sr, sa = shape(D / "experiments/archive/2026-10-shape-limit/results/shape_rotor.csv"), shape(D / "experiments/archive/2026-10-shape-limit/results/shape_ants.csv")
x = np.arange(15) * 0.075 + 0.0375
cone = 3 * (1 - x)  # mean-visit density of a cone, units t/A; mean over the disc is 1
N5["shape"] = {
    "rotor": sr, "ants": sa,
    "max_rel_diff_ants_rotor_shells0_9": float(max(abs(a - r) / r for a, r in zip(sa["profile"][:10], sr["profile"][:10]))),
    "max_rel_diff_ants_cone_shells0_9": float(max(abs(a - c) / c for a, c in zip(sa["profile"][:10], cone[:10]))),
}
t4 = (D / "experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_stats.txt").read_text()
t4r = (D / "experiments/archive/2026-10-item4-exponent-rotor-calibrated/results/item4_rotor_stats.txt").read_text()
m = re.search(r"mean of last-6 a\(k\): across-rule mean ([\d.]+) sd ([\d.]+); range ([\d.]+)\.\.([\d.]+)", t4)
rows = re.findall(r"^(\w+)\s+[\d.+\-()]+\s+[\d.+\-()]+\s+[\d.+\-()]+\s+\|\s+([\d.]+)\+-", t4, re.M)
rot6 = float(re.search(r"mean of last-6 a\(k\): across-rule mean ([\d.]+)", t4r).group(1))
last6 = {r: float(v) for r, v in rows if r != "rotor"}
N5["item4"] = {
    "ant_last6_mean": float(m.group(1)), "ant_last6_sd": float(m.group(2)), "ant_range": [float(m.group(3)), float(m.group(4))],
    "rotor_last6": rot6, "rules": len(last6),
    "within_0006_of_rotor": sum(abs(v - rot6) <= 0.0065 for v in last6.values()),
    "runs_kept": int(re.search(r"runs (\d+)", t4).group(1)),
}
t21 = (D / "experiments/archive/2026-10-item21-slow-outliers/results/item21_stats.txt").read_text()
hi = re.search(r"== high: (\d+) rules.*?regress below 0.37: ([\d.]+) of rules; persistent.*?: (\d+) rules", t21, re.S)
lo = re.search(r"== low: (\d+) rules.*?rise above 0.30: ([\d.]+) of rules; persistent.*?: (\d+) rules", t21, re.S)
N5["item21"] = {"high_n": int(hi.group(1)), "high_regress": float(hi.group(2)), "high_persist": int(hi.group(3)),
               "low_n": int(lo.group(1)), "low_regress": float(lo.group(2)), "low_persist": int(lo.group(3)),
               "spearman_census": float(re.search(r"Spearman\(census alpha, 12-seed mean\) over outliers: ([\d.]+)", t21).group(1)),
               "spearman_gk": float(re.search(r"Spearman\(g_k, 12-seed mean\) over outliers: ([\d.]+)", t21).group(1))}
(R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").write_text(json.dumps(N5, indent=1, default=float))

# --- 2026-10-13 PM follow-ups: H1 (filling fraction), H3 (c*kappa prefactor), G1 (RLRLLL switch). Parsed from the text outputs of
# experiments/archive/2026-10-h1-lacunarity-decomposition/scripts/h1_lacunarity.py, experiments/archive/2026-10-h3-scaling-collapse/scripts/h3_collapse.py, experiments/archive/2026-10-g1-ribbon-breakout/scripts/g1_stats.py (+ the examples/ribbon_trace.rs log); notes/research-frontier-2026-10-13-pm.md.
N6 = json.loads((R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").read_text())
h1t = (D / "experiments/archive/2026-10-h1-lacunarity-decomposition/results/h1_lacunarity.txt").read_text().split("== core band")[1]  # core-band section, the same filter as b2_anova.py / h3_collapse.py
h3t = (D / "experiments/archive/2026-10-h3-scaling-collapse/results/h3_collapse.txt").read_text()
icc = lambda txt, name: float(re.search(rf"(?:ICC )?\b{name}\s+rules \d+\s+sd_within [\d.]+\s+sd_between [\d.]+\s+ICC ([\d.]+)", txt).group(1))
cov = [float(v) for v in re.search(r"Cov\(term, a\): ax ([\d.]+)\s+ay ([\d.]+)\s+geta ([\d.]+)\s+\(sum ([\d.]+)\)", h3t).groups()]
cm = [[float(v) for v in row.split()] for row in re.findall(r"^\s*\[?\[\s*([-\d.e+ ]+?)\s*\]", h3t.split("rule-mean covariance")[1], re.M)]
N6["h1"] = {
    "r2_geta_vs_excess": float(re.search(r"R\^2\(g_eta -> a-2alpha_w\) = ([\d.]+)", h1t).group(1)),
    "icc_geta": icc(h1t, "geta"), "icc_a": icc(h1t, "a"),
    "icc_ax": icc(h3t, "ax"), "icc_ay": icc(h3t, "ay"),
    "mean_geta": float(re.search(r"mean g_eta ([+-][\d.]+)", h1t).group(1)),
    "frac_geta_pos": float(re.search(r"frac rules g_eta>0: ([\d.]+)", h1t).group(1)),
    "share_ax": cov[0] / cov[3], "share_ay": cov[1] / cov[3], "share_geta": cov[2] / cov[3],
    "corr_axay": cm[0][1] / (cm[0][0] * cm[1][1]) ** 0.5,
}
N6["h3"] = {
    "reduction": float(re.search(r"reduction ([\d.]+)%", h3t).group(1)) / 100,
    "fit_power": float(re.search(r"log K = [\d.]+ \+ ([\d.]+) log\(c kappa\)", h3t).group(1)),
    "fit_r2": float(re.search(r"log\(c kappa\); R\^2 = ([\d.]+)", h3t).group(1)),
}
g1t = (D / "experiments/archive/2026-10-g1-ribbon-breakout/results/g1_stats.txt").read_text()
g1m = re.search(r"ONSET of the steady phase: window ending t = (\d+) \((\d+) windows", g1t)
N6["g1"] = {
    "onset_t": int(g1m.group(1)), "steady_windows": int(g1m.group(2)),
    "steady_steps_per_new": float(re.search(r"steady phase: steps/new median ([\d.]+)", g1t).group(1)),
    "exit_step": int(re.search(r"left the board at step (\d+)", (D / "experiments/archive/2026-10-g1-ribbon-breakout/results/g1_ribbon.log").read_text()).group(1)),
}
(R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").write_text(json.dumps(N6, indent=1, default=float))

# log/blob cut robustness (experiments/archive/2026-10-alpha-gap)
N7 = json.loads((R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").read_text())
_g = jl("experiments/archive/2026-10-alpha-gap/results/gap_robustness.json")
N7["alpha_gap"] = {
    "dip": _g["dip_nonbuilder"]["dip"], "dip_n": _g["dip_nonbuilder"]["n"],
    "gmm_means": _g["gmm2_nonbuilder"]["means"], "gmm_weights": _g["gmm2_nonbuilder"]["weights"],
    "cuts": {str(r["cut"]): r["median_alpha_w"] for r in _g["cut_sensitivity"]},
    "spread_0.15_0.25": max(r["median_alpha_w"] for r in _g["cut_sensitivity"] if r["cut"] >= 0.15) - min(r["median_alpha_w"] for r in _g["cut_sensitivity"] if r["cut"] >= 0.15),
    "spread_0.10_0.25": _g["median_range_cuts_0.10_0.25"]["spread"],
    "n_per_bin_015": _g["trough_in_0.05_0.30"]["count_at_0.145_0.155"],
}
(R / "research-outputs" / "working-papers" / "cube-root-growth" / "numbers.json").write_text(json.dumps(N7, indent=1, default=float))
