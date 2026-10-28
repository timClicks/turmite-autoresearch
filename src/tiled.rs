//! A tile-based CPU grid for the lean ant: sparse allocation, a bounded cache of uncompressed tiles and, optionally,
//! bit-packed storage for the tiles that are not being stepped on. Design, memory accounting and the checkpoint format:
//! `experiments/active/2026-10-tiled-grid-backend/README.md`.
//!
//! The board is the same bounded `size x size` square as `lean::LeanGrid` (start cell at the centre, escape = leaving it),
//! cut into `T x T` tiles (T a power of two) aligned to the *relative* coordinates (tile `x.div_euclid(T)`), so about half
//! the tiles have negative indices. A resident tile is a `(T+2) x (T+2)` byte array: the `T x T` cells plus a one-cell halo,
//! with the lean byte encoding (colour in bits 0..7, `TOUCHED` in bit 7). The halo and every interior cell outside the
//! board hold the `SENT` sentinel, so lean's inner loop (`lean::advance`) runs unchanged inside a tile and stops exactly when
//! the ant steps onto a cell that is not this tile's: no per-step coordinate test. The halo never holds data and is never
//! written, so each cell has exactly one authoritative copy: the resident tile if there is one, else the inactive payload.
//! Inactive tiles are `Raw` (T*T bytes) or `Packed` (`ceil(log2 n)` colour bits plus one touched bit per cell); an
//! all-blank tile is dropped, because "absent" is the blank background. `Cell colour 0` is *not* "unvisited": the touched
//! bit is stored explicitly.
//!
//! Simulation output depends on neither tile size nor cache size (tests/tiled.rs); only the stats do.

use crate::fast::{Config, RunResult, Stop};
use crate::lean::{Ckpt, SENT, TOUCHED, Tables, advance, classify_trail, finish_extent, fused_table, tables};
use crate::walkers::mix64;
use crate::{DIRS, Rule};
use std::collections::HashMap;
use std::hash::{BuildHasherDefault, Hasher};

pub const MIN_TILE_LOG2: u32 = 2;
pub const MAX_TILE_LOG2: u32 = 12;
/// The ant needs its current tile and, to avoid thrashing at a tile edge, the previous one.
pub const MIN_CACHE_TILES: usize = 2;
/// Tile coordinates must fit an i32 each (`key`).
pub const MAX_BOARD: usize = 1 << 30;
/// Bytes of idle tile buffers (and directory capacity) a reused grid keeps across `begin`; a bigger footprint is released.
const RETAIN_BYTES: usize = 8 << 20;
const NIL: u32 = u32::MAX;
/// Checkpoint format version (the file also starts with the magic `TTK1`).
pub const CKPT_VERSION: u32 = 1;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TileError {
    BadConfig(String),
    /// A tile payload or checkpoint is damaged (truncated, bad checksum, colour out of range, ...).
    Corrupt(String),
    /// A well-formed checkpoint for a different rule, board or tile size.
    Incompatible(String),
    Io(String),
}

impl std::fmt::Display for TileError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            TileError::BadConfig(s) => write!(f, "bad tiled-grid configuration: {s}"),
            TileError::Corrupt(s) => write!(f, "corrupt tiled data: {s}"),
            TileError::Incompatible(s) => write!(f, "incompatible checkpoint: {s}"),
            TileError::Io(s) => write!(f, "i/o error: {s}"),
        }
    }
}

impl std::error::Error for TileError {}

/// How a tile that is not resident is stored.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Inactive {
    /// `T*T` bytes, the resident encoding without the halo.
    Raw,
    /// Fixed-width bit-packed (falls back to `Raw` when that would not be smaller, i.e. for 65 or more colours).
    Packed,
    /// As `Packed`, then an LZ4 block (lz4_flex, safe mode) of that canonical payload when the block is smaller; otherwise the
    /// packed or raw payload. Compression happens once per eviction, never while a tile is resident.
    Compressed,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct TileConfig {
    pub tile_log2: u32,
    /// Maximum resident (uncompressed) tiles; `None` keeps every tile resident (sparse allocation only, nothing is ever evicted).
    pub cache_tiles: Option<usize>,
    pub inactive: Inactive,
}

impl Default for TileConfig {
    fn default() -> TileConfig {
        TileConfig { tile_log2: 6, cache_tiles: None, inactive: Inactive::Raw }
    }
}

/// Counters for one run (reset by `TiledGrid::begin`). They describe cost, never the simulation.
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct TileStats {
    /// Tile changes by the ant (plus those of the trail reversal and replay).
    pub transitions: u64,
    /// Transition into a tile that was already resident.
    pub hits: u64,
    /// Transition into a tile that had to be decoded from its inactive payload.
    pub misses: u64,
    /// Transition into a tile that did not exist (blank background).
    pub creations: u64,
    /// Resident tiles pushed out to make room. Every evicted tile was entered by the stepper, which writes the cell it
    /// enters, so every eviction is of a dirty tile: there is no clean-eviction shortcut to count.
    pub evictions: u64,
    /// Evictions of a tile that held only blank background and was dropped instead of stored.
    pub blank_drops: u64,
    pub packed_stores: u64,
    pub raw_stores: u64,
    pub compressed_stores: u64,
    /// Payload bytes produced by evictions / consumed by misses.
    pub bytes_encoded: u64,
    pub bytes_decoded: u64,
    pub peak_resident_tiles: usize,
    pub peak_inactive_bytes: usize,
    /// Peak of resident buffers + inactive payload + directory and cache metadata estimates.
    pub peak_total_bytes: usize,
}

/// Logical bytes held by the grid right now (allocator overhead and OS paging are not included: compare with peak RSS).
#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct MemoryReport {
    pub tiles_total: usize,
    pub tiles_resident: usize,
    pub tiles_packed: usize,
    pub tiles_raw_inactive: usize,
    pub tiles_compressed: usize,
    /// Allocated resident buffers, `(T+2)^2` bytes each, including free-listed ones.
    pub resident_bytes: usize,
    pub packed_bytes: usize,
    pub raw_inactive_bytes: usize,
    pub compressed_bytes: usize,
    /// Estimate: hash-table capacity times (key + slot + control byte).
    pub directory_bytes: usize,
    /// Pool bookkeeping (tick, key, free list, scratch).
    pub cache_meta_bytes: usize,
}

impl MemoryReport {
    pub fn inactive_bytes(&self) -> usize {
        self.packed_bytes + self.raw_inactive_bytes + self.compressed_bytes
    }
    pub fn total_bytes(&self) -> usize {
        self.resident_bytes + self.inactive_bytes() + self.directory_bytes + self.cache_meta_bytes
    }
}

#[derive(Default)]
struct DetHasher(u64);

impl Hasher for DetHasher {
    fn finish(&self) -> u64 {
        mix64(self.0)
    }
    fn write(&mut self, bytes: &[u8]) {
        for &b in bytes {
            self.0 = (self.0.rotate_left(8) ^ b as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15);
        }
    }
    fn write_u64(&mut self, i: u64) {
        self.0 = i;
    }
}

enum Slot {
    Resident(u32),
    Raw(Box<[u8]>),
    Packed(Box<[u8]>),
    /// LZ4 block of the canonical payload (`canonical_len` bytes once expanded).
    Lz4(Box<[u8]>),
}

struct Pooled {
    key: u64,
    cells: Box<[u8]>,
    live: bool,
}

/// Valid (on-board) interior cells of a tile: local columns `x0..x1`, rows `y0..y1`.
#[derive(Clone, Copy, Debug)]
struct Rect {
    x0: usize,
    x1: usize,
    y0: usize,
    y1: usize,
}

impl Rect {
    fn contains(&self, lx: usize, ly: usize) -> bool {
        lx >= self.x0 && lx < self.x1 && ly >= self.y0 && ly < self.y1
    }
}

fn key(tx: i64, ty: i64) -> u64 {
    ((tx as i32 as u32 as u64) << 32) | ty as i32 as u32 as u64
}

fn unkey(k: u64) -> (i64, i64) {
    ((k >> 32) as u32 as i32 as i64, k as u32 as i32 as i64)
}

/// Bits per colour for a rule with `n` colours (0 for the one-colour rule).
pub fn colour_width(n: usize) -> u32 {
    usize::BITS - n.saturating_sub(1).leading_zeros()
}

fn colour_plane_len(t: usize, w: u32) -> usize {
    (t * t * w as usize).div_ceil(8)
}

/// Bytes of a packed tile: the colour plane followed by one touched bit per cell.
pub fn packed_len(t: usize, w: u32) -> usize {
    colour_plane_len(t, w) + t * t / 8
}

/// Pack the `t x t` cells at `src[base + ly*stride + lx]` (lean encoding) that lie in `rect`; others are stored as blank.
/// Layout, little-endian bit order: cell `i = ly*t + lx` has its colour in bits `[i*w, (i+1)*w)` of the colour plane
/// and its touched flag in bit `i` of the touched plane that follows.
fn encode(src: &[u8], stride: usize, base: usize, t: usize, w: u32, rect: Rect, out: &mut Vec<u8>) {
    let clen = colour_plane_len(t, w);
    out.clear();
    out.resize(clen + t * t / 8, 0);
    let mut i = 0usize;
    for ly in 0..t {
        for lx in 0..t {
            let b = if rect.contains(lx, ly) { src[base + ly * stride + lx] } else { 0 };
            if w > 0 {
                let col = (b & 127) as u32;
                debug_assert!(col < 1 << w);
                let bit = i * w as usize;
                let (byte, sh) = (bit >> 3, (bit & 7) as u32);
                let v = col << sh;
                out[byte] |= v as u8;
                if sh + w > 8 {
                    out[byte + 1] |= (v >> 8) as u8;
                }
            }
            out[clen + (i >> 3)] |= (b >> 7) << (i & 7);
            i += 1;
        }
    }
}

/// Inverse of `encode`, writing the lean encoding (and `SENT` outside `rect`). Rejects a wrong length, a colour `>= n`
/// and any non-blank cell outside `rect`.
fn decode(payload: &[u8], dst: &mut [u8], stride: usize, base: usize, t: usize, w: u32, n: usize, rect: Rect) -> Result<(), TileError> {
    let clen = colour_plane_len(t, w);
    if payload.len() != clen + t * t / 8 {
        return Err(TileError::Corrupt(format!("packed tile has {} bytes, expected {}", payload.len(), clen + t * t / 8)));
    }
    let mask = (1u32 << w) - 1;
    let mut i = 0usize;
    for ly in 0..t {
        for lx in 0..t {
            let col = if w > 0 {
                let bit = i * w as usize;
                let (byte, sh) = (bit >> 3, bit & 7);
                let v = payload[byte] as u32 | (payload.get(byte + 1).copied().unwrap_or(0) as u32) << 8;
                (v >> sh) & mask
            } else {
                0
            };
            let touched = (payload[clen + (i >> 3)] >> (i & 7)) & 1;
            let o = base + ly * stride + lx;
            if rect.contains(lx, ly) {
                if col as usize >= n {
                    return Err(TileError::Corrupt(format!("colour {col} out of range for {n} colours")));
                }
                dst[o] = col as u8 | touched << 7;
            } else {
                if col != 0 || touched != 0 {
                    return Err(TileError::Corrupt("off-board cell is not blank".into()));
                }
                dst[o] = SENT;
            }
            i += 1;
        }
    }
    Ok(())
}

fn store_raw(src: &[u8], stride: usize, base: usize, t: usize, rect: Rect, out: &mut Vec<u8>) {
    out.clear();
    out.resize(t * t, 0);
    for ly in rect.y0..rect.y1 {
        let s = base + ly * stride;
        out[ly * t + rect.x0..ly * t + rect.x1].copy_from_slice(&src[s + rect.x0..s + rect.x1]);
    }
}

fn load_raw(payload: &[u8], dst: &mut [u8], stride: usize, base: usize, t: usize, n: usize, rect: Rect) -> Result<(), TileError> {
    if payload.len() != t * t {
        return Err(TileError::Corrupt(format!("raw tile has {} bytes, expected {}", payload.len(), t * t)));
    }
    for ly in 0..t {
        for lx in 0..t {
            let b = payload[ly * t + lx];
            let o = base + ly * stride + lx;
            if rect.contains(lx, ly) {
                if (b & 127) as usize >= n {
                    return Err(TileError::Corrupt(format!("colour {} out of range for {n} colours", b & 127)));
                }
                dst[o] = b;
            } else {
                if b != 0 {
                    return Err(TileError::Corrupt("off-board cell is not blank".into()));
                }
                dst[o] = SENT;
            }
        }
    }
    Ok(())
}

/// Bytes of the canonical inactive payload: packed when that is smaller than raw, else raw.
fn canonical_len(t: usize, w: u32) -> usize {
    packed_len(t, w).min(t * t)
}

/// Expand an LZ4 block that must yield exactly `len` bytes.
fn expand(block: &[u8], len: usize, out: &mut Vec<u8>) -> Result<(), TileError> {
    out.clear();
    out.resize(len, 0);
    match lz4_flex::block::decompress_into(block, out) {
        Ok(n) if n == len => Ok(()),
        Ok(n) => Err(TileError::Corrupt(format!("lz4 block expands to {n} bytes, expected {len}"))),
        Err(e) => Err(TileError::Corrupt(format!("lz4 block: {e}"))),
    }
}

/// Pack a full `t x t` array of lean-encoded cells (all on board): the codec on its own, for tests and benchmarks.
pub fn pack_cells(cells: &[u8], t: usize, w: u32) -> Vec<u8> {
    assert_eq!(cells.len(), t * t);
    let mut out = vec![];
    encode(cells, t, 0, t, w, Rect { x0: 0, x1: t, y0: 0, y1: t }, &mut out);
    out
}

/// Inverse of `pack_cells` for a rule with `n` colours.
pub fn unpack_cells(payload: &[u8], t: usize, w: u32, n: usize) -> Result<Vec<u8>, TileError> {
    let mut out = vec![0u8; t * t];
    decode(payload, &mut out, t, 0, t, w, n, Rect { x0: 0, x1: t, y0: 0, y1: t })?;
    Ok(out)
}

pub struct TiledGrid {
    /// Side of the board, as in `lean::LeanGrid`.
    pub size: usize,
    cfg: TileConfig,
    t: usize,
    stride: usize,
    lo: i64,
    hi: i64,
    dir: HashMap<u64, Slot, BuildHasherDefault<DetHasher>>,
    pool: Vec<Pooled>,
    /// Recency list of live buffers (doubly linked through pool indices): `head` is the newest, `tail` the LRU victim.
    prev: Vec<u32>,
    next: Vec<u32>,
    head: u32,
    tail: u32,
    free: Vec<u32>,
    cur: u32,
    idx: usize,
    h: u8,
    n: usize,
    w: u32,
    stats: TileStats,
    inactive_bytes: usize,
    scratch: Vec<u8>,
}

impl TiledGrid {
    pub fn new(size: usize, cfg: TileConfig) -> Result<TiledGrid, TileError> {
        if size == 0 || size > MAX_BOARD {
            return Err(TileError::BadConfig(format!("board side {size} outside 1..={MAX_BOARD}")));
        }
        if !(MIN_TILE_LOG2..=MAX_TILE_LOG2).contains(&cfg.tile_log2) {
            return Err(TileError::BadConfig(format!("tile_log2 {} outside {MIN_TILE_LOG2}..={MAX_TILE_LOG2}", cfg.tile_log2)));
        }
        if let Some(c) = cfg.cache_tiles
            && c < MIN_CACHE_TILES {
                return Err(TileError::BadConfig(format!("cache of {c} tiles is below the minimum {MIN_CACHE_TILES}")));
            }
        let t = 1usize << cfg.tile_log2;
        let c = (size / 2) as i64;
        Ok(TiledGrid {
            size,
            cfg,
            t,
            stride: t + 2,
            lo: -c,
            hi: size as i64 - c,
            dir: HashMap::default(),
            pool: vec![],
            prev: vec![],
            next: vec![],
            head: NIL,
            tail: NIL,
            free: vec![],
            cur: u32::MAX,
            idx: 0,
            h: 0,
            n: 0,
            w: 0,
            stats: TileStats::default(),
            inactive_bytes: 0,
            scratch: vec![],
        })
    }

    pub fn config(&self) -> TileConfig {
        self.cfg
    }

    pub fn stats(&self) -> &TileStats {
        &self.stats
    }

    /// Forget every tile and prepare for `rule`. Up to `RETAIN_BYTES` of buffers are kept for reuse (at least two); the rest and an
    /// oversized directory are released, so a worker does not hold the high-water mark of the biggest rule it has run. Nothing from
    /// the previous run survives: each buffer is fully re-initialised when it is next handed out.
    pub fn begin(&mut self, rule: &Rule) {
        let n = rule.len();
        assert!(n < 100, "tiled ant supports fewer than 100 colours");
        self.dir.clear();
        if self.dir.capacity() * (std::mem::size_of::<(u64, Slot)>() + 1) > RETAIN_BYTES {
            self.dir = HashMap::default();
        }
        let keep = (RETAIN_BYTES / (self.stride * self.stride)).max(2);
        if self.pool.len() > keep {
            self.pool.truncate(keep);
            self.pool.shrink_to_fit();
        }
        self.prev.clear();
        self.prev.resize(self.pool.len(), NIL);
        self.next.clear();
        self.next.resize(self.pool.len(), NIL);
        self.head = NIL;
        self.tail = NIL;
        self.free.clear();
        for (i, p) in self.pool.iter_mut().enumerate() {
            p.live = false;
            self.free.push(i as u32);
        }
        self.free.reverse(); // hand out low indices first
        self.cur = u32::MAX;
        self.idx = 0;
        self.h = 0;
        self.n = n;
        self.w = colour_width(n);
        self.stats = TileStats::default();
        self.inactive_bytes = 0;
    }

    pub fn memory(&self) -> MemoryReport {
        let mut m = MemoryReport::default();
        for s in self.dir.values() {
            m.tiles_total += 1;
            match s {
                Slot::Resident(_) => m.tiles_resident += 1,
                Slot::Packed(b) => {
                    m.tiles_packed += 1;
                    m.packed_bytes += b.len();
                }
                Slot::Raw(b) => {
                    m.tiles_raw_inactive += 1;
                    m.raw_inactive_bytes += b.len();
                }
                Slot::Lz4(b) => {
                    m.tiles_compressed += 1;
                    m.compressed_bytes += b.len();
                }
            }
        }
        m.resident_bytes = self.pool.len() * self.stride * self.stride;
        m.directory_bytes = self.dir.capacity() * (std::mem::size_of::<(u64, Slot)>() + 1);
        m.cache_meta_bytes = self.pool.len() * (std::mem::size_of::<Pooled>() + 8 + 4) + self.scratch.capacity();
        m
    }

    fn rect(&self, tx: i64, ty: i64) -> Rect {
        let t = self.t as i64;
        let span = |o: i64| ((self.lo - o).clamp(0, t) as usize, (self.hi - o).clamp(0, t) as usize);
        let (x0, x1) = span(tx * t);
        let (y0, y1) = span(ty * t);
        Rect { x0, x1, y0, y1 }
    }

    fn note_peaks(&mut self) {
        let live = self.pool.len() - self.free.len();
        self.stats.peak_resident_tiles = self.stats.peak_resident_tiles.max(live);
        self.stats.peak_inactive_bytes = self.stats.peak_inactive_bytes.max(self.inactive_bytes);
        let total = self.pool.len() * self.stride * self.stride
            + self.inactive_bytes
            + self.dir.capacity() * (std::mem::size_of::<(u64, Slot)>() + 1)
            + self.pool.len() * (std::mem::size_of::<Pooled>() + 12);
        self.stats.peak_total_bytes = self.stats.peak_total_bytes.max(total);
    }

    fn unlink(&mut self, i: u32) {
        let (p, n) = (self.prev[i as usize], self.next[i as usize]);
        if p == NIL { self.head = n } else { self.next[p as usize] = n }
        if n == NIL { self.tail = p } else { self.prev[n as usize] = p }
        self.prev[i as usize] = NIL;
        self.next[i as usize] = NIL;
    }

    fn push_front(&mut self, i: u32) {
        self.prev[i as usize] = NIL;
        self.next[i as usize] = self.head;
        if self.head == NIL { self.tail = i } else { self.prev[self.head as usize] = i }
        self.head = i;
    }

    /// Store the resident tile `pi` as inactive (or drop it if blank) and release its buffer.
    fn evict(&mut self, pi: u32) {
        let p = &self.pool[pi as usize];
        let (tx, ty) = unkey(p.key);
        let (t, stride, base) = (self.t, self.stride, self.stride + 1);
        let rect = self.rect(tx, ty);
        let blank = (rect.y0..rect.y1).all(|ly| {
            let s = base + ly * stride;
            p.cells[s + rect.x0..s + rect.x1].iter().all(|&b| b == 0)
        });
        if blank {
            self.dir.remove(&p.key);
            self.stats.blank_drops += 1;
        } else {
            let mut buf = std::mem::take(&mut self.scratch);
            let pack = self.cfg.inactive != Inactive::Raw && packed_len(t, self.w) < t * t;
            if pack {
                encode(&p.cells, stride, base, t, self.w, rect, &mut buf);
            } else {
                store_raw(&p.cells, stride, base, t, rect, &mut buf);
            }
            self.stats.bytes_encoded += buf.len() as u64;
            self.inactive_bytes += buf.len();
            let lz4 = (self.cfg.inactive == Inactive::Compressed).then(|| lz4_flex::compress(&buf)).filter(|c| c.len() < buf.len());
            if let Some(c) = lz4 {
                self.inactive_bytes = self.inactive_bytes - buf.len() + c.len();
                self.dir.insert(p.key, Slot::Lz4(c.into_boxed_slice()));
                self.stats.compressed_stores += 1;
                self.scratch = buf;
                self.pool[pi as usize].live = false;
                self.unlink(pi);
                return;
            }
            let payload: Box<[u8]> = buf.as_slice().into();
            self.dir.insert(p.key, if pack { Slot::Packed(payload) } else { Slot::Raw(payload) });
            if pack {
                self.stats.packed_stores += 1;
            } else {
                self.stats.raw_stores += 1;
            }
            self.scratch = buf;
        }
        self.pool[pi as usize].live = false;
        self.unlink(pi);
    }

    /// A buffer for a tile about to become resident: free-listed, newly allocated, or the least recently used tile's.
    fn acquire(&mut self) -> u32 {
        if let Some(i) = self.free.pop() {
            return i;
        }
        if self.cfg.cache_tiles.is_none_or(|cap| self.pool.len() < cap) {
            self.pool.push(Pooled { key: 0, cells: vec![SENT; self.stride * self.stride].into_boxed_slice(), live: false });
            self.prev.push(NIL);
            self.next.push(NIL);
            return (self.pool.len() - 1) as u32;
        }
        // Deterministic LRU: the list tail is the least recently entered tile. The current tile is the head, so with at least
        // two live tiles it is never chosen.
        let victim = self.tail;
        assert!(victim != NIL && victim != self.cur, "cache holds at least two live tiles");
        self.evict(victim);
        self.stats.evictions += 1;
        victim
    }

    /// Make tile `k` resident (creating or decoding it) and return its pool index. `k` must not be resident.
    fn load(&mut self, k: u64) -> u32 {
        let (tx, ty) = unkey(k);
        let slot = self.dir.remove(&k);
        let pi = self.acquire();
        let (t, stride, base, n, w) = (self.t, self.stride, self.stride + 1, self.n, self.w);
        let rect = self.rect(tx, ty);
        let buf = &mut self.pool[pi as usize].cells;
        match slot {
            None => {
                buf.fill(SENT);
                for ly in rect.y0..rect.y1 {
                    let s = base + ly * stride;
                    buf[s + rect.x0..s + rect.x1].fill(0);
                }
                self.stats.creations += 1;
            }
            Some(Slot::Raw(b)) => {
                load_raw(&b, buf, stride, base, t, n, rect).expect("inactive raw tile is internally consistent");
                self.inactive_bytes -= b.len();
                self.stats.bytes_decoded += b.len() as u64;
                self.stats.misses += 1;
            }
            Some(Slot::Packed(b)) => {
                decode(&b, buf, stride, base, t, w, n, rect).expect("inactive packed tile is internally consistent");
                self.inactive_bytes -= b.len();
                self.stats.bytes_decoded += b.len() as u64;
                self.stats.misses += 1;
            }
            Some(Slot::Lz4(b)) => {
                let mut tmp = std::mem::take(&mut self.scratch);
                expand(&b, canonical_len(t, w), &mut tmp).expect("inactive lz4 tile is internally consistent");
                if packed_len(t, w) < t * t {
                    decode(&tmp, buf, stride, base, t, w, n, rect)
                } else {
                    load_raw(&tmp, buf, stride, base, t, n, rect)
                }
                .expect("inactive lz4 tile is internally consistent");
                self.scratch = tmp;
                self.inactive_bytes -= b.len();
                self.stats.bytes_decoded += b.len() as u64;
                self.stats.misses += 1;
            }
            Some(Slot::Resident(_)) => unreachable!("load of a resident tile"),
        }
        let p = &mut self.pool[pi as usize];
        p.key = k;
        p.live = true;
        self.dir.insert(k, Slot::Resident(pi));
        self.note_peaks();
        pi
    }

    /// Point the cursor at cell `(x, y)` (relative coordinates), switching tile if needed. `(x, y)` may lie off the board
    /// (a ring position of a finished run): the tile is then created blank.
    fn enter(&mut self, x: i64, y: i64) {
        let t = self.t as i64;
        let (tx, ty) = (x.div_euclid(t), y.div_euclid(t));
        let k = key(tx, ty);
        self.stats.transitions += 1;
        let pi = match self.dir.get(&k) {
            Some(Slot::Resident(i)) => {
                self.stats.hits += 1;
                let i = *i;
                if self.head != i {
                    self.unlink(i);
                    self.push_front(i);
                }
                i
            }
            _ => {
                let i = self.load(k);
                self.push_front(i);
                i
            }
        };
        self.cur = pi;
        let (lx, ly) = ((x - tx * t) as usize, (y - ty * t) as usize);
        self.idx = (ly + 1) * self.stride + lx + 1;
    }

    /// Cursor position in relative coordinates (may be a halo or ring cell).
    fn position(&self) -> (i64, i64) {
        let (tx, ty) = unkey(self.pool[self.cur as usize].key);
        let t = self.t as i64;
        (tx * t + (self.idx % self.stride) as i64 - 1, ty * t + (self.idx / self.stride) as i64 - 1)
    }

    /// After the inner loop stopped: if the cursor sits on a halo cell that is on the board, move to the owning tile.
    /// Returns whether the cursor is off the board (a ring cell).
    fn settle(&mut self) -> bool {
        let (x, y) = self.position();
        if x < self.lo || x >= self.hi || y < self.lo || y >= self.hi {
            return true;
        }
        let (lx, ly) = (self.idx % self.stride, self.idx / self.stride);
        if !(1..=self.t).contains(&lx) || !(1..=self.t).contains(&ly) {
            self.enter(x, y);
        }
        false
    }

    /// Run up to `k` steps from the cursor, crossing tiles. Returns (steps done, left the board).
    fn advance_steps(&mut self, tb: &Tables, k: u64) -> (u64, bool) {
        let mut done = 0u64;
        while done < k {
            let (d, hit) = advance(&mut self.pool[self.cur as usize].cells, tb, &mut self.idx, &mut self.h, k - done);
            done += d;
            if self.settle() {
                return (done, hit);
            }
        }
        (done, false)
    }

    /// Put the cursor on `(x, y)`, which must be on the board.
    fn goto(&mut self, x: i64, y: i64) {
        let t = self.t as i64;
        let (tx, ty) = unkey(self.pool[self.cur as usize].key);
        let (lx, ly) = (x - tx * t, y - ty * t);
        if (0..t).contains(&lx) && (0..t).contains(&ly) {
            self.idx = (ly as usize + 1) * self.stride + lx as usize + 1;
        } else {
            self.enter(x, y);
        }
    }

    /// Undo `back` steps from the cursor with the same arithmetic as lean's reversal, returning the positions
    /// newest-first (`out[j]` is the position `j` steps before the start). The cursor is left at the undone state.
    fn reverse(&mut self, tb: &Tables, back: u64) -> Vec<(i64, i64)> {
        let (mut x, mut y) = self.position();
        let mut h = self.h;
        let mut hist = Vec::with_capacity(back as usize + 1);
        hist.push((x, y));
        for _ in 0..back {
            let (dx, dy) = DIRS[h as usize];
            x -= dx as i64;
            y -= dy as i64;
            self.goto(x, y);
            let cell = &mut self.pool[self.cur as usize].cells[self.idx];
            let col = (*cell & 127) as usize;
            let prev = (col + tb.n - 1) % tb.n;
            let pb = prev as u8 | TOUCHED;
            *cell = pb;
            h = (h + 4 - tb.turn[pb as usize]) & 3;
            hist.push((x, y));
        }
        self.h = h;
        hist
    }

    /// Bytes of tile `slot` for reading: (data, row stride, index of cell (0, 0)). Packed tiles are decoded into `scratch`.
    fn view<'a>(&'a self, k: u64, slot: &'a Slot, scratch: &'a mut Vec<u8>) -> Result<(&'a [u8], usize, usize), TileError> {
        let (tx, ty) = unkey(k);
        let rect = self.rect(tx, ty);
        Ok(match slot {
            Slot::Resident(i) => (&self.pool[*i as usize].cells[..], self.stride, self.stride + 1),
            Slot::Raw(b) => (&b[..], self.t, 0),
            Slot::Packed(b) => {
                scratch.clear();
                scratch.resize(self.t * self.t, 0);
                decode(b, scratch, self.t, 0, self.t, self.w, self.n, rect)?;
                (&scratch[..], self.t, 0)
            }
            Slot::Lz4(b) => {
                let mut canon = vec![];
                expand(b, canonical_len(self.t, self.w), &mut canon)?;
                scratch.clear();
                scratch.resize(self.t * self.t, 0);
                if packed_len(self.t, self.w) < self.t * self.t {
                    decode(&canon, scratch, self.t, 0, self.t, self.w, self.n, rect)?;
                } else {
                    load_raw(&canon, scratch, self.t, 0, self.t, self.n, rect)?;
                }
                (&scratch[..], self.t, 0)
            }
        })
    }

    /// Internal consistency, for tests: accounting matches the payloads, every resident slot and pool entry agree, the
    /// cache respects its bound, and no buffer's halo or off-board cell has been written.
    pub fn check_invariants(&self) -> Result<(), String> {
        let (mut inactive, mut resident) = (0usize, 0usize);
        for (&k, s) in &self.dir {
            match s {
                Slot::Resident(i) => {
                    let p = self.pool.get(*i as usize).ok_or("resident slot beyond pool")?;
                    if !p.live || p.key != k {
                        return Err(format!("resident slot {k:x} points at a dead or foreign buffer"));
                    }
                    resident += 1;
                }
                Slot::Raw(b) | Slot::Packed(b) | Slot::Lz4(b) => inactive += b.len(),
            }
        }
        if inactive != self.inactive_bytes {
            return Err(format!("inactive_bytes {} but payloads sum to {inactive}", self.inactive_bytes));
        }
        let live = self.pool.iter().filter(|p| p.live).count();
        if live != resident || live + self.free.len() != self.pool.len() {
            return Err(format!("{live} live buffers, {resident} resident slots, {} free, {} pooled", self.free.len(), self.pool.len()));
        }
        if self.free.iter().any(|&i| self.pool[i as usize].live) {
            return Err("free-listed buffer is live".into());
        }
        if let Some(cap) = self.cfg.cache_tiles
            && self.pool.len() > cap {
                return Err(format!("{} buffers exceed the cache bound {cap}", self.pool.len()));
            }
        for p in &self.pool {
            let s = self.stride;
            let halo_ok = (0..s).all(|i| p.cells[i] == SENT && p.cells[(s - 1) * s + i] == SENT && p.cells[i * s] == SENT && p.cells[i * s + s - 1] == SENT);
            if !halo_ok {
                return Err("a halo cell was overwritten".into());
            }
            if p.live {
                let (tx, ty) = unkey(p.key);
                let rect = self.rect(tx, ty);
                for ly in 0..self.t {
                    for lx in 0..self.t {
                        let b = p.cells[(ly + 1) * s + lx + 1];
                        if !rect.contains(lx, ly) && b != SENT {
                            return Err("an off-board cell was overwritten".into());
                        }
                        if rect.contains(lx, ly) && (b & 127) as usize >= self.n {
                            return Err("colour out of range".into());
                        }
                    }
                }
            }
        }
        Ok(())
    }

    /// Lean-encoded byte at `(x, y)` (relative coordinates), read without disturbing the cache; `None` off the board.
    pub fn byte_at(&self, x: i64, y: i64) -> Option<u8> {
        if x < self.lo || x >= self.hi || y < self.lo || y >= self.hi {
            return None;
        }
        let t = self.t as i64;
        let (tx, ty) = (x.div_euclid(t), y.div_euclid(t));
        let (lx, ly) = ((x - tx * t) as usize, (y - ty * t) as usize);
        let k = key(tx, ty);
        let Some(slot) = self.dir.get(&k) else { return Some(0) };
        let mut scratch = vec![];
        let (d, stride, base) = self.view(k, slot, &mut scratch).expect("consistent tile");
        Some(d[base + ly * stride + lx])
    }

    /// Every on-board cell whose byte is not blank, as ((x, y), byte), sorted by (y, x): the complete logical state.
    pub fn logical_cells(&self) -> Vec<((i64, i64), u8)> {
        let mut out = vec![];
        let mut scratch = vec![];
        let t = self.t as i64;
        for (&k, slot) in &self.dir {
            let (tx, ty) = unkey(k);
            let rect = self.rect(tx, ty);
            let (d, stride, base) = self.view(k, slot, &mut scratch).expect("consistent tile");
            for ly in rect.y0..rect.y1 {
                for lx in rect.x0..rect.x1 {
                    let b = d[base + ly * stride + lx];
                    if b != 0 {
                        out.push(((tx * t + lx as i64, ty * t + ly as i64), b));
                    }
                }
            }
        }
        out.sort_by_key(|&((x, y), _)| (y, x));
        out
    }

    /// Bounding box of touched cells in lean's inner-board coordinates: (minx, miny, maxx, maxy), `usize::MAX`/0 if none.
    fn touched_bbox(&self) -> (usize, usize, usize, usize) {
        let (mut minx, mut miny, mut maxx, mut maxy) = (usize::MAX, usize::MAX, 0usize, 0usize);
        let mut scratch = vec![];
        let (t, c) = (self.t as i64, -self.lo);
        for (&k, slot) in &self.dir {
            let (tx, ty) = unkey(k);
            let rect = self.rect(tx, ty);
            let (d, stride, base) = self.view(k, slot, &mut scratch).expect("consistent tile");
            for ly in rect.y0..rect.y1 {
                let row = &d[base + ly * stride + rect.x0..base + ly * stride + rect.x1];
                if let (Some(a), Some(b)) = (row.iter().position(|&b| b & TOUCHED != 0), row.iter().rposition(|&b| b & TOUCHED != 0)) {
                    minx = minx.min((tx * t + (rect.x0 + a) as i64 + c) as usize);
                    maxx = maxx.max((tx * t + (rect.x0 + b) as i64 + c) as usize);
                    miny = miny.min((ty * t + ly as i64 + c) as usize);
                    maxy = maxy.max((ty * t + ly as i64 + c) as usize);
                }
            }
        }
        (minx, miny, maxx, maxy)
    }
}

/// As `lean::run_lean`: same result on a fresh blank board.
pub fn run_tiled(rule: &Rule, grid: &mut TiledGrid, cfg: &Config) -> RunResult {
    run_tiled_ckpt(rule, grid, cfg, None).expect("no checkpoint, no error")
}

/// As `lean::run_lean_ckpt`, with the tiled checkpoint format (`TTK1`, see `save_ckpt`). A missing checkpoint starts afresh
/// and one past `cfg.max_steps` is ignored, as in lean; a checkpoint for another rule/board/tile size or a damaged one is an
/// error rather than silently overwritten.
pub fn run_tiled_ckpt(rule: &Rule, grid: &mut TiledGrid, cfg: &Config, ckpt: Option<&Ckpt>) -> Result<RunResult, TileError> {
    grid.begin(rule);
    let mut tb = tables(rule);
    tb.fused = fused_table(&tb, grid.stride);
    let c = (grid.size / 2) as i64;
    grid.enter(0, 0);
    let mut steps = 0u64;
    let mut stop = Stop::Budget;
    if let Some(ck) = ckpt
        && let Some(st) = load_ckpt(&ck.path, rule, grid)? {
            if st.steps <= cfg.max_steps {
                grid.enter(st.x, st.y);
                grid.h = st.h;
                steps = st.steps;
            } else {
                grid.begin(rule);
                grid.enter(0, 0);
            }
        }
    while steps < cfg.max_steps {
        let k = ckpt.map_or(u64::MAX, |c| c.every.max(1)).min(cfg.max_steps - steps);
        let (d, left) = grid.advance_steps(&tb, k);
        steps += d;
        if left {
            stop = Stop::Escaped;
            break;
        }
        if let Some(ck) = ckpt {
            save_ckpt(&ck.path, rule, grid, steps)?;
        }
    }
    let (px, py) = grid.position();
    let h = grid.h;
    let (start_x, start_y) = (c as usize, c as usize);

    // Trail: positions at times T-len+1..=T where T is the last in-board time (steps-1 if escaped), rebuilt as in lean.
    let last_t = if stop == Stop::Escaped { steps - 1 } else { steps };
    let len = (cfg.history as u64).min(last_t + 1);
    let back = steps - (last_t + 1 - len);
    let hist = grid.reverse(&tb, back);
    let mut trail = vec![(0i32, 0i32); len as usize];
    for (k, slot) in trail.iter_mut().enumerate() {
        let time = last_t + 1 - len + k as u64;
        let (x, y) = hist[(steps - time) as usize];
        *slot = (x as i32, y as i32);
    }
    debug_assert_eq!(grid.position(), *hist.last().unwrap());
    grid.advance_steps(&tb, back); // restore the final state by stepping forward again
    debug_assert_eq!((grid.position(), grid.h), ((px, py), h));

    let (periodic_tail, highway) = classify_trail(&trail, cfg, stop, h);
    let last = (stop == Stop::Budget).then(|| ((px + c) as usize, (py + c) as usize));
    let extent = finish_extent(grid.touched_bbox(), (start_x, start_y), last);
    Ok(RunResult { steps, stop, pos: (px as i32, py as i32), heading: h, highway, periodic_tail, extent })
}

/// As `lean::highway_onset_flat`, on a tiled board of the same side (`grid.size`), so that a highway run needs no
/// `(size+2)^2` allocation. Leaves `grid` holding the replayed state.
pub fn highway_onset_tiled(rule: &Rule, hw: crate::detect::Highway, until: u64, grid: &mut TiledGrid) -> u64 {
    grid.begin(rule);
    let mut tb = tables(rule);
    tb.fused = fused_table(&tb, grid.stride);
    let p = hw.period as usize;
    let mut ring = vec![(0i32, 0i32); p];
    grid.enter(0, 0);
    let (mut x, mut y) = (0i64, 0i64);
    let mut h = 0u8;
    let (mut step, mut last_bad) = (0u64, 0u64);
    while step < until {
        {
            let cells = &mut grid.pool[grid.cur as usize].cells;
            let mut i = grid.idx;
            while step < until {
                let b = cells[i];
                if b == SENT {
                    break;
                }
                let (nh, delta) = tb.fused[((h as usize) << 8) | b as usize];
                cells[i] = tb.next[b as usize];
                h = nh as u8;
                i = i.wrapping_add_signed(delta as isize);
                let (dx, dy) = DIRS[h as usize];
                x += dx as i64;
                y += dy as i64;
                step += 1;
                let pos = (x as i32, y as i32);
                let slot = (step as usize) % p;
                let prev = ring[slot];
                ring[slot] = pos;
                if step < p as u64 || (pos.0 - prev.0, pos.1 - prev.1) != (hw.dx, hw.dy) {
                    last_bad = step;
                }
            }
            grid.idx = i;
        }
        if step < until && grid.settle() {
            break; // left the board (only possible on the final step of an escaped run)
        }
    }
    (last_bad + 1).saturating_sub(p as u64)
}

const MAGIC: &[u8; 4] = b"TTK1";

struct CkptState {
    steps: u64,
    x: i64,
    y: i64,
    h: u8,
}

fn fnv1a(bytes: &[u8]) -> u64 {
    bytes.iter().fold(0xcbf2_9ce4_8422_2325u64, |h, &b| (h ^ b as u64).wrapping_mul(0x100_0000_01b3))
}

/// Tiled checkpoint, version 1, little-endian:
/// `"TTK1"`, `u32` version, `u32` rule-name length + name, `u64` board side, `u32` tile_log2, `u8` colour width,
/// `u64` steps, `i64` x, `i64` y (cursor, relative to the start), `u8` heading, `u64` tile count, then per tile in
/// ascending (ty, tx) order: `i32` tx, `i32` ty, `u8` tag (1 packed, 2 raw), `u32` length, payload; finally `u64`
/// FNV-1a of everything before. Blank tiles are omitted and the payload form depends only on (colours, tile size), so the
/// bytes are independent of cache size, eviction history and `Inactive` mode.
fn save_ckpt(path: &std::path::Path, rule: &Rule, grid: &TiledGrid, steps: u64) -> Result<(), TileError> {
    let io = |e: std::io::Error| TileError::Io(format!("{}: {e}", path.display()));
    let (x, y) = grid.position();
    let name = rule.to_string();
    let mut b: Vec<u8> = vec![];
    b.extend_from_slice(MAGIC);
    b.extend_from_slice(&CKPT_VERSION.to_le_bytes());
    b.extend_from_slice(&(name.len() as u32).to_le_bytes());
    b.extend_from_slice(name.as_bytes());
    b.extend_from_slice(&(grid.size as u64).to_le_bytes());
    b.extend_from_slice(&grid.cfg.tile_log2.to_le_bytes());
    b.push(grid.w as u8);
    b.extend_from_slice(&steps.to_le_bytes());
    b.extend_from_slice(&x.to_le_bytes());
    b.extend_from_slice(&y.to_le_bytes());
    b.push(grid.h);
    let mut keys: Vec<(i64, i64)> = grid.dir.keys().map(|&k| unkey(k)).map(|(tx, ty)| (ty, tx)).collect();
    keys.sort_unstable();
    let (t, w) = (grid.t, grid.w);
    let mut tiles: Vec<u8> = vec![];
    let mut count = 0u64;
    let mut scratch = vec![];
    let mut enc = vec![];
    for (ty, tx) in keys {
        let k = key(tx, ty);
        let slot = &grid.dir[&k];
        let rect = grid.rect(tx, ty);
        let (tag, payload): (u8, &[u8]) = match slot {
            Slot::Packed(p) => (1, p), // already canonical: only built when packed is smaller
            Slot::Lz4(b) => {
                expand(b, canonical_len(t, w), &mut enc)?;
                (if packed_len(t, w) < t * t { 1 } else { 2 }, &enc)
            }
            _ => {
                let (d, stride, base) = grid.view(k, slot, &mut scratch)?;
                let blank = (rect.y0..rect.y1).all(|ly| d[base + ly * stride + rect.x0..base + ly * stride + rect.x1].iter().all(|&v| v == 0));
                if blank {
                    continue;
                }
                if packed_len(t, w) < t * t {
                    encode(d, stride, base, t, w, rect, &mut enc);
                    (1, &enc)
                } else {
                    store_raw(d, stride, base, t, rect, &mut enc);
                    (2, &enc)
                }
            }
        };
        tiles.extend_from_slice(&(tx as i32).to_le_bytes());
        tiles.extend_from_slice(&(ty as i32).to_le_bytes());
        tiles.push(tag);
        tiles.extend_from_slice(&(payload.len() as u32).to_le_bytes());
        tiles.extend_from_slice(payload);
        count += 1;
    }
    b.extend_from_slice(&count.to_le_bytes());
    b.extend_from_slice(&tiles);
    let sum = fnv1a(&b);
    b.extend_from_slice(&sum.to_le_bytes());
    let tmp = path.with_extension("tmp");
    {
        use std::io::Write;
        let mut f = std::fs::File::create(&tmp).map_err(io)?;
        f.write_all(&b).map_err(io)?;
        f.sync_all().map_err(io)?;
    }
    std::fs::rename(&tmp, path).map_err(io) // atomic: a kill mid-save leaves the previous checkpoint intact
}

/// `Ok(None)` if the file does not exist. Otherwise the tiles are installed as inactive payloads (the grid is rebuilt from
/// scratch) and the cursor state returned; any inconsistency is an error and leaves the grid blank.
fn load_ckpt(path: &std::path::Path, rule: &Rule, grid: &mut TiledGrid) -> Result<Option<CkptState>, TileError> {
    let b = match std::fs::read(path) {
        Ok(b) => b,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(None),
        Err(e) => return Err(TileError::Io(format!("{}: {e}", path.display()))),
    };
    let r = parse_ckpt(&b, rule, grid);
    if r.is_err() {
        grid.begin(rule);
    }
    r.map(Some)
}

fn parse_ckpt(b: &[u8], rule: &Rule, grid: &mut TiledGrid) -> Result<CkptState, TileError> {
    let bad = |m: &str| TileError::Corrupt(m.to_string());
    if b.len() < 8 || &b[..4] != MAGIC {
        return Err(bad("not a tiled checkpoint (bad magic)"));
    }
    let (body, tail) = b.split_at(b.len() - 8);
    if fnv1a(body) != u64::from_le_bytes(tail.try_into().unwrap()) {
        return Err(bad("checksum mismatch (truncated or damaged)"));
    }
    let mut p = 4usize;
    let mut take = |n: usize| -> Result<&[u8], TileError> {
        let s = body.get(p..p + n).ok_or_else(|| TileError::Corrupt("truncated".into()))?;
        p += n;
        Ok(s)
    };
    let u32_ = |s: &[u8]| u32::from_le_bytes(s.try_into().unwrap());
    let u64_ = |s: &[u8]| u64::from_le_bytes(s.try_into().unwrap());
    let i64_ = |s: &[u8]| i64::from_le_bytes(s.try_into().unwrap());
    let version = u32_(take(4)?);
    if version != CKPT_VERSION {
        return Err(TileError::Incompatible(format!("format version {version}, this build reads {CKPT_VERSION}")));
    }
    let nl = u32_(take(4)?) as usize;
    let name = take(nl)?;
    if name != rule.to_string().as_bytes() {
        return Err(TileError::Incompatible(format!("checkpoint is for rule {}", String::from_utf8_lossy(name))));
    }
    let size = u64_(take(8)?);
    if size != grid.size as u64 {
        return Err(TileError::Incompatible(format!("checkpoint board {size}, run board {}", grid.size)));
    }
    let tl = u32_(take(4)?);
    if tl != grid.cfg.tile_log2 {
        return Err(TileError::Incompatible(format!("checkpoint tile_log2 {tl}, run tile_log2 {}", grid.cfg.tile_log2)));
    }
    let w = take(1)?[0] as u32;
    if w != grid.w {
        return Err(bad("colour width disagrees with the rule"));
    }
    let steps = u64_(take(8)?);
    let (x, y) = (i64_(take(8)?), i64_(take(8)?));
    let h = take(1)?[0];
    if h > 3 {
        return Err(bad("heading out of range"));
    }
    let count = u64_(take(8)?);
    if x.abs() > size as i64 + 1 || y.abs() > size as i64 + 1 {
        return Err(bad("cursor far outside the board"));
    }
    grid.begin(rule);
    let t = grid.t;
    let mut prev: Option<(i64, i64)> = None;
    for _ in 0..count {
        let tx = u32_(take(4)?) as i32 as i64;
        let ty = u32_(take(4)?) as i32 as i64;
        let tag = take(1)?[0];
        let len = u32_(take(4)?) as usize;
        let payload = take(len)?;
        if prev.is_some_and(|q| q >= (ty, tx)) {
            return Err(bad("tiles not in strictly ascending (ty, tx) order"));
        }
        prev = Some((ty, tx));
        let rect = grid.rect(tx, ty);
        if rect.x0 >= rect.x1 || rect.y0 >= rect.y1 {
            return Err(bad("tile lies outside the board"));
        }
        // Validate now (a throwaway decode) so corruption surfaces here, not as a panic when the tile is first entered.
        let mut tmp = vec![SENT; t * t];
        match tag {
            1 if packed_len(t, w) < t * t => decode(payload, &mut tmp, t, 0, t, w, grid.n, rect)?,
            2 if packed_len(t, w) >= t * t => load_raw(payload, &mut tmp, t, 0, t, grid.n, rect)?,
            _ => return Err(bad("tile tag does not match this rule's canonical form")),
        }
        let blank = (rect.y0..rect.y1).all(|ly| tmp[ly * t + rect.x0..ly * t + rect.x1].iter().all(|&v| v == 0));
        if blank {
            return Err(bad("blank tile stored"));
        }
        grid.inactive_bytes += len;
        let payload: Box<[u8]> = payload.into();
        grid.dir.insert(key(tx, ty), if tag == 1 { Slot::Packed(payload) } else { Slot::Raw(payload) });
    }
    if p != body.len() {
        return Err(bad("trailing bytes"));
    }
    Ok(CkptState { steps, x, y, h })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn widths() {
        let w: Vec<u32> = [1, 2, 3, 4, 5, 8, 9, 16, 17, 64, 65, 99].iter().map(|&n| colour_width(n)).collect();
        assert_eq!(w, [0, 1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 7]);
    }

    #[test]
    fn key_round_trip_negative() {
        for (x, y) in [(0, 0), (-1, 5), (7, -9), (-2_000_000, 2_000_000), (i32::MIN as i64, i32::MAX as i64)] {
            assert_eq!(unkey(key(x, y)), (x, y));
        }
    }
}
