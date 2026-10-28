import json
import numpy as np
from scipy import stats

with open("experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.json") as f:
    d = json.load(f)

# Also check depth across the 44 rules
import polars as pl
df = pl.read_csv("experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.csv")
p_k = df.filter(pl.col("spec").str.contains("@") & (pl.col("k") == 25))
p_k = p_k.with_columns(pl.col("spec").str.split("@").list.get(0).alias("rule"))

rule_stats = p_k.group_by("rule").agg([
    pl.col("kappa").mean().alias("kappa"),
    pl.col("disp_med").mean().alias("disp_med"),
    pl.col("depth_med").mean().alias("depth_med"),
    pl.col("depth_mean").mean().alias("depth_mean"),
    pl.col("l_mean").mean().alias("l_mean"),
    pl.col("l_med").mean().alias("l_med"),
    pl.col("n_completed").mean().alias("n_completed"),
    pl.col("boundary_steps").mean().alias("boundary_steps"),
])

kappas = rule_stats["kappa"].to_numpy()
depth_med = rule_stats["depth_med"].to_numpy()
depth_mean = rule_stats["depth_mean"].to_numpy()
disp_med = rule_stats["disp_med"].to_numpy()
l_mean = rule_stats["l_mean"].to_numpy()
n_completed = rule_stats["n_completed"].to_numpy()

print("Correlations with kappa across 44 rules at k=25:")
for name, val in [("disp_med", disp_med), ("depth_med", depth_med), ("depth_mean", depth_mean), ("l_mean", l_mean), ("n_completed", n_completed)]:
    r, p = stats.spearmanr(val, kappas)
    print(f"  {name:<15}: rho = {r:+.3f} (p = {p:.2e})")

# Check regression with disp_med predicting log(kappa)
log_kappa = np.log(kappas)
r_log, p_log = stats.pearsonr(disp_med, log_kappa)
print(f"\nPearson corr(disp_med, log kappa): r = {r_log:.3f} (R^2 = {r_log**2:.3f}, p = {p_log:.2e})")

# Cross-validated R^2 predicting log(kappa) from disp_med
y = log_kappa
X = np.column_stack([np.ones_like(disp_med), disp_med])
y_preds = []
for i in range(len(y)):
    train_idx = [j for j in range(len(y)) if j != i]
    beta = np.linalg.lstsq(X[train_idx], y[train_idx], rcond=None)[0]
    y_preds.append(X[i] @ beta)

y_preds = np.array(y_preds)
ss_tot = np.sum((y - np.mean(y))**2)
ss_res = np.sum((y - y_preds)**2)
r2_loocv = 1.0 - ss_res / ss_tot
print(f"Leave-one-out cross-validated R^2 predicting log(kappa) from disp_med: {r2_loocv:.3f}")
