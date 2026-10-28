"""Shared helpers for the kappa-rule-space experiment (read-only use of the pre-restructure data, now in experiments/*/*/results/)."""
import subprocess, sys
from pathlib import Path
import numpy as np, polars as pl

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
SEED = 20261014
sys.path.insert(0, str(ROOT / "experiments" / "_lib"))
from analyse_probe import per_rule  # noqa: E402


def legacy(name):
    """Path of a pre-restructure data/ file, which now lives in some experiments/<exp>/results/ (not in this experiment)."""
    hits = [p for p in sorted(ROOT.glob(f"experiments/*/*/results/{name}")) if EXP not in p.parents]
    if len(hits) != 1:
        raise FileNotFoundError(f"{name}: expected exactly one match under experiments/*/*/results, got {hits}")
    return hits[0]


def header(cmd: str) -> str:
    """Recipe line for every results file (AGENTS.md: record command, commit, seed)."""
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    return f"# cmd: {cmd}\n# git: {sha} (working tree may be dirty)  seed: {SEED}\n"


def rng(offset=0):
    return np.random.default_rng(SEED + offset)


def pool_runs(files):
    """Per-run table (core band, kappa>0) with base rule, kappa, c, g_k, alpha_w, ln A(22)."""
    out = []
    for f in files:
        raw = pl.read_csv(legacy(f))
        r = per_rule(raw).with_columns(base=pl.col("rule").str.split("@").list.first(), src=pl.lit(f))
        a22 = raw.filter(pl.col("k") == 22).select("rule", lnA22=pl.col("area").log())
        out.append(r.join(a22, on="rule", how="left"))
    r = pl.concat(out)
    return r.filter(pl.col("alpha_w").is_between(0.25, 0.42) & (pl.col("kappa") > 0))


def rule_means(runs, min_runs=6):
    return runs.group_by("base").agg(
        n_runs=pl.len(), lnk=pl.col("kappa").log().mean(), lnk_sd=pl.col("kappa").log().std(),
        c=pl.col("c").mean(), g_k=pl.col("g_k").median(), lnA22=pl.col("lnA22").mean(),
        kappa=pl.col("kappa").mean(),
    ).filter(pl.col("n_runs") >= min_runs).sort("base")


def icc_groups(groups):
    groups = [g for g in groups if len(g) >= 6]
    sw = np.sqrt(np.mean([g.var(ddof=1) for g in groups]))
    means = np.array([g.mean() for g in groups]); m = np.mean([len(g) for g in groups])
    sb2 = max(means.var(ddof=1) - sw ** 2 / m, 0.0)
    return sb2 / (sb2 + sw ** 2), sw, np.sqrt(sb2), len(groups)


def onehot(s):
    v = np.zeros(26)
    for i, ch in enumerate(s[:12]):
        v[2 * i + (ch == "R")] = 1
    v[24] = len(s); v[25] = s.count("R") / len(s)
    return v


def loo_ridge_r2(X, y, lam=10.0):
    X = (X - X.mean(0)) / (X.std(0) + 1e-9); N = len(y); pred = np.zeros(N)
    for i in range(N):
        tr = np.arange(N) != i; A = X[tr]
        b = np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ (y[tr] - y[tr].mean()))
        pred[i] = X[i] @ b + y[tr].mean()
    return 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def canon(rule: str) -> str:
    """Mirror-canonical form (census keeps rules starting with R)."""
    return rule if rule[0] == "R" else rule.translate(str.maketrans("LR", "RL"))


def census(nonbursty=True):
    df = pl.read_csv(legacy("probe_summary.csv")).filter(pl.col("cls") == "blob")
    if nonbursty:
        df = df.filter(~pl.col("bursty"))
    raw = pl.read_csv(legacy("probe_all.csv"), columns=["rule", "k", "area"]).filter(pl.col("k") == 22)
    return df.join(raw.select("rule", lnA22=pl.col("area").log()), on="rule", how="left")
