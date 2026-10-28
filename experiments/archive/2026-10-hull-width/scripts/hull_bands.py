# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Band-power ratio ants/rotor from stored spec_bands (README 'Band-power ratio', registered before this script existed). No simulation.
usage (repo root): uv run experiments/archive/2026-10-hull-width/scripts/hull_bands.py"""
import subprocess
from pathlib import Path
import numpy as np, polars as pl
from scipy.stats import spearmanr

R = Path(__file__).resolve().parents[1] / "results"
BANDS = ["3-4", "5-8", "9-16", "17-32", "33-64", "65-128", "129-256"]
rng = np.random.default_rng(20261014)
out = ["# hull band ratios; commit " + subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()]


def load(f):
    d = pl.read_csv(R / f, infer_schema_length=0)
    d = d.with_columns(pl.col("k").cast(pl.Int64))
    rows = []
    for r in d.iter_rows(named=True):
        rows.append((r["spec"], int(r["k"]), np.array([float(x) for x in r["spec_bands"].split(";")])))
    return rows


ants, rot = load("hull_ants.csv"), load("hull_rotor.csv")
res = {}
for k in (28, 30):
    A = {}
    for spec, kk, b in ants:
        if kk == k and np.all(np.isfinite(b)):
            A.setdefault(spec.split("@")[0], []).append(b)
    rule_med = {r: np.median(np.array(v), axis=0) for r, v in A.items()}
    Rt = np.array([b for spec, kk, b in rot if kk == k and np.all(np.isfinite(b))])
    out.append(f"\n## k={k}: ant rules with finite bands {len(rule_med)} (runs {sum(len(v) for v in A.values())}), rotor runs {len(Rt)}")
    if len(Rt) < 2 or not rule_med:
        out.append("  insufficient data"); continue
    rmed = np.median(Rt, axis=0)
    lrot = np.log(Rt)
    boot = np.array([np.median(lrot[rng.integers(0, len(Rt), len(Rt))], axis=0) for _ in range(2000)])
    sd_boot = boot.std(axis=0)
    amed = np.median(np.array(list(rule_med.values())), axis=0)
    ratio = amed / rmed
    out.append("  band      " + "  ".join(f"{b:>8s}" for b in BANDS))
    out.append("  rotor med " + "  ".join(f"{v:8.2e}" for v in rmed))
    out.append("  ants med  " + "  ".join(f"{v:8.2e}" for v in amed))
    out.append("  ratio R_b " + "  ".join(f"{v:8.3f}" for v in ratio))
    out.append("  rotor sd(log med) " + "  ".join(f"{v:6.3f}" for v in sd_boot))
    out.append("  rotor run sd(log) " + "  ".join(f"{v:6.3f}" for v in lrot.std(axis=0, ddof=1)))
    perrule = {r: v / rmed for r, v in rule_med.items()}
    n_lo = sum(1 for r in perrule if perrule[r][0] > 1 and perrule[r][1] > 1)
    n_hi = sum(1 for r in perrule if perrule[r][5] < 1)
    out.append(f"  rules with R>1 in bands 3-4 and 5-8: {n_lo}/{len(perrule)}; rules with R<1 in 65-128: {n_hi}/{len(perrule)}")
    rho = spearmanr(np.arange(7), np.log(ratio))[0]
    below = [i for i in range(7) if ratio[i] < 1]
    out.append(f"  Spearman(band index, log R_b) = {rho:+.3f}; crossover band (first R_b<1): {BANDS[below[0]] if below else 'none'}")
    exceed = [BANDS[i] for i in range(7) if np.log(ratio[i]) > 2 * sd_boot[i]]
    out.append(f"  bands where log R_b > 2 sd(rotor log median): {exceed}")
    res[k] = dict(n_lo=n_lo, n_hi=n_hi, nr=len(perrule), rho=rho, cross=below[0] if below else None, rmed=rmed,
                  low=bool(ratio[0] > 1 and ratio[1] > 1), hi=bool(ratio[5] < 1))

# P5: rotor stability k=28 -> 30 per band
r28 = np.median(np.array([b for s, kk, b in rot if kk == 28]), axis=0); r30 = np.median(np.array([b for s, kk, b in rot if kk == 30]), axis=0)
f = r30 / r28
out.append("\n## rotor median band power k=30 / k=28: " + "  ".join(f"{v:.3f}" for v in f))
v = ["\n== registered verdicts =="]
ok1 = all(r["n_lo"] >= 5 and r["low"] for r in res.values()) and len(res) == 2
ok2 = all(r["n_hi"] >= 5 and r["hi"] for r in res.values()) and len(res) == 2
ok3 = len(res) == 2 and all(r["rho"] <= -0.8 for r in res.values())
ok4 = len(res) == 2 and res[28]["cross"] is not None and res[30]["cross"] is not None and abs(res[28]["cross"] - res[30]["cross"]) <= 1
ok5 = bool(np.all((f >= 0.7) & (f <= 1.4)))
v += [f"1 low bands R>1 at both k, >=5/6 rules: {ok1}", f"2 band 65-128 R<1 at both k, >=5/6 rules: {ok2}",
      f"3 Spearman <= -0.8 at both k: {ok3}", f"4 crossover within one band across k: {ok4}", f"5 rotor k=30/28 band ratio in [0.7,1.4]: {ok5}"]
out += v
(R / "hull_bands.txt").write_text("\n".join(out) + "\n"); print("\n".join(out))
