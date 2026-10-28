# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "scipy", "polars"]
# ///
"""Segment-state chain estimator for the kappa first-passage experiment.

Input is the pair table written by examples/kappa_first_passage_sampler.rs (or the synthetic
generator in calibrate.py): one row per (band, start state, next state | open) with counts n and
summed elapsed time. States are nested: M0 = (m, dir); M1 adds (heading, phase); M2 adds
(patch, hist). Frozen choices (README "Calibration registration"): a state backs off one level
(down to M0) when it was observed as a source fewer than `floor` times; milestone 0 absorbs.
"""
from __future__ import annotations

import numpy as np
import polars as pl
import scipy.sparse as sp
import scipy.sparse.linalg as spla

KEYS = ["m", "dir", "heading", "phase", "patch", "hist"]
NEXT = ["nm", "ndir", "nheading", "nphase", "npatch", "nhist"]
DEEP = 7  # milestone index of depth 64


def codes(df: pl.DataFrame, cols: list[str]) -> dict[int, pl.Expr]:
    m, d, h, p, pa, hi = (pl.col(c).cast(pl.UInt64) for c in cols)
    c0 = m + d * 8
    c1 = c0 + h * 32 + p * 128
    c2 = c1 + pa * 512 + hi * 33554432
    return {0: c0, 1: c1, 2: c2}


def read_pairs(files: list[str]) -> pl.DataFrame:
    frames = [pl.read_csv(f, null_values="NA") for f in files]
    return pl.concat(frames)


DIRECT_MAX = 50_000  # above this many states the sparse direct solve fills in badly (the pooled P3 chains did not finish in 2.5 h)


def _solve(A, b):
    """Solve A x = b for the (I - Q) systems: sparse direct for small chains, BiCGSTAB (checked) for large ones."""
    if A.shape[0] <= DIRECT_MAX:
        return spla.spsolve(A, b)
    x, info = spla.bicgstab(A, b, rtol=1e-11, atol=0.0, maxiter=20000)
    if info != 0 or not np.isfinite(x).all():
        raise RuntimeError(f"iterative solve did not converge (info={info})")
    resid = np.linalg.norm(A @ x - b) / max(np.linalg.norm(b), 1e-300)
    if resid > 1e-8:
        raise RuntimeError(f"iterative solve residual {resid:.2e}")
    return x


def fit(df: pl.DataFrame, level: int = 0, floor: int = 20, bands: list[int] | None = None, max_dead: float = 0.01, entry_df: pl.DataFrame | None = None) -> dict:
    """Fit the chain on `df` (all rows used; filter bands beforehand or via `bands`)."""
    if bands is not None:
        df = df.filter(pl.col("band").is_in(bands))
    done = df.filter(pl.col("nm").is_not_null())
    openr = df.filter(pl.col("nm").is_null())
    src = codes(done, KEYS)
    dst = codes(done, NEXT)
    done = done.with_columns(*(src[l].alias(f"s{l}") for l in range(3)), *(dst[l].alias(f"d{l}") for l in range(3)))
    # source support at each level (interior sources only; m = 0 sources give E[D])
    inner = done.filter(pl.col("m") > 0)
    support = {l: inner.group_by(f"s{l}").agg(pl.col("n").sum().alias("N")) for l in range(3)}

    def pick(prefix: str, frame: pl.DataFrame) -> pl.DataFrame:
        """Assign each row's state to the highest level <= `level` with support >= floor."""
        out = frame
        chosen = pl.lit(0, dtype=pl.UInt64)
        tag = pl.lit(0, dtype=pl.UInt64)
        for l in range(level + 1):
            sup = support[l].filter(pl.col("N") >= floor).select(pl.col(f"s{l}").alias(f"_k{l}"))
            out = out.join(sup.with_columns(pl.lit(True).alias(f"_ok{l}")), left_on=f"{prefix}{l}", right_on=f"_k{l}", how="left")
            ok = pl.col(f"_ok{l}").fill_null(False)
            chosen = pl.when(ok).then(pl.col(f"{prefix}{l}")).otherwise(chosen)
            tag = pl.when(ok).then(pl.lit(l, dtype=pl.UInt64)).otherwise(tag)
        out = out.with_columns((chosen + tag * (2**50)).alias(f"{prefix}id")).drop([c for c in out.columns if c.startswith("_")])
        return out

    inner = pick("s", inner)
    inner = pick("d", inner)
    # rows: source id -> dest id, with absorbing flag
    rows = inner.with_columns((pl.col("nm") == 0).alias("absorb"))
    srcstat = rows.group_by("sid").agg(pl.col("n").sum().alias("N"), pl.col("time").sum().alias("T"), pl.col("m").first().alias("m"))
    ids = srcstat["sid"].to_list()
    index = {v: i for i, v in enumerate(ids)}
    nS = len(ids)
    Ns = srcstat["N"].to_numpy().astype(float)
    ms = srcstat["T"].to_numpy().astype(float) / Ns
    mil = srcstat["m"].to_numpy()
    tr = rows.filter(~pl.col("absorb")).group_by(["sid", "did"]).agg(pl.col("n").sum())
    ab = rows.filter(pl.col("absorb")).group_by("sid").agg(pl.col("n").sum())
    r, c, w = [], [], []
    dead = 0.0
    total_trans = float(rows["n"].sum()) if rows.height else 0.0
    for s_id, d_id, n in tr.iter_rows():
        if d_id in index:
            r.append(index[s_id]); c.append(index[d_id]); w.append(n / Ns[index[s_id]])
        else:
            dead += n
    Q = sp.csr_matrix((w, (r, c)), shape=(nS, nS)) if nS else sp.csr_matrix((0, 0))
    a = np.zeros(nS)
    for s_id, n in ab.iter_rows():
        a[index[s_id]] = n / Ns[index[s_id]]
    # dead-end destinations (never a supported source): renormalise their rows, record the mass
    rowsum = np.asarray(Q.sum(axis=1)).ravel() + a if nS else np.zeros(0)
    res: dict = dict(level=level, floor=floor, n_states=nS, dead_end_mass=dead / total_trans if total_trans else 0.0, status="ok")
    if nS == 0 or rowsum.min() <= 0:
        res["status"] = "no-data"
        return res
    if res["dead_end_mass"] > max_dead:
        res["status"] = "dead-end-mass"
    Q = sp.diags(1.0 / rowsum) @ Q
    a = a / rowsum
    # absorption reachability (nonabsorbing classes are failures, never dropped)
    rev = Q.T.tocsr()
    reach = a > 0
    frontier = list(np.flatnonzero(reach))
    while frontier:
        nxt = []
        for j in frontier:
            for i in rev.indices[rev.indptr[j]:rev.indptr[j + 1]]:
                if not reach[i]:
                    reach[i] = True
                    nxt.append(i)
        frontier = nxt
    res["unreachable_states"] = int((~reach).sum())
    if (~reach).any():
        res["status"] = "nonabsorbing"
        return res
    A = sp.identity(nS, format="csc") - Q.tocsc()
    u = _solve(A, ms)
    # entry law: first interior segment after a milestone-0 segment
    start = df.filter(pl.col("nm").is_not_null() & (pl.col("m") == 0))
    ed = float(start["time"].sum() / start["n"].sum()) if start.height else float("nan")
    ent = done if entry_df is None else entry_df.filter(pl.col("nm").is_not_null()).with_columns(*(codes(entry_df, NEXT)[l].alias(f"d{l}") for l in range(3)))
    ent = ent.filter((pl.col("m") == 0) & (pl.col("nm") >= 1))
    ent = pick("d", ent)
    eg = ent.group_by("did").agg(pl.col("n").sum())
    wsum = 0.0; ET = 0.0; lost = 0.0
    wvec = np.zeros(nS)
    for d_id, n in eg.iter_rows():
        if d_id in index:
            wvec[index[d_id]] += n
            wsum += n
        else:
            lost += n
    if wsum == 0:
        res["status"] = "no-entry"
        return res
    wvec /= wsum
    ET = float(wvec @ u)
    visits = _solve(A.T.tocsc(), wvec)
    deep_time = float((visits * ms)[mil == DEEP].sum())
    res.update(ED=ed, ET=ET, pred_BS=ed / (ed + ET), deep_share=deep_time / ET if ET > 0 else float("nan"),
               entry_lost=lost / (wsum + lost), censored_time=float(openr["time"].sum()), completed_time=float(done["time"].sum()),
               skipped=int(done["skipped"].sum()), n_segments=int(done["n"].sum()))
    return res


def bootstrap(replicates: list[pl.DataFrame], reps: int, seed: int, **kw) -> dict:
    """Resample whole replicate runs (never individual segments)."""
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(reps):
        pick_ = rng.integers(0, len(replicates), len(replicates))
        r = fit(pl.concat([replicates[i] for i in pick_]), **kw)
        vals.append(r.get("ET", float("nan")))
    v = np.array(vals)
    v = v[np.isfinite(v)]
    return dict(lo=float(np.quantile(v, 0.025)), hi=float(np.quantile(v, 0.975)), sd=float(v.std()), n=int(v.size))
