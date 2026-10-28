//! Bulk fingerprint of a walker on an area-matched mature field (W5 of experiments/archive/2026-10-kappa-rule-space).
//!
//! `run_bulk` runs a walker from the start until the visited area first reaches `a0`, freezes a depth
//! mask, then records `t_rec` further steps. A cell's depth is its 4-neighbour distance to the nearest
//! cell that was still unvisited at that moment (a probe boundary cell has depth 0). Unvisited cells only
//! disappear, so the frozen depth is a lower bound on the true depth for the whole recording: a step on a
//! cell of frozen depth >= `d0` is a *bulk* step whatever the territory did meanwhile. Lagged
//! quantities use a pair of steps (j-m, j) only if every step in j-m..=j is bulk.
//!
//! `fingerprint` is a pure function of the recorded trajectory so that `tests/kappa_rs_bulk.rs` can check it
//! against an obvious O(n * lag) oracle on arbitrary trajectories.

use crate::DIRS;
use crate::colourflux::MAXC;
use crate::walkers::Walker;

pub const MAXLAG: usize = 256;
pub const MSD_LAGS: [usize; 3] = [64, 512, 4096];
pub const HEAD_LAG: usize = 64;
pub const RET_WIN: usize = 32;
pub const REUSE_WIN: u64 = 64;
pub const GAP_BINS: usize = 18;
const NONE: u32 = u32::MAX;

/// One entry per recorded step, indexed by the step's start.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Traj {
    pub x: Vec<i32>,
    pub y: Vec<i32>,
    /// Board index of the start cell (any injective cell label works; `fingerprint` only compares them).
    pub cell: Vec<u32>,
    /// Colour of the start cell before the step.
    pub colour: Vec<u8>,
    /// Heading change of the step, quarter turns clockwise mod 4.
    pub dh: Vec<u8>,
    /// Heading after the step.
    pub head: Vec<u8>,
    pub bulk: Vec<bool>,
    /// Start cell was last visited (as a step start, any time since t = 0) within `REUSE_WIN` steps.
    pub reuse: Vec<bool>,
}

impl Traj {
    pub fn len(&self) -> usize {
        self.x.len()
    }
    pub fn is_empty(&self) -> bool {
        self.x.is_empty()
    }
}

/// Raw integer tallies; every derived statistic is computed downstream (deterministic, no float order issues here).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Fingerprint {
    pub n_rec: u64,
    pub n_bulk: u64,
    pub sum_s: i64,
    pub sum_s2: i64,
    /// Index m = 1..=MAXLAG (index 0 unused): sum of s_j s_{j-m} and number of valid pairs.
    pub turn_s: Vec<i64>,
    pub turn_n: Vec<u64>,
    pub msd_sum: [u64; 3],
    pub msd_n: [u64; 3],
    pub head_sum: i64,
    pub head_n: u64,
    pub ret_hit: u64,
    pub ret_elig: u64,
    /// First-return gaps (valid pairs only) by floor(log2 gap).
    pub gap_hist: [u64; GAP_BINS],
    pub n_reuse: u64,
    pub dh_hist: [u64; 4],
    /// Bulk steps by start colour.
    pub col_steps: [u64; MAXC],
}

/// `board_len` bounds the cell labels in `tr.cell`.
pub fn fingerprint(tr: &Traj, board_len: usize) -> Fingerprint {
    let n = tr.len();
    // runlen[j] = number of consecutive bulk steps ending at j (0 if j is not bulk).
    let mut runlen = vec![0u32; n];
    for j in 0..n {
        runlen[j] = if tr.bulk[j] { (if j > 0 { runlen[j - 1] } else { 0 }) + 1 } else { 0 };
    }
    let sgn = |dh: u8| -> i32 {
        match dh {
            1 => 1,
            3 => -1,
            _ => 0,
        }
    };
    let s: Vec<i32> = tr.dh.iter().map(|&d| sgn(d)).collect();
    let mut fp = Fingerprint {
        n_rec: n as u64,
        n_bulk: 0,
        sum_s: 0,
        sum_s2: 0,
        turn_s: vec![0; MAXLAG + 1],
        turn_n: vec![0; MAXLAG + 1],
        msd_sum: [0; 3],
        msd_n: [0; 3],
        head_sum: 0,
        head_n: 0,
        ret_hit: 0,
        ret_elig: 0,
        gap_hist: [0; GAP_BINS],
        n_reuse: 0,
        dh_hist: [0; 4],
        col_steps: [0; MAXC],
    };
    const COS: [i64; 4] = [1, 0, -1, 0];
    for j in 0..n {
        if !tr.bulk[j] {
            continue;
        }
        fp.n_bulk += 1;
        fp.sum_s += s[j] as i64;
        fp.sum_s2 += (s[j] * s[j]) as i64;
        fp.dh_hist[tr.dh[j] as usize] += 1;
        fp.col_steps[tr.colour[j] as usize] += 1;
        if tr.reuse[j] {
            fp.n_reuse += 1;
        }
        let r = runlen[j] as usize;
        for m in 1..=MAXLAG.min(r - 1) {
            fp.turn_s[m] += (s[j] * s[j - m]) as i64;
            fp.turn_n[m] += 1;
        }
        for (a, &l) in MSD_LAGS.iter().enumerate() {
            if r > l {
                let (dx, dy) = ((tr.x[j] - tr.x[j - l]) as i64, (tr.y[j] - tr.y[j - l]) as i64);
                fp.msd_sum[a] += (dx * dx + dy * dy) as u64;
                fp.msd_n[a] += 1;
            }
        }
        if r > HEAD_LAG {
            fp.head_sum += COS[((tr.head[j] + 4 - tr.head[j - HEAD_LAG]) & 3) as usize];
            fp.head_n += 1;
        }
    }
    // First returns: nv[i] = time of the next step starting on the same cell.
    let mut last = vec![NONE; board_len];
    let mut nv = vec![NONE; n];
    for j in 0..n {
        let c = tr.cell[j] as usize;
        if last[c] != NONE {
            nv[last[c] as usize] = j as u32;
        }
        last[c] = j as u32;
    }
    for i in 0..n {
        if nv[i] == NONE {
            continue;
        }
        let j = nv[i] as usize;
        let g = j - i;
        if runlen[j] as usize > g {
            fp.gap_hist[g.ilog2() as usize] += 1;
        }
    }
    for i in 0..n.saturating_sub(RET_WIN) {
        if runlen[i + RET_WIN] as usize > RET_WIN {
            fp.ret_elig += 1;
            if nv[i] != NONE && (nv[i] as usize) - i <= RET_WIN {
                fp.ret_hit += 1;
            }
        }
    }
    fp
}

/// Visited region with the probe's boundary bookkeeping (as `colourflux::Region`; `tests/kappa_rs_bulk.rs` checks the depths built on it).
struct Region {
    size: usize,
    /// For visited cells: number of never-visited 4-neighbours. 255 otherwise.
    unv: Vec<u8>,
    nbr: [isize; 4],
    area: u64,
    lo: (usize, usize),
    hi: (usize, usize),
}

impl Region {
    fn new(size: usize) -> Region {
        let s = size as isize;
        Region { size, unv: vec![255; size * size], nbr: [-s, 1, s, -1], area: 0, lo: (usize::MAX, usize::MAX), hi: (0, 0) }
    }

    fn visit(&mut self, idx: usize) {
        let mut u = 0u8;
        for d in self.nbr {
            let j = (idx as isize + d) as usize;
            if self.unv[j] == 255 {
                u += 1;
            } else {
                self.unv[j] -= 1;
            }
        }
        self.unv[idx] = u;
        self.area += 1;
        let (gx, gy) = (idx % self.size, idx / self.size);
        self.lo = (self.lo.0.min(gx), self.lo.1.min(gy));
        self.hi = (self.hi.0.max(gx), self.hi.1.max(gy));
    }
}

#[derive(Clone, Copy, Debug)]
pub struct BulkParams {
    pub size: usize,
    /// Territory size at which the field counts as mature and the depth mask is frozen.
    pub a0: u64,
    /// Steps recorded after A0.
    pub t_rec: usize,
    pub d0: u32,
    /// Give up if A0 is not reached by this many steps.
    pub max_steps: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Status {
    Ok,
    /// A0 not reached within `max_steps`.
    NoA0,
    /// Within two cells of the board edge before the recording ended.
    Escaped,
}

pub struct BulkRun {
    pub status: Status,
    /// Steps taken when the area first reached A0.
    pub t_star: u64,
    pub area0: u64,
    pub area_end: u64,
    /// Cells with frozen depth >= d0.
    pub mask_cells: u64,
    /// Colour histogram of the mask cells at the end of the recording.
    pub core_hist: [u64; MAXC],
    pub fp: Option<Fingerprint>,
    pub traj: Option<Traj>,
}

pub fn run_bulk<W: Walker>(mut walker: W, p: &BulkParams, keep_traj: bool) -> BulkRun {
    let size = p.size;
    let c = (size / 2) as i64;
    let s = size as isize;
    let mut colour = vec![0u8; size * size];
    if W::RANDOM_INIT {
        for (i, cell) in colour.iter_mut().enumerate() {
            let (gx, gy) = ((i % size) as i64, (i / size) as i64);
            *cell = walker.initial_cell(gx - c, gy - c);
        }
    }
    let mut reg = Region::new(size);
    let nbr: [isize; 4] = [-s, 1, s, -1];
    let mut last = vec![0u32; size * size];
    let (mut x, mut y, mut h) = (0i32, 0i32, 0u8);
    let mut idx = (c * size as i64 + c) as usize;
    reg.visit(idx);
    let mut t: u64 = 0;
    let escape = |x: i32, y: i32| (x.abs() as i64) >= c - 2 || (y.abs() as i64) >= c - 2;
    let empty = |status, t_star, area0, area_end| BulkRun {
        status,
        t_star,
        area0,
        area_end,
        mask_cells: 0,
        core_hist: [0; MAXC],
        fp: None,
        traj: None,
    };

    // Phase 1: grow to A0.
    while reg.area < p.a0 {
        if t >= p.max_steps {
            return empty(Status::NoA0, t, reg.area, reg.area);
        }
        last[idx] = (t + 1) as u32;
        walker.step(&mut colour[idx], &mut h);
        let (dx, dy) = DIRS[h as usize];
        x += dx;
        y += dy;
        idx = (idx as isize + dy as isize * s + dx as isize) as usize;
        t += 1;
        if reg.unv[idx] == 255 {
            reg.visit(idx);
        }
        if escape(x, y) {
            return empty(Status::Escaped, t, reg.area, reg.area);
        }
    }
    let (t_star, area0) = (t, reg.area);
    let (lo, hi) = (reg.lo, reg.hi);

    // Freeze the depth mask. depth[i] is the 4-neighbour distance to the nearest unvisited cell (a boundary cell is 1; 0 = unvisited at A0),
    // so the module-level "depth" (boundary = 0) is depth[i] - 1 and a step is bulk when depth[i] >= d0 + 1.
    let mut depth = vec![0u8; size * size];
    let mut queue: Vec<u32> = vec![];
    for gy in lo.1..=hi.1 {
        for gx in lo.0..=hi.0 {
            let i = gy * size + gx;
            if reg.unv[i] != 255 && reg.unv[i] > 0 {
                depth[i] = 1;
                queue.push(i as u32);
            }
        }
    }
    let mut head_q = 0;
    while head_q < queue.len() {
        let i = queue[head_q] as usize;
        head_q += 1;
        let d = depth[i];
        for dd in nbr {
            let j = (i as isize + dd) as usize;
            if reg.unv[j] != 255 && depth[j] == 0 {
                depth[j] = d.saturating_add(1);
                queue.push(j as u32);
            }
        }
    }
    let thresh = (p.d0 + 1).min(255) as u8;
    let is_bulk = |i: usize| depth[i] >= thresh;

    // Phase 2: record.
    let mut tr = Traj::default();
    let n = p.t_rec;
    tr.x.reserve(n);
    tr.y.reserve(n);
    tr.cell.reserve(n);
    tr.colour.reserve(n);
    tr.dh.reserve(n);
    tr.head.reserve(n);
    tr.bulk.reserve(n);
    tr.reuse.reserve(n);
    for _ in 0..n {
        let step_no = (t + 1) as u32;
        tr.x.push(x);
        tr.y.push(y);
        tr.cell.push(idx as u32);
        tr.colour.push(colour[idx]);
        tr.bulk.push(is_bulk(idx));
        tr.reuse.push(last[idx] != 0 && (step_no - last[idx]) as u64 <= REUSE_WIN);
        last[idx] = step_no;
        let h0 = h;
        walker.step(&mut colour[idx], &mut h);
        tr.dh.push((h + 4 - h0) & 3);
        tr.head.push(h);
        let (dx, dy) = DIRS[h as usize];
        x += dx;
        y += dy;
        idx = (idx as isize + dy as isize * s + dx as isize) as usize;
        t += 1;
        if reg.unv[idx] == 255 {
            reg.visit(idx);
        }
        if escape(x, y) {
            return empty(Status::Escaped, t_star, area0, reg.area);
        }
    }
    let mut core_hist = [0u64; MAXC];
    let mut mask_cells = 0u64;
    for gy in lo.1..=hi.1 {
        for gx in lo.0..=hi.0 {
            let i = gy * size + gx;
            if is_bulk(i) {
                mask_cells += 1;
                core_hist[colour[i] as usize] += 1;
            }
        }
    }
    let fp = fingerprint(&tr, size * size);
    BulkRun {
        status: Status::Ok,
        t_star,
        area0,
        area_end: reg.area,
        mask_cells,
        core_hist,
        fp: Some(fp),
        traj: if keep_traj { Some(tr) } else { None },
    }
}
