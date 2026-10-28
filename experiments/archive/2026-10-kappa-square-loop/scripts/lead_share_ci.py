# /// script
# dependencies = ["numpy", "polars"]
# ///
"""ACTIVE.md item: CI on 'lead-colour laps are ~8% of loop steps' (README, P2). Post hoc, unregistered.
Per lead, ratio of rule-means mean(frac_lead)/mean(frac_all) with a percentile bootstrap over rules (rule = unit; seeds are
already averaged within rule in loops_per_rule.csv). Also reports the pooled share over all leads.
usage (repo root): uv run experiments/archive/2026-10-kappa-square-loop/scripts/lead_share_ci.py"""
from pathlib import Path
import numpy as np, polars as pl

EXP = Path(__file__).resolve().parents[1]
SEED, NB = 20261016, 4000
rng = np.random.default_rng(SEED + 41)
d = pl.read_csv(EXP / "results/loops_per_rule.csv", comment_prefix="#")
out = [f"# cmd: uv run experiments/archive/2026-10-kappa-square-loop/scripts/lead_share_ci.py  seed {SEED}  bootstraps {NB} over rules (post hoc)",
       f"rules {d.height}; share = mean(frac_lead)/mean(frac_all) over rules; 95% percentile CI"]


def share(fl, fa):
    return float(fl.sum() / fa.sum())


def line(name, sub):
    fl, fa = sub["frac_lead"].to_numpy(), sub["frac_all"].to_numpy()
    ix = rng.integers(0, len(fl), (NB, len(fl)))
    bs = fl[ix].sum(1) / fa[ix].sum(1)
    lo, hi = np.quantile(bs, [.025, .975])
    ls = sub["lead_share"].to_numpy()  # mean of per-rule shares: the estimator behind the README's 8%
    mlo, mhi = np.quantile(ls[ix].mean(1), [.025, .975])
    out.append(f"{name}: n={len(fl)} ratio-of-means share {share(fl, fa):.4f} [{lo:.4f}, {hi:.4f}]; "
               f"mean of per-rule shares {ls.mean():.4f} [{mlo:.4f}, {mhi:.4f}]  frac_lead mean {fl.mean():.5f}")


for L in range(1, 7):
    sub = d.filter(pl.col("lead") == L)
    if sub.height >= 2:
        line(f"lead {L}", sub)
line("all leads", d)
(EXP / "results/lead_share_ci.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
