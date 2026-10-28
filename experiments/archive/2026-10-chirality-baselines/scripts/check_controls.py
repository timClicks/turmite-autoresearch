"""Synthetic scoring controls; no ant instrument/window/estimator is changed."""
import unittest
import numpy as np
from compare import centered_r2, fit_baseline, predict_baseline, metrics, comparison


class Controls(unittest.TestCase):
    def test_residual_skill(self):
        y = np.array([0., 2., 10., 12.])
        labels = np.array(["L", "L", "R", "R"])
        constant = np.array([1., 1., 11., 11.])
        self.assertEqual(centered_r2(y, constant, labels), 0.)
        self.assertEqual(centered_r2(y, y, labels), 1.)
        self.assertEqual(centered_r2(y, 2 * constant - y, labels), -3.)
        self.assertEqual(centered_r2(y, y + 100, labels), 1.)
        self.assertLess(metrics(y, y + 100, 6.)["r2"], 0.)

    def test_training_only_and_fallbacks(self):
        rules, y = ["RLLL", "RLLR", "RRLL"], np.array([1., 3., 8.])
        primary = fit_baseline(rules, y, 1)
        fine = fit_baseline(rules, y, 3)
        np.testing.assert_array_equal(predict_baseline(["RLLL", "RLRR", "RRRR"], fine, primary, 4., 3), [1., 2., 8.])
        np.testing.assert_array_equal(predict_baseline(["R"], fine, primary, 4., 3), [4.])
        self.assertEqual(primary, {"L": 2., "R": 8.})

    def test_paired_bootstrap_and_score(self):
        y = np.array([0., 2., 10., 12.])
        labels = np.array(["L", "L", "R", "R"])
        a = comparison(y, y, y + 1, labels, np.random.default_rng(42))
        b = comparison(y, y, y + 1, labels, np.random.default_rng(42))
        self.assertEqual(a, b)
        self.assertEqual(a["sse_reduction"], 1.)
        self.assertEqual(a["sse_reduction_ci"], [1., 1.])


if __name__ == "__main__":
    unittest.main()
