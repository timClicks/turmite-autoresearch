"""Score the leak titration exactly as registered in the README (gates G1-G5, predictions P1-P5).

usage (repo root): uv run --frozen python experiments/active/2026-10-leak-titration/scripts/analyse.py [RESULTS_DIR]
Reads RESULTS_DIR/probe.csv (default: the committed results/), results/specs.txt, results/spec_roles.csv and the
committed wall-vs-memory results (gates). Writes runs.csv, curves.csv, analysis.txt and fig_curves.png into RESULTS_DIR.
`fit`, `classify`, `stalled` and `filler` are copied unchanged from wall-vs-memory/scripts/analyse_stage3c.py.
All cut-offs below are the registered ones; nothing here is tuned on the data.
"""
import sys
from pathlib import Path

import numpy as np
import polars as pl

EXP = Path(__file__).resolve().parents[1]
WVM = EXP.parent / "2026-10-wall-vs-memory" / "results"
RES = Path(sys.argv[1]) if len(sys.argv) > 1 else EXP / "results"
WINDOWS = {"early": (12, 22), "late": (20, 26)}
K_ENDS = (16, 18, 20, 22)
GRID = [round(0.1 * i, 1) for i in range(11)]
SHARP, SMOOTH = 0.40, 0.28       # on M = median S_r (calibration_sharpness.txt)
MIN_DELTA, MIN_SEEDS = 0.10, 6


def fit(g: pl.DataFrame, lo: int, hi: int) -> dict | None:
    w = g.filter((pl.col("k") >= lo) & (pl.col("k") <= hi))
    if w.height < hi - lo + 1:
        return None
    t = w["t"].to_numpy().astype(float)
    A = w["area"].to_numpy().astype(float)
    P = w["perimeter"].to_numpy().astype(float)
    return dict(a=np.polyfit(np.log(t), np.log(A), 1)[0], beta=np.polyfit(np.log(A), np.log(P), 1)[0])


def classify(c: dict) -> str:
    a, b = c.get("early_a"), c.get("early_beta")
    if a is None or np.isnan(a):
        return "no early fit"
    if a <= 0.78 and b <= 0.65:
        if c["late_n"] >= 6 and not c["late_a"] <= 0.74:
            return "intermediate"
        return "compact"
    if a >= 0.85 and b >= 0.80:
        return "porous"
    return "intermediate"


def stalled(g: pl.DataFrame, early_a: float) -> bool:
    areas = g.sort("k")["area"].to_list()
    return (not np.isnan(early_a) and early_a < 0.45) or (len(areas) >= 2 and areas[-1] == areas[-2])


def filler(g: pl.DataFrame, early_a: float, early_beta: float) -> bool:
    last = g.sort("k").tail(3)
    at = (last["area"] / last["t"]).to_numpy()
    return early_a >= 0.90 and early_beta <= 0.62 and len(at) == 3 and bool(np.all(np.abs(at / at.mean() - 1) <= 0.03))


out: list[str] = []


def P(s: str = "") -> None:
    out.append(s)
    print(s)


def rule_of(spec: str) -> str:
    return spec.split(":")[1]


df = pl.read_csv(RES / "probe.csv")
roles = pl.read_csv(EXP / "results" / "spec_roles.csv")
specs = (EXP / "results" / "specs.txt").read_text().split()
rules = sorted((WVM / "rules.txt").read_text().split())
P(f"# leak titration scoring; {len(specs)} registered specs, {df['rule'].n_unique()} present in probe.csv")
assert set(df["rule"].unique().to_list()) == set(specs), "probe.csv does not hold exactly the registered specs"

# ---- per-run fits and classes --------------------------------------------------------------
rows = []
for spec in specs:
    g = df.filter(pl.col("rule") == spec).sort("k")
    e, l = fit(g, *WINDOWS["early"]), fit(g, *WINDOWS["late"])
    ea, eb = (e["a"], e["beta"]) if e else (np.nan, np.nan)
    c = dict(early_a=ea, early_beta=eb, late_a=l["a"] if l else np.nan, late_n=1 if l else 0)
    if e is None and bool(g["escaped"].any()):
        cls = "escape"
    elif stalled(g, ea):
        cls = "stalled"
    elif e is not None and filler(g, ea, eb):
        cls = "filler"
    else:
        cls = classify(c)
    drift = {f"a_k{ke}": (fit(g, 12, ke) or {"a": np.nan})["a"] for ke in K_ENDS}
    rows.append(dict(spec=spec, rule=rule_of(spec), early_a=ea, early_beta=eb, late_a=c["late_a"], cls=cls, **drift))
runs = pl.DataFrame(rows).join(roles, on="spec").with_columns(pl.col("ef").cast(pl.Float64))
runs.sort("arm", "rule", "ef", "spec").write_csv(RES / "runs.csv", float_precision=6)

# ---- gates -----------------------------------------------------------------------------------
P()
gates = {}
s1 = pl.read_csv(WVM / "probe.csv")
g1 = [df.filter(pl.col("rule") == s).sort("k").equals(s1.filter(pl.col("rule") == s).sort("k")) and s1.filter(pl.col("rule") == s).height > 0
      for s in roles.filter(pl.col("role") == "gate_hy")["spec"].to_list()]
gates["G1"] = all(g1)
P(f"G1 gate_hy rows (EF = 0, 0.1, 1) identical to wall-vs-memory Stage 1 probe.csv: {sum(g1)}/{len(g1)} -> {'PASS' if gates['G1'] else 'FAIL'}")
s3 = pl.read_csv(WVM / "stage3_probe.csv")
g2 = [df.filter(pl.col("rule") == s).sort("k").equals(s3.filter(pl.col("rule") == s).sort("k")) and s3.filter(pl.col("rule") == s).height > 0
      for s in roles.filter(pl.col("role") == "gate_ft")["spec"].to_list()]
gates["G2"] = all(g2)
P(f"G2 ft:RULE:L rows identical to wall-vs-memory Stage 3: {sum(g2)}/{len(g2)} -> {'PASS' if gates['G2'] else 'FAIL'}")


def abar(arm: str, ef: float, rule: str, col: str = "early_a") -> tuple[float, int]:
    v = runs.filter((pl.col("arm") == arm) & (pl.col("ef") == ef) & (pl.col("rule") == rule))[col].drop_nans().to_numpy()
    return (float(v.mean()) if len(v) else np.nan, len(v))


def law_gate(arm_x: str, arm_y: str, efs: tuple[float, ...]) -> tuple[bool, list[float]]:
    d = [abar(arm_x, ef, r)[0] - abar(arm_y, ef, r)[0] for ef in efs for r in rules]
    d = np.array(d)
    return bool(abs(np.nanmean(d)) <= 0.02 and np.all(np.abs(d) <= 0.04)), list(d)


ok3, d3 = law_gate("Rfs", "R", (0.5, 0.8))
gates["G3"] = ok3
P(f"G3 base R through fs: vs hy: at EF 0.5, 0.8: mean d {np.nanmean(d3):+.4f} (<= 0.02), max |d| {np.nanmax(np.abs(d3)):.4f} (<= 0.04) -> {'PASS' if ok3 else 'FAIL'}")
ok4, d4 = law_gate("L", "R", (1.0,))
gates["G4"] = ok4
P(f"G4 arm L vs arm R at EF = 1: mean d {np.nanmean(d4):+.4f}, max |d| {np.nanmax(np.abs(d4)):.4f} -> {'PASS' if ok4 else 'FAIL'}")

s1runs = pl.read_csv(WVM / "runs.csv")
s1cond = pl.read_csv(WVM / "conditions.csv")
bad = []
for r in runs.filter(pl.col("role") == "gate_hy").iter_rows(named=True):
    ref = s1runs.filter(pl.col("spec") == r["spec"])
    if ref.height != 1 or abs(ref["early_a"][0] - r["early_a"]) > 5e-4 or abs(ref["early_beta"][0] - r["early_beta"]) > 5e-4:
        bad.append(r["spec"])
cond_bad = []
for ef_s, ef in (("0", 0.0), ("1", 1.0)):
    for rule in rules:
        sub = runs.filter((pl.col("arm") == "R") & (pl.col("ef") == ef) & (pl.col("rule") == rule))
        late = sub["late_a"].drop_nans()
        c = dict(early_a=float(sub["early_a"].drop_nans().mean()), early_beta=float(sub["early_beta"].drop_nans().mean()),
                 late_a=float(late.mean()) if late.len() else np.nan, late_n=late.len())
        ref = s1cond.filter(pl.col("group") == f"hy:{rule}:0:{ef_s}")["class"].to_list()
        if not ref or classify(c) != ref[0]:
            cond_bad.append((rule, ef_s, classify(c), ref))
gates["G5"] = not bad and not cond_bad
P(f"G5 classifier: per-run early a/beta equal Stage 1 runs.csv (tol 5e-4): {102 - len(bad)}/102; EF 0 and 1 condition classes equal "
  f"Stage 1 conditions.csv: {12 - len(cond_bad)}/12 -> {'PASS' if gates['G5'] else 'FAIL'}")
if cond_bad:
    P(f"   class mismatches: {cond_bad}")

# ---- curves --------------------------------------------------------------------------------------
curve_rows = []
curve = {}
for arm in ("R", "L"):
    for rule in rules:
        for ke in (None,) + K_ENDS:
            col = "early_a" if ke is None else f"a_k{ke}"
            ab, ns = zip(*[abar(arm, ef, rule, col) for ef in GRID])
            curve[(arm, rule, ke)] = (np.array(ab), np.array(ns))
        ab, ns = curve[(arm, rule, None)]
        for ef, a_, n_ in zip(GRID, ab, ns):
            curve_rows.append(dict(arm=arm, rule=rule, ef=ef, abar=a_, n=n_))
pl.DataFrame(curve_rows).write_csv(RES / "curves.csv", float_precision=6)


def scoreable(arm: str, rule: str) -> tuple[bool, str]:
    ab, ns = curve[(arm, rule, None)]
    c0 = runs.filter((pl.col("arm") == arm) & (pl.col("ef") == 0.0) & (pl.col("rule") == rule))["cls"].to_list()
    if not c0 or c0[0] != "compact":
        return False, f"EF = 0 run is {c0[0] if c0 else 'missing'}"
    if np.any(ns[1:] < MIN_SEEDS):
        return False, f"fewer than {MIN_SEEDS} early fits at EF {[g for g, n in zip(GRID, ns) if n < MIN_SEEDS and g > 0]}"
    if ab[-1] - ab[0] < MIN_DELTA:
        return False, f"rise {ab[-1] - ab[0]:.3f} < {MIN_DELTA}"
    return True, ""


def shape(ab: np.ndarray) -> dict:
    d = ab[-1] - ab[0]
    steps = np.diff(ab)
    ef50 = next((g for g, v in zip(GRID, ab) if v >= ab[0] + 0.5 * d), np.nan)
    i = int(np.argmax(steps))
    return dict(delta=d, S=steps[i] / d, ef_step=GRID[i], ef50=ef50, min_step=float(steps.min()))


P()
P("curve statistics (S = share of the total rise in the steepest 0.1 step; EF_50 = first grid EF at half the rise)")
res = {}
for arm in ("R", "L"):
    P(f"-- arm {arm}")
    P(f"   {'rule':<14}{'scoreable':<10}{'Delta':>7}{'S':>7}{'EF_step':>9}{'EF_50':>7}{'min step':>10}   early a at EF = " + " ".join(f"{g:.1f}" for g in GRID))
    for rule in rules:
        ok, why = scoreable(arm, rule)
        ab, ns = curve[(arm, rule, None)]
        sh = shape(ab) if np.all(~np.isnan(ab)) else dict(delta=np.nan, S=np.nan, ef_step=np.nan, ef50=np.nan, min_step=np.nan)
        res[(arm, rule)] = (ok, sh)
        tag = "yes" if ok else "NO"
        P(f"   {rule:<14}{tag:<10}{sh['delta']:>7.3f}{sh['S']:>7.3f}{sh['ef_step']:>9.1f}{sh['ef50']:>7.1f}{sh['min_step']:>+10.3f}   "
          + " ".join(f"{v:.3f}" for v in ab) + (f"   [{why}]" if not ok else ""))


def reading(arm: str) -> tuple[str, float, list[float]]:
    sc = [res[(arm, r)][1] for r in rules if res[(arm, r)][0]]
    if len(sc) < 3:
        return "not scored (fewer than 3 scoreable rules)", np.nan, []
    M = float(np.median([s["S"] for s in sc]))
    steps = [s["ef_step"] for s in sc]
    if M >= SHARP:
        word = "H-endpoint" if np.median(steps) >= 0.9 else "H-sharp"
    elif M <= SMOOTH:
        word = "H-smooth"
    else:
        word = "unresolved"
    return word, M, steps


P()
fail_early = not (gates["G1"] and gates["G2"])
for arm in ("R", "L"):
    word, M, steps = reading(arm)
    n_sc = sum(res[(arm, r)][0] for r in rules)
    P(f"P1 arm {arm}: {n_sc} scoreable rules, M = median S = {M:.3f}, EF_step per rule {steps} -> {word}"
      + ("   [NOT SCORED: G1/G2 failed]" if fail_early else ""))
wordR, MR, _ = reading("R")

sc_r = [r for r in rules if res[("R", r)][0]]
ef50 = [res[("R", r)][1]["ef50"] for r in sc_r]
med50 = float(np.nanmedian(ef50)) if ef50 else np.nan
P(f"P2 median EF_50 (arm R) = {med50:.2f} (registered [0.3, 0.7]) -> {'HELD' if 0.3 <= med50 <= 0.7 else 'FAILED'}")
n_mono = sum(res[("R", r)][1]["min_step"] >= -0.015 for r in rules if not np.isnan(res[("R", r)][1]["min_step"]))
P(f"P3 monotone within 0.015 in {n_mono}/6 rules (registered >= 5) -> {'HELD' if n_mono >= 5 else 'FAILED'}")

both = [r for r in rules if res[("R", r)][0] and res[("L", r)][0]]
wordL, ML, _ = reading("L")
if len(both) < 3 or not (gates["G3"] and gates["G4"]):
    P(f"P4 not scored ({len(both)} rules scoreable in both arms; G3 {gates['G3']}, G4 {gates['G4']})")
else:
    close = [r for r in both if abs(res[("L", r)][1]["ef50"] - res[("R", r)][1]["ef50"]) <= 0.1 + 1e-9]
    ok = len(close) >= 2 / 3 * len(both) and wordL == wordR
    P(f"P4 handedness: EF_50 within 0.1 in {len(close)}/{len(both)} rules (need >= 2/3), readings L={wordL}, R={wordR} -> {'HELD' if ok else 'FAILED'}")

D = []
P("P5 window drift (arm R): EF_50 from fits over k = 12..k_end")
for rule in sc_r:
    e50 = []
    for ke in K_ENDS:
        ab, _ = curve[("R", rule, ke)]
        d = ab[-1] - ab[0]
        e50.append(next((g for g, v in zip(GRID, ab) if v >= ab[0] + 0.5 * d), np.nan) if d >= MIN_DELTA else np.nan)
    D.append(e50[-1] - e50[0])
    P(f"   {rule:<14} EF_50 at k_end {K_ENDS}: {e50}   D = {D[-1]:+.2f}")
medD = float(np.nanmedian(np.abs(D))) if D else np.nan
P(f"P5 median |D| = {medD:.2f} -> " + ("no detectable drift" if medD <= 0.1 else "drift" if medD >= 0.2 else "unresolved"))

# ---- descriptives ------------------------------------------------------------------------------------
P()
P("descriptive (not scored): classes pooled over rules and seeds; escape rate")
for arm in ("R", "L"):
    P(f"-- arm {arm}: EF: compact/intermediate/porous/escape/other of the runs; between-seed sd of early a averaged over rules")
    for ef in GRID:
        sub = runs.filter((pl.col("arm") == arm) & (pl.col("ef") == ef))
        cnt = dict(sub.group_by("cls").len().iter_rows())
        sd = np.nanmean([runs.filter((pl.col("arm") == arm) & (pl.col("ef") == ef) & (pl.col("rule") == r))["early_a"].drop_nans().std() for r in rules]) if ef > 0 else np.nan
        other = sum(v for k, v in cnt.items() if k not in ("compact", "intermediate", "porous", "escape"))
        P(f"   EF {ef:.1f}: {cnt.get('compact', 0)}/{cnt.get('intermediate', 0)}/{cnt.get('porous', 0)}/{cnt.get('escape', 0)}/{other}   sd {sd:.3f}")
coex = []
for arm in ("R", "L"):
    for rule in rules:
        for ef in GRID[1:]:
            sub = runs.filter((pl.col("arm") == arm) & (pl.col("ef") == ef) & (pl.col("rule") == rule))["cls"].to_list()
            if sub.count("compact") >= 2 and sub.count("porous") >= 2:
                coex.append((arm, rule, ef))
P(f"coexistence cells (>= 2 compact and >= 2 porous of 8 at one rule and EF): {len(coex)}: {coex}")

(RES / "analysis.txt").write_text("\n".join(out) + "\n")

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, arm in zip(axes, ("R", "L")):
        for rule in rules:
            ab, _ = curve[(arm, rule, None)]
            ax.plot(GRID, ab, marker="o", ms=3, lw=1, label=rule)
        ax.axhline(0.78, color="grey", ls=":", lw=0.8)
        ax.axhline(0.85, color="grey", ls="--", lw=0.8)
        ax.set_title(f"arm {arm}: base fresh turn {arm}, leak EF")
        ax.set_xlabel("EF (leak probability per fresh step)")
    axes[0].set_ylabel("early area exponent a (k = 12..22)")
    axes[1].legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(RES / "fig_curves.png", dpi=130)
except Exception as exc:  # figure is a convenience only
    print("figure skipped:", exc)
