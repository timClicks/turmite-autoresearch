//! The octave-window probe (`probe.rs`) on three lattices: square (4 neighbours), hexagonal (6, axial offsets of
//! `ext::HEX_DIRS`) and triangular cells (3, parity dependent, as `ext::TriSim`). Same window definitions as `probe.rs`:
//! a *boundary step* starts on a visited cell with >= 1 unvisited neighbour, a *birth* enters a never-visited cell,
//! `perimeter` counts visited cells with >= 1 unvisited neighbour. Only the fields the lattice c-law study needs are
//! produced (no radius of gyration or ant-spread sums). Movers: the lattice ant, a uniform random walk and a
//! mean-field walker (resample uniformly over visited cells, then step to a uniform neighbour).
//!
//! Neighbour order is part of the definition because the random movers pick `splitmix % z`:
//! square N,E,S,W (`DIRS`); hex `HEX_DIRS` order; triangular `[x-1, x+1, vertical]`
//! (vertical = y+1 on up triangles, y-1 on down triangles).

use crate::ext::{HEX_DIRS, hex_turns, tri_step};
use crate::walkers::splitmix_next;
use crate::DIRS;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Lattice {
    Square,
    Hex,
    Tri,
    /// Square lattice with 8 neighbours (Moore). Headings N, NE, E, SE, S, SW, W, NW; letters `r`/`l` turn 45 degrees (loop 8), `R`/`L` 90 degrees (loop 4).
    Moore,
}

#[derive(Clone, Debug)]
pub enum Mover {
    /// Rule letters: `L`/`R` on square and triangular; `r`, `l`, `R`, `L` on hex.
    Ant(String),
    /// Uniform random walk; the seed starts the SplitMix64 stream.
    RandomWalk(u64),
    MeanField(u64),
}

#[derive(Clone, Debug, PartialEq)]
pub struct LWindow {
    pub k: u32,
    pub area: u64,
    pub perimeter: u64,
    pub new_cells: u64,
    pub boundary_steps: u64,
    pub fresh_nbrs: u64,
    /// Bounding box of visited cells in grid index coordinates (hex: axial, triangular: columns of half-edges).
    pub width: u32,
    pub height: u32,
}

#[derive(Clone, Debug)]
pub struct LResult {
    pub windows: Vec<LWindow>,
    pub escaped: bool,
}

pub const MOORE_DIRS: [(i32, i32); 8] = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)];

const UNVISITED: u8 = u8::MAX;

/// Neighbour index offsets of cell `idx` (row-major, `size` per row); count is 4, 6 or 3.
#[inline(always)]
fn nbrs(lat: Lattice, idx: usize, size: usize) -> ([isize; 8], usize) {
    let s = size as isize;
    match lat {
        Lattice::Square => ([-s, 1, s, -1, 0, 0, 0, 0], 4),
        Lattice::Moore => {
            let mut o = [0isize; 8];
            for (i, (dx, dy)) in MOORE_DIRS.iter().enumerate() {
                o[i] = *dy as isize * s + *dx as isize;
            }
            (o, 8)
        }
        Lattice::Hex => {
            let mut o = [0isize; 6 + 2];
            for (i, (dq, dr)) in HEX_DIRS.iter().enumerate() {
                o[i] = *dr as isize * s + *dq as isize;
            }
            (o, 6)
        }
        Lattice::Tri => {
            let (x, y) = (idx % size, idx / size);
            let up = (x + y) % 2 == 0;
            ([-1, 1, if up { s } else { -s }, 0, 0, 0, 0, 0], 3)
        }
    }
}

struct Region {
    lat: Lattice,
    size: usize,
    unv: Vec<u8>,
    area: u64,
    perimeter: u64,
    min: (i64, i64),
    max: (i64, i64),
}

impl Region {
    fn visited(&self, idx: usize) -> bool {
        self.unv[idx] != UNVISITED
    }
    fn on_boundary(&self, idx: usize) -> bool {
        self.unv[idx] != UNVISITED && self.unv[idx] > 0
    }
    fn visit(&mut self, idx: usize) {
        let (o, z) = nbrs(self.lat, idx, self.size);
        let mut u = 0u8;
        for d in &o[..z] {
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
        let (x, y) = ((idx % self.size) as i64, (idx / self.size) as i64);
        self.min = (self.min.0.min(x), self.min.1.min(y));
        self.max = (self.max.0.max(x), self.max.1.max(y));
    }
}

/// Run `mover` on `lat` for 2^max_log2 steps on a size x size board (size even), reporting windows (2^k, 2^(k+1)]
/// for min_log2 <= k < max_log2. Stops early if the walker gets within two cells of the edge (relative to the start
/// cell, as `probe.rs`). The start cell is the board centre, moved to even row and column for the triangular lattice.
pub fn lattice_probe(lat: Lattice, mover: &Mover, size: usize, min_log2: u32, max_log2: u32) -> LResult {
    assert!(min_log2 >= 1 && size.is_multiple_of(2));
    let c = size / 2;
    let c0 = c - c % 2;
    let s = size as isize;
    let start = c0 * size + c0;
    let mut region = Region { lat, size, unv: vec![UNVISITED; size * size], area: 0, perimeter: 0, min: (c0 as i64, c0 as i64), max: (c0 as i64, c0 as i64) };
    region.visit(start);

    // Ant state.
    let mut colour = vec![0u8; if matches!(mover, Mover::Ant(_)) { size * size } else { 0 }];
    let (turns, modulus): (Vec<u8>, u8) = match mover {
        Mover::Ant(rule) => match lat {
            Lattice::Square => (rule.chars().map(|ch| match ch { 'R' => 1, 'L' => 3, o => panic!("bad turn {o:?}") }).collect(), 4),
            Lattice::Hex => (hex_turns(rule).expect("hex rule"), 6),
            Lattice::Tri => (rule.chars().map(|ch| match ch { 'L' => 2, 'R' => 4, o => panic!("bad turn {o:?}") }).collect(), 6),
            Lattice::Moore => (rule.chars().map(|ch| match ch { 'r' => 1, 'R' => 2, 'l' => 7, 'L' => 6, o => panic!("bad turn {o:?}") }).collect(), 8),
        },
        _ => (vec![], 1),
    };
    let n = turns.len() as u8;
    let mut h: u8 = 0; // heading (square, hex, moore) or entry edge (triangular, starts at 4)
    if lat == Lattice::Tri {
        h = 4;
    }
    let mut rng = match mover {
        Mover::RandomWalk(s) | Mover::MeanField(s) => *s,
        _ => 0,
    };
    let mut visited_list: Vec<usize> = if matches!(mover, Mover::MeanField(_)) { vec![start] } else { vec![] };

    let mut idx = start;
    let mut windows = vec![];
    let mut escaped = false;
    let mut t: u64 = 0;
    for k in 0..max_log2 {
        let t_end = 1u64 << (k + 1);
        let (mut new_cells, mut boundary_steps, mut fresh_nbrs) = (0u64, 0u64, 0u64);
        while t < t_end {
            if let Mover::MeanField(_) = mover {
                idx = visited_list[(splitmix_next(&mut rng) % visited_list.len() as u64) as usize];
            }
            if region.on_boundary(idx) {
                boundary_steps += 1;
                fresh_nbrs += region.unv[idx] as u64;
            }
            match mover {
                Mover::Ant(_) => {
                    let col = colour[idx];
                    colour[idx] = if col + 1 == n { 0 } else { col + 1 };
                    match lat {
                        Lattice::Square => {
                            h = (h + turns[col as usize]) & 3;
                            let (dx, dy) = DIRS[h as usize];
                            idx = (idx as isize + dy as isize * s + dx as isize) as usize;
                        }
                        Lattice::Hex => {
                            h = (h + turns[col as usize]) % modulus;
                            let (dq, dr) = HEX_DIRS[h as usize];
                            idx = (idx as isize + dr as isize * s + dq as isize) as usize;
                        }
                        Lattice::Moore => {
                            h = (h + turns[col as usize]) % modulus;
                            let (dx, dy) = MOORE_DIRS[h as usize];
                            idx = (idx as isize + dy as isize * s + dx as isize) as usize;
                        }
                        Lattice::Tri => {
                            let exit = (h + turns[col as usize]) % modulus;
                            let (x, y) = ((idx % size) as i64, (idx / size) as i64);
                            let (dx, dy) = tri_step((x + y) % 2 == 0, exit);
                            idx = ((y + dy) as usize) * size + (x + dx) as usize;
                            h = (exit + 3) % 6;
                        }
                    }
                }
                Mover::RandomWalk(_) | Mover::MeanField(_) => {
                    let (o, z) = nbrs(lat, idx, size);
                    let d = o[(splitmix_next(&mut rng) % z as u64) as usize];
                    idx = (idx as isize + d) as usize;
                }
            }
            t += 1;
            if !region.visited(idx) {
                new_cells += 1;
                region.visit(idx);
                if matches!(mover, Mover::MeanField(_)) {
                    visited_list.push(idx);
                }
            }
            let (x, y) = ((idx % size) as i64 - c0 as i64, (idx / size) as i64 - c0 as i64);
            if x.abs() >= c as i64 - 2 || y.abs() >= c as i64 - 2 {
                escaped = true;
                break;
            }
        }
        if escaped {
            break;
        }
        if k >= min_log2 {
            windows.push(LWindow {
                k,
                area: region.area,
                perimeter: region.perimeter,
                new_cells,
                boundary_steps,
                fresh_nbrs,
                width: (region.max.0 - region.min.0 + 1) as u32,
                height: (region.max.1 - region.min.1 + 1) as u32,
            });
        }
    }
    LResult { windows, escaped }
}

pub const CSV_HEADER: &str = "lattice,spec,k,area,perimeter,new_cells,boundary_steps,fresh_nbrs,escaped,width,height";

pub fn csv_rows(lat: Lattice, spec: &str, res: &LResult) -> String {
    let name = match lat {
        Lattice::Square => "square",
        Lattice::Hex => "hex",
        Lattice::Tri => "tri",
        Lattice::Moore => "moore",
    };
    res.windows
        .iter()
        .map(|w| {
            format!(
                "{name},{spec},{},{},{},{},{},{},{},{},{}\n",
                w.k, w.area, w.perimeter, w.new_cells, w.boundary_steps, w.fresh_nbrs, res.escaped, w.width, w.height
            )
        })
        .collect()
}
