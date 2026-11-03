# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Run with uv run --offline --script .../scripts/test_python_sim.py."""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
EXPERIMENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments/_lib"))
import turmite_sim as sim


class Oracle:
    """Visit counts, vector turns and a local RNG: no production step/geometry code."""
    def __init__(self, config):
        self.config = config
        self.visits = {}
        self.pos = (0, 0)
        self.direction = (0, -1)
        self.random = config.seed
        self.run = 0
        self.origin = True
        self.kappa = 0.0
        self.defined = self.boundary_reads = 0

    def step(self):
        occupied = set(self.visits)
        boundary = {p for p in occupied if any(q not in occupied for q in
                    ((p[0]-1,p[1]), (p[0]+1,p[1]), (p[0],p[1]-1), (p[0],p[1]+1)))}
        if boundary:
            self.defined += 1
            self.boundary_reads += self.pos in boundary
            self.kappa += (len(occupied) / len(boundary)) if self.pos in boundary else 0
        self.random = (self.random + 11400714819323198485) % (2**64)
        z = self.random
        z = ((z ^ (z // (2**30))) * 13787848793156543929) % (2**64)
        z = ((z ^ (z // (2**27))) * 10723151780598845931) % (2**64)
        draw = z ^ (z // (2**31))
        count = self.visits.get(self.pos, 0)
        self.run = 0 if count else self.run + 1
        if count:
            self.origin = False
        turn = self.config.rule[count % len(self.config.rule)]
        if not count and self.config.policy == "fresh-set":
            turn = self.config.fresh_set[(draw // (2**32) * len(self.config.fresh_set)) // (2**32)]
        if not count and self.config.policy == "persistent-fresh":
            if self.config.cap is not None and self.run >= self.config.cap:
                turn = "U"
            else:
                u = draw // (2**32)
                turn = "S" if u % 128 else ("L" if (u // 128) % 2 else "R")
        dx, dy = self.direction
        self.direction = {"S": (dx, dy), "R": (-dy, dx), "L": (dy, -dx), "U": (-dx, -dy)}[turn]
        self.visits[self.pos] = count + 1
        self.pos = self.pos[0] + self.direction[0], self.pos[1] + self.direction[1]


class SimulationTests(unittest.TestCase):
    def test_splitmix_published_seed_zero_vector(self):
        state, draw = sim.splitmix_next(0)
        self.assertEqual(draw, 0xE220A8397B1DCDAF)
        self.assertEqual(sim.splitmix_next(state)[1], 0x6E789E6AA1B965F4)

    def test_bit_sampler_has_exact_dyadic_frequencies(self):
        turns = [sim.persistent_turn(u << 32) for u in range(256)]
        self.assertEqual(turns.count(0), 254)
        self.assertEqual(turns.count(1), 1)
        self.assertEqual(turns.count(3), 1)

    def test_oracle_stepwise_colours_position_geometry_and_rng(self):
        cases = [sim.Config(rule, policy, seed, cap, turns)
                 for rule, seed in [("RL", 0), ("RLL", 7), ("RRLLLRLRRRLL", 2**64-1)]
                 for policy, cap, turns in [("ant", None, "RL"), ("fresh-set", None, "RLU"),
                    ("fresh-set", None, "RU"), ("persistent-fresh", 1, "RLU"),
                    ("persistent-fresh", 4, "RLU"), ("persistent-fresh", 32, "RLU"),
                    ("persistent-fresh", None, "RLU")]]
        for config in cases:
            with self.subTest(config=config):
                walker, reference = sim.SparseWalker(config), Oracle(config)
                for _ in range(256):
                    walker.step()
                    reference.step()
                    self.assertEqual((walker.x, walker.y), reference.pos)
                    self.assertEqual(sim.DIRS[walker.heading], reference.direction)
                    self.assertEqual(walker.cells, {p: n % len(config.rule) for p, n in reference.visits.items()})
                    self.assertEqual(walker.state, reference.random)
                    self.assertEqual(walker.run_length, reference.run)
                    self.assertEqual(walker.origin_run, reference.origin)
                    self.assertAlmostEqual(walker.kappa_sum, reference.kappa)
                    self.assertEqual(walker.boundary_reads, reference.boundary_reads)
                self.assert_geometry(walker)

    def assert_geometry(self, walker):
        cells = walker.cells
        perimeter = sum((x+dx, y+dy) not in cells for x, y in cells for dx, dy in sim.DIRS)
        boundary = {(x,y) for x,y in cells if any((x+dx,y+dy) not in cells for dx,dy in sim.DIRS)}
        self.assertEqual(walker.perimeter, perimeter)
        self.assertEqual(walker.boundary, boundary)

    def test_all_small_rules_against_count_oracle(self):
        for n in range(1, 5):
            for letters in itertools.product("RL", repeat=n):
                config = sim.Config("".join(letters))
                walker, reference = sim.SparseWalker(config), Oracle(config)
                for _ in range(96):
                    walker.step()
                    reference.step()
                self.assertEqual((walker.x, walker.y), reference.pos)
                self.assertEqual(walker.cells, {p: v % n for p, v in reference.visits.items()})

    def test_seen_zero_is_not_virgin(self):
        walker = sim.SparseWalker(sim.Config("R", "fresh-set", 1, fresh_set="RU"))
        seen_zero_revisits = 0
        for _ in range(1000):
            p = walker.x, walker.y
            before = p in walker.cells
            seen_zero_revisits += before and walker.cells[p] == 0
            fresh = walker.step()
            self.assertEqual(fresh, not before)
        self.assertGreater(seen_zero_revisits, 0)

    def test_cap_origin_exception_and_conservation(self):
        # Force straight draws: the first origin reversal lands on a virgin cell.
        def straight(state):
            return (state + 0x9E3779B97F4A7C15) & sim.MASK64, 1 << 32
        for cap in (1,2,4,8,16,32,64,128):
            walker = sim.SparseWalker(sim.Config("RLL", "persistent-fresh", 7, cap))
            with patch.object(sim, "splitmix_next", straight):
                for _ in range(512):
                    walker.step()
                    self.assertLessEqual(walker.run_length, cap + int(walker.origin_run))
            summary = walker.fresh_summary()
            accounted = (summary["origin_completed_length"] or 0) + summary["unfinished"]["length"]
            accounted += sum(r["duration_weight"] for r in summary["completed_nonorigin"])
            self.assertEqual(accounted, len(walker.cells))
        walker = sim.SparseWalker(sim.Config("RLL", "persistent-fresh", 0, 1))
        walker.step()
        walker.step()
        self.assertEqual(walker.run_length, 2)
        self.assertTrue(walker.origin_run)

    def test_fresh_ru_bound_and_rlu_nonvacuity(self):
        for turns in ("RU", "LU", "RLU"):
            w = sim.SparseWalker(sim.Config("RRLLLRLRRRLL", "fresh-set", 2026102601, fresh_set=turns))
            longest = 0
            for _ in range(10000):
                w.step()
                longest = max(longest, w.run_length)
                if turns != "RLU":
                    self.assertLessEqual(w.run_length, 4 + int(w.origin_run))
            if turns == "RLU":
                self.assertGreater(longest, 5)

    def test_resource_stop_does_not_advance_state(self):
        w = sim.SparseWalker(sim.Config("RL", "persistent-fresh", cap=128))
        w.step()
        before = w.checkpoint()
        with self.assertRaises(sim.CellLimit):
            w.step(max_cells=1)
        self.assertEqual(w.checkpoint(), before)

    def test_resume_matches_uninterrupted_including_metrics(self):
        for config in (sim.Config(), sim.Config("RLL", "fresh-set", fresh_set="RLU"),
                       sim.Config("RLL", "persistent-fresh", 1729, 8)):
            a = sim.SparseWalker(config)
            for _ in range(511):
                a.step()
            b = sim.SparseWalker.from_checkpoint(json.loads(json.dumps(a.checkpoint())))
            for _ in range(700):
                a.step()
                b.step()
            self.assertEqual(a.checkpoint(), b.checkpoint())
            self.assertEqual(a.snapshot(hull=True), b.snapshot(hull=True))

    def test_checkpoint_rejects_bad_version_colours_and_clock(self):
        w = sim.SparseWalker(sim.Config())
        w.step()
        for key, value in (("format", "wrong"), ("cells", [[0,0,999]]), ("rng_state", 0),
                           ("fresh_hist", [[4,1]])):
            data = w.checkpoint()
            data[key] = value
            with self.assertRaises(ValueError):
                sim.SparseWalker.from_checkpoint(data)

    def test_hull_degenerate_and_translated_square(self):
        for pts in ([], [(0,0)], [(1,1),(2,2),(3,3)]):
            self.assertEqual(sim.hull_area(pts), 0)
        self.assertEqual(sim.hull_area([(-10,-5),(-7,-5),(-7,-1),(-10,-1),(-9,-4)]), 12)

    def test_nine_point_fit_and_partial_window_exclusion(self):
        samples = []
        for t in sim.sample_steps(1024, suboctaves=True):
            samples.append(dict(steps=t, area=t**0.7, width=t**0.33, boundary_reads=t/10,
                                kappa_sum=t/2, kappa_defined_steps=t))
        fits = sim.octave_fits(samples, suboctaves=True)
        last = fits[-1]
        self.assertEqual(last["samples"], 9)
        self.assertAlmostEqual(last["alpha_A"], 0.7)
        self.assertAlmostEqual(last["alpha_W"], 0.33)
        self.assertEqual(last["estimator"], "ols_suboctave")
        self.assertLess(len(sim.octave_fits(samples[:-1], suboctaves=True)), len(fits))
        missing = [r for r in samples if r["steps"] != sim.sample_steps(1024,512,suboctaves=True)[3]]
        self.assertNotIn(1024, [r["end"] for r in sim.octave_fits(missing,suboctaves=True)])

    def test_input_validation(self):
        for kw in ({"rule":""}, {"rule":"RX"}, {"seed":-1}, {"cap":0},
                   {"cap":4}, {"policy":"bogus"}, {"fresh_set":"S"}):
            with self.assertRaises(ValueError):
                sim.Config(**kw)

    def test_cli_checkpoint_resource_exit_and_no_overwrite(self):
        scratch = EXPERIMENT / "scratch"
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            dest = Path(tmp) / "run"
            cmd = [sys.executable, str(Path(__file__).with_name("python_sim.py")),
                   "--steps", "1024", "--policy", "persistent-fresh", "--cap", "8",
                   "--max-cells", "2", "--output-dir", str(dest)]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 2, first.stderr)
            self.assertEqual(json.loads((dest/"provenance.json").read_text())["status"], "resource_incomplete")
            again = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)
            self.assertIn("File exists", again.stderr)
            resumed = subprocess.run([sys.executable, str(Path(__file__).with_name("python_sim.py")),
                "--resume", str(dest/"checkpoint.json"), "--steps", "1024", "--suboctaves",
                "--output-dir", str(Path(tmp)/"resumed")], capture_output=True, text=True)
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            self.assertEqual(json.loads(resumed.stdout)["steps"], 1024)


if __name__ == "__main__":
    unittest.main(verbosity=2)
