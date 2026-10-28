# /// script
# dependencies = ["numpy", "polars"]
# ///
"""Instrument-identity check for Part B: mutants that coincide with base-sample rules (in_base_sample) were probed
twice, once in the base run (d4fd349 binary) and once in the mutant rerun (fa73570 binary), with the same seeds.
Their per-rule statistics must agree, or the paired d mixes two instruments. Same pipeline as analyse_mutants.py.
usage (repo root): uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/check_overlap.py"""
from pathlib import Path
import sys
import polars as pl

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
sys.path.insert(0, str(ROOT / "experiments/archive/2026-10-kappa-rule-space/scripts"))
from kcommon import per_rule, rule_means  # noqa: E402

raw = pl.read_csv(EXP / "dumps/mutants.csv")
runs = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first())
runs = runs.join(raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
core = runs.filter(pl.col("alpha_w").is_between(.25, .42) & (pl.col("kappa") > 0))
mt = rule_means(core, 6)  # same keep threshold as fresh_rules.csv (non-kept rules have null stats there)
ov = pl.read_csv(EXP / "results/mutants.csv").filter(pl.col("in_base_sample"))["mutant"].to_list()
fr = pl.read_csv(EXP / "results/fresh_rules.csv").filter(pl.col("rule").is_in(ov))
j = fr.select("rule", f_n=pl.col("n_runs"), f_lnk="lnk", f_lnA="lnA22", f_g="g_k").join(
    mt.filter(pl.col("base").is_in(ov)).select(pl.col("base").alias("rule"), m_n="n_runs", m_lnk="lnk", m_lnA="lnA22", m_g="g_k"), on="rule", how="full", coalesce=True)
out = [f"# cmd: uv run experiments/archive/2026-10-kappa-leadrun-fresh/scripts/check_overlap.py",
       f"overlap rules {len(ov)}; in fresh_rules.csv {fr.height}; kept in base {int(fr['kept'].sum())}; kept in rerun {int(mt['base'].is_in(ov).sum())}"]
d = j.with_columns(dn=(pl.col("f_n").fill_null(0) - pl.col("m_n").fill_null(0)).abs(),
                   dk=(pl.col("f_lnk") - pl.col("m_lnk")).abs(), dA=(pl.col("f_lnA") - pl.col("m_lnA")).abs(),
                   dg=(pl.col("f_g") - pl.col("m_g")).abs())
out.append(f"max |d n_runs| {d['dn'].max()}, max |d lnk| {d['dk'].max()}, max |d lnA22| {d['dA'].max()}, max |d g_k| {d['dg'].max()}")
out.append("IDENTICAL" if (d["dn"].max() == 0 and (d["dk"].fill_null(0).max() or 0) < 1e-9 and (d["dA"].fill_null(0).max() or 0) < 1e-9) else "MISMATCH")
(EXP / "results/overlap_check.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
