"""Task C1b: an independent verifier of the sweeper family's closure C(m, q) -> C(m + 2, q + 1).

usage: python3 c1b.py [--canonical PATH] [--rule RULE] [--mmax 100]

Written without reference to the first checker's code. Proof architecture (my own), per phase q, rows are tuples over the
51 columns x = -3 .. 47 (x = 0 is the front, x >= 48 is "east of the strip": arbitrary, never to be touched):

    C(m, q) = [blank] . top_q . bulk^m . bottom_q . [blank]

    S1  finite run on [blank^NB top_q bulk^K1], ends at the first arrival on the row below it (a sentinel).
        Output: rows U (above A), the frame A (last H rows), ant (x1, h1).
    D   descent lemma: patch [A bulk^p], ant on the first bulk row; the run ends at the first arrival on the row below the
        patch, with the ant in the same x and heading and with A reproduced p rows lower; the p rows it leaves above are r'.
        By induction on n, A bulk^(p n) -> r'^n A in n s_d steps (each application only sees its own patch; the row below
        the patch is a sentinel the ant may arrive on but never read).
    S3  finite run on [sentinel] A bulk^e bottom_q blank^NB [sentinel], from the ant (x1, h1) on the row after A; ends at the first
        arrival on the sentinel above A, which is the last r' row.
    R   return lemma, mirror image: patch [sentinel r'^p' A'], A' = S3's rows just below the arrival row; ant on the last r'
        row; ends at the first arrival on the sentinel with A' reproduced p' rows higher; the p' rows it leaves below are r''.
    S5  finite run on [U A' r''^k5 sentinel], ant on the last row of U (the arrival row); ends the first time x = -3 (the new
        front). Output: the rows E5.
    Compose: final = E5 . (r'' band, n p - k5 rows) . D3 where D3 are S3's rows below A'; compare with C(m + 2, q + 1) shifted by
        3 columns, for the whole cell set in x = 0 .. 47 and the ant (column, heading, row offset).
Every finite run: positions outside x <= 47 or x < the floor fail; reaching a sentinel row ends the run only if the success
condition holds there, otherwise the run fails.
"""
import argparse
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c1_ant import Ant, CW, parse_canonical, run_cycle, closes, STRIP

W = 51  # columns x = -3 .. 47
NB = 14  # blank rows kept above and below the rectangle in the end-stage patches
BLANK = (0,) * W
SMAX = 3000


def ext(s):
    return (0, 0, 0) + tuple(0 if ch in ".0" else int(ch) for ch in s)


def to_cells(rows):
    return {(i - 3, y): c for y, r in enumerate(rows) for i, c in enumerate(r) if c}


def to_rows(cells, n):
    return [tuple(cells.get((i - 3, y), 0) for i in range(W)) for y in range(n)]


class Fail(Exception):
    pass


def run(rule, rows, pos, h, success, xfloor=-2, smax=SMAX):
    """Run my ant on the patch `rows` (sentinel rows at y = -1 and y = len(rows)). `success(ant)` is evaluated after every
    step. Returns (rows_after, steps, ant_pos, heading, stats). Raises Fail on: x > 47, x < xfloor, reading a sentinel
    (arriving there is fine only when `success` holds at that step), or no success within smax steps."""
    n = len(rows)
    ant = Ant(rule, to_cells(rows), pos, h)
    ys, xs = {pos[1]}, {pos[0]}
    for _ in range(smax):
        ant.step()
        x, y = ant.pos
        ys.add(y)
        xs.add(x)
        if x > STRIP - 1:
            raise Fail(f"left the strip at column {x}")
        if x < xfloor:
            raise Fail(f"reached column {x} < {xfloor} before success")
        ok = success(ant)
        if y < 0 or y >= n:
            if y < -1 or y > n or not ok:
                raise Fail(f"arrived on sentinel row {y} (patch rows 0..{n - 1}) without success")
            return to_rows(ant.cells, n), ant.steps, ant.pos, ant.h, dict(miny=min(ys), maxy=max(ys), minx=min(xs), maxx=max(xs))
        if ok:
            return to_rows(ant.cells, n), ant.steps, ant.pos, ant.h, dict(miny=min(ys), maxy=max(ys), minx=min(xs), maxx=max(xs))
    raise Fail("no success within the step limit")


def band_at_bottom(rows_top_to_bottom):
    return rows_top_to_bottom


def verify_phase(rule, ph, q, lines, mmax):
    """Returns dict with verdict and the symbolic result for phase q (or raises Fail with the stage name)."""
    p0, nq = ph[q], ph[(q + 1) % 3]
    top = [ext(r) for r in p0["top"]]
    bulk = ext(p0["bulk"])
    bottom = [ext(r) for r in p0["bottom"]]
    T, Bt = len(top), len(bottom)
    ntop = [ext(r) for r in nq["top"]]
    nbulk = ext(nq["bulk"])
    nbottom = [ext(r) for r in nq["bottom"]]
    log = lambda s: lines.append(f"  {s}")

    # ---- S1 and the descent lemma: search K1, then (H, p)
    desc = None
    for K1 in range(1, 8):
        rows1 = [BLANK] * NB + top + [bulk] * K1
        R1 = len(rows1)
        try:
            e1, s1, pos1, h1, st1 = run(rule, rows1, (p0["dx"], NB + p0["dy"]), p0["h"], lambda a: a.pos[1] == R1)
        except Fail as f:
            log(f"S1 with K1 = {K1}: {f}")
            continue
        for p in (1, 2, 3, 4):
            for H in range(1, 7):
                A = e1[R1 - H:R1]
                patch = A + [bulk] * p
                try:
                    d1, sd, posd, hd, std = run(rule, patch, (pos1[0], H), h1,
                                                lambda a, p=p, H=H: a.pos[1] == H + p)
                except Fail:
                    continue
                if posd[0] == pos1[0] and hd == h1 and d1[p:p + H] == A:
                    desc = dict(K1=K1, R1=R1, e1=e1, s1=s1, pos1=pos1, h1=h1, st1=st1, H=H, p=p, A=A, sd=sd, rprime=d1[:p], std=std)
                    break
            if desc:
                break
        if desc:
            break
    if not desc:
        raise Fail("no descent lemma (S1 + shift lemma) found for K1 <= 7, p <= 4, H <= 6")
    K1, R1, e1, H, p, A, sd = desc["K1"], desc["R1"], desc["e1"], desc["H"], desc["p"], desc["A"], desc["sd"]
    U = e1[:R1 - H]
    log(f"S1: K1 = {K1} band rows, {desc['s1']} steps, ant arrives on row {R1} at x = {desc['pos1'][0]}, heading {desc['h1']}; "
        f"rows touched {desc['st1']['miny']}..{desc['st1']['maxy']} of 0..{R1 - 1}, x {desc['st1']['minx']}..{desc['st1']['maxx']}")
    log(f"descent lemma: H = {H}, p = {p}, s = {sd} steps per application; A = rows {R1 - H}..{R1 - 1} of the S1 output; "
        f"patch rows touched {desc['std']['miny']}..{desc['std']['maxy']} of 0..{H + p - 1}, x {desc['std']['minx']}..{desc['std']['maxx']}")

    # ---- S3 and the return lemma: search e, then (H', p')
    ret = None
    for e in range(0, 8):
        if (K1 + e) % p:  # band m = K1 + p n + e must be an even number for every n; here m even <=> (K1 + e) even for p = 2
            continue
        rows3 = list(A) + [bulk] * e + bottom + [BLANK] * NB
        R3 = len(rows3)
        try:
            e3, s3, pos3, h3, st3 = run(rule, rows3, (desc["pos1"][0], H), desc["h1"], lambda a: a.pos[1] == -1)
        except Fail as f:
            log(f"S3 with e = {e}: {f}")
            continue
        rp = desc["rprime"]
        for pp in (p, 2 * p):
            blk = [rp[(len(rp) - pp + i) % len(rp)] for i in range(pp)]
            for Hp in range(1, 7):
                Ap = e3[:Hp]
                patch = [BLANK] + blk + Ap
                try:
                    r1, sr, posr, hr, strr = run(rule, patch, (pos3[0], pp), h3, lambda a, pp=pp: a.pos[1] == 0)
                except Fail:
                    continue
                if posr[0] == pos3[0] and hr == h3 and r1[1:1 + Hp] == Ap:
                    ret = dict(e=e, s3=s3, pos3=pos3, h3=h3, e3=e3, st3=st3, Hp=Hp, pp=pp, Ap=Ap, sr=sr, rpp=r1[1 + Hp:1 + Hp + pp], blk=blk, strr=strr)
                    break
            if ret:
                break
        if ret:
            break
    if not ret:
        raise Fail("no return lemma (S3 + mirror shift lemma) found for e <= 7")
    e, Hp, pp, sr = ret["e"], ret["Hp"], ret["pp"], ret["sr"]
    log(f"S3: e = {e} band rows, {ret['s3']} steps; rows touched {ret['st3']['miny']}..{ret['st3']['maxy']} of 0..{len(A) + e + Bt + NB - 1} "
        f"(A = rows 0..{H - 1}, bottom_q = rows {H + e}..{H + e + Bt - 1}), x {ret['st3']['minx']}..{ret['st3']['maxx']}; ant at x = {ret['pos3'][0]}, heading {ret['h3']}")
    log(f"return lemma: H' = {Hp}, p' = {pp}, s = {sr} steps per application; patch rows touched {ret['strr']['miny']}..{ret['strr']['maxy']} of 0..{1 + pp + Hp - 1}, x {ret['strr']['minx']}..{ret['strr']['maxx']}")
    if pp != p:
        raise Fail(f"descent period {p} and return period {pp} differ: leftover handling not implemented")

    # ---- S5: top rows U, A', then k5 rows of the r'' band; search k5
    rpp = ret["rpp"]
    fin = None
    for k5 in range(0, 6):
        band5 = [rpp[i % pp] for i in range(k5)]
        rows5 = list(U) + list(ret["Ap"]) + band5
        R5 = len(rows5)
        try:
            e5, s5, pos5, h5, st5 = run(rule, rows5, (ret["pos3"][0], len(U) - 1), ret["h3"], lambda a: a.pos[0] == -3, xfloor=-3)
        except Fail as f:
            log(f"S5 with k5 = {k5}: {f}")
            continue
        fin = dict(k5=k5, e5=e5, s5=s5, pos5=pos5, h5=h5, st5=st5)
        break
    if not fin:
        raise Fail("S5 failed for k5 <= 5")
    k5, e5, s5, pos5, h5 = fin["k5"], fin["e5"], fin["s5"], fin["pos5"], fin["h5"]
    log(f"S5: k5 = {k5} band rows, {s5} steps; rows touched {fin['st5']['miny']}..{fin['st5']['maxy']} of 0..{len(e5) - 1}, x {fin['st5']['minx']}..{fin['st5']['maxx']}; final ant x = {pos5[0]}, heading {h5}")

    # ---- composition: n >= n_min applications, n p - k5 band rows of r'' left, then D3 = S3 rows from A' on
    D3 = ret["e3"][Hp:]
    nmin = -(-k5 // p)
    ok_compose = True
    why = ""
    sym = None
    for n in range(nmin, nmin + 4):
        m = K1 + p * n + e
        if m % 2:
            continue
        left = p * n - k5
        band = [rpp[(k5 + i) % pp] for i in range(left)]
        final = list(e5) + band + list(D3)
        # strip -> new window: old column x -> x + 3, keep 0..47; the ant's row decides where the rectangle sits
        fc = {(x + 3, y): c for (x, y), c in to_cells(final).items() if x + 3 < STRIP}
        ay = pos5[1]
        target = [ntop[i] for i in range(len(ntop))] + [nbulk] * (m + 2) + nbottom
        tc = {(x, ay - nq["dy"] + y): c for (x, y), c in to_cells(target).items()}
        if fc != tc:
            diff = sorted(set(fc.items()) ^ set(tc.items()), key=lambda t: (t[0][1], t[0][0]))
            first = diff[0][0]
            ok_compose = False
            why = f"n = {n} (m = {m}): final state is not C(m + 2, {(q + 1) % 3}); {len(diff)} cells differ, first at window (x, y) = {first}"
            break
        if (pos5[0] + 3, h5) != (nq["dx"], nq["h"]):
            ok_compose = False
            why = f"n = {n}: ant (x {pos5[0] + 3}, heading {h5}) != expected (x {nq['dx']}, heading {nq['h']})"
            break
    if not ok_compose:
        raise Fail("composition: " + why)
    # The four sampled n above are not yet "for all n". Insertion argument: final(n + 1) is final(n) with p more rows of the
    # r'' band inserted at the junction E5 | band | D3; target(n + 1) is target(n) with p more bulk rows inserted in the bulk
    # run. They agree for all n >= nmin if (i) each r'' row, shifted by 3 and cut at x = 47, is the next phase's bulk row, and
    # (ii) that junction lies inside (or at an end of) the target's bulk run. Both are checked here.
    for r in rpp:
        sh = {(x + 3, 0): c for (x, _), c in to_cells([r]).items() if x + 3 < STRIP}
        if sh != {(x, 0): c for (x, _), c in to_cells([nbulk]).items()}:
            raise Fail("composition: an r'' row, shifted by 3 columns, is not the next phase's bulk row")
    m_lo = K1 + p * nmin + e
    t0 = pos5[1] - nq["dy"]  # row of the target's first row in the frame of `final`
    lo, hi = t0 + len(ntop), t0 + len(ntop) + m_lo + 2
    if not (lo <= len(e5) <= hi):
        raise Fail(f"composition: the junction (row {len(e5)}) is outside the bulk run of the target (rows {lo}..{hi})")
    # steps: s1 + n sd + s3 + n sr + s5, with m = K1 + p n + e
    a_coef = Fraction(sd + sr, p)  # steps per unit of m
    b_const = desc["s1"] + ret["s3"] + s5 - a_coef * (K1 + e)
    m0 = K1 + e + p * nmin
    log(f"compose: for n = {nmin}..{nmin + 3} (m = K1 + p n + e = {K1 + p * nmin + e}..) final = C(m + 2, {(q + 1) % 3}) exactly "
        f"(all cells in x = 0..47 and the ant); steps = {desc['s1']} + {ret['s3']} + {s5} + n ({sd} + {sr}) = {a_coef} m + {b_const}")
    t0 = pos5[1] - nq["dy"]
    dtop_up = NB - t0  # rows the rectangle's top row moves up in one cycle
    dbot_down = t0 + len(ntop) + len(nbottom) + 2 - NB - T - Bt  # rows its bottom row moves down (independent of m)
    data = dict(bulk=bulk, A=A, x1=desc["pos1"][0], h1=desc["h1"], rp=desc["rprime"], Ap=ret["Ap"], rpp=rpp, x3=ret["pos3"][0], h3=ret["h3"])
    return dict(a=a_coef, b=b_const, m0=m0, _data=data, dtop_up=dtop_up, dbot_down=dbot_down, _std=desc["std"], _strr=ret["strr"], K1=K1, e=e, p=p, k5=k5, nmin=nmin, sd=sd, sr=sr, H=H, Hp=Hp,
                reach=dict(s1=desc["st1"], s3=ret["st3"], s5=fin["st5"], NB=NB, T=T, Bt=Bt, H=H, e=e, K1=K1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical", default=None)
    ap.add_argument("--rule", default="RLRLLL")
    ap.add_argument("--mmax", type=int, default=100)
    ap.add_argument("--skip-brute", action="store_true")
    a = ap.parse_args()
    ph = parse_canonical(a.canonical)
    rule = a.rule
    out = [f"# c1b: independent verifier. rule {rule}, canonical {a.canonical or 'results/canonical_k0.txt'}, python {sys.version.split()[0]}"]
    res = {}
    all_ok = True
    for q in range(3):
        lines = [f"phase {q} -> {(q + 1) % 3}:"]
        try:
            res[q] = verify_phase(rule, ph, q, lines, a.mmax)
            r = res[q]
            lines.append(f"  OK: C(m, {q}) -> C(m + 2, {(q + 1) % 3}) in {r['a']} m + {r['b']} steps for every even m >= {r['m0']} (m = {r['K1']} + {r['p']} n + {r['e']}, n >= {r['nmin']})")
        except Fail as f:
            all_ok = False
            lines.append(f"  FAILED: {f}")
        out.extend(lines)
    # brute force over m = 2, 4, .., mmax, three phases
    if res and len(res) == 3 and not a.skip_brute:
        bad = 0
        cnt = 0
        mismatches = []
        for q in range(3):
            for m in range(2, a.mmax + 1, 2):
                r = run_cycle(rule, ph[q], m)
                cnt += 1
                want = 12 * m + (934, 1058, 898)[q] if rule == "RLRLLL" else None
                good = r["ok"] and closes(rule, ph, q, m)
                steps_ok = want is None or r["steps"] == want
                if not (good and steps_ok):
                    bad += 1
                    if len(mismatches) < 5:
                        mismatches.append((q, m, r["ok"] and r["steps"], want, good))
        out.append(f"brute force m = 2..{a.mmax} step 2, three phases ({cnt} runs): " + ("all end in C(m + 2, q + 1) with 12 m + (934, 1058, 898)[q] steps" if not bad else f"{bad} MISMATCHES, first {mismatches}"))
        all_ok &= not bad
        # compare the symbolic law with the brute-force step counts
        sym_ok = all(res[q]["a"] == 12 and res[q]["b"] == (934, 1058, 898)[q] for q in range(3)) if rule == "RLRLLL" else None
        out.append(f"symbolic law equals (12, 934/1058/898): {sym_ok}")
    elif res and len(res) == 3:
        pass
    out.append("RESULT: " + ("CLOSED (independent verifier)" if all_ok else "NOT CLOSED"))
    print("\n".join(out))


if __name__ == "__main__":
    main()
