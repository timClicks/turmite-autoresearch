//! Falsification harness (experiment `2026-10-falsification-harness`).
//!
//! A registered claim about a rule ("this rule forms a stable highway", "this rule is chaotic")
//! is attacked rather than merely re-run for longer: perturbed initial boards, asymmetric
//! colourings, obstacles dropped in front of an established highway, off-centre starts on
//! odd-sized boards, and a hill-climb over seed patches that maximises the delay before the
//! claimed behaviour. Every attack is a deterministic function of (claim seed, rule, class,
//! index), so output is independent of thread count.
//!
//! What a finite run can and cannot refute, which decides the verdict logic:
//! - "no highway" (chaotic) claims are refuted by one *confirmed* highway, reproduced on a second
//!   board geometry. Surviving is only "no highway by horizon h" and is reported per 4x of horizon.
//! - "highway from every start" claims are refuted conclusively only by a confirmed highway of a
//!   different type (when the claim says the type is fixed). A start that has not escaped by the
//!   horizon is `Unresolved`, which is "unsupported at this horizon", never "refuted".
//! - Two instrument controls must pass or the verdict is `Invalid`: the four headings of a blank
//!   start are rotations of one another, and a blank start near a board edge has the same dynamics
//!   as the centred one, so a confirmed highway of a different type there is a detector error.
//!
//! Only finite perturbations with a blank far field are valid: `detect` assumes a highway ends in
//! blank cells.
//!
//! `simulate` is checked step for step against `reference::Ant` in `tests/falsify.rs`.

use crate::detect::{Highway, MIN_SPAN, exit_confirms, find_highway};
use crate::fast::Trail;
use crate::walkers::{mix64, splitmix_next};
use crate::{DIRS, Rule};
use std::collections::BTreeMap;

/// Finite non-blank cells (relative to the start cell) and the starting heading.
#[derive(Clone, Debug, PartialEq, Eq, Default)]
pub struct Init {
    pub cells: Vec<((i32, i32), u8)>,
    pub heading: u8,
}

/// A patch of random colours dropped `ahead` cells in front of the ant's direction of travel at
/// step `at`.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Perturb {
    pub at: u64,
    pub ahead: i32,
    pub radius: i32,
    pub seed: u64,
}

#[derive(Clone, Debug)]
pub struct Sim {
    pub size: usize,
    /// Start cell in grid coordinates (the centre unless stressing the boundary).
    pub start: (usize, usize),
    pub max_steps: u64,
    pub history: usize,
    pub max_period: usize,
}

impl Sim {
    pub fn centred(size: usize, max_steps: u64) -> Sim {
        Sim { size, start: (size / 2, size / 2), max_steps, history: 250_000, max_period: 50_000 }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Outcome {
    /// Periodic motion with drift that carried the ant off the board, outward.
    Highway(Highway),
    /// Left the board without a confirmed highway (edge-walker or too-short window).
    EdgeEscape,
    /// Still on the board at the step budget.
    Unresolved,
}

#[derive(Clone, Debug)]
pub struct Run {
    pub outcome: Outcome,
    pub steps: u64,
    pub pos: (i32, i32),
    pub heading: u8,
    pub extent: (u32, u32),
}

/// Highway type up to the symmetries of the square lattice: (period, |long drift|, |short drift|).
pub fn canon(hw: Highway) -> (u32, u32, u32) {
    let (a, b) = (hw.dx.unsigned_abs(), hw.dy.unsigned_abs());
    (hw.period, a.max(b), a.min(b))
}

/// Run `rule` from `init` on a fresh flat board. Starts with a fresh allocation every call, so a
/// seed can never leak into a later run (`fast::Grid::reset` only clears the old bounding box).
pub fn simulate(rule: &Rule, init: &Init, sim: &Sim, perturb: Option<&Perturb>) -> Run {
    let n = rule.len();
    let size = sim.size;
    let (sx, sy) = sim.start;
    let mut cells = vec![0u8; size * size];
    let index = |p: (i32, i32)| -> Option<usize> {
        let (x, y) = (sx as i64 + p.0 as i64, sy as i64 + p.1 as i64);
        (x >= 0 && y >= 0 && x < size as i64 && y < size as i64).then(|| y as usize * size + x as usize)
    };
    let (mut minx, mut miny, mut maxx, mut maxy) = (sx, sy, sx, sy);
    for &(p, c) in &init.cells {
        debug_assert!((c as usize) < n);
        let i = index(p).expect("seed cell outside board");
        cells[i] = c;
        minx = minx.min(sx.wrapping_add_signed(p.0 as isize));
        maxx = maxx.max(sx.wrapping_add_signed(p.0 as isize));
        miny = miny.min(sy.wrapping_add_signed(p.1 as isize));
        maxy = maxy.max(sy.wrapping_add_signed(p.1 as isize));
    }
    let next: Vec<u8> = (0..n).map(|i| ((i + 1) % n) as u8).collect();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let (mut x, mut y) = (sx, sy);
    let mut h = init.heading & 3;
    let mut steps: u64 = 0;
    let mut trail = Trail::new(sim.history);
    trail.push((0, 0));
    let mut escaped = false;
    let mut event = perturb.map_or(u64::MAX, |p| p.at);
    let rel = |x: usize, y: usize| (x as i32 - sx as i32, y as i32 - sy as i32);
    while steps < sim.max_steps && !escaped {
        let stop = event.min(sim.max_steps);
        while steps < stop {
            let i = y * size + x;
            let col = cells[i] as usize;
            h = (h + turn[col]) & 3;
            cells[i] = next[col];
            let (dx, dy) = DIRS[h as usize];
            x = x.wrapping_add_signed(dx as isize);
            y = y.wrapping_add_signed(dy as isize);
            steps += 1;
            if x >= size || y >= size {
                escaped = true;
                break;
            }
            minx = minx.min(x);
            maxx = maxx.max(x);
            miny = miny.min(y);
            maxy = maxy.max(y);
            trail.push(rel(x, y));
        }
        if !escaped && steps == event && event < sim.max_steps {
            let p = perturb.unwrap();
            let ordered = trail.ordered();
            let back = ordered[ordered.len().saturating_sub(4001)];
            let here = rel(x, y);
            let (vx, vy) = (here.0 - back.0, here.1 - back.1);
            let m = vx.abs().max(vy.abs()).max(1) as f64;
            let c = (
                here.0 + (vx as f64 / m * p.ahead as f64).round() as i32,
                here.1 + (vy as f64 / m * p.ahead as f64).round() as i32,
            );
            let mut st = p.seed;
            for dy in -p.radius..=p.radius {
                for dx in -p.radius..=p.radius {
                    let q = (c.0 + dx, c.1 + dy);
                    let colour = (splitmix_next(&mut st) % n as u64) as u8;
                    if let Some(i) = index(q) {
                        cells[i] = colour;
                        let (gx, gy) = (i % size, i / size);
                        minx = minx.min(gx);
                        maxx = maxx.max(gx);
                        miny = miny.min(gy);
                        maxy = maxy.max(gy);
                    }
                }
            }
            event = u64::MAX;
        }
    }
    let tail = trail.ordered();
    let periodic_tail = find_highway(&tail, sim.max_period, MIN_SPAN);
    let outcome = if escaped {
        match periodic_tail
            .or_else(|| find_highway(&tail, sim.max_period, 2_000))
            .filter(|&hw| exit_confirms(hw, h))
        {
            Some(hw) => Outcome::Highway(hw),
            None => Outcome::EdgeEscape,
        }
    } else {
        Outcome::Unresolved
    };
    Run {
        outcome,
        steps,
        pos: rel(x, y),
        heading: h,
        extent: ((maxx - minx + 1) as u32, (maxy - miny + 1) as u32),
    }
}

// ---------------------------------------------------------------- attacks

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum Class {
    /// The claim as literally stated: blank board, heading 0.
    Blank,
    /// Control: blank start, each of the four headings.
    Heading,
    /// Control: blank start near an edge of an odd-sized board.
    Boundary,
    /// Uniform random colours in a (2r+1)^2 patch, random heading.
    Patch,
    /// Asymmetric: a patch of one colour only.
    Mono,
    /// Asymmetric: a finite half-plane of one colour.
    Half,
    /// Asymmetric: one row or column of random colours.
    Stripe,
    /// Sparse random speckle in a window.
    Sparse,
    /// Blank start, random patch dropped in front of the established highway.
    Obstacle,
    /// Hill-climb over a radius-3 patch against the claim.
    Adaptive,
}

impl Class {
    pub const ALL: [Class; 10] = [
        Class::Blank,
        Class::Heading,
        Class::Boundary,
        Class::Patch,
        Class::Mono,
        Class::Half,
        Class::Stripe,
        Class::Sparse,
        Class::Obstacle,
        Class::Adaptive,
    ];
    pub fn name(self) -> &'static str {
        match self {
            Class::Blank => "blank",
            Class::Heading => "heading",
            Class::Boundary => "boundary",
            Class::Patch => "patch",
            Class::Mono => "mono",
            Class::Half => "half",
            Class::Stripe => "stripe",
            Class::Sparse => "sparse",
            Class::Obstacle => "obstacle",
            Class::Adaptive => "adaptive",
        }
    }
    pub fn parse(s: &str) -> Option<Class> {
        Class::ALL.into_iter().find(|c| c.name() == s)
    }
    /// Controls test the instrument, not the claim.
    pub fn is_control(self) -> bool {
        matches!(self, Class::Heading | Class::Boundary)
    }
}

#[derive(Clone, Debug)]
pub struct Trial {
    pub class: Class,
    pub index: u32,
    pub seed: u64,
    pub init: Init,
    pub sim: Sim,
    pub perturb: Option<Perturb>,
}

#[derive(Clone, Debug)]
pub struct TrialResult {
    pub trial: Trial,
    pub run: Run,
}

fn fnv(s: &str) -> u64 {
    s.bytes().fold(0xcbf2_9ce4_8422_2325, |h, b| (h ^ b as u64).wrapping_mul(0x100_0000_01b3))
}

pub fn trial_seed(claim_seed: u64, rule: &Rule, class: Class, index: u32) -> u64 {
    mix64(mix64(mix64(claim_seed ^ fnv(&rule.to_string())) ^ class as u64) ^ index as u64)
}

/// The blank-start run every other trial is compared with, and what it implies for placing obstacles.
#[derive(Clone, Debug)]
pub struct Baseline {
    pub run: Run,
    pub canon: Option<(u32, u32, u32)>,
    /// Step at which motion became periodic, when the baseline is a highway.
    pub onset: Option<u64>,
    pub period: u32,
}

pub fn baseline(rule: &Rule, size: usize, horizon: u64) -> Baseline {
    let run = simulate(rule, &Init::default(), &Sim::centred(size, horizon), None);
    match run.outcome {
        Outcome::Highway(hw) => Baseline {
            canon: Some(canon(hw)),
            onset: Some(crate::fast::highway_onset(rule, hw, run.steps)),
            period: hw.period,
            run,
        },
        _ => Baseline { run, canon: None, onset: None, period: 0 },
    }
}

fn window_cells(rule_n: u8, st: &mut u64, r: i32, fill: impl Fn(&mut u64, i32, i32) -> Option<u8>) -> Vec<((i32, i32), u8)> {
    let mut m = BTreeMap::new();
    for y in -r..=r {
        for x in -r..=r {
            if let Some(c) = fill(st, x, y) {
                debug_assert!(c < rule_n);
                if c != 0 {
                    m.insert((x, y), c);
                }
            }
        }
    }
    m.into_iter().collect()
}

/// Build trial `index` of `class`. Pure in its arguments.
pub fn make_trial(rule: &Rule, class: Class, index: u32, claim_seed: u64, size: usize, horizon: u64, base: &Baseline) -> Trial {
    let seed = trial_seed(claim_seed, rule, class, index);
    let mut st = seed;
    let n = rule.len() as u8;
    let mut sim = Sim::centred(size, horizon);
    let mut init = Init { cells: vec![], heading: (splitmix_next(&mut st) % 4) as u8 };
    let mut perturb = None;
    match class {
        Class::Blank => init.heading = 0,
        Class::Heading => init.heading = (index % 4) as u8,
        Class::Boundary => {
            init.heading = 0;
            // Odd sizes break the centre symmetry; the start is 16..=512 cells from one edge.
            let s = (size - 1 - 2 * (splitmix_next(&mut st) % (size as u64 / 8)) as usize) | 1;
            let d = 16usize << (splitmix_next(&mut st) % 6);
            let d = d.min(s / 2 - 1);
            let mid = s / 2;
            sim.size = s;
            sim.start = match splitmix_next(&mut st) % 4 {
                0 => (d, mid),
                1 => (s - 1 - d, mid),
                2 => (mid, d),
                _ => (mid, s - 1 - d),
            };
        }
        Class::Patch => {
            let r = 1 + (splitmix_next(&mut st) % 3) as i32;
            init.cells = window_cells(n, &mut st, r, |st, _, _| Some((splitmix_next(st) % n as u64) as u8));
        }
        Class::Mono => {
            let r = 1 + (splitmix_next(&mut st) % 3) as i32;
            let c = 1 + (splitmix_next(&mut st) % (n as u64 - 1)) as u8;
            init.cells = window_cells(n, &mut st, r, |_, _, _| Some(c));
        }
        Class::Half => {
            let c = 1 + (splitmix_next(&mut st) % (n as u64 - 1)) as u8;
            init.cells = window_cells(n, &mut st, 20, |_, x, _| (x < 0).then_some(c));
        }
        Class::Stripe => {
            let vertical = splitmix_next(&mut st).is_multiple_of(2);
            init.cells = window_cells(n, &mut st, 24, |st, x, y| {
                ((if vertical { x } else { y }) == 0).then(|| (splitmix_next(st) % n as u64) as u8)
            });
        }
        Class::Sparse => {
            let density = [0.02, 0.1, 0.3][(splitmix_next(&mut st) % 3) as usize];
            init.cells = window_cells(n, &mut st, 16, |st, _, _| {
                let u = (splitmix_next(st) >> 11) as f64 / (1u64 << 53) as f64;
                (u < density).then(|| 1 + (splitmix_next(st) % (n as u64 - 1)) as u8)
            });
        }
        Class::Obstacle => {
            init.heading = 0;
            let radius = 1 + (splitmix_next(&mut st) % 4) as i32;
            let ps = splitmix_next(&mut st);
            let (at, ahead) = match base.onset {
                Some(o) => {
                    let p = base.period as u64;
                    let lo = o + 4 * p;
                    let hi = (o + (base.run.steps - o) / 2).max(lo + 1);
                    (lo + splitmix_next(&mut st) % (hi - lo), 8 + (splitmix_next(&mut st) % 120) as i32)
                }
                None => (horizon / 8 + splitmix_next(&mut st) % (horizon / 4).max(1), (splitmix_next(&mut st) % 8) as i32),
            };
            perturb = Some(Perturb { at, ahead, radius, seed: ps });
        }
        Class::Adaptive => {
            // The starting patch of a chain; the search itself is `adaptive_chain`.
            init.cells = window_cells(n, &mut st, 3, |st, _, _| Some((splitmix_next(st) % n as u64) as u8));
        }
    }
    Trial { class, index, seed, init, sim, perturb }
}

pub fn run_trial(rule: &Rule, t: &Trial) -> TrialResult {
    TrialResult { trial: t.clone(), run: simulate(rule, &t.init, &t.sim, t.perturb.as_ref()) }
}

/// What the claim would like to see, and how badly the attacker wants to prevent it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Kind {
    /// Every start ends in a confirmed highway (of the baseline's type when `same_canon`).
    Highway,
    /// No start ever ends in a highway.
    Chaotic,
}

/// Attacker's objective for the hill-climb (higher is better for the attacker). Highway claims:
/// delay before escape, with "never escaped" the best. Chaotic claims: a compact pattern
/// (small bounding box) at the horizon is closer to periodic order, a heuristic and nothing more.
fn score(kind: Kind, r: &Run, horizon: u64) -> f64 {
    match kind {
        Kind::Highway => match r.outcome {
            Outcome::Highway(_) => r.steps as f64,
            _ => horizon as f64 * 2.0,
        },
        Kind::Chaotic => match r.outcome {
            Outcome::Highway(_) => f64::INFINITY,
            _ => -(r.extent.0 as f64 * r.extent.1 as f64),
        },
    }
}

/// One hill-climbing chain: mutate a single cell of a radius-3 patch, keep the mutation when the
/// attacker's score does not decrease. Every evaluated candidate is returned (each may itself be
/// a counterexample). Sequential within a chain so the result is deterministic.
pub fn adaptive_chain(rule: &Rule, kind: Kind, chain: u32, evals: u32, claim_seed: u64, size: usize, horizon: u64, base: &Baseline) -> Vec<TrialResult> {
    let n = rule.len() as u64;
    let mut cur = make_trial(rule, Class::Adaptive, chain * evals, claim_seed, size, horizon, base);
    let mut out = vec![run_trial(rule, &cur)];
    let mut best = score(kind, &out[0].run, horizon);
    let mut st = cur.seed;
    for k in 1..evals {
        let mut cand = cur.clone();
        cand.index = chain * evals + k;
        cand.seed = trial_seed(claim_seed, rule, Class::Adaptive, cand.index);
        let mut m: BTreeMap<(i32, i32), u8> = cand.init.cells.iter().copied().collect();
        let p = ((splitmix_next(&mut st) % 7) as i32 - 3, (splitmix_next(&mut st) % 7) as i32 - 3);
        let c = (splitmix_next(&mut st) % n) as u8;
        if c == 0 {
            m.remove(&p);
        } else {
            m.insert(p, c);
        }
        cand.init.cells = m.into_iter().collect();
        let res = run_trial(rule, &cand);
        let s = score(kind, &res.run, horizon);
        if s >= best {
            best = s;
            cur = cand;
        }
        out.push(res);
    }
    out
}

const UNION: [Class; 6] = [Class::Patch, Class::Mono, Class::Half, Class::Stripe, Class::Sparse, Class::Obstacle];
const ELITES: usize = 8;

/// The attacker's score for the evolutionary search. Highway claims: escape step of a baseline-type
/// highway; twice the horizon for a start that never resolved; four times the horizon for a highway of
/// a different type (a counterexample). Chaotic claims fall back to `score`.
pub fn attack_score(kind: Kind, r: &Run, base: &Baseline, horizon: u64) -> f64 {
    match kind {
        Kind::Chaotic => score(kind, r, horizon),
        Kind::Highway => match categorise(r, base) {
            Cat::HwSame => r.steps as f64,
            Cat::HwOther => 4.0 * horizon as f64,
            Cat::Edge | Cat::Unresolved => 2.0 * horizon as f64,
        },
    }
}

/// One draw from the plain random sampler: a uniformly chosen generator among the dense-start classes.
pub fn random_draw(rule: &Rule, idx: u32, seed: u64, size: usize, horizon: u64, base: &Baseline) -> Trial {
    let class = UNION[(mix64(seed ^ idx as u64) % UNION.len() as u64) as usize];
    make_trial(rule, class, idx, seed, size, horizon, base)
}

/// Multi-scale mutation: recolour, delete, add, shift, re-aim, stamp a 3x3 patch, or change the
/// obstacle's timing, distance, size and seed.
fn mutate(rule: &Rule, parent: &Trial, st: &mut u64, idx: u32, claim_seed: u64, size: usize, horizon: u64, base: &Baseline) -> Trial {
    let n = rule.len() as u64;
    let mut t = parent.clone();
    t.class = Class::Adaptive;
    t.index = idx;
    t.seed = trial_seed(claim_seed, rule, Class::Adaptive, idx);
    let mut m: BTreeMap<(i32, i32), u8> = t.init.cells.iter().copied().collect();
    let pick = |st: &mut u64, m: &BTreeMap<(i32, i32), u8>| -> Option<(i32, i32)> {
        (!m.is_empty()).then(|| *m.keys().nth((splitmix_next(st) % m.len() as u64) as usize).unwrap())
    };
    let pos = |st: &mut u64| ((splitmix_next(st) % 25) as i32 - 12, (splitmix_next(st) % 25) as i32 - 12);
    for _ in 0..1 + splitmix_next(st) % 3 {
        match splitmix_next(st) % 7 {
            0 => {
                if let Some(p) = pick(st, &m) {
                    let col = (splitmix_next(st) % n) as u8;
                    if col == 0 { m.remove(&p); } else { m.insert(p, col); }
                }
            }
            1 => {
                if let Some(p) = pick(st, &m) { m.remove(&p); }
            }
            2 => {
                let p = pos(st);
                m.insert(p, 1 + (splitmix_next(st) % (n - 1)) as u8);
            }
            3 => {
                let (dx, dy) = ((splitmix_next(st) % 5) as i32 - 2, (splitmix_next(st) % 5) as i32 - 2);
                m = m.into_iter().map(|((x, y), v)| ((x + dx, y + dy), v)).filter(|((x, y), _)| x.abs() <= 40 && y.abs() <= 40).collect();
            }
            4 => t.init.heading = (splitmix_next(st) % 4) as u8,
            5 => {
                let (cx, cy) = pos(st);
                for dy in 0..3 {
                    for dx in 0..3 {
                        let col = (splitmix_next(st) % n) as u8;
                        if col == 0 { m.remove(&(cx + dx, cy + dy)); } else { m.insert((cx + dx, cy + dy), col); }
                    }
                }
            }
            _ => {
                let scale = (base.period as i64 * 4).max(1000);
                t.perturb = match (&t.perturb, splitmix_next(st) % 5) {
                    (None, _) | (Some(_), 0) => make_trial(rule, Class::Obstacle, idx, claim_seed, size, horizon, base).perturb,
                    (Some(p), 1) => Some(Perturb { at: (p.at as i64 + (splitmix_next(st) % (2 * scale as u64 + 1)) as i64 - scale).max(1) as u64, ..p.clone() }),
                    (Some(p), 2) => Some(Perturb { ahead: (p.ahead + (splitmix_next(st) % 17) as i32 - 8).clamp(0, 200), ..p.clone() }),
                    (Some(p), 3) => Some(Perturb { radius: (p.radius + (splitmix_next(st) % 3) as i32 - 1).clamp(0, 6), seed: splitmix_next(st), ..p.clone() }),
                    (Some(_), _) => None,
                };
            }
        }
    }
    t.init.cells = m.into_iter().collect();
    t
}

/// Evolutionary attack chain: the first quarter of the budget is plain random draws, then a (mu + lambda)
/// search (mu = 8 elites) mutates uniformly chosen elites. With `immigrate`, a quarter of the children are
/// fresh random draws instead, which keeps rare structures (a start that gives a different highway) from
/// being starved by delay-ranking. Equal-budget results against random sampling and the one-cell hill-climb:
/// `experiments/archive/2026-10-falsify-adaptive-search`. `salt` separates the random streams of different arms.
pub fn evolve_chain(rule: &Rule, kind: Kind, rep: u32, budget: u32, immigrate: bool, claim_seed: u64, salt: u64, size: usize, horizon: u64, base: &Baseline) -> Vec<TrialResult> {
    let drawn_seed = claim_seed ^ salt;
    let mut st = mix64(claim_seed ^ salt ^ rep as u64);
    let seeding = budget / 4;
    let mut pop: Vec<(f64, Trial)> = vec![];
    let mut out = Vec::with_capacity(budget as usize);
    for k in 0..budget {
        let idx = rep * budget + k;
        let fresh = immigrate && k >= seeding && splitmix_next(&mut st).is_multiple_of(4);
        let t = if k < seeding || fresh {
            random_draw(rule, idx, drawn_seed, size, horizon, base)
        } else {
            let parent = pop[(splitmix_next(&mut st) % pop.len() as u64) as usize].1.clone();
            mutate(rule, &parent, &mut st, idx, claim_seed, size, horizon, base)
        };
        let res = run_trial(rule, &t);
        pop.push((attack_score(kind, &res.run, base, horizon), t));
        out.push(res);
        if k + 1 >= seeding || pop.len() > ELITES {
            // stable sort keeps the older of equal scores
            pop.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap());
            pop.truncate(ELITES);
        }
    }
    out
}

// ---------------------------------------------------------------- verdicts

/// How one trial relates to the baseline highway type.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Cat {
    HwSame,
    HwOther,
    Edge,
    Unresolved,
}

pub fn categorise(r: &Run, base: &Baseline) -> Cat {
    match r.outcome {
        Outcome::Highway(hw) if Some(canon(hw)) == base.canon => Cat::HwSame,
        Outcome::Highway(_) => Cat::HwOther,
        Outcome::EdgeEscape => Cat::Edge,
        Outcome::Unresolved => Cat::Unresolved,
    }
}

#[derive(Clone, Debug)]
pub struct Claim {
    pub id: String,
    pub kind: Kind,
    pub rule: Rule,
    pub universal: bool,
    pub p_min: f64,
    pub same_canon: bool,
    pub classes: Vec<Class>,
    pub trials: u32,
    pub horizon: u64,
    pub ladder: u32,
    pub size: usize,
    pub seed: u64,
    pub chains: u32,
    pub evals: u32,
    pub registered: String,
}

impl Claim {
    /// One claim per line: whitespace-separated `key=value`; `#` starts a comment.
    pub fn parse(line: &str) -> Result<Claim, String> {
        let mut kv = BTreeMap::new();
        for token in line.split('#').next().unwrap_or("").split_whitespace() {
            let (key, value) = token.split_once('=').ok_or(format!("expected key=value, got {token:?}"))?;
            if value.is_empty() || kv.insert(key, value).is_some() {
                return Err(format!("empty or duplicate field {key}"));
            }
        }
        let get = |k: &str| kv.get(k).copied().ok_or(format!("missing {k}="));
        let num = |k: &str, d: &str| -> Result<f64, String> {
            kv.get(k).copied().unwrap_or(d).parse::<f64>().map_err(|e| format!("{k}: {e}"))
        };
        let kind = match get("kind")? {
            "highway" => Kind::Highway,
            "chaotic" => Kind::Chaotic,
            k => return Err(format!("kind must be highway|chaotic, got {k}")),
        };
        let classes = match kv.get("attacks").copied().unwrap_or("all") {
            "all" => Class::ALL.to_vec(),
            s => s.split(',').map(|c| Class::parse(c).ok_or(format!("unknown attack {c}"))).collect::<Result<_, _>>()?,
        };
        let allowed_unknown = ["registered"];
        for k in kv.keys() {
            if !["id", "kind", "rule", "quantifier", "p_min", "same_canon", "attacks", "trials", "horizon", "ladder", "size", "seed", "chains", "evals"]
                .contains(k)
                && !allowed_unknown.contains(k)
            {
                return Err(format!("unknown key {k}"));
            }
        }
        let integer = |k: &str, d: &str| -> Result<u64, String> {
            kv.get(k).copied().unwrap_or(d).parse::<u64>().map_err(|e| format!("{k}: {e}"))
        };
        let count = |k: &str, d: &str| -> Result<u32, String> {
            u32::try_from(integer(k, d)?).map_err(|_| format!("{k} exceeds u32"))
        };
        let universal = match kv.get("quantifier").copied().unwrap_or("universal") {
            "universal" => true,
            "probabilistic" => false,
            _ => return Err("quantifier must be universal|probabilistic".into()),
        };
        let same_canon = match kv.get("same_canon").copied().unwrap_or("true") {
            "true" => true,
            "false" => false,
            _ => return Err("same_canon must be true|false".into()),
        };
        let claim = Claim {
            id: get("id")?.to_string(),
            kind,
            rule: get("rule")?.parse()?,
            universal,
            p_min: num("p_min", "0.99")?,
            same_canon,
            classes,
            trials: count("trials", "64")?,
            horizon: integer("horizon", "1000000")?,
            ladder: count("ladder", "2")?,
            size: usize::try_from(integer("size", "2048")?).map_err(|_| "size exceeds usize")?,
            seed: integer("seed", "1")?,
            chains: count("chains", "4")?,
            evals: count("evals", "200")?,
            // The prediction must be time-stamped before the attack; the git check lives in the binary.
            registered: get("registered")?.to_string(),
        };
        if !claim.id.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_') {
            return Err("id must contain only ASCII letters, digits, '-' or '_'".into());
        }
        if claim.rule.len() < 2 || claim.rule.len() > 255 || claim.size < 64 || claim.size > i32::MAX as usize {
            return Err("requires 2..255 colours and board size 64..i32::MAX".into());
        }
        if claim.trials == 0 || claim.horizon == 0 || claim.chains == 0 || claim.evals == 0
            || claim.chains.checked_mul(claim.evals).is_none()
            || claim.size.checked_mul(claim.size).is_none()
            || 4u64.checked_pow(claim.ladder).and_then(|m| claim.horizon.checked_mul(m)).is_none()
        {
            return Err("budgets must be positive and their products must not overflow".into());
        }
        if !claim.p_min.is_finite() || !(0.0..=1.0).contains(&claim.p_min) {
            return Err("p_min must be finite and in [0,1]".into());
        }
        Ok(claim)
    }
}

/// Every trial of a claim, in a fixed order, evaluated in parallel by the caller if desired.
/// Controls are always included so the instrument is checked on every claim.
pub fn plan(claim: &Claim, base: &Baseline) -> Vec<(Class, u32)> {
    let mut v = vec![];
    for &c in Class::ALL.iter().filter(|c| claim.classes.contains(c) || c.is_control() || **c == Class::Blank) {
        match c {
            Class::Blank => v.push((c, 0)),
            Class::Heading => v.extend((0..4).map(|i| (c, i))),
            Class::Adaptive => {}
            Class::Obstacle if base.canon.is_none() && claim.kind == Kind::Highway => {}
            _ => v.extend((0..claim.trials).map(|i| (c, i))),
        }
    }
    v
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Verdict {
    /// A reproduced counterexample exists.
    Falsified,
    /// The instrument controls failed; nothing about the rule can be concluded.
    Invalid,
    /// No counterexample, but some starts never resolved within the horizon (highway claims).
    Unsupported,
    /// No counterexample at this horizon. Not a proof.
    Survived,
}

#[derive(Clone, Debug, Default)]
pub struct ClassRow {
    pub class: Option<Class>,
    pub n: u64,
    pub hw_same: u64,
    pub hw_other: u64,
    pub edge: u64,
    pub unresolved: u64,
}

#[derive(Clone, Debug)]
pub struct Report {
    pub verdict: Verdict,
    pub reasons: Vec<String>,
    pub rows: Vec<ClassRow>,
    /// (horizon, number of non-control trials with a confirmed highway by then, of n).
    pub rungs: Vec<(u64, u64, u64)>,
    /// Indices into the result list of trials that falsify the claim.
    pub counterexamples: Vec<usize>,
    pub success_ci: Option<(f64, f64)>,
    /// Chaotic claim whose blank-board highway starts after the claim's stated horizon.
    pub late: bool,
}

/// Exact (Clopper-Pearson) two-sided interval for k successes in n trials.
pub fn clopper_pearson(k: u64, n: u64, alpha: f64) -> (f64, f64) {
    if n == 0 {
        return (0.0, 1.0);
    }
    let lnf: Vec<f64> = std::iter::once(0.0)
        .chain((1..=n).scan(0.0, |a, i| {
            *a += (i as f64).ln();
            Some(*a)
        }))
        .collect();
    // P(X <= j | p)
    let cdf = |j: u64, p: f64| -> f64 {
        (0..=j)
            .map(|i| (lnf[n as usize] - lnf[i as usize] - lnf[(n - i) as usize] + i as f64 * p.ln() + (n - i) as f64 * (1.0 - p).ln()).exp())
            .sum()
    };
    let solve = |f: &dyn Fn(f64) -> f64, target: f64, increasing: bool| -> f64 {
        let (mut lo, mut hi) = (1e-12, 1.0 - 1e-12);
        for _ in 0..80 {
            let mid = 0.5 * (lo + hi);
            if (f(mid) > target) == increasing {
                hi = mid;
            } else {
                lo = mid;
            }
        }
        0.5 * (lo + hi)
    };
    // upper: P(X <= k | p) = alpha/2, decreasing in p
    let upper = if k >= n { 1.0 } else { solve(&|p| cdf(k, p), alpha / 2.0, false) };
    // lower: P(X >= k | p) = 1 - P(X <= k-1 | p) = alpha/2, increasing in p
    let lower = if k == 0 { 0.0 } else { solve(&|p| 1.0 - cdf(k - 1, p), alpha / 2.0, true) };
    (lower, upper)
}

pub fn evaluate(claim: &Claim, base: &Baseline, results: &[TrialResult]) -> Report {
    let mut rows: BTreeMap<Class, ClassRow> = BTreeMap::new();
    let mut counterexamples = vec![];
    let mut reasons = vec![];
    let mut invalid = false;
    let mut unresolved_claim = 0u64;
    let base_cat = categorise(&base.run, base);
    for (i, r) in results.iter().enumerate() {
        let cat = categorise(&r.run, base);
        let row = rows.entry(r.trial.class).or_default();
        row.class = Some(r.trial.class);
        row.n += 1;
        match cat {
            Cat::HwSame => row.hw_same += 1,
            Cat::HwOther => row.hw_other += 1,
            Cat::Edge => row.edge += 1,
            Cat::Unresolved => row.unresolved += 1,
        }
        if r.trial.class.is_control() {
            // Blank start on any geometry: dynamics identical to the baseline until the first edge hit.
            if r.trial.class == Class::Heading && cat != base_cat {
                invalid = true;
                reasons.push(format!("control heading#{}: {:?} but baseline {:?}", r.trial.index, cat, base_cat));
            }
            if matches!(cat, Cat::HwOther) || (cat == Cat::HwSame && base.canon.is_none()) {
                invalid = true;
                reasons.push(format!("control {}#{}: confirmed highway {:?} disagrees with baseline", r.trial.class.name(), r.trial.index, r.run.outcome));
            }
            continue;
        }
        let falsifies = match claim.kind {
            Kind::Chaotic => matches!(r.run.outcome, Outcome::Highway(_)),
            Kind::Highway => cat == Cat::HwOther && claim.same_canon,
        };
        if falsifies {
            counterexamples.push(i);
        }
        if claim.kind == Kind::Highway && matches!(cat, Cat::Edge | Cat::Unresolved) {
            unresolved_claim += 1;
        }
    }
    let attack: Vec<&TrialResult> = results.iter().filter(|r| !r.trial.class.is_control()).collect();
    // The claim's `horizon` is what its author looked at; trials ran to horizon * 4^ladder.
    // Lateness is judged on the claim as stated (the blank board), whose onset is exact. A trial's
    // escape step is not an onset: it adds the board-crossing time (about size/2 / speed), so
    // escapes by h below are a conservative count of highways that exist by h.
    let late = claim.kind == Kind::Chaotic && base.onset.is_some_and(|o| o > claim.horizon);
    if late {
        reasons.push(format!(
            "horizon-sensitive: the blank-board highway starts at step {} > stated horizon {}",
            base.onset.unwrap(),
            claim.horizon
        ));
    }
    let rungs = (0..=claim.ladder)
        .map(|k| {
            let h = claim.horizon * 4u64.pow(k);
            let hits = attack.iter().filter(|r| matches!(r.run.outcome, Outcome::Highway(_)) && r.run.steps <= h).count() as u64;
            (h, hits, attack.len() as u64)
        })
        .collect();
    // Correlated adaptive candidates and different attack distributions are not IID trials.
    let success_ci = None;
    let verdict = if invalid {
        Verdict::Invalid
    } else if !claim.universal {
        reasons.push("probabilistic claims require a separately registered IID sampling distribution; pooled attacks cannot estimate p_min".into());
        Verdict::Unsupported
    } else if !counterexamples.is_empty() {
        Verdict::Falsified
    } else if unresolved_claim > 0 {
        reasons.push(format!("{unresolved_claim} attack trials did not end in a highway by the horizon (not a refutation)"));
        Verdict::Unsupported
    } else {
        Verdict::Survived
    };
    Report { verdict, reasons, rows: rows.into_values().collect(), rungs, counterexamples, success_ci, late }
}

/// Greedy delta-debugging: drop cells while `still` holds. At most `budget` evaluations.
pub fn shrink(init: &Init, budget: u32, mut still: impl FnMut(&Init) -> bool) -> Init {
    let mut cur = init.clone();
    let mut used = 0;
    let mut chunk = (cur.cells.len() / 2).max(1);
    loop {
        let mut i = 0;
        while i < cur.cells.len() && used < budget {
            let mut cand = cur.clone();
            cand.cells.drain(i..(i + chunk).min(cur.cells.len()));
            used += 1;
            if still(&cand) {
                cur = cand;
            } else {
                i += chunk;
            }
        }
        if chunk == 1 || used >= budget {
            return cur;
        }
        chunk = (chunk / 2).max(1);
    }
}

/// Re-run a trial on a different board geometry (even size + 1, start shifted off-centre); a real
/// counterexample must not depend on the board.
pub fn on_other_geometry(t: &Trial) -> Trial {
    let mut u = t.clone();
    u.sim.size = t.sim.size + 1 + 2 * (t.sim.size % 3);
    u.sim.start = (u.sim.size / 2 + 5, u.sim.size / 2 - 3);
    u.sim.history = t.sim.history + 1000;
    if t.class == Class::Boundary {
        u.sim = t.sim.clone();
    }
    u
}

// Display helpers shared by the binary and tests.
pub fn cells_to_string(cells: &[((i32, i32), u8)]) -> String {
    cells.iter().map(|((x, y), c)| format!("{x}:{y}:{c}")).collect::<Vec<_>>().join(";")
}

pub fn cells_from_string(s: &str) -> Result<Vec<((i32, i32), u8)>, String> {
    if s.is_empty() || s == "-" {
        return Ok(vec![]);
    }
    s.split(';')
        .map(|t| {
            let v: Vec<&str> = t.split(':').collect();
            match v[..] {
                [x, y, c] => Ok(((x.parse().map_err(|e| format!("{e}"))?, y.parse().map_err(|e| format!("{e}"))?), c.parse().map_err(|e| format!("{e}"))?)),
                _ => Err(format!("bad cell {t:?}")),
            }
        })
        .collect()
}
