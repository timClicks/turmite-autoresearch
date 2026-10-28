"""Checks that the atlas stays a view of the record: python3 blog/scripts/test_atlas.py"""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import atlas  # noqa: E402


class AtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inp = atlas.load_inputs()

    def mutated(self, fn):
        inp = copy.deepcopy(self.inp)
        fn(inp)
        return atlas.validate(inp)

    def test_committed_atlas_is_valid(self):
        self.assertEqual(atlas.validate(self.inp), [])

    def test_every_experiment_is_covered(self):
        topics = self.inp["atlas"]["topics"]
        filed = {i["ref"] for t in topics for i in t["evidence"] + t["counter"]} | {s for t in topics for s in t["also"]}
        self.assertEqual(self.inp["experiments"] - filed - set(self.inp["atlas"]["unfiled"]), set())

    def test_unfiled_experiment_fails(self):
        errs = self.mutated(lambda i: i["experiments"].add("2099-01-new-thing") or i["guides"].update({"2099-01-new-thing": {}}))
        self.assertTrue(any("neither filed" in e for e in errs))

    def test_unknown_experiment_and_claim_fail(self):
        def f(i):
            t = i["atlas"]["topics"][0]
            t["evidence"].append({"ref": "2026-10-nope"})
            t["claims"].append("ZZ-99")
        errs = self.mutated(f)
        self.assertTrue(any("unknown experiment" in e for e in errs))
        self.assertTrue(any("unknown claim" in e for e in errs))

    def test_measurements_are_rejected_in_curated_text(self):
        for text in ("exponent 0.33", "up by 12%", "t^(1/3) at 2e9 steps", "p < 0.01"):
            errs = self.mutated(lambda i, text=text: i["atlas"]["topics"][0].update(state_summary=text))
            self.assertTrue(errs, text)

    def test_untracked_file_reference_fails(self):
        errs = self.mutated(lambda i: i["atlas"]["topics"][0]["evidence"].append({"ref": "file:notes/does-not-exist.md", "why": "x"}))
        self.assertTrue(any("not tracked" in e for e in errs))

    def test_findings_are_copied_not_rewritten(self):
        view = atlas.materialise(self.inp, "test")
        first = view["topics"][0]["evidence"][0]
        self.assertEqual(first["finding"], self.inp["guides"][first["slug"]]["finding"])
        claims = {c["id"]: c for t in view["topics"] for c in t["claims"]}
        self.assertEqual(claims["BO-02"]["observation"], self.inp["claims"]["BO-02"]["observation"])

    def test_staleness_flags_newer_experiments(self):
        def f(i):
            i["atlas"]["topics"][0]["reviewed"] = "2026-10-13"
        inp = copy.deepcopy(self.inp)
        f(inp)
        view = atlas.materialise(inp, "test")
        self.assertTrue(view["topics"][0]["newer_than_review"])


if __name__ == "__main__":
    unittest.main()
