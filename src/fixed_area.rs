//! Fixed-area sampling with boundary/interior cycle accounting
//! (experiments/archive/2026-10-fixed-area-cycles; conventions in its NOTEBOOK.md).
//!
//! Two deliberately separate parts so each has its own oracle in `tests/fixed_area.rs`:
//! - the *producer* [`drive`]: a walker on a dense board plus an incrementally
//!   maintained visited region, yielding one state (label, area, perimeter,
//!   geometry) per time t;
//! - the *accountant* [`Accountant`]: a pure state machine over that stream and
//!   a list of area bands. It never sees the walker.
//!
//! State t is the state after t moves. Departure t is the move t -> t+1. The label
//! `z_t` is true (boundary, "B") iff the walker stands on a visited cell with at
//! least one unvisited 4-neighbour in state t, otherwise interior ("I"). The origin
//! is visited at t = 0, so `z_0` is B. Band [lo, hi) covers departures
//! tau(lo) <= t < tau(hi), tau(a) = first t with area >= a.

use crate::DIRS;
use crate::walkers::Walker;

const UNVISITED: u8 = u8::MAX;
pub const BINS: usize = 32;

/// Integer geometry of the visited set (coordinates relative to the start).
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub struct Geom {
    pub width: u32,
    pub height: u32,
    pub sx: i64,
    pub sy: i64,
    pub sxx: i64,
}

/// The visited region on a dense board. Same bookkeeping as `probe::Region`
/// (kept separate: that one is private and window-oriented).
#[derive(Clone)]
pub struct Region {
    unv: Vec<u8>,
    nbr: [isize; 4],
    pub area: u64,
    pub perimeter: u64,
    sx: i64,
    sy: i64,
    sxx: i64,
    min: (i64, i64),
    max: (i64, i64),
}

impl Region {
    pub fn new(size: usize) -> Region {
        let s = size as isize;
        Region { unv: vec![UNVISITED; size * size], nbr: [-s, 1, s, -1], area: 0, perimeter: 0, sx: 0, sy: 0, sxx: 0, min: (0, 0), max: (0, 0) }
    }

    #[inline(always)]
    pub fn visited(&self, idx: usize) -> bool {
        self.unv[idx] != UNVISITED
    }

    #[inline(always)]
    pub fn on_boundary(&self, idx: usize) -> bool {
        self.visited(idx) && self.unv[idx] > 0
    }

    pub fn visit(&mut self, idx: usize, x: i64, y: i64) {
        debug_assert!(!self.visited(idx));
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
        self.sx += x;
        self.sy += y;
        self.sxx += x * x + y * y;
        self.min = (self.min.0.min(x), self.min.1.min(y));
        self.max = (self.max.0.max(x), self.max.1.max(y));
    }

    pub fn size(&self) -> usize {
        self.nbr[2] as usize
    }

    /// Bounding box of the visited cells as (row lo, row hi, col lo, col hi) board indices; None if empty.
    pub fn bbox(&self) -> Option<(usize, usize, usize, usize)> {
        if self.area == 0 {
            return None;
        }
        let size = self.nbr[2] as usize;
        let c = (size / 2) as i64;
        Some(((c + self.min.1) as usize, (c + self.max.1) as usize, (c + self.min.0) as usize, (c + self.max.0) as usize))
    }

    /// Checkpoint form: scalars plus the board cropped to the visited bounding box.
    pub fn snap(&self, w: &mut crate::snap::Wr) {
        let size = self.nbr[2] as usize;
        w.u64(size as u64);
        w.u64(self.area);
        w.u64(self.perimeter);
        for v in [self.sx, self.sy, self.sxx, self.min.0, self.min.1, self.max.0, self.max.1] {
            w.i64(v);
        }
        crate::snap::put_crop(w, &self.unv, size, self.bbox());
    }

    pub fn unsnap(r: &mut crate::snap::Rd) -> Result<Region, String> {
        let size = r.u64()? as usize;
        let mut reg = Region::new(size);
        reg.area = r.u64()?;
        reg.perimeter = r.u64()?;
        reg.sx = r.i64()?;
        reg.sy = r.i64()?;
        reg.sxx = r.i64()?;
        reg.min = (r.i64()?, r.i64()?);
        reg.max = (r.i64()?, r.i64()?);
        crate::snap::get_crop(r, &mut reg.unv, size)?;
        Ok(reg)
    }

    pub fn geom(&self) -> Geom {
        Geom {
            width: (self.max.0 - self.min.0 + 1) as u32,
            height: (self.max.1 - self.min.1 + 1) as u32,
            sx: self.sx,
            sy: self.sy,
            sxx: self.sxx,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stop {
    /// The sink asked to stop (all bands closed).
    Sink,
    /// `cap` moves were made.
    Budget,
    /// The walker came within two cells of the board edge.
    Escaped,
}

/// One state of the stream.
#[derive(Clone, Copy, Debug)]
pub struct State {
    pub t: u64,
    pub z: bool,
    pub area: u64,
    pub perimeter: u64,
    pub geom: Geom,
}

/// Run `walker` on a `size` x `size` board, calling `sink` with every state
/// t = 0, 1, ... (including the final one, whose departure is not executed).
/// `sink` returns true to stop. Returns why the run ended and the final t.
pub fn drive<W: Walker>(mut walker: W, size: usize, cap: u64, mut sink: impl FnMut(&State) -> bool) -> (Stop, u64) {
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
    region.visit(idx, 0, 0);
    let mut t = 0u64;
    let mut escaped = false;
    loop {
        let st = State { t, z: region.on_boundary(idx), area: region.area, perimeter: region.perimeter, geom: region.geom() };
        if sink(&st) {
            return (Stop::Sink, t);
        }
        if t >= cap {
            return (Stop::Budget, t);
        }
        if escaped {
            return (Stop::Escaped, t);
        }
        walker.step(&mut colour[idx], &mut h);
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        idx = (idx as isize + dy as isize * s + dx as isize) as usize;
        t += 1;
        if !region.visited(idx) {
            region.visit(idx, x, y);
        }
        escaped = x.abs() >= c - 2 || y.abs() >= c - 2;
    }
}

/// Per-label episode accounting inside one band.
#[derive(Clone, Debug, PartialEq)]
pub struct EpStats {
    /// Complete-contained episodes: both transitions observed, whole episode inside the band.
    pub complete: u64,
    pub complete_steps: u64,
    /// Complete-contained episodes by floor(log2(duration)).
    pub bin_n: [u64; BINS],
    pub bin_steps: [u64; BINS],
    /// Intersections of all other episodes with the band (clipped by a band edge, the run
    /// start, or the end of the run).
    pub clipped_frags: u64,
    pub clipped_steps: u64,
    pub clipped_max: u64,
}

impl Default for EpStats {
    fn default() -> Self {
        EpStats { complete: 0, complete_steps: 0, bin_n: [0; BINS], bin_steps: [0; BINS], clipped_frags: 0, clipped_steps: 0, clipped_max: 0 }
    }
}

impl EpStats {
    pub fn steps(&self) -> u64 {
        self.complete_steps + self.clipped_steps
    }
}

#[derive(Clone, Debug, Default, PartialEq)]
pub struct BandOut {
    pub lo: u64,
    pub hi: u64,
    pub reached_lo: bool,
    pub reached_hi: bool,
    /// tau(lo) and tau(hi) (or the final t when hi was not reached).
    pub t_start: u64,
    pub t_end: u64,
    pub area_start: u64,
    pub area_end: u64,
    pub perim_start: u64,
    pub perim_end: u64,
    /// Departures in the band, counted directly (independent of the episode tables).
    pub steps: u64,
    pub b_dep: u64,
    pub i_dep: u64,
    /// Departures from an interior cell that increased the area: must be 0.
    pub fresh_from_interior: u64,
    /// Sum over departure states of P_t / A_t, accumulated in increasing t.
    pub sum_pa: f64,
    pub geom_start: Geom,
    pub geom_end: Geom,
    pub b: EpStats,
    pub i: EpStats,
    /// Complete cycles (complete B then complete I) wholly inside the band.
    pub cycles: u64,
    pub cycle_d_sum: u64,
    pub cycle_t_sum: u64,
    /// Durations of complete-contained I episodes, in order of completion.
    pub i_durations: Vec<u32>,
}

impl BandOut {
    pub fn new_cells(&self) -> u64 {
        self.area_end - self.area_start
    }

    /// Nearest-rank quantile of the complete-contained I durations:
    /// sorted[ceil(q n) - 1]. None when there are none.
    pub fn i_quantile(&self, q: f64) -> Option<u32> {
        nearest_rank(&self.i_durations, q)
    }
}

pub fn nearest_rank(v: &[u32], q: f64) -> Option<u32> {
    if v.is_empty() {
        return None;
    }
    let mut s = v.to_vec();
    s.sort_unstable();
    let k = ((q * s.len() as f64).ceil() as usize).clamp(1, s.len());
    Some(s[k - 1])
}

struct Run {
    s: u64,
    z: bool,
    start_obs: bool,
    /// Bands that already received this run's right-clipped fragment.
    credited: u64,
}

/// The accounting state machine. Feed it every state in order, then `finish`.
pub struct Accountant {
    bands: Vec<BandOut>,
    started: usize,
    /// Index of the band currently open (started, not closed).
    active: Option<usize>,
    prev: Option<State>,
    run: Option<Run>,
    /// Last completed B episode: (start, start observed).
    last_b: Option<(u64, bool)>,
}

impl Accountant {
    pub fn new(bands: &[(u64, u64)]) -> Accountant {
        assert!(bands.len() <= 64);
        for (k, &(lo, hi)) in bands.iter().enumerate() {
            assert!(lo >= 2 && hi > lo, "band needs 2 <= lo < hi");
            assert!(k == 0 || bands[k - 1].1 <= lo, "bands must be ordered and disjoint");
        }
        Accountant {
            bands: bands.iter().map(|&(lo, hi)| BandOut { lo, hi, ..Default::default() }).collect(),
            started: 0,
            active: None,
            prev: None,
            run: None,
            last_b: None,
        }
    }

    /// All bands have been closed.
    pub fn done(&self) -> bool {
        self.started == self.bands.len() && self.active.is_none()
    }

    pub fn feed(&mut self, st: &State) {
        // 1. Departure t-1 was executed: account it to the open band.
        if let Some(p) = self.prev {
            assert_eq!(st.t, p.t + 1);
            assert!(st.area == p.area || st.area == p.area + 1, "area grows by at most one per step");
            if let Some(k) = self.active {
                let b = &mut self.bands[k];
                b.steps += 1;
                if p.z {
                    b.b_dep += 1;
                } else {
                    b.i_dep += 1;
                    if st.area > p.area {
                        b.fresh_from_interior += 1;
                    }
                }
                b.sum_pa += p.perimeter as f64 / p.area as f64;
            }
        }
        // 2. A label change ends the current run (transition observed at t).
        match &self.run {
            None => self.run = Some(Run { s: st.t, z: st.z, start_obs: false, credited: 0 }),
            Some(r) if r.z != st.z => {
                let (s, z, so) = (r.s, r.z, r.start_obs);
                self.close_run(s, st.t, z, so, true);
                self.run = Some(Run { s: st.t, z: st.z, start_obs: true, credited: 0 });
            }
            _ => {}
        }
        // 3. Band boundaries at this state.
        if let Some(k) = self.active
            && st.area >= self.bands[k].hi {
                assert_eq!(st.area, self.bands[k].hi);
                let b = &mut self.bands[k];
                b.reached_hi = true;
                b.t_end = st.t;
                b.area_end = st.area;
                b.perim_end = st.perimeter;
                b.geom_end = st.geom;
                // Credit the open run's right-clipped fragment now: its band is closing.
                let r = self.run.as_mut().unwrap();
                let (s, z) = (r.s, r.z);
                r.credited |= 1 << k;
                let from = s.max(self.bands[k].t_start);
                self.bands[k].add_clipped(from, st.t, z);
                self.active = None;
            }
        if self.active.is_none() && self.started < self.bands.len() && st.area >= self.bands[self.started].lo {
            let k = self.started;
            assert_eq!(st.area, self.bands[k].lo);
            let b = &mut self.bands[k];
            b.reached_lo = true;
            b.t_start = st.t;
            b.area_start = st.area;
            b.perim_start = st.perimeter;
            b.geom_start = st.geom;
            self.started += 1;
            self.active = Some(k);
        }
        self.prev = Some(*st);
    }

    /// Close the open run at the final state (its departure is not executed) and the open band.
    pub fn finish(mut self) -> Vec<BandOut> {
        if let (Some(r), Some(p)) = (&self.run, self.prev) {
            let (s, z, so) = (r.s, r.z, r.start_obs);
            self.close_run(s, p.t, z, so, false);
        }
        if let (Some(k), Some(p)) = (self.active, self.prev) {
            let b = &mut self.bands[k];
            b.t_end = p.t;
            b.area_end = p.area;
            b.perim_end = p.perimeter;
            b.geom_end = p.geom;
        }
        self.bands
    }

    fn close_run(&mut self, s: u64, e: u64, z: bool, start_obs: bool, end_obs: bool) {
        let credited = self.run.as_ref().map_or(0, |r| r.credited);
        // Pair with the previous B episode to form a cycle: B complete, then I complete.
        let mut cycle: Option<(u64, u64, u64)> = None; // (start, end, D)
        if z {
            self.last_b = Some((s, start_obs));
        } else if start_obs && end_obs
            && let Some((bs, true)) = self.last_b {
                cycle = Some((bs, e, s - bs));
            }
        for k in 0..self.started {
            let band = &mut self.bands[k];
            if credited >> k & 1 == 1 {
                continue;
            }
            let t_end = if self.active == Some(k) { e } else { band.t_end };
            let (lo_i, hi_i) = (s.max(band.t_start), e.min(t_end));
            if lo_i >= hi_i {
                continue;
            }
            if start_obs && end_obs && s >= band.t_start && e <= t_end {
                band.add_complete(s, e, z);
            } else {
                band.add_clipped(lo_i, hi_i, z);
            }
            if let Some((cs, ce, d)) = cycle
                && cs >= band.t_start && ce <= t_end {
                    band.cycles += 1;
                    band.cycle_d_sum += d;
                    band.cycle_t_sum += e - s;
                }
        }
    }
}

impl BandOut {
    fn add_complete(&mut self, s: u64, e: u64, z: bool) {
        let d = e - s;
        let st = if z { &mut self.b } else { &mut self.i };
        st.complete += 1;
        st.complete_steps += d;
        let j = (63 - d.leading_zeros()) as usize;
        st.bin_n[j] += 1;
        st.bin_steps[j] += d;
        if !z {
            self.i_durations.push(d as u32);
        }
    }

    fn add_clipped(&mut self, s: u64, e: u64, z: bool) {
        if e <= s {
            return;
        }
        let st = if z { &mut self.b } else { &mut self.i };
        st.clipped_frags += 1;
        st.clipped_steps += e - s;
        st.clipped_max = st.clipped_max.max(e - s);
    }
}

#[derive(Debug)]
pub struct RunOut {
    pub bands: Vec<BandOut>,
    pub stop: Stop,
    pub t_final: u64,
    pub area_final: u64,
}

/// Run a walker until every band has closed, the budget `cap` is spent, or it escapes.
pub fn run<W: Walker>(walker: W, size: usize, cap: u64, bands: &[(u64, u64)]) -> RunOut {
    let mut acc = Accountant::new(bands);
    let mut area_final = 0;
    let (stop, t_final) = drive(walker, size, cap, |st| {
        acc.feed(st);
        area_final = st.area;
        acc.done()
    });
    RunOut { bands: acc.finish(), stop, t_final, area_final }
}
