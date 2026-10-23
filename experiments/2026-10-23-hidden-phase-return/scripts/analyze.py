"""Analyse the frozen pilot; replicas are not independent starts."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
RULES = ["RLLLLRLLRLRL", "RLLLRRLRLL", "RLLRRLLLLLLL"]
SEEDS = list(range(2026102301, 2026102305))


def load_results():
    rows, audit, hashes = [], [], {}
    for rule in RULES:
        for seed in SEEDS:
            for suffix, target in [(".csv", rows), (".audit.csv", audit)]:
                path = HERE / "results" / f"{rule}_{seed}{suffix}"
                hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
                with path.open() as stream:
                    target.extend(csv.DictReader(stream))
    return rows, audit, hashes


def analyse():
    rows, audit, hashes = load_results()
    groups = defaultdict(list)
    for row in rows:
        groups[row["rule"], int(row["band"]), int(row["k"]), int(row["seed"])].append(row)

    starts = []
    for (rule, band, k, seed), data in sorted(groups.items()):
        by_departure = defaultdict(list)
        for row in data:
            by_departure[int(row["departure"])].append(row)
        assert all(len(rep) == 4 for rep in by_departure.values())
        logs = np.array([np.log2(int(r["arm_t"]) / int(r["base_t"])) for r in data])
        starts.append(dict(rule=rule, band=band, k=k, seed=seed,
            departures=len(by_departure), effect=float(np.abs(logs).mean()),
            signed=float(logs.mean()), factor_two=float((np.abs(logs) >= 1).mean()),
            path_equal=float(np.mean([int(r["path_equal"]) for r in data])),
            return_equal=float(np.mean([int(r["return_equal"]) for r in data])),
            censored=sum(int(r["censored"]) for r in data), replicas=len(data),
            read_changed=float(np.mean([int(r["read_changed"]) / int(r["read_cells"]) for r in data]))))

    rng = np.random.default_rng(2026102300)
    cells = []
    for rule in RULES:
        for band in [0, 1]:
            arms = {}
            for k in [0, 1, 2, 4, len(rule)]:
                data = [s for s in starts if (s["rule"], s["band"], s["k"]) == (rule, band, k)]
                effects = np.array([s["effect"] for s in data])
                arms[k] = dict(k=k, starts=len(data), effect=float(effects.mean()) if len(data) else None,
                    seed_sd=float(effects.std(ddof=1)) if len(data) > 1 else None,
                    signed=float(np.mean([s["signed"] for s in data])) if data else None,
                    factor_two=float(np.mean([s["factor_two"] for s in data])) if data else None,
                    return_equal=float(np.mean([s["return_equal"] for s in data])) if data else None,
                    path_equal=float(np.mean([s["path_equal"] for s in data])) if data else None,
                    censored=sum(s["censored"] for s in data), replicas=sum(s["replicas"] for s in data))

            zero = {s["seed"]: s["effect"] for s in starts if (s["rule"], s["band"], s["k"]) == (rule, band, 0)}
            one = {s["seed"]: s["effect"] for s in starts if (s["rule"], s["band"], s["k"]) == (rule, band, 1)}
            paired = sorted(zero.keys() & one.keys())
            ratio = None
            interval = None
            if paired and sum(zero[s] for s in paired) > 0:
                a, b = np.array([zero[s] for s in paired]), np.array([one[s] for s in paired])
                ratio = float(b.mean() / a.mean())
                draws = rng.integers(0, len(paired), size=(10000, len(paired)))
                denominators = a[draws].mean(axis=1)
                if np.all(denominators > 0):
                    interval = np.quantile(b[draws].mean(axis=1) / denominators, [.025, .975]).tolist()

            exposed = [int(r["read_changed"]) / int(r["read_cells"]) for r in rows
                       if (r["rule"], int(r["band"]), int(r["k"])) == (rule, band, 1)]
            cells.append(dict(rule=rule, band=band, arms=arms, ratio=ratio, ratio_interval=interval,
                median_read_changed=float(np.median(exposed)) if exposed else None,
                threshold_met=ratio is not None and ratio >= .5 and arms[1]["effect"] >= .5))

    total = {name: sum(int(a[name]) for a in audit) for name in ["departures", "short", "eligible_long", "overflow", "sampled", "gap_or_quota", "unfinished", "completed_time", "overflow_time", "unfinished_time"]}
    for row in audit:
        assert int(row["departures"]) == sum(int(row[key]) for key in ["short", "eligible_long", "overflow", "unfinished"])
        assert int(row["eligible_long"]) == int(row["sampled"]) + int(row["gap_or_quota"])
    assert len(audit) == 24
    assert len(rows) == total["sampled"] * 20
    censoring = {}
    for k_label in ["0", "1", "2", "4", "n"]:
        data = [r for r in rows if (int(r["k"]) == len(r["rule"]) if k_label == "n" else r["k"] == k_label)]
        censoring[k_label] = dict(censored=sum(int(r["censored"]) for r in data), n=len(data))
    gates = {
        "all_starts_complete": all(a["status"] == "complete" for a in audit),
        "eight_departures_each": all(int(a["sampled"]) >= 8 for a in audit),
        "baseline_censoring_below_one_percent": (total["overflow"] + total["unfinished"]) < .01 * total["departures"],
        "each_arm_censoring_at_most_one_percent": all(c["n"] and c["censored"] <= .01 * c["n"] for c in censoring.values()),
        "turn_map_edit_support": all(c["median_read_changed"] is not None and c["median_read_changed"] >= .1 for c in cells),
        "equivalent_phase_sham": all(int(r["path_equal"]) == 1 and int(r["censored"]) == 0 for r in rows if int(r["k"]) == len(r["rule"])),
        "prefix_guarantee": all(int(r["split_step"]) == 0 or int(r["split_visit"]) > int(r["k"]) for r in rows),
    }
    met = all(c["threshold_met"] for c in cells)
    map_met = all(c["ratio"] is not None and c["ratio"] <= .2 for c in cells)
    verdict = "H-clock pilot criterion met" if met else ("H-map pilot criterion met" if map_met else "mechanistic comparison unresolved")
    if not all(gates.values()):
        verdict = "gates failed; capped conditional effects only; " + verdict
    return dict(seed=2026102300, bootstrap_draws=10000, hashes=hashes, totals=total,
                censoring=censoring, gates=gates, cells=cells, starts=starts, audit=audit, verdict=verdict)


def write_outputs(result):
    (HERE / "results" / "analysis.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    lines = ["# Hidden-phase pilot results", "", result["verdict"], "",
             "Paired start bootstrap, four starts per rule; intervals do not measure between-rule uncertainty.", "",
             "| Rule | Area | k=0 effect | k=1 effect (seed SD) | Ratio [95% interval] | k=1 read edits | P1 cell |",
             "|---|---:|---:|---:|---:|---:|---|"]
    for c in result["cells"]:
        a, b = c["arms"][0], c["arms"][1]
        interval = c["ratio_interval"]
        ci = f"[{interval[0]:.3f}, {interval[1]:.3f}]" if interval else "unavailable"
        ratio = f'{c["ratio"]:.3f}' if c["ratio"] is not None else "unavailable"
        fmt = lambda value: f"{value:.3f}" if value is not None else "unavailable"
        lines.append(f'| {c["rule"]} | {[4096,16384][c["band"]]} | {fmt(a["effect"])} | {fmt(b["effect"])} ({fmt(b["seed_sd"])}) | {ratio} {ci} | {fmt(c["median_read_changed"])} | {c["threshold_met"]} |')
    lines += ["", "Effects are mean absolute log2 capped return-time ratios, with equal start weights.", "",
              "## Eligibility", "", "```json", json.dumps(result["totals"], indent=2), "```", "",
              "## Gates", "", "```json", json.dumps(result["gates"], indent=2), "```", "",
              "## Replay censoring", "", "```json", json.dumps(result["censoring"], indent=2), "```", "",
              "The first long departures are selected, not a random or time-representative sample.",
              "Capped effects do not estimate uncensored means. Sensitivity is not prediction or a growth mechanism."]
    (HERE / "results" / "summary.md").write_text("\n".join(lines) + "\n")


def figure(result):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    colours = ["#0072B2", "#D55E00", "#009E73"]
    for band, ax in enumerate(axes):
        for rule, colour in zip(RULES, colours):
            cell = next(c for c in result["cells"] if (c["rule"], c["band"]) == (rule, band))
            arms = [cell["arms"][k] for k in [0, 1, 2, 4, len(rule)]]
            ax.errorbar(range(5), [a["effect"] for a in arms], yerr=[a["seed_sd"] for a in arms],
                        marker="o", capsize=3, color=colour, label=rule)
        ax.set_xticks(range(5), ["0", "1", "2", "4", "all"])
        ax.set_xlabel("Future turns preserved at every cell")
        ax.set_title(f"Departure area {[4096,16384][band]:,}")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Mean |log₂(capped time / baseline time)|")
    axes[1].legend(fontsize=8)
    fig.suptitle("An unchanged next-turn map can hide a different return", fontsize=13)
    fig.text(.5, .01, "Selected long excursions; 4 starts/rule; bars: seed SD. Sensitivity, not an occupation forecast.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .04, 1, .96))
    fig.savefig(HERE / "results" / "phase_effect.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    result = analyse()
    write_outputs(result)
    figure(result)
    print(result["verdict"])
