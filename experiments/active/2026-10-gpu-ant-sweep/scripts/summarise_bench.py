# /// script
# requires-python = ">=3.10"
# ///
"""Parse results/bench_*.log into results/bench_summary.json and print a table. Stdlib only."""
import json, re, sys
from pathlib import Path

res = Path(__file__).resolve().parents[1] / "results"
out = {}
for log in sorted(res.glob("bench_L*.log")):
    tag = log.stem.removeprefix("bench_")
    rows, lean, lean_clean = [], None, None
    for line in log.read_text().splitlines():
        if line.startswith("sweep_lean_clean"):
            lean_clean = float(re.search(r"wall_s=([\d.]+)", line).group(1))
        elif line.startswith("sweep_lean "):
            lean = float(re.search(r"wall_s=([\d.]+)", line).group(1))
        elif line.startswith("gpu "):
            g = re.search(r"lanes=(\d+) wall_s=([\d.]+).*csv=(\w+) \| (\d+) steps in ([\d.]+)s", line)
            rows.append(dict(lanes=int(g[1]), wall_s=float(g[2]), csv=g[3], steps=int(g[4]), device_path_s=float(g[5])))
    # a "clean" re-run line, when present, supersedes a lean time that overlapped another job
    base = lean_clean if lean_clean is not None else lean
    for r in rows:
        r["speedup_vs_lean"] = round(base / r["wall_s"], 2)
        r["device_path_steps_per_s"] = r["steps"] / r["device_path_s"]
    out[tag] = dict(lean_wall_s=base, lean_clean_rerun=lean_clean is not None, gpu=rows)
(res / "bench_summary.json").write_text(json.dumps(out, indent=1))
for tag, d in out.items():
    print(f"{tag}: sweep_lean {d['lean_wall_s']:.1f}s")
    for r in d["gpu"]:
        print(f"  lanes {r['lanes']:>5}: {r['wall_s']:6.1f}s  {r['speedup_vs_lean']:5.2f}x  device-path {r['device_path_steps_per_s']:.2e} steps/s  csv {r['csv']}")
