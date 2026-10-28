# /// script
# dependencies = ["polars", "numpy"]
# ///
"""Control-walker calibration of the fixed-area estimator (rotor, random walk; seeds 801..928).

usage: uv run experiments/archive/2026-10-fixed-area-cycles/scripts/controls_report.py
reads dumps/controls_w{32,16,8,4} (scripts/run_controls.sh); writes results/controls.txt and results/controls_summary.csv.
Reports bias, not pass/fail: width dependence at fixed entry area, endpoint vs time-averaged P/A,
direct vs cycle-reconstructed boundary occupancy, completed-only vs clipped accounting, and the
group-to-group scatter of the pooled nearest-rank quantiles (16 seeds per group, 8 groups).
"""
import subprocess
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SEEDS = list(range(801, 929))
GROUP = 16
QS = (0.5, 0.99, 0.999)


def nearest_rank(v, q):
    v = np.sort(v)
    return v[max(int(np.ceil(q * len(v))), 1) - 1]


def main():
    out, rows = [], []
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    out += ["# control calibration of the fixed-area estimator (rotor, rw; seeds 801..928; 8 groups x 16 seeds)",
            f"# command: uv run experiments/archive/2026-10-fixed-area-cycles/scripts/controls_report.py; base commit {commit} (dirty workspace)",
            "# columns: mean over seeds (sd between seeds) unless noted; q = pooled nearest-rank quantile of complete-contained I durations per 16-seed group, mean (sd over 8 groups) of ln q"]
    for kind in ("rotor", "rw"):
        for w in (32, 16, 8, 4):
            d = EXP / "dumps" / f"controls_w{w}"
            b = pl.concat([pl.read_csv(d / f"{kind}_{s}.bands.csv", schema_overrides={"i_q50": pl.Float64}) for s in SEEDS]).with_columns(pl.col("spec").str.split(":").list.last().cast(pl.Int64).alias("seed"))
            assert b["reached_hi"].min() == 1
            b = b.with_columns(
                (pl.col("b_dep") / pl.col("steps")).alias("fB"),
                (pl.col("new_cells") / pl.col("b_dep")).alias("c"),
                (pl.col("perim_end") / pl.col("area_end")).alias("pa_end"),
                (pl.col("sum_pa") / pl.col("steps")).alias("pa_time"),
                (pl.col("cycle_d_sum") / (pl.col("cycle_d_sum") + pl.col("cycle_t_sum"))).alias("fB_recon"),
                (pl.col("i_complete_steps") / pl.col("i_complete")).alias("mean_i"),
                (pl.col("i_clip_steps") / pl.col("i_dep")).alias("i_clip_share"),
                (pl.col("b_clip_steps") / pl.col("b_dep")).alias("b_clip_share"),
            ).with_columns(
                (pl.col("fB") / pl.col("pa_end")).log().alias("lnk_end"),
                (pl.col("fB") / pl.col("pa_time")).log().alias("lnk_time"),
                (pl.col("pa_end") / pl.col("pa_time")).alias("pa_ratio"),
                (pl.col("fB_recon") - pl.col("fB")).alias("recon_gap"),
            )
            for band in (0, 1):
                s = b.filter(pl.col("band_id") == band).sort("seed")
                lq = {q: [] for q in QS}
                for g in range(len(SEEDS) // GROUP):
                    dur = np.concatenate([np.fromfile(d / f"{kind}_{sd}.idur{band}.u32", dtype="<u4") for sd in SEEDS[g * GROUP:(g + 1) * GROUP]])
                    assert len(dur) == s.filter(pl.col("seed").is_in(SEEDS[g * GROUP:(g + 1) * GROUP]))["i_complete"].sum()
                    for q in QS:
                        lq[q].append(np.log(nearest_rank(dur, q)))
                ms = lambda c: f"{s[c].mean():.4f}({s[c].std():.4f})"
                row = dict(walker=kind, w=f"1/{w}", band=band, lo=s["lo"][0], n_seeds=s.height, steps=s["steps"].mean(), I_complete_per_seed=s["i_complete"].mean(),
                           fB=s["fB"].mean(), fB_sd=s["fB"].std(), c=s["c"].mean(), mean_I=s["mean_i"].mean(), pa_ratio=s["pa_ratio"].mean(),
                           dlnk_end_minus_time=(s["lnk_end"] - s["lnk_time"]).mean(), lnk_end=s["lnk_end"].mean(), lnk_end_sd=s["lnk_end"].std(), lnk_time=s["lnk_time"].mean(),
                           recon_gap=s["recon_gap"].mean(), recon_gap_sd=s["recon_gap"].std(), i_clip_share_max=s["i_clip_share"].max(), b_clip_share_mean=s["b_clip_share"].mean(),
                           **{f"lnq{str(q)[2:]}": float(np.mean(lq[q])) for q in QS}, **{f"lnq{str(q)[2:]}_sd": float(np.std(lq[q], ddof=1)) for q in QS})
                rows.append(row)
                out.append(f"{kind:5s} w=1/{w:<2d} band{band} (lo={row['lo']}): steps={row['steps']:.0f}  nI/seed={row['I_complete_per_seed']:.0f}  fB={ms('fB')}  c={ms('c')}  meanI={ms('mean_i')}  "
                           f"PA_end/PA_time={ms('pa_ratio')}  lnk_end={ms('lnk_end')}  (lnk_end-lnk_time)={row['dlnk_end_minus_time']:.4f}  "
                           f"fB_recon-fB={ms('recon_gap')}  I-clip max share={row['i_clip_share_max']:.5f}  B-clip share={row['b_clip_share_mean']:.5f}  "
                           f"lnq50={row['lnq5']:.3f}({row['lnq5_sd']:.3f}) lnq99={row['lnq99']:.3f}({row['lnq99_sd']:.3f}) lnq999={row['lnq999']:.3f}({row['lnq999_sd']:.3f})")
    df = pl.DataFrame(rows)
    df.write_csv(EXP / "results" / "controls_summary.csv")
    out.append("\n# width bias at fixed entry area: value(w) - value(1/32), in units of the between-seed standard error of the mean at that w")
    for kind in ("rotor", "rw"):
        for band in (0, 1):
            base = df.filter((pl.col("walker") == kind) & (pl.col("band") == band) & (pl.col("w") == "1/32")).row(0, named=True)
            for w in ("1/16", "1/8", "1/4"):
                r = df.filter((pl.col("walker") == kind) & (pl.col("band") == band) & (pl.col("w") == w)).row(0, named=True)
                sem = r["lnk_end_sd"] / np.sqrt(r["n_seeds"])
                out.append(f"{kind:5s} band{band} {w:4s}: d fB={r['fB'] - base['fB']:+.4f}  d lnk_end={r['lnk_end'] - base['lnk_end']:+.4f} ({(r['lnk_end'] - base['lnk_end']) / sem:+.1f} sem)  "
                           f"d lnq999={r['lnq999'] - base['lnq999']:+.3f} (group sd {r['lnq999_sd']:.3f})  d c={r['c'] - base['c']:+.4f}")
    text = "\n".join(out) + "\n"
    (EXP / "results" / "controls.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
