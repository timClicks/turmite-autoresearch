# /// script
# dependencies = ["polars"]
# ///
"""Build research-outputs/data-papers/rule-census/rule_census.csv: one row per swept rule (length 2-12,
4083 rules), joining every per-rule measurement the paper's census uses.

Run from the repo root:
  uv run research-outputs/data-papers/rule-census/build_rule_census.py

Deterministic: pure joins of committed result files, no randomness; rows are
sorted by (n, rule). Nothing here is re-measured; see README.md for provenance.

Guards (exit 1 on failure):
  --check        rebuild in memory and fail if the committed CSV / summary JSON
                 differ (the dataset is stale, or was hand-edited)
  --list-inputs  print the repo-relative files the table is built from (used by
                 .githooks/pre-commit to decide when to run --check)
Every build, with or without --check, also asserts that the table agrees with the
census counts and blob median exponent in ../../scholarly-articles/cube-root-growth/numbers.json, so the paper and
the dataset cannot drift apart silently.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CS = ROOT / "experiments/archive/2026-10-census-sweeps/results"
PG = ROOT / "experiments/archive/2026-10-probe-growth-census/results"


def root_of(s: str) -> str:
    """Shortest u with u^k == s (identical dynamics); s itself if primitive."""
    n = len(s)
    for p in range(1, n):
        if n % p == 0 and s[:p] * (n // p) == s:
            return s[:p]
    return s

INPUTS = [
    *(f"experiments/archive/2026-10-census-sweeps/results/{f}" for f in (
        "sweep_v2.csv", "confirmed_v2.csv", "sweep_1B.csv", "sweep_1B_extra.csv",
        "1B_highways.txt", "census.csv")),
    *(f"experiments/archive/2026-10-probe-growth-census/results/{f}" for f in (
        "probe_summary.csv", "c_model.csv")),
    "experiments/archive/2026-10-kappa-uniform-baseline/results/census_spread.txt",  # cross-check only
    "experiments/archive/2026-10-kappa-chiral-edge/results/c_law.json",
]
SPREAD = ROOT / "experiments/archive/2026-10-kappa-uniform-baseline/results/census_spread.txt"
CSV = OUT / "rule_census.csv"
SUMMARY = OUT / "rule_census.build.json"
NUMBERS = ROOT / "research-outputs/scholarly-articles/cube-root-growth/numbers.json"


def build() -> tuple[pl.DataFrame, str, dict]:
    """Return (table, csv text, summary). Pure function of the committed inputs."""
    sweep = pl.read_csv(CS / "sweep_v2.csv").with_columns(
        steps_per_cell=pl.col("steps") / (pl.col("width") * pl.col("height")))
    sweep = sweep.rename({c: f"sweep_{c}" for c in sweep.columns
                          if c not in ("rule", "n", "steps_per_cell")})
    sweep = sweep.rename({"steps_per_cell": "sweep_steps_per_cell"})

    conf = pl.read_csv(CS / "confirmed_v2.csv").drop("n")
    conf = conf.rename({c: f"conf_{c}" for c in conf.columns if c != "rule"})

    # 1e9-step re-run of the rules still unresolved at 1e8 (a subset of rules).
    b1 = pl.concat([pl.read_csv(CS / "sweep_1B.csv"),
                    pl.read_csv(CS / "sweep_1B_extra.csv")], how="diagonal_relaxed").drop("n").unique(maintain_order=True)
    assert b1["rule"].is_unique().all(), "1e9 files disagree on a rule"
    b1 = b1.rename({c: f"run1e9_{c}" for c in b1.columns if c != "rule"})
    b1_hw = set((CS / "1B_highways.txt").read_text().split())

    cen = pl.read_csv(CS / "census.csv").drop("n", "spc")
    cen = cen.rename({"full": "reached_2e27", "alpha": "census_alpha_w",
                      "per_doubling": "census_ext_per_doubling", "ext": "census_ext_2e27",
                      "cls": "phase_census"})

    probe = pl.read_csv(PG / "probe_summary.csv").drop("n", "cls", "alpha")
    probe = probe.rename({"alpha_w": "probe_alpha_w", "alpha_rg": "probe_alpha_rg"})
    probe = probe.rename({c: f"probe_{c}" for c in probe.columns
                          if c not in ("rule",) and not c.startswith("probe_")})

    cmod = pl.read_csv(PG / "c_model.csv").drop("c")
    cmod = cmod.rename({"c_pred": "cmodel_c_pred", "held_out": "cmodel_held_out"})

    d = (sweep.join(conf, on="rule", how="left")
         .join(b1, on="rule", how="left")
         .join(cen, on="rule", how="left")
         .join(probe, on="rule", how="left")
         .join(cmod, on="rule", how="left"))

    d = d.with_columns(
        in_census=pl.col("phase_census").is_not_null(),
        phase=pl.coalesce("phase_census", pl.lit("highway")),
        analysed=pl.col("probe_alpha_w").is_not_null(),
        n_L=pl.col("rule").str.count_matches("L"),
        n_R=pl.col("rule").str.count_matches("R"),
        opening_run=pl.col("rule").map_elements(
            lambda s: len(s) - len(s.lstrip(s[0])), return_dtype=pl.Int64),
        primitive_root=pl.col("rule").map_elements(root_of, return_dtype=pl.String),
        highway_1e9=pl.col("rule").is_in(list(b1_hw)),
    ).with_columns(
        is_repeat=pl.col("primitive_root") != pl.col("rule"),
        # the 7 census rules that escaped the 8192 grid late are kept in the census
        census_late_escape=pl.col("in_census") & (pl.col("sweep_stop") == "escaped"),
    ).drop("phase_census")

    # Per-rule uniform reference (experiments/archive/2026-10-kappa-uniform-baseline): the probe kappa of a walker that is
    # uniform on its territory at every instant, 2 * int_{1/2}^1 x^-e dx with e = a(1 - beta), from this rule's own
    # fitted a and beta. kappa_stationary: |g_k| < 0.05, the cut the baseline note uses (kappa not drifting).
    e = pl.col("probe_a") * (1 - pl.col("probe_beta"))
    d = d.with_columns(
        probe_kappa_unif=2 * (1 - 0.5 ** (1 - e)) / (1 - e),
        kappa_stationary=pl.col("probe_g_k").abs() < 0.05,
    ).with_columns(probe_kappa_ratio=pl.col("probe_kappa") / pl.col("probe_kappa_unif"))

    law = json.loads((ROOT / INPUTS[-1]).read_text())["C1"]
    d = d.with_columns(c_lead_pred=1 / (law["a"] + law["b"] * pl.col("opening_run").clip(upper_bound=8)))

    front = ["rule", "n", "n_L", "n_R", "primitive_root", "is_repeat", "phase", "in_census",
             "census_late_escape", "analysed"]
    d = d.select(front + [c for c in d.columns if c not in front]).sort("n", "rule")
    assert d["rule"].is_unique().all() and d.height == 4083
    text = d.write_csv(float_precision=10)
    summary = {
        "rows": d.height, "columns": d.width,
        "phase_counts": {r["phase"]: r["len"] for r in d.group_by("phase").len().iter_rows(named=True)},
        "in_census": int(d["in_census"].sum()), "analysed": int(d["analysed"].sum()),
        "blob_median_probe_alpha_w": round(float(
            d.filter(pl.col("phase") == "blob", pl.col("analysed"))["probe_alpha_w"].median()), 6),
    }
    st = d.filter(pl.col("phase") == "blob", pl.col("kappa_stationary"))["probe_kappa_ratio"]
    summary["kappa_ratio_stationary_blob"] = {
        "n": st.len(), "q05": round(float(st.quantile(0.05, "linear")), 3), "q25": round(float(st.quantile(0.25, "linear")), 3),
        "median": round(float(st.median()), 3), "q75": round(float(st.quantile(0.75, "linear")), 3),
        "q95": round(float(st.quantile(0.95, "linear")), 3)}
    return d, text, summary


def paper_mismatches(summary: dict) -> list[str]:
    """Compare against the numbers the manuscript prints (numbers.json)."""
    if not NUMBERS.exists():
        return [f"{NUMBERS.relative_to(ROOT)} missing; cannot cross-check the paper"]
    n = json.loads(NUMBERS.read_text(encoding="utf-8"))
    pc = summary["phase_counts"]
    want = {
        "census rules": (summary["in_census"], n["census"]["rules"]),
        "builders": (pc["builder"], n["census"]["builders"]),
        "log rules": (pc["log"], n["census"]["log"]),
        "blob rules": (pc["blob"], n["census"]["blob"]),
        "analysed rules": (summary["analysed"], n["probe"]["analysed"]),
        "blob median alpha_w": (summary["blob_median_probe_alpha_w"], round(n["alpha_w_blob"][0], 6)),
    }
    bad = [f"{k}: dataset {a} != numbers.json {b}" for k, (a, b) in want.items() if a != b]
    # the per-rule kappa ratio must reproduce the published census_spread line
    line = next((l for l in SPREAD.read_text().splitlines() if l.startswith("kappa/kappa_unif, stationary")), "")
    m = re.search(r"n=(\d+) q05/25/50/75/95=\[([^\]]+)\]", line)
    k = summary["kappa_ratio_stationary_blob"]
    got = [k["n"], k["q05"], k["q25"], k["median"], k["q75"], k["q95"]]
    ref = [int(m.group(1))] + [float(x) for x in m.group(2).split(",")] if m else None
    if ref != got:
        bad.append(f"kappa ratio quantiles: dataset {got} != census_spread.txt {ref}")
    return bad
def same_text(path: Path, text: str) -> bool:
    # git on Windows may check files out with CRLF; the content is what matters
    return path.exists() and path.read_text(encoding="utf-8").replace("\r\n", "\n") == text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="fail if committed files are stale")
    ap.add_argument("--list-inputs", action="store_true")
    args = ap.parse_args()
    me = Path(__file__).resolve().relative_to(ROOT).as_posix()
    if args.list_inputs:
        print("\n".join(INPUTS + [me]))
        return 0

    _, text, summary = build()
    summary_text = json.dumps(summary, indent=1, sort_keys=True) + "\n"
    problems = paper_mismatches(summary)
    if args.check:
        for path, new in ((CSV, text), (SUMMARY, summary_text)):
            if not same_text(path, new):
                problems.append(f"{path.relative_to(ROOT).as_posix()} is stale (differs from a fresh rebuild)")
        if problems:
            print("rule_census check FAILED:\n  " + "\n  ".join(problems), file=sys.stderr)
            print(f"Fix: uv run {me}  and commit the regenerated files "
                  "(or fix numbers.json / the inputs).", file=sys.stderr)
            return 1
        print("rule_census check ok:", json.dumps(summary, sort_keys=True))
        return 0

    if problems:
        print("rule_census does NOT agree with the paper (nothing written):\n  "
              + "\n  ".join(problems), file=sys.stderr)
        return 1
    CSV.write_text(text, encoding="utf-8", newline="\n")
    SUMMARY.write_text(summary_text, encoding="utf-8", newline="\n")
    print(summary_text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
