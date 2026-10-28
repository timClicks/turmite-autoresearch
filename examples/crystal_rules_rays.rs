//! Diagonal-ray segmentation of a trajectory (crystal-rules S1; spec in experiments/archive/2026-10-crystal-rules/README.md, "Ray segmentation").
//!
//! A step t is *ray-like* if over the previous L steps the displacement (dx, dy) has |dx| >= L/8 (i.e. <= 8 steps per cell) and
//! ||dx| - |dy|| <= 2 (straight diagonal within one cell at each end). A ray is a maximal run of ray-like steps with the same
//! diagonal heading (sign dx, sign dy); it spans steps (first - L, last]. Endpoints are therefore accurate to about L steps.
//! The segmenter is a pure function of the position/colour sequence, so it is tested on planted paths and against the oracle.
//!
//! Usage: ant RULE STEPS SIZE | rotor SEED STEPS SIZE | rw SEED STEPS SIZE   (blank board; CSV of rays with length >= 16 cells to stdout)
use turmite::{Rule, DIRS};

pub const L: usize = 128;

#[derive(Clone, Debug)]
pub struct Ray {
    pub t_start: u64,
    pub t_end: u64,
    pub heading: (i32, i32),
    pub cells: Vec<(i32, i32)>,
    pub colours: Vec<u8>,
}

impl Ray {
    pub fn length_cells(&self) -> i32 {
        let (a, b) = (self.cells[0], *self.cells.last().unwrap());
        (b.0 - a.0).abs().max((b.1 - a.1).abs())
    }
}

/// Streaming segmenter. `push(pos, colour)`: pos after the step, colour read at the step. Initial position given at construction.
pub struct Segmenter {
    px: Vec<i32>,
    py: Vec<i32>,
    col: Vec<u8>,
    t: u64,
    active: Option<Ray>,
}

impl Segmenter {
    pub fn new(start: (i32, i32)) -> Self {
        let mut s = Segmenter { px: vec![0; L + 1], py: vec![0; L + 1], col: vec![0; L + 1], t: 0, active: None };
        s.px[0] = start.0;
        s.py[0] = start.1;
        s
    }

    pub fn push(&mut self, pos: (i32, i32), colour: u8, out: &mut Vec<Ray>) {
        self.t += 1;
        let i = (self.t % (L as u64 + 1)) as usize;
        self.px[i] = pos.0;
        self.py[i] = pos.1;
        self.col[i] = colour;
        let mut heading = None;
        if self.t >= L as u64 {
            let j = ((self.t - L as u64) % (L as u64 + 1)) as usize;
            let (dx, dy) = (pos.0 - self.px[j], pos.1 - self.py[j]);
            if dx.abs() >= (L / 8) as i32 && (dx.abs() - dy.abs()).abs() <= 2 && dy != 0 {
                heading = Some((dx.signum(), dy.signum()));
            }
        }
        match (heading, self.active.as_mut()) {
            (Some(h), Some(r)) if r.heading == h => {
                r.t_end = self.t;
                r.cells.push(pos);
                r.colours.push(colour);
            }
            (Some(h), _) => {
                if let Some(r) = self.active.take() {
                    out.push(r);
                }
                let t0 = self.t - L as u64;
                let (mut cells, mut colours) = (Vec::with_capacity(L + 1), Vec::with_capacity(L));
                for u in t0..=self.t {
                    let k = (u % (L as u64 + 1)) as usize;
                    cells.push((self.px[k], self.py[k]));
                    if u > t0 {
                        colours.push(self.col[k]);
                    }
                }
                self.active = Some(Ray { t_start: t0, t_end: self.t, heading: h, cells, colours });
            }
            (None, _) => {
                if let Some(r) = self.active.take() {
                    out.push(r);
                }
            }
        }
    }

    pub fn finish(&mut self, out: &mut Vec<Ray>) {
        if let Some(r) = self.active.take() {
            out.push(r);
        }
    }
}

/// Smallest period p in 2..=256 with >= 98% agreement of c[i] == c[i+p] over the central half; returns (p, agreement, canonical motif).
pub fn motif(c: &[u8]) -> Option<(usize, f64, Vec<u8>)> {
    let m = c.len();
    let mid = &c[m / 4..3 * m / 4];
    for p in 2..=256usize {
        if mid.len() <= 4 * p {
            return None;
        }
        let ok = (0..mid.len() - p).filter(|&i| mid[i] == mid[i + p]).count();
        let f = ok as f64 / (mid.len() - p) as f64;
        if f >= 0.98 {
            let w = &mid[..p];
            let best = (0..p).map(|s| w[s..].iter().chain(&w[..s]).copied().collect::<Vec<u8>>()).min().unwrap();
            return Some((p, f, best));
        }
    }
    None
}

struct Board {
    size: usize,
    cells: Vec<u8>,
    pos: (i32, i32),
    heading: u8,
    rule: Rule,
}
impl Board {
    fn new(rule: Rule, size: usize) -> Self {
        Self { size, cells: vec![0; size * size], pos: (0, 0), heading: 0, rule }
    }
    fn index(&self, p: (i32, i32)) -> usize {
        let c = (self.size / 2) as i32;
        assert!(p.0 + c >= 0 && p.1 + c >= 0 && p.0 + c < self.size as i32 && p.1 + c < self.size as i32, "left the board");
        (p.1 + c) as usize * self.size + (p.0 + c) as usize
    }
    fn step(&mut self) -> u8 {
        let i = self.index(self.pos);
        let colour = self.cells[i];
        self.heading = (self.heading + self.rule.0[colour as usize].delta()) & 3;
        self.cells[i] = (colour + 1) % self.rule.len() as u8;
        let d = DIRS[self.heading as usize];
        self.pos = (self.pos.0 + d.0, self.pos.1 + d.1);
        colour
    }
}

fn heading_bit(h: (i32, i32)) -> u8 {
    1 << (u8::from(h.0 > 0) * 2 + u8::from(h.1 > 0))
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    assert!(a.len() == 5 || a.len() == 6, "ant RULE STEPS SIZE | rotor SEED STEPS SIZE | rw SEED STEPS SIZE");
    let kind = a[1].as_str();
    let steps: u64 = a[3].parse().unwrap();
    let size: usize = a[4].parse().unwrap();
    let mut rays = Vec::new();
    let mut seg = Segmenter::new((0, 0));
    match kind {
        "ant" => {
            let mut b = Board::new(a[2].parse().unwrap(), size);
            for _ in 0..steps {
                let c = b.step();
                seg.push(b.pos, c, &mut rays);
            }
        }
        "rotor" => {
            let mut w = turmite::reference::Rotor::new(a[2].parse().unwrap());
            for _ in 0..steps {
                w.step();
                seg.push(w.pos, 0, &mut rays);
            }
        }
        "rw" => {
            let mut w = turmite::reference::RandomWalk::new(a[2].parse().unwrap());
            for _ in 0..steps {
                w.step();
                seg.push(w.pos, 0, &mut rays);
            }
        }
        _ => panic!("kind"),
    }
    seg.finish(&mut rays);
    // Overlap with earlier rays by heading: flat bitmap of (cell, heading) so memory is size^2 bytes.
    let c0 = (size / 2) as i32;
    let idx = |p: (i32, i32)| (p.1 + c0) as usize * size + (p.0 + c0) as usize;
    let mut seen = vec![0u8; size * size];
    println!("kind,spec,t_start,t_end,length_cells,hx,hy,steps_per_cell,term_colour,period,agree,motif,rev_frac,same_frac");
    for r in rays {
        let len = r.length_cells();
        let hb = heading_bit(r.heading);
        let ob = heading_bit((-r.heading.0, -r.heading.1));
        let n = r.cells.len() as f64;
        let rev = r.cells.iter().filter(|&&p| seen[idx(p)] & ob != 0).count() as f64 / n;
        let same = r.cells.iter().filter(|&&p| seen[idx(p)] & hb != 0).count() as f64 / n;
        for &p in &r.cells {
            seen[idx(p)] |= hb;
        }
        if len < 16 {
            continue;
        }
        let spc = (r.t_end - r.t_start) as f64 / len as f64;
        let (p, f, m) = motif(&r.colours).map(|(p, f, m)| (p, f, m.iter().map(|c| (b'0' + c) as char).collect::<String>())).unwrap_or((0, 0.0, String::new()));
        println!("{kind},{},{},{},{len},{},{},{spc:.3},{},{p},{f:.4},{m},{rev:.4},{same:.4}", a[2], r.t_start, r.t_end, r.heading.0, r.heading.1, r.colours.last().unwrap());
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use proptest::prelude::*;

    fn run(path: &[(i32, i32)]) -> Vec<Ray> {
        let mut s = Segmenter::new(path[0]);
        let mut out = Vec::new();
        for &p in &path[1..] {
            s.push(p, 0, &mut out);
        }
        s.finish(&mut out);
        out
    }

    /// Planted piecewise path: random-walk filler, then diagonal rays with `spc` in {2, 4, 6} steps per cell. Returns path and planted (t0, t1, heading).
    fn planted(seed: u64, n_rays: usize) -> (Vec<(i32, i32)>, Vec<(u64, u64, (i32, i32))>) {
        let mut st = seed;
        let mut p = (0, 0);
        let mut path = vec![p];
        let mut plan = vec![];
        for _ in 0..n_rays {
            for _ in 0..600 {
                let d = DIRS[(turmite::walkers::splitmix_next(&mut st) % 4) as usize];
                p = (p.0 + d.0, p.1 + d.1);
                path.push(p);
            }
            let h = [(1, 1), (1, -1), (-1, 1), (-1, -1)][(turmite::walkers::splitmix_next(&mut st) % 4) as usize];
            let cells = 80 + (turmite::walkers::splitmix_next(&mut st) % 120) as i32;
            let wiggle = (turmite::walkers::splitmix_next(&mut st) % 3) as usize; // 0: 2 steps/cell, 1: 4, 2: 6
            let t0 = path.len() as u64 - 1;
            for _ in 0..cells {
                let mv = [(h.0, 0), (0, h.1)];
                let mut seq = vec![mv[0], mv[1]];
                for _ in 0..wiggle {
                    seq.splice(1..1, [(-h.0, 0), (h.0, 0)]);
                }
                for d in seq {
                    p = (p.0 + d.0, p.1 + d.1);
                    path.push(p);
                }
            }
            plan.push((t0, path.len() as u64 - 1, h));
        }
        (path, plan)
    }

    proptest! {
        #![proptest_config(ProptestConfig::with_cases(40))]
        /// Every planted ray (>= 80 cells, <= 6 steps/cell) is recovered with its heading, endpoints within L steps, and is the dominant overlap.
        #[test]
        fn recovers_planted(seed in 0u64..10_000, n in 1usize..5) {
            let (path, plan) = planted(seed, n);
            let rays: Vec<Ray> = run(&path).into_iter().filter(|r| r.length_cells() >= 40).collect();
            for (t0, t1, h) in plan {
                let hit = rays.iter().find(|r| r.heading == h && r.t_start <= t1 && r.t_end >= t0 && r.t_end.min(t1) - r.t_start.max(t0) >= (t1 - t0) / 2);
                prop_assert!(hit.is_some(), "planted ray {:?} not found in {:?}", (t0, t1, h), rays.iter().map(|r| (r.t_start, r.t_end, r.heading)).collect::<Vec<_>>());
                let r = hit.unwrap();
                prop_assert!(r.t_start.abs_diff(t0) <= 2 * L as u64 && r.t_end.abs_diff(t1) <= 2 * L as u64, "endpoints {:?} vs {:?}", (r.t_start, r.t_end), (t0, t1));
            }
        }

        /// The position stream of the board loop used here equals the reference ant step for step, so segmentation of either is identical.
        #[test]
        fn board_matches_oracle(bits in 0u32..4096, n in 2usize..13, steps in 1usize..3000) {
            let rule = Rule::from_bits(bits, n);
            let mut b = Board::new(rule.clone(), 4096);
            let mut o = turmite::reference::Ant::new(rule);
            let (mut sb, mut so) = (Segmenter::new((0, 0)), Segmenter::new((0, 0)));
            let (mut rb, mut ro) = (vec![], vec![]);
            for _ in 0..steps {
                let p = b.pos;
                let c = b.step();
                prop_assert_eq!(c, o.colour_at(p));
                o.step();
                prop_assert_eq!(b.pos, o.pos);
                sb.push(b.pos, c, &mut rb);
                so.push(o.pos, c, &mut ro);
            }
            sb.finish(&mut rb);
            so.finish(&mut ro);
            prop_assert_eq!(rb.len(), ro.len());
            for (x, y) in rb.iter().zip(&ro) {
                prop_assert_eq!((x.t_start, x.t_end, x.heading, &x.cells, &x.colours), (y.t_start, y.t_end, y.heading, &y.cells, &y.colours));
            }
        }
    }

    #[test]
    fn straight_axial_line_is_not_a_ray() {
        let path: Vec<(i32, i32)> = (0..2000).map(|i| (i, 0)).collect();
        assert!(run(&path).is_empty());
    }

    #[test]
    fn motif_period_and_rotation() {
        let w = [1u8, 2, 0, 2, 2, 1, 0];
        let c: Vec<u8> = (0..4000).map(|i| w[i % 7]).collect();
        let (p, f, m) = motif(&c).unwrap();
        assert_eq!((p, f), (7, 1.0));
        let rot: Vec<u8> = (0..4000).map(|i| w[(i + 3) % 7]).collect();
        assert_eq!(motif(&rot).unwrap().2, m, "canonical form is rotation invariant");
    }
}
