# /// script
# dependencies = ["nbformat"]
# ///
"""Builds notebook.ipynb (execute: see experiments/README.md). usage: uv run experiments/archive/2026-10-lattice-c-law/scripts/build_notebook.py"""
from pathlib import Path

import nbformat as nbf

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# Does the c law survive a change of lattice? Hexagonal and triangular ants

## Question
On the square lattice `1/c = 1.36 + 0.70 lead` (c = births per boundary step, lead = opening same-letter run). Is the slope a property of the 2x2 loop, of the lattice
coordination, or of neither? Three hypotheses were registered before any lattice c existed (README): **A** b scales with loop length, **B** b is lattice-independent,
**C** b follows 4/z. Secondary: is the kappa deficit (ants at ~0.8 of the uniform reference) square-specific?

## Assumptions and definitions
Generic octave-window probe on square / hex / triangular lattices (`src/lattice_probe.rs`); boundary step, birth, perimeter as `src/probe.rs`; kappa ratio = kappa / kappa_unif(a, beta)
with the run's own a, beta (k = 20..26). Instrument gates G1-G3 (`cargo test --release --test lattice_probe`) **passed**; G4 (mean-field walker) and G5 (square c law) are checked below."""),
code("""import hashlib, json, subprocess
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
R = ROOT / "experiments/archive/2026-10-lattice-c-law/results"
for n in ["ants.csv", "controls.csv", "analysis.json", "analysis.txt", "explore.txt", "run.log"]:
    print(hashlib.sha256((R / n).read_bytes()).hexdigest()[:16], n)
print("git", subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip() or "unresolvable here; see README (instrument adf6677)")
A = json.loads((R / "analysis.json").read_text())"""),
md("## Results\n### Gates and the c law per stratum (registered fit)"),
code("""k = A["kappa"]
print("G4 mean-field kappa ratio:", {l: round(k[l]["mf"]["ratio_mean"], 3) for l in k})
for key, f in A["fits"].items():
    print(f"{key:9s} n={f['n']:3d}  1/c = {f['a']:6.2f} + {f['b']:5.2f} lead   b 95% CI [{f['b_ci'][0]:.2f}, {f['b_ci'][1]:.2f}]  R2 {f['r2']:.2f}")
print("retention (kept per lead 1..5):", {key: v["kept"] for key, v in A["retention"].items()})
print("decision rule verdict:", A["verdict"])"""),
md("""Square reproduces the census (G5 passes). Triangular b is half the square's, with a tight interval. The hex r-lead fit is corrupted by one rule with 1/c = 390 that passed the frozen filters; the registered decision rule returns **undecided**.
It does **not** show a mechanism for b. The next cell is post hoc and unregistered."""),
code("""print((R / "explore.txt").read_text())"""),
md("""Per-lead medians give b of about 0.86 (hex R, loop 3), 0.70 (square, loop 4), 0.34 (triangular, loop 6) and 0.27 (hex r, loop 6): **b falls as the loop gets longer**, opposite to H-A.
All three registered hypotheses are disproven as stated: triangular alone is at least 0.33 away from each vector. A line `b ~ 1.5 - 0.2 l` fits but has two parameters for four points chosen after the fact."""),
md("### Kappa"),
code("""for l, v in k.items():
    print(f"{l:6s} ants median ratio {v['ants_median']:.3f} (n={v['ants_n']}, IQR {v['ants_q'][1]:.2f}-{v['ants_q'][2]:.2f})   random walk {v['rw']['ratio_mean']:.2f}   mean-field {v['mf']['ratio_mean']:.3f}")
print("K3 slopes of ln kappa on lead:", {a: round(b, 3) for a, b in A["k3"].items()})"""),
md("""The deficit is not square-specific: all three lattices have ant medians of 0.74-0.86 with a mean-field reference at 1.00 and memoryless walkers at 1.3-1.4 (random-walk window k = 16..22). It does not explain the deficit.

## Caveats
- Single deterministic run per rule; survivor selection (e.g. square lead 2 keeps 18 of 36 alive); `alpha_w` is a proxy for the census `blob` class.
- Hex has four letters; letters after the lead are not separated by type. Triangular loops enclose a vertex, so "loop length" may not be the variable that matters.
- Failed registered predictions: L1 (outlier), L2, K4. Deviations: 2^27 steps, no gyration fields, random walk window.

## Next
Register b(l) and a letter-typed hex lead before using a new loop length; derive why b falls with l; check whether the intercept (1.3 square/triangular, ~2.5 hex) tracks coordination."""),
]
nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
Path(__file__).resolve().parents[1].joinpath("notebook.ipynb").write_text(nbf.writes(nb))
