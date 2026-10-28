//! kappa_exposure_classes MAX_LOG2 [GRID] [--check] < specs.txt > out.csv
//!
//! Boundary occupation split by exposure class (experiment 2026-10-kappa-exposure-classes).
//! A boundary cell's class u (1..4) is its number of unvisited 4-neighbours. Per octave window of
//! S = 2^j steps, t in (2^j, 2^(j+1)] (output column `k` = j + 1, the window-end exponent, as in
//! the probe census; `steps` = S), it records for each u:
//! - b_u: steps starting on a class-u cell (sum over u = the probe's `boundary_steps`),
//! - f_u: those steps that start on the cell the walker entered as a new cell on the previous step
//!   (the forced first departure from a newborn cell),
//! - m_u: the sum over the same steps of P_u(t)/A(t) at step start, i.e. S times the time-averaged
//!   class-u share. b_u / m_u is a convention-free occupation ratio: exactly 1 in expectation for a
//!   walker uniform over the visited set at every instant, with no end-of-window reference;
//! - p_u: the class-u count at window end.
//!
//! Specs: `RULE` (blank board), `RULE@SEED` (5x5 random patch, as bin/probe), `rotor:SEED`,
//! `rw:SEED`, `mf:SEED` (mean-field walker of examples/kappa_uniform_baseline.rs: each step resample
//! a uniform visited cell, then step to a uniform random neighbour; uniform by construction).
//! Stepping and region bookkeeping copy src/probe.rs (same escape rule). `--check` additionally
//! compares every window with probe::probe_walker (area, perimeter, new_cells, boundary_steps,
//! fresh_nbrs = sum u b_u) and recounts p_u by scanning the board, panicking on any mismatch.
//! Those sums cannot see a mis-split between classes (a 1->2 and a 3->2 error cancel), so `--check`
//! also re-derives, at every step and from a separate visited bitmap, the start cell's class, the
//! newborn flag behind f_u and the class counts behind the shares summed into m_u (added
//! 2026-10-25; output unchanged, see the experiment NOTEBOOK).
use rayon::prelude::*;
use std::io::Write;
use turmite::probe::probe_walker;
use turmite::walkers::{PatchedAnt, RandomWalk, Rotor, Walker, splitmix_next};
use turmite::{DIRS, Rule};

const UNV: u8 = u8::MAX;

struct Region {
    unv: Vec<u8>,
    nbr: [isize; 4],
    area: u64,
    /// pc[u]: visited cells with exactly u unvisited neighbours (pc[0] = interior).
    pc: [u64; 5],
}

impl Region {
    fn new(size: usize) -> Region {
        let s = size as isize;
        Region { unv: vec![UNV; size * size], nbr: [-s, 1, s, -1], area: 0, pc: [0; 5] }
    }
    fn visited(&self, idx: usize) -> bool {
        self.unv[idx] != UNV
    }
    fn visit(&mut self, idx: usize) {
        let mut u = 0u8;
        for d in self.nbr {
            let j = (idx as isize + d) as usize;
            if self.unv[j] == UNV {
                u += 1;
            } else {
                self.pc[self.unv[j] as usize] -= 1;
                self.unv[j] -= 1;
                self.pc[self.unv[j] as usize] += 1;
            }
        }
        self.unv[idx] = u;
        self.pc[u as usize] += 1;
        self.area += 1;
    }
    fn shares(&self) -> [f64; 5] {
        let a = self.area as f64;
        [0.0, self.pc[1] as f64 / a, self.pc[2] as f64 / a, self.pc[3] as f64 / a, self.pc[4] as f64 / a]
    }
    fn scan(&self) -> [u64; 5] {
        let mut pc = [0u64; 5];
        for &u in &self.unv {
            if u != UNV {
                pc[u as usize] += 1;
            }
        }
        pc
    }
}

/// Independent recount used only by `--check`: its own visited bitmap and class counts, updated
/// without reading `Region`, so a bookkeeping error in `Region::visit` cannot hide in both.
struct Shadow {
    vis: Vec<bool>,
    nbr: [isize; 4],
    pc: [u64; 5],
    area: u64,
    born: usize,
}

impl Shadow {
    fn new(size: usize, start: usize) -> Shadow {
        let s = size as isize;
        let mut sh = Shadow { vis: vec![false; size * size], nbr: [-s, 1, s, -1], pc: [0; 5], area: 0, born: usize::MAX };
        sh.mark(start);
        sh.born = usize::MAX;
        sh
    }
    fn class(&self, idx: usize) -> usize {
        self.nbr.iter().filter(|&&d| !self.vis[(idx as isize + d) as usize]).count()
    }
    /// Mark the step-end cell; remember it as newborn when it was unvisited.
    fn mark(&mut self, idx: usize) {
        self.born = usize::MAX;
        if self.vis[idx] {
            return;
        }
        let around: Vec<usize> = self.nbr.iter().map(|&d| (idx as isize + d) as usize).filter(|&j| self.vis[j]).collect();
        for &j in &around {
            self.pc[self.class(j)] -= 1;
        }
        self.vis[idx] = true;
        for &j in &around {
            self.pc[self.class(j)] += 1;
        }
        self.pc[self.class(idx)] += 1;
        self.area += 1;
        self.born = idx;
    }
    fn shares(&self) -> [f64; 5] {
        let a = self.area as f64;
        [0.0, self.pc[1] as f64 / a, self.pc[2] as f64 / a, self.pc[3] as f64 / a, self.pc[4] as f64 / a]
    }
}

#[derive(Clone, Debug, Default)]
struct Win {
    k: u32,
    area: u64,
    p: [u64; 5],
    new_cells: u64,
    b: [u64; 5],
    f: [u64; 5],
    m: [f64; 5],
}

struct Out {
    wins: Vec<Win>,
    escaped: bool,
}

/// One step of the walker: given the step-start cell index, return the step-end index.
trait Mover {
    fn start_cell(&mut self, cur: usize, region: &Region) -> usize;
    fn advance(&mut self, at: usize, colour: &mut [u8], size: usize) -> (usize, i64, i64);
}

struct WalkerMover<W: Walker> {
    w: W,
    h: u8,
    x: i64,
    y: i64,
}

impl<W: Walker> Mover for WalkerMover<W> {
    fn start_cell(&mut self, cur: usize, _: &Region) -> usize {
        cur
    }
    fn advance(&mut self, at: usize, colour: &mut [u8], size: usize) -> (usize, i64, i64) {
        self.w.step(&mut colour[at], &mut self.h);
        let (dx, dy) = DIRS[self.h as usize];
        self.x += dx as i64;
        self.y += dy as i64;
        let s = size as isize;
        ((at as isize + dy as isize * s + dx as isize) as usize, self.x, self.y)
    }
}

struct MeanField {
    st: u64,
    cells: Vec<usize>,
    r: u64,
}

impl Mover for MeanField {
    fn start_cell(&mut self, _: usize, _: &Region) -> usize {
        self.r = splitmix_next(&mut self.st);
        self.cells[((self.r >> 8) % self.cells.len() as u64) as usize]
    }
    fn advance(&mut self, at: usize, _: &mut [u8], size: usize) -> (usize, i64, i64) {
        let s = size as isize;
        let d = [-s, 1, s, -1][(self.r & 3) as usize];
        let j = (at as isize + d) as usize;
        let c = (size / 2) as i64;
        let (x, y) = ((j % size) as i64 - c, (j / size) as i64 - c);
        (j, x, y)
    }
}

fn run<M: Mover>(mut mv: M, mut colour: Vec<u8>, size: usize, max_log2: u32, check: bool) -> Out {
    let c = (size / 2) as i64;
    let mut region = Region::new(size);
    let mut idx = (c * size as i64 + c) as usize;
    region.visit(idx);
    let mut share = region.shares();
    let mut newborn: usize = usize::MAX;
    let mut wins = vec![];
    let mut escaped = false;
    let mut t: u64 = 0;
    let mut shadow = check.then(|| Shadow::new(size, idx));
    for k in 0..max_log2 {
        let t_end = 1u64 << (k + 1);
        let mut w = Win { k, ..Default::default() };
        while t < t_end {
            let at = mv.start_cell(idx, &region);
            let u = region.unv[at] as usize;
            if let Some(sh) = &shadow {
                assert!(sh.vis[at], "step starts on an unvisited cell at t={t}");
                assert_eq!(sh.class(at), u, "start-cell class at t={t}");
                assert_eq!(sh.born == at, at == newborn, "newborn flag at t={t}");
                assert_eq!((sh.area, sh.shares()), (region.area, share), "class shares at t={t}");
            }
            for (m, s) in w.m.iter_mut().zip(share).skip(1) {
                *m += s;
            }
            if u > 0 {
                w.b[u] += 1;
                if at == newborn {
                    w.f[u] += 1;
                }
            }
            let (j, x, y) = mv.advance(at, &mut colour, size);
            idx = j;
            if let Some(sh) = &mut shadow {
                sh.mark(j);
            }
            t += 1;
            newborn = usize::MAX;
            if !region.visited(idx) {
                w.new_cells += 1;
                region.visit(idx);
                share = region.shares();
                newborn = idx;
            }
            if x.abs() >= c - 2 || y.abs() >= c - 2 {
                escaped = true;
                break;
            }
        }
        if escaped {
            break;
        }
        w.area = region.area;
        w.p = region.pc;
        if check {
            assert_eq!(region.scan(), region.pc, "class counts disagree with a board scan at k={k}");
        }
        if k >= 8 {
            wins.push(w);
        }
    }
    Out { wins, escaped }
}

/// The mean-field walker needs the growing cell list inside the mover; run it with its own loop
/// wrapper so the list stays in sync (cells are appended in visit order).
fn run_mf(seed: u64, size: usize, max_log2: u32, check: bool) -> Out {
    // Seed mixing as in examples/kappa_uniform_baseline.rs.
    let st = seed.wrapping_mul(0xD1B5_4A32_D192_ED03) ^ 0x2545_F491_4F6C_DD1D;
    let c = size / 2;
    let start = c * size + c;
    let mv = MeanFieldSync { inner: MeanField { st, cells: vec![start], r: 0 }, seen: 1 };
    run(mv, vec![0u8; size * size], size, max_log2, check)
}

/// MeanField whose cell list is refreshed from the region's visit order: a cell is new exactly when
/// the region's area grows, and the only cell that can become visited in a step is the step's end.
struct MeanFieldSync {
    inner: MeanField,
    seen: u64,
}

impl Mover for MeanFieldSync {
    fn start_cell(&mut self, cur: usize, region: &Region) -> usize {
        if region.area > self.seen {
            debug_assert_eq!(region.area, self.seen + 1);
            self.inner.cells.push(cur);
            self.seen = region.area;
        }
        self.inner.start_cell(cur, region)
    }
    fn advance(&mut self, at: usize, colour: &mut [u8], size: usize) -> (usize, i64, i64) {
        self.inner.advance(at, colour, size)
    }
}

fn walker_out<W: Walker>(w: W, size: usize, max_log2: u32, check: bool) -> Out {
    let c = (size / 2) as i64;
    let mut colour = vec![0u8; size * size];
    if W::RANDOM_INIT {
        for (i, cell) in colour.iter_mut().enumerate() {
            *cell = w.initial_cell((i % size) as i64 - c, (i / size) as i64 - c);
        }
    }
    run(WalkerMover { w, h: 0, x: 0, y: 0 }, colour, size, max_log2, check)
}

fn check_against_probe<W: Walker>(w: W, out: &Out, size: usize, max_log2: u32) {
    let pr = probe_walker(w, size, 8, max_log2);
    assert_eq!(pr.escaped, out.escaped, "escape flag");
    assert_eq!(pr.windows.len(), out.wins.len(), "window count");
    for (a, b) in pr.windows.iter().zip(&out.wins) {
        let p: u64 = b.p[1..].iter().sum();
        let bs: u64 = b.b[1..].iter().sum();
        let fresh: u64 = (1..5).map(|u| u as u64 * b.b[u]).sum();
        assert_eq!(a.t_end.trailing_zeros(), b.k + 1, "k");
        assert_eq!((a.area, a.perimeter, a.new_cells, a.boundary_steps, a.fresh_nbrs), (b.area, p, b.new_cells, bs, fresh), "window k={}", b.k);
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let max_log2: u32 = a[1].parse().unwrap();
    let size: usize = a.get(2).filter(|s| !s.starts_with("--")).map(|s| s.parse().unwrap()).unwrap_or(4096);
    let check = a.iter().any(|s| s == "--check");
    let specs: Vec<String> = std::io::stdin().lines().map(|l| l.unwrap().trim().to_string()).filter(|l| !l.is_empty() && !l.starts_with('#')).collect();
    eprintln!("{} specs, max_log2 {max_log2}, grid {size}, check {check}", specs.len());
    let blocks: Vec<String> = specs
        .par_iter()
        .map(|s| {
            let out = if let Some(seed) = s.strip_prefix("mf:") {
                run_mf(seed.parse().unwrap(), size, max_log2, check)
            } else if let Some(seed) = s.strip_prefix("rotor:") {
                let seed: u64 = seed.parse().unwrap();
                let o = walker_out(Rotor { seed }, size, max_log2, check);
                if check {
                    check_against_probe(Rotor { seed }, &o, size, max_log2);
                }
                o
            } else if let Some(seed) = s.strip_prefix("rw:") {
                let seed: u64 = seed.parse().unwrap();
                let o = walker_out(RandomWalk { state: seed }, size, max_log2, check);
                if check {
                    check_against_probe(RandomWalk { state: seed }, &o, size, max_log2);
                }
                o
            } else if let Some((rule, seed)) = s.split_once('@') {
                let rule: Rule = rule.parse().unwrap();
                let seed: u64 = seed.parse().unwrap();
                let o = walker_out(PatchedAnt::new(&rule, seed, 2), size, max_log2, check);
                if check {
                    check_against_probe(PatchedAnt::new(&rule, seed, 2), &o, size, max_log2);
                }
                o
            } else {
                let rule: Rule = s.parse().unwrap();
                let o = walker_out(turmite::walkers::AntWalker::new(&rule), size, max_log2, check);
                if check {
                    check_against_probe(turmite::walkers::AntWalker::new(&rule), &o, size, max_log2);
                }
                o
            };
            let mut txt = String::new();
            for w in &out.wins {
                txt += &format!(
                    "{s},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{:.6},{:.6},{:.6},{:.6},{}\n",
                    w.k + 1,
                    w.area,
                    w.p[1], w.p[2], w.p[3], w.p[4],
                    w.new_cells,
                    w.b[1], w.b[2], w.b[3], w.b[4],
                    w.f[1], w.f[2], w.f[3], w.f[4],
                    w.p[0],
                    1u64 << w.k,
                    w.m[1], w.m[2], w.m[3], w.m[4],
                    out.escaped
                );
            }
            txt
        })
        .collect();
    let mut o = std::io::stdout().lock();
    writeln!(o, "spec,k,area,p1,p2,p3,p4,new_cells,b1,b2,b3,b4,f1,f2,f3,f4,p0,steps,m1,m2,m3,m4,escaped").unwrap();
    for b in blocks {
        o.write_all(b.as_bytes()).unwrap();
    }
}
