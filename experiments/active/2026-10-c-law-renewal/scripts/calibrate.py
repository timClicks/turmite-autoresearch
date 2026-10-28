"""Synthetic calibration of the stationary reward estimator; no ant outcomes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
from scipy.sparse import csr_matrix, csgraph

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def stationary(matrix, tolerance=1e-12, maxiter=100000):
    """Unique stationary law; lazy iteration handles periodic chains explicitly."""
    p = csr_matrix(matrix, dtype=float)
    if p.shape[0] == 0 or p.shape[0] != p.shape[1]:
        raise ValueError("empty or nonsquare chain")
    if not np.all(np.isfinite(p.data)) or np.any(p.data < 0):
        raise ValueError("invalid probabilities")
    if not np.allclose(np.asarray(p.sum(axis=1)).ravel(), 1, atol=1e-12, rtol=0):
        raise ValueError("not a stochastic matrix")
    components = csgraph.connected_components(p, directed=True, connection="strong", return_labels=False)
    if components != 1:
        raise ValueError("non-irreducible chain needs an explicitly registered class rule")
    pi = np.full(p.shape[0], 1 / p.shape[0])
    for _ in range(maxiter):
        nxt = (pi + p.T @ pi) / 2
        if np.max(np.abs(nxt - pi)) < tolerance:
            return nxt / nxt.sum()
        pi = nxt
    raise ValueError("stationary solver did not converge")


def main():
    n = 1_000_000
    seeds = list(range(2026102031, 2026102047))
    p = np.array([[0.9, 0.1], [0.2, 0.8]])
    reward = np.array([0.1, 0.7])
    true_pi = np.array([2 / 3, 1 / 3])
    truth = float(true_pi @ reward)
    assert np.max(np.abs(stationary(p) - true_pi)) < 1e-10
    assert np.max(np.abs(stationary([[0, 1], [1, 0]]) - [0.5, 0.5])) < 1e-10
    try:
        stationary(np.eye(2))
    except ValueError:
        pass
    else:
        raise AssertionError("reducible chain accepted")
    estimates = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        u = rng.random(n)
        states = np.zeros(n, dtype=np.int8)
        for t in range(1, n):
            states[t] = int(u[t] >= p[states[t - 1], 0])
        counts = np.bincount(states[:-1] * 2 + states[1:], minlength=4).reshape(2, 2)
        fitted = counts / counts.sum(axis=1, keepdims=True)
        births = rng.random(n) < reward[states]
        rates = np.bincount(states, weights=births, minlength=2) / np.bincount(states, minlength=2)
        estimate = float(stationary(fitted) @ rates)
        estimates.append(estimate)
    # A hidden, slowly changing regime has the same pooled mean but very
    # different conditional futures. Matching c alone cannot detect it.
    rng = np.random.default_rng(2026102047)
    hidden = (np.arange(n) // 256) % 2
    y = rng.random(n) < np.where(hidden == 0, 0.05, 0.95)
    after_birth = float(y[1:][y[:-1]].mean())
    after_no_birth = float(y[1:][~y[:-1]].mean())
    contrast = after_birth - after_no_birth
    errors = np.asarray(estimates) - truth
    report = {
        "status": "synthetic_only",
        "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "command": "uv run --frozen experiments/active/2026-10-c-law-renewal/scripts/calibrate.py",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "n_events_per_seed": n, "seeds": seeds, "true_c": truth,
        "estimates": estimates, "signed_bias": float(errors.mean()),
        "between_seed_sd": float(np.std(estimates, ddof=1)),
        "max_absolute_error": float(np.max(np.abs(errors))),
        "negative_control": {"seed": 2026102047, "hidden_block_length": 256,
            "after_birth": after_birth, "after_no_birth": after_no_birth,
            "contrast": contrast, "pooled_c": float(y.mean()),
            "interpretation": "pooled c can be correct despite failure of history-free conditional prediction"},
        "passed": bool(np.max(np.abs(errors)) <= 0.01 and contrast > 0.5),
        "scope": "stationary solver and reward estimator only; ant state/backoff model not calibrated yet",
    }
    path = EXP / "results" / "calibration.json"
    data = (json.dumps(report, indent=2) + "\n").encode()
    if path.exists() and path.read_bytes() != data:
        raise RuntimeError("refusing to overwrite calibration; register a versioned rerun")
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(data)
    print(json.dumps(report, indent=2))
    assert report["passed"]


if __name__ == "__main__":
    main()
