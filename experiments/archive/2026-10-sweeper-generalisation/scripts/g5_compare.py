"""G5: the 32768-board run must reproduce the 65536-board run's event logs and windows up to the smaller board's exit step.
usage: python3 g5_compare.py SMALL_DIR BIG_DIR EXIT_STEP"""
import sys
from pathlib import Path
small, big, exit_t = Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3])
ok = True
for name in ("events_xmin.csv", "events_xmax.csv", "events_ymin.csv", "events_ymax.csv", "windows.csv"):
    a = [l for l in (small / name).read_text().splitlines()[1:] if int(l.split(",")[0]) < exit_t]
    b = [l for l in (big / name).read_text().splitlines()[1:] if int(l.split(",")[0]) < exit_t]
    same = a == b
    ok &= same
    print(f"{name}: {len(a)} rows (small) vs {len(b)} rows (big) before step {exit_t}: identical={same}")
print("G5", "PASS" if ok else "FAIL")
