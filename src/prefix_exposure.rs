//! Per-colour exposure and fresh-cell launch instrument
//! (experiments/archive/2026-10-kappa-prefix-exposure; conventions in its NOTEBOOK.md and SCHEMA.md).
//!
//! Same producer/accountant split as `fixed_area`, each with its own oracle in
//! `tests/prefix_exposure.rs`:
//! - the *producer* [`drive`]: a walker on a dense board; every state t yields a [`Dep`]
//!   (the departure t -> t+1 that is about to be made): boundary label, colour read, the
//!   cell's graph depth below the boundary, completed-colour-cycle class, fresh flag, heading
//!   and position. Depth is stored per cell and recomputed in a small ball around each new
//!   cell, so the per-step cost is a byte load;
//! - the *accountant* [`Accountant`]: a pure state machine over that stream and a list of area
//!   bands. It never sees the walker.
//!
//! Conventions. State t is the state after t moves; a departure is counted only if it is
//! executed (the last state of a run has none). Label z = boundary (B) iff the cell is visited
//! and has an unvisited 4-neighbour, holes included, as in `fixed_area`. Depth of a cell is the
//! graph distance, inside the visited set, to the nearest B cell (0 on B); 5 means "5 or more".
//! A *fresh* state is the arrival at a never-visited cell (the origin counts at t = 0).
//! Band [lo, hi) covers departures tau(lo) <= t < tau(hi), tau(a) = first t with area >= a.
//!
//! Launch window of a fresh departure f (width w, 64 in the experiment): `left` = some state in
//! (f, f+w] is interior; `long` = an interior episode (maximal run of I states) that *begins*
//! in (f, f+w] lasts at least w states; displacement is pos(f+w) - pos(f) resolved along the
//! arrival heading (fwd) and its right-hand side (lat). A window is resolved once state
//! f + 2w - 1 is seen (the latest a qualifying episode can reach w); windows still open when
//! the run stops are `cens`, with `cens_long` counting those already known to be long.
//! Windows overlap; they are correlated observations, never independent samples.

use crate::DIRS;
use crate::fixed_area::{Region, Stop};
use crate::walkers::Walker;
use std::collections::VecDeque;

pub const MAX_COLOURS: usize = 16;
/// Depth 0 = boundary, 1..=4 = that many steps below it, 5 = five or more.
pub const DEPTH_CLASSES: usize = 6;
/// Completed colour cycles of the cell at the read: 0, 1, 2, 3 or more.
pub const CYCLE_CLASSES: usize = 4;
/// Default depth-map update radius: see [`DepthMap`] and the sensitivity test.
pub const UPDATE_RADIUS: i64 = 5;
/// Cells within this distance of the board edge are never reached: the walker stops earlier, so
/// every depth-update window stays on the board.
pub const MARGIN: i64 = 12;

const UNSEEN: u8 = u8::MAX;

/// Depth below the boundary, maintained incrementally.
///
/// When a cell v is first visited, only cells whose shortest <= 4 path to a boundary changes can
/// change class; every such path has length <= 4, so those cells lie within `radius` = 5 of v
/// (v itself, or a neighbour whose boundary status flipped, is on the path). The ball is
/// re-derived from a multi-source BFS in the window of radius `radius + 4`. The radius is a
/// parameter only so the test can show that a too-small value is caught.
pub struct DepthMap {
    pub d: Vec<u8>,
    size: usize,
    radius: i64,
}

impl DepthMap {
    pub fn new(size: usize, radius: i64) -> DepthMap {
        DepthMap { d: vec![UNSEEN; size * size], size, radius }
    }

    /// Re-derive depth in the ball around the cell at (`x`, `y`) (board coordinates) just visited.
    pub fn update(&mut self, region: &Region, x: i64, y: i64) {
        let r = self.radius;
        let wr = r + 4;
        let side = (2 * wr + 1) as usize;
        let mut dist = vec![UNSEEN; side * side];
        let mut cur: Vec<(i64, i64)> = Vec::new();
        let at = |dx: i64, dy: i64| -> usize { (dy + wr) as usize * side + (dx + wr) as usize };
        let size = self.size;
        let idx = |dx: i64, dy: i64| -> usize { ((y + dy) as usize) * size + (x + dx) as usize };
        for dy in -wr..=wr {
            for dx in -wr..=wr {
                if dx.abs() + dy.abs() <= wr && region.on_boundary(idx(dx, dy)) {
                    dist[at(dx, dy)] = 0;
                    cur.push((dx, dy));
                }
            }
        }
        for level in 1..=4u8 {
            let mut next = Vec::new();
            for &(dx, dy) in &cur {
                for (ex, ey) in [(0, -1), (1, 0), (0, 1), (-1, 0)] {
                    let (nx, ny) = (dx + ex, dy + ey);
                    if nx.abs() + ny.abs() > wr || dist[at(nx, ny)] != UNSEEN || !region.visited(idx(nx, ny)) {
                        continue;
                    }
                    dist[at(nx, ny)] = level;
                    next.push((nx, ny));
                }
            }
            cur = next;
        }
        for dy in -r..=r {
            for dx in -r..=r {
                if dx.abs() + dy.abs() <= r && region.visited(idx(dx, dy)) {
                    let v = dist[at(dx, dy)];
                    self.d[idx(dx, dy)] = if v == UNSEEN { 5 } else { v };
                }
            }
        }
    }
}

/// The departure about to be made from state `t`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Dep {
    pub t: u64,
    pub z: bool,
    pub area: u64,
    pub perimeter: u64,
    pub colour: u8,
    pub depth: u8,
    pub cycle: u8,
    pub fresh: bool,
    pub heading: u8,
    pub x: i64,
    pub y: i64,
}

/// Run `walker` on a `size` x `size` board (`size` >= 32, even), calling `sink` with every state
/// t = 0, 1, ... including the final one. `sink` returns true to stop. Unvisited cells are
/// initialised on first arrival (`Walker::initial_cell` is pure, so this equals dense
/// initialisation). The walker stops `MARGIN` cells short of the edge.
pub fn drive<W: Walker>(mut walker: W, size: usize, cap: u64, radius: i64, mut sink: impl FnMut(&Dep) -> bool) -> (Stop, u64) {
    assert!(size >= 32 && size.is_multiple_of(2) && radius >= 0);
    assert!(MARGIN > radius + 4, "update window must stay on the board");
    let c = (size / 2) as i64;
    let mut colour = vec![0u8; size * size];
    let mut wraps = vec![0u8; size * size];
    let mut region = Region::new(size);
    let mut depth = DepthMap::new(size, radius);
    let (mut x, mut y, mut h, mut t) = (0i64, 0i64, 0u8, 0u64);
    let mut idx = (c * size as i64 + c) as usize;
    let mut fresh = true;
    colour[idx] = walker.initial_cell(0, 0);
    region.visit(idx, 0, 0);
    depth.update(&region, c, c);
    loop {
        let dep = Dep {
            t,
            z: region.on_boundary(idx),
            area: region.area,
            perimeter: region.perimeter,
            colour: colour[idx],
            depth: depth.d[idx],
            cycle: wraps[idx].min(CYCLE_CLASSES as u8 - 1),
            fresh,
            heading: h,
            x,
            y,
        };
        if sink(&dep) {
            return (Stop::Sink, t);
        }
        if t >= cap {
            return (Stop::Budget, t);
        }
        if x.abs() >= c - MARGIN || y.abs() >= c - MARGIN {
            return (Stop::Escaped, t);
        }
        walker.step(&mut colour[idx], &mut h);
        if colour[idx] == 0 {
            wraps[idx] = wraps[idx].saturating_add(1);
        }
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        idx = (idx as isize + dy as isize * size as isize + dx as isize) as usize;
        t += 1;
        fresh = !region.visited(idx);
        if fresh {
            colour[idx] = walker.initial_cell(x, y);
            region.visit(idx, x, y);
            depth.update(&region, c + x, c + y);
        }
    }
}

/// Launch-window tallies (see the module docs). All fields are sums over resolved windows.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Launch {
    pub n: u64,
    /// Windows whose fresh cell was itself an interior cell (a filled hole).
    pub n_interior_start: u64,
    pub left: u64,
    pub long: u64,
    /// Sum over windows of the number of other fresh states in (f, f+w].
    pub overlap: u64,
    pub sum_fwd: i64,
    pub sum_lat: i64,
    pub sum_r2: u64,
    /// Windows unresolved when the run stopped, and how many of those are already known long.
    pub cens: u64,
    pub cens_long: u64,
}

#[derive(Clone, Debug, PartialEq)]
pub struct BandOut {
    pub lo: u64,
    pub hi: u64,
    pub reached_lo: bool,
    pub reached_hi: bool,
    pub t_start: u64,
    pub t_end: u64,
    pub area_start: u64,
    pub area_end: u64,
    pub perim_start: u64,
    pub perim_end: u64,
    pub steps: u64,
    pub b_dep: u64,
    pub i_dep: u64,
    /// Sum over executed departures of P_t / A_t, accumulated in increasing t (time-normalised kappa).
    pub sum_pa: f64,
    /// Executed departures by [colour][depth][cycle], flattened; see [`reads_idx`].
    pub reads: Vec<u64>,
    /// Fresh departures by the colour read there.
    pub fresh_colour: [u64; MAX_COLOURS],
    pub launch: Launch,
    /// Interior episodes (maximal runs of I states) whose first departure is in the band.
    pub ep_n: u64,
    /// Of those, how many last at least ws[i] states (exact once the episode ended or reached ws[i]).
    pub ep_long_n: Vec<u64>,
    /// In-band interior departures that belong to an episode of at least ws[i] states, wherever it began.
    /// For ws[i] = 1 this is exactly i_dep.
    pub tail_steps: Vec<u64>,
}

pub fn reads_idx(colour: usize, depth: usize, cycle: usize) -> usize {
    (colour * DEPTH_CLASSES + depth) * CYCLE_CLASSES + cycle
}

impl BandOut {
    fn new(lo: u64, hi: u64, nw: usize) -> BandOut {
        BandOut {
            lo,
            hi,
            reached_lo: false,
            reached_hi: false,
            t_start: 0,
            t_end: 0,
            area_start: 0,
            area_end: 0,
            perim_start: 0,
            perim_end: 0,
            steps: 0,
            b_dep: 0,
            i_dep: 0,
            sum_pa: 0.0,
            reads: vec![0; MAX_COLOURS * DEPTH_CLASSES * CYCLE_CLASSES],
            fresh_colour: [0; MAX_COLOURS],
            launch: Launch::default(),
            ep_n: 0,
            ep_long_n: vec![0; nw],
            tail_steps: vec![0; nw],
        }
    }

    pub fn reads_of(&self, colour: usize, depth: usize) -> u64 {
        (0..CYCLE_CLASSES).map(|y| self.reads[reads_idx(colour, depth, y)]).sum()
    }
}

/// Whole-run tallies, independent of bands. `first_read[c]` is the first executed departure that
/// reads colour c: (t, area, depth). A rule mutated at letter c matches the base exactly up to
/// and including that state's position, and differs at the next one.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Whole {
    pub first_read: [Option<(u64, u64, u8)>; MAX_COLOURS],
    pub reads: [u64; MAX_COLOURS],
    /// The interior episode still open when the run stopped: (band of its first departure, states so far).
    /// Classifications at thresholds above the length so far are not known for it.
    pub open_episode: Option<(Option<usize>, u64)>,
}

struct Ep {
    begin_state: u64,
    begin_band: Option<usize>,
    dep: Vec<u64>,
}

struct Window {
    f: u64,
    band: usize,
    z_f: bool,
    h_f: u8,
    pos_f: (i64, i64),
    pos_w: Option<(i64, i64)>,
    left: bool,
    long: bool,
    overlap: u64,
}

pub struct Accountant {
    w: u64,
    ws: Vec<u64>,
    ep: Option<Ep>,
    bands: Vec<BandOut>,
    started: usize,
    active: Option<usize>,
    prev: Option<(Dep, Option<usize>)>,
    run: u64,
    windows: VecDeque<Window>,
    whole: Whole,
}

impl Accountant {
    /// `w` is the fresh-launch window; `ws` are the episode-length thresholds (each >= 1).
    pub fn new(bands: &[(u64, u64)], w: u64, ws: &[u64]) -> Accountant {
        assert!(w >= 1 && !ws.is_empty() && ws.iter().all(|&x| x >= 1));
        for (k, &(lo, hi)) in bands.iter().enumerate() {
            assert!(lo >= 2 && hi > lo, "band needs 2 <= lo < hi");
            assert!(k == 0 || bands[k - 1].1 <= lo, "bands must be ordered and disjoint");
        }
        Accountant {
            w,
            ws: ws.to_vec(),
            ep: None,
            bands: bands.iter().map(|&(lo, hi)| BandOut::new(lo, hi, ws.len())).collect(),
            started: 0,
            active: None,
            prev: None,
            run: 0,
            windows: VecDeque::new(),
            whole: Whole { first_read: [None; MAX_COLOURS], reads: [0; MAX_COLOURS], open_episode: None },
        }
    }

    /// All bands closed, every launch window resolved, and no episode that touched a band is still
    /// short of the largest threshold.
    pub fn done(&self) -> bool {
        let max_w = *self.ws.iter().max().unwrap();
        let pending = self.ep.as_ref().is_some_and(|e| (e.begin_band.is_some() || e.dep.iter().any(|&x| x > 0)) && self.run < max_w);
        self.started == self.bands.len() && self.active.is_none() && self.windows.is_empty() && !pending
    }

    fn close_episode(&mut self, ep: Ep, len: u64) {
        for (i, &w) in self.ws.iter().enumerate() {
            if len < w {
                continue;
            }
            if let Some(k) = ep.begin_band {
                self.bands[k].ep_long_n[i] += 1;
            }
            for (k, &n) in ep.dep.iter().enumerate() {
                self.bands[k].tail_steps[i] += n;
            }
        }
    }

    pub fn feed(&mut self, d: &Dep) {
        let w = self.w;
        // 1. The departure of the previous state was executed: account it.
        if let Some((p, band)) = self.prev.take() {
            assert_eq!(d.t, p.t + 1);
            assert!(d.area == p.area || d.area == p.area + 1, "area grows by at most one per step");
            let c = p.colour as usize;
            self.whole.reads[c] += 1;
            if self.whole.first_read[c].is_none() {
                self.whole.first_read[c] = Some((p.t, p.area, p.depth));
            }
            if !p.z {
                let ep = self.ep.as_mut().expect("an interior state opens an episode when it is fed");
                if p.t == ep.begin_state {
                    ep.begin_band = band;
                    if let Some(k) = band {
                        self.bands[k].ep_n += 1;
                    }
                }
                if let Some(k) = band {
                    ep.dep[k] += 1;
                }
            }
            if let Some(k) = band {
                let b = &mut self.bands[k];
                b.steps += 1;
                if p.z {
                    b.b_dep += 1;
                } else {
                    b.i_dep += 1;
                }
                b.sum_pa += p.perimeter as f64 / p.area as f64;
                b.reads[reads_idx(c, p.depth as usize, p.cycle as usize)] += 1;
                if p.fresh {
                    b.fresh_colour[c] += 1;
                    self.windows.push_back(Window {
                        f: p.t,
                        band: k,
                        z_f: p.z,
                        h_f: p.heading,
                        pos_f: (p.x, p.y),
                        pos_w: None,
                        left: false,
                        long: false,
                        overlap: 0,
                    });
                }
            }
        }
        // 2. Windows and the interior-run counter see state d.
        let prev_run = self.run;
        self.run = if d.z { 0 } else { self.run + 1 };
        if d.z && prev_run > 0 {
            let ep = self.ep.take().unwrap();
            self.close_episode(ep, prev_run);
        }
        if !d.z && prev_run == 0 {
            self.ep = Some(Ep { begin_state: d.t, begin_band: None, dep: vec![0; self.bands.len()] });
        }
        for win in self.windows.iter_mut() {
            if d.t > win.f && d.t <= win.f + w {
                if !d.z {
                    win.left = true;
                }
                if d.fresh {
                    win.overlap += 1;
                }
                if d.t == win.f + w {
                    win.pos_w = Some((d.x, d.y));
                }
            }
        }
        if self.run == w {
            let s0 = d.t + 1 - w;
            for win in self.windows.iter_mut() {
                if s0 > win.f && s0 <= win.f + w {
                    win.long = true;
                }
            }
        }
        while self.windows.front().is_some_and(|win| win.f + 2 * w - 1 <= d.t) {
            let win = self.windows.pop_front().unwrap();
            let l = &mut self.bands[win.band].launch;
            let (px, py) = win.pos_w.expect("state f + w precedes f + 2w - 1");
            let (dx, dy) = (px - win.pos_f.0, py - win.pos_f.1);
            let (ex, ey) = DIRS[win.h_f as usize];
            let (rx, ry) = DIRS[(win.h_f as usize + 1) % 4];
            l.n += 1;
            l.n_interior_start += u64::from(!win.z_f);
            l.left += u64::from(win.left);
            l.long += u64::from(win.long);
            l.overlap += win.overlap;
            l.sum_fwd += dx * ex as i64 + dy * ey as i64;
            l.sum_lat += dx * rx as i64 + dy * ry as i64;
            l.sum_r2 += (dx * dx + dy * dy) as u64;
        }
        // 3. Band boundaries at this state.
        if let Some(k) = self.active
            && d.area >= self.bands[k].hi {
                assert_eq!(d.area, self.bands[k].hi);
                let b = &mut self.bands[k];
                b.reached_hi = true;
                b.t_end = d.t;
                b.area_end = d.area;
                b.perim_end = d.perimeter;
                self.active = None;
            }
        if self.active.is_none() && self.started < self.bands.len() && d.area >= self.bands[self.started].lo {
            let k = self.started;
            assert_eq!(d.area, self.bands[k].lo);
            let b = &mut self.bands[k];
            b.reached_lo = true;
            b.t_start = d.t;
            b.area_start = d.area;
            b.perim_start = d.perimeter;
            self.started += 1;
            self.active = Some(k);
        }
        self.prev = Some((*d, self.active));
    }

    pub fn finish(mut self) -> (Vec<BandOut>, Whole) {
        if let Some(ep) = self.ep.take() {
            let len = self.run;
            self.whole.open_episode = Some((ep.begin_band, len));
            self.close_episode(ep, len);
        }
        if let (Some(k), Some((p, _))) = (self.active, self.prev) {
            let b = &mut self.bands[k];
            b.t_end = p.t;
            b.area_end = p.area;
            b.perim_end = p.perimeter;
        }
        for win in self.windows.drain(..) {
            let l = &mut self.bands[win.band].launch;
            l.cens += 1;
            l.cens_long += u64::from(win.long);
        }
        (self.bands, self.whole)
    }
}

#[derive(Debug)]
pub struct RunOut {
    pub bands: Vec<BandOut>,
    pub whole: Whole,
    pub stop: Stop,
    pub t_final: u64,
    pub area_final: u64,
}

/// Run a walker until every band has closed and every window resolved, the budget `cap` is
/// spent, or it escapes.
pub fn run<W: Walker>(walker: W, size: usize, cap: u64, bands: &[(u64, u64)], w: u64, ws: &[u64]) -> RunOut {
    let mut acc = Accountant::new(bands, w, ws);
    let mut area_final = 0;
    let (stop, t_final) = drive(walker, size, cap, UPDATE_RADIUS, |d| {
        acc.feed(d);
        area_final = d.area;
        acc.done()
    });
    let (bands, whole) = acc.finish();
    RunOut { bands, whole, stop, t_final, area_final }
}
