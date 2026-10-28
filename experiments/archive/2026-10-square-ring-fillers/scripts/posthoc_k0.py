"""POST HOC (not registered): the k = 0 member of the crawler family. C_0 has a = 0, b = c = 1, d = 2 (one row of 1s over an
interior of 2s) and needs T(0) = L, T(1) = R; its mirror image (L <-> R, x -> -x) is the edge of canonical rules starting `RL`.
For k = 0 the configuration does not depend on k, so a finite check over the two letters read is a complete proof.

usage: python3 experiments/archive/2026-10-square-ring-fillers/scripts/posthoc_k0.py   -> results/posthoc_k0.txt
"""
import itertools
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]
BIN = ROOT / "target/release/examples/square_ring_fillers_crawler"


def run(rule):
    out = subprocess.run([str(BIN), "0", rule, "16"], capture_output=True, text=True, check=True).stdout.strip()
    return out, "periods_ok=16 " in out and "first_fail=none" in out


lines = ["POST HOC: k = 0 crawler (C_0, a=0, b=c=1, d=2), 16 periods, every rule of length 2..6 over {L, R}"]
ok_pred = bad = 0
for n in range(2, 7):
    for t in itertools.product("LR", repeat=n):
        r = "".join(t)
        out, ok = run(r)
        pred = r[0] == "L" and r[1] == "R"
        ok_pred += ok == pred
        bad += ok != pred
        lines.append(f"{r} translates={ok} predicted={pred}")
lines.append(f"translation iff T(0) = L and T(1) = R: {ok_pred} agree, {bad} disagree")
(EXP / "results/posthoc_k0.txt").write_text("\n".join(lines) + "\n")
print(lines[0]); print(lines[-1])
