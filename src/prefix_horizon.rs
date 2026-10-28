//! First-read times along a plain ant's trajectory: when does each colour first matter?
//!
//! Colour `c` is first read on the first `(c+1)`-th visit to any cell, so `first[c]` is the record time of the per-cell visit count.
//! Two rules whose letters agree below index `q` take identical steps until `first[q]` (see
//! `experiments/archive/2026-10-prefix-causal-horizon/README.md` for the statement, the z3 step proofs and the oracle test in
//! `tests/prefix_horizon.rs`). `wrapped_read` is the first step that reads a cell already visited `n` times, i.e. a cell written 0
//! by a wrap; it bounds how long a rule that merely repeats a shorter one's letters can differ from it.

use crate::{DIRS, Rule};

const WRAPPED: u8 = 0x80;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Horizon {
    /// `first[c]` = number (from 1) of the first step that reads colour `c`; `None` if not reached.
    pub first: Vec<Option<u64>>,
    /// First step that reads a cell holding a wrapped zero (visit `n+1`); the run stops there, so every colour is read by then.
    pub wrapped_read: Option<u64>,
    pub steps: u64,
    /// The ant left the `board x board` square (start at its centre) before either event completed.
    pub escaped: bool,
}

/// Run until the first wrapped read, `max_steps`, or leaving the board. Colours are below 100 (the lean limit), so the wrap flag
/// fits in bit 7 of the cell byte.
pub fn horizon(rule: &Rule, max_steps: u64, board: usize) -> Horizon {
    let n = rule.len();
    assert!((1..100).contains(&n) && board >= 3);
    let side = board as i64;
    let mut grid = vec![0u8; board * board];
    let (mut x, mut y, mut h) = (side / 2, side / 2, 0u8);
    let mut first = vec![None; n];
    let mut steps = 0u64;
    let mut out = Horizon { first: Vec::new(), wrapped_read: None, steps: 0, escaped: false };
    while steps < max_steps {
        let cell = &mut grid[(y * side + x) as usize];
        let (c, wrapped) = ((*cell & !WRAPPED) as usize, *cell & WRAPPED != 0);
        steps += 1;
        if wrapped {
            out.wrapped_read = Some(steps);
            break;
        }
        if first[c].is_none() {
            first[c] = Some(steps);
        }
        h = (h + rule.0[c].delta()) % 4;
        *cell = if c + 1 == n { WRAPPED } else { (c + 1) as u8 };
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        if x < 0 || y < 0 || x >= side || y >= side {
            out.escaped = true;
            break;
        }
    }
    out.first = first;
    out.steps = steps;
    out
}

/// The least colour `c < n'` where the longer rule's letter differs from the periodic extension of the shorter one's
/// (`None` if `w'` is `w` repeated, possibly cut short). Requires `w.len() <= w2.len()`.
pub fn first_mismatch(w: &Rule, w2: &Rule) -> Option<usize> {
    assert!(w.len() <= w2.len());
    (0..w2.len()).find(|&c| w2.0[c] != w.0[c % w.len()])
}

struct Walk<'a> {
    rule: &'a Rule,
    grid: Vec<u8>,
    side: i64,
    x: i64,
    y: i64,
    h: u8,
}

impl<'a> Walk<'a> {
    fn new(rule: &'a Rule, board: usize) -> Self {
        let side = board as i64;
        Walk { rule, grid: vec![0u8; board * board], side, x: side / 2, y: side / 2, h: 0 }
    }

    /// One step; false if the ant left the board.
    fn step(&mut self) -> bool {
        let cell = &mut self.grid[(self.y * self.side + self.x) as usize];
        let c = *cell as usize;
        self.h = (self.h + self.rule.0[c].delta()) % 4;
        *cell = if c + 1 == self.rule.len() { 0 } else { (c + 1) as u8 };
        let (dx, dy) = DIRS[self.h as usize];
        self.x += dx as i64;
        self.y += dy as i64;
        (0..self.side).contains(&self.x) && (0..self.side).contains(&self.y)
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum PairRun {
    /// Positions first differ after this many steps.
    Differ(u64),
    /// Positions agreed after every one of this many steps (the budget).
    Same(u64),
    /// One ant left the board after this many steps with the positions still equal (the run says nothing further).
    Left(u64),
}

/// Run two plain ants in lockstep from blank boards and report when their positions first differ.
/// The only observable is position, as in the prefix lemma (colours may differ while positions agree).
pub fn first_position_difference(a: &Rule, b: &Rule, max_steps: u64, board: usize) -> PairRun {
    let (mut wa, mut wb) = (Walk::new(a, board), Walk::new(b, board));
    for t in 1..=max_steps {
        let (ina, inb) = (wa.step(), wb.step());
        if (wa.x, wa.y) != (wb.x, wb.y) {
            return PairRun::Differ(t);
        }
        if !(ina && inb) {
            return PairRun::Left(t);
        }
    }
    PairRun::Same(max_steps)
}

/// Footprint of the cells an ant has written (visited), summarised so that two runs can be compared up to translation and the
/// eight symmetries of the square. `hash` is the minimum over those symmetries of an FNV-1a hash of the sorted, origin-shifted cell list.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Shape {
    pub width: usize,
    pub height: usize,
    pub cells: usize,
    pub hash: u64,
}

/// Canonical (translation- and dihedral-invariant) hash of a set of lattice cells.
pub fn canonical_hash(cells: &[(i64, i64)]) -> u64 {
    let maps: [fn(i64, i64) -> (i64, i64); 8] = [
        |x, y| (x, y),
        |x, y| (-x, y),
        |x, y| (x, -y),
        |x, y| (-x, -y),
        |x, y| (y, x),
        |x, y| (-y, x),
        |x, y| (y, -x),
        |x, y| (-y, -x),
    ];
    maps.iter()
        .map(|m| {
            let mut t: Vec<(i64, i64)> = cells.iter().map(|&(x, y)| m(x, y)).collect();
            let (mx, my) = (t.iter().map(|c| c.0).min().unwrap_or(0), t.iter().map(|c| c.1).min().unwrap_or(0));
            t.iter_mut().for_each(|c| *c = (c.0 - mx, c.1 - my));
            t.sort_unstable();
            let mut h = 0xcbf2_9ce4_8422_2325u64;
            for (x, y) in t {
                for b in x.to_le_bytes().into_iter().chain(y.to_le_bytes()) {
                    h = (h ^ b as u64).wrapping_mul(0x0100_0000_01b3);
                }
            }
            h
        })
        .min()
        .unwrap_or(0)
}

/// Run `steps` steps and summarise the visited cells; `None` if the ant left the board.
pub fn touched_shape(rule: &Rule, steps: u64, board: usize) -> Option<Shape> {
    touched_shape_bg(rule, steps, board, 0)
}

/// As `touched_shape`, but every cell starts at colour `background` (< n) instead of 0. A uniform background `k` is the same
/// dynamics as the rule rotated by `k` (`rot_k(w)[c] = w[(c + k) mod n]`) on a blank board, which `tests/prefix_horizon.rs` checks.
pub fn touched_shape_bg(rule: &Rule, steps: u64, board: usize, background: usize) -> Option<Shape> {
    const TOUCHED: u8 = 0x80;
    let n = rule.len();
    assert!((1..100).contains(&n) && board >= 3 && background < n);
    let side = board as i64;
    let mut grid = vec![background as u8; board * board];
    let (mut x, mut y, mut h) = (side / 2, side / 2, 0u8);
    let (mut x0, mut x1, mut y0, mut y1) = (x, x, y, y);
    for _ in 0..steps {
        let cell = &mut grid[(y * side + x) as usize];
        let c = (*cell & !TOUCHED) as usize;
        h = (h + rule.0[c].delta()) % 4;
        *cell = TOUCHED | if c + 1 == n { 0 } else { (c + 1) as u8 };
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        if x < 0 || y < 0 || x >= side || y >= side {
            return None;
        }
        (x0, x1, y0, y1) = (x0.min(x), x1.max(x), y0.min(y), y1.max(y));
    }
    let mut cells = Vec::new();
    for yy in y0..=y1 {
        for xx in x0..=x1 {
            if grid[(yy * side + xx) as usize] & TOUCHED != 0 {
                cells.push((xx, yy));
            }
        }
    }
    // The scan window also holds the cell the ant stands on, which is not written yet, so measure the touched cells themselves.
    let span = |f: fn(&(i64, i64)) -> i64| cells.iter().map(f).max().unwrap_or(0) - cells.iter().map(f).min().unwrap_or(0) + 1;
    Some(Shape { width: span(|c| c.0) as usize, height: span(|c| c.1) as usize, cells: cells.len(), hash: canonical_hash(&cells) })
}
