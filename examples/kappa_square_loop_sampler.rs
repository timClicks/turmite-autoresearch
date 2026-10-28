// Square-loop (H-loop) instrument: experiments/archive/2026-10-kappa-square-loop.
//
// usage: kappa_square_loop_sampler MAX_LOG2 [GRID [MIN_LOG2]] < specs > loops.csv
// Specs: RULE@SEED (PatchedAnt, radius 2), pw:Q:SEED (PersistentWalk), rotor:SEED. Same board, escape rule, octave
// windows and boundary-step definition as `turmite::probe::probe_walker`; the stepping loop is copied (not shared)
// because src/probe.rs is being edited by another session. tests/kappa_square_loop.rs includes this file with
// #[path] and checks it against probe_walker and against a store-the-whole-path reference.
//
// Definitions (README of the experiment; fixed before any loop data):
//   step s (pre-index t = s - 1) starts on cell p_t, reads colour c_t, turns by d_t = (heading' - heading) mod 4, moves.
//   LOOP STEP at s >= 4: the position after step s equals the start cell of step s-3, and the turns of steps s-3..s
//   are the same letter (d = 1 four times, or d = 3 four times). Chirality-agnostic. (A closed 4-path of four equal
//   turns is exactly a 2x2 lap.)
//   LEAD-COLOUR loop step: a loop step whose four colours read (c_{t-3..t}) are all < lead (lead = length of the
//   rule's opening same-letter run; 0 for walkers without a rule, so none of their loops are lead-colour).
//   OTHER loop step: any other loop step.
//   ENTRY: a loop step whose predecessor step was not a loop step; kind = kind of that step.
//   b / i: the step starts on a cell with / without an unvisited 4-neighbour (the probe's boundary step).
//   LAPS: maximal runs of consecutive lead-colour loop steps; a run of L steps is (L+3)/4 laps (a pure k-lap trap is
//   4k-3 loop steps). Counted in the window of the first step after the run; runs cut by the end of the run are lost.
use rayon::prelude::*;
use turmite::walkers::{PatchedAnt, PersistentWalk, Rotor, Walker};
use turmite::{DIRS, Rule};

const UNVISITED: u8 = u8::MAX;

struct Region {
    unv: Vec<u8>,
    nbr: [isize; 4],
    area: u64,
    perimeter: u64,
}

impl Region {
    fn new(size: usize) -> Region {
        let s = size as isize;
        Region { unv: vec![UNVISITED; size * size], nbr: [-s, 1, s, -1], area: 0, perimeter: 0 }
    }
    fn visited(&self, idx: usize) -> bool {
        self.unv[idx] != UNVISITED
    }
    fn on_boundary(&self, idx: usize) -> bool {
        self.visited(idx) && self.unv[idx] > 0
    }
    fn visit(&mut self, idx: usize) {
        let mut u = 0u8;
        for d in self.nbr {
            let j = (idx as isize + d) as usize;
            if self.unv[j] == UNVISITED {
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

/// One window's counters. Indices: [lead?][boundary?] with lead = 0 other / 1 lead-colour; boundary = 0 interior / 1 boundary.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Win {
    pub k: u32,
    pub t_end: u64,
    pub steps: u64,
    pub area: u64,
    pub perimeter: u64,
    pub new_cells: u64,
    pub boundary_steps: u64,
    pub loops: [[u64; 2]; 2],
    pub entries: [[u64; 2]; 2],
    /// Completed lead-colour loop runs by laps: [0..8] = 1..8 laps, [8] = more than 8.
    pub laps: [u64; 9],
}

#[derive(Clone, Debug)]
pub struct Out {
    pub windows: Vec<Win>,
    pub escaped: bool,
}

/// Run `walker` for 2^max_log2 steps; emit windows (octaves) min_log2 <= k < max_log2. `lead` as in the header comment.
pub fn run_walker<W: Walker>(mut walker: W, lead: u8, size: usize, min_log2: u32, max_log2: u32) -> Out {
    assert!(min_log2 >= 1);
    let c = (size / 2) as i64;
    let mut colour = vec![0u8; size * size];
    if W::RANDOM_INIT {
        for (i, cell) in colour.iter_mut().enumerate() {
            let (gx, gy) = ((i % size) as i64, (i / size) as i64);
            *cell = walker.initial_cell(gx - c, gy - c);
        }
    }
    let mut region = Region::new(size);
    let s = size as isize;
    let (mut x, mut y, mut h) = (0i64, 0i64, 0u8);
    let mut idx = (c * size as i64 + c) as usize;
    region.visit(idx);

    // Last four steps (start cell, turn, colour read), slot = pre-index mod 4.
    let (mut r_start, mut r_turn, mut r_col) = ([0usize; 4], [0u8; 4], [0u8; 4]);
    let (mut prev_loop, mut lead_run) = (false, 0u64);
    let mut windows = vec![];
    let mut escaped = false;
    let mut t: u64 = 0;
    for k in 0..max_log2 {
        let t_end = 1u64 << (k + 1);
        let mut w = Win { k, t_end, steps: t_end - (1u64 << k), ..Win::default() };
        while t < t_end {
            let b = region.on_boundary(idx);
            if b {
                w.boundary_steps += 1;
            }
            let (start, col, h0) = (idx, colour[idx], h);
            walker.step(&mut colour[idx], &mut h);
            let (dx, dy) = DIRS[h as usize];
            x += dx as i64;
            y += dy as i64;
            idx = (idx as isize + dy as isize * s + dx as isize) as usize;
            let cur = (t & 3) as usize;
            (r_start[cur], r_turn[cur], r_col[cur]) = (start, (h.wrapping_sub(h0)) & 3, col);
            let old = (cur + 1) & 3; // the step three before this one
            let is_loop = t >= 3 && r_start[old] == idx && r_turn[0] == r_turn[1] && r_turn[1] == r_turn[2] && r_turn[2] == r_turn[3] && (r_turn[0] == 1 || r_turn[0] == 3);
            t += 1;
            if !region.visited(idx) {
                w.new_cells += 1;
                region.visit(idx);
            }
            let is_lead = is_loop && lead > 0 && r_col.iter().all(|&v| v < lead);
            if is_loop {
                w.loops[is_lead as usize][b as usize] += 1;
                if !prev_loop {
                    w.entries[is_lead as usize][b as usize] += 1;
                }
            }
            if is_lead {
                lead_run += 1;
            } else if lead_run > 0 {
                w.laps[(((lead_run + 3) / 4).min(9) - 1) as usize] += 1;
                lead_run = 0;
            }
            prev_loop = is_loop;
            if x.abs() >= c - 2 || y.abs() >= c - 2 {
                escaped = true;
                break;
            }
        }
        if escaped {
            break;
        }
        if k >= min_log2 {
            w.area = region.area;
            w.perimeter = region.perimeter;
            windows.push(w);
        }
    }
    Out { windows, escaped }
}

/// Opening same-letter run length of a rule string (the parent's `lead`).
pub fn lead_of(rule: &str) -> u8 {
    let f = rule.chars().next().unwrap();
    rule.chars().take_while(|&ch| ch == f).count() as u8
}

pub const CSV_HEADER: &str = "rule,k,t,steps,escaped,area,perimeter,new_cells,boundary_steps,loop_lead_b,loop_lead_i,loop_other_b,loop_other_i,entry_lead_b,entry_lead_i,entry_other_b,entry_other_i,laps_1,laps_2,laps_3,laps_4,laps_5,laps_6,laps_7,laps_8,laps_gt8\n";

pub fn run_spec(spec: &str, size: usize, min_log2: u32, max_log2: u32) -> Out {
    if let Some(seed) = spec.strip_prefix("rotor:") {
        run_walker(Rotor { seed: seed.parse().unwrap() }, 0, size, min_log2, max_log2)
    } else if let Some(p) = spec.strip_prefix("pw:") {
        let (q, seed) = p.split_once(':').unwrap();
        run_walker(PersistentWalk::new(seed.parse().unwrap(), q.parse().unwrap()), 0, size, min_log2, max_log2)
    } else if let Some((rule, seed)) = spec.split_once('@') {
        run_walker(PatchedAnt::new(&rule.parse::<Rule>().unwrap(), seed.parse().unwrap(), 2), lead_of(rule), size, min_log2, max_log2)
    } else {
        panic!("bad spec {spec}")
    }
}

pub fn csv_rows(spec: &str, o: &Out) -> String {
    let mut s = String::new();
    for w in &o.windows {
        let l = &w.loops;
        let e = &w.entries;
        s += &format!(
            "{spec},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            w.k, w.t_end, w.steps, o.escaped, w.area, w.perimeter, w.new_cells, w.boundary_steps,
            l[1][1], l[1][0], l[0][1], l[0][0], e[1][1], e[1][0], e[0][1], e[0][0]
        );
        for v in w.laps {
            s += &format!(",{v}");
        }
        s.push('\n');
    }
    s
}

/// Whole batch as CSV text; rayon `collect` keeps input order, so bytes do not depend on the thread count.
pub fn batch_csv(specs: &[String], size: usize, min_log2: u32, max_log2: u32, progress: bool) -> String {
    let done = std::sync::atomic::AtomicUsize::new(0);
    let blocks: Vec<String> = specs
        .par_iter()
        .map(|sp| {
            let o = run_spec(sp, size, min_log2, max_log2);
            let n = done.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
            if progress && n % 200 == 0 {
                eprintln!("{n}");
            }
            csv_rows(sp, &o)
        })
        .collect();
    let mut out = String::from(CSV_HEADER);
    for b in blocks {
        out += &b;
    }
    out
}

#[allow(dead_code)]
fn main() {
    use std::io::Write;
    let a: Vec<String> = std::env::args().collect();
    let max_log2: u32 = a[1].parse().unwrap();
    let size: usize = a.get(2).map(|s| s.parse().unwrap()).unwrap_or(8192);
    let min_log2: u32 = a.get(3).map(|s| s.parse().unwrap()).unwrap_or(20);
    let specs: Vec<String> = std::io::stdin().lines().map(|l| l.unwrap().trim().to_string()).filter(|l| !l.is_empty()).collect();
    eprintln!("{} specs", specs.len());
    let out = batch_csv(&specs, size, min_log2, max_log2, true);
    std::io::stdout().lock().write_all(out.as_bytes()).unwrap();
}
