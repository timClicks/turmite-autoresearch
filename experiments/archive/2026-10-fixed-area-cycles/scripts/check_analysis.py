# /// script
# dependencies = ["polars", "numpy", "scipy"]
# ///
"""Check numerical estimators against exact synthetic answers and PRESS identity."""
import numpy as np
from analyse import loo_terms, nearest_rank, rho


def main():
    seed = 20261016
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(44, 3))
    design = np.column_stack([np.ones(44), X])
    y_linear = design @ np.array([2.0, 0.3, -0.8, 1.4])
    exact_errors, _ = loo_terms(X, y_linear)
    assert np.max(exact_errors) < 1e-24
    y = y_linear + rng.normal(size=44)
    e, denominator = loo_terms(X, y)
    beta = np.linalg.lstsq(design, y, rcond=None)[0]
    hat_diag = np.sum(design * (design @ np.linalg.inv(design.T @ design)), axis=1)
    press = ((y - design @ beta) / (1 - hat_diag)) ** 2
    assert np.allclose(e, press, rtol=1e-11, atol=1e-11)
    intercept_error, intercept_denominator = loo_terms(None, y)
    assert np.allclose(intercept_error, intercept_denominator, rtol=1e-12, atol=1e-12)
    assert np.array_equal(denominator, intercept_denominator)
    assert nearest_rank(np.arange(1, 1001), 0.999) == 999
    assert nearest_rank(np.array([1, 1, 9]), 0.5) == 1
    assert rho(np.arange(44), -np.arange(44)) == -1
    print(f"seed={seed}; exact linear residual, independent PRESS identity, training-mean denominator, nearest-rank and Spearman checks PASS")


if __name__ == "__main__":
    main()
