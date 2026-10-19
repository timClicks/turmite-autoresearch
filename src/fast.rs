//! A bounded flat-array ant for sweeping. Cells live in a `size x size` u8
//! grid with the ant starting in the centre; the run stops if it leaves.

use crate::detect::{Highway, MIN_SPAN, exit_confirms, find_highway};
use crate::{DIRS, Rule};

pub struct Grid {
    pub size: usize,
    pub cells: Vec<u8>,
    // Bounding box of touched cells, so reset only clears what was used.
    pub min: (usize, usize),
    pub max: (usize, usize),
}

impl Grid {
    pub fn new(size: usize) -> Grid {
        let c = size / 2;
        Grid {
            size,
            cells: vec![0; size * size],
            min: (c, c),
            max: (c, c),
        }
    }

    pub fn reset(&mut self) {
        for y in self.min.1..=self.max.1 {
            let row = y * self.size;
            self.cells[row + self.min.0..=row + self.max.0].fill(0);
        }
        let c = self.size / 2;
        self.min = (c, c);
        self.max = (c, c);
    }

    /// Colour at coordinates relative to the start cell.
    pub fn get(&self, x: i32, y: i32) -> u8 {
        let c = (self.size / 2) as i32;
        let (gx, gy) = (x + c, y + c);
        if gx < 0 || gy < 0 || gx >= self.size as i32 || gy >= self.size as i32 {
            return 0;
        }
        self.cells[gy as usize * self.size + gx as usize]
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stop {
    /// Hit the step budget.
    Budget,
    /// Walked off the grid.
    Escaped,
}

#[derive(Clone, Debug)]
pub struct RunResult {
    pub steps: u64,
    pub stop: Stop,
    pub pos: (i32, i32),
    pub heading: u8,
    /// Confirmed highway: periodic motion that carried the ant off the grid.
    pub highway: Option<Highway>,
    /// Periodic motion at the end of the run, confirmed or not.
    pub periodic_tail: Option<Highway>,
    /// Width and height of the region touched.
    pub extent: (u32, u32),
}

pub struct Config {
    pub max_steps: u64,
    pub checkpoint: u64,
    pub max_period: usize,
    /// Positions retained for detection; must exceed MIN_REPS * max_period.
    pub history: usize,
}

impl Default for Config {
    fn default() -> Config {
        Config {
            max_steps: 10_000_000,
            checkpoint: 1_000_000,
            max_period: 50_000,
            history: 250_000,
        }
    }
}

/// Ring buffer of recent positions.
struct Trail {
    buf: Vec<u32>,
    head: usize,
    len: usize,
}

impl Trail {
    fn new(cap: usize) -> Trail {
        Trail {
            buf: vec![0; cap],
            head: 0,
            len: 0,
        }
    }
    #[inline(always)]
    fn push(&mut self, p: u32) {
        self.buf[self.head] = p;
        self.head += 1;
        if self.head == self.buf.len() {
            self.head = 0;
        }
        if self.len < self.buf.len() {
            self.len += 1;
        }
    }
    /// Positions oldest first, decoded from cell indices to coordinates
    /// relative to the start cell on a `size`-wide grid.
    fn ordered(&self, size: usize) -> Vec<(i32, i32)> {
        let cap = self.buf.len();
        let start = (self.head + cap - self.len) % cap;
        let c = (size / 2) as i32;
        (0..self.len)
            .map(|i| {
                let k = self.buf[(start + i) % cap] as usize;
                ((k % size) as i32 - c, (k / size) as i32 - c)
            })
            .collect()
    }
}

pub fn run(rule: &Rule, grid: &mut Grid, cfg: &Config) -> RunResult {
    grid.reset();
    let n = rule.len();
    let size = grid.size;
    let c = size / 2;
    // next[c] and turn[c] tables avoid modulo in the hot loop.
    let next: Vec<u8> = (0..n).map(|i| ((i + 1) % n) as u8).collect();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    // Index deltas per heading; wrapping arithmetic on usize.
    let didx: [isize; 4] = DIRS.map(|(dx, dy)| dy as isize * size as isize + dx as isize);

    let (mut x, mut y) = (c, c);
    let mut idx = y * size + x;
    let mut h: u8 = 0;
    let mut steps: u64 = 0;
    let mut trail = Trail::new(cfg.history);
    trail.push(idx as u32);
    let (mut minx, mut miny, mut maxx, mut maxy) = (c, c, c, c);
    let mut stop = Stop::Budget;
    let mut highway = None;

    'outer: while steps < cfg.max_steps {
        let chunk_end = (steps + cfg.checkpoint).min(cfg.max_steps);
        while steps < chunk_end {
            let col = grid.cells[idx] as usize;
            h = (h + turn[col]) & 3;
            grid.cells[idx] = next[col];
            let (dx, dy) = DIRS[h as usize];
            x = x.wrapping_add_signed(dx as isize);
            y = y.wrapping_add_signed(dy as isize);
            steps += 1;
            if x >= size || y >= size {
                stop = Stop::Escaped;
                break 'outer;
            }
            idx = idx.wrapping_add_signed(didx[h as usize]);
            minx = minx.min(x);
            maxx = maxx.max(x);
            miny = miny.min(y);
            maxy = maxy.max(y);
            trail.push(idx as u32);
        }
    }
    // A periodic tail alone is not proof: inside a large structured pattern
    // the ant can march periodically along an old structure for tens of
    // thousands of steps and then break off. Only an ant that kept that march
    // up all the way off the grid, into blank cells, is on a true highway.
    // Leaving the grid is itself strong evidence, so a shorter window is fine.
    let tail = trail.ordered(size);
    let periodic_tail = find_highway(&tail, cfg.max_period, MIN_SPAN);
    if stop == Stop::Escaped {
        // A highway leaves in the direction it travels. An edge-walker whose
        // growing square reaches the grid walks along the boundary and steps
        // out sideways, perpendicular to its drift; reject those.
        highway = periodic_tail
            .or_else(|| find_highway(&tail, cfg.max_period, 2_000))
            .filter(|&hw| exit_confirms(hw, h));
    }
    grid.min = (minx, miny);
    grid.max = (maxx, maxy);
    let pos = (x as i32 - c as i32, y as i32 - c as i32);
    RunResult {
        steps,
        stop,
        pos,
        heading: h,
        highway,
        periodic_tail,
        extent: ((maxx - minx + 1) as u32, (maxy - miny + 1) as u32),
    }
}

/// Given a confirmed highway, re-run from scratch to find the first step s
/// after which the motion is periodic: pos[t] - pos[t-p] == d for all t >= s+p.
/// Uses only a ring buffer of length p, so it is cheap.
pub fn highway_onset(rule: &Rule, hw: Highway, until: u64) -> u64 {
    let n = rule.len();
    let p = hw.period as usize;
    let mut cells = std::collections::HashMap::<(i32, i32), u8>::new();
    let mut ring = vec![(0i32, 0i32); p];
    let (mut pos, mut h) = ((0i32, 0i32), 0u8);
    ring[0] = pos;
    let mut last_bad: u64 = 0; // last t whose check failed (or couldn't run)
    for t in 1..=until {
        let col = cells.get(&pos).copied().unwrap_or(0) as usize;
        h = (h + rule.0[col].delta()) % 4;
        cells.insert(pos, ((col + 1) % n) as u8);
        let (dx, dy) = DIRS[h as usize];
        pos = (pos.0 + dx, pos.1 + dy);
        let slot = (t as usize) % p;
        let prev = ring[slot]; // pos at t - p
        ring[slot] = pos;
        if t < p as u64 || (pos.0 - prev.0, pos.1 - prev.1) != (hw.dx, hw.dy) {
            last_bad = t;
        }
    }
    // Onset: first t from which all checks pass, minus one period.
    (last_bad + 1).saturating_sub(p as u64)
}
