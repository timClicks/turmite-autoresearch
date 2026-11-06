# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Revision 4 G1 synthetic gate (README "Revision 4 registration").

Reads the dhist-format output of examples/boundary_excursions_depth_synth.rs (base seed 2026102981, 20 reps)
and applies the frozen depth readout. Writes results/rev4_synth.{json,txt}.
Usage: synth_rev4.py PATH_TO_SYNTH_CSV
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import depth_score as ds  # noqa: E402

RES = Path(__file__).resolve().parents[1] / "results"
TRUTH = {"SD": "area", "SDL": "area", "SA": "area", "SB": "line", "SC": "line"}
OPP = {"area": "line", "line": "area"}


def main():
    h = ds.load_dhist(Path(sys.argv[1]))
    reps = defaultdict(list)  # (law, rep) -> per-window
    for (spec, k), axes in h.items():
        law, rep, ps = spec.split(":")
        L = 6 * 2 ** (3 * (k - 16) / 8)
        if not (ds.K_LO <= k <= ds.K_HI) or L < ds.L_MIN:
            continue
        b, nb, span = ds.window_beta(axes["d"], L)
        if b is None:
            continue
        reps[(law, int(rep))].append({"seed": int(ps), "k": k, "beta": b})
    out, lines = {}, []
    ok_all = True
    lines.append("Rev4 G1 synthetic gate (depth readout). Calls: area >= 1.70, line <= 1.30.")
    lines.append(f"{'law':4} {'truth':5} correct opposite inconcl/uninf  median-beta  [min, max] over reps  windows/rep")
    for law, truth in TRUTH.items():
        res = [ds.kind_summary(reps[(law, r)]) for r in range(20)]
        calls = [x["call"] for x in res]
        betas = [x["beta"] for x in res if x["beta"] is not None]
        nc = sum(c == truth for c in calls)
        no = sum(c == OPP[truth] for c in calls)
        passed = nc >= 18 and no == 0
        ok_all &= passed
        out[law] = {"truth": truth, "correct": nc, "opposite": no, "calls": calls,
                    "betas": [x["beta"] for x in res], "n_windows": [x["n_windows"] for x in res], "pass": passed}
        import numpy as np
        lines.append(f"{law:4} {truth:5} {nc:2d}/20  {no:2d}/20    {20 - nc - no:2d}/20        {np.median(betas):.3f}"
                     f"       [{min(betas):.3f}, {max(betas):.3f}]        {sorted(set(out[law]['n_windows']))}"
                     f"  {'PASS' if passed else 'FAIL'}")
    lines.append(f"G1: {'PASS' if ok_all else 'FAIL'}")
    out["G1"] = "PASS" if ok_all else "FAIL"
    (RES / "rev4_synth.json").write_text(json.dumps(out, indent=1))
    (RES / "rev4_synth.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
