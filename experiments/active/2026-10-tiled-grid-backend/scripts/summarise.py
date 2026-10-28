"""Summarise results/runs into results/summary.csv and print a markdown table.

usage (repository root): uv run --frozen experiments/active/2026-10-tiled-grid-backend/scripts/summarise.py
Reads only results/runs/{WL}__{CFG}__r{K}.{json,time,load,err}, the dense CSVs and identity.tsv written by bench.sh.
Medians are over repetitions; the table also gives min and max, because the machine is shared (see provenance.txt).
"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path

import polars as pl

root = Path(__file__).resolve().parents[1]
name = sys.argv[1] if len(sys.argv) > 1 else "runs"
runs = root / "results" / name

ident = pl.read_csv(runs / "identity.tsv", separator="\t", has_header=False, new_columns=["wl", "cfg", "rep", "same"])

rows = []
for j in sorted(runs.glob("*__*__r*.json")):
    wl, cfg, rep = j.stem.split("__")
    rep = int(rep[1:])
    st = json.loads(j.read_text())
    tm = json.loads(j.with_suffix(".time").read_text())
    ld = json.loads(j.with_suffix(".load").read_text())
    steps = int(pl.read_csv(runs / f"{wl}__A__r{rep}.csv")["steps"][0])
    pr = (st.get("per_rule") or [{}])[0]
    rows.append(
        dict(
            wl=wl, cfg=cfg, rep=rep, steps=steps,
            wall_s=st["wall_s"], user_s=tm["user_s"], sys_s=tm["sys_s"],
            steps_per_s=steps / st["wall_s"],
            rss_mib=st["peak_rss_kb"] / 1024, time_rss_mib=tm["maxrss_kb"] / 1024,
            load_before=ld["load1_before"], load_after=ld["load1_after"],
            transitions_per_step=pr.get("transitions", 0) / steps if pr else None,
            misses=pr.get("misses"), evictions=pr.get("evictions"), creations=pr.get("creations"),
            peak_resident_tiles=pr.get("peak_resident_tiles"), end_tiles=pr.get("end_tiles"),
            peak_total_mib=(pr.get("peak_total_bytes") or 0) / 2**20 if pr else None,
            end_packed_mib=(pr.get("end_packed_bytes") or 0) / 2**20 if pr else None,
            end_raw_inactive_mib=(pr.get("end_raw_inactive_bytes") or 0) / 2**20 if pr else None,
            bytes_encoded_mib=(pr.get("bytes_encoded") or 0) / 2**20 if pr else None,
            onset_peak_total_mib=(pr.get("onset_peak_total_bytes") or 0) / 2**20 if pr and pr.get("onset_peak_total_bytes") else None,
        )
    )
df = pl.DataFrame(rows, infer_schema_length=None)

agg = (
    df.group_by("wl", "cfg", maintain_order=True)
    .agg(
        pl.len().alias("reps"),
        pl.col("steps").first(),
        pl.col("steps_per_s").median().alias("sps_med"),
        pl.col("steps_per_s").min().alias("sps_min"),
        pl.col("steps_per_s").max().alias("sps_max"),
        pl.col("wall_s").median().alias("wall_med"),
        pl.col("rss_mib").median().alias("rss_med"),
        pl.col("rss_mib").min().alias("rss_min"),
        pl.col("rss_mib").max().alias("rss_max"),
        pl.col("user_s").median().alias("user_med"),
        pl.col("sys_s").median().alias("sys_med"),
        pl.col("load_before").max().alias("load_max"),
        pl.col("transitions_per_step").first(),
        pl.col("misses").first(),
        pl.col("evictions").first(),
        pl.col("end_tiles").first(),
        pl.col("peak_resident_tiles").first(),
        pl.col("peak_total_mib").first(),
        pl.col("end_packed_mib").first(),
        pl.col("end_raw_inactive_mib").first(),
        pl.col("bytes_encoded_mib").first(),
        pl.col("onset_peak_total_mib").first(),
    )
)
dense = agg.filter(pl.col("cfg") == "A").select("wl", pl.col("sps_med").alias("dense_sps"), pl.col("rss_med").alias("dense_rss"))
bcfg = agg.filter(pl.col("cfg") == "B6").select("wl", pl.col("sps_med").alias("b6_sps"), pl.col("rss_med").alias("b6_rss"))
agg = (
    agg.join(dense, on="wl").join(bcfg, on="wl")
    .with_columns(
        (pl.col("sps_med") / pl.col("dense_sps")).alias("tput_vs_dense"),
        (pl.col("sps_med") / pl.col("b6_sps")).alias("tput_vs_B6"),
        (pl.col("rss_med") / pl.col("dense_rss")).alias("rss_vs_dense"),
        (pl.col("rss_med") / pl.col("b6_rss")).alias("rss_vs_B6"),
    )
    .drop("dense_sps", "dense_rss", "b6_sps", "b6_rss")
)
out = root / "results" / ("summary.csv" if name == "runs" else f"summary_{name}.csv")
agg.write_csv(out, float_precision=4)

bad = ident.filter(pl.col("same") != 1)
print(f"{ident.height} runs, CSV identical to dense in {ident.height - bad.height}; not identical: {bad.height}")
with pl.Config(tbl_rows=100, tbl_cols=30, fmt_str_lengths=40, tbl_width_chars=250):
    print(
        agg.select(
            "wl", "cfg", "reps", "sps_med", "sps_min", "sps_max", "tput_vs_dense", "tput_vs_B6", "rss_med", "rss_min", "rss_max",
            "rss_vs_dense", "rss_vs_B6", "transitions_per_step", "misses", "evictions", "end_tiles", "load_max",
        ).with_columns(pl.col(pl.Float64).round(3))
    )
print(f"wrote {out}")
