"""Task C1a: my independent ant against `reference::Ant` (through the thin driver examples/rlrlll_c1_reference_hash.rs).

usage (inside WSL): python3 c1a.py DRIVER_BINARY SCRATCH_DIR
Prints the report that is saved as results/c1a_semantics.txt. Python builds every state and decides every stopping rule; the
driver only steps the reference ant N times and folds every step into a hash.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c1_ant import *

OFFSET, PRIME, M64 = 0xcbf29ce484222325, 0x100000001b3, (1 << 64) - 1


def fold(acc, w):
    return ((acc ^ (w & 0xFFFFFFFF)) * PRIME) & M64


def cell_hash(cells):
    h = OFFSET
    for (x, y), c in sorted(cells.items()):
        for w in (x, y, c):
            h = fold(h, w)
    return h


def py_run(rule, cells, pos, h, steps=None, stop_xmin=None, cp=1000, keep_trace=False):
    """My ant. Runs `steps` steps, or until the minimum x first reaches `stop_xmin`. Returns checkpoints, end line, trace."""
    ant = Ant(rule, cells, pos, h)
    acc, cps, trace, xmin = OFFSET, [], [], pos[0]
    while True:
        if steps is not None and ant.steps >= steps:
            break
        if stop_xmin is not None and xmin <= stop_xmin:
            break
        x, y, c, hh = ant.step()
        for w in (x, y, c, hh):
            acc = fold(acc, w)
        xmin = min(xmin, ant.pos[0])
        if keep_trace:
            trace.append((x, y, c, hh))
        if ant.steps % cp == 0:
            cps.append((ant.steps, acc))
    return dict(ant=ant, cps=cps, acc=acc, xmin=xmin, trace=trace)


def write_state(path, rule, cells, pos, h, steps, cp):
    with open(path, "w") as f:
        f.write(f"rule {rule}\nant {pos[0]} {pos[1]} {h}\nsteps {steps}\ncheckpoint {cp}\ncells {len(cells)}\n")
        for (x, y), c in sorted(cells.items()):
            f.write(f"{x} {y} {c}\n")


def ref_run(driver, scratch, tag, rule, cells, pos, h, steps, cp, trace=False):
    st, co, tr = scratch / f"{tag}.state", scratch / f"{tag}.cells", scratch / f"{tag}.trace"
    write_state(st, rule, cells, pos, h, steps, cp)
    cmd = [driver, str(st), str(co)] + ([str(tr)] if trace else [])
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.splitlines()
    cps = [(int(l.split()[1]), int(l.split()[2], 16)) for l in out if l.startswith("cp ")]
    t = out[-1].split()  # end steps N pos X Y heading H ncells n cellhash h acc a minx m
    end = dict(steps=t[2], pos=f"{t[4]} {t[5]}", heading=t[7], ncells=t[9], cellhash=t[11], acc=t[13], minx=t[15])
    return dict(cps=cps, end=end, cells_file=co, trace_file=tr)


def compare(py, ref, ant):
    """Returns a list of disagreements (empty = identical)."""
    bad = []
    if len(py["cps"]) != len(ref["cps"]):
        bad.append(f"checkpoint count {len(py['cps'])} vs {len(ref['cps'])}")
    for (s1, a1), (s2, a2) in zip(py["cps"], ref["cps"]):
        if (s1, a1) != (s2, a2):
            bad.append(f"first differing checkpoint at step {s1}: {a1:016x} vs {a2:016x}")
            break
    e = ref["end"]
    mine = dict(steps=str(ant.steps), pos=f"{ant.pos[0]} {ant.pos[1]}", heading=str(ant.h), ncells=str(len(ant.cells)),
                cellhash=f"{cell_hash(ant.cells):016x}", acc=f"{py['acc']:016x}")
    for k, v in mine.items():
        got = e.get(k)
        if got != v:
            bad.append(f"final {k}: mine {v} vs reference {got}")
    return bad, mine


def main():
    driver, scratch = sys.argv[1], Path(sys.argv[2])
    scratch.mkdir(parents=True, exist_ok=True)
    ph = parse_canonical()
    ok_all = True
    print("# C1a: independent ant vs reference::Ant; per-step FNV-1a fold of (x, y, colour read, heading after turn)")
    print(f"# driver sha256 in results/c1_driver.sha256; python {sys.version.split()[0]}")

    # C1a-2: blank board, 1e6 steps
    N = 1_000_000
    for label, rule in (("RLRLLL (correct)", "RLRLLL"), ("control 1a: colour 3 L->R, RLRRLL", "RLRRLL"), ("control 1b: colour 0 R->L, LLRLLL", "LLRLLL")):
        py = py_run(rule, {}, (0, 0), 0, steps=N)
        ref = ref_run(driver, scratch, "blank", "RLRLLL", {}, (0, 0), 0, N, 1000)
        bad, mine = compare(py, ref, py["ant"])
        if rule == "RLRLLL":
            ok_all &= not bad
        print(f"blank board {N} steps, ant rule {label}, reference rule RLRLLL: {len(py['cps'])} checkpoints; "
              + ("IDENTICAL" if not bad else "DISAGREE: " + "; ".join(bad)))
        print(f"   final: steps {mine['steps']} pos {py['ant'].pos} heading {mine['heading']} ncells {mine['ncells']} cellhash {mine['cellhash']}")

    # C1a-3: windows, one full cycle each
    for q in range(3):
        for m in (2, 4, 10, 50):
            cells, pos, h = start_state(ph[q], m)
            py = py_run("RLRLLL", cells, pos, h, stop_xmin=-3, cp=100)
            n = py["ant"].steps
            ref = ref_run(driver, scratch, "win", "RLRLLL", cells, pos, h, n, 100)
            bad, mine = compare(py, ref, py["ant"])
            refcells = {}
            for l in ref["cells_file"].read_text().splitlines():
                x, y, c = map(int, l.split())
                refcells[(x, y)] = c
            if refcells != py["ant"].cells:
                bad.append("final cell sets differ")
            if ref["end"]["minx"] != "-3":
                bad.append(f"reference min x {ref['end']['minx']} != -3")
            ok_all &= not bad
            print(f"window q={q} m={m:3d}: {n} steps, {len(py['cps'])} checkpoints, final {len(refcells)} cells, min x {ref['end']['minx']}: "
                  + ("IDENTICAL" if not bad else "DISAGREE: " + "; ".join(bad)))
    print("C1a RESULT:", "all correct-rule comparisons identical" if ok_all else "DISAGREEMENT (see above)")


main()
