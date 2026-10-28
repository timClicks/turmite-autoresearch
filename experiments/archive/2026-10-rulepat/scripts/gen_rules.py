"""gen_rules.py MINLEN MAXLEN : every R-prefixed rule (mirror image of L-prefixed) of those lengths, lexicographic."""
import sys, itertools
lo, hi = int(sys.argv[1]), int(sys.argv[2])
for n in range(lo, hi + 1):
    for tail in itertools.product("LR", repeat=n - 1):
        print("R" + "".join(tail))
