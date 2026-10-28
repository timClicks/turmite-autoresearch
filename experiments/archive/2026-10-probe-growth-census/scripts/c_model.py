"""Predict c from a rule's letters using the edge's chirality.

Constants come only from the 300-rule calibration sample (edgestats_sample.csv):
  - s[k]: pooled share of edge steps that start on colour k (k = 0..5, 6+),
  - p0: chance a step from a just-entered (colour 0) cell breaks new ground,
  - pL[k], pR[k]: fraction of edge steps on colour k with fresh ground to the
    left / right (the edge's chirality).
Prediction for a rule: c = s0 p0 + sum_k s_k * (pL[k] if rule[k] == L else pR[k]),
renormalised over the colours the rule actually has. Tested on all other rules.
"""
import numpy as np
import polars as pl

cal = pl.read_csv("experiments/archive/2026-10-edge-statistics/results/edgestats_sample.csv")
cal_rules = set(cal["rule"])
K = 6  # colours 0..5 individually, 6+ pooled
cal = cal.with_columns(kk=pl.min_horizontal(pl.col("colour"), pl.lit(K)))
g = cal.group_by("kk").agg(
    steps=pl.col("edge_steps").sum(),
    new=pl.col("new_cells").sum(),
    left=pl.col("left_fresh").sum(),
    right=pl.col("right_fresh").sum(),
).sort("kk")
share = (g["steps"] / g["steps"].sum()).to_numpy()
pL = (g["left"] / g["steps"]).to_numpy()
pR = (g["right"] / g["steps"]).to_numpy()
p0 = float(g["new"][0] / g["steps"][0])


def predict(rule: str) -> float:
    n = len(rule)
    num = share[0] * p0
    den = share[0]
    for k in range(1, K + 1):
        if k >= n:
            break
        if k < K:
            num += share[k] * (pL[k] if rule[k] == "L" else pR[k])
            den += share[k]
        else:  # colours 6+: mix by the fraction of L among them
            tail = rule[K:]
            fl = tail.count("L") / len(tail)
            num += share[K] * (fl * pL[K] + (1 - fl) * pR[K])
            den += share[K]
    return num / den


s = pl.read_csv("experiments/archive/2026-10-probe-growth-census/results/probe_summary.csv").filter(~pl.col("bursty"))
s = s.with_columns(c_pred=pl.col("rule").map_elements(predict, return_dtype=pl.Float64),
                   held_out=~pl.col("rule").is_in(list(cal_rules)))
test = s.filter(pl.col("held_out"))
y, yhat = test["c"].to_numpy(), test["c_pred"].to_numpy()
r2 = 1 - ((y - yhat) ** 2).sum() / ((y - y.mean()) ** 2).sum()
print(f"constants: p0={p0:.3f}  shares={np.round(share,3)}  pL={np.round(pL,3)}  pR={np.round(pR,3)}")
print(f"held-out rules: {test.height}; R^2 = {r2:.3f}; corr = {np.corrcoef(y, yhat)[0,1]:.3f}; median |err| = {np.median(np.abs(y-yhat)):.3f}")
# baseline: random heading (fresh neighbours / 4) is only available for the iso sample; use letter-group means instead
s.select("rule", "c", "c_pred", "held_out").write_csv("experiments/archive/2026-10-probe-growth-census/results/c_model.csv")
