"""Known-answer controls for weighting, censoring and pilot decision logic."""
import unittest
from unittest.mock import patch

import analyze


def fixture():
    rows, audits = [], []
    for rule in analyze.RULES:
        for seed in analyze.SEEDS:
            for band in [0, 1]:
                audits.append(dict(rule=rule, seed=str(seed), band=str(band), status="complete",
                    departures="8", short="0", eligible_long="8", overflow="0", sampled="8",
                    gap_or_quota="0", unfinished="0", completed_time="1024", overflow_time="0", unfinished_time="0"))
                for dep in range(8):
                    for k in [0, 1, 2, 4, len(rule)]:
                        for rep in range(4):
                            effect = {0: 2, 1: 1}.get(k, 0)
                            rows.append(dict(rule=rule, seed=str(seed), band=str(band), departure=str(dep),
                                k=str(k), replica=str(rep), base_t="128", arm_t=str(128 * 2**effect),
                                path_equal=str(int(effect == 0)), return_equal=str(int(effect == 0)),
                                censored="0", read_changed="5", read_cells="10",
                                split_step=str(10 if effect else 0), split_visit="3"))
    return rows, audits, {}


class AnalysisTests(unittest.TestCase):
    def test_planted_effects_pass_without_replica_pseudoreplication(self):
        with patch.object(analyze, "load_results", return_value=fixture()):
            result = analyze.analyse()
        self.assertTrue(all(result["gates"].values()))
        for cell in result["cells"]:
            self.assertEqual(cell["arms"][1]["starts"], 4)
            self.assertEqual(cell["arms"][1]["effect"], 1)
            self.assertEqual(cell["ratio_interval"], [.5, .5])
            self.assertEqual(cell["arms"][1]["seed_sd"], 0)
        self.assertEqual(result["verdict"], "H-clock pilot criterion met")

    def test_censored_arms_cannot_pass_the_gate(self):
        rows, audits, hashes = fixture()
        for row in rows:
            if row["k"] == "1":
                row["censored"] = "1"
        with patch.object(analyze, "load_results", return_value=(rows, audits, hashes)):
            result = analyze.analyse()
        self.assertFalse(result["gates"]["each_arm_censoring_at_most_one_percent"])
        self.assertTrue(result["verdict"].startswith("gates failed"))

    def test_one_overflow_can_carry_most_of_the_time(self):
        rows, audits, hashes = fixture()
        audits[0].update(departures="9", overflow="1", overflow_time="1000000", completed_time="1001024")
        with patch.object(analyze, "load_results", return_value=(rows, audits, hashes)):
            result = analyze.analyse()
        self.assertTrue(result["gates"]["baseline_censoring_below_one_percent"])
        self.assertGreater(result["totals"]["overflow_time"] / result["totals"]["completed_time"], .9)


if __name__ == "__main__":
    unittest.main()
