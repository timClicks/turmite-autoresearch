# /// script
# dependencies = ["nbformat"]
# ///
"""Builds notebook.ipynb (then execute it: see README). usage: uv run experiments/archive/2026-10-c-law-mechanism/scripts/build_notebook.py"""
from pathlib import Path

import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# Mechanism of the c law (1/c = 1.36 + 0.70 lead) and what it implies for kappa

## Question and why it matters
In chaotic generalised Langton's ants, c = births per boundary step is almost a function of the rule's opening same-letter run (`lead`): 1/c = 1.363 + 0.696 lead on the census. This notebook asks why, whether it is a fresh-ground (edge) effect, and whether the earlier "lead raises kappa at fixed area" finding is real.
Registrations, failed predictions and deviations: `README.md`; thinking: `NOTEBOOK.md`; summary in `notes/open-questions-hypotheses.md`. Predecessor: `experiments/archive/2026-10-kappa-chiral-edge`.

## Assumptions and definitions
- Boundary step: starts on a visited cell with an unvisited 4-neighbour (as `src/probe.rs`, inner-hole rims included). Birth: step onto a never-visited cell. c = births / boundary steps. Window = last octave of 2^24 steps on a 4096 board unless stated.
- `src/edge_trace.rs` is the instrument; it agrees exactly with `probe_walker` and a HashMap brute force (`tests/edge_trace.rs`). **Held** (calibration: rotor c 0.4977 vs 0.498, random walk 0.448 vs 0.44).
- Assumption: Stage 2/3 filter "kept" = not escaped, births >= 200, 1.3 <= area/area_t0 <= 1.9 (blob-like). **Untested** beyond the counts printed below."""),
md("## Provenance"),
code("""import hashlib, json, subprocess, datetime
from pathlib import Path
import numpy as np, polars as pl
SEED = 20261019
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
R = ROOT / "experiments/archive/2026-10-c-law-mechanism/results"
names = ["stage1_profile.json", "stage1_k3.json", "stage2_analysis.json", "stage2c_analysis.json", "stage3_analysis.json", "stage4_analysis.json",
         "stage2_decompose.txt", "p1/p1_pairs.csv", "PROVENANCE.md"]
assert all((R / n).exists() for n in names), [n for n in names if not (R / n).exists()]
sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip() or "unresolvable from WSL; see PROVENANCE.md: base f0b96b7, code b7b4758, results 8cc447f"
print("git", sha, "| seed", SEED, "| run", datetime.date.today().isoformat())
for n in names:
    print(hashlib.sha256((R / n).read_bytes()).hexdigest()[:16], n)
J = lambda n: json.loads((R / n).read_text())"""),
md("""## Data and method
Stage 1: per-colour profile of boundary steps from `edgestats_sample.csv` (207 stationary blob rules). Stage 2: tracer on 207 rules, 600 new validation rules, calibration walkers, and a **flat torus band** (256 x 1024, fresh rows 0..511, i.i.d. interior) with an interior ablation. Stage 3: `SparseBgAnt` dose-response, 60 rules x densities. Stage 4: kappa (collider check, growth identity, lead-preserving early flips run with the unchanged `probe 27 8192` pipeline). Heavy computation is in Rust (`examples/c_law_mechanism_trace.rs`, `probe`)."""),
md("## Results\n### 1. c is a local fresh-ground property"),
code("""s2, s2c = J("stage2_analysis.json"), J("stage2c_analysis.json")
print("flat band (i.i.d. interior): 1/c = %.3f + %.3f lead; corr^2 with census c %.4f; median c_band/c_census %.4f" % (s2["S"]["band_intercept"], s2["S"]["band_slope"], s2["S"]["corr2"], s2["S"]["ratio_median"]))
for k, nm in zip("ZYH", ["all-zero", "young colours", "old colours"]):
    v = s2c[k]; print(f"interior {nm:14s}: median |c/c_U - 1| = {v['median_rel']:.4f}, 1/c = {v['intercept']:.3f} + {v['slope']:.3f} lead, kept {v['n']}/60")"""),
md("""A flat front in a random interior reproduces the census c rule by rule to 0.2%, and even an all-colour-0 interior changes it by 0.3%. It does **not** explain the numbers 1.4 and 0.68; it shows they are properties of the rule on fresh ground (not of curvature, holes or the ant-built bulk)."""),
md("### 2. Where the boundary steps go"),
code("""p = J("stage1_profile.json")
for m, v in p["rk_by_lead"].items():
    print(f"lead {m} (n={v['n']:3d}): r_k = " + " ".join(f"{x:.2f}" for x in v["mean"]))
print(); print((R / "stage2_decompose.txt").read_text())
print("lag-4 share of circulating reads: %.3f; killing reads: %.3f; chains q1,q2,q3 = %s; Little median E[N_b]/(1/c) = %.3f" % (s2["L1"]["frac_lag4"], s2["L2"]["frac_lag4"], np.round(s2["C1"]["q"][:3], 3), s2["N1"]["median_ratio"]))"""),
md("""1/c is exactly the number of boundary reads per born cell (Little's law holds to 1.6%); 78% of circulating reads are 4-step returns (2x2 loops); runs of consecutive births never exceed 3. The registered "flat plateau" and "geometric chain" pictures failed. It does **not** derive a or b: the split is descriptive, and the "first reads" bucket in the decomposition also contains returns with lag > 40."""),
md("### 3. Sparse background: the slope is a fresh-ground effect"),
code("""s3 = J("stage3_analysis.json")
print(pl.DataFrame([(float(d), v["a"], v["b"], v["mix_b"]) for d, v in s3["fit"].items() if not d.startswith("secondary")], schema=["density", "a", "b_obs", "b_mixture"], orient="row"))
print("B3' mixture R2 %.3f median rel err %.3f (null no density effect: %.3f / %.3f)" % (s3["B3p"]["r2"], s3["B3p"]["median_rel"], s3["B3p"]["null_d0_r2"], s3["B3p"]["null_d0_median_rel"]))"""),
md("""The lead slope falls monotonically with background density and a parameter-free single-cell mixture tracks it (observed falls slightly faster). The intercept rises, not falls. It does **not** reach d = 1: above d ~ 0.7 the ant leaves the board, so there is no blob regime there and the registered B1 was untestable."""),
md("### 4. Forward models of c"),
code("""k3 = J("stage1_k3.json"); v = s2["V"]
print("census held-out R2(ln c): lead-only %.3f, K3 %.3f, K4 %.3f" % (k3["split"]["lead_only_r2_lnc"], k3["split"]["K3_r2_lnc_B"], s2["K4_census"]["r2_lnc_B"]))
print("fresh 176 R2(c): lead law %.3f, K3 %.3f" % (k3["fresh"]["lead_law_r2_c"], k3["fresh"]["K3_r2_c"]))
print("new validation rules (n=%d) R2(c): lead %.3f, K3 %.3f, K4 %.3f" % (v["n"], v["lead"]["r2"], v["K3"]["r2"], v["K4"]["r2"]))"""),
md("""A 3-parameter survival kernel over the first 12 letters beats the lead law out of sample by 0.04-0.07 in R^2, not by enough to reach the 0.95 of an 8-letter lookup. It does **not** explain why letters 5-8 matter; none of my few-parameter kernels did."""),
md("### 5. Kappa"),
code("""s4 = J("stage4_analysis.json"); a = s4["4a"]
print("176 fresh rules: conditional lead coef %.3f vs no-direct-effect null %.3f %s; with ln c: %.3f %s" % (a["obs_lead"], a["null_lead_mean"], np.round(a["null_lead_ci"], 3), a["with_c"]["lead"], np.round(a["with_c"]["ci"], 3)))
print("growth fit ln A22 = %.2f + %.3f ln c + %.3f ln kappa" % tuple(a["growth_fit"]))
b = s4["4b"]; print("Part B pairs: g=%.3f" % b["g"], {k: (round(x["mean_dA_obs"], 3), round(x["mean_dA_pred"], 3)) for k, x in b["arms"].items()})
c = s4["4c"]; print("lead-preserving flips: %d pairs, mean d %.3f %s, area-adjusted residual %.3f" % (c["n_pairs"], c["mean_d"], np.round(c["ci"], 3), c["resid_mean"]))
pp = pl.read_csv(R / "p1/p1_pairs.csv").with_columns(flip=pl.struct("base", "idx").map_elements(lambda s: s["base"][s["idx"]] + ">" + ("R" if s["base"][s["idx"]] == "L" else "L"), return_dtype=pl.String))
print(pp.group_by("flip").agg(n=pl.len(), mean_d=pl.col("d").mean(), sd_d=pl.col("d").std()))"""),
md("""Conditioning on ln A22 (a function of c and kappa, residual sd 0.09) manufactures the +0.15 "lead effect on kappa"; a null with no direct effect reproduces it and adding ln c removes it. The E/S area asymmetry of the earlier mutants follows from the c law. Lead-preserving flips change kappa by zero on average. It does **not** show that lead has no causal effect on kappa: single flips move kappa by about +/-0.2 with sign set by letter direction (post hoc split), and the S and E arms are confounded with that direction."""),
md("""## Caveats and controls
- Registered failures: D1-D4 (flat plateau), C1 (geometric chains), K3-1, K4 (all), V1, S5, L2, B5; B1 untestable. Deviations: random-walk calibration at 2^20, band window rule, Stage 3 restated cohort, P-4 NaN fix. All in README/NOTEBOOK.
- Timestamps in early NOTEBOOK entries were estimated, not read from the clock; real times and commits are in `results/PROVENANCE.md`. The edgestats sample used K = 23 (recovered).
- Survivor selection limits Stage 3 (d = 0.4) and Stage 4c (retention 0.65).

## What this changes / next steps
The c law is a property of the rule on fresh ground (flat band, interior ablation, sparse background). Open: derive a = 1.4, b = 0.68 (loop-formation probability x 4 steps / births per chain is the lead candidate); why letters 5-8 enter; the S/E direction confound for kappa (needs flips balanced for direction at fixed lead change); the blob regime boundary between d = 0.2 and 0.7."""),
]
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
Path(__file__).resolve().parents[1].joinpath("notebook.ipynb").write_text(nbf.writes(nb))
