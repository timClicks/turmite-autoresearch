"""Build the feasibility report and shareable notebook from compact results."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[4]
EXP=Path(__file__).resolve().parents[1]
age=EXP.name.endswith("field-age")
s=json.loads((EXP/"results/pilot_summary.json").read_text())
c=json.loads((EXP/"results/calibration.json").read_text())
d=json.loads((EXP/"results/determinism.json").read_text())
m=json.loads((EXP/"results/pilot-v2.manifest.json").read_text())
g=s["run_gates"]
lines=["# Instrument feasibility results", "", "This report supersedes the scaffold's NOT RUN status. Scientific confirmation has **not** run.", "",
       f"Frozen pilot: {s['requested_rules']} rules x {s['seeds_per_rule']} starts, three area bands; cap 2^30, grid 4096, four workers. Base commit `{m['git_commit']}`; dirty source hashes and seed identities are in [manifest](pilot-v2.manifest.json).", "",
       "| Band start | Completed / requested | Unresolved interior time | Minimum completed entry episodes |", "|---|---:|---:|---:|"]
for b in s["bands"]:
    lines.append(f"| {b['lo']} | {b['completed']} / {b['requested']} | {b['unresolved_overlap']} | {b['min_completed_entry_episodes']} |")
lines += ["", f"No-escape gate: **{g['no_escape']}**. All-complete gate: **{g['all_complete']}**. Quarter-cap reserve gate: **{g['quarter_cap_reserve']}** (max final step {g['max_t']:,}). Ant batch wall time {g['elapsed_seconds']:.1f} s; measured whole-process peak RSS {max(s['peak_process_rss_kib'])/1024:.1f} MiB (four concurrent jobs).", "",
          "## Instrument validation", "", "Four reference/property tests check discovery times, exact departure counts, nonzero patch phase offsets, visited-boundary rim census, offline fragment accounting, follow-up past band edges, right censoring, and rotor/random-walk paths. Full release tests passed; see the tail-budget results/instrument-release-tests.log.", "",
          f"Sampled thread replay: **{d['passed']}**, {len(d['specs'])} specs and {d['files_compared']} files, one versus six workers at the two profile bands. Finished-trajectory resume preserves bytes. Full all-seed replay and mid-trajectory state checkpoints are **not** validated.", ""]
if age:
    support=s["cohort_audit"]
    lines += [f"Existing pool support before matching: {support['counts']['stationary']} stationary and {support['counts']['drifting']} drifting rules. The latter is below the required 24 even without matching; exact length/prefix matching retains {support['exact_length_prefix3_pairs']} pairs. See cohort_audit.json.", ""]
    lines += ["## Coverage by pre-existing stratum", "", "| Stratum | Area 32768 | Area 131072 | Area 524288 |", "|---|---:|---:|---:|"]
    for label in ["stationary","drifting"]:
        vals=[b["by_stratum"][label] for b in s["bands"]]
        lines.append("| "+label+" | "+" | ".join(f"{v['completed']} / {v['requested']}" for v in vals)+" |")
    lines += [""]
    lines += [f"Synthetic exogenous-age chain (N={c['N']:,}, seed {c['seed']}): known return-hazard contrast {c['known_contrast']:.2f}, estimated {c['planted']['contrast']:.6f}; after within-stratum label permutation {c['permuted']['contrast']:.6f}. Both four-standard-error calibration checks pass. This calibrates transition-frequency estimation, not a kappa model or a physical ageing intervention.", "",
              f"**Original cohort feasibility gate failed:** {s['original_age_cohort_gate']}. The pilot uses the 44 supported rules (22 exact length/prefix-matched pairs). This does not silently replace the planned 48-rule confirmation cohort.", ""]
else:
    lines += ["Known-answer renewal calibration uses 16 independent seeds per law, 20,000 cycles per seed. Mean interior durations (mean +/- between-seed sd; known mean):", ""]
    for family,v in c["families"].items():
        lines.append(f"- {family}: {v['mean']:.6f} +/- {v['between_seed_sd']:.6f}; known {v['known']:.6f}; bias {v['bias']:+.6f}.")
    lines += ["", "All three predeclared four-standard-error Monte Carlo checks pass. These calibrate the actual episode accountant, including a serially correlated mixture, not a fitted survival family.", ""]
if s.get("noncomplete_trajectories"):
    lines += ["## Noncomplete trajectories", "", "These remain in every coverage denominator; missing-band features are null, not zero effects.", ""]
    for run in s["noncomplete_trajectories"]:
        st=run["status"]
        lines.append(f"- `{run['spec']}`: {st['stop']}, final step {st['t_final']}, visited cells {st['cells']}.")
    lines += [""]
lines += ["## Split-seed feature reliability (descriptive)", "", "Spearman correlation across rules between first two and last two pilot seeds, restricted to rules with all four starts attaining the band and the feature observed. Contributing rule counts are shown in parentheses. No bootstrap inference is made; coverage denominators retain every requested start. The CSV includes every seed and between-seed dispersion is in the summary JSON.", "",
          "| Feature | Area 32768 | Area 131072 | Area 524288 |", "|---|---:|---:|---:|"]
labels=["immature","median_log_age","cycle_variance"] if age else ["entry_mean","tail_probability_64","tail_mean_64"]
for label in labels:
    vals=[b["split_seed_reliability"][label] for b in s["bands"]]
    lines.append("| "+label+" | "+" | ".join("missing" if v["spearman_two_seed_halves"] is None else f"{v['spearman_two_seed_halves']:.3f} ({v['rules']})" for v in vals)+" |")
lines += ["", "## Meaning and remaining work", "", "These results establish observation/accounting feasibility at the measured scales and describe repeatability. They do not test T1/T2 or A1/A2/A3, compare tail or age features with kappa, establish causal mechanisms, or calibrate a survival-family fit or drift forecast.", "",
          "Confirmation remains unregistered and unlaunched. Before confirmation: implement and byte-test mid-trajectory state checkpoints; calibrate/freeze the survival family and predictor loss; freeze grouped rule folds and seed roles; resolve the failed age cohort support gate explicitly; choose seed counts using pilot feature reliability. Retain the original thresholds and report deviations prospectively. No successful scientific prediction is claimed.", "",
          "## Reproduce", "", "Use WSL from the repo root with `export UV_PROJECT_ENVIRONMENT=$HOME/.venvs/turmite UV_LINK_MODE=copy`. Source-hash guards reject changes to registered inputs; retain old manifests and use a new run label for changed sources.", "", "```bash",
          "cargo build --release --example kappa_tail_budget_sampler --example kappa_field_age_sampler --example kappa_tail_budget_calibrate",
          f"uv run {Path(__file__).with_name('calibrate.py').relative_to(ROOT)}",
          f"uv run {Path(__file__).with_name('run.py').relative_to(ROOT)} --name pilot-v2",
          f"uv run {Path(__file__).with_name('summarize.py').relative_to(ROOT)}",
          f"uv run {Path(__file__).with_name('verify.py').relative_to(ROOT)}",
          f"uv run {Path(__file__).relative_to(ROOT)}", "cargo test --release", "```", "",
          "The pilot itself is frozen prospectively in pilot-v2.manifest.json. Its exact preparation command is recorded there. pilot-v1 was rejected before simulation because an unrelated module export changed src/lib.rs; its manifest and failure log are retained.", ""]
(EXP/"results/REPORT.md").write_text("\n".join(lines))

def md(text):return {"cell_type":"markdown","metadata":{},"source":text.splitlines(keepends=True)}
def code(text):return {"cell_type":"code","metadata":{},"source":text.splitlines(keepends=True),"outputs":[],"execution_count":None}
rel=str(EXP.relative_to(ROOT))
cells=[md(f"# {'Field age' if age else 'Tail budget'}: instrument feasibility\n\n## Question and why it matters\nDoes field maturation explain return hazards?" if age else "# Tail budget: instrument feasibility\n\n## Question and why it matters\nDoes a transferable interior survival law explain boundary occupation?"),
       md("This notebook reports instrument calibration and a prospective feasibility pilot. Scientific confirmation is not run. See [README](README.md) and [mechanism note](../../../notes/kappa-mechanisms-2026-10-15.md)."),
       md("## Assumptions and definitions\nDiscovery includes first arrival; visit count means departures, including from the initial patch. Phase is (initial colour + departures) mod rule length. Completed cycles are floor(departures/n), without inventing prehistory for initial patch colours. The visited boundary includes hole edges; rim depth 0..4 is graph distance to that boundary. Census features weight cells; hazard tables weight departures. Exact fixture/property checks support these definitions. Return-hazard estimates remain observational."),
       md("## Provenance\nAll inputs below are small results intended for version control; this session makes no commit. The notebook never reads dumps or runs simulation. Seed identities are printed from the frozen manifest."),
       code(f'''from pathlib import Path
import hashlib, json, csv
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "Cargo.toml").is_file() and (p / "experiments").is_dir())
EXP = ROOT / "{rel}"
inputs = ["pilot-v2.manifest.json", "pilot_summary.json", "pilot_features.csv", "calibration.json", "determinism.json", "REPORT.md"] + (["cohort_audit.json"] if EXP.name.endswith("field-age") else [])
for name in inputs:
    path = EXP / "results" / name
    assert path.is_file(), path
    print(name, hashlib.sha256(path.read_bytes()).hexdigest())
manifest = json.loads((EXP / "results/pilot-v2.manifest.json").read_text())
print("Simulation base commit:", manifest["git_commit"])
print("Registered UTC:", manifest["recorded_utc"])
print("Pilot seeds:", manifest["config"]["seeds"])
SEED = manifest["config"]["seeds"][0]
'''),
       md("## Data and method\nThe Rust observation driver preserves the original walker and feeds the tested fixed-area accountant. Interior episodes intersecting a band are followed beyond its end; full durations and in-band overlap have separate columns. An unresolved return has no assumed finite upper bound. Birth, midpoint and endpoint censuses enumerate the visited rim. Heavy computation lives in the example binary and scripts/pilot.py. Matching and all seeds were fixed before new ant outcomes."),
       md("## Results\n"+"\n".join(lines[4:]).replace("](pilot-v2.manifest.json)", "](results/pilot-v2.manifest.json)")),
       code('''summary = json.loads((EXP / "results/pilot_summary.json").read_text())
print("Run gates:", json.dumps(summary["run_gates"], indent=2))
for b in summary["bands"]:
    print("Area", b["lo"], "completed", b["completed"], "/", b["requested"],
          "unresolved in-band I steps", b["unresolved_overlap"])
print("Scientific verdict:", summary["scientific_verdict"])
'''),
       md("The tables show instrument coverage and repeatability at these scales. They do not show that either mechanism predicts independent-seed kappa.\n\n## Caveats and controls\nRotor and random walk are path/accounting controls at smaller areas, not a universal kappa calibration. Synthetic hazard labels are exogenous; label permutation is not a physical field intervention. Full state checkpoints and a frozen scientific estimator remain missing. The original age cohort matching gate failed.\n\n## What this changes / next steps\nObservation-only pilots are now feasible with measured resource cost. Freeze the estimator and resolve the cohort and checkpoint requirements before confirmation.\n\n## Open questions\nDoes tail probability or conditional tail mean transfer independently? Do cell-weighted age features add predictive value beyond elapsed time, geometry, and prefix on held-out rules?")]
for i, cell in enumerate(cells):cell["id"] = f"cell-{i:02d}"
notebook={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.12"}},"nbformat":4,"nbformat_minor":5}
(EXP/"notebook.ipynb").write_text(json.dumps(notebook,indent=1)+"\n")
print(EXP/"results/REPORT.md")
