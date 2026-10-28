"""Replace the initial NOT RUN notebook with a results-only, reproducible report.

Inputs are small results files; no raw simulations run inside the notebook.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EXP = Path(__file__).resolve().parents[1]


def main():
    # Require results before replacing the historical scaffold.
    result = json.loads((EXP / "results/analysis.json").read_text())
    cells = []

    def cell(kind, source):
        c = {"cell_type": kind, "id": f"fixed-area-results-{len(cells)}", "metadata": {},
             "source": source.strip().splitlines(True)}
        if kind == "code":
            c.update(execution_count=None, outputs=[])
        cells.append(c)

    cell("markdown", """
# Fixed-area cycles: registered confirmation

## Question and why it matters
Does the extreme interior-excursion tail predict boundary activity when visited
area is fixed by design? Does it add held-out information beyond boundary
residence and perimeter/area? See [registration and results](README.md),
[lab notebook](NOTEBOOK.md), and [research context](../../../notes/cutoff-research-avenues-2026-10-15.md).

## Assumptions and definitions
The selected 44-rule T1b cohort is not representative of all chaotic rules.
Patched starts use radius 2. State t follows t moves; B means the current visited
cell has an unvisited four-neighbour. Bands contain departures between first
hits of the registered areas. Boundary labels change with the visited region.
Quantiles pool complete-contained I episodes across 16 seeds; kappa_time is
boundary fraction divided by time-averaged P/A. Seed groups A/B predict C/D
in the primary test. Reliability is checked rather than assumed.
""")
    cell("markdown", "## Provenance\nAll inputs below are small files under results/. No dumps are read. Files are currently uncommitted; commit only on user request.")
    cell("code", """
from pathlib import Path
import csv, datetime, hashlib, json, subprocess
SEED = 20261016
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents]
            if (p / 'Cargo.toml').exists() and (p / 'experiments').is_dir())
EXP = ROOT / 'experiments/archive/2026-10-fixed-area-cycles'
names = ['analysis.json', 'rule_summary.csv', 'audit.json', 'determinism.json',
         'cohort_rules.txt', 'controls_summary.csv', 'controls.txt', 'pilot_feasibility.txt',
         'association.png', 'association.json']
print('git', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
print('UTC', datetime.datetime.now(datetime.timezone.utc).isoformat(), 'bootstrap seed', SEED)
for name in names:
    p = EXP / 'results' / name
    print(p.relative_to(ROOT), hashlib.sha256(p.read_bytes()).hexdigest())
analysis = json.loads((EXP / 'results/analysis.json').read_text())
audit = json.loads((EXP / 'results/audit.json').read_text())
det = json.loads((EXP / 'results/determinism.json').read_text())
assert analysis['bootstrap']['seed'] == SEED
print('Frozen config SHA256:', analysis['config_sha256'])
""")
    cell("markdown", """
## Data and method
Production uses 44 rules × 64 seeds (1001–1064), split into four groups of 16.
Primary bands are [32768,34816) and [131072,139264); 1/8-width bands reuse the
same seeds as a sensitivity analysis. Grid 8192, cap 2^29. The sampler,
`scripts/audit.py`, and `scripts/analyse.py` do the heavy work.
P1 averages two independent-seed Spearman correlations. P2 compares OLS with
and without ln q999 in leave-one-rule-out prediction of ln kappa; its baseline
uses ln mean B duration and ln P/A from disjoint seeds. Bootstrap uses 2000 rule
resamples; P2 resamples fixed per-rule held-out errors rather than refitting.
Both area bands must pass each prediction's threshold.
""")
    cell("markdown", "## Results\nCoverage and accounting first; no failed run or rule is dropped.")
    cell("code", """
for run in ['prod16', 'prod8']:
    print(run, audit['runs'][run])
    print('quantile minimum pooled counts:', analysis[run]['g_quantile_min_pooled_n'])
    print('max final time:', analysis[run]['checks']['max_t_final'],
          'budget gate:', analysis[run]['checks']['g_budget_ok'])
print('Determinism check:', det['scope'])
print(det['runs'])
""")
    cell("markdown", "These checks test coverage and conservation. Accounting identities do not establish an excursion mechanism, and the production thread replay covers one seed per rule.")
    cell("code", """
for run in ['prod16', 'prod8']:
    print('\\n', run)
    for band in [0, 1]:
        b = analysis[run][f'band{band}']
        p1, p2 = b['P1'], b['P2']
        print(f"band {band}: reliability q={b['rel_lnq999_AB']:.3f}, kappa={b['rel_lnk_CD']:.3f}, gate={b['g_reliab_ok']}")
        print(f"  P1 rho={p1['statistic']:.3f}, CI={p1['ci95']}, numerical threshold={p1['success']}")
        print(f"  P2 R2 gain={p2['gain']:.3f}, CI={p2['ci95']}, numerical threshold={p2['success']}")
        print('  baseline/full R2 per rotation:', p2['r2_cv_baseline_full_per_rotation'])
    print('Statistically testable:', analysis[run]['statistically_testable'])
    print('P1 both bands:', analysis[run]['P1_overall_success'],
          'P2 both bands:', analysis[run]['P2_overall_success'])
""")
    cell("markdown", "The registered tests assess an association and incremental prediction in this cohort. Even a pass would not demonstrate causality; a failed reliability gate makes the predictions untestable at the achieved precision.")
    cell("code", """
from IPython.display import Image, display
display(Image(filename=str(EXP / 'results/association.png')))
""")
    cell("markdown", "Each panel shows 44 rules twice, using disjoint seed rotations; the dots are not 88 independent rules. The plot shows the registered association and does not control field geometry or demonstrate tail causality.")
    primary = result["prod16"]
    cell("markdown", f"""
The primary both-band verdict is P1 **{'PASS' if primary['P1_overall_success'] else 'FAIL'}**
and secondary P2 **{'PASS' if primary['P2_overall_success'] else 'FAIL'}**.
P1 correlations are {primary['band0']['P1']['statistic']:.3f} and
{primary['band1']['P1']['statistic']:.3f}; its required cutoff is <= -0.30 at both
bands. P2 held-out R2 gains are {primary['band0']['P2']['gain']:.3f} and
{primary['band1']['P2']['gain']:.3f}. The smaller-area primary association cannot
be rescued by rounding or reporting only the sign of its confidence interval.
The q999 predictor adds information in the registered model; it does not measure
the amount of time carried by the tail or establish mediation.

The 1/8-width sensitivity passes P1 at both areas (-0.417 and -0.815) and
passes P2 again. It reuses the same seeds and does not rescue the primary P1
failure. The smaller-area conclusion depends on band width; the wider band
changes both event counts and the sampling ensemble.
""")
    cell("markdown", "## Between-seed uncertainty\nPer-rule `lnk_time_sd` is the sample sd across 16 seeds. The following quantities compare variation across the four groups with variation across rule means.")
    cell("code", """
for band in [0, 1]:
    b = analysis['prod16'][f'band{band}']
    for col in ['ln_q999', 'lnk_time']:
        print('band', band, col, 'between-rule sd', b[f'{col}_sd_between_rules_of_means'],
              'RMS within-rule group sd', b[f'{col}_mean_within_rule_group_sd'])
""")
    cell("markdown", "These dispersion estimates expose finite-seed noise. Group dispersion is not the standard error of a single trajectory or proof of a universal noise ceiling.")
    cell("markdown", """
## Caveats and controls
Oracle/property tests and the release suite validate instrumentation. Rotor and
random-walk controls quantify band-width and normalization effects; see
`results/controls.txt`. Their conditional kappa has no prespecified known target.
The pilot budget gate initially failed; the cap was raised before production.
The all-production conservation audit and the one-seed-per-rule thread replay
are different checks: the full all-seed determinism clause of P3 remains unchecked.
First-area-hit sampling differs from fixed-time sampling. Equal area does not
fix age, shape or colour field. The width sensitivity shares trajectories.
The q999 cutoff is not a direct tail-time-burden measurement, and P2 uses ln kappa
rather than unnormalized occupancy. This limits any mechanistic interpretation.
The prior matched-area noise-floor failure remains failed.

## What this changes / next steps
Use the registered gate verdicts above to decide whether the earlier cutoff lead
survives fixed-area sampling at this precision. Do not select a successful band
or replace the tail statistic after seeing outcomes. A fresh experiment would
be needed for a revised estimand, larger cohort, or causal mutation/transplant test.

## Open questions
How much of the tail variability is seed noise versus rule structure? Does a
direct tail-time burden outperform a high quantile on fresh data? Which field
interventions can change return times while controlling boundary residence?
""")
    nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
           "language_info": {"name": "python", "version": "3.12"}}, "nbformat": 4, "nbformat_minor": 5}
    (EXP / "notebook.ipynb").write_text(json.dumps(nb, indent=1) + "\n")


if __name__ == "__main__":
    main()
