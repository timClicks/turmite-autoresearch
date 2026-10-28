"""Deterministic, nested sample order of the 702 survivors: sort by sha256("q19-fourth-decade:" + rule).
Any prefix is a uniform random subsample without replacement, so stages can be extended and pooled.
Run: python3 experiments/proposed/2026-10-late-highway-fourth-decade/scripts/order.py"""
import hashlib, pathlib
d = pathlib.Path(__file__).resolve().parents[1] / "results"
rules = d.joinpath("survivors_1e11.txt").read_text().split()
order = sorted(rules, key=lambda r: hashlib.sha256(("q19-fourth-decade:" + r).encode()).hexdigest())
d.joinpath("sample_order.txt").write_text("\n".join(order) + "\n")
