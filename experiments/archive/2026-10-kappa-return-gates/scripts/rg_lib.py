"""Feature definitions shared by pilot and confirmation analyses (frozen in README.md)."""
import math
import numpy as np
import polars as pl

MIN_EXC = 50  # completed excursions per exit heading, pooled over the seed set


def spread(n, s):
    v = [math.log(s[h] / n[h]) for h in range(4) if n[h] >= MIN_EXC]
    return max(v) - min(v) if len(v) >= 2 else float("nan")


def rule_band_features(g: pl.DataFrame) -> dict:
    """g: run rows (one band) for ONE rule and ONE seed set. Everything pooled or averaged over seeds."""
    steps, b = g["steps"].sum(), g["B"].sum()
    d = [g[f"d{i}"].sum() for i in range(6)]
    rim = d[1] + d[2] + d[3] + d[4]
    ok = g.filter(pl.col("g1_events") > 0)
    g1 = float((ok["g1_obs"] - ok["g1_null"]).mean()) if ok.height else float("nan")
    return dict(
        n_seeds=g.height, y=math.log(b / steps),
        f_lnpa=math.log(g["sum_pa"].sum() / steps),
        f_lnbrun=math.log(g["b_run_steps"].sum() / g["b_runs"].sum()) if g["b_runs"].sum() else float("nan"),
        f_rimshape=math.log(d[1] / rim) if d[1] and rim else float("nan"),
        f_interior=math.log(d[5] / rim) if d[5] and rim else float("nan"),
        f_lnq=math.log(b / steps),
        g1=g1,
        g2=spread([g[f"exc_n{h}"].sum() for h in range(4)], [g[f"exc_s{h}"].sum() for h in range(4)]),
        n_events=int(g["g1_events"].sum()),
        reclass_share=float((g["reclass_in"].sum() + g["reclass_out"].sum()) / max(1, g["exits"].sum() + g["entries"].sum() + g["reclass_in"].sum() + g["reclass_out"].sum())),
    )


def table(runs: pl.DataFrame, rules: list, band: int, seeds=None) -> pl.DataFrame:
    rows = []
    for r in rules:
        g = runs.filter((pl.col("rule") == r) & (pl.col("band") == band) & (pl.col("reached_hi") == 1))
        if seeds is not None:
            g = g.filter(pl.col("seed").is_in(list(seeds)))
        rows.append(dict(rule=r, **rule_band_features(g)) if g.height else dict(rule=r, n_seeds=0))
    return pl.DataFrame(rows, infer_schema_length=None)
