"""P5 analysis (registered in README): results/p5_transplant.csv -> results/p5_analysis.txt.
(a) control rows must have the same final position, heading and visit-count hash (vhash) as the original;
(b) flipped rows must read a count > 2k+2 within one revolution after t0 (revolution = interval between the first two xmax
advances after t0 in the matching control row), or stop advancing the front every revolution.
"""
import csv
from pathlib import Path

EXP = Path(__file__).resolve().parents[1]


def main():
    rows = list(csv.DictReader(open(EXP / "results/p5_transplant.csv")))
    out = ["P5: transplant of mid-fill states (8192 board, t0 + 1e8 steps)"]
    a_ok = b_ok = 0
    for i in range(0, len(rows), 3):
        orig, ctl, flp = rows[i], rows[i + 1], rows[i + 2]
        k = (int(orig["spec"].split("#")[1]) - 2) // 2
        t0 = int(ctl["spec"].split("@")[1].split("#")[0])
        same = all(orig[c] == ctl[c] for c in ("x", "y", "h", "vhash", "visited"))
        fr = [int(v) for v in ctl["fronts_after"].split(";")]
        rev = fr[1] - fr[0]
        fg = int(flp["first_gt"]) - t0 if flp["first_gt"] else None
        broke = fg is not None and fg <= rev
        a_ok += same
        b_ok += broke
        out.append(f"k={k} t0={t0}: original {orig['spec']} visited={orig['visited']}")
        out.append(f"  (a) {ctl['spec']}: identical position/heading/vhash/visited = {same}")
        out.append(f"  (b) {flp['spec']}: first read > {2*k+2} at t0+{fg}; revolution at t0 = {rev} steps -> broke within one "
                   f"revolution = {broke}; visited at end {flp['visited']} vs {orig['visited']}; last-window max read "
                   f"{flp['win_maxread']}, new cells {flp['win_new']} vs {orig['win_new']}")
    out += [f"(a) controls identical: {a_ok}/3", f"(b) ring broken within one revolution: {b_ok}/3",
            "VERDICT: P5 HELD" if a_ok == 3 and b_ok == 3 else "VERDICT: P5 FAILED"]
    (EXP / "results/p5_analysis.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


main()
