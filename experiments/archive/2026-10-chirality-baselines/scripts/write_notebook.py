"""Create the lightweight shareable write-up; execute separately under uv."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "source": text.splitlines(keepends=True),
            "execution_count": None, "outputs": []}


cells = [
    md("# Question and why it matters\nDoes the chirality model predict edge-entry probability beyond coarse letter groups? A high pooled score need not imply within-group prediction. See [registration and recipe](README.md) and [scientific record](../../../notes/chirality-baselines-2026-10-15.md)."),
    md("## Assumptions and definitions\nVerified: the saved cohort, target values, calibration membership and chirality predictions reconstruct exactly (tolerance 1e-14). Fit group means on the same 300 calibration rules; score all 2,747 original held-out rules. Primary groups use rule[1]; secondary groups use rule[1:4], with training-only fallback. No grouping uses measured c. This is a reanalysis after inspection of the original plot."),
    code('''from pathlib import Path
import hashlib, json
import numpy as np
import polars as pl
SEED = 20261046
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "Cargo.toml").exists())
E = ROOT / "experiments/archive/2026-10-chirality-baselines/results"
paths = [E / "comparison.json", E / "groups.csv", E / "held_out_predictions.csv"]
assert all(p.is_file() for p in paths)
s = json.loads(paths[0].read_text())
assert s["seed"] == SEED
print("Registration date: 2026-10-15 NZDT; seed:", SEED)
print(json.dumps(s["provenance"], indent=2))
for p in paths:
    print(p.relative_to(ROOT), hashlib.sha256(p.read_bytes()).hexdigest())
'''),
    md("## Data and method\nThe producing script is `scripts/compare.py`; it writes per-rule predictions and subgroup statistics. Conventional R² uses the held-out mean only as a scoring denominator; strict R² compares with the training-mean predictor. RMSE and SSE compare actual predictions. Centered within-group R² subtracts each held-out group's mean from both observations and predictions, isolating discrimination from group-mean bias; these centering operations do not define a deployable predictor. Bootstrap intervals resample paired held-out rules within the two primary groups, keeping model fits fixed (4,000 draws)."),
    md("## Results"),
    code('''table = pl.DataFrame([{"model": k, **{m: v[m] for m in ["n", "r2", "strict_r2", "sse", "rmse", "mae"]}} for k, v in s["overall"].items()])
print(table)
print(json.dumps(s["comparisons"], indent=2))
assert abs(s["overall"]["chirality"]["r2"] - 0.6600227968106389) < 1e-12
'''),
    md("Chirality improves on one-letter grouping but the three-letter lookup predicts more accurately. These are held-out predictions of c, not evidence for the origin of the growth exponent. The quoted R²=0.88 is not reproduced: existing results give R²=0.660 and correlation 0.869."),
    code('''groups = pl.read_csv(E / "groups.csv")
print(groups.filter((pl.col("grouping") == "letter1") & (pl.col("model") != "constant")).select("group", "model", "n", "n_train_group", "r2", "rmse", "vs_baseline_sse_reduction"))
print(json.dumps(s["grouping"], indent=2))
print("Registered prediction outcomes:", s["registered_predictions"])
'''),
    md("Chirality has nonzero skill inside the broad one-letter groups (R²=0.190 and 0.164), but centered within the three-letter groups its pooled R² is approximately zero. The latter describes residual discrimination; it does not establish that every individual group has exactly zero skill. The prediction that one-letter grouping lies within 0.05 of chirality fails; the prediction of less than 10% gain over three-letter grouping holds, with chirality actually worse."),
    md("## Caveats and controls\nSynthetic controls test perfect, zero and adverse residual prediction, group-mean shifts, training-only fits, fallback and paired bootstrap reproducibility. They do not validate a physical mechanism. No trajectory estimator or fit window changed, so rotor/random-walk calibration was not rerun. The current cohort includes related/repeated rules; rule bootstrap assumes independent sampling units and conditions on this training sample. No between-seed uncertainty or fresh-rule confirmation is available. Sparse/short groups are retained with explicit fallback and undefined within-group R² where variance is zero.\n\n## What this changes / next steps\nPresent the three-letter lookup as the stronger predictive baseline and qualify the chirality model's mechanistic interpretation. The coarse one-letter description alone understates the chirality model's residual information. A future independent test should hold out rule families and recalibrate across initial seeds. No claim that c alone diagnoses cube-root growth follows from these comparisons."),
]
notebook = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                          "language_info": {"name": "python", "version": "3.12"}},
            "nbformat": 4, "nbformat_minor": 5}
for i, cell in enumerate(cells):
    cell["id"] = f"chirality-{i:02d}"
(HERE / "notebook.ipynb").write_text(json.dumps(notebook, indent=1) + "\n")
