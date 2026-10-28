# /// script
# dependencies = ["polars"]
# ///
"""Feasibility summary of the registered pilot (README 'Pilot protocol'). No tail/kappa association is computed.

usage: uv run experiments/archive/2026-10-fixed-area-cycles/scripts/pilot_report.py
reads dumps/pilot16 and dumps/pilot8 (made by run_pilot.sh); writes results/pilot_feasibility.txt
"""
import math
import subprocess
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
CAP = 2**28
GATE_N = 10_000


def load(d):
    bands = pl.concat([pl.read_csv(f, schema_overrides={"i_q50": pl.Float64}) for f in sorted((EXP / "dumps" / d).glob("*.bands.csv"))], how="diagonal_relaxed")
    status = pl.concat([pl.read_csv(f) for f in sorted((EXP / "dumps" / d).glob("*.status.csv"))])
    kind = pl.when(pl.col("spec").str.starts_with("rotor")).then(pl.lit("rotor")).when(pl.col("spec").str.starts_with("rw")).then(pl.lit("rw")).otherwise(pl.lit("ant"))
    bands = bands.with_columns(kind.alias("kind"), pl.col("spec").str.split("@").list.first().alias("rule"))
    status = status.with_columns(kind.alias("kind"))
    return bands, status


def report(name, out):
    bands, status = load(name)
    out.append(f"\n===== {name} =====")
    out.append("run status by kind: " + str(status.group_by("kind", "stop").len().sort("kind", "stop").rows()))
    out.append(f"max t_final / cap: {status['t_final'].max()} / {CAP}  (G-budget needs <= cap/4 = {CAP // 4}: {'PASS' if status['t_final'].max() <= CAP // 4 else 'FAIL'})")
    out.append(f"unreached bands: {bands.filter(pl.col('reached_hi') == 0).height} of {bands.height}")
    b = bands.filter(pl.col("reached_hi") == 1).with_columns(
        (pl.col("i_complete") / 1).alias("n_i"),
        (pl.col("i_clip_steps") / pl.col("i_dep")).alias("i_cens"),
        (pl.col("i_complete_steps") / pl.col("steps")).alias("i_share"),
        (pl.col("i_complete") * 0.001).alias("rank_beyond_q999"),
    )
    out.append("conservation: fresh_from_interior sum = %d; B+I != steps rows = %d" % (b["fresh_from_interior"].sum(), b.filter(pl.col("b_dep") + pl.col("i_dep") != pl.col("steps")).height))
    for kind in ("ant", "rotor", "rw"):
        for band in sorted(b["band_id"].unique()):
            s = b.filter((pl.col("kind") == kind) & (pl.col("band_id") == band))
            q = lambda c, p: s[c].quantile(p, "nearest")
            out.append(
                f"[{kind} band{band} lo={s['lo'][0]}] n_specs={s.height}  t_end min/med/max={s['t_end'].min()}/{int(s['t_end'].median())}/{s['t_end'].max()}  "
                f"band steps med={int(s['steps'].median())}  complete-I n min/med/max={s['n_i'].min()}/{int(s['n_i'].median())}/{s['n_i'].max()}  "
                f"I-censor share max={s['i_cens'].max():.4f} (G-censor<=0.10: {'PASS' if s['i_cens'].max() <= 0.10 else 'FAIL'})  "
                f"clipped-I max frag max={s['i_clip_max'].max()}  complete-I share of band steps med={s['i_share'].median():.3f}"
            )
    # seeds per group: per-rule median per-seed count; the binding rule is the smallest.
    ant = b.filter(pl.col("kind") == "ant")
    for band in sorted(ant["band_id"].unique()):
        per_rule = ant.filter(pl.col("band_id") == band).group_by("rule").agg(pl.col("n_i").median().alias("med")).sort("med")
        worst = per_rule.row(0)
        need = math.ceil(GATE_N / worst[1])
        pow2 = 1 << (need - 1).bit_length()
        out.append(f"seeds/group for G-quantile, band{band}: binding rule {worst[0]} median per-seed n={worst[1]:.0f} -> need {need}, power of two {pow2}; "
                   f"rules with per-seed median n<1000: {per_rule.filter(pl.col('med') < 1000).height}")
        out.append("  five lowest per-rule medians: " + ", ".join(f"{r}:{m:.0f}" for r, m in per_rule.head(5).rows()))
        # within-rule seed spread of the counts (feasibility planning, not an association)
        spread = ant.filter(pl.col("band_id") == band).group_by("rule").agg((pl.col("n_i").max() / pl.col("n_i").min()).alias("r"))
        out.append(f"  max/min complete-I count across the 4 seeds: median {spread['r'].median():.2f}, max {spread['r'].max():.2f}")
    # Also: time to reach the last band, for planning
    out.append("slowest ant runs (t_final): " + ", ".join(f"{s}:{t}" for s, t in status.filter(pl.col('kind') == 'ant').sort('t_final', descending=True).head(5).select('spec', 't_final').rows()))


def main():
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    out = [
        "# pilot feasibility summary (no kappa/L999 association computed)",
        f"# command: uv run experiments/archive/2026-10-fixed-area-cycles/scripts/pilot_report.py   (inputs from scripts/run_pilot.sh) base commit {commit} (dirty workspace)",
        "# wall/RSS: see README pilot table (measured by run_pilot.sh).",
    ]
    for n in ("pilot16", "pilot8"):
        report(n, out)
    t1 = {f.name: f.read_bytes() for f in (EXP / "dumps" / "pilot16").glob("*") if f.suffix == ".csv"}
    t2 = {f.name: f.read_bytes() for f in (EXP / "dumps" / "pilot16_t1").glob("*") if f.suffix == ".csv"}
    out.append(f"\ndeterminism (4-thread vs 1-thread payload CSVs): {len(t1)} files, identical = {t1 == t2}")
    text = "\n".join(out) + "\n"
    (EXP / "results" / "pilot_feasibility.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
