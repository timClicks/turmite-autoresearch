//! `edge_trace`'s per-colour boundary tallies, return-lag histogram and N_b distribution on the three lattices of
//! `lattice_probe` (square, hex, triangular), blank board, lattice ant only. Same window as `edge_trace`: steps
//! t0 < t <= T with T = 2^log2, t0 = T/2, i.e. the probe's last octave k = log2 - 1. Definitions as `lattice_probe`
//! (boundary step = starts on a visited cell with >= 1 unvisited neighbour; birth = step onto a never-visited cell) and
//! as `edge_trace` (lag = steps since the cell's previous read, N_b = boundary reads a window-born cell receives while
//! it is a boundary cell, resolved when it becomes interior, censored at the end).
//!
//! Extra over `edge_trace`: `hole_births`, births into a cell whose neighbours were all already visited (a filled
//! hole, e.g. the centre of a hex 6-ring).

use crate::DIRS;
use crate::ext::{HEX_DIRS, hex_turns, tri_step};
use crate::lattice_probe::{Lattice, MOORE_DIRS};

pub const KC: usize = 64;
pub const LAGK: usize = 8;
pub const LAGC: usize = 64;
pub const NBC: usize = 64;
pub const RUNC: usize = 64;

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Tally {
    pub edge: u64,
    pub births: u64,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct LTrace {
    pub by_colour: Vec<Tally>,
    pub boundary_steps: u64,
    pub births: u64,
    /// lag[min(colour, LAGK-1)][min(lag, LAGC-1)]: boundary reads of cells read before.
    pub lag: Vec<Vec<u64>>,
    pub nb_resolved: Vec<u64>,
    pub nb_censored: Vec<u64>,
    /// Births into a cell all of whose neighbours were already visited (filling a hole, e.g. a ring centre).
    pub hole_births: u64,
    /// Loop length of the rule's first letter (square 4, triangular 6, hex r/l 6, hex R/L 3).
    pub loop_len: u32,
    /// run_count[min(len, RUNC-1)]: maximal runs of consecutive steps that each re-read a cell last read exactly `loop_len` steps
    /// earlier (a circulation); run_boundary[same index] sums the boundary steps inside those runs.
    pub run_count: Vec<u64>,
    pub run_boundary: Vec<u64>,
    pub area: u64,
    pub escaped: bool,
}

const UNVISITED: u8 = u8::MAX;
const NONE_T: u32 = u32::MAX;
const TRACKED: u16 = 0x8000;

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
            let mut o = [0isize; 8];
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

/// Loop length of a run of the rule's first letter: square R/L 4; triangular +-2 edges 6; hex r/l (60 degrees) 6, R/L (120) 3.
pub fn loop_len(lat: Lattice, rule: &str) -> u32 {
    match (lat, rule.chars().next()) {
        (Lattice::Square, _) => 4,
        (Lattice::Moore, Some('r' | 'l')) => 8,
        (Lattice::Moore, Some('R' | 'L')) => 4,
        (Lattice::Tri, _) => 6,
        (Lattice::Hex, Some('r' | 'l')) => 6,
        (Lattice::Hex, Some('R' | 'L')) => 3,
        _ => panic!("empty or bad rule"),
    }
}

fn leave(nbv: &mut u16, resolved: &mut [u64]) {
    if *nbv & TRACKED != 0 {
        resolved[((*nbv & !TRACKED) as usize).min(NBC - 1)] += 1;
        *nbv &= !TRACKED;
    }
}

/// Run the ant `rule` on `lat` for 2^log2 steps (log2 <= 30) on a size x size board (size even).
pub fn lattice_trace(lat: Lattice, rule: &str, size: usize, log2: u32) -> LTrace {
    assert!(log2 <= 30 && size.is_multiple_of(2));
    let c = size / 2;
    let c0 = c - c % 2;
    let s = size as isize;
    let start = c0 * size + c0;
    let mut unv = vec![UNVISITED; size * size];
    let mut colour = vec![0u8; size * size];
    let mut last_t = vec![NONE_T; size * size];
    let mut nb = vec![0u16; size * size];
    let (turns, modulus): (Vec<u8>, u8) = match lat {
        Lattice::Square => (rule.chars().map(|ch| match ch { 'R' => 1, 'L' => 3, o => panic!("bad turn {o:?}") }).collect(), 4),
        Lattice::Hex => (hex_turns(rule).expect("hex rule"), 6),
        Lattice::Moore => (rule.chars().map(|ch| match ch { 'r' => 1, 'R' => 2, 'l' => 7, 'L' => 6, o => panic!("bad turn {o:?}") }).collect(), 8),
        Lattice::Tri => (rule.chars().map(|ch| match ch { 'L' => 2, 'R' => 4, o => panic!("bad turn {o:?}") }).collect(), 6),
    };
    let n = turns.len() as u8;
    let ell = loop_len(lat, rule);
    let (mut run, mut run_b) = (0usize, 0u64);
    let mut tr = LTrace {
        by_colour: vec![Tally::default(); KC],
        boundary_steps: 0,
        births: 0,
        lag: vec![vec![0; LAGC]; LAGK],
        nb_resolved: vec![0; NBC],
        nb_censored: vec![0; NBC],
        hole_births: 0,
        loop_len: ell,
        run_count: vec![0; RUNC],
        run_boundary: vec![0; RUNC],
        area: 0,
        escaped: false,
    };
    // visit(): mark idx visited, update neighbour counters; returns (u = unvisited nbrs of idx).
    let visit = |unv: &mut Vec<u8>, nb: &mut Vec<u16>, resolved: &mut Vec<u64>, idx: usize| -> u8 {
        let (o, z) = nbrs(lat, idx, size);
        let mut u = 0u8;
        for d in &o[..z] {
            let j = (idx as isize + d) as usize;
            if unv[j] == UNVISITED {
                u += 1;
            } else {
                unv[j] -= 1;
                if unv[j] == 0 {
                    leave(&mut nb[j], resolved);
                }
            }
        }
        unv[idx] = u;
        if u == 0 {
            leave(&mut nb[idx], resolved);
        }
        u
    };
    visit(&mut unv, &mut nb, &mut tr.nb_resolved, start);
    tr.area = 1;
    let mut h: u8 = if lat == Lattice::Tri { 4 } else { 0 };
    let mut idx = start;
    let total = 1u64 << log2;
    let t0 = total / 2;
    for t in 1..=total {
        let in_win = t > t0;
        let on_b = unv[idx] != UNVISITED && unv[idx] > 0;
        let col = colour[idx];
        if on_b {
            if nb[idx] & !TRACKED < 0x7FFF {
                nb[idx] += 1;
            }
            if in_win {
                tr.boundary_steps += 1;
                tr.by_colour[(col as usize).min(KC - 1)].edge += 1;
                if last_t[idx] != NONE_T {
                    let lag = (t as u32 - last_t[idx]) as usize;
                    tr.lag[(col as usize).min(LAGK - 1)][lag.min(LAGC - 1)] += 1;
                }
            }
        }
        if in_win {
            if last_t[idx] != NONE_T && t as u32 - last_t[idx] == ell {
                run += 1;
                run_b += on_b as u64;
            } else if run > 0 {
                tr.run_count[run.min(RUNC - 1)] += 1;
                tr.run_boundary[run.min(RUNC - 1)] += run_b;
                run = 0;
                run_b = 0;
            }
        }
        last_t[idx] = t as u32;
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
        if unv[idx] == UNVISITED {
            if in_win {
                tr.births += 1;
                tr.by_colour[(col as usize).min(KC - 1)].births += 1;
                nb[idx] |= TRACKED;
            }
            let u = visit(&mut unv, &mut nb, &mut tr.nb_resolved, idx);
            if in_win && u == 0 {
                tr.hole_births += 1;
            }
            tr.area += 1;
        }
        let (x, y) = ((idx % size) as i64 - c0 as i64, (idx / size) as i64 - c0 as i64);
        if x.abs() >= c as i64 - 2 || y.abs() >= c as i64 - 2 {
            tr.escaped = true;
            break;
        }
    }
    if run > 0 {
        tr.run_count[run.min(RUNC - 1)] += 1;
        tr.run_boundary[run.min(RUNC - 1)] += run_b;
    }
    for &v in &nb {
        if v & TRACKED != 0 {
            tr.nb_censored[((v & !TRACKED) as usize).min(NBC - 1)] += 1;
        }
    }
    tr
}
