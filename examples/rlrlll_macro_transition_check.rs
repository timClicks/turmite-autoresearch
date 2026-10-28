//! experiments/archive/2026-10-rlrlll-macro-transition, Stage 2: check that the proposed sweeper family is closed.
//! usage: rlrlll_macro_transition_check RULE CANONICAL_TXT
//!
//! The canonical file (scripts/extract_canonical.py) proposes three phases q = 0, 1, 2. Phase q is the configuration
//! C(m, q): on columns [x_f - WEST, x_f + width) the rows `top_q`, then the bulk row repeated m times, then `bottom`;
//! every other cell west of x_f + width is colour 0; the ant at (x_f + dx, top + dy) with heading h. Cells east of
//! the strip are arbitrary: the check fails if the ant ever goes there.
//!
//! For each q the checker runs C(m, q) with m symbolic until the front (minimum x reached) has moved 3 columns west,
//! and shows that the result is C(m + d_q, q + 1 mod 3), giving T_q(m) = a_q m + b_q steps, for every even
//! m >= mu_q. Counts are kept as a j + b with m = 2j: the descent's moving frame has period 2 rows, so the bulk is
//! crossed two rows at a time, and m is even in every observed phase (it grows by 2 per cycle).
//! Every concrete step is a `reference::Ant` step. A symbolic band `r^n` is crossed only through a shift lemma
//! `A.r -> r'.A` (or `r.A -> A.r'` going up): a finite run of `reference::Ant` on the H + 1 rows A.r alone, which
//! must not touch any other row, column or a new front column and must end with the ant one row on, in the same
//! state relative to A, with A reproduced. By induction on n, A.r^n -> r'^n.A in n s steps, for every n >= 0. When no
//! lemma applies, one row is peeled off the band, which needs n >= 1 and so adds a lower bound on m. A band may
//! hold a block of several rows (period p); a lemma may regroup k copies of the block into one.
use std::collections::HashMap;
use turmite::reference::Ant;
use turmite::{DIRS, Rule};

const WEST: usize = 4;
const H_MAX: usize = 48;
const S_MAX: u64 = 400;

type Row = Vec<u8>;

/// a * m + b, or infinitely many (the blank half-planes above and below).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum Count {
    Lin(i64, i64),
    Inf,
}

#[derive(Clone, Debug)]
enum Seg {
    Rows(Vec<Row>),
    /// A block of rows repeated `Count` times.
    Rep(Vec<Row>, Count),
}

struct Phase {
    m: i64,
    dx: i64,
    dy: i64,
    h: u8,
    top: Vec<Row>,
    bulk: Row,
    bottom: Vec<Row>,
}

fn parse_row(s: &str) -> Row {
    let mut r = vec![0u8; WEST];
    r.extend(s.bytes().map(|c| if c == b'.' { 0 } else { c - b'0' }));
    r
}

fn parse(text: &str) -> Vec<Phase> {
    let mut out = Vec::new();
    let mut lines = text.lines().filter(|l| !l.starts_with('#'));
    while let Some(l) = lines.next() {
        let f: Vec<&str> = l.split_whitespace().collect();
        assert_eq!(f[0], "phase");
        let (m, dx, dy, h) = (f[5].parse().unwrap(), f[7].parse().unwrap(), f[8].parse().unwrap(), f[9].parse().unwrap());
        let nt: usize = lines.next().unwrap().split_whitespace().nth(1).unwrap().parse().unwrap();
        let top = (0..nt).map(|_| parse_row(lines.next().unwrap())).collect();
        assert_eq!(lines.next().unwrap(), "bulk");
        let bulk = parse_row(lines.next().unwrap());
        let nb: usize = lines.next().unwrap().split_whitespace().nth(1).unwrap().parse().unwrap();
        let bottom = (0..nb).map(|_| parse_row(lines.next().unwrap())).collect();
        out.push(Phase { m, dx, dy, h, top, bulk, bottom });
    }
    out
}

/// A finite run of the reference ant on a stack of rows. Coordinates: x = column in the strip, y = row index.
/// Returns None if the ant leaves the rows, the strip, reaches a column west of `xmin`, or would read row `sentinel`,
/// before `done` holds.
fn run_patch(
    rule: &Rule,
    rows: &[Row],
    pos: (i32, i32),
    h: u8,
    xmin: i32,
    smax: u64,
    sentinel: usize,
    done: impl Fn(&Ant, &[Row]) -> bool,
) -> Option<(Vec<Row>, u64, (i32, i32), u8)> {
    let w = rows[0].len() as i32;
    let mut ant = Ant::new(rule.clone());
    ant.cells = to_cells(rows);
    ant.pos = pos;
    ant.heading = h;
    for s in 1..=smax {
        ant.step();
        let (x, y) = ant.pos;
        if x < xmin || x >= w || y < 0 || y >= rows.len() as i32 {
            return None;
        }
        let now = from_cells(&ant.cells, rows.len(), w as usize);
        if done(&ant, &now) {
            return Some((now, s, ant.pos, ant.heading));
        }
        if y as usize == sentinel {
            return None; // it would read a row the lemma does not own
        }
    }
    None
}

fn to_cells(rows: &[Row]) -> HashMap<(i32, i32), u8> {
    let mut m = HashMap::new();
    for (y, r) in rows.iter().enumerate() {
        for (x, &c) in r.iter().enumerate() {
            if c != 0 {
                m.insert((x as i32, y as i32), c);
            }
        }
    }
    m
}

fn from_cells(cells: &HashMap<(i32, i32), u8>, n: usize, w: usize) -> Vec<Row> {
    let mut rows = vec![vec![0u8; w]; n];
    for (&(x, y), &c) in cells {
        rows[y as usize][x as usize] = c;
    }
    rows
}

struct Sym {
    rule: Rule,
    above: Vec<Seg>, // nearest segment last
    below: Vec<Seg>, // nearest segment last
    ant: Ant,        // the focus rows live in ant.cells at y in ytop..=ybot
    ytop: i32,
    ybot: i32,
    width: usize,
    xmin: i32,
    steps: (i64, i64), // a * m + b
    mu: i64,           // the derivation holds for m >= mu
    lemmas: Vec<String>,
}

impl Sym {
    fn focus_rows(&self, y0: i32, y1: i32) -> Vec<Row> {
        let mut rows = vec![vec![0u8; self.width]; (y1 - y0 + 1) as usize];
        for (&(x, y), &c) in &self.ant.cells {
            if y >= y0 && y <= y1 {
                rows[(y - y0) as usize][x as usize] = c;
            }
        }
        rows
    }

    fn need(&mut self, c: Count) -> Result<(), String> {
        match c {
            Count::Inf => Ok(()),
            Count::Lin(0, b) if b >= 1 => Ok(()),
            Count::Lin(0, b) => Err(format!("peel from an empty band (count {b})")),
            Count::Lin(a, b) if a > 0 => {
                self.mu = self.mu.max((1 - b + a - 1).div_euclid(a));
                Ok(())
            }
            Count::Lin(a, b) => Err(format!("band count {a} m + {b} decreases with m")),
        }
    }

    /// Take the nearest row off a stack, recording the constraint that a band is non-empty.
    fn peel(&mut self, up: bool) -> Result<Row, String> {
        let stack = if up { &mut self.above } else { &mut self.below };
        let seg = stack.pop().ok_or("ran off the configuration")?;
        let (row, rest) = match seg {
            Seg::Rows(mut v) => {
                let r = if up { v.pop().unwrap() } else { v.remove(0) };
                (r, if v.is_empty() { None } else { Some(Seg::Rows(v)) })
            }
            Seg::Rep(block, c) => {
                self.need(c)?;
                let c2 = match c {
                    Count::Inf => Count::Inf,
                    Count::Lin(a, b) => Count::Lin(a, b - 1),
                };
                let stack = if up { &mut self.above } else { &mut self.below };
                if c2 != Count::Lin(0, 0) {
                    stack.push(Seg::Rep(block.clone(), c2));
                }
                let (row, rest) = if up {
                    (block[block.len() - 1].clone(), block[..block.len() - 1].to_vec())
                } else {
                    (block[0].clone(), block[1..].to_vec())
                };
                if !rest.is_empty() {
                    stack.push(Seg::Rows(rest));
                }
                return Ok(row);
            }
        };
        let stack = if up { &mut self.above } else { &mut self.below };
        if let Some(s) = rest {
            stack.push(s);
        }
        Ok(row)
    }

    fn materialise(&mut self, up: bool) -> Result<(), String> {
        let row = self.peel(up)?;
        let y = if up {
            self.ytop -= 1;
            self.ytop
        } else {
            self.ybot += 1;
            self.ybot
        };
        for (x, &c) in row.iter().enumerate() {
            if c != 0 {
                self.ant.cells.insert((x as i32, y), c);
            }
        }
        Ok(())
    }

    /// If the nearest segment in the direction of travel is a symbolic band, try to cross it with a shift lemma.
    /// Called when the ant has just stepped onto the band's nearest row (or is still inside the focus).
    fn try_shift(&mut self, up: bool) -> Result<bool, String> {
        let stack = if up { &self.above } else { &self.below };
        let (block, (ba, bb)) = match stack.last() {
            Some(Seg::Rep(r, Count::Lin(a, b))) if *a != 0 => (r.clone(), (*a, *b)),
            _ => return Ok(false),
        };
        let (ax, ay) = self.ant.pos;
        let h0 = self.ant.heading;
        // The moving frame may need several copies of the band's block per shift (the descent has period 2 rows
        // in a period-1 bulk); regroup the band as k-fold blocks when its count allows it.
        for k in 1..=4i64 {
            if ba % k != 0 || bb % k != 0 {
                continue;
            }
            let r: Vec<Row> = (0..k).flat_map(|_| block.iter().cloned()).collect();
            let c = Count::Lin(ba / k, bb / k);
            let p = r.len();
            for hgt in 1..=H_MAX {
                // A = the hgt focus rows next to the band. The ant is in A or on the band's nearest row.
                let (a0, a1) =
                    if up { (self.ytop, self.ytop + hgt as i32 - 1) } else { (self.ybot - hgt as i32 + 1, self.ybot) };
                if a0 < self.ytop || a1 > self.ybot || ay < a0 - 1 || ay > a1 + 1 || (up && ay > a1) || (!up && ay < a0) {
                    continue;
                }
                let a_rows = self.focus_rows(a0, a1);
                // Patch: [sentinel] block A (up) or A block [sentinel] (down). The sentinel stands for the row beyond
                // the block: the ant may arrive there at the final step but never read it.
                let blank = vec![0u8; self.width];
                let mut patch = Vec::new();
                let (start, want, sentinel);
                if up {
                    patch.push(blank);
                    patch.extend(r.iter().cloned());
                    patch.extend(a_rows.iter().cloned());
                    start = (ax, 1 + p as i32 + (ay - a0));
                    want = (ax, start.1 - p as i32);
                    sentinel = 0;
                } else {
                    patch.extend(a_rows.iter().cloned());
                    patch.extend(r.iter().cloned());
                    patch.push(blank);
                    start = (ax, ay - a0);
                    want = (ax, start.1 + p as i32);
                    sentinel = patch.len() - 1;
                }
                let a_ref = &a_rows;
                let res = run_patch(&self.rule, &patch, start, h0, self.xmin, S_MAX, sentinel, |ant, now| {
                    ant.pos == want
                        && ant.heading == h0
                        && if up { &now[1..1 + hgt] == a_ref.as_slice() } else { &now[p..p + hgt] == a_ref.as_slice() }
                });
                if let Some((now, s, _, _)) = res {
                    let r2: Vec<Row> = if up { now[1 + hgt..1 + hgt + p].to_vec() } else { now[..p].to_vec() };
                    let Count::Lin(ca, cb) = c else { unreachable!() };
                    // The induction covers n >= 0 copies; a negative count would be meaningless.
                    if ca > 0 {
                        self.mu = self.mu.max((-cb + ca - 1).div_euclid(ca));
                    } else {
                        return Err("band count decreases with m".into());
                    }
                    self.lemmas.push(format!(
                        "{} H={hgt} p={p} s={s}: band of ({ca} j + {cb}) blocks crossed",
                        if up { "up  " } else { "down" }
                    ));
                    // The far focus rows stay behind, the band is rewritten to r2, and A (with the ant at the same
                    // relative place) sits beyond it. Keep absolute coordinates of A and the ant unchanged.
                    let (far0, far1) = if up { (a1 + 1, self.ybot) } else { (self.ytop, a0 - 1) };
                    let far = if far0 <= far1 { self.focus_rows(far0, far1) } else { vec![] };
                    if up {
                        self.above.pop();
                        if !far.is_empty() {
                            self.below.push(Seg::Rows(far));
                        }
                        self.below.push(Seg::Rep(r2, c));
                    } else {
                        self.below.pop();
                        if !far.is_empty() {
                            self.above.push(Seg::Rows(far));
                        }
                        self.above.push(Seg::Rep(r2, c));
                    }
                    self.ant.cells = to_cells(&a_rows).into_iter().map(|((x, y), v)| ((x, y + a0), v)).collect();
                    self.ytop = a0;
                    self.ybot = a1;
                    self.steps.0 += ca * s as i64;
                    self.steps.1 += cb * s as i64;
                    return Ok(true);
                }
            }
        }
        Ok(false)
    }

    fn step(&mut self) -> Result<(), String> {
        self.ant.step();
        self.steps.1 += 1;
        let x = self.ant.pos.0;
        if x < 0 || x >= self.width as i32 {
            return Err(format!("left the strip at column {x}"));
        }
        self.xmin = self.xmin.min(x);
        // The ant reads its new cell on the next step, so make sure it is concrete now.
        while self.ant.pos.1 < self.ytop || self.ant.pos.1 > self.ybot {
            let up = self.ant.pos.1 < self.ytop;
            if !self.try_shift(up)? {
                if std::env::var("CHECK_DEBUG").is_ok() && self.ybot - self.ytop < 80 {
                    eprintln!(
                        "peel {} at step {} ant {:?} h {} focus {}..={} xmin {}",
                        if up { "up" } else { "down" }, self.steps.1, self.ant.pos, self.ant.heading, self.ytop, self.ybot, self.xmin
                    );
                }
                self.materialise(up)?;
            }
        }
        Ok(())
    }

    /// All rows top to bottom (the ant's focus as one Rows segment), and the ant's offset into that list's focus.
    fn flatten(&self) -> (Vec<Seg>, usize) {
        let mut segs: Vec<Seg> = self.above.clone();
        let focus_index = segs.len();
        segs.push(Seg::Rows(self.focus_rows(self.ytop, self.ybot)));
        segs.extend(self.below.iter().rev().cloned());
        (segs, focus_index)
    }
}

/// Normal form: constant-count bands expanded, rows equal to an adjacent band absorbed into it, adjacent equal
/// bands merged, blank rows at both ends dropped. Returns segments and how many rows were dropped above `mark`
/// (a concrete row index from the top, used to locate the ant).
fn normalise(segs: Vec<Seg>) -> Vec<Seg> {
    let mut flat: Vec<Seg> = Vec::new();
    for s in segs {
        match s {
            Seg::Rep(block, Count::Lin(0, b)) => {
                for _ in 0..b {
                    flat.extend(block.iter().map(|r| Seg::Rows(vec![r.clone()])));
                }
            }
            Seg::Rep(block, Count::Lin(a, b)) if block.iter().all(|r| *r == block[0]) => {
                let n = block.len() as i64;
                flat.push(Seg::Rep(vec![block[0].clone()], Count::Lin(a * n, b * n)));
            }
            Seg::Rows(v) => flat.extend(v.into_iter().map(|r| Seg::Rows(vec![r]))),
            other => flat.push(other),
        }
    }
    // Merge single rows into neighbouring bands of the same row, and bands into bands.
    let mut changed = true;
    while changed {
        changed = false;
        let mut out: Vec<Seg> = Vec::new();
        for s in flat.drain(..) {
            if let Some(last) = out.last_mut() {
                match (&*last, &s) {
                    (Seg::Rep(r, c), Seg::Rows(v)) | (Seg::Rows(v), Seg::Rep(r, c)) if v.len() == 1 && r.len() == 1 && v[0] == r[0] => {
                        let c2 = add(*c, Count::Lin(0, 1));
                        let r2 = r.clone();
                        *out.last_mut().unwrap() = Seg::Rep(r2, c2);
                        changed = true;
                        continue;
                    }
                    (Seg::Rep(r, c), Seg::Rep(r2, c2)) if r == r2 => {
                        let c3 = add(*c, *c2);
                        let r3 = r.clone();
                        *out.last_mut().unwrap() = Seg::Rep(r3, c3);
                        changed = true;
                        continue;
                    }
                    _ => {}
                }
            }
            out.push(s);
        }
        flat = out;
    }
    let blank = |s: &Seg| match s {
        Seg::Rows(v) => v.iter().all(|r| r.iter().all(|&c| c == 0)),
        Seg::Rep(r, _) => r.iter().flatten().all(|&c| c == 0),
    };
    while flat.first().is_some_and(blank) {
        flat.remove(0);
    }
    while flat.last().is_some_and(blank) {
        flat.pop();
    }
    flat
}

fn add(a: Count, b: Count) -> Count {
    match (a, b) {
        (Count::Lin(a1, b1), Count::Lin(a2, b2)) => Count::Lin(a1 + a2, b1 + b2),
        _ => Count::Inf,
    }
}

fn shift_west(row: &Row, by: usize) -> Row {
    let mut r = vec![0u8; by];
    r.extend_from_slice(&row[..row.len() - by]);
    r
}

fn initial(p: &Phase) -> Vec<Seg> {
    vec![
        Seg::Rep(vec![vec![0; p.bulk.len()]], Count::Inf),
        Seg::Rows(p.top.clone()),
        Seg::Rep(vec![p.bulk.clone()], Count::Lin(2, 0)),
        Seg::Rows(p.bottom.clone()),
        Seg::Rep(vec![vec![0; p.bulk.len()]], Count::Inf),
    ]
}

/// Run phase p symbolically for one cycle; return the normalised result (re-anchored 3 columns west), the ant's
/// (dx, dy, h) relative to the new front and the first non-blank row, steps, mu and the lemmas used.
#[allow(clippy::type_complexity)]
fn cycle(rule: &Rule, p: &Phase) -> Result<(Vec<Seg>, (i64, i64, u8), (i64, i64), i64, Vec<String>), String> {
    let width = p.bulk.len();
    // Start with the top block as the focus; the bulk band and bottom below, blank above.
    let mut s = Sym {
        rule: rule.clone(),
        above: vec![Seg::Rep(vec![vec![0; width]], Count::Inf)],
        below: vec![
            Seg::Rep(vec![vec![0; width]], Count::Inf),
            Seg::Rows(p.bottom.clone()),
            Seg::Rep(vec![p.bulk.clone()], Count::Lin(2, 0)),
        ],
        ant: Ant::new(rule.clone()),
        ytop: 0,
        ybot: p.top.len() as i32 - 1,
        width,
        xmin: (WEST as i64 + p.dx) as i32,
        steps: (0, 0),
        mu: 0,
        lemmas: vec![],
    };
    s.ant.cells = to_cells(&p.top);
    s.ant.pos = ((WEST as i64 + p.dx) as i32, p.dy as i32);
    s.ant.heading = p.h;
    let front0 = WEST as i32; // x_f is column WEST
    while s.xmin > front0 - 3 {
        s.step()?;
        if s.steps.1 > 10_000_000 {
            return Err("no front advance within 1e7 concrete steps".into());
        }
    }
    // Re-anchor three columns west and normalise.
    let (segs, fi) = s.flatten();
    let ant_row_in_focus = (s.ant.pos.1 - s.ytop) as usize;
    let shifted: Vec<Seg> = segs
        .into_iter()
        .map(|g| match g {
            Seg::Rows(v) => Seg::Rows(v.iter().map(|r| shift_west(r, 3)).collect()),
            Seg::Rep(r, c) => Seg::Rep(r.iter().map(|x| shift_west(x, 3)).collect(), c),
        })
        .collect();
    // Locate the ant: count concrete rows from the first non-blank row; the ant must sit above every symbolic band.
    let mut rows_before = 0i64;
    let mut seen_nonblank = false;
    for (i, g) in shifted.iter().enumerate() {
        if i == fi {
            break;
        }
        match g {
            Seg::Rep(r, Count::Inf) if r.iter().flatten().all(|&c| c == 0) => {}
            Seg::Rows(v) => {
                for r in v {
                    if seen_nonblank || r.iter().any(|&c| c != 0) {
                        seen_nonblank = true;
                        rows_before += 1;
                    }
                }
            }
            _ => return Err("ant is below a symbolic band at the cycle boundary".into()),
        }
    }
    let Seg::Rows(focus) = &shifted[fi] else { unreachable!() };
    let mut dy = rows_before;
    for r in &focus[..ant_row_in_focus] {
        if seen_nonblank || r.iter().any(|&c| c != 0) {
            seen_nonblank = true;
            dy += 1;
        }
    }
    let dx = (s.ant.pos.0 + 3) as i64 - WEST as i64;
    let norm = normalise(shifted);
    Ok((norm, (dx, dy, s.ant.heading), s.steps, s.mu, s.lemmas))
}

fn same(a: &[Seg], b: &[Seg]) -> Result<Count, String> {
    // Expect Rows, Rep(bulk, count), Rows with equal rows; return result count minus expected count.
    if a.len() != b.len() {
        return Err(format!("segment counts differ: {} vs {}", a.len(), b.len()));
    }
    let mut diff = None;
    for (x, y) in a.iter().zip(b) {
        match (x, y) {
            (Seg::Rows(u), Seg::Rows(v)) if u == v => {}
            (Seg::Rep(r1, Count::Lin(a1, b1)), Seg::Rep(r2, Count::Lin(a2, b2))) if r1 == r2 && diff.is_none() => {
                diff = Some(Count::Lin(a1 - a2, b1 - b2));
            }
            _ => return Err("segments differ".into()),
        }
    }
    diff.ok_or_else(|| "no band".into())
}

/// Brute-force cross-check: build C(m, q) concretely, run the reference ant until the front has moved 3 columns,
/// and return (steps, the window re-anchored at the new front, ant (dx, dy, h)). Independent of the symbolic code.
fn concrete_cycle(rule: &Rule, p: &Phase, m: usize) -> Option<(u64, Vec<Row>, (i64, i64, u8))> {
    let mut rows: Vec<Row> = p.top.clone();
    rows.extend(std::iter::repeat_n(p.bulk.clone(), m));
    rows.extend(p.bottom.iter().cloned());
    let mut ant = Ant::new(rule.clone());
    ant.cells = to_cells(&rows);
    ant.pos = ((WEST as i64 + p.dx) as i32, p.dy as i32);
    ant.heading = p.h;
    let width = p.bulk.len() as i32;
    let mut xmin = ant.pos.0;
    while xmin > WEST as i32 - 3 {
        ant.step();
        if ant.pos.0 < 0 || ant.pos.0 >= width || ant.steps > 10_000_000 {
            return None;
        }
        xmin = xmin.min(ant.pos.0);
    }
    // Window of the same width anchored 3 columns west, all rows that hold a non-zero colour.
    let (ymin, ymax) = ant.cells.keys().fold((i32::MAX, i32::MIN), |(a, b), &(_, y)| (a.min(y), b.max(y)));
    let mut win = vec![vec![0u8; width as usize]; (ymax - ymin + 1) as usize];
    for (&(x, y), &c) in &ant.cells {
        let nx = x + 3;
        if nx < width {
            win[(y - ymin) as usize][nx as usize] = c;
        }
    }
    while win.first().is_some_and(|r| r.iter().all(|&c| c == 0)) {
        win.remove(0);
    }
    while win.last().is_some_and(|r| r.iter().all(|&c| c == 0)) {
        win.pop();
    }
    let top_row = ant.cells.iter().filter(|&(&(x, _), _)| x + 3 < width).map(|(&(_, y), _)| y).min().unwrap();
    Some((ant.steps, win, ((ant.pos.0 + 3) as i64 - WEST as i64, (ant.pos.1 - top_row) as i64, ant.heading)))
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let phases = parse(&std::fs::read_to_string(&a[2]).unwrap());
    assert_eq!(phases.len(), 3);
    let _ = DIRS;
    let mut all_ok = true;
    for q in 0..3 {
        let p = &phases[q];
        let nq = &phases[(q + 1) % 3];
        println!("phase {q} -> {}:", (q + 1) % 3);
        match cycle(&rule, p) {
            Err(e) => {
                println!("  FAILED: {e}");
                all_ok = false;
            }
            Ok((norm, ant, steps, mu, lemmas)) => {
                for l in &lemmas {
                    println!("  lemma {l}");
                }
                // Target: C(m', q+1) with m' symbolic; compare with m' = 1 m + 0 and read off the offset.
                let target = normalise(initial(nq));
                let want_ant = (nq.dx, nq.dy, nq.h);
                match same(&norm, &target) {
                    Ok(Count::Lin(da, db)) if ant == want_ant => {
                        // Counts are in j with m = 2j; report them in m.
                        println!(
                            "  OK: C(m, {q}) -> C(m + {db}, {}) in {}/2 m + {} steps, for all even m >= {}; ant {:?}{}",
                            (q + 1) % 3,
                            steps.0,
                            steps.1,
                            2 * mu,
                            ant,
                            if da != 0 { format!(" BUT band coefficient changed by {da}") } else { String::new() }
                        );
                        println!("  (proposal had m = {} for this phase; next phase m = {})", p.m, nq.m);
                        if da != 0 {
                            all_ok = false;
                        }
                    }
                    Ok(_) => {
                        println!("  FAILED: rows match but ant {:?} != expected {:?}", ant, want_ant);
                        all_ok = false;
                    }
                    Err(e) => {
                        println!("  FAILED: result is not C(m', {}): {e}", (q + 1) % 3);
                        all_ok = false;
                    }
                }
            }
        }
    }
    // Brute-force cross-check of the closure claim at small and moderate m, by the reference ant alone.
    let ms: Vec<usize> = vec![2, 4, 6, 8, 10, 20, 50, 100, 434];
    for q in 0..3 {
        let (p, nq) = (&phases[q], &phases[(q + 1) % 3]);
        for &m in &ms {
            let Some((steps, win, ant)) = concrete_cycle(&rule, p, m) else {
                println!("  concrete check phase {q}, m = {m}: MISMATCH (left the strip or no front advance)");
                all_ok = false;
                continue;
            };
            let mut want: Vec<Row> = nq.top.clone();
            want.extend(std::iter::repeat_n(nq.bulk.clone(), m + 2));
            want.extend(nq.bottom.iter().cloned());
            let ok = win == want && ant == (nq.dx, nq.dy, nq.h);
            println!("  concrete check phase {q}, m = {m}: {steps} steps, result {}", if ok { "C(m + 2, next)" } else { "MISMATCH" });
            all_ok &= ok;
        }
    }
    println!("{}", if all_ok { "CLOSED: the family is invariant" } else { "NOT CLOSED" });
}
