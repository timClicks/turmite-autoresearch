"""Plain loop against reference::Ant run from step 0, for the census highways with onset <= 3e5 at t = onset + 3P.
usage: python3 verify_from_zero.py DUMPER_WITH_VERIFY OUT_TXT   (from the experiment directory; the dumper is built from examples/highway_decider_dump.rs
with DUMP_VERIFY support and prints `verify RULE T=.. reference-from-zero identical=true|false`)"""
import csv
import os
import subprocess
import sys
from pathlib import Path

exp = Path(__file__).resolve().parents[1]
census = exp.parents[2] / "experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv"
rows = [r for r in csv.DictReader(open(census)) if r["confirmed"] == "true" and int(r["onset"]) <= 300000]
env = dict(os.environ, DUMP_VERIFY="1")
n = ok = 0
with open(sys.argv[2], "w") as out:
    for r in rows:
        P = int(r["period"])
        t = int(r["onset"]) + 3 * P
        p = subprocess.run([sys.argv[1], r["rule"], str(t), str(P), "4096", str(exp / "scratch" / "verify_tmp")], capture_output=True, text=True, env=env)
        line = p.stdout.strip()
        out.write(line + "\n")
        n += 1
        ok += "identical=true" in line
    out.write(f"TOTAL {ok} of {n} identical\n")
print(f"verify: {ok} of {n} identical")
