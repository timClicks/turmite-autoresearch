"""C1a-1: which of the four heading conventions close the sweeper cycle on the canonical file (derivation, not copy)."""
import sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from c1_ant import *

ph = parse_canonical()
rule = sys.argv[1] if len(sys.argv) > 1 else "RLRLLL"
ok = {}
for tname, table in (("CW", CW), ("CCW", CCW)):
    for rs in (1, -1):
        res = [closes(rule, ph, q, m, table, rs) for q in range(3) for m in (2, 4, 10, 50)]
        ok[(tname, rs)] = res
        print(f"table={tname} R={rs:+d}: closes {sum(res)}/{len(res)} of (q in 0..2) x (m in 2,4,10,50)")
closing = [k for k, v in ok.items() if all(v)]
print("closing candidates:", closing)
