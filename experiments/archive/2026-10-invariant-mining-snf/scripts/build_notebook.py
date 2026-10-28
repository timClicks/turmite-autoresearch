"""Build and execute notebook.ipynb from the committed results/ (standard library only).

  uv run --no-project experiments/archive/2026-10-invariant-mining-snf/scripts/build_notebook.py

Each code cell is executed in order in one namespace with stdout captured as the cell output, so the
notebook runs top to bottom from a clean interpreter.  No randomness; no file outside results/ is read
except the inputs whose hashes the provenance cell prints.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]

MD = lambda s: ("markdown", s.strip("\n"))
CODE = lambda s: ("code", s.strip("\n"))

CELLS = [
    MD("""
# Additive conservation laws of generalised Langton's ants, for all moduli at once

*For a colleague who has not seen the work.* An n-colour ant turns by `rule[c]` on colour `c`, advances the
colour to `(c+1) % n` and steps. We ask for **exact** laws `V = a x + b y + e t + Phi(h, class) + sum_cells w(class, colour)`
that no step can change (mod some `m`). Each law is a proof, not a statistic: it is the solution of a finite
integer-linear system (every local transition), solved for all `m` at once by Smith normal form.
Predictions were registered in the README before any code existed (commit `db7eb40`).
"""),
    MD("## Provenance"),
    CODE("""
import json, hashlib, csv, pathlib
from collections import Counter
R = pathlib.Path('results') if pathlib.Path('results').exists() else pathlib.Path('experiments/archive/2026-10-invariant-mining-snf/results')
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()[:16]
prov = json.load(open(R / 'census_provenance.json'))
print('census command :', prov['command'])
print('census git head:', prov['git_head'])
print('lawmod.py sha  :', prov['lawmod_sha256'][:16])
for name in ['fingerprints.csv','universal.csv','p4.csv','by_counts.csv','summary.json','oracle_summary.json','crosscheck_peer.json','highways_tilefree.json']:
    print(f'{name:26s} sha256[:16] = {sha(R/name)}')
"""),
    MD("## Assumptions and what a law means"),
    MD("""
* One ant on the square lattice, blank (colour 0) background, finite-support field; with an infinite non-blank
  background read the field sum as the finite change from the initial field.
* Families: **A0** (no class, `Phi = d*h`, the other agent's ansatz), **F1** (no class, any `Phi(h)`),
  **F2** (class `(x+y) mod 2`, only states with `h = x+y` mod 2), **F3** (class `(x mod 2, y mod 2)`, same manifold).
  The manifold `h + x + y` even is itself an invariant, and the blank start lies on it.
* *Universal* laws hold for every rule of that length; the interesting part of a rule is its law group modulo the
  universal one (summarised by Smith invariant factors).
"""),
    MD("## P1: the law group of a rule depends only on (n, #R)"),
    CODE("""
S = json.load(open(R / 'summary.json'))
print('rules per family            :', S['P1_rules_per_family'])
print('(family,n,#R) with >1 fingerprint:', S['P1_exceptions'])
print('post hoc: groups by (n, +-D mod 4, trivial):', S['P1b_posthoc_groups'], ' with >1 fingerprint:', S['P1b_posthoc_groups_with_more_than_one_fingerprint'])
print('differences under complement / reverse / rotations:', S['P1_symmetry_differences'])
print('distinct fingerprints per (family, n):')
for k, v in S['distinct_fingerprints_per_family_n'].items():
    if k.startswith('F1') or k.startswith('F3'): print(f'  {k}: {v}')
"""),
    MD("""
Reading: `P1_exceptions` = 0 means no rule of length <= 8 has a law group different from the other rules with the same
number of R. In particular `RRLL` and `RLRL` are indistinguishable to every law in A0-F3: these invariants are *blind to
the order of the colours*. That follows from a short argument (README, "Derivation behind P1"): a cell potential
cannot see the heading, so each colour's net contribution is a constant `E_R` or `E_L`, and only
`#R*E_R + #L*E_L = 0` survives the trip round the colour cycle.
"""),
    MD("## P3, P6, P7: universal laws (true of every rule of the length)"),
    CODE("""
print('P3 (F1 universal orders; observed, predicted):')
for k, v in S['P3_cells'].items(): print(f'  {k:12s} {v}')
print('P3 all as predicted:', S['P3_all_as_predicted'])
print()
print('Universal group order at modulus m = n  (P6, P7):')
for n, d in S['P6_orders_at_m_eq_n'].items(): print(f'  n={n}: {d}')
print('P6 F2 > F1 for every n:', S['P6_F2_gt_F1_all_n'])
print('P7 F3 > F2 for some n :', S['P7_F3_gt_F2_some_n'], S['P7_ns_where_F3_gt_F2'])
"""),
    MD("## P4: when does the tape determine the heading?"),
    CODE("""
print('rules:', S['P4_rules'], ' with D=#R-#L = 0 mod 4:', S['P4_rules_with_D0'])
print('registered P4 (any law a=b=e=0, Phi nonconstant, mod 4 iff D=0 mod 4): mismatches =', S['P4_registered_mismatches'],
      ' D values of mismatches =', S['P4_mismatch_D_values'], ' all n even:', S['P4_mismatch_all_n_even'])
print('post hoc refinement (a law with Phi(1) odd, i.e. pins h mod 4):          mismatches =', S['P4_posthoc_mismatches'])
"""),
    MD("""
The registered statement was too strong: for even `n` the colour clock gives `t = sum c N_c (mod 2)` and the heading parity
equals the time parity, so heading *parity* is always a function of the tape. What `D = 0 (mod 4)` buys is the full
heading mod 4 (Langton's ant: heading = number of colour-1 cells mod 4). The refinement was written after seeing the
failure and is labelled post hoc.
"""),
    MD("## P5 and P2: are the laws really laws? (oracle and cross-check)"),
    CODE("""
O = json.load(open(R / 'oracle_summary.json'))
print('oracle: steps', O['steps'], 'starts/rule', O['starts_per_rule'], 'seed', O['seed'], 'git', O['git_head'][:10])
for k, v in O['by_family'].items(): print(f'  {k:12s} {v}')
print('law violations:', O['law_violations_total'], ' control detection rate:', O['control_detection_rate'])
X = json.load(open(R / 'crosscheck_peer.json'))
print('cross-check vs src/invariants.rs: comparisons', X['comparisons'], 'mismatches', X['mismatches'],
      '| peer files committed when run:', X['peer_files_committed'])
"""),
    MD("## P8: tile-free laws against the confirmed highways"),
    CODE("""
H = json.load(open(R / 'highways_tilefree.json'))
print('highways:', H['n_highways'])
print('violations:', {k: v['count'] for k, v in H['violations'].items()})
print('tile-free group orders at m=2,4,8 (rules with that order):', H['tile_free_group_orders_m2_m4_m8'])
print('tile-free group equals the universal one for every rule (orders at m=2,4,8):', H['rule_tile_free_equals_universal_for_all'])
"""),
    MD("""
## What this does and does not show
* **Shows (exact, finite):** the complete law group of every rule of length <= 8 within A0-F3, its universal part, and
  that the rule-dependent part is a function of `(n, #R)`. Every generator survived 2000 oracle steps from random starts, and
  random non-laws were caught, so the checker has power.
* **Does not show:** anything about growth exponents, highway formation or chaos. Laws that couple the ant to the
  colours of neighbouring cells, pair potentials, edge flux and history dependence are outside the ansatz and are the only
  place rule order could enter an invariant. The tile-free highway check is an instrument check (no violations, nothing new
  beyond known parity facts).
* **Caveats:** the oracle checks lengths <= 6; the census covers <= 8; the claim for all `n` rests on the short argument
  above, not on a checked proof. The README's rule count (510) is a typo for 508 (2^2 + ... + 2^8). P4 as registered failed.

## Next
Build a pair-potential family with a quotient by functionals that vanish on all finite fields (otherwise group orders are
inflated), and ask whether any law there depends on the *order* of the colours.
"""),
]


def build() -> dict:
    ns: dict = {}
    cells = []
    count = 1
    for kind, src in CELLS:
        if kind == "markdown":
            cells.append({"cell_type": "markdown", "metadata": {}, "source": src.splitlines(keepends=True)})
            continue
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(src, f"<cell {count}>", "exec"), ns)
        out = buf.getvalue()
        cells.append({
            "cell_type": "code", "execution_count": count, "metadata": {},
            "outputs": [{"output_type": "stream", "name": "stdout", "text": out.splitlines(keepends=True)}] if out else [],
            "source": src.splitlines(keepends=True),
        })
        count += 1
    return {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                                         "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}


if __name__ == "__main__":
    import os
    os.chdir(ROOT / "experiments/archive/2026-10-invariant-mining-snf")
    nb = build()
    (EXP / "notebook.ipynb").write_text(json.dumps(nb, indent=1) + "\n")
    print("wrote notebook.ipynb with", len(nb["cells"]), "cells")
