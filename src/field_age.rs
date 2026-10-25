//! Observation-only discovery/visit instrument for the tail-budget and age pilots.
//! Discovery includes arrivals; visits count departures (colour reads). An initial
//! patch colour is a phase offset, not an unobserved number of completed cycles.
use crate::fixed_area::{Accountant, BandOut, Geom, Region, State, Stop};
use crate::walkers::Walker;
use crate::DIRS;
use std::collections::{BTreeMap, VecDeque};

#[derive(Clone, Debug)]
pub struct Cell {
    pub idx: usize,
    pub born: u64,
    pub visits: u64,
    pub initial: u8,
}

pub struct Frame<'a> {
    pub state: State,
    pub pos: (i64, i64),
    pub heading: u8,
    pub phase: u8,
    pub current: usize,
    pub cells: &'a [Cell],
    pub ids: &'a [u32],
    pub region: &'a Region,
    pub size: usize,
}

/// Dense colour/region/id boards (6 bytes per board cell), sparse histories.
/// `sink` sees every state, including the final state before any departure.
pub fn drive<W: Walker>(mut walker: W, size: usize, cap: u64, mut sink: impl FnMut(Frame<'_>) -> bool) -> (Stop, u64) {
    assert!(size >= 16 && size.is_multiple_of(2));
    let c = (size / 2) as i64;
    let mut colours = vec![0u8; size.checked_mul(size).unwrap()];
    let mut ids = vec![u32::MAX; colours.len()];
    let mut cells = Vec::<Cell>::new();
    let mut region = Region::new(size);
    let (mut x, mut y, mut h, mut t) = (0i64, 0i64, 0u8, 0u64);
    let mut idx = (c * size as i64 + c) as usize;
    loop {
        if ids[idx] == u32::MAX {
            ids[idx] = u32::try_from(cells.len()).expect("history index overflow");
            assert_ne!(ids[idx], u32::MAX);
            // Lazy initialisation is valid because Walker::initial_cell is pure
            // and the cell cannot be read before its first arrival.
            colours[idx] = walker.initial_cell(x, y);
            cells.push(Cell { idx, born: t, visits: 0, initial: colours[idx] });
            region.visit(idx, x, y);
        }
        let st = State { t, z: region.on_boundary(idx), area: region.area, perimeter: region.perimeter, geom: region.geom() };
        if sink(Frame { state: st, pos: (x, y), heading: h, phase: colours[idx], current: ids[idx] as usize, cells: &cells, ids: &ids, region: &region, size }) {
            return (Stop::Sink, t);
        }
        if t == cap { return (Stop::Budget, t); }
        if x.abs() >= c - 2 || y.abs() >= c - 2 { return (Stop::Escaped, t); }
        let cell = &mut cells[ids[idx] as usize];
        cell.visits = cell.visits.checked_add(1).expect("visit overflow");
        walker.step(&mut colours[idx], &mut h);
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        idx = (idx as isize + dy as isize * size as isize + dx as isize) as usize;
        t = t.checked_add(1).unwrap();
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct Census {
    pub band: usize,
    pub target: u64,
    pub t: u64,
    pub area: u64,
    pub perimeter: u64,
    pub geom: Geom,
    pub rim_n: usize,
    pub immature: f64,
    pub median_log_age: f64,
    pub cycle_variance: f64,
}

/// Exact graph distance on the visited set to ANY visited boundary, holes
/// included. Boundary depth is zero; census includes depths 0..=4.
pub fn census(f: &Frame<'_>, band: usize, target: u64, n: u64) -> Census {
    assert!(n > 0);
    let mut depth = vec![u8::MAX; f.cells.len()];
    let mut q = VecDeque::new();
    for (i, cell) in f.cells.iter().enumerate() {
        if f.region.on_boundary(cell.idx) { depth[i] = 0; q.push_back(i); }
    }
    while let Some(i) = q.pop_front() {
        if depth[i] == 4 { continue; }
        for d in [-(f.size as isize), 1, f.size as isize, -1] {
            let j = (f.cells[i].idx as isize + d) as usize;
            let id = f.ids[j];
            if id != u32::MAX && depth[id as usize] == u8::MAX {
                depth[id as usize] = depth[i] + 1;
                q.push_back(id as usize);
            }
        }
    }
    let rim: Vec<&Cell> = f.cells.iter().zip(&depth).filter(|(_, d)| **d <= 4).map(|(c, _)| c).collect();
    let mut ages: Vec<u64> = rim.iter().map(|c| f.state.t - c.born).collect();
    ages.sort_unstable();
    let m = rim.len() as f64;
    let mean = rim.iter().map(|c| (c.visits / n) as f64).sum::<f64>() / m;
    let variance = rim.iter().map(|c| ((c.visits / n) as f64 - mean).powi(2)).sum::<f64>() / m;
    let median = if ages.len() % 2 == 1 { (ages[ages.len()/2] as f64).ln_1p() }
        else { ((ages[ages.len()/2-1] as f64).ln_1p() + (ages[ages.len()/2] as f64).ln_1p()) / 2.0 };
    Census { band, target, t: f.state.t, area: f.state.area, perimeter: f.state.perimeter, geom: f.state.geom, rim_n: rim.len(),
        immature: rim.iter().filter(|c| c.visits < n).count() as f64 / m, median_log_age: median, cycle_variance: variance }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Tail {
    pub completed_n: [u64; 64],
    pub completed_steps: [u64; 64],
    pub overlap_steps: u64,
    pub unresolved_overlap: u64,
    pub unresolved_duration_lower: u64,
    pub left_entry_unknown: u64,
    pub entered_n: [u64; 64],
    pub entered_steps: [u64; 64],
}

impl Default for Tail {
    fn default() -> Self {
        Self { completed_n: [0;64], completed_steps: [0;64], overlap_steps: 0, unresolved_overlap: 0,
            unresolved_duration_lower: 0, left_entry_unknown: 0, entered_n: [0;64], entered_steps: [0;64] }
    }
}

/// Follow every interior episode intersecting a band, including beyond hi.
/// Full durations and in-band overlap are distinct. No finite upper bound is
/// asserted for a return unresolved at cap.
pub struct Tails {
    bands: Vec<(u64,u64)>,
    intervals: Vec<(Option<u64>, Option<u64>)>,
    out: Vec<Tail>,
    open: Option<(u64, bool)>,
    prev: Option<State>,
}

impl Tails {
    pub fn new(bands: &[(u64,u64)]) -> Self {
        Self { bands: bands.to_vec(), intervals: vec![(None,None); bands.len()], out: vec![Tail::default(); bands.len()], open: None, prev: None }
    }
    pub fn feed(&mut self, st: State) {
        for (k, &(lo,hi)) in self.bands.iter().enumerate() {
            if st.area >= lo && self.intervals[k].0.is_none() { self.intervals[k].0 = Some(st.t); }
            if st.area >= hi && self.intervals[k].1.is_none() { self.intervals[k].1 = Some(st.t); }
        }
        if self.prev.is_some_and(|p| !p.z) && st.z { self.close(st.t, true); }
        if !st.z && self.open.is_none() { self.open = Some((st.t, self.prev.is_some())); }
        self.prev = Some(st);
    }
    fn close(&mut self, t: u64, resolved: bool) {
        if let Some((s, known)) = self.open.take() {
            let duration = t-s;
            if duration == 0 { return; }
            let bin = (63-duration.leading_zeros()) as usize;
            for (k, &(lo, hi)) in self.intervals.iter().enumerate() {
                let Some(lo) = lo else { continue; };
                let overlap = t.min(hi.unwrap_or(t)).saturating_sub(s.max(lo));
                if overlap == 0 { continue; }
                let out = &mut self.out[k];
                out.overlap_steps += overlap;
                if resolved && known {
                    out.completed_n[bin] += 1;
                    out.completed_steps[bin] += duration;
                    if s >= lo && s < hi.unwrap_or(t) { out.entered_n[bin] += 1; out.entered_steps[bin] += duration; }
                } else {
                    out.unresolved_overlap += overlap;
                    out.unresolved_duration_lower = duration;
                    if !known { out.left_entry_unknown += overlap; }
                }
            }
        }
    }
    pub fn done(&self) -> bool {
        let Some(last_end) = self.intervals.last().and_then(|v| v.1) else { return false; };
        self.open.is_none_or(|(s,_)| s >= last_end)
    }
    pub fn finish(mut self) -> Vec<Tail> {
        if let Some(p) = self.prev { self.close(p.t, false); }
        self.out
    }
}

/// Key: band, B/I departure, log2(1+age), log2(1+visits), heading, phase.
/// Value: departures at risk, label transitions. These are step-weighted
/// conditional transition frequencies, not cell-weighted census features.
pub type Hazards = BTreeMap<(usize,bool,u8,u8,u8,u8), (u64,u64)>;
fn logbin(v: u64) -> u8 { (63-v.checked_add(1).unwrap().leading_zeros()) as u8 }

pub struct Output {
    pub stop: Stop,
    pub t: u64,
    pub bands: Vec<BandOut>,
    pub tails: Vec<Tail>,
    pub censuses: Vec<Census>,
    pub hazards: Hazards,
    pub cells: usize,
}

pub fn run<W: Walker>(walker: W, n: u64, size: usize, cap: u64, bands: &[(u64,u64)]) -> Output {
    let mut accountant = Accountant::new(bands);
    let mut tails = Tails::new(bands);
    let mut censuses = Vec::new();
    let mut hazards = Hazards::new();
    let mut prev_key = None;
    let mut prev_z = false;
    let mut targets: Vec<(u64,usize)> = bands.iter().enumerate().flat_map(|(k,&(lo,hi))| [(lo,k), (lo+(hi-lo)/2,k), (hi,k)]).collect();
    targets.sort_unstable();
    let mut next = 0;
    let mut cells = 0;
    let (stop,t) = drive(walker,size,cap, |f| {
        cells = f.cells.len();
        accountant.feed(&f.state);
        tails.feed(f.state);
        if let Some(key) = prev_key.take() {
            let h = hazards.entry(key).or_insert((0,0));
            h.0 += 1;
            h.1 += u64::from(f.state.z != prev_z);
        }
        while next < targets.len() && f.state.area >= targets[next].0 {
            let (a,k) = targets[next];
            censuses.push(census(&f,k,a,n));
            next += 1;
        }
        if tails.done() { return true; }
        if let Some((k,_)) = bands.iter().enumerate().find(|(_,b)| f.state.area >= b.0 && f.state.area < b.1) {
            let c = &f.cells[f.current];
            prev_key = Some((k,f.state.z,logbin(f.state.t-c.born),logbin(c.visits),f.heading,f.phase));
            prev_z = f.state.z;
        }
        false
    });
    Output { stop,t,bands: accountant.finish(),tails: tails.finish(),censuses,hazards,cells }
}
