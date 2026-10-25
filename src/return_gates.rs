//! Observation-only rim/interior crossing instrument (experiments/2026-10-15-kappa-return-gates).
//!
//! Conventions (frozen in that experiment's README before any ant outcome):
//! - depth of a visited cell = 4-neighbour graph distance through visited cells to the
//!   nearest visited boundary cell (boundary = visited with an unvisited 4-neighbour, holes
//!   included, so boundary cells have depth 0 and `z` of the probe is "depth 0"); depths
//!   are capped at [`DEEP`] = 5. Rim = depth <= [`RIM`] = 4.
//! - the state at time t is labelled with the depth map of time t. A step t -> t+1 is split in
//!   two stages: (A) the move, judged under the OLD map (a newly discovered cell counts as
//!   rim); (B) the map update caused by that discovery, judged at the fixed new position.
//!   A label change in stage A is a crossing (exit rim->interior, entry interior->rim);
//!   a label change in stage B is a reclassification and is never a spatial crossing.
//! - crossings and exposures are keyed (tile x, tile y, heading after the move, kind) with 8x8
//!   tiles anchored at the start origin and the tile of the RIM-side cell. Exposure counts, at
//!   every departure, each of the 4 directions whose neighbour has a different label
//!   (unvisited neighbours count as rim), keyed by the same rule.
//! - everything is gated to departures whose state area lies in a band [lo, hi).
use crate::field_age::Frame;
use crate::walkers::mix64;
use crate::DIRS;
use std::collections::BTreeMap;

pub const RIM: u8 = 4;
pub const DEEP: u8 = 5;
pub const TILE: i64 = 8;
const UNV: u8 = u8::MAX;
const BALL: i64 = 9;

/// (tile x, tile y, heading after the move, kind: 0 = exit rim->interior, 1 = entry).
pub type Key = (i32, i32, u8, u8);

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Tally {
    pub steps: u64,
    /// Departures by depth of the departure cell (capped at DEEP).
    pub depth_steps: [u64; 6],
    pub exits: u64,
    pub entries: u64,
    /// Map-update label changes at a fixed position (not spatial transport).
    pub reclass_in: u64,
    pub reclass_out: u64,
    pub events: BTreeMap<Key, u64>,
    pub exposure: BTreeMap<Key, u64>,
    /// Completed boundary runs whose first departure was preceded by an in-window interior departure.
    pub b_runs: u64,
    pub b_run_steps: u64,
    /// Completed interior excursions begun by an exit, by exit heading (steps until the next rim state).
    pub exc_n: [u64; 4],
    pub exc_steps: [u64; 4],
    pub exc_unresolved: u64,
}

struct Prev {
    idx: usize,
    label: bool,
    depth: u8,
    z: bool,
    area: u64,
    ncells: usize,
}

pub struct Obs {
    size: usize,
    bands: Vec<(u64, u64)>,
    pub out: Vec<Tally>,
    depth: Vec<u8>,
    prev: Option<Prev>,
    open: Option<(u64, u8, usize)>,
    brun: Option<u64>,
    prev_in_window_interior: bool,
}

pub fn tile_of(idx: usize, size: usize) -> (i32, i32) {
    let c = (size / 2) as i64;
    let (x, y) = ((idx % size) as i64 - c, (idx / size) as i64 - c);
    (x.div_euclid(TILE) as i32, y.div_euclid(TILE) as i32)
}

impl Obs {
    pub fn new(bands: &[(u64, u64)], size: usize) -> Obs {
        Obs { size, bands: bands.to_vec(), out: vec![Tally::default(); bands.len()], depth: vec![UNV; size * size],
              prev: None, open: None, brun: None, prev_in_window_interior: false }
    }

    fn band(&self, area: u64) -> Option<usize> {
        self.bands.iter().position(|&(lo, hi)| area >= lo && area < hi)
    }

    /// Exact depth for every visited cell within L1 distance 5 of the newly visited cell
    /// (boundary status changes only at distance <= 1, and depth <= 4 needs sources within 4).
    fn refresh(&mut self, f: &Frame<'_>, idx: usize) {
        let s = self.size as i64;
        let (x0, y0) = ((idx % self.size) as i64, (idx / self.size) as i64);
        const W: usize = (2 * BALL + 1) as usize;
        let mut dist = [u8::MAX; W * W];
        let mut q: Vec<(i64, i64)> = Vec::new();
        for dy in -BALL..=BALL {
            for dx in -(BALL - dy.abs())..=(BALL - dy.abs()) {
                let (x, y) = (x0 + dx, y0 + dy);
                if x < 0 || y < 0 || x >= s || y >= s { continue; }
                let j = (y * s + x) as usize;
                if self.depth[j] != UNV && f.region.on_boundary(j) {
                    dist[((dy + BALL) as usize) * W + (dx + BALL) as usize] = 0;
                    q.push((dx, dy));
                }
            }
        }
        let mut head = 0;
        while head < q.len() {
            let (dx, dy) = q[head];
            head += 1;
            let d = dist[((dy + BALL) as usize) * W + (dx + BALL) as usize];
            if d >= RIM { continue; }
            for (ex, ey) in DIRS {
                let (nx, ny) = (dx + ex as i64, dy + ey as i64);
                if nx.abs() + ny.abs() > BALL { continue; }
                let (x, y) = (x0 + nx, y0 + ny);
                if x < 0 || y < 0 || x >= s || y >= s { continue; }
                let j = (y * s + x) as usize;
                let slot = ((ny + BALL) as usize) * W + (nx + BALL) as usize;
                if self.depth[j] != UNV && dist[slot] == u8::MAX {
                    dist[slot] = d + 1;
                    q.push((nx, ny));
                }
            }
        }
        for dy in -5i64..=5 {
            for dx in -(5 - dy.abs())..=(5 - dy.abs()) {
                let (x, y) = (x0 + dx, y0 + dy);
                if x < 0 || y < 0 || x >= s || y >= s { continue; }
                let j = (y * s + x) as usize;
                if self.depth[j] == UNV { continue; }
                let d = dist[((dy + BALL) as usize) * W + (dx + BALL) as usize];
                self.depth[j] = if d <= RIM { d } else { DEEP };
            }
        }
    }

    pub fn feed(&mut self, f: &Frame<'_>) {
        let c = (f.size / 2) as i64;
        let idx = ((c + f.pos.1) as usize) * f.size + (c + f.pos.0) as usize;
        let ncells = f.cells.len();
        let size = self.size;
        let Some(p) = self.prev.take() else {
            self.depth[idx] = DEEP;
            self.refresh(f, idx);
            self.prev = Some(Prev { idx, label: self.depth[idx] <= RIM, depth: self.depth[idx], z: f.state.z, area: f.state.area, ncells });
            return;
        };
        let k = self.band(p.area);
        let is_new = ncells > p.ncells;
        let l_a = is_new || self.depth[idx] <= RIM;
        if let Some(k) = k {
            let t = &mut self.out[k];
            t.steps += 1;
            t.depth_steps[p.depth.min(DEEP) as usize] += 1;
            for (h, (dx, dy)) in DIRS.iter().enumerate() {
                let n = (p.idx as isize + *dy as isize * size as isize + *dx as isize) as usize;
                let nl = self.depth[n] == UNV || self.depth[n] <= RIM;
                if nl != p.label {
                    let (kind, rim_cell) = if p.label { (0u8, p.idx) } else { (1u8, n) };
                    let (tx, ty) = tile_of(rim_cell, size);
                    *self.out[k].exposure.entry((tx, ty, h as u8, kind)).or_insert(0) += 1;
                }
            }
            // boundary runs
            if p.z {
                self.brun = match self.brun {
                    Some(n) => Some(n + 1),
                    None if self.prev_in_window_interior => Some(1),
                    None => None,
                };
            } else {
                if let Some(n) = self.brun.take() {
                    self.out[k].b_runs += 1;
                    self.out[k].b_run_steps += n;
                }
            }
            self.prev_in_window_interior = !p.z;
            if l_a != p.label {
                let (kind, rim_cell) = if p.label { (0u8, p.idx) } else { (1u8, idx) };
                let (tx, ty) = tile_of(rim_cell, size);
                let t = &mut self.out[k];
                *t.events.entry((tx, ty, f.heading, kind)).or_insert(0) += 1;
                if kind == 0 { t.exits += 1 } else { t.entries += 1 }
            }
        } else {
            self.brun = None;
            self.prev_in_window_interior = false;
        }
        if is_new {
            self.depth[idx] = DEEP;
            self.refresh(f, idx);
        }
        let l_new = self.depth[idx] <= RIM;
        if let Some(k) = k {
            if l_new != l_a {
                if l_new { self.out[k].reclass_in += 1 } else { self.out[k].reclass_out += 1 }
            }
            if p.label && !l_a && !l_new {
                self.open = Some((f.state.t, f.heading, k));
            }
        }
        if l_new
            && let Some((t0, h, kb)) = self.open.take() {
                self.out[kb].exc_n[h as usize] += 1;
                self.out[kb].exc_steps[h as usize] += f.state.t - t0;
            }
        self.prev = Some(Prev { idx, label: l_new, depth: self.depth[idx], z: f.state.z, area: f.state.area, ncells });
    }

    pub fn open_excursion(&self) -> bool {
        self.open.is_some()
    }

    pub fn finish(mut self) -> Vec<Tally> {
        if let Some((_, _, k)) = self.open.take() {
            self.out[k].exc_unresolved += 1;
        }
        self.out
    }
}

/// Boundary cells split by a flood fill of the unvisited cells from outside the bounding box:
/// (exterior boundary, boundary cells touching only enclosed unvisited cells). Reference-style
/// (not incremental): call at band edges only.
pub fn hole_split(f: &Frame<'_>) -> (u64, u64) {
    let size = f.size;
    let (mut x0, mut x1, mut y0, mut y1) = (usize::MAX, 0usize, usize::MAX, 0usize);
    for cell in f.cells {
        let (x, y) = (cell.idx % size, cell.idx / size);
        x0 = x0.min(x); x1 = x1.max(x); y0 = y0.min(y); y1 = y1.max(y);
    }
    let (x0, x1, y0, y1) = (x0 - 1, x1 + 1, y0 - 1, y1 + 1);
    let w = x1 - x0 + 1;
    let mut outside = vec![false; w * (y1 - y0 + 1)];
    let at = |x: usize, y: usize| (y - y0) * w + (x - x0);
    let mut q = std::collections::VecDeque::from([(x0, y0)]);
    outside[at(x0, y0)] = true;
    while let Some((x, y)) = q.pop_front() {
        for (dx, dy) in DIRS {
            let (nx, ny) = (x as i64 + dx as i64, y as i64 + dy as i64);
            if nx < x0 as i64 || nx > x1 as i64 || ny < y0 as i64 || ny > y1 as i64 { continue; }
            let (nx, ny) = (nx as usize, ny as usize);
            if f.ids[ny * size + nx] == u32::MAX && !outside[at(nx, ny)] {
                outside[at(nx, ny)] = true;
                q.push_back((nx, ny));
            }
        }
    }
    let (mut ext, mut hole) = (0, 0);
    for cell in f.cells {
        if !f.region.on_boundary(cell.idx) { continue; }
        let (x, y) = (cell.idx % size, cell.idx / size);
        let mut to_outside = false;
        for (dx, dy) in DIRS {
            let (nx, ny) = ((x as i64 + dx as i64) as usize, (y as i64 + dy as i64) as usize);
            if f.ids[ny * size + nx] == u32::MAX && outside[at(nx, ny)] { to_outside = true; }
        }
        if to_outside { ext += 1 } else { hole += 1 }
    }
    (ext, hole)
}

fn rng_next(s: &mut u64) -> u64 {
    *s = s.wrapping_add(0x9E37_79B9_7F4A_7C15);
    mix64(*s)
}

fn uniform(s: &mut u64) -> f64 {
    ((rng_next(s) >> 11) as f64 + 0.5) / (1u64 << 53) as f64
}

fn poisson(lambda: f64, s: &mut u64) -> u64 {
    if lambda < 30.0 {
        let l = (-lambda).exp();
        let (mut k, mut p) = (0u64, 1.0);
        loop {
            p *= uniform(s);
            if p <= l { return k; }
            k += 1;
        }
    }
    let z = (-2.0 * uniform(s).ln()).sqrt() * (2.0 * std::f64::consts::PI * uniform(s)).cos();
    (lambda + lambda.sqrt() * z + 0.5).max(0.0).floor() as u64
}

fn top_share(mut counts: Vec<u64>) -> f64 {
    let total: u64 = counts.iter().sum();
    if total == 0 { return f64::NAN; }
    counts.sort_unstable_by(|a, b| b.cmp(a));
    let m = counts.len().div_ceil(10);
    counts[..m].iter().sum::<u64>() as f64 / total as f64
}

/// Gate concentration: top-decile share of crossing events over the bins that have positive
/// exposure, minus the mean of the same share under Poisson event counts with total
/// intensity matched to the observed number of events and rates proportional to exposure.
/// Returns (observed share, null mean, null sd over draws, n bins, n events).
pub fn concentration(t: &Tally, seed: u64, draws: usize) -> (f64, f64, f64, usize, u64) {
    let keys: Vec<&Key> = t.exposure.keys().collect();
    let n: u64 = t.events.values().sum();
    assert!(t.events.keys().all(|k| t.exposure.contains_key(k)), "event outside exposure support");
    if keys.is_empty() || n == 0 { return (f64::NAN, f64::NAN, f64::NAN, keys.len(), n); }
    let observed = top_share(keys.iter().map(|k| *t.events.get(*k).unwrap_or(&0)).collect());
    let e_total: u64 = t.exposure.values().sum();
    let mut s = seed;
    let mut shares = Vec::with_capacity(draws);
    for _ in 0..draws {
        let counts: Vec<u64> = keys.iter().map(|k| poisson(n as f64 * t.exposure[*k] as f64 / e_total as f64, &mut s)).collect();
        shares.push(top_share(counts));
    }
    let mean = shares.iter().sum::<f64>() / draws as f64;
    let sd = (shares.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / (draws as f64 - 1.0)).sqrt();
    (observed, mean, sd, keys.len(), n)
}

/// Directional return spread: max - min over exit headings with at least `min_n` completed
/// excursions of ln(mean excursion duration). NaN with fewer than two such headings.
pub fn return_spread(exc_n: &[u64; 4], exc_steps: &[u64; 4], min_n: u64) -> f64 {
    let v: Vec<f64> = (0..4).filter(|&h| exc_n[h] >= min_n).map(|h| (exc_steps[h] as f64 / exc_n[h] as f64).ln()).collect();
    if v.len() < 2 { return f64::NAN; }
    v.iter().cloned().fold(f64::MIN, f64::max) - v.iter().cloned().fold(f64::MAX, f64::min)
}

pub struct Output {
    pub stop: crate::fixed_area::Stop,
    pub t: u64,
    pub bands: Vec<crate::fixed_area::BandOut>,
    pub tallies: Vec<Tally>,
    /// (exterior boundary, hole-only boundary) at each band's upper edge, when reached.
    pub holes: Vec<Option<(u64, u64)>>,
    pub cells: usize,
}

/// Follow a walker until every band closed AND every excursion begun in a band has returned
/// (or the cap, or board escape).
pub fn run<W: crate::walkers::Walker>(walker: W, size: usize, cap: u64, bands: &[(u64, u64)]) -> Output {
    let mut acc = crate::fixed_area::Accountant::new(bands);
    let mut obs = Obs::new(bands, size);
    let mut holes = vec![None; bands.len()];
    let mut cells = 0;
    let (stop, t) = crate::field_age::drive(walker, size, cap, |f| {
        cells = f.cells.len();
        acc.feed(&f.state);
        obs.feed(&f);
        for (k, &(_, hi)) in bands.iter().enumerate() {
            if holes[k].is_none() && f.state.area >= hi { holes[k] = Some(hole_split(&f)); }
        }
        acc.done() && !obs.open_excursion()
    });
    Output { stop, t, bands: acc.finish(), tallies: obs.finish(), holes, cells }
}
