//! Edge tracer: what the walker does at the boundary of its visited region.
//!
//! Extends `probe` (same definitions: a *boundary step* starts on a visited cell
//! with at least one unvisited 4-neighbour, inner-hole rims included; a *birth*
//! is a step onto a never-visited cell) with, over the last half of the run
//! (steps t0 < t <= T, T = 2^log2, t0 = T/2, the probe's last octave):
//! - per-colour tallies (boundary steps, births, ahead/left/right fresh), as `examples/edgestats.rs`;
//! - for boundary reads of a cell that was read before: the lag since its previous read
//!   (any step), bucketed by the cell state at the read. A circulation around a 2x2 block gives lag 4;
//! - N_b, the number of boundary reads a cell receives while it is a boundary cell, for cells born in
//!   the window: recorded when the cell becomes interior (resolved) or at the end (censored).
//!   Little's law: births * E[N_b over all cells] = boundary steps, so 1/c = E[N_b] up to censoring;
//! - birth chains: lengths of maximal runs of consecutive births.
//!
//! The layout is a `w x h` grid, optionally a torus, optionally pre-filled with visited cells of given
//! colours (a flat-edge "band" experiment). Without prefill it is `probe_walker`'s setting: blank
//! board, one visited start cell in the middle, escape when within two cells of the edge.

use crate::DIRS;
use crate::walkers::Walker;

pub const KC: usize = 64;
pub const LAGK: usize = 8;
pub const LAGC: usize = 64;
pub const NBC: usize = 64;
pub const CHC: usize = 32;

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Tally {
    pub edge: u64,
    pub births: u64,
    pub ahead: u64,
    pub left: u64,
    pub right: u64,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct EdgeTrace {
    pub by_colour: Vec<Tally>,
    pub boundary_steps: u64,
    pub births: u64,
    pub fresh_nbrs: u64,
    /// lag[min(colour, LAGK-1)][min(lag, LAGC-1)]: boundary reads whose cell had been read before.
    pub lag: Vec<Vec<u64>>,
    pub nb_resolved: Vec<u64>,
    pub nb_censored: Vec<u64>,
    /// chain[min(len, CHC-1)]: maximal runs of consecutive births, by length.
    pub chain: Vec<u64>,
    pub area: u64,
    pub perimeter: u64,
    /// Visited area after step t0 = T/2 (start of the window).
    pub area_t0: u64,
    pub escaped: bool,
}

#[derive(Clone, Copy)]
pub struct Layout {
    pub w: usize,
    pub h: usize,
    pub wrap: bool,
}

const NONE_T: u32 = u32::MAX;
const TRACKED: u16 = 0x8000;

/// Run `walker` for 2^log2 steps (log2 <= 30). `prefill(gx, gy)` returns `Some(colour)` for cells that start
/// visited with that colour (`u8::MAX`: the walker's own initial colour); `start` must be such a cell. Fresh cells start at `walker.initial_cell(gx - w/2, gy - h/2)`
/// if the walker has a random init, else 0.
pub fn trace<W: Walker>(
    mut walker: W,
    lay: Layout,
    prefill: &dyn Fn(usize, usize) -> Option<u8>,
    start: (usize, usize, u8),
    log2: u32,
) -> EdgeTrace {
    assert!(log2 <= 30);
    let Layout { w, h, wrap } = lay;
    let n = w * h;
    let (cx, cy) = ((w / 2) as i64, (h / 2) as i64);
    let mut colour = vec![0u8; n];
    let mut vis = vec![false; n];
    for gy in 0..h {
        for gx in 0..w {
            let i = gy * w + gx;
            let init = |walker: &W| if W::RANDOM_INIT { walker.initial_cell(gx as i64 - cx, gy as i64 - cy) } else { 0 };
            if let Some(c) = prefill(gx, gy) {
                vis[i] = true;
                colour[i] = if c == u8::MAX { init(&walker) } else { c };
            } else if W::RANDOM_INIT {
                colour[i] = walker.initial_cell(gx as i64 - cx, gy as i64 - cy);
            }
        }
    }
    let nbr = |gx: usize, gy: usize, d: usize| -> usize {
        let (dx, dy) = DIRS[d];
        let (nx, ny) = (gx as isize + dx as isize, gy as isize + dy as isize);
        if wrap {
            (ny.rem_euclid(h as isize) as usize) * w + nx.rem_euclid(w as isize) as usize
        } else {
            ny as usize * w + nx as usize
        }
    };
    // unv[i]: number of unvisited neighbours of visited cell i
    let mut unv = vec![0u8; n];
    let (mut area, mut perimeter) = (0u64, 0u64);
    for gy in 0..h {
        for gx in 0..w {
            let i = gy * w + gx;
            if vis[i] {
                area += 1;
                let u = (0..4).filter(|&d| !vis[nbr(gx, gy, d)]).count() as u8;
                unv[i] = u;
                if u > 0 {
                    perimeter += 1;
                }
            }
        }
    }
    let (mut gx, mut gy, mut hd) = start;
    assert!(vis[gy * w + gx], "start cell must be visited");
    let mut last_t = vec![NONE_T; n];
    let mut nb = vec![0u16; n];
    let mut tr = EdgeTrace {
        by_colour: vec![Tally::default(); KC],
        boundary_steps: 0,
        births: 0,
        fresh_nbrs: 0,
        lag: vec![vec![0; LAGC]; LAGK],
        nb_resolved: vec![0; NBC],
        nb_censored: vec![0; NBC],
        chain: vec![0; CHC],
        area: 0,
        perimeter: 0,
        area_t0: 0,
        escaped: false,
    };
    let total = 1u64 << log2;
    let t0 = total / 2;
    let mut run = 0usize;
    for t in 1..=total {
        let i = gy * w + gx;
        let in_win = t > t0;
        let on_b = unv[i] > 0;
        let c = colour[i];
        if on_b {
            if nb[i] & !TRACKED < 0x7FFF {
                nb[i] += 1;
            }
            if in_win {
                tr.boundary_steps += 1;
                tr.fresh_nbrs += unv[i] as u64;
                let e = &mut tr.by_colour[(c as usize).min(KC - 1)];
                e.edge += 1;
                let fresh = |d: usize| !vis[nbr(gx, gy, d & 3)];
                e.ahead += fresh(hd as usize) as u64;
                e.left += fresh(hd as usize + 3) as u64;
                e.right += fresh(hd as usize + 1) as u64;
                if last_t[i] != NONE_T {
                    let lag = (t as u32 - last_t[i]) as usize;
                    tr.lag[(c as usize).min(LAGK - 1)][lag.min(LAGC - 1)] += 1;
                }
            }
        }
        last_t[i] = t as u32;
        walker.step(&mut colour[i], &mut hd);
        let (dx, dy) = DIRS[hd as usize];
        
        if wrap {
            gx = (gx as isize + dx as isize).rem_euclid(w as isize) as usize;
            gy = (gy as isize + dy as isize).rem_euclid(h as isize) as usize;
        } else {
            gx = (gx as isize + dx as isize) as usize;
            gy = (gy as isize + dy as isize) as usize;
        }
        let j = gy * w + gx;
        let born = !vis[j];
        if born {
            if in_win {
                tr.births += 1;
                tr.by_colour[(c as usize).min(KC - 1)].births += 1;
                nb[j] |= TRACKED;
            }
            // visit j
            vis[j] = true;
            let mut u = 0u8;
            for d in 0..4 {
                let k = nbr(gx, gy, d);
                if !vis[k] {
                    u += 1;
                } else {
                    unv[k] -= 1;
                    if unv[k] == 0 {
                        perimeter -= 1;
                        leave(&mut nb[k], &mut tr.nb_resolved);
                    }
                }
            }
            unv[j] = u;
            area += 1;
            if u > 0 {
                perimeter += 1;
            } else {
                leave(&mut nb[j], &mut tr.nb_resolved);
            }
        }
        if t == t0 {
            tr.area_t0 = area;
        }
        if in_win {
            if born {
                run += 1;
            } else if run > 0 {
                tr.chain[run.min(CHC - 1)] += 1;
                run = 0;
            }
        }
        if !wrap && (gx <= 2 || gy <= 2 || gx >= w - 2 || gy >= h - 2) {
            tr.escaped = true;
            break;
        }
    }
    if run > 0 {
        tr.chain[run.min(CHC - 1)] += 1;
    }
    for &v in &nb {
        if v & TRACKED != 0 {
            tr.nb_censored[((v & !TRACKED) as usize).min(NBC - 1)] += 1;
        }
    }
    tr.area = area;
    tr.perimeter = perimeter;
    tr
}

fn leave(nbv: &mut u16, resolved: &mut [u64]) {
    if *nbv & TRACKED != 0 {
        resolved[((*nbv & !TRACKED) as usize).min(NBC - 1)] += 1;
        *nbv &= !TRACKED;
    }
}

/// `probe_walker`'s setting: blank square board, one visited start cell in the middle, heading north.
pub fn trace_blank<W: Walker>(walker: W, size: usize, log2: u32) -> EdgeTrace {
    let c = size / 2;
    trace(walker, Layout { w: size, h: size, wrap: false }, &|x, y| if (x, y) == (c, c) { Some(u8::MAX) } else { None }, (c, c, 0), log2)
}
