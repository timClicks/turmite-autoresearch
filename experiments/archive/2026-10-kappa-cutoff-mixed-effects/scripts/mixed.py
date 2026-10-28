"""Random-intercept REML and the split-seed pipeline for kappa-cutoff-mixed-effects (see ../README.md).

Library only (imported by calibrate.py and fit.py). No statsmodels: the model is
    y_gi = X_gi b + u_g + e_gi,  u_g ~ N(0, s_u^2), e ~ N(0, s_e^2)
fitted by REML with a 1-D profile over lambda = s_u^2/s_e^2 and closed-form GLS for b.
Data layout: DATA = list of rules; rule = {"name": str, "k": {k: {"seed": int[], "lnA": float[], "lk": float[], "q": float[]}}}
(q = ln_ratio). A split is {rule_index: set(seed ids in covariate half X)}; Y = the other seeds of that rule.
"""
import numpy as np
from scipy.optimize import minimize_scalar


def reml(y, X, g):
    """y (N,), X (N,p), g (N,) integer group ids (contiguous not required). Returns dict(b, cov, su2, se2, lam)."""
    order = np.argsort(g, kind="stable")
    y, X, g = y[order], X[order], g[order]
    starts = np.r_[0, np.flatnonzero(np.diff(g)) + 1]
    n = np.diff(np.r_[starts, len(y)]).astype(float)
    a = np.add.reduceat(X, starts, axis=0)
    Sxx = np.add.reduceat(X[:, :, None] * X[:, None, :], starts, axis=0)
    Sxy = np.add.reduceat(X * y[:, None], starts, axis=0)
    s1 = np.add.reduceat(y, starts)
    syy = np.add.reduceat(y * y, starts)
    N, p = X.shape

    def parts(lam):
        c = lam / (1.0 + n * lam)
        XtVX = Sxx.sum(0) - np.einsum("g,gi,gj->ij", c, a, a)
        XtVy = Sxy.sum(0) - np.einsum("g,gi,g->i", c, a, s1)
        yVy = syy.sum() - np.sum(c * s1 * s1)
        b = np.linalg.solve(XtVX, XtVy)
        rss = yVy - b @ XtVy
        return XtVX, b, max(rss, 1e-300)

    def crit(loglam):
        lam = np.exp(loglam)
        XtVX, b, rss = parts(lam)
        s2 = rss / (N - p)
        return (N - p) * np.log(s2) + np.sum(np.log1p(n * lam)) + np.linalg.slogdet(XtVX)[1]

    r = minimize_scalar(crit, bounds=(-12.0, 6.0), method="bounded", options={"xatol": 1e-4})
    lam = float(np.exp(r.x))
    XtVX, b, rss = parts(lam)
    s2 = rss / (N - p)
    return dict(b=b, cov=s2 * np.linalg.inv(XtVX), su2=lam * s2, se2=s2, lam=lam)


# ---------- split-seed pipeline ----------

def _half_means(rule, k, sel):
    d = rule["k"][k]
    m = np.isin(d["seed"], list(sel)) if sel is not None else np.ones(len(d["seed"]), bool)
    return d["lnA"][m].mean(), d["lk"][m].mean()


def covariates(rules, split, k, which):
    """Rule-level (A, K) from half `which` in {"X","Y"} of the split."""
    A, K = [], []
    for i, rule in enumerate(rules):
        d = rule["k"][k]
        inx = np.isin(d["seed"], list(split[i]))
        m = inx if which == "X" else ~inx
        A.append(d["lnA"][m].mean())
        K.append(d["lk"][m].mean())
    return np.array(A), np.array(K)


def make_tf(A, K):
    b, a = np.polyfit(A, K, 1)
    r = K - (a + b * A)
    return dict(a=a, b=b, mA=A.mean(), sA=A.std(ddof=1), mr=r.mean(), sr=r.std(ddof=1))


def apply_tf(tf, A, K):
    r = K - (tf["a"] + tf["b"] * A)
    return (A - tf["mA"]) / tf["sA"], (r - tf["mr"]) / tf["sr"]


def response_rows(rules, split, k, which):
    """Return (rule_idx, q) rows of the response half."""
    gi, q = [], []
    for i, rule in enumerate(rules):
        d = rule["k"][k]
        inx = np.isin(d["seed"], list(split[i]))
        m = ~inx if which == "Y" else inx
        gi.extend([i] * int(m.sum()))
        q.extend(d["q"][m].tolist())
    return np.array(gi), np.array(q)


def design(zA, zr, gi, kind, with_r=True):
    cols = [np.ones(len(gi)), zA[gi]]
    if with_r:
        cols.append(zr[gi])
    return np.column_stack(cols)


def fit_direction(rules, split, k, direction="A", with_r=True):
    """Fit on covariates from one half, responses from the other. direction A: cov=X,resp=Y; B: cov=Y,resp=X."""
    cov_half, resp_half = ("X", "Y") if direction == "A" else ("Y", "X")
    A, K = covariates(rules, split, k, cov_half)
    tf = make_tf(A, K)
    zA, zr = apply_tf(tf, A, K)
    gi, q = response_rows(rules, split, k, resp_half)
    fit = reml(q, design(zA, zr, gi, k, with_r), gi)
    # rule-mean response sd for the standardised effect
    ym = np.array([q[gi == i].mean() for i in np.unique(gi)])
    fit["ysd"] = ym.std(ddof=1)
    fit["tf"] = tf
    fit["resp_half"] = resp_half
    fit["cov_half"] = cov_half
    return fit


def r2_oos(rules, split, k, fit, with_r, direction="A"):
    """Frozen-transform evaluation on the other seed halves (covariates from the old response half, response = old covariate half)."""
    cov_half, resp_half = ("Y", "X") if direction == "A" else ("X", "Y")
    A, K = covariates(rules, split, k, cov_half)
    zA, zr = apply_tf(fit["tf"], A, K)
    gi, q = response_rows(rules, split, k, resp_half)
    ym = np.array([q[gi == i].mean() for i in range(len(rules))])
    X = np.column_stack([np.ones(len(rules)), zA] + ([zr] if with_r else []))
    yhat = X @ fit["b"]
    return 1.0 - np.sum((ym - yhat) ** 2) / np.sum((ym - ym.mean()) ** 2)


def pooled_fit(rules, split, ks, direction="A"):
    cov_half, resp_half = ("X", "Y") if direction == "A" else ("Y", "X")
    rows_g, rows_q, rows_X = [], [], []
    ysd = []
    for j, k in enumerate(ks):
        A, K = covariates(rules, split, k, cov_half)
        zA, zr = apply_tf(make_tf(A, K), A, K)
        gi, q = response_rows(rules, split, k, resp_half)
        ind = np.full(len(gi), float(j))
        rows_X.append(np.column_stack([np.ones(len(gi)), ind, zA[gi], zr[gi]]))
        rows_g.append(gi)
        rows_q.append(q)
        ysd.append(q.std(ddof=1))
    q = np.concatenate(rows_q)
    fit = reml(q, np.vstack(rows_X), np.concatenate(rows_g))
    # rule-mean ln_ratio sd after removing the k offset, over rules
    fit["ysd"] = float(np.mean([np.std([qq[gg == i].mean() for i in np.unique(gg)], ddof=1) for qq, gg in zip(rows_q, rows_g)]))
    return fit


def random_split(rules, rng):
    """Balanced random split: for each rule, floor(n/2) of the seeds (union across k) go to X."""
    split = {}
    for i, rule in enumerate(rules):
        seeds = np.unique(np.concatenate([rule["k"][k]["seed"] for k in rule["k"]]))
        perm = rng.permutation(seeds)
        split[i] = set(perm[: len(seeds) // 2].tolist())
    return split


def parity_split(rules):
    return {i: {int(s) for k in r["k"] for s in r["k"][k]["seed"] if s % 2 == 0} for i, r in enumerate(rules)}


def resample_rules(rules, rng):
    return [rules[j] for j in rng.integers(0, len(rules), len(rules))]


def boot_br(rules, k, rng, B, direction="A", with_oos=False):
    """Rule-cluster bootstrap, fresh random split per replicate. Returns arrays of br, Std (and dR2)."""
    br, std, d2 = [], [], []
    for _ in range(B):
        rs = resample_rules(rules, rng)
        sp = random_split(rs, rng)
        f1 = fit_direction(rs, sp, k, direction, True)
        br.append(f1["b"][2])
        std.append(f1["b"][2] / f1["ysd"])
        if with_oos:
            f0 = fit_direction(rs, sp, k, direction, False)
            d2.append(r2_oos(rs, sp, k, f1, True, direction) - r2_oos(rs, sp, k, f0, False, direction))
    return np.array(br), np.array(std), np.array(d2)
