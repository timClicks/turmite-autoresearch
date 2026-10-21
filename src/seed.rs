//! Causal dependency sets of the ant's future (experiment `2026-10-21-highway-preconditions`).
//!
//! `D(tau)` is the set of cells that are nonzero after `tau` steps and are read again at
//! some later step. Their colours, plus the ant's position and heading, determine the
//! whole future: zero cells are indistinguishable from blank and later writes are made by
//! the dynamics. Each read at step `t` of a cell last written at step `w` (colour `c != 0`)
//! puts that cell in `D(tau)` exactly for `tau in [w, t-1]`, so `|D(tau)|` for many `tau`
//! at once is a range count over reads. Checked against a brute-force `reference::Ant`
//! snapshot in `tests/seed.rs`.

use crate::{DIRS, Rule};
use std::collections::HashMap;

/// Last-write time of a cell that was never visited.
pub const NEVER: u64 = u64::MAX;

/// One step's read: the cell the ant stood on before step `t`.
#[derive(Clone, Copy, Debug)]
pub struct Read {
    pub t: u64,
    pub pos: (i32, i32),
    pub colour: u8,
    /// Step at which this cell was last written, or `NEVER`.
    pub prev: u64,
    pub turn: u8,
}

/// Flat-grid ant that also remembers when each cell was last written.
pub struct Tracked {
    pub size: usize,
    pub cells: Vec<u8>,
    pub last: Vec<u64>,
    pub pos: (i32, i32),
    pub heading: u8,
    pub t: u64,
    turn: Vec<u8>,
    n: u8,
}

impl Tracked {
    pub fn new(rule: &Rule, size: usize) -> Tracked {
        Tracked {
            size,
            cells: vec![0; size * size],
            last: vec![NEVER; size * size],
            pos: (0, 0),
            heading: 0,
            t: 0,
            turn: rule.0.iter().map(|t| t.delta()).collect(),
            n: rule.len() as u8,
        }
    }

    /// Board with the given nonzero cells, ant at `pos` heading `heading`, clock at `t`.
    /// Seed cells get last-write time `t` (they exist "now").
    pub fn with_cells(rule: &Rule, size: usize, cells: &[((i32, i32), u8)], pos: (i32, i32), heading: u8, t: u64) -> Tracked {
        let mut a = Tracked::new(rule, size);
        for &(p, c) in cells {
            let i = a.index(p).expect("seed cell outside board");
            a.cells[i] = c;
            a.last[i] = t;
        }
        a.pos = pos;
        a.heading = heading;
        a.t = t;
        a
    }

    pub fn index(&self, p: (i32, i32)) -> Option<usize> {
        let c = (self.size / 2) as i64;
        let (x, y) = (p.0 as i64 + c, p.1 as i64 + c);
        if x < 0 || y < 0 || x >= self.size as i64 || y >= self.size as i64 {
            None
        } else {
            Some(y as usize * self.size + x as usize)
        }
    }

    pub fn colour(&self, p: (i32, i32)) -> u8 {
        self.index(p).map_or(0, |i| self.cells[i])
    }

    /// Same update as `reference::Ant::step`. `None` if the ant stands outside the board.
    pub fn step(&mut self) -> Option<Read> {
        let i = self.index(self.pos)?;
        let c = self.cells[i];
        let turn = self.turn[c as usize];
        self.heading = (self.heading + turn) & 3;
        self.cells[i] = (c + 1) % self.n;
        self.t += 1;
        let prev = self.last[i];
        self.last[i] = self.t;
        let read = Read { t: self.t, pos: self.pos, colour: c, prev, turn };
        let (dx, dy) = DIRS[self.heading as usize];
        self.pos = (self.pos.0 + dx, self.pos.1 + dy);
        Some(read)
    }
}

/// `|D(tau)|` and the truncated `|D_delta(tau)|` (reads within `delta` steps after `tau`)
/// at a sorted list of query times, accumulated from the reads of one run.
pub struct DepCounter {
    queries: Vec<u64>,
    delta: u64,
    full: Vec<i64>,
    trunc: Vec<i64>,
}

impl DepCounter {
    pub fn new(queries: Vec<u64>, delta: u64) -> DepCounter {
        assert!(queries.windows(2).all(|w| w[0] < w[1]), "queries must be strictly increasing");
        let m = queries.len();
        DepCounter { queries, delta, full: vec![0; m + 1], trunc: vec![0; m + 1] }
    }

    fn add(diff: &mut [i64], q: &[u64], lo: u64, hi: u64) {
        // +1 for every query in [lo, hi]
        if lo > hi {
            return;
        }
        let a = q.partition_point(|&x| x < lo);
        let b = q.partition_point(|&x| x <= hi);
        if a < b {
            diff[a] += 1;
            diff[b] -= 1;
        }
    }

    pub fn observe(&mut self, r: &Read) {
        if r.colour == 0 || r.prev == NEVER {
            return;
        }
        let (Some(&q0), Some(&q1)) = (self.queries.first(), self.queries.last()) else { return };
        let hi = r.t - 1;
        if hi < q0 || r.prev > q1 {
            return;
        }
        Self::add(&mut self.full, &self.queries, r.prev, hi);
        Self::add(&mut self.trunc, &self.queries, r.prev.max(r.t.saturating_sub(self.delta)), hi);
    }

    pub fn queries(&self) -> &[u64] {
        &self.queries
    }

    /// (`|D(tau)|`, `|D_delta(tau)|`) per query, valid if every read after the last query
    /// that could touch an old cell has been observed.
    pub fn finish(&self) -> (Vec<u32>, Vec<u32>) {
        let integrate = |d: &[i64]| {
            let mut acc = 0i64;
            d[..self.queries.len()]
                .iter()
                .map(|&v| {
                    acc += v;
                    acc as u32
                })
                .collect::<Vec<u32>>()
        };
        (integrate(&self.full), integrate(&self.trunc))
    }
}

/// One cell of `D(tau)`: where it is, its colour at `tau`, and the turns the ant takes on
/// each later read of it (its rule-independent "turn word").
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SeedCell {
    pub pos: (i32, i32),
    pub colour: u8,
    pub word: Vec<u8>,
}

/// Collects `D(tau)` itself (not just its size) from the reads after `tau`.
pub struct SeedCollector {
    tau: u64,
    pub cells: Vec<SeedCell>,
    index: HashMap<(i32, i32), usize>,
}

impl SeedCollector {
    pub fn new(tau: u64) -> SeedCollector {
        SeedCollector { tau, cells: Vec::new(), index: HashMap::new() }
    }

    pub fn observe(&mut self, r: &Read) {
        if r.t <= self.tau {
            return;
        }
        if let Some(&k) = self.index.get(&r.pos) {
            self.cells[k].word.push(r.turn);
        } else if r.colour != 0 && r.prev != NEVER && r.prev <= self.tau {
            self.index.insert(r.pos, self.cells.len());
            self.cells.push(SeedCell { pos: r.pos, colour: r.colour, word: vec![r.turn] });
        }
    }
}

/// Rotate an offset so that `heading` becomes north (heading 0); turn words are already
/// rotation invariant, so this puts seeds of different orientations in one frame.
pub fn to_ant_frame(d: (i32, i32), heading: u8) -> (i32, i32) {
    // Rotating the board anticlockwise by one quarter maps east (1,0) to north (0,-1).
    let mut v = d;
    for _ in 0..heading {
        v = (v.1, -v.0);
    }
    v
}

/// Lexicographically least rotation of a cyclic word.
pub fn least_rotation(w: &[u8]) -> Vec<u8> {
    (0..w.len().max(1))
        .map(|k| w[k..].iter().chain(&w[..k]).copied().collect::<Vec<u8>>())
        .min()
        .unwrap_or_default()
}
