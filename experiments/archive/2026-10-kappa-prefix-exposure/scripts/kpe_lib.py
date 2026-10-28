"""Shared loaders and definitions for kappa-prefix-exposure (sampler output -> polars tables).

All pooled quantities are ratios of sums over a named seed set, never means of per-seed ratios,
so a seed with few events weighs by its events. Episode thresholds WS match the sampler.
Definitions (per band, pooled over a seed set of valid runs):
  bs        = sum b_dep / sum steps                       (boundary-step share B/S)
  kappa_end = bs / (sum perim_end / sum area_end)         (endpoint kappa)
  kappa_time= bs / (sum sum_pa / sum steps)               (time-normalised kappa)
  Lam_w     = (sum ep_long_w + 0.5) / sum new_cells       (episodes begun in band lasting >= w states, per discovered cell)
  tau_w     = sum tail_w / sum steps                      (share of band time spent in episodes lasting >= w states)
"""
from pathlib import Path

import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]
RES = EXP / "results"
WS = [1, 16, 64, 256, 1024]


def _split(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(rule=pl.col("spec").str.split("@").list.first(), seed=pl.col("spec").str.split("@").list.last().cast(pl.Int64))


def load_bands(d: Path) -> pl.DataFrame:
    """One row per (spec, band): band tallies, episode tallies (wide), run status; `valid` drops attained
    runs whose band-touching interior episode was still open (and short of a threshold) at the stop."""
    frames = [pl.read_csv(p, infer_schema_length=0) for p in sorted(d.glob("*.bands.csv"))]
    b = pl.concat(frames).with_columns(
        [pl.col(c).cast(pl.Int64) for c in frames[0].columns if c not in ("spec", "fresh_colour", "sum_pa")] + [pl.col("sum_pa").cast(pl.Float64)])
    ep = pl.concat([pl.read_csv(p, schema_overrides={c: pl.Int64 for c in ("band_id", "w", "ep_n", "ep_long_n", "tail_steps")}) for p in sorted(d.glob("*.episodes.csv"))])
    wide = ep.group_by("spec", "band_id").agg(
        ep_n=pl.col("ep_n").first(),
        **{f"epl_{w}": pl.col("ep_long_n").filter(pl.col("w") == w).first() for w in WS},
        **{f"tail_{w}": pl.col("tail_steps").filter(pl.col("w") == w).first() for w in WS})
    b = b.join(wide, on=["spec", "band_id"], how="left")
    st = pl.concat([pl.read_csv(p, schema_overrides={"open_begin_band": pl.Utf8, "open_len": pl.Int64}) for p in sorted(d.glob("*.status.csv"))]).select(
        "spec", "stop", "t_final", "area_final", "open_begin_band", "open_len")
    b = _split(b.join(st, on="spec"))
    b = b.with_columns(attained=pl.col("reached_hi") == 1, new_cells=pl.col("area_end") - pl.col("area_start"))
    flagged = (pl.col("open_begin_band") == pl.col("band_id").cast(pl.Utf8)) & (pl.col("open_len") < max(WS))
    return b.with_columns(valid=pl.col("attained") & ~flagged.fill_null(False))


def load_reads(d: Path) -> pl.DataFrame:
    return _split(pl.concat([pl.read_csv(p, schema_overrides={c: pl.Int64 for c in ("band_id", "colour", "depth", "cycle", "n")}) for p in sorted(d.glob("*.reads.csv"))]))


def load_whole(d: Path) -> pl.DataFrame:
    return _split(pl.concat([pl.read_csv(p, schema_overrides={c: pl.Int64 for c in ("colour", "reads", "first_t", "first_area", "first_depth")}) for p in sorted(d.glob("*.whole.csv"))]))


def pooled(b: pl.DataFrame, by: list[str]) -> pl.DataFrame:
    """Pool valid band rows by `by` (ratio of sums)."""
    a = b.filter(pl.col("valid"))
    cols = ["steps", "b_dep", "sum_pa", "perim_end", "area_end", "new_cells", "ep_n", "launch_n", "launch_left", "launch_sum_fwd", "launch_sum_r2"] \
        + [f"epl_{w}" for w in WS] + [f"tail_{w}" for w in WS]
    out = a.group_by(by).agg(n_seeds=pl.len(), **{c: pl.col(c).sum() for c in cols}).with_columns(
        bs=pl.col("b_dep") / pl.col("steps"),
        lnbs=(pl.col("b_dep") / pl.col("steps")).log(),
        kappa_end=(pl.col("b_dep") / pl.col("steps")) / (pl.col("perim_end") / pl.col("area_end")),
        kappa_time=(pl.col("b_dep") / pl.col("steps")) / (pl.col("sum_pa") / pl.col("steps")),
        mean_fwd=pl.col("launch_sum_fwd") / pl.col("launch_n"),
    )
    return out.with_columns(
        [((pl.col(f"epl_{w}") + 0.5) / pl.col("new_cells")).alias(f"Lam_{w}") for w in WS]
        + [(pl.col(f"tail_{w}") / pl.col("steps")).alias(f"tau_{w}") for w in WS])


def colour_exposure(reads: pl.DataFrame, bands: pl.DataFrame, rule: str, seeds: list[int], band_id: int, colour: int) -> dict:
    """Exposure of one colour in the run of `rule`, pooled over `seeds` (valid runs only)."""
    ok = bands.filter((pl.col("rule") == rule) & pl.col("seed").is_in(seeds) & (pl.col("band_id") == band_id) & pl.col("valid"))
    steps = int(ok["steps"].sum())
    r = reads.filter((pl.col("rule") == rule) & pl.col("seed").is_in(ok["seed"].to_list()) & (pl.col("band_id") == band_id) & (pl.col("colour") == colour))
    n = int(r["n"].sum())
    by_d = {d: int(r.filter(pl.col("depth") == d)["n"].sum()) for d in range(6)}
    mean_depth = sum(d * v for d, v in by_d.items()) / n if n else np.nan
    return dict(steps=steps, reads=n, share=n / steps if steps else np.nan, boundary_share=by_d[0] / n if n else np.nan,
                near_share=(by_d[1] + by_d[2]) / n if n else np.nan, mean_depth=mean_depth, by_depth=by_d)
