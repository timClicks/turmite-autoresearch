//! A leaner fast ant (frontier item 31).
//!
//! `fast::run` spends most of each step on bookkeeping that is not the ant: x/y coordinates, an
//! escape test, four min/max updates and an 8-byte trail write. Here the hot loop is only
//! "read cell, turn, write cell, move". Everything else is recovered afterwards:
//! - escape: the grid is ringed by a sentinel colour that the ant stops on (no per-step coordinate test);
//! - extent: each cell's byte carries a *touched* flag in bit 7 (colour in bits 0..7), scanned at the end;
//! - trail: the dynamics is exactly reversible, so the last `history` positions are rebuilt by
//!   stepping backwards from the final state (then stepping forward again to restore it).
//!
//! `run_lean` must return the same `RunResult` as `fast::run` (tests/lean.rs).

use crate::detect::{MIN_SPAN, exit_confirms, find_highway};
use crate::fast::{Config, RunResult, Stop};
use crate::{DIRS, Rule};

pub(crate) const SENT: u8 = 0x7F;
pub(crate) const TOUCHED: u8 = 0x80;

pub struct LeanGrid {
    /// Side of the inner (usable) square, as in `fast::Grid`.
    pub size: usize,
    stride: usize,
    cells: Vec<u8>,
}

impl LeanGrid {
    pub fn new(size: usize) -> LeanGrid {
        let stride = size + 2;
        let mut g = LeanGrid { size, stride, cells: vec![0; stride * stride] };
        g.clear();
        g
    }

    /// Byte (colour in bits 0..7, `TOUCHED` in bit 7) at coordinates relative to the start cell; `None` off the board.
    /// For tests and diagnostics; the stepping code never calls it.
    pub fn cell_byte(&self, x: i64, y: i64) -> Option<u8> {
        let c = (self.size / 2) as i64;
        let (gx, gy) = (x + c, y + c);
        let inside = gx >= 0 && gy >= 0 && gx < self.size as i64 && gy < self.size as i64;
        inside.then(|| self.cells[(gy as usize + 1) * self.stride + gx as usize + 1])
    }

    fn clear(&mut self) {
        let s = self.stride;
        self.cells.fill(0);
        for i in 0..s {
            self.cells[i] = SENT;
            self.cells[(s - 1) * s + i] = SENT;
            self.cells[i * s] = SENT;
            self.cells[i * s + s - 1] = SENT;
        }
    }
}

pub(crate) struct Tables {
    pub(crate) turn: [u8; 256],
    pub(crate) next: [u8; 256],
    pub(crate) n: usize,
    /// Fused transition, indexed by (heading << 8 | cell byte): (new heading, index delta). One dependent
    /// load instead of two on the critical path (turn lookup then delta lookup).
    pub(crate) fused: Vec<(u32, i32)>,
}

pub(crate) fn tables(rule: &Rule) -> Tables {
    let n = rule.len();
    assert!(n < 100, "lean ant supports fewer than 100 colours");
    let mut t = Tables { turn: [0; 256], next: [0; 256], n, fused: vec![] };
    for b in 0..128usize {
        let col = b & 127;
        if col < n {
            t.turn[b] = rule.0[col].delta();
            t.turn[b | 128] = t.turn[b];
            t.next[b] = (((col + 1) % n) as u8) | TOUCHED;
            t.next[b | 128] = t.next[b];
        }
    }
    t
}

/// The fused transition table for a grid of row stride `stride` (see `Tables::fused`).
pub(crate) fn fused_table(t: &Tables, stride: usize) -> Vec<(u32, i32)> {
    let didx: [isize; 4] = DIRS.map(|(dx, dy)| dy as isize * stride as isize + dx as isize);
    (0..1024usize)
        .map(|k| {
            let (h0, b) = (k >> 8, k & 255);
            let nh = (h0 + t.turn[b] as usize) & 3;
            (nh as u32, didx[nh] as i32)
        })
        .collect()
}

/// Run up to `k` steps from (idx, h). Returns (steps done, hit the sentinel).
#[inline(never)]
pub(crate) fn advance(cells: &mut [u8], t: &Tables, idx: &mut usize, h: &mut u8, k: u64) -> (u64, bool) {
    let (mut i, mut hh) = (*idx, *h);
    let mut done = 0u64;
    let mut hit = false;
    while done < k {
        // SAFETY: i always indexes a cell of the padded grid: the ring of SENT cells stops the ant
        // before it can step outside (the step onto the ring completes, the next read stops).
        let b = unsafe { *cells.get_unchecked(i) };
        if b == SENT {
            hit = true;
            break;
        }
        let (nh, delta) = unsafe { *t.fused.get_unchecked(((hh as usize) << 8) | b as usize) };
        unsafe { *cells.get_unchecked_mut(i) = *t.next.get_unchecked(b as usize) };
        hh = nh as u8;
        i = i.wrapping_add_signed(delta as isize);
        done += 1;
    }
    *idx = i;
    *h = hh;
    (done, hit)
}

/// Same contract as `fast::run`, on a fresh blank grid (the grid is cleared first).
pub fn run_lean(rule: &Rule, grid: &mut LeanGrid, cfg: &Config) -> RunResult {
    run_lean_ckpt(rule, grid, cfg, None)
}

/// As `run_lean`, but resumes from `ckpt.path` if it holds a state of this rule and board at or before `cfg.max_steps`,
/// saves every `ckpt.every` steps, and saves the final state of a run that stops at the budget (not an escape).
pub fn run_lean_ckpt(rule: &Rule, grid: &mut LeanGrid, cfg: &Config, ckpt: Option<&Ckpt>) -> RunResult {
    grid.clear();
    let mut t = tables(rule);
    let s = grid.stride;
    let didx: [isize; 4] = DIRS.map(|(dx, dy)| dy as isize * s as isize + dx as isize);
    t.fused = fused_table(&t, s);
    let c = grid.size / 2;
    let mut idx = (c + 1) * s + c + 1;
    let start = idx;
    let mut h = 0u8;
    let mut steps = 0u64;
    let mut stop = Stop::Budget;
    if let Some(ck) = ckpt {
        match load_ckpt(&ck.path, rule, grid) {
            Some((i, hh, s0)) if s0 <= cfg.max_steps => (idx, h, steps) = (i, hh, s0),
            _ => grid.clear(),
        }
    }
    while steps < cfg.max_steps {
        let k = ckpt.map_or(u64::MAX, |c| c.every.max(1)).min(cfg.max_steps - steps);
        let (d, hit) = advance(&mut grid.cells, &t, &mut idx, &mut h, k);
        steps += d;
        if hit {
            stop = Stop::Escaped;
            break;
        }
        if let Some(ck) = ckpt {
            save_ckpt(&ck.path, rule, grid, idx, h, steps).expect("checkpoint write failed");
        }
    }
    let pos_of = |i: usize| ((i % s) as i64 - 1 - c as i64, (i / s) as i64 - 1 - c as i64);
    let pos = pos_of(idx);

    // Trail: positions at times T-len+1..=T where T is the last in-grid time (steps-1 if escaped).
    let last_t = if stop == Stop::Escaped { steps - 1 } else { steps };
    let len = (cfg.history as u64).min(last_t + 1);
    let mut trail = vec![(0i32, 0i32); len as usize];
    let back = steps - (last_t + 1 - len); // steps to undo to reach the oldest retained position
    // undo `back` steps, recording positions on the way forward
    let mut undone = 0u64;
    let (mut ui, mut uh) = (idx, h);
    let mut hist_idx: Vec<usize> = Vec::with_capacity(back as usize + 1);
    hist_idx.push(ui);
    while undone < back {
        // reverse one step: move back, then undo the cell update and the turn
        ui = ui.wrapping_add_signed(-didx[uh as usize]);
        let b = grid.cells[ui];
        let col = (b & 127) as usize;
        let prev = (col + t.n - 1) % t.n;
        let pb = prev as u8 | TOUCHED;
        grid.cells[ui] = pb;
        uh = (uh + 4 - t.turn[pb as usize]) & 3;
        hist_idx.push(ui);
        undone += 1;
    }
    // hist_idx is newest-first: hist_idx[j] is the position at time steps - j.
    for (k, slot) in trail.iter_mut().enumerate() {
        // time of this entry: (last_t + 1 - len) + k; j = steps - time
        let time = last_t + 1 - len + k as u64;
        let j = (steps - time) as usize;
        let p = pos_of(hist_idx[j]);
        *slot = (p.0 as i32, p.1 as i32);
    }
    // restore the final state by stepping forward again
    let (mut ri, mut rh) = (ui, uh);
    advance(&mut grid.cells, &t, &mut ri, &mut rh, back);
    debug_assert_eq!((ri, rh), (idx, h));

    let (periodic_tail, highway) = classify_trail(&trail, cfg, stop, h);

    // Extent of touched cells (excluding the ring). The start cell is always touched.
    let (mut minx, mut miny, mut maxx, mut maxy) = (usize::MAX, usize::MAX, 0usize, 0usize);
    for y in 1..=grid.size {
        let row = &grid.cells[y * s + 1..y * s + 1 + grid.size];
        if let (Some(a), Some(b)) = (row.iter().position(|&b| b & TOUCHED != 0), row.iter().rposition(|&b| b & TOUCHED != 0)) {
            minx = minx.min(a);
            maxx = maxx.max(b);
            miny = miny.min(y - 1);
            maxy = maxy.max(y - 1);
        }
    }
    // The start cell and (if the run did not escape) the final cell are touched by arrival, not by a write.
    let last = (stop == Stop::Budget).then(|| ((idx % s).wrapping_sub(1), (idx / s).wrapping_sub(1)));
    let extent = finish_extent((minx, miny, maxx, maxy), ((start % s) - 1, (start / s) - 1), last);
    RunResult {
        steps,
        stop,
        pos: (pos.0 as i32, pos.1 as i32),
        heading: h,
        highway,
        periodic_tail,
        extent,
    }
}

/// Highway verdict from the rebuilt trail; shared with the tiled backend so detection cannot diverge.
pub(crate) fn classify_trail(
    trail: &[(i32, i32)],
    cfg: &Config,
    stop: Stop,
    h: u8,
) -> (Option<crate::detect::Highway>, Option<crate::detect::Highway>) {
    let periodic_tail = find_highway(trail, cfg.max_period, MIN_SPAN);
    let highway = if stop == Stop::Escaped {
        periodic_tail.or_else(|| find_highway(trail, cfg.max_period, 2_000)).filter(|&hw| exit_confirms(hw, h))
    } else {
        None
    };
    (periodic_tail, highway)
}

/// Extent from the touched-cell bounding box `(minx, miny, maxx, maxy)` (inner-board coordinates; `usize::MAX`/0 when
/// empty), the start cell, and the final cell of a run that stopped at its budget. Moved verbatim from the inline code.
/// When a budget ends exactly on the step onto the ring the "final cell" is a ring cell and the result is wrong (width 0
/// or one too large). That quirk is pinned by tests/tiled.rs and deliberately not fixed here: it would change CSVs.
pub(crate) fn finish_extent(bbox: (usize, usize, usize, usize), start: (usize, usize), last: Option<(usize, usize)>) -> (u32, u32) {
    let (mut minx, mut miny, mut maxx, mut maxy) = bbox;
    for (ex, ey) in std::iter::once(start).chain(last) {
        minx = minx.min(ex);
        maxx = if minx == usize::MAX { ex } else { maxx.max(ex) };
        miny = miny.min(ey);
        maxy = maxy.max(ey);
    }
    (maxx.wrapping_sub(minx).wrapping_add(1) as u32, maxy.wrapping_sub(miny).wrapping_add(1) as u32)
}

/// As `fast::highway_onset` (first step s after which pos[t] - pos[t-p] == d for all t >= s + p), but on a flat grid
/// instead of a HashMap: the HashMap replay needs memory proportional to every cell ever written and took >10 GB for
/// runs of billions of steps. `size` must be at least the grid the original run used (the replay stays inside it).
pub fn highway_onset_flat(rule: &Rule, hw: crate::detect::Highway, until: u64, size: usize) -> u64 {
    let n = rule.len();
    let p = hw.period as usize;
    let t = tables(rule);
    let s = size + 2;
    let mut cells = vec![0u8; s * s];
    let c = size / 2;
    let (mut x, mut y) = ((c + 1) as i64, (c + 1) as i64);
    let mut ring = vec![(0i32, 0i32); p];
    let mut h = 0u8;
    let mut last_bad: u64 = 0;
    for step in 1..=until {
        let idx = y as usize * s + x as usize;
        let b = cells[idx] & 127;
        h = (h + t.turn[b as usize]) & 3;
        cells[idx] = (((b as usize + 1) % n) as u8) | TOUCHED;
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        let pos = ((x - 1 - c as i64) as i32, (y - 1 - c as i64) as i32);
        let slot = (step as usize) % p;
        let prev = ring[slot];
        ring[slot] = pos;
        if step < p as u64 || (pos.0 - prev.0, pos.1 - prev.1) != (hw.dx, hw.dy) {
            last_bad = step;
        }
        if x < 1 || y < 1 || x >= s as i64 - 1 || y >= s as i64 - 1 {
            break; // left the grid (only possible on the final step of an escaped run)
        }
    }
    (last_bad + 1).saturating_sub(p as u64)
}

/// Mid-trajectory checkpointing for `run_lean_ckpt`. The ant is deterministic, so a run resumed from a checkpoint is
/// step-for-step the run that was never interrupted (tests/lean_ckpt.rs), and a checkpoint written at the budget lets a
/// later call with a larger `max_steps` extend the run instead of restarting it.
pub struct Ckpt {
    pub path: std::path::PathBuf,
    /// Steps between saves.
    pub every: u64,
}

const MAGIC: &[u8; 4] = b"TCK1";

fn save_ckpt(path: &std::path::Path, rule: &Rule, grid: &LeanGrid, idx: usize, h: u8, steps: u64) -> std::io::Result<()> {
    use std::io::Write;
    let tmp = path.with_extension("tmp");
    let mut w = std::io::BufWriter::new(std::fs::File::create(&tmp)?);
    let name = rule.to_string();
    w.write_all(MAGIC)?;
    w.write_all(&(name.len() as u32).to_le_bytes())?;
    w.write_all(name.as_bytes())?;
    for v in [grid.size as u64, steps, idx as u64] {
        w.write_all(&v.to_le_bytes())?;
    }
    w.write_all(&[h])?;
    // Run-length coding of zero bytes: (zeros, literal length, literal bytes)*, the blob is sparse in the board.
    let c = &grid.cells;
    let mut i = 0;
    while i < c.len() {
        let z = c[i..].iter().position(|&b| b != 0).unwrap_or(c.len() - i);
        i += z;
        let l = c[i..].iter().position(|&b| b == 0).unwrap_or(c.len() - i);
        w.write_all(&(z as u64).to_le_bytes())?;
        w.write_all(&(l as u64).to_le_bytes())?;
        w.write_all(&c[i..i + l])?;
        i += l;
    }
    w.flush()?;
    w.into_inner().map_err(|e| e.into_error())?.sync_all()?;
    std::fs::rename(&tmp, path) // atomic: a kill mid-save leaves the previous checkpoint intact
}

/// Loads into `grid`; None (grid untouched or cleared) if the file is absent, damaged or for another rule/board.
fn load_ckpt(path: &std::path::Path, rule: &Rule, grid: &mut LeanGrid) -> Option<(usize, u8, u64)> {
    let b = std::fs::read(path).ok()?;
    let u64_at = |o: usize| b.get(o..o + 8).map(|s| u64::from_le_bytes(s.try_into().unwrap()));
    if b.get(..4)? != MAGIC {
        return None;
    }
    let nl = u32::from_le_bytes(b.get(4..8)?.try_into().unwrap()) as usize;
    if b.get(8..8 + nl)? != rule.to_string().as_bytes() {
        return None;
    }
    let o = 8 + nl;
    let (size, steps, idx) = (u64_at(o)?, u64_at(o + 8)?, u64_at(o + 16)?);
    let h = *b.get(o + 24)?;
    if size as usize != grid.size {
        return None;
    }
    let mut cells = vec![0u8; grid.cells.len()];
    let (mut p, mut i) = (o + 25, 0usize);
    while p < b.len() {
        let (z, l) = (u64_at(p)? as usize, u64_at(p + 8)? as usize);
        p += 16;
        i += z;
        cells.get_mut(i..i + l)?.copy_from_slice(b.get(p..p + l)?);
        p += l;
        i += l;
    }
    grid.cells = cells;
    Some((idx as usize, h, steps))
}
