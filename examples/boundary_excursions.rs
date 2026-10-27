//! boundary_excursions MAX_LOG2 [GRID] [--check] [--hist PATH] < specs.txt > windows.csv
//!
//! Interior excursion durations for the stage-1 collapse test
//! (experiments/2026-10-27-boundary-excursion-durations).
//!
//! Boundary and stepping copy src/probe.rs: a step is a boundary step iff it
//! *starts* on a visited cell with an unvisited 4-neighbour. An excursion is a
//! maximal run of steps that start off the boundary (evolving territory).
//! Completed durations are histogrammed by floor(log2(tau)); unresolved
//! excursions at window end are counted as right-censored (not in the hist).
//!
//! Specs: RULE, RULE@SEED, rotor:SEED, rw:SEED, mf:SEED (mean-field of
//! examples/kappa_uniform_baseline.rs / kappa_exposure_classes.rs),
//! cup:P:SEED (reflecting cup: RW on visited set; birth onto unvisited with
//! probability P, else stay — Revision 1 D calibrator).
//! `--check` compares every recorded window's (area, perimeter, new_cells,
//! boundary_steps) with probe::probe_walker and asserts the per-window step
//! budget boundary_steps + interior_steps = window length. For cup:1.0:SEED,
//! totals must match rw:SEED (accept-draw skipped at P=1).
use rayon::prelude::*;
use std::io::Write;
use std::sync::atomic::{AtomicBool, Ordering};
use turmite::probe::probe_walker;
use turmite::walkers::{PatchedAnt, RandomWalk, Rotor, Walker, splitmix_next};
use turmite::{DIRS, Rule};

static MUTANT: AtomicBool = AtomicBool::new(false);

const UNV: u8 = u8::MAX;
const MAX_BIN: usize = 40; // floor(log2(tau)) in 0..MAX_BIN

struct Region {
    unv: Vec<u8>,
    nbr: [isize; 4],
    area: u64,
    perimeter: u64,
}

impl Region {
    fn new(size: usize) -> Region {
        let s = size as isize;
        Region {
            unv: vec![UNV; size * size],
            nbr: [-s, 1, s, -1],
            area: 0,
            perimeter: 0,
        }
    }
    fn visited(&self, idx: usize) -> bool {
        self.unv[idx] != UNV
    }
    fn on_boundary(&self, idx: usize) -> bool {
        let native = self.visited(idx) && self.unv[idx] > 0;
        if MUTANT.load(Ordering::Relaxed) {
            // Visited non-boundary cells are reported as boundary (and vice versa).
            self.visited(idx) && !native
        } else {
            native
        }
    }
    fn visit(&mut self, idx: usize) {
        let mut u = 0u8;
        for d in self.nbr {
            let j = (idx as isize + d) as usize;
            if self.unv[j] == UNV {
                u += 1;
            } else {
                self.unv[j] -= 1;
                if self.unv[j] == 0 {
                    self.perimeter -= 1;
                }
            }
        }
        self.unv[idx] = u;
        if u > 0 {
            self.perimeter += 1;
        }
        self.area += 1;
    }
}

#[derive(Clone, Debug)]
struct Win {
    k: u32, // window-end exponent label (probe: k=1 for (1,2], …); stored as end_log2
    area: u64,
    perimeter: u64,
    new_cells: u64,
    boundary_steps: u64,
    interior_steps: u64,
    n_completed: u64,
    n_censored: u64,
    unresolved_steps: u64,
    sum_tau: u64,
    bins: [u64; MAX_BIN],
}

struct Out {
    wins: Vec<Win>,
    escaped: bool,
}

trait Mover {
    fn start_cell(&mut self, cur: usize, region: &Region) -> usize;
    fn advance(
        &mut self,
        at: usize,
        colour: &mut [u8],
        size: usize,
        region: &Region,
    ) -> (usize, i64, i64);
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
    fn advance(
        &mut self,
        at: usize,
        colour: &mut [u8],
        size: usize,
        _: &Region,
    ) -> (usize, i64, i64) {
        self.w.step(&mut colour[at], &mut self.h);
        let (dx, dy) = DIRS[self.h as usize];
        self.x += dx as i64;
        self.y += dy as i64;
        let s = size as isize;
        (
            (at as isize + dy as isize * s + dx as isize) as usize,
            self.x,
            self.y,
        )
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
    fn advance(
        &mut self,
        at: usize,
        _: &mut [u8],
        size: usize,
        _: &Region,
    ) -> (usize, i64, i64) {
        let s = size as isize;
        let d = [-s, 1, s, -1][(self.r & 3) as usize];
        let j = (at as isize + d) as usize;
        let c = (size / 2) as i64;
        let (x, y) = ((j % size) as i64 - c, (j / size) as i64 - c);
        (j, x, y)
    }
}

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
    fn advance(
        &mut self,
        at: usize,
        colour: &mut [u8],
        size: usize,
        region: &Region,
    ) -> (usize, i64, i64) {
        self.inner.advance(at, colour, size, region)
    }
}

/// Reflecting cup: simple random walk on the visited set; a proposed step onto
/// an unvisited cell is accepted with probability `p` (else stay). Revision 1
/// compact-domain D calibrator. At p = 1 the accept draw is skipped so the
/// trajectory matches `RandomWalk` with the same seed.
struct ReflectingCup {
    st: u64,
    p_q32: u64,
    p_is_one: bool,
    x: i64,
    y: i64,
}

impl ReflectingCup {
    fn new(seed: u64, p: f64) -> Self {
        assert!(p.is_finite() && (0.0..=1.0).contains(&p), "cup p in [0,1]");
        Self {
            st: seed,
            p_q32: (p * 4294967296.0) as u64,
            p_is_one: p >= 1.0,
            x: 0,
            y: 0,
        }
    }
}

impl Mover for ReflectingCup {
    fn start_cell(&mut self, cur: usize, _: &Region) -> usize {
        cur
    }
    fn advance(
        &mut self,
        at: usize,
        _: &mut [u8],
        size: usize,
        region: &Region,
    ) -> (usize, i64, i64) {
        let dir = (splitmix_next(&mut self.st) & 3) as usize;
        let (dx, dy) = DIRS[dir];
        let nx = self.x + dx as i64;
        let ny = self.y + dy as i64;
        let s = size as isize;
        let j = (at as isize + dy as isize * s + dx as isize) as usize;
        if region.visited(j) {
            self.x = nx;
            self.y = ny;
            return (j, self.x, self.y);
        }
        // Unvisited target: accept birth with probability p; else stay.
        if self.p_is_one {
            self.x = nx;
            self.y = ny;
            return (j, self.x, self.y);
        }
        let r = splitmix_next(&mut self.st);
        if (r >> 32) < self.p_q32 {
            self.x = nx;
            self.y = ny;
            return (j, self.x, self.y);
        }
        (at, self.x, self.y)
    }
}

fn run<M: Mover>(mut mv: M, mut colour: Vec<u8>, size: usize, max_log2: u32) -> Out {
    let c = (size / 2) as i64;
    let mut region = Region::new(size);
    let mut idx = (c * size as i64 + c) as usize;
    region.visit(idx);
    let mut wins = vec![];
    let mut escaped = false;
    let mut t: u64 = 0;

    // Excursion state carries across windows.
    let mut in_exc = false;
    let mut exc_len: u64 = 0;

    for k in 0..max_log2 {
        let t_end = 1u64 << (k + 1);
        let mut w = Win {
            k: k + 1, // probe-style end-exponent label
            area: 0,
            perimeter: 0,
            new_cells: 0,
            boundary_steps: 0,
            interior_steps: 0,
            n_completed: 0,
            n_censored: 0,
            unresolved_steps: 0,
            sum_tau: 0,
            bins: [0; MAX_BIN],
        };
        // Steps of an excursion that began before this window and are still open
        // contribute to unresolved_steps if still open at window end; completed
        // lengths include the full excursion (cross-window) so the duration law
        // is not truncated by octave cuts. Budget identity uses interior_steps
        // counted in-window only.
        while t < t_end {
            let at = mv.start_cell(idx, &region);
            let on_b = region.on_boundary(at);
            if on_b {
                w.boundary_steps += 1;
            } else {
                w.interior_steps += 1;
            }

            let (j, x, y) = mv.advance(at, &mut colour, size, &region);
            idx = j;
            t += 1;
            if !region.visited(idx) {
                w.new_cells += 1;
                region.visit(idx);
            }

            // Episode update from *start-of-step* boundary flag (on_b), matching
            // the definition "maximal run of steps that start off the boundary".
            // Transition is keyed only on consecutive start flags; we track the
            // previous start flag via in_exc/exc_len.
            // After counting this step:
            // - if !on_b: this step is interior; extend or start excursion
            // - if on_b: this step is boundary; if we were in an excursion, the
            //   excursion ended *before* this step (last interior step was the end)
            if !on_b {
                if !in_exc {
                    in_exc = true;
                    exc_len = 1;
                } else {
                    exc_len += 1;
                }
            } else if in_exc {
                // Completed with length exc_len (does not include this boundary step).
                let bin = (63 - exc_len.leading_zeros()) as usize; // floor(log2)
                if bin < MAX_BIN {
                    w.bins[bin] += 1;
                }
                w.n_completed += 1;
                w.sum_tau += exc_len;
                in_exc = false;
                exc_len = 0;
            }

            if x.abs() >= c - 2 || y.abs() >= c - 2 {
                escaped = true;
                break;
            }
        }

        if in_exc {
            w.n_censored = 1;
            w.unresolved_steps = exc_len; // full open length (may predate window)
            // Keep in_exc/exc_len so a later completion gets the full duration.
        }

        w.area = region.area;
        w.perimeter = region.perimeter;
        // Record from k_end >= 9 (2^8..), matching exposure-classes probe compare band start.
        if k + 1 >= 9 {
            wins.push(w);
        }
        if escaped {
            break;
        }
    }
    Out { wins, escaped }
}

fn run_cup(seed: u64, p: f64, size: usize, max_log2: u32) -> Out {
    run(
        ReflectingCup::new(seed, p),
        vec![0u8; size * size],
        size,
        max_log2,
    )
}

fn run_mf(seed: u64, size: usize, max_log2: u32) -> Out {
    let st = seed.wrapping_mul(0xD1B5_4A32_D192_ED03) ^ 0x2545_F491_4F6C_DD1D;
    let c = size / 2;
    let start = c * size + c;
    let mv = MeanFieldSync {
        inner: MeanField {
            st,
            cells: vec![start],
            r: 0,
        },
        seen: 1,
    };
    run(mv, vec![0u8; size * size], size, max_log2)
}

fn walker_out<W: Walker>(w: W, size: usize, max_log2: u32) -> Out {
    let c = (size / 2) as i64;
    let mut colour = vec![0u8; size * size];
    if W::RANDOM_INIT {
        for (i, cell) in colour.iter_mut().enumerate() {
            *cell = w.initial_cell((i % size) as i64 - c, (i / size) as i64 - c);
        }
    }
    run(WalkerMover { w, h: 0, x: 0, y: 0 }, colour, size, max_log2)
}

fn check_against_probe<W: Walker>(w: W, out: &Out, size: usize, max_log2: u32) {
    let pr = probe_walker(w, size, 8, max_log2);
    assert_eq!(pr.escaped, out.escaped, "escape flag");
    assert_eq!(pr.windows.len(), out.wins.len(), "window count");
    for (a, b) in pr.windows.iter().zip(&out.wins) {
        assert_eq!(a.t_end.trailing_zeros(), b.k, "k label");
        assert_eq!(
            (a.area, a.perimeter, a.new_cells, a.boundary_steps),
            (b.area, b.perimeter, b.new_cells, b.boundary_steps),
            "window k={}",
            b.k
        );
        let win_len = 1u64 << (b.k - 1);
        assert_eq!(
            b.boundary_steps + b.interior_steps,
            win_len,
            "step budget k={}",
            b.k
        );
    }
}

fn format_block(spec: &str, out: &Out) -> (String, String) {
    let mut win = String::new();
    let mut hist = String::new();
    for w in &out.wins {
        let l = if w.perimeter > 0 {
            w.area as f64 / w.perimeter as f64
        } else {
            f64::NAN
        };
        let steps = (w.boundary_steps + w.interior_steps) as f64;
        let kappa = if w.perimeter > 0 && w.area > 0 && steps > 0.0 {
            (w.boundary_steps as f64 / steps) / (w.perimeter as f64 / w.area as f64)
        } else {
            f64::NAN
        };
        let cens_share = if w.interior_steps > 0 {
            w.unresolved_steps as f64 / w.interior_steps as f64
        } else {
            0.0
        };
        win += &format!(
            "{spec},{},{},{},{},{},{},{},{},{},{},{:.6},{:.6},{:.6},{}\n",
            w.k,
            1u64 << w.k,
            w.area,
            w.perimeter,
            w.new_cells,
            w.boundary_steps,
            w.interior_steps,
            w.n_completed,
            w.n_censored,
            w.unresolved_steps,
            l,
            kappa,
            cens_share,
            out.escaped
        );
        for (b, &c) in w.bins.iter().enumerate() {
            if c > 0 {
                hist += &format!("{spec},{},{},{}\n", w.k, b, c);
            }
        }
        // Censored sentinel bin = -1
        if w.n_censored > 0 {
            hist += &format!("{spec},{},-1,{}\n", w.k, w.n_censored);
        }
    }
    (win, hist)
}

fn run_spec(s: &str, size: usize, max_log2: u32, check: bool) -> Out {
    if let Some(rest) = s.strip_prefix("cup:") {
        // cup:P:SEED
        let (p_str, seed_str) = rest
            .split_once(':')
            .unwrap_or_else(|| panic!("cup spec must be cup:P:SEED, got {s}"));
        let p: f64 = p_str.parse().expect("cup P");
        let seed: u64 = seed_str.parse().expect("cup SEED");
        let out = run_cup(seed, p, size, max_log2);
        if check {
            for w in &out.wins {
                let win_len = 1u64 << (w.k - 1);
                assert_eq!(
                    w.boundary_steps + w.interior_steps,
                    win_len,
                    "cup budget k={}",
                    w.k
                );
            }
            if (p - 1.0).abs() < 1e-12 {
                let rw = walker_out(RandomWalk { state: seed }, size, max_log2);
                assert_eq!(rw.escaped, out.escaped, "cup:1 vs rw escape");
                assert_eq!(rw.wins.len(), out.wins.len(), "cup:1 vs rw nwindows");
                for (a, b) in rw.wins.iter().zip(&out.wins) {
                    assert_eq!(
                        (a.area, a.perimeter, a.new_cells, a.boundary_steps),
                        (b.area, b.perimeter, b.new_cells, b.boundary_steps),
                        "cup:1.0:{seed} must match rw:{seed} at k={}",
                        b.k
                    );
                }
            }
        }
        out
    } else if let Some(seed) = s.strip_prefix("mf:") {
        let out = run_mf(seed.parse().unwrap(), size, max_log2);
        // MF has no probe_walker equivalent; check budget identity only.
        if check {
            for w in &out.wins {
                let win_len = 1u64 << (w.k - 1);
                assert_eq!(
                    w.boundary_steps + w.interior_steps,
                    win_len,
                    "mf budget k={}",
                    w.k
                );
            }
        }
        out
    } else if let Some(seed) = s.strip_prefix("rotor:") {
        let seed: u64 = seed.parse().unwrap();
        let out = walker_out(Rotor { seed }, size, max_log2);
        if check {
            check_against_probe(Rotor { seed }, &out, size, max_log2);
        }
        out
    } else if let Some(seed) = s.strip_prefix("rw:") {
        let seed: u64 = seed.parse().unwrap();
        let out = walker_out(RandomWalk { state: seed }, size, max_log2);
        if check {
            check_against_probe(RandomWalk { state: seed }, &out, size, max_log2);
        }
        out
    } else if let Some((rule, seed)) = s.split_once('@') {
        let rule: Rule = rule.parse().unwrap();
        let seed: u64 = seed.parse().unwrap();
        let out = walker_out(PatchedAnt::new(&rule, seed, 2), size, max_log2);
        if check {
            check_against_probe(PatchedAnt::new(&rule, seed, 2), &out, size, max_log2);
        }
        out
    } else {
        let rule: Rule = s.parse().unwrap();
        let out = walker_out(turmite::walkers::AntWalker::new(&rule), size, max_log2);
        if check {
            check_against_probe(turmite::walkers::AntWalker::new(&rule), &out, size, max_log2);
        }
        out
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let max_log2: u32 = a
        .get(1)
        .expect("usage: boundary_excursions MAX_LOG2 [GRID] [--check] [--hist PATH]")
        .parse()
        .unwrap();
    let size: usize = a
        .get(2)
        .filter(|s| !s.starts_with("--"))
        .map(|s| s.parse().unwrap())
        .unwrap_or(8192);
    let check = a.iter().any(|s| s == "--check");
    let mutant = a.iter().any(|s| s == "--mutant");
    if mutant {
        // C0: invert the boundary predicate so probe totals must disagree.
        MUTANT.store(true, Ordering::Relaxed);
    }
    let hist_path = a
        .iter()
        .position(|s| s == "--hist")
        .and_then(|i| a.get(i + 1))
        .cloned();
    let specs: Vec<String> = std::io::stdin()
        .lines()
        .map(|l| l.unwrap().trim().to_string())
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
        .collect();
    eprintln!(
        "{} specs, max_log2 {max_log2}, grid {size}, check {check}",
        specs.len()
    );
    let blocks: Vec<(String, String)> = specs
        .par_iter()
        .map(|s| {
            let out = run_spec(s, size, max_log2, check);
            format_block(s, &out)
        })
        .collect();

    let mut out = std::io::stdout().lock();
    writeln!(
        out,
        "spec,k,t_end,area,perimeter,new_cells,boundary_steps,interior_steps,n_completed,n_censored,unresolved_steps,L,kappa,censored_step_share,escaped"
    )
    .unwrap();
    let mut hist_buf = String::from("spec,k,log2_tau,count\n");
    for (w, h) in &blocks {
        out.write_all(w.as_bytes()).unwrap();
        hist_buf.push_str(h);
    }
    if let Some(path) = hist_path {
        std::fs::write(&path, &hist_buf).unwrap();
        eprintln!("wrote hist {}", path);
    } else {
        // Default: write hist next to a marker on stderr only if no path; require --hist in scripts.
        eprint!("(no --hist path; hist rows = {})\n", hist_buf.lines().count() - 1);
    }
}
