"""Task C1 controls 2-4, brute-force side: where does a mutated input first deviate from the unmutated run?
usage: python3 c1_controls.py   (prints the report saved as results/c1_controls.txt)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from c1_ant import *

good = parse_canonical()
mut = parse_canonical(E / "results/canonical_k0_mut46.txt")
print("# control 3/4a: bulk row string index 46 changed 3 -> 4 (results/canonical_k0_mut46.txt)")
for q in range(3):
    for m in (2, 10, 50):
        rg = run_cycle("RLRLLL", good[q], m, record=True)
        rm = run_cycle("RLRLLL", mut[q], m, record=True)
        same_traj = rg["trail"] == rm["trail"] and rg["steps"] == rm["steps"]
        east = max(x for x, y in rg["trail"])
        print(f"q={q} m={m}: trajectories identical for the whole cycle: {same_traj} (steps {rg['steps']}; ant reaches at most column {east} < 46); "
              f"next-phase closure with mutated family: {closes('RLRLLL', mut, q, m)}")
print("# control 2/4b: rule RLRLLR on the canonical file")
for q in range(3):
    for m in (2, 10):
        rg = run_cycle("RLRLLL", good[q], m, record=True)
        rr = run_cycle("RLRLLR", good[q], m, record=True)
        dev = next((i for i, (a, b) in enumerate(zip(rg["trail"], rr["trail"])) if a != b), None)
        # colour read at the last common position before the deviation
        print(f"q={q} m={m}: RLRLLR cycle ok={rr['ok']} ({rr.get('why')}), at step {rr['steps']}; trajectories first differ at step {dev} (RLRLLL ant is then at {rg['trail'][dev]})")
