"""Plot the frozen independent-seed associations from small summary results."""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def main():
    source = EXP / "results/rule_summary.csv"
    result_path = EXP / "results/analysis.json"
    with source.open() as f:
        rows = [r for r in csv.DictReader(f) if r["run"] == "prod16"]
    result = json.loads(result_path.read_text())["prod16"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True)
    for band, ax in enumerate(axes):
        keyed = {(r["rule"], r["group"]): r for r in rows if int(r["band"]) == band}
        rules = sorted({r for r, g in keyed})
        for a, b, color in [("A", "C", "#156e9a"), ("B", "D", "#cb6a35")]:
            ax.scatter([float(keyed[r, a]["ln_q999"]) for r in rules],
                       [float(keyed[r, b]["lnk_time"]) for r in rules],
                       s=23, alpha=0.7, color=color, label=f"tail {a}, outcome {b}")
        p1 = result[f"band{band}"]["P1"]
        ax.set_title(f"Area {32768 if band == 0 else 131072:,}\nmean rho = {p1['statistic']:.3f}")
        ax.set_xlabel("ln pooled interior q99.9 (steps)")
        ax.grid(alpha=0.18)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("mean ln kappa_time (independent seeds)")
    axes[1].legend(frameon=False, fontsize=8)
    fig.suptitle("Fixed area: independent-seed tail cutoff and boundary activity", fontsize=12)
    fig.tight_layout()
    fig.savefig(EXP / "results/association.png", dpi=150)
    plt.close(fig)
    provenance = {"command": "uv run experiments/archive/2026-10-fixed-area-cycles/scripts/figures.py",
                  "inputs": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [source, result_path]},
                  "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  "scope": "primary only; 44 rules x two rotations per panel, not 88 independent rules"}
    (EXP / "results/association.json").write_text(json.dumps(provenance, indent=2) + "\n")


if __name__ == "__main__":
    main()
