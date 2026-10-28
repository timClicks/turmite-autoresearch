"""Build notebook.ipynb (reads only committed results/; run it with nbconvert to execute)."""
from pathlib import Path
import nbformat as nbf
EXP = Path(__file__).resolve().parents[1]
md, code = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
cells = [
md("""# Do rim/interior "gates" explain boundary occupation of generalised Langton's ants?

**For a colleague who has not seen this work.** Rules are strings over {L,R}; the walker's *boundary occupation* is the share of
steps spent on a visited cell with an unvisited neighbour. Earlier experiments (see `notes/kappa-mechanisms-2026-10-15.md`)
could not explain how this varies across rules. Hypothesis tested here: a few directional crossings between the active rim
(visited depth <= 4 from the boundary) and the interior carry the information. **Stage 1** asks whether two gate summaries
improve held-out prediction over a baseline. Stage 2 (interventions) was *not* attempted.

**Answer in one line:** no improvement at either area band, but the verdict is *UNINFORMATIVE*: the baseline already explains
88-95% of the variance (no headroom at band 1) and one gate feature was unreliable at band 0."""),
md("""## Assumptions and design (frozen before the confirmation run; full text in README.md, 'REGISTRATION')
- 24 rules, 6 per {crust, uniform} x {stationary, nonstationary} cell, from existing labels; fresh random-patch starts.
- Window: departures with visited area in [A, A + A/16), A = 32768 and 131072. Predictor seeds (64/rule) and target seeds (32/rule) are disjoint.
- Target: ln(boundary steps / steps) from target seeds. Baseline B0: 4 features from predictor seeds that exclude boundary occupancy itself.
- Gate features: g1 = excess concentration of crossings in a few (tile, heading, kind) bins vs an exposure-matched Poisson null; g2 = spread over exit headings of ln mean excursion length.
- Ridge (lambda 1), leave-one-rule-out; pass = DeltaR2 >= 0.10, bootstrap lower bound > 0, permutation p <= 0.05, at both bands; gates: coverage, split-seed reliability >= 0.7, headroom R2(B0) <= 0.90."""),
code("""import json, hashlib, subprocess
from pathlib import Path
import polars as pl
EXP = Path.cwd()
while not (EXP / 'results').is_dir() and EXP != EXP.parent.parent:
    EXP = EXP.parent.parent if (EXP / 'README.md').exists() is False else EXP
R = EXP / 'results'
if not R.is_dir():
    R = Path('experiments/archive/2026-10-kappa-return-gates/results')
files = ['cohort.csv','pilot_runs.csv','confirm_runs.csv','confirm_analysis.json','pilot_analysis.json','controls_analysis.json','g1_null_calibration.json','determinism.json','sensitivity_g1_nan.json']
prov = {f: hashlib.sha256((R/f).read_bytes()).hexdigest()[:16] for f in files}
conf = json.loads((R/'confirm_analysis.json').read_text())
print('analysis commit (base, dirty tree):', conf['provenance']['git_commit'])
print(json.dumps(prov, indent=1))"""),
md("## Provenance and instrument checks"),
code("""print('determinism:', json.loads((R/'determinism.json').read_text()))
print((R/'return_gates_tests.log').read_text().strip())
cal = json.loads((R/'g1_null_calibration.json').read_text())
print(pl.DataFrame(cal['rows']))"""),
md("""The incremental depth map agrees with a from-scratch BFS oracle on random rules (property test), 1 and 6 threads give identical bytes, and an interrupted run resumes to identical bytes. The gate-concentration null is unbiased on synthetic uniform flow but has weak power in the sparse regime (30 bins, 400 events) that real runs partly occupy."""),
md("## Cohort"),
code("print(pl.read_csv(R/'cohort.csv').select('base','crust','stationary','c','g_k'))"),
md("## Pilot (8 seeds/rule): reliability and the seed-count rule"),
code("""p = json.loads((R/'pilot_analysis.json').read_text())
rows = [dict(band=b, feature=f, split_half_spearman_4v4=p['bands'][b][f]['split_half_spearman_4v4'], projected_64=p['bands'][b][f]['projected']['64']) for b in ('0','1') for f in ('g1','g2','y')]
print(pl.DataFrame(rows)); print('S_pred =', p['S_pred'])"""),
md("## Confirmation: the registered test"),
code("""rows = []
for b, r in conf['bands'].items():
    rows.append(dict(band=int(b), rules=r['n_rules_evaluable'], R2_B0=r['r2_baseline'], R2_with_gates=r['r2_with_gates'], dR2=r['delta_r2'], ci_lo=r['delta_ci95'][0], ci_hi=r['delta_ci95'][1], perm_p=r['permutation_p'], rel_g1=r['reliability']['g1']['split_half_spearman'], rel_g2=r['reliability']['g2']['split_half_spearman']))
print(pl.DataFrame(rows)); print(conf['gates']); print(conf['verdict'])"""),
md("""**Reading.** DeltaR2 is zero or negative with upper bounds (+0.006, +0.031) far below the +0.10 criterion, so the prediction is not supported.
But the test is mostly decided by the baseline (R2 0.88 and 0.95), and g2 at band 0 fails its reliability gate, so this is an
uninformative rather than a clean rejection. It does **not** show gates are causally irrelevant."""),
md("## Exploratory checks (not gating)"),
code("""for b, r in conf['bands'].items():
    print('band', b, r['exploratory'])
s = json.loads((R/'sensitivity_g1_nan.json').read_text())
print('sensitivity (3 NaN-g1 runs ignored, 24 rules at band 0):', {k: s['0'][k] for k in ('n_rules_evaluable','delta_r2','delta_ci95','permutation_p')})
print(pl.DataFrame(json.loads((R/'controls_analysis.json').read_text())).select('walker','band','g1_mean','boundary_occupancy_mean','hole_boundary_fraction'))"""),
md("""## Caveats
n = 24 rules; labels come from earlier pooled summaries; bootstrap omits training-fold uncertainty; g1's absolute level is not
interpretable (rotor and random walk give -0.04 / -0.01 rather than 0); colour phase and other tile/depth choices were not tested;
three runs had a NaN null (reported, registered result unchanged). The depth-profile baseline is close to an accounting identity
with the target, which is why headroom vanished.

## Next steps
Re-test gates only against a baseline built from quantities that precede the window or from independent mechanism features;
keep the permutation criterion. G2 (matched gate vs non-gate edits from forked snapshots) needs its own registration and is
unrun. See `notes/open-questions-hypotheses.md`."""),
]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}})
nbf.write(nb, EXP / "notebook.ipynb")
