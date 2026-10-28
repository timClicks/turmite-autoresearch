//! Colour-resolved boundary occupancy (W4 of experiments/archive/2026-10-kappa-rule-space).
//!
//! The same octave windows (2^k, 2^(k+1)] and the same boundary definition as `probe`
//! (a visited cell with at least one never-visited 4-neighbour, tested at the start of a
//! step), but every count is also split by the colour of the cell the walker stands on
//! *before* the step. With m_k the fraction of a window's steps that start on colour k,
//! f_k the fraction of those that start on a boundary cell and kappa_k = f_k / (P/A),
//! probe's kappa is exactly sum_k m_k kappa_k.
//!
//! This duplicates `probe::Region` rather than touching it: `tests/colourflux.rs` checks
//! every field against a HashMap oracle and against `probe_walker`.

use crate::DIRS;
use crate::walkers::{AntWalker, Walker};
use crate::Rule;

/// Cell states above this are not representable (ants of length <= 16; rotor uses 0..4).
pub const MAXC: usize = 16;
const UNVISITED: u8 = u8::MAX;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FluxWindow {
    pub t_start: u64,
    pub t_end: u64,
    pub area: u64,
    pub perimeter: u64,
    pub new_cells: u64,
    pub boundary_steps: u64,
    /// Steps starting on a cell of each colour (colour before the step).
    pub steps_by_colour: [u64; MAXC],
    /// ...of which the cell was a boundary cell.
    pub boundary_by_colour: [u64; MAXC],
    /// Steps that entered a never-visited cell, by the colour of the cell they started on.
    pub new_by_colour: [u64; MAXC],
    /// Colours of all visited cells, and of boundary cells, at t_end.
    pub hist_all: [u64; MAXC],
    pub hist_boundary: [u64; MAXC],
}

pub struct FluxResult {
    pub windows: Vec<FluxWindow>,
    /// The walker got within two cells of the board edge before the last window finished.
    pub escaped: bool,
}

struct Region {
    size: usize,
    /// For visited cells: number of never-visited 4-neighbours. UNVISITED otherwise.
    unv: Vec<u8>,
    nbr: [isize; 4],
    area: u64,
    perimeter: u64,
    /// Bounding box in board coordinates, for the end-of-window scan.
    lo: (usize, usize),
    hi: (usize, usize),
}

impl Region {
    fn new(size: usize) -> Region {
        let s = size as isize;
        Region { size, unv: vec![UNVISITED; size * size], nbr: [-s, 1, s, -1], area: 0, perimeter: 0, lo: (usize::MAX, usize::MAX), hi: (0, 0) }
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
        let (gx, gy) = (idx % self.size, idx / self.size);
        self.lo = (self.lo.0.min(gx), self.lo.1.min(gy));
        self.hi = (self.hi.0.max(gx), self.hi.1.max(gy));
    }
}

pub fn flux(rule: &Rule, size: usize, min_log2: u32, max_log2: u32) -> FluxResult {
    flux_walker(AntWalker::new(rule), size, min_log2, max_log2)
}

/// Windows (2^k, 2^(k+1)] for min_log2 <= k < max_log2, as `probe::probe_walker`.
pub fn flux_walker<W: Walker>(mut walker: W, size: usize, min_log2: u32, max_log2: u32) -> FluxResult {
    assert!(min_log2 >= 1);
    let c = (size / 2) as i64;
    let mut colour = vec![0u8; size * size];
    if W::RANDOM_INIT {
        for (i, cell) in colour.iter_mut().enumerate() {
            let (gx, gy) = ((i % size) as i64, (i / size) as i64);
            *cell = walker.initial_cell(gx - c, gy - c);
        }
    }
    let mut reg = Region::new(size);
    let s = size as isize;

    let (mut x, mut y, mut h) = (0i64, 0i64, 0u8);
    let mut idx = (c * size as i64 + c) as usize;
    reg.visit(idx);

    let mut windows = vec![];
    let mut escaped = false;
    let mut t: u64 = 0;
    for k in 0..max_log2 {
        let (t_start, t_end) = (1u64 << k, 1u64 << (k + 1));
        let mut w = FluxWindow {
            t_start,
            t_end,
            area: 0,
            perimeter: 0,
            new_cells: 0,
            boundary_steps: 0,
            steps_by_colour: [0; MAXC],
            boundary_by_colour: [0; MAXC],
            new_by_colour: [0; MAXC],
            hist_all: [0; MAXC],
            hist_boundary: [0; MAXC],
        };
        while t < t_end {
            let col = colour[idx] as usize;
            debug_assert!(col < MAXC);
            w.steps_by_colour[col] += 1;
            if reg.unv[idx] != UNVISITED && reg.unv[idx] > 0 {
                w.boundary_steps += 1;
                w.boundary_by_colour[col] += 1;
            }
            walker.step(&mut colour[idx], &mut h);
            let (dx, dy) = DIRS[h as usize];
            x += dx as i64;
            y += dy as i64;
            idx = (idx as isize + dy as isize * s + dx as isize) as usize;
            t += 1;
            if reg.unv[idx] == UNVISITED {
                w.new_cells += 1;
                w.new_by_colour[col] += 1;
                reg.visit(idx);
            }
            if x.abs() >= c - 2 || y.abs() >= c - 2 {
                escaped = true;
                break;
            }
        }
        if escaped {
            break;
        }
        if k >= min_log2 {
            w.area = reg.area;
            w.perimeter = reg.perimeter;
            for gy in reg.lo.1..=reg.hi.1 {
                let row = gy * size;
                for gx in reg.lo.0..=reg.hi.0 {
                    let i = row + gx;
                    if reg.unv[i] != UNVISITED {
                        let col = colour[i] as usize;
                        w.hist_all[col] += 1;
                        if reg.unv[i] > 0 {
                            w.hist_boundary[col] += 1;
                        }
                    }
                }
            }
            windows.push(w);
        }
    }
    FluxResult { windows, escaped }
}
