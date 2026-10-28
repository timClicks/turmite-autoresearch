"""Spec generators for the lattice/turmite screens (items 24, 25, 28). usage: python3 experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_screens.py hex|cube|tm"""
import itertools, sys
kind = sys.argv[1]
if kind == "hex":  # mirror-canonical: first letter in {r, R}; lengths 2..6
    for n in range(2, 7):
        for w in itertools.product("rRlL", repeat=n):
            if w[0] in "rR" and len(set(w)) > 1:
                print("hex:" + "".join(w))
elif kind == "cube":  # lengths 2..5 (6 later if time)
    top = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    for n in range(2, top + 1):
        for w in itertools.product("LRUD", repeat=n):
            lr = [c for c in w if c in "LR"]; ud = [c for c in w if c in "UD"]
            # mirror canonical: first L/R letter is R, first U/D letter is U (two reflections)
            if len(set(w)) > 1 and (not lr or lr[0] == "R") and (not ud or ud[0] == "U"):
                print("cube:" + "".join(w))
elif kind == "tm":
    for i in range(65536):
        print(f"tm:2:2:{i}")
