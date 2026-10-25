//! On-disk checkpoints for `Sim`. The walker is not stored: it must be stateless (`PatchedAnt`,
//! `Rotor`: pure functions of position and seed) and is supplied again on restore. `recipe`
//! identifies the run (rule, seed, bands, board, cap, instrument version); a checkpoint of a
//! different recipe is refused. Boards are stored cropped to the visited bounding box.

use super::*;
use crate::snap::{Rd, Wr, get_crop, put_crop};

const MAGIC: &[u8] = b"FPCK1";

fn put_key(w: &mut Wr, k: &StateKey) {
    w.u64(k.m as u64);
    w.u64(k.dir as u64);
    w.u64(k.heading as u64);
    w.u64(k.phase as u64);
    w.u64(k.patch as u64);
    w.u64(k.hist as u64);
}

fn get_key(r: &mut Rd) -> Result<StateKey, String> {
    Ok(StateKey { m: r.u64()? as u8, dir: r.u64()? as u8, heading: r.u64()? as u8, phase: r.u64()? as u8, patch: r.u64()? as u16, hist: r.u64()? as u16 })
}

fn put_ep(w: &mut Wr, e: &EpTally) {
    for v in [e.entered_complete, e.entered_complete_steps, e.entered_unresolved, e.unresolved_lower, e.left_fragments, e.left_fragment_overlap, e.overlap, e.unresolved_overlap] {
        w.u64(v);
    }
    w.u64s(&e.hist_n);
    w.u64s(&e.hist_steps);
}

#[allow(clippy::field_reassign_with_default)] // fields are read in file order
fn get_ep(r: &mut Rd) -> Result<EpTally, String> {
    let mut e = EpTally::default();
    e.entered_complete = r.u64()?;
    e.entered_complete_steps = r.u64()?;
    e.entered_unresolved = r.u64()?;
    e.unresolved_lower = r.u64()?;
    e.left_fragments = r.u64()?;
    e.left_fragment_overlap = r.u64()?;
    e.overlap = r.u64()?;
    e.unresolved_overlap = r.u64()?;
    e.hist_n = r.u64s()?;
    e.hist_steps = r.u64s()?;
    Ok(e)
}

impl DepthField {
    pub fn snap(&self, w: &mut Wr) {
        self.region.snap(w);
        w.u64(self.decreases);
        w.u64(self.raised);
        put_crop(w, &self.depth, self.size, self.region.bbox());
    }

    pub fn unsnap(r: &mut Rd) -> Result<Self, String> {
        let region = Region::unsnap(r)?;
        let mut f = DepthField::new(region.size());
        f.region = region;
        f.decreases = r.u64()?;
        f.raised = r.u64()?;
        get_crop(r, &mut f.depth, f.size)?;
        Ok(f)
    }
}

impl<W: Walker + Clone> Sim<W> {
    /// Serialise the full dynamic state. Only meaningful for stateless walkers (see module note).
    pub fn snapshot(&self, recipe: &str) -> Vec<u8> {
        assert!(self.trace.is_none(), "trace recording cannot be checkpointed");
        assert!(self.ctx4.is_none(), "radius-4 context recording cannot be checkpointed");
        let mut w = Wr::default();
        w.0.extend_from_slice(MAGIC);
        w.bytes(recipe.as_bytes());
        w.u64(self.cap);
        w.i64(self.margin);
        w.u64(self.bands.len() as u64);
        for b in &self.bands {
            for v in [b.lo, b.hi, b.t_start, b.t_end, b.area_start, b.area_end, b.perim_end, b.steps, b.b_dep, b.i_dep, b.seg_overlap] {
                w.u64(v);
            }
            w.bool(b.reached_lo);
            w.bool(b.reached_hi);
            w.f64(b.sum_pa);
            put_ep(&mut w, &b.eps[0]);
            put_ep(&mut w, &b.eps[1]);
        }
        for v in self.tau_lo.iter().chain(self.tau_hi.iter()) {
            w.opt_u64(*v);
        }
        w.u64(self.started as u64);
        w.opt_u64(self.active.map(|a| a as u64));
        self.field.snap(&mut w);
        put_crop(&mut w, &self.colour, self.field.size, self.field.region.bbox());
        w.i64(self.pos.0);
        w.i64(self.pos.1);
        w.u8(self.h);
        w.u64(self.t);
        w.u64(self.idx as u64);
        w.bool(self.prev.is_some());
        if let Some(p) = self.prev {
            w.bool(p.z);
            w.u64(p.area);
            w.u64(p.perim);
            w.u8(p.depth);
        }
        w.bool(self.run.is_some());
        if let Some(r) = &self.run {
            w.u64(r.s);
            w.bool(r.z);
            w.bool(r.start_obs);
        }
        w.bool(self.seg.is_some());
        if let Some(s) = &self.seg {
            w.u64(s.cur as u64);
            w.u64(s.start_t);
            put_key(&mut w, &s.key);
            w.opt_u64(s.start_band.map(|b| b as u64));
            w.u64(s.revisits);
            w.bool(s.jump_any);
            w.u64(s.hist as u64);
        }
        w.u64(self.tallies.len() as u64);
        for ((band, a, b), p) in &self.tallies {
            w.u64(*band as u64);
            put_key(&mut w, a);
            w.bool(b.is_some());
            if let Some(k) = b {
                put_key(&mut w, k);
            }
            for v in [p.n, p.time, p.skipped, p.jumps, p.revisits] {
                w.u64(v);
            }
        }
        w.bytes(&self.cls);
        w.u64(self.max_pairs as u64);
        w.u64(self.overflowed);
        w.u64(self.jump_steps);
        w.u64(self.lipschitz_violations);
        w.u8(match self.stop {
            None => 255,
            Some(Stop::Sink) => 0,
            Some(Stop::Budget) => 1,
            Some(Stop::Escaped) => 2,
        });
        w.0
    }

    #[allow(clippy::field_reassign_with_default)] // fields are read in file order
    pub fn restore(walker: W, bytes: &[u8], recipe: &str) -> Result<Self, String> {
        let mut r = Rd::new(bytes);
        let magic = (0..MAGIC.len()).map(|_| r.u8()).collect::<Result<Vec<u8>, String>>()?;
        if magic != MAGIC {
            return Err("not a first_passage checkpoint".into());
        }
        if r.bytes()? != recipe.as_bytes() {
            return Err("checkpoint recipe differs from this run".into());
        }
        let cap = r.u64()?;
        let margin = r.i64()?;
        let nb = r.u64()? as usize;
        let mut bands = Vec::with_capacity(nb);
        for _ in 0..nb {
            let mut b = BandAgg::default();
            b.lo = r.u64()?;
            b.hi = r.u64()?;
            b.t_start = r.u64()?;
            b.t_end = r.u64()?;
            b.area_start = r.u64()?;
            b.area_end = r.u64()?;
            b.perim_end = r.u64()?;
            b.steps = r.u64()?;
            b.b_dep = r.u64()?;
            b.i_dep = r.u64()?;
            b.seg_overlap = r.u64()?;
            b.reached_lo = r.bool()?;
            b.reached_hi = r.bool()?;
            b.sum_pa = r.f64()?;
            b.eps = [get_ep(&mut r)?, get_ep(&mut r)?];
            bands.push(b);
        }
        let tau_lo = (0..nb).map(|_| r.opt_u64()).collect::<Result<Vec<_>, _>>()?;
        let tau_hi = (0..nb).map(|_| r.opt_u64()).collect::<Result<Vec<_>, _>>()?;
        let started = r.u64()? as usize;
        let active = r.opt_u64()?.map(|a| a as usize);
        let field = DepthField::unsnap(&mut r)?;
        let ranges: Vec<(u64, u64)> = bands.iter().map(|b| (b.lo, b.hi)).collect();
        let mut s = Sim::new(walker, field.size, cap, &ranges);
        let mut colour = vec![0u8; field.size * field.size];
        get_crop(&mut r, &mut colour, field.size)?;
        s.colour = colour;
        s.field = field;
        s.margin = margin;
        s.bands = bands;
        s.tau_lo = tau_lo;
        s.tau_hi = tau_hi;
        s.started = started;
        s.active = active;
        s.pos = (r.i64()?, r.i64()?);
        s.h = r.u8()?;
        s.t = r.u64()?;
        s.idx = r.u64()? as usize;
        s.prev = if r.bool()? { Some(Prev { z: r.bool()?, area: r.u64()?, perim: r.u64()?, depth: r.u8()? }) } else { None };
        s.run = if r.bool()? { Some(Run { s: r.u64()?, z: r.bool()?, start_obs: r.bool()? }) } else { None };
        s.seg = if r.bool()? {
            Some(Seg { cur: r.u64()? as usize, start_t: r.u64()?, key: get_key(&mut r)?, start_band: r.opt_u64()?.map(|b| b as usize), revisits: r.u64()?, jump_any: r.bool()?, hist: r.u64()? as u16, r4: 0 })
        } else {
            None
        };
        let nt = r.u64()? as usize;
        s.tallies.clear();
        for _ in 0..nt {
            let band = r.u64()? as usize;
            let a = get_key(&mut r)?;
            let b = if r.bool()? { Some(get_key(&mut r)?) } else { None };
            let p = Pair { n: r.u64()?, time: r.u64()?, skipped: r.u64()?, jumps: r.u64()?, revisits: r.u64()? };
            s.tallies.insert((band, a, b), p);
        }
        s.cls = r.bytes()?.to_vec();
        s.max_pairs = r.u64()? as usize;
        s.overflowed = r.u64()?;
        s.jump_steps = r.u64()?;
        s.lipschitz_violations = r.u64()?;
        s.stop = match r.u8()? {
            255 => None,
            0 => Some(Stop::Sink),
            1 => Some(Stop::Budget),
            2 => Some(Stop::Escaped),
            _ => return Err("bad stop code".into()),
        };
        if !r.done() {
            return Err("trailing bytes in checkpoint".into());
        }
        Ok(s)
    }
}
