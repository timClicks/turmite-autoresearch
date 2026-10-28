# /// script
# dependencies = ["polars", "numpy"]
# ///
"""W0: tidy rule tables, cohort reconciliation, instrument checks.
usage (repo root): uv run experiments/archive/2026-10-kappa-rule-space/scripts/w0_build.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np, polars as pl
from kcommon import *

out = []
cen = census()
all_blob = pl.read_csv(legacy("probe_summary.csv")).filter(pl.col("cls") == "blob")
out.append(f"census blob rules fitted (probe_summary.csv): {all_blob.height}; bursty: {all_blob['bursty'].sum()}; non-bursty: {cen.height}")
cc = pl.read_csv(legacy("census.csv")).filter(pl.col("cls") == "blob")
out.append(f"census.csv blob (before fit filter): {cc.height}; in census.csv but not probe_summary blob: {len(set(cc['rule']) - set(all_blob['rule']))}")
out.append("=> 2622 quoted in notes = 2630 fitted blob - 8 bursty. Census cohort used here: non-bursty (2622).")

r152 = rule_means(pool_runs(["b2_probe.csv", "item21_probe.csv"]))
r192 = rule_means(pool_runs(["b2_probe.csv", "item21_probe.csv", "patched.csv"]))
out.append(f"pool-152 (b2+item21, >=6 core-band runs): {r152.height}; pool-192 (+patched.csv, a1c definition): {r192.height}; pool-152 subset of pool-192: {set(r152['base']) <= set(r192['base'])}")
out.append("=> 152 = armc design pool (arm C script); 192 = a1c_predict pool (adds patched.csv). Primary pool here: pool-192.")
in_cen = len(set(r192["base"]) & set(cen["rule"]))
out.append(f"pool-192 rules also in census cohort: {in_cen}; not in it (bursty/unfitted/other class): {r192.height - in_cen}")

tab = r192.join(cen.select(base="rule", cen_kappa="kappa", cen_c="c", cen_gk="g_k", cen_lnA22="lnA22"), on="base", how="left").with_columns(
    n=pl.col("base").str.len_chars(), nR=pl.col("base").str.count_matches("R"), pool152=pl.col("base").is_in(r152["base"]))
tab.write_csv(EXP / "results" / "rules_pool.csv")
cen.with_columns(n=pl.col("rule").str.len_chars(), nR=pl.col("rule").str.count_matches("R"),
                 in_pool=pl.col("rule").is_in(r192["base"])).write_csv(EXP / "results" / "rules_census.csv")

# CHECK1: ICC of ln kappa, b2 core band -- reference 0.625
b2 = pool_runs(["b2_probe.csv"])
groups = [g["kappa"].log().to_numpy() for _, g in b2.group_by("base")]
i, sw, sb, ng = icc_groups(groups)
out.append(f"CHECK1 ICC ln kappa b2 core band: {i:.3f} (sd within {sw:.3f}, between {sb:.3f}, rules {ng}); reference 0.625 -> {'PASS' if abs(i - 0.625) <= 0.01 else 'FAIL'}")

# CHECK2: letters baseline reproduces a1c
rules = r192["base"].to_list(); y = r192["lnk"].to_numpy(); yc = r192["c"].to_numpy()
X = np.array([onehot(s) for s in rules])
base = {lam: loo_ridge_r2(X, y, lam) for lam in (1, 10, 30)}
out.append("CHECK2 letter-by-position ridge LOO R^2 on ln kappa: " + ", ".join(f"lam={l}: {v:+.3f}" for l, v in base.items())
           + " (a1c reference -0.061, -0.046, -0.036) -> " + ("PASS" if abs(base[10] + 0.046) <= 0.01 else "FAIL"))
out.append(f"        pool-192: N={len(y)}, sd rule-mean ln kappa {y.std():.3f} (a1c: 192, 0.503)")

# CHECK3: planted signal (R^2 0.3 on one letter indicator) must be recovered
R = rng(3); rec = []
x = X[:, 2 * 2 + 1]  # third letter is R
xs = (x - x.mean()) / x.std(); sd = y.std()
for _ in range(20):
    yy = np.sqrt(0.3) * sd * xs + np.sqrt(0.7) * sd * R.standard_normal(len(y))
    rec.append(loo_ridge_r2(X, yy, 10))
out.append(f"CHECK3 planted R^2 0.30 recovered by letter ridge LOO (20 draws): mean {np.mean(rec):+.3f}, min {np.min(rec):+.3f} -> {'PASS' if np.mean(rec) >= 0.2 else 'FAIL'}")

# CHECK4: positive control, letters predict c
rc = loo_ridge_r2(X, yc, 10)
out.append(f"CHECK4 letter ridge LOO R^2 on c (pool-192): {rc:+.3f} (need >= 0.5) -> {'PASS' if rc >= 0.5 else 'FAIL'}")

txt = header("uv run experiments/archive/2026-10-kappa-rule-space/scripts/w0_build.py") + "\n".join(out) + "\n"
(EXP / "results" / "w0_checks.txt").write_text(txt); print(txt)
