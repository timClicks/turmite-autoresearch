"""Shared contour estimators and synthetic calibration; run under uv."""
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
BANDS = {"shape": (3, 8), "local": (9, 64), "fine": (65, 256)}
LAGS = (1, 2, 4, 8, 16, 32, 64, 128)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coefficients(r):
    return np.fft.rfft(r) / len(r)


def band(r, name):
    c = coefficients(r)
    lo, hi = BANDS[name]
    keep = np.zeros_like(c)
    keep[lo:min(hi + 1, len(c))] = c[lo:min(hi + 1, len(c))]
    return np.fft.irfft(keep * len(r), n=len(r)), keep


def measure(r):
    result = {"radius": float(np.mean(r))}
    for name in BANDS:
        h, _ = band(r, name)
        v = float(np.mean(h * h))
        result[name] = v
        result[name + "_normalised"] = v / result["radius"] ** 2
    h, _ = band(r, "local")
    result["structure"] = [float(np.mean((np.roll(h, lag) - h) ** 2)) for lag in LAGS]
    crossing = next((lag for lag, s in zip(LAGS, result["structure"])
                     if result["local"] > 0 and s >= result["local"]), None)
    result["length"] = None if crossing is None else 2 * np.pi * result["radius"] * crossing / len(r)
    coarse = r.reshape(-1, 2).max(axis=1)
    hc, _ = band(coarse, "local")
    result["coarse_local_ratio"] = float(np.mean(hc * hc) / result["local"]) if result["local"] > 0 else None
    return result


def calibration():
    theta = 2 * np.pi * np.arange(512) / 512
    for m, name in ((4, "shape"), (32, "local")):
        r = 100 + 3 * np.cos(m * theta)
        h, _ = band(r, name)
        np.testing.assert_allclose(np.mean(h * h), 4.5, rtol=1e-10)
        for other in set(BANDS) - {name}:
            assert np.mean(band(r, other)[0] ** 2) < 1e-20
        for lag in LAGS:
            expected = 9 * (1 - np.cos(2 * np.pi * m * lag / 512))
            np.testing.assert_allclose(np.mean((np.roll(h, lag) - h) ** 2), expected, rtol=1e-10, atol=1e-20)
    r = 100 + 3 * (-1.) ** np.arange(512)
    np.testing.assert_allclose(np.mean(band(r, "fine")[0] ** 2), 9, rtol=1e-10)
    r = 100 + sum(a * np.cos(m * theta + .1 * m) for m, a in ((4, 3), (32, 2), (128, 1)))
    np.testing.assert_allclose(sum(np.mean(band(r, name)[0] ** 2) for name in BANDS), np.var(r), rtol=1e-10)
    # Fixed lobe persists; orthogonal local modes decorrelate in the same frame.
    a = coefficients(100 + 3 * np.cos(4 * theta) + np.cos(32 * theta))
    b = coefficients(100 + 3 * np.cos(4 * theta) + np.cos(33 * theta))
    np.testing.assert_allclose(persistence(a[3:9], b[3:9]), 1, atol=1e-10)
    np.testing.assert_allclose(persistence(a[9:65], b[9:65]), 0, atol=1e-10)
    return {"status": "PASS", "seed": 20261015, "tests": ["mode separation", "sinusoid structure function", "Nyquist variance", "Parseval", "persistence"]}


def persistence(a, b):
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.vdot(a, b).real / norm) if norm > 0 else None


if __name__ == "__main__":
    result = calibration()
    result["command"] = "uv run experiments/archive/2026-10-hull-checks/scripts/checks.py"
    result["commit"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    result["source_sha256"] = digest(Path(__file__))
    (EXP / "results" / "calibration.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
