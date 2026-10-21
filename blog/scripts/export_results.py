"""Export homepage numbers and copies of existing manuscript figures.

WSL: uv run --frozen --only-group blog blog/scripts/export_results.py [--check]
No fits or simulations. Every source is committed; hashes pin the evidence.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
PAPER = ROOT / "research-outputs/cube-root-growth-paper"
OUT = ROOT / "blog/_data/preliminary_results.json"
IMAGES = ("exponents", "hero", "ck_time", "memory_paths", "late_switch")
SOURCES = ["main.typ", "numbers.json", "recent_findings.json", "kappa_prediction.json",
           "supplementary/rule-census/rule_census.build.json",
           "supplementary/walker-reference/walker_reference.csv"]
FORECAST = "experiments/2026-10-13-transport-forecast/results/transport_forecast.json"
# Homepage-only figures drawn from experiment results rather than the manuscript: name -> committed source.
PORTRAIT = "experiments/2026-10-21-rlrlll-portrait/results"
EXTRA_IMAGES = {"rlrlll_portrait": f"{PORTRAIT}/portrait.png", "rlrlll_details": f"{PORTRAIT}/portrait_details.png",
                "rlrlll_map": f"{PORTRAIT}/territory_map.png", "rlrlll_arrival": f"{PORTRAIT}/arrival_b16.png"}


def git(*args):
    # /mnt/f reports executable bits differently from Windows Git; compare
    # content without mistaking that mount artefact for changed measurements.
    return subprocess.check_output(["git", "-c", "core.filemode=false", *args], cwd=ROOT, text=True).strip()


def sweeper(frames_path, figure_path):
    """Saved snapshot times, exact visited-cell counts and figure colours for card 09's time slider."""
    frames, fig = json.loads(frames_path.read_text()), json.loads(figure_path.read_text())
    assert len(fig["frame_colours"]) == len(frames["frames"])
    return {"switch_t": fig["switch_t"], "block": frames["block"], "width_cells": frames["bbox_cells"]["w"],
            "t": [f["t"] for f in frames["frames"]], "visited": [f["visited_cells"] for f in frames["frames"]],
            "colours": fig["frame_colours"]}


def export():
    image_sources = {p: PAPER / f"fig/{p}.png" for p in IMAGES} | {k: ROOT / v for k, v in EXTRA_IMAGES.items()}
    portrait = [ROOT / PORTRAIT / "frames.json", ROOT / PORTRAIT / "figure.json"]
    inputs = [PAPER / p for p in SOURCES] + [ROOT / FORECAST] + portrait + list(image_sources.values())
    paths = [p.relative_to(ROOT).as_posix() for p in inputs]
    if git("status", "--porcelain", "--", *paths):
        raise SystemExit("Commit scientific inputs before exporting homepage results")
    n = json.loads((PAPER / "numbers.json").read_text())
    rf = json.loads((PAPER / "recent_findings.json").read_text())
    kp = json.loads((PAPER / "kappa_prediction.json").read_text())
    census = json.loads((PAPER / SOURCES[4]).read_text())
    forecast = json.loads((ROOT / FORECAST).read_text())["cohorts"]["ants"]
    source = (PAPER / "main.typ").read_text().split('[Key results]', 1)[1].split('= The cube-root', 1)[0]
    titles = re.findall(r"^  - \*([^*]+)\*", source, re.M)
    assert len(titles) == 9, "Review homepage coverage when paper key results change"
    walkers = list(csv.DictReader(io.StringIO((PAPER / SOURCES[5]).read_text())))
    groups = []
    for name, window in (("rw", "k12-22"), ("rotor", "k20-26")):
        rows = [r for r in walkers if r["walker"] == name and r["window_set"] == window]
        assert len(rows) == 8
        groups.append({"label": "Random walk" if name == "rw" else "Rotor",
                       "raw": sum(float(r["kappa"]) for r in rows) / len(rows),
                       "ratio": sum(float(r["ratio"]) for r in rows) / len(rows)})
    sizes = {}
    for name, src in image_sources.items():
        width, height = struct.unpack(">II", src.read_bytes()[16:24])
        sizes[name] = {"width": width, "height": height}
    data = {"titles": titles, "images": sizes, "blob_count": n["probe"]["blob"], "exponent": round(n["alpha_w_blob"][0], 4),
            "profile_difference_pct": round(100 * n["shape"]["max_rel_diff_ants_rotor_shells0_9"]),
            "log_count": n["probe"]["log"], "fast_count": n["probe"]["fast"],
            "law": rf["c_law"]["C1"], "broad_r2": rf["edge"]["V"]["lead"]["r2"],
            "prefix_r2": kp["prefix_r2"], "conditioning": rf["conditioning"]["4a"],
            "ant_ratio": census["kappa_ratio_stationary_blob"]["median"],
            "ant_raw": None,
            "walkers": groups, "forecast_reduction_pct": round(100 * forecast["reduction"], 1),
            "forecast_rules": forecast["rules"], "onset_billions": round(n["g1"]["onset_t"] / 1e9, 1),
            "sweeper": sweeper(*portrait),
            "provenance": {"revision": git("log", "-1", "--format=%H", "--", *paths),
                           "command": "uv run --frozen --only-group blog blog/scripts/export_results.py",
                           "sha256": {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}}
    # The saved census-spread summary, not a different core cohort, supplies the
    # stationary-blob median used for the raw/normalized display.
    spread = ROOT / "experiments/2026-10-16-kappa-uniform-baseline/results/census_spread.txt"
    line = next(l for l in spread.read_text().splitlines() if l.startswith("kappa, stationary"))
    data["ant_raw"] = float(re.search(r"\[([^\]]+)\]", line)[1].split(",")[2])
    assert not git("status", "--porcelain", "--", str(spread.relative_to(ROOT)))
    data["provenance"]["sha256"][spread.relative_to(ROOT).as_posix()] = hashlib.sha256(spread.read_bytes()).hexdigest()
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    targets = {OUT: text.encode()}
    targets.update({ROOT / f"blog/assets/results/{p}.png": src.read_bytes() for p, src in image_sources.items()})
    for path, content in targets.items():
        if "--check" in sys.argv:
            if not path.exists() or path.read_bytes() != content:
                raise SystemExit(f"Stale homepage asset: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    print(f"Homepage results {'checked' if '--check' in sys.argv else 'exported'}: {len(titles)} cards, {len(image_sources)} figures")


if __name__ == "__main__":
    export()
