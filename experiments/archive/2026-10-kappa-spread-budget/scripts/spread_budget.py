# /// script
# dependencies = []
# ///
"""Variance budget for the spread of ln kappa over stationary blob rules (ACTIVE.md: 'kappa/kappa_unif distribution').

POST HOC SYNTHESIS, not a registered test: every input value was seen before this script was written. No new runs, no refits;
numbers are parsed from committed result files, so each is traceable. Because kappa_unif is rule-independent (sd ln 0.004,
census_spread.txt), the spread of kappa/kappa_unif is the spread of ln kappa. Inputs come from three different cohorts
(census single runs; pool-192 patched starts; fresh 13-14 letter rules), so the shares below are approximate and carry no
propagated uncertainty. Output: results/spread_budget.{txt,json}.
usage (repo root): uv run experiments/archive/2026-10-kappa-spread-budget/scripts/spread_budget.py
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
RS = ROOT / "experiments/archive/2026-10-kappa-rule-space/results"
UB = ROOT / "experiments/archive/2026-10-kappa-uniform-baseline/results"
FILES = {"census": UB / "census_spread.txt", "w2": RS / "w2_stationarity.txt", "x2": RS / "x2_prefix_heldout.txt", "w3c": RS / "w3c_stats.txt"}
T = {k: p.read_text(encoding="utf-8", errors="replace") for k, p in FILES.items()}


def grab(text, pattern, group=1):
    m = re.search(pattern, text, re.M)
    if m is None:
        raise ValueError(f"missing: {pattern}")
    return float(m.group(group))


# 1. total spread: census, stationary blob rules, single blank-board run each
sd_census = grab(T["census"], r"kappa, stationary .*?sd_ln=([\d.]+)")
n_census = int(grab(T["census"], r"kappa, stationary .*?n=(\d+)"))
# 2. start-to-start noise: pool-192, patched starts, stationary rules, threshold 0.05 row of the sensitivity table
icc = grab(T["w2"], r"^0\.05\s+\d+\s+[\d.]+\s+n=.*?\|.*?\|\s*([\d.]+) \(\d+\)")
sd_pool = grab(T["w2"], r"^0\.05\s+\d+\s+[\d.]+\s+n=.*?\|\s*[\d.]+ -> ([\d.]+)")
# 3. prefix-8 held-out R^2: (a) pool patched means, stationary only (x2); (b) strict fresh stationary rules, prefix-only (w3c)
stat_x2 = T["x2"].split("[stationary only]", 1)[1]
r2_pool = grab(stat_x2, r"prefix<=8: held-out R\^2 on pool patched means ([+\-\d.]+)")
r2_fresh = grab(T["w3c"].split("[stationary]", 1)[1].split("[all]", 1)[0], r"prefix<=8: strict held-out R\^2 ([+\-\d.]+)")

var_total = sd_census ** 2
noise_share = 1 - icc            # share of single-run variance that is not rule-determined (patched starts)
rule_share = icc
rows = {}
for label, r2 in (("pool patched means", r2_pool), ("fresh rules, strict", r2_fresh)):
    explained = rule_share * r2   # prefix R^2 is against rule-level means, so scale to the single-run total
    rows[label] = dict(r2_prefix8=r2, explained_of_total=explained, rule_unexplained_of_total=rule_share - explained, noise_of_total=noise_share)
out = dict(
    sd_ln_kappa_census_stationary=sd_census, n_census=n_census, var_total=var_total,
    icc_pool_stationary=icc, sd_ln_kappa_pool_stationary=sd_pool,
    noise_share=noise_share, noise_sd=sd_pool * noise_share ** .5, rule_mean_sd=sd_pool * rule_share ** .5,
    budget=rows,
    caveats=["Total spread from census single runs; noise share from pool-192 patched starts (a different cohort and start condition).",
             "Prefix R^2 is against rule-level means (pool patched means, or strict fresh rules); scaled by the ICC to a share of single-run variance, which assumes the means are noise-free.",
             "Fresh-rule R^2 is on 13-14 letter rules, pool R^2 on census-length rules; the two differ by 0.08.",
             "No uncertainty is propagated; the shares are rough to about +-0.1.",
             "This budgets the SPREAD only. Why the location is about 0.8 x kappa_unif (below every walker reference) is untouched."],
    provenance=dict(command="uv run experiments/archive/2026-10-kappa-spread-budget/scripts/spread_budget.py",
                    input_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES.values()}))
(EXP / "results").mkdir(exist_ok=True)
(EXP / "results/spread_budget.json").write_text(json.dumps(out, indent=2) + "\n")
lines = ["# cmd: uv run experiments/archive/2026-10-kappa-spread-budget/scripts/spread_budget.py  (post hoc synthesis; no new runs)",
         f"total sd ln kappa (census stationary, n={n_census}): {sd_census:.3f}  (variance {var_total:.4f})",
         f"start-to-start noise share 1-ICC = {noise_share:.3f} (ICC {icc:.3f}, pool-192 stationary patched starts; sd ln kappa there {sd_pool:.3f}) -> noise sd {out['noise_sd']:.3f}, rule-mean sd {out['rule_mean_sd']:.3f}"]
for label, r in rows.items():
    lines.append(f"prefix-8 R^2 [{label}] {r['r2_prefix8']:+.3f}: shares of single-run variance: prefix-predictable {r['explained_of_total']:.2f}, "
                 f"rule-determined but not prefix-predictable {r['rule_unexplained_of_total']:.2f}, start noise {r['noise_of_total']:.2f}")
lines += ["caveats:"] + [f"  - {c}" for c in out["caveats"]]
(EXP / "results/spread_budget.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
