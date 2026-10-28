"""G1(a,b): reserve-gate projection from pilot-v2 final steps (results/ only).
Predictive model: log t_final = mu_rule + eps, pooled empirical residuals,
mu_rule uncertainty from 4 seeds propagated (t3 scaled). Seeded; single thread.
Usage: uv run scripts/reserve_gate.py [--validation reserve-v1]
"""
from pathlib import Path
import argparse, json, re, hashlib
import numpy as np
ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument("--validation", default=None)
args = ap.parse_args()
audit = json.loads((EXP / "results/pilot-v2.audit.json").read_text())
runs = audit["batches"]["ants"]["runs"]
by = {}
for r in runs:
    rule = r["spec"].split("@")[0]
    by.setdefault(rule, []).append(int(r["status"]["t_final"]))
rules = sorted(by)
logs = np.array([np.log(by[r]) for r in rules])           # 44 x 4
mu = logs.mean(1); res = (logs - mu[:, None]) * np.sqrt(4 / 3)   # unbiased-scale residuals
pooled = res.ravel()
s = float(np.sqrt((res ** 2).sum() / (res.size - len(rules)) * 0 + (res ** 2).mean()))
rng = np.random.default_rng(20261016)
N_SEEDS, DRAWS = 32, 2000
pmax = np.empty(DRAWS)
rulemax = np.empty((DRAWS, len(rules)))
for d in range(DRAWS):
    mu_draw = mu + s / 2.0 * rng.standard_t(3, size=len(rules)) / np.sqrt(3.0)   # t3 scaled to unit variance
    eps = rng.choice(pooled, size=(len(rules), N_SEEDS))
    lt = mu_draw[:, None] + eps
    rulemax[d] = lt.max(1)
    pmax[d] = lt.max()
q_pooled = {f"q{p}": float(np.exp(np.quantile(pmax, p / 100))) for p in (50, 90, 99, 99.9)}
# The pooled-residual model registered at 00:10 is retained above but DISCARDED: per-rule
# sd of log t_final spans 0.006-1.6 (heteroscedastic), so pooling puts the large spread of
# cheap rules on the slowest rules. Replacement (deviation, logged): per-rule predictive,
# sigma_r^2 ~ scaled-inv-chi2(3, s_r^2), mu_r ~ N(ybar_r, sigma_r^2/4), eps ~ N(0, sigma_r^2).
sr = logs.std(1, ddof=1)
pmax = np.empty(DRAWS); rulemax = np.empty((DRAWS, len(rules)))
for d in range(DRAWS):
    sig = sr * np.sqrt(3.0 / rng.chisquare(3, size=len(rules)))
    mu_d = mu + sig / 2.0 * rng.standard_normal(len(rules))
    lt = mu_d[:, None] + sig[:, None] * rng.standard_normal((len(rules), N_SEEDS))
    rulemax[d] = lt.max(1); pmax[d] = lt.max()
q = {f"q{p}": float(np.exp(np.quantile(pmax, p / 100))) for p in (50, 90, 99, 99.9)}
slow = sorted(rules, key=lambda r: -max(by[r]))[:4]
out = dict(
    command="uv run experiments/archive/2026-10-kappa-tail-budget/scripts/reserve_gate.py",
    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    audit_sha256=hashlib.sha256((EXP / "results/pilot-v2.audit.json").read_bytes()).hexdigest(),
    pilot_max_final_step=int(max(max(v) for v in by.values())),
    pooled_residual_sd_log=s, draws=DRAWS, seeds_per_rule_projected=N_SEEDS, rules=len(rules),
    DISCARDED_parametric_projection_per_rule_model=q, DISCARDED_parametric_projection_pooled_model=q_pooled,
    projection_discard_reason="log-normal extrapolation is invalid: per-rule sd of log t_final spans 0.006-1.6 with a 29x range in one cheap rule; extreme-value quantiles are driven by the inverse-chi2 / pooled spread of cheap rules, not by physics. Gate 1(b) is replaced by a direct fresh validation batch (see NOTEBOOK).",
    per_rule_sd_log_range=[float(sr.min()), float(sr.max())],
    slowest_rules=slow,
    candidates={},
)
for name, C in (("2^30", 2 ** 30), ("2^32", 2 ** 32), ("2^33", 2 ** 33)):
    res_ = C / 4
    out["candidates"][name] = dict(cap=C, reserve=res_, pilot_ok=out["pilot_max_final_step"] <= res_,
                                   headroom_over_pilot_max=res_ / out["pilot_max_final_step"])
# wall times (contended, 4 workers) from pilot-v2.log
secs = [float(m[1]) for l in (EXP / "results/pilot-v2.log").read_text().splitlines() if (m := re.search(r"seconds=([\d.]+)", l))]
out["pilot_traj_seconds"] = dict(n=len(secs), median=float(np.median(secs)), max=max(secs), total_cpu=sum(secs))
out["confirmation_cost_projection_hours_at_2_threads"] = out["pilot_traj_seconds"]["total_cpu"] / 180 * 1408 / 2 / 3600
if args.validation:
    a = json.loads((EXP / f"results/{args.validation}.audit.json").read_text())["batches"]["ants"]
    t = {}
    for r in a["runs"]:
        t.setdefault(r["spec"].split("@")[0], []).append(int(r["status"]["t_final"]))
    out["validation"] = dict(name=args.validation, completed=a["completed"], requested=a["requested"], escaped=a["escaped"],
                             max_t=a["max_t"], per_rule_max={k: max(v) for k, v in t.items()},
                             per_rule_mean={k: float(np.mean(v)) for k, v in t.items()},
                             max_over_pilot_rule_max={k: max(v) / max(by[k]) for k, v in t.items()},
                             all_within_quarter_cap={C_: a["max_t"] <= C_ / 4 for C_ in (2 ** 32, 2 ** 33)})
(EXP / "results/reserve_projection.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(json.dumps({k: out[k] for k in ("pilot_max_final_step", "candidates", "pilot_traj_seconds", "confirmation_cost_projection_hours_at_2_threads")}, indent=1))
