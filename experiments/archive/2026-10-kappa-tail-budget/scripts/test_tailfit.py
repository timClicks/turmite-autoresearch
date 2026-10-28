"""Unit/property checks of tailfit.py against brute force and known answers.
Seeded; run: uv run scripts/test_tailfit.py   (prints PASS lines, exits nonzero on failure)
"""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
import tailfit as tf
rng = np.random.default_rng(20261016)
# 1. Euler-Maclaurin tail mean vs brute-force integer sum
worst = 0.0
for a in (0.3, 0.7, 1.0, 1.4, 2.5):
    for lh in (7.0, 12.25, 18.5, 22.0):
        H = 2.0 ** lh
        u = np.arange(tf.U0, int(np.floor(H)) + 1, dtype=float)
        brute = (tf.U0 - 1) + tf.surv(u, a, lh).sum()
        em = tf.tail_mean(a, lh)[0]
        worst = max(worst, abs(em / brute - 1))
assert worst < 1e-7, worst
print(f"PASS tail_mean Euler-Maclaurin vs brute force, worst rel err {worst:.2e}")
# 2. bin probabilities sum to one for every grid point
P = tf.bin_probs(tf.G_A, tf.G_LH)
assert np.abs(P.sum(1) - 1).max() < 1e-9
print("PASS bin probabilities normalised on the whole grid")
# 3. sampler vs bin probabilities (chi-square) and vs mean, at three off-grid truths
for a, lh in ((0.62, 15.1), (1.0, 20.3), (1.9, 11.7)):
    t = tf.sample_tail(a, lh, 400000, rng)
    assert t.min() >= tf.U0 and t.max() <= 2.0 ** lh
    c = tf.tail_counts(t)
    p = tf.bin_probs(a, lh)[0]
    keep = p * len(t) > 20
    chi2 = (((c[keep] - p[keep] * len(t)) ** 2) / (p[keep] * len(t))).sum()
    assert chi2 < keep.sum() * 3 + 30, (a, lh, chi2, keep.sum())
    m_true = tf.tail_mean(a, lh)[0]
    se = t.std() / np.sqrt(len(t))
    assert abs(t.mean() - m_true) < 5 * se, (a, lh, t.mean(), m_true, se)
print("PASS sampler matches bin probabilities and tail mean")
# 4. exact bit-length binning, including powers of two near float precision limits
v = np.concatenate([np.arange(1, 5000, dtype=float), 2.0 ** np.arange(0, 52), 2.0 ** np.arange(1, 52) - 1])
want = np.array([int(x).bit_length() - 1 for x in v])
assert (tf.log2bin(v) == want).all()
print("PASS floor(log2 t) exact")
# 5. recovery at huge n (grid resolution limits accuracy)
a, lh = 0.9, 18.0
t = tf.sample_tail(a, lh, 2_000_000, rng)
ah, lhh = tf.fit(tf.tail_counts(t))
assert abs(ah[0] - a) <= 0.06 and abs(lhh[0] - lh) <= 0.3, (ah, lhh)
print(f"PASS large-n recovery: a {ah[0]:.2f} (true {a}), log2H {lhh[0]:.2f} (true {lh})")
# 6. deviance: ~chi-square scale under the fitted truth, huge when mass sits where model has none
c = tf.tail_counts(t); ah, lhh = tf.fit(c)
d = tf.deviance(c, ah, lhh)[0]
assert d < 100, d
bad = c.copy(); bad[-3] += 50
assert tf.deviance(bad, ah, lhh)[0] > 1e3
print(f"PASS deviance sane (null {d:.1f})")
print("ALL PASS")
