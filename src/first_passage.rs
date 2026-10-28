//! Depth-crossing instrument for `experiments/archive/2026-10-kappa-first-passage`.
//!
//! * [`DepthField`]: exact depth (graph distance through visited cells to the nearest
//!   boundary cell, boundary = 0) maintained incrementally, clamped at [`CLAMP`].
//!   Inserting a cell never lowers any depth (checked against a BFS oracle in
//!   `tests/first_passage.rs`), so repair is an increase-propagation worklist.
//! * [`Sim`]: a clonable stepping machine (clone = in-memory checkpoint) that observes
//!   states exactly as `fixed_area::drive` does (state t = after t moves; departure t is
//!   t -> t+1) and tallies band occupation, boundary/interior episodes and
//!   milestone-to-milestone segments.
//!
//! Skipped-milestone policy: a milestone hit whose index differs from the current one by
//! more than one is recorded as a segment with `skipped = |diff| - 1`; the current
//! milestone becomes the hit one. A step is a *geometry jump* when it births a new cell and
//! the ant's depth changes by more than one (a physical move on a fixed field is 1-Lipschitz).
//! Area is constant during an interior episode, so the depth map and boundary set are
//! frozen for its whole duration: the "frozen-depth" termination coincides with the evolving one
//! (tested by brute force in `tests/first_passage.rs`).

mod ckpt;

use crate::fixed_area::{Geom, Region, Stop};
use crate::walkers::Walker;
use crate::DIRS;
use std::collections::{BTreeMap, VecDeque};

pub const MILESTONES: [u8; 8] = [0, 1, 2, 4, 8, 16, 32, 64];
pub const CLAMP: u8 = 65;
pub const HBINS: usize = 256;

fn milestone_idx(d: u8) -> Option<usize> {
    MILESTONES.iter().position(|&m| m == d)
}

#[derive(Clone)]
pub struct DepthField {
    pub size: usize,
    nbr: [isize; 4],
    pub region: Region,
    depth: Vec<u8>,
    work: VecDeque<usize>,
    /// Number of times a repair would have lowered a depth (must stay 0).
    pub decreases: u64,
    pub raised: u64,
}

impl DepthField {
    pub fn new(size: usize) -> Self {
        let s = size as isize;
        Self { size, nbr: [-s, 1, s, -1], region: Region::new(size), depth: vec![0; size * size], work: VecDeque::new(), decreases: 0, raised: 0 }
    }

    #[inline(always)]
    pub fn depth(&self, idx: usize) -> u8 {
        self.depth[idx]
    }

    fn recompute(&self, c: usize) -> u8 {
        if self.region.on_boundary(c) {
            return 0;
        }
        let mut m = CLAMP;
        for d in self.nbr {
            let j = (c as isize + d) as usize;
            debug_assert!(self.region.visited(j));
            m = m.min(self.depth[j].saturating_add(1));
        }
        m
    }

    pub fn visit(&mut self, idx: usize, x: i64, y: i64) {
        self.region.visit(idx, x, y);
        self.depth[idx] = self.recompute(idx);
        for d in self.nbr {
            let j = (idx as isize + d) as usize;
            if self.region.visited(j) {
                self.work.push_back(j);
            }
        }
        while let Some(c) = self.work.pop_front() {
            let new = self.recompute(c);
            let old = self.depth[c];
            if new == old {
                continue;
            }
            if new < old {
                self.decreases += 1;
            } else {
                self.raised += 1;
            }
            self.depth[c] = new;
            for d in self.nbr {
                let j = (c as isize + d) as usize;
                if self.region.visited(j) {
                    self.work.push_back(j);
                }
            }
        }
    }
}

/// Segment state at a milestone hit. M0 = (m, dir); M1 adds absolute heading and the colour class
/// under the ant; M2 adds the colour classes of the four axis neighbours relative to the heading
/// (3 bits each, 4 = unvisited) and the last four milestone labels (including this one).
/// Colour class = 2*turn(c) + turn(c+1) (L=0,R=1): comparable across rules of different length.
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct StateKey {
    pub m: u8,
    /// 0 = run start, 1 = arrived from a lower milestone, 2 = from a higher one.
    pub dir: u8,
    pub heading: u8,
    pub phase: u8,
    pub patch: u16,
    pub hist: u16,
}

impl StateKey {
    /// M1 backoff (patch and history unknown).
    pub fn m1(self) -> Self {
        Self { patch: OVERFLOW, hist: OVERFLOW, ..self }
    }
}

pub const OVERFLOW: u16 = 0xFFFF;

#[derive(Clone, Debug, Default, PartialEq)]
pub struct Pair {
    pub n: u64,
    pub time: u64,
    pub skipped: u64,
    pub jumps: u64,
    pub revisits: u64,
}

#[derive(Clone, Debug, PartialEq)]
pub struct EpTally {
    /// Episodes whose observed start lies in the band, run to resolution.
    pub entered_complete: u64,
    pub entered_complete_steps: u64,
    pub hist_n: Vec<u64>,
    pub hist_steps: Vec<u64>,
    /// Entered in band but unresolved at the end of the run, with the lower bound on duration.
    pub entered_unresolved: u64,
    pub unresolved_lower: u64,
    /// Episodes begun before the band (or at t=0, start unobserved) that overlap it.
    pub left_fragments: u64,
    pub left_fragment_overlap: u64,
    /// Exact in-band time of this label (all episodes).
    pub overlap: u64,
    /// Overlap contributed by unresolved episodes.
    pub unresolved_overlap: u64,
}

impl Default for EpTally {
    fn default() -> Self {
        Self { entered_complete: 0, entered_complete_steps: 0, hist_n: vec![0; HBINS], hist_steps: vec![0; HBINS], entered_unresolved: 0, unresolved_lower: 0, left_fragments: 0, left_fragment_overlap: 0, overlap: 0, unresolved_overlap: 0 }
    }
}

#[derive(Clone, Debug, Default, PartialEq)]
pub struct BandAgg {
    pub lo: u64,
    pub hi: u64,
    pub reached_lo: bool,
    pub reached_hi: bool,
    pub t_start: u64,
    pub t_end: u64,
    pub area_start: u64,
    pub area_end: u64,
    pub perim_end: u64,
    pub steps: u64,
    pub b_dep: u64,
    pub i_dep: u64,
    pub sum_pa: f64,
    /// [boundary, interior]
    pub eps: [EpTally; 2],
    /// Exact in-band time summed over all segments (must equal `steps`).
    pub seg_overlap: u64,
}

/// Duration bin: four per octave.
pub fn hbin(d: u64) -> usize {
    let o = 63 - d.leading_zeros() as usize;
    (o * 4 + ((((d as u128) << 2) >> o) & 3) as usize).min(HBINS - 1)
}

#[derive(Clone, Copy, Debug)]
struct Prev {
    z: bool,
    area: u64,
    perim: u64,
    depth: u8,
}

#[derive(Clone, Debug)]
struct Run {
    s: u64,
    z: bool,
    start_obs: bool,
}

#[derive(Clone, Debug)]
struct Seg {
    cur: usize,
    start_t: u64,
    key: StateKey,
    start_band: Option<usize>,
    revisits: u64,
    jump_any: bool,
    hist: u16,
    /// Hash of the radius-4 colour-class context at segment start (0 when context recording is off).
    r4: u64,
}

/// Optional radius-4 context table for the P4 sufficiency test: per (band, M2 start state, radius-4
/// context hash) the number of completed segments and how many of them ended at a higher milestone.
/// Capped at `max_rows`; beyond it new contexts fold to hash 0 (an "unsupported context" bucket).
#[derive(Clone)]
pub struct Ctx4 {
    max_rows: usize,
    offs: Vec<isize>,
    pub map: BTreeMap<(usize, StateKey, u64), (u64, u64)>,
    pub overflowed: u64,
}

pub const R4_FOLDED: u64 = 0;

#[derive(Clone)]
pub struct Sim<W: Walker + Clone> {
    walker: W,
    cap: u64,
    margin: i64,
    bands: Vec<BandAgg>,
    tau_lo: Vec<Option<u64>>,
    tau_hi: Vec<Option<u64>>,
    started: usize,
    active: Option<usize>,
    pub field: DepthField,
    colour: Vec<u8>,
    pos: (i64, i64),
    h: u8,
    pub t: u64,
    idx: usize,
    prev: Option<Prev>,
    run: Option<Run>,
    seg: Option<Seg>,
    /// (band of segment start, start state, destination state or None if open at the end).
    pub tallies: BTreeMap<(usize, StateKey, Option<StateKey>), Pair>,
    cls: Vec<u8>,
    max_pairs: usize,
    /// Segments folded to M1 backoff keys because the pair table was full.
    pub overflowed: u64,
    /// Steps that were a geometry jump (all, in or out of band).
    pub jump_steps: u64,
    /// Steps onto a visited cell whose depth changed by more than one (must stay 0).
    pub lipschitz_violations: u64,
    pub stop: Option<Stop>,
    /// Observed state sequence is recorded only when asked (tests).
    pub trace: Option<Vec<(bool, u64, u64, u8, Geom)>>,
    /// Radius-4 context recording (P4); off by default, never changes the trajectory or the pair table.
    pub ctx4: Option<Ctx4>,
}

impl<W: Walker + Clone> Sim<W> {
    pub fn new(walker: W, size: usize, cap: u64, bands: &[(u64, u64)]) -> Self {
        assert!(size >= 32 && size.is_multiple_of(2));
        for (k, &(lo, hi)) in bands.iter().enumerate() {
            assert!(lo >= 2 && hi > lo && (k == 0 || bands[k - 1].1 <= lo));
        }
        Self {
            walker,
            cap,
            margin: 6,
            bands: bands.iter().map(|&(lo, hi)| BandAgg { lo, hi, ..Default::default() }).collect(),
            tau_lo: vec![None; bands.len()],
            tau_hi: vec![None; bands.len()],
            started: 0,
            active: None,
            field: DepthField::new(size),
            colour: vec![0; size * size],
            pos: (0, 0),
            h: 0,
            t: 0,
            idx: (size / 2) * size + size / 2,
            prev: None,
            run: None,
            seg: None,
            tallies: BTreeMap::new(),
            cls: (0..256).map(|c| (c as u8).min(3)).collect(),
            max_pairs: 3_000_000,
            overflowed: 0,
            jump_steps: 0,
            lipschitz_violations: 0,
            stop: None,
            trace: None,
            ctx4: None,
        }
    }

    /// Record the radius-4 context table (see [`Ctx4`]).
    pub fn with_ctx4(mut self, max_rows: usize) -> Self {
        let size = self.field.size;
        let mut offs = Vec::new();
        for dy in -4i32..=4 {
            for dx in -4i32..=4 {
                if dx.abs() + dy.abs() <= 4 {
                    offs.push(dy as isize * size as isize + dx as isize);
                }
            }
        }
        self.ctx4 = Some(Ctx4 { max_rows, offs, map: BTreeMap::new(), overflowed: 0 });
        self
    }

    /// Hash of the radius-4 colour classes (3 bits per cell, 4 = unvisited); never equals [`R4_FOLDED`].
    fn r4_hash(&self) -> u64 {
        let Some(c) = &self.ctx4 else { return 0 };
        let mut h = 0xCBF2_9CE4_8422_2325u64;
        for &o in &c.offs {
            h = crate::walkers::mix64(h ^ self.class_at((self.idx as isize + o) as usize) as u64);
        }
        h | 1
    }

    pub fn with_trace(mut self) -> Self {
        self.trace = Some(Vec::new());
        self
    }

    /// Colour classes (see [`StateKey`]) for each colour value, e.g. from the rule.
    pub fn with_classes(mut self, cls: Vec<u8>) -> Self {
        assert!(cls.iter().all(|&c| c < 4));
        self.cls = cls;
        self
    }

    pub fn with_max_pairs(mut self, n: usize) -> Self {
        self.max_pairs = n;
        self
    }

    fn class_at(&self, j: usize) -> u16 {
        if self.field.region.visited(j) { self.cls[self.colour[j] as usize] as u16 } else { 4 }
    }

    fn key(&self, m: usize, dir: u8, hist: u16) -> StateKey {
        // relative to the heading: ahead, right, behind, left
        let s = self.field.size as isize;
        let nb = [-s, 1, s, -1];
        let mut patch = 0u16;
        for k in 0..4 {
            let j = (self.idx as isize + nb[(self.h as usize + k) & 3]) as usize;
            patch = (patch << 3) | self.class_at(j);
        }
        StateKey { m: m as u8, dir, heading: self.h, phase: self.cls[self.colour[self.idx] as usize], patch, hist }
    }

    /// True when every band closed and the run in force began after the last band ended
    /// (so every episode entered in a band has been resolved).
    fn finished(&self) -> bool {
        let Some(last) = self.tau_hi.last().copied().flatten() else { return false };
        self.run.as_ref().is_some_and(|r| r.s >= last)
    }

    /// Account the state at time `self.t` (before its departure).
    fn observe(&mut self, new_cell: bool) {
        let t = self.t;
        let reg = &self.field.region;
        let z = reg.on_boundary(self.idx);
        let (area, perim) = (reg.area, reg.perimeter);
        let depth = self.field.depth(self.idx);
        if let Some(tr) = &mut self.trace {
            tr.push((z, area, perim, depth, reg.geom()));
        }
        // 1. departure t-1
        if let Some(p) = self.prev
            && let Some(k) = self.active {
                let b = &mut self.bands[k];
                b.steps += 1;
                if p.z { b.b_dep += 1 } else { b.i_dep += 1 }
                b.sum_pa += p.perim as f64 / p.area as f64;
            }
        // 2. label change closes a run
        match &self.run {
            None => self.run = Some(Run { s: t, z, start_obs: false }),
            Some(r) if r.z != z => {
                let r = r.clone();
                self.close_run(&r, t, true);
                self.run = Some(Run { s: t, z, start_obs: true });
            }
            _ => {}
        }
        // 3. band boundaries
        if let Some(k) = self.active
            && area >= self.bands[k].hi {
                assert_eq!(area, self.bands[k].hi);
                let b = &mut self.bands[k];
                b.reached_hi = true;
                b.t_end = t;
                b.area_end = area;
                b.perim_end = perim;
                self.tau_hi[k] = Some(t);
                self.active = None;
            }
        if self.active.is_none() && self.started < self.bands.len() && area >= self.bands[self.started].lo {
            let k = self.started;
            assert_eq!(area, self.bands[k].lo);
            let b = &mut self.bands[k];
            b.reached_lo = true;
            b.t_start = t;
            b.area_start = area;
            self.tau_lo[k] = Some(t);
            self.started += 1;
            self.active = Some(k);
        }
        // 4. milestone segments
        match &mut self.seg {
            None => {
                let m = milestone_idx(depth).expect("start depth is 0");
                let key = self.key(m, 0, m as u16);
                let r4 = self.r4_hash();
                self.seg = Some(Seg { cur: m, start_t: t, key, start_band: self.active, revisits: 0, jump_any: false, hist: m as u16, r4 });
            }
            Some(_) => {
                let last = self.prev.unwrap().depth;
                let jump = new_cell && (depth as i32 - last as i32).abs() > 1;
                if !new_cell && (depth as i32 - last as i32).abs() > 1 {
                    self.lipschitz_violations += 1;
                }
                if jump {
                    self.jump_steps += 1;
                }
                let seg = self.seg.as_mut().unwrap();
                seg.jump_any |= jump;
                if let Some(j) = milestone_idx(depth) {
                    if j == seg.cur {
                        if last != depth {
                            seg.revisits += 1;
                        }
                    } else {
                        let seg = self.seg.take().unwrap();
                        self.end_seg(seg, Some(j), t);
                    }
                }
            }
        }
        self.prev = Some(Prev { z, area, perim, depth });
    }

    fn end_seg(&mut self, s: Seg, to: Option<usize>, t: u64) {
        let elapsed = t - s.start_t;
        // exact in-band time for every band
        for k in 0..self.bands.len() {
            if let Some(lo) = self.tau_lo[k] {
                let hi = self.tau_hi[k].unwrap_or(t);
                self.bands[k].seg_overlap += hi.min(t).saturating_sub(lo.max(s.start_t));
            }
        }
        let next = to.map(|j| {
            let dir = if j > s.cur { 1 } else { 2 };
            let hist = ((s.hist << 3) | j as u16) & 0xFFF;
            (self.key(j, dir, hist), hist)
        });
        if let Some(k) = s.start_band {
            let (mut a, mut b) = (s.key, next.map(|n| n.0));
            if self.tallies.len() >= self.max_pairs && !self.tallies.contains_key(&(k, a, b)) {
                a = a.m1();
                b = b.map(StateKey::m1);
                self.overflowed += 1;
            }
            let p = self.tallies.entry((k, a, b)).or_default();
            p.n += 1;
            p.time += elapsed;
            p.revisits += s.revisits;
            p.jumps += s.jump_any as u64;
            if let Some(j) = to {
                p.skipped += (j as i64 - s.cur as i64).unsigned_abs() - 1;
            }
        }
        if let (Some(k), Some(j)) = (s.start_band, to)
            && self.ctx4.is_some() {
                let c = self.ctx4.as_mut().unwrap();
                let mut key = (k, s.key, s.r4);
                if c.map.len() >= c.max_rows && !c.map.contains_key(&key) {
                    key.2 = R4_FOLDED;
                    c.overflowed += 1;
                }
                let e = c.map.entry(key).or_default();
                e.0 += 1;
                e.1 += (j > s.cur) as u64;
            }
        if let (Some(j), Some((key, hist))) = (to, next) {
            let r4 = self.r4_hash();
            self.seg = Some(Seg { cur: j, start_t: t, key, start_band: self.active, revisits: 0, jump_any: false, hist, r4 });
        }
    }

    fn close_run(&mut self, r: &Run, e: u64, resolved: bool) {
        let which = if r.z { 0 } else { 1 };
        let d = e - r.s;
        for k in 0..self.bands.len() {
            let Some(lo) = self.tau_lo[k] else { continue };
            let hi = self.tau_hi[k].unwrap_or(e);
            let ov = e.min(hi).saturating_sub(r.s.max(lo));
            let tally = &mut self.bands[k].eps[which];
            tally.overlap += ov;
            if !resolved {
                tally.unresolved_overlap += ov;
            }
            // entered: observed start inside [lo, hi). A band's own lo..hi holds even if hi unknown (= still open or e).
            let entered = r.start_obs && r.s >= lo && r.s < hi;
            if entered {
                if resolved {
                    tally.entered_complete += 1;
                    tally.entered_complete_steps += d;
                    let b = hbin(d);
                    tally.hist_n[b] += 1;
                    tally.hist_steps[b] += d;
                } else {
                    tally.entered_unresolved += 1;
                    tally.unresolved_lower = tally.unresolved_lower.max(d);
                }
            } else if ov > 0 && !(r.start_obs && r.s >= hi) {
                tally.left_fragments += 1;
                tally.left_fragment_overlap += ov;
            }
        }
    }

    /// Advance until a stop, or until `max_steps` more states have been observed (None = no limit).
    pub fn advance(&mut self, max_steps: Option<u64>) -> Option<Stop> {
        let c = (self.field.size / 2) as i64;
        let size = self.field.size as isize;
        let mut left = max_steps;
        loop {
            if let Some(s) = self.stop {
                return Some(s);
            }
            if let Some(l) = &mut left {
                if *l == 0 {
                    return None;
                }
                *l -= 1;
            }
            let new_cell = !self.field.region.visited(self.idx);
            if new_cell {
                self.colour[self.idx] = self.walker.initial_cell(self.pos.0, self.pos.1);
                self.field.visit(self.idx, self.pos.0, self.pos.1);
            }
            self.observe(new_cell);
            if self.finished() {
                self.stop = Some(Stop::Sink);
            } else if self.t >= self.cap {
                self.stop = Some(Stop::Budget);
            } else if self.pos.0.abs() >= c - self.margin || self.pos.1.abs() >= c - self.margin {
                self.stop = Some(Stop::Escaped);
            }
            if self.stop.is_some() {
                continue;
            }
            self.walker.step(&mut self.colour[self.idx], &mut self.h);
            let (dx, dy) = DIRS[self.h as usize];
            self.pos.0 += dx as i64;
            self.pos.1 += dy as i64;
            self.idx = (self.idx as isize + dy as isize * size + dx as isize) as usize;
            self.t += 1;
        }
    }

    /// Close open objects at the final state and return the results. Consumes a clone.
    pub fn finish(&self) -> Output {
        let mut s = self.clone();
        let t = s.t;
        if let Some(r) = s.run.clone() {
            s.close_run(&r, t, false);
        }
        if let Some(seg) = s.seg.take() {
            s.end_seg(seg, None, t);
        }
        if let (Some(k), Some(p)) = (s.active, s.prev) {
            s.bands[k].t_end = t;
            s.bands[k].area_end = p.area;
            s.bands[k].perim_end = p.perim;
        }
        Output { stop: s.stop, t, bands: s.bands, tallies: s.tallies, overflowed: s.overflowed, area: s.field.region.area, perimeter: s.field.region.perimeter, jump_steps: s.jump_steps, lipschitz_violations: s.lipschitz_violations, depth_decreases: s.field.decreases, depth_raises: s.field.raised, ctx4: s.ctx4.map(|c| (c.map, c.overflowed)) }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct Output {
    pub stop: Option<Stop>,
    pub t: u64,
    pub bands: Vec<BandAgg>,
    pub tallies: BTreeMap<(usize, StateKey, Option<StateKey>), Pair>,
    pub overflowed: u64,
    pub area: u64,
    pub perimeter: u64,
    pub jump_steps: u64,
    pub lipschitz_violations: u64,
    pub depth_decreases: u64,
    pub depth_raises: u64,
    /// Radius-4 context table and its overflow count, when recorded.
    pub ctx4: Option<(BTreeMap<(usize, StateKey, u64), (u64, u64)>, u64)>,
}

pub fn run<W: Walker + Clone>(walker: W, size: usize, cap: u64, bands: &[(u64, u64)]) -> Output {
    let mut s = Sim::new(walker, size, cap, bands);
    s.advance(None);
    s.finish()
}
