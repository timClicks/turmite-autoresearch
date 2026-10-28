# /// script
# dependencies = ["nbformat", "nbclient"]
# ///
"""Builds and executes notebook.ipynb for 2026-10-lattice-c-law-colours.
Usage: uv run experiments/archive/2026-10-lattice-c-law-colours/scripts/build_notebook.py
"""
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell

cells = [
    md("""# Where does the lead slope live? Circulations vs boundary reads by colour

## Question
On the square lattice, $1/c = 1.36 + 0.70 \\times \\text{lead}$. Off the square lattice, the slope $b$ falls with the loop length $\\ell$ that the lead letter closes:
0.86 (hex R, $\\ell=3$), 0.70 (square, 4), 0.34 (triangular, 6), 0.28 (hex r, 6).
The first-principles reading $b = \\ell_b / N_b$ (boundary cells per lap over births per circulation episode) had never been measured.
This experiment measures the two factors of $b$ and tests whether circulation frequency carries the drop across lattices.

## Assumptions and definitions
- Everything as in `experiments/archive/2026-10-lattice-c-law` (octave window $k=26$, steps $(2^{26}, 2^{27}]$).
- **Return**: a step starting on a cell last read exactly $\\ell$ steps earlier (square 4, triangular 6, hex r 6, hex R 3).
- **Circulation**: maximal run of consecutive returns of length $\\ge \\ell$.
  - $\\epsilon$: circulations per birth
  - $R$: mean run length of circulations (capped at 63)
  - $C$: total steps in circulation runs per birth ($= \\epsilon R$)
  - $C_b$: boundary steps in circulation runs per birth
- Gates: **T2** requires births and boundary steps to match parent `ants.csv` exactly, with $\\sum_k \\text{edge}_k = \\text{boundary steps}$."""),

    code("""import hashlib, json, subprocess
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "AGENTS.md").exists())
R = ROOT / "experiments/archive/2026-10-lattice-c-law-colours/results"
for n in ["traces.jsonl", "analysis.json", "analysis.txt", "explore.txt", "run.log"]:
    print(hashlib.sha256((R / n).read_bytes()).hexdigest()[:16], n)
git_rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
print("git", git_rev or "unresolvable")
A = json.loads((R / "analysis.json").read_text())"""),

    md("""## Results
### Gate T2 and Registered Predictions (P1–P6)"""),

    code("""# Summary of registered predictions and outcomes
for stratum, data in A.items():
    print(f"=== {stratum} (ell={data['ell']}) ===")
    print(f"  inv_c medians: {[round(x, 3) for x in data['inv_c_meds']]}")
    print(f"  Cb medians:    {[round(x, 3) for x in data['Cb_meds']]}")
    print(f"  C medians:     {[round(x, 1) for x in data['C_meds']]}")
    print(f"  b_med: {data['b_med']:.3f} | Theil-Sen b: {data['b_ts']:.3f} | Cb slope: {data['Cb_slope']:.3f} | R slope: {data['R_slope']:.3f} (R slope/ell: {data['R_slope']/data['ell']:.3f})")
    print(f"  eps(lead 3): {data['eps3']:.2f}")"""),

    md("""### Why P3 is not evidence
The registered discriminator P3 (comparing $\\epsilon$ across lattices) appeared to pass formally with huge ratios (7.2 and 75).
However, the circulation definition counted interior returns as well as boundary returns.
$C$ (steps in circulation runs) is 30–120 per birth on the square lattice while $1/c$ is only 2–5!
Interior loops completely swamped the boundary episodes.
The boundary-only version $C_b$ carries only 17–42% of the slope ($C_b$ slope / $b_{\\text{med}} = 0.42$ square, $0.19$ tri, $0.29$ hex R, $0.17$ hex r), so P1 failed.
The circulation-lap decomposition $b = \\ell_b / N_b$ was therefore **not validly measured** by this instrument.

### Post hoc: Where does the slope live? By colour!"""),

    code("""# Post hoc decomposition of boundary reads by colour group
print((R / "explore.txt").read_text())"""),

    md("""## Interpretation
1. **The lead slope lives in circulating colours (1..m-1)**:
   - Hex R (loop 3): ~0.95 boundary reads added per lead colour.
   - Square (loop 4): ~0.80 boundary reads added per lead colour.
   - Triangular (loop 6): ~0.65 to 0.35 boundary reads added per lead colour.
   - Hex r (loop 6): ~0.69 to 0.47 boundary reads added per lead colour.
2. **Cancellation by killing and later colours**:
   The slope of reads at the killing colour and later colours is negative (-0.05 to -0.31), pulling down the net slope $b$.
3. **Lag-$\\ell$ ring returns do not generalize off the square lattice**:
   On the square lattice, 66–87% of circulating reads return after exactly 4 steps.
   On triangular and hexagonal lattices, lag-$\\ell$ share is small (5–44%). The "2x2 ring loop" picture is square-specific.
4. **Hex r rules fill ring centres**:
   15% of lead-1 births on hex r land in cells whose neighbours are all visited (hole births), dropping to 6% at lead 5. Hex R and square sit at 1–2%.

## Caveats and Limitations
- The registered circulation estimator was corrupted by interior loops; passing P3 is an artefact.
- Post hoc colour decomposition restates the identity $1/c = E[N_b]$ and shows *where* the slope lives, but does not yet supply a dynamic mechanism for the plateau survival probability.
- Survivorship selection: kept rules filter out blob/lacy rules, which differ across lattices.

## Next steps
1. Segment boundary-only episodes (runs of consecutive boundary reads of colours 1..m-1) to isolate genuine boundary revisits.
2. Model the per-colour boundary survival plateau as a function of local geometry (e.g. outside unvisited neighbours)."""),
]

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
out_path = Path(__file__).resolve().parents[1] / "notebook.ipynb"

# Execute notebook to capture outputs
client = NotebookClient(nb, timeout=60, kernel_name="python3")
executed_nb = client.execute()
out_path.write_text(nbf.writes(executed_nb), encoding="utf-8")
print(f"Wrote executed notebook to {out_path}")
