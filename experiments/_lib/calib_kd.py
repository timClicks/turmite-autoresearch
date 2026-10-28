"""Calibration part B: compare rotor runs with Kapri & Dhar (2009) and
Bou-Rabee & Peres (2026).

Targets (Kapri & Dhar):
  - mean square displacement exponent: R_N ~ N^nu, nu = 0.33 +- 0.01
  - mean radius of the nbar = 1 contour at N = 1e6: 145.436 +- 0.003
  - boundary width W_N ~ N^delta, delta = 0.136 (+- 0.02 in text, 0.002 in caption)
  - "most" sites visited exactly 4 times in the last 4S steps
  - scaling form nbar(r) = a N^(1/3) (1 - r / (b N^(1/3))), a = 0.5, b = 1.38
Target (Bou-Rabee & Peres): S(N) / N^(2/3) tends to a deterministic constant,
so its relative spread across seeds should shrink with N.
"""
import glob
import json
import sys

import numpy as np
import polars as pl

CROP = 1024


def contour_radius(nbar, level=1.0, nang=3600):
    """Mean radius of the outermost crossing of `level` along rays from the
    origin, using bilinear interpolation (Kapri & Dhar interpolate linearly
    on triangles; both are linear interpolations of the same field)."""
    c = CROP // 2
    radii = []
    rs = np.arange(0, c - 2, 0.05)
    for th in np.linspace(0, 2 * np.pi, nang, endpoint=False):
        xs, ys = c + rs * np.cos(th), c + rs * np.sin(th)
        x0, y0 = np.floor(xs).astype(int), np.floor(ys).astype(int)
        fx, fy = xs - x0, ys - y0
        v = (nbar[y0, x0] * (1 - fx) * (1 - fy) + nbar[y0, x0 + 1] * fx * (1 - fy)
             + nbar[y0 + 1, x0] * (1 - fx) * fy + nbar[y0 + 1, x0 + 1] * fx * fy)
        above = np.nonzero(v >= level)[0]
        k = above[-1]  # last point at or above the level
        # interpolate between rs[k] and rs[k+1]
        r = rs[k] + (v[k] - level) / (v[k] - v[k + 1]) * (rs[k + 1] - rs[k])
        radii.append(r)
    radii = np.array(radii)
    return float(radii.mean()), float(radii.std()), radii


def main(long_dir, short_dir):
    out = {}
    ck = pl.concat([pl.read_csv(p) for p in glob.glob(f"{long_dir}/checkpoints_*.csv")])
    g = ck.group_by("N").agg(R2=pl.col("R2").mean(), S=pl.col("S").mean(), S_cv=pl.col("S").std() / pl.col("S").mean(),
                             W=pl.col("W").mean(), seeds=pl.len()).sort("N")
    N = g["N"].to_numpy().astype(float)
    nu, nu_err = np.polyfit(np.log(N), 0.5 * np.log(g["R2"].to_numpy()), 1, cov=True)
    dl, dl_err = np.polyfit(np.log(N), np.log(g["W"].to_numpy()), 1, cov=True)
    sa, sa_err = np.polyfit(np.log(N), np.log(g["S"].to_numpy()), 1, cov=True)
    # Seed-bootstrap for exponent uncertainties.
    seeds = ck["seed"].unique().to_numpy()
    rng = np.random.default_rng(1)
    boot = {"nu": [], "delta": [], "s": []}
    piv = {k: ck.pivot(on="N", index="seed", values=k).sort("seed").drop("seed").to_numpy() for k in ["R2", "W", "S"]}
    for _ in range(400):
        idx = rng.integers(0, len(seeds), len(seeds))
        boot["nu"].append(np.polyfit(np.log(N), 0.5 * np.log(piv["R2"][idx].mean(0)), 1)[0])
        boot["delta"].append(np.polyfit(np.log(N), np.log(piv["W"][idx].mean(0)), 1)[0])
        boot["s"].append(np.polyfit(np.log(N), np.log(piv["S"][idx].mean(0)), 1)[0])
    out["seeds_long"] = int(g["seeds"][0])
    out["nu"] = [round(float(nu[0]), 4), round(float(np.std(boot["nu"])), 4)]
    out["delta"] = [round(float(dl[0]), 4), round(float(np.std(boot["delta"])), 4)]
    out["range_exponent"] = [round(float(sa[0]), 4), round(float(np.std(boot["s"])), 4)]
    # local exponents between successive checkpoints, to see drift
    out["delta_local"] = [round(float(x), 3) for x in np.diff(np.log(g["W"].to_numpy())) / np.diff(np.log(N))]
    out["nu_local"] = [round(float(x), 3) for x in 0.5 * np.diff(np.log(g["R2"].to_numpy())) / np.diff(np.log(N))]
    out["S_over_N23"] = [round(float(x), 4) for x in g["S"].to_numpy() / N ** (2 / 3)]
    out["S_cv"] = [round(float(x), 4) for x in g["S_cv"].to_numpy()]
    out["N"] = [int(x) for x in N]

    e4 = np.concatenate([np.loadtxt(p) for p in glob.glob(f"{long_dir}/exactly4_*.txt") + glob.glob(f"{short_dir}/exactly4_*.txt")])
    out["exactly4"] = [round(float(e4.mean()), 4), round(float(e4.std()), 4), len(e4)]

    for name in ["contour_long", "contour_all"]:
        files = glob.glob(f"{long_dir}/visits_1e6_*.f64") + (glob.glob(f"{short_dir}/visits_1e6_*.f64") if name == "contour_all" else [])
        if not files:
            continue
        tot, n = None, 0
        for path in files:
            seed0 = path.split("_")[-1].split(".")[0]
            k = sum(1 for _ in open(path.replace(f"visits_1e6_{seed0}.f64", f"exactly4_{seed0}.txt")))
            v = np.fromfile(path, dtype="<f8").reshape(CROP, CROP)
            tot = v if tot is None else tot + v
            n += k
        nbar = tot / n
        mean_r, sd_r, radii = contour_radius(nbar)
        # Uncertainty from seed-to-seed variation: split into 4 chunks of files.
        out[name] = {"seeds": n, "radius": round(mean_r, 3), "angular_sd": round(sd_r, 3)}
        # Profile along the axes for the scaling form.
        c = CROP // 2
        L = 500
        prof = 0.25 * (nbar[c, c:c + L] + nbar[c, c - L + 1:c + 1][::-1] + nbar[c:c + L, c] + nbar[c - L + 1:c + 1, c][::-1])
        out[name]["profile_r0_10"] = [round(float(v), 3) for v in prof[:11]]
        out[name]["nbar_at_origin"] = round(float(nbar[c, c]), 3)
        # Linear fit of nbar(r) on 20 <= r <= 120 -> a N^(1/3) (1 - r/(b N^(1/3)))
        r = np.arange(len(prof))
        s = (r >= 20) & (r <= 120)
        m, k0 = np.polyfit(r[s], prof[s], 1)
        N13 = 1e6 ** (1 / 3)
        a = k0 / N13
        b = -k0 / m / N13
        out[name]["a"], out[name]["b"], out[name]["ab2"] = round(float(a), 3), round(float(b), 3), round(float(a * b * b), 3)
        np.save(f"{long_dir}/../nbar_{name}.npy", nbar)
    json.dump(out, open("experiments/archive/2026-10-calib-instrument-calibration/results/calib_partB.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
