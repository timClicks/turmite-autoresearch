//! Walkers the probe can drive. Each owns the rule for how a cell's state and
//! the walker's heading change on a visit; the probe owns the bookkeeping.
//!
//! - `AntWalker`: the generalised Langton's ant. Turn relative to heading by
//!   rule[colour], then advance the colour. Board starts blank.
//! - `Rotor`: the Eulerian (rotor-router) walker of Priezzhev et al. and Kapri &
//!   Dhar: rotate the cell's arrow 90 degrees clockwise, then step along it.
//!   Arrows start i.i.d. uniform, derived from a seed and the cell position so
//!   that independent implementations agree.
//! - `RandomWalk`: simple random walk, a negative control.
//!
//! Directions use the crate's encoding: 0 N, 1 E, 2 S, 3 W (screen coordinates,
//! so N -> E -> S -> W is clockwise).

use crate::Rule;

/// SplitMix64 finaliser: a good 64-bit mixing function.
pub fn mix64(mut z: u64) -> u64 {
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

/// Next value of a SplitMix64 stream.
pub fn splitmix_next(state: &mut u64) -> u64 {
    *state = state.wrapping_add(0x9E37_79B9_7F4A_7C15);
    mix64(*state)
}

/// The initial arrow (0..4) at (x, y), relative to the start, for a seed.
pub fn initial_arrow(seed: u64, x: i64, y: i64) -> u8 {
    let key = ((x as i32 as u32 as u64) << 32) | (y as i32 as u32 as u64);
    (mix64(mix64(seed ^ 0xA076_1D64_78BD_642F) ^ key) & 3) as u8
}

pub trait Walker {
    /// Whether unvisited cells start in a non-zero, position-dependent state.
    const RANDOM_INIT: bool;
    fn initial_cell(&self, x: i64, y: i64) -> u8;
    /// Update the cell under the walker and its heading for one step.
    fn step(&mut self, cell: &mut u8, heading: &mut u8);
}

#[derive(Clone)]
pub struct AntWalker {
    turn: Vec<u8>,
    next: Vec<u8>,
}

impl AntWalker {
    pub fn new(rule: &Rule) -> AntWalker {
        let n = rule.len();
        AntWalker {
            turn: rule.0.iter().map(|t| t.delta()).collect(),
            next: (0..n).map(|i| ((i + 1) % n) as u8).collect(),
        }
    }
}

impl Walker for AntWalker {
    const RANDOM_INIT: bool = false;
    fn initial_cell(&self, _: i64, _: i64) -> u8 {
        0
    }
    #[inline(always)]
    fn step(&mut self, cell: &mut u8, heading: &mut u8) {
        let c = *cell as usize;
        *heading = (*heading + self.turn[c]) & 3;
        *cell = self.next[c];
    }
}

#[derive(Clone)]
pub struct Rotor {
    pub seed: u64,
}

impl Walker for Rotor {
    const RANDOM_INIT: bool = true;
    fn initial_cell(&self, x: i64, y: i64) -> u8 {
        initial_arrow(self.seed, x, y)
    }
    #[inline(always)]
    fn step(&mut self, cell: &mut u8, heading: &mut u8) {
        *cell = (*cell + 1) & 3;
        *heading = *cell;
    }
}

#[derive(Clone)]
pub struct RandomWalk {
    pub state: u64,
}

/// One cookie per site: first departure follows its arrow with probability
/// `bias`, otherwise uniform; later departures are uniform. Random arrows
/// remove ensemble drift but do not make individual trajectories isotropic.
pub struct CookieWalk {
    pub seed: u64,
    pub state: u64,
    pub bias_q32: u64,
    pub random_arrows: bool,
}

impl CookieWalk {
    pub fn new(seed: u64, bias: f64, random_arrows: bool) -> Self {
        assert!(bias.is_finite() && (0.0..=1.0).contains(&bias));
        Self { seed, state: seed, bias_q32: (bias * 4294967296.0) as u64, random_arrows }
    }
}

impl Walker for CookieWalk {
    const RANDOM_INIT: bool = true;
    fn initial_cell(&self, x: i64, y: i64) -> u8 {
        if self.random_arrows { initial_arrow(self.seed, x, y) } else { 1 }
    }
    fn step(&mut self, cell: &mut u8, heading: &mut u8) {
        let r = splitmix_next(&mut self.state);
        *heading = if *cell < 4 && (r >> 32) < self.bias_q32 { *cell } else { (r & 3) as u8 };
        *cell |= 4;
    }
}

/// Linear reinforcement of undirected edge weights, initially one. Position
/// is private walker state because the cell API cannot represent shared edges.
pub struct EdgeReinforcedWalk {
    state: u64,
    increment: u64,
    pos: (i64, i64),
    weights: std::collections::HashMap<((i64, i64), (i64, i64)), u64>,
}

impl EdgeReinforcedWalk {
    pub fn new(seed: u64, increment: u64) -> Self {
        Self { state: seed, increment, pos: (0, 0), weights: std::collections::HashMap::new() }
    }
}

impl Walker for EdgeReinforcedWalk {
    const RANDOM_INIT: bool = false;
    fn initial_cell(&self, _: i64, _: i64) -> u8 { 0 }
    fn step(&mut self, _: &mut u8, heading: &mut u8) {
        let edges = crate::DIRS.map(|(dx, dy)| {
            let q = (self.pos.0 + dx as i64, self.pos.1 + dy as i64);
            if self.pos < q { (self.pos, q) } else { (q, self.pos) }
        });
        let weights = edges.map(|e| *self.weights.get(&e).unwrap_or(&1));
        let total: u64 = weights.iter().sum();
        // Rejection avoids modulo bias, with a fixed N,E,S,W candidate order.
        let threshold = total.wrapping_neg() % total;
        let mut ticket = loop {
            let r = splitmix_next(&mut self.state);
            if r >= threshold { break r % total; }
        };
        for d in 0..4 {
            if ticket < weights[d] {
                *heading = d as u8;
                let weight = self.weights.entry(edges[d]).or_insert(1);
                *weight = weight.checked_add(self.increment).expect("edge weight overflow");
                let (dx, dy) = crate::DIRS[d];
                self.pos = (self.pos.0 + dx as i64, self.pos.1 + dy as i64);
                return;
            }
            ticket -= weights[d];
        }
        unreachable!()
    }
}

impl Walker for RandomWalk {
    const RANDOM_INIT: bool = false;
    fn initial_cell(&self, _: i64, _: i64) -> u8 {
        0
    }
    #[inline(always)]
    fn step(&mut self, _cell: &mut u8, heading: &mut u8) {
        *heading = (splitmix_next(&mut self.state) & 3) as u8;
    }
}

/// A generalised ant whose board starts blank except for a small square patch
/// of random colours around the start. Different seeds give independent runs
/// of the same rule, which measures how much a fitted exponent scatters for
/// one rule.
#[derive(Clone)]
pub struct PatchedAnt {
    pub ant: AntWalker,
    pub n: u8,
    pub seed: u64,
    /// Half-width of the random patch.
    pub radius: i64,
}

impl PatchedAnt {
    pub fn new(rule: &Rule, seed: u64, radius: i64) -> PatchedAnt {
        PatchedAnt { ant: AntWalker::new(rule), n: rule.len() as u8, seed, radius }
    }
}

impl Walker for PatchedAnt {
    const RANDOM_INIT: bool = true;
    fn initial_cell(&self, x: i64, y: i64) -> u8 {
        if x.abs() <= self.radius && y.abs() <= self.radius {
            let key = ((x as i32 as u32 as u64) << 32) | (y as i32 as u32 as u64);
            (mix64(mix64(self.seed ^ 0x5851_F42D_4C95_7F2D) ^ key) % self.n as u64) as u8
        } else {
            0
        }
    }
    #[inline(always)]
    fn step(&mut self, cell: &mut u8, heading: &mut u8) {
        self.ant.step(cell, heading);
    }
}

/// Rotor walker whose initial arrows are biased towards north (C2 of the 2026-10-13 frontier):
/// with probability `bias` (a fraction of 2^32, so the run is exactly reproducible) the arrow is north,
/// otherwise uniform. `bias = 0` is not bit-identical to `Rotor` (different hash stream), only equal in law.
pub struct BiasedRotor {
    pub seed: u64,
    pub bias_q32: u64,
}

impl BiasedRotor {
    pub fn new(seed: u64, bias: f64) -> BiasedRotor {
        BiasedRotor { seed, bias_q32: (bias * 4294967296.0) as u64 }
    }
}

/// The initial arrow of `BiasedRotor` at (x, y); shared with the brute-force test.
pub fn biased_arrow(seed: u64, bias_q32: u64, x: i64, y: i64) -> u8 {
    let key = ((x as i32 as u32 as u64) << 32) | (y as i32 as u32 as u64);
    let h = mix64(mix64(seed ^ 0x3C6E_F372_FE94_F82B) ^ key);
    if (h >> 32) < bias_q32 { 0 } else { (h & 3) as u8 }
}

impl Walker for BiasedRotor {
    const RANDOM_INIT: bool = true;
    fn initial_cell(&self, x: i64, y: i64) -> u8 {
        biased_arrow(self.seed, self.bias_q32, x, y)
    }
    #[inline(always)]
    fn step(&mut self, cell: &mut u8, heading: &mut u8) {
        *cell = (*cell + 1) & 3;
        *heading = *cell;
    }
}

/// Generalised ant on a sparse random background (B2b of the 2026-10-13 frontier): each cell independently starts in a uniformly random
/// non-zero colour with probability `density` (a fraction of 2^32, so runs are exactly reproducible), otherwise blank.
pub struct SparseBgAnt {
    pub ant: AntWalker,
    pub n: u8,
    pub seed: u64,
    pub density_q32: u64,
}

impl SparseBgAnt {
    pub fn new(rule: &Rule, seed: u64, density: f64) -> SparseBgAnt {
        SparseBgAnt { ant: AntWalker::new(rule), n: rule.len() as u8, seed, density_q32: (density * 4294967296.0) as u64 }
    }
}

/// Initial colour of `SparseBgAnt` at (x, y); shared with the brute-force test.
pub fn sparse_bg_colour(seed: u64, density_q32: u64, n: u8, x: i64, y: i64) -> u8 {
    let key = ((x as i32 as u32 as u64) << 32) | (y as i32 as u32 as u64);
    let h = mix64(mix64(seed ^ 0x7F4A_7C15_9E37_79B9) ^ key);
    if (h >> 32) < density_q32 { 1 + ((h & 0xFFFF_FFFF) % (n as u64 - 1)) as u8 } else { 0 }
}

impl Walker for SparseBgAnt {
    const RANDOM_INIT: bool = true;
    fn initial_cell(&self, x: i64, y: i64) -> u8 {
        sparse_bg_colour(self.seed, self.density_q32, self.n, x, y)
    }
    #[inline(always)]
    fn step(&mut self, cell: &mut u8, heading: &mut u8) {
        self.ant.step(cell, heading);
    }
}

/// Memoryless persistent walker (A1d): every step turns right with
/// probability `q` and left otherwise, independent of the board. This is the
/// "independent turns" model of the mixing test, and it has no memory in the
/// environment, so it separates what a persistent random walk alone explains
/// from what the ant's colour field adds.
pub struct PersistentWalk {
    pub state: u64,
    /// Turn-right probability scaled to 2^32.
    pub q32: u64,
}

impl PersistentWalk {
    pub fn new(seed: u64, q: f64) -> PersistentWalk {
        PersistentWalk { state: seed, q32: (q * 4294967296.0) as u64 }
    }
}

impl Walker for PersistentWalk {
    const RANDOM_INIT: bool = false;
    fn initial_cell(&self, _: i64, _: i64) -> u8 {
        0
    }
    #[inline(always)]
    fn step(&mut self, _cell: &mut u8, heading: &mut u8) {
        let r = (splitmix_next(&mut self.state) >> 32) < self.q32;
        *heading = (*heading + if r { 1 } else { 3 }) & 3;
    }
}

/// Rotor with memory noise (A1 Arm B): as `Rotor`, but with probability `eps`
/// per visit the new arrow is uniform random instead of the next clockwise one.
/// eps = 0 is the rotor; eps = 1 is a memoryless random walk that never turns
/// back on its own board.
pub struct NoisyRotor {
    pub seed: u64,
    pub state: u64,
    pub eps32: u64,
}

impl NoisyRotor {
    pub fn new(seed: u64, eps: f64) -> NoisyRotor {
        NoisyRotor { seed, state: mix64(seed ^ 0x2545_F491_4F6C_DD1D), eps32: (eps * 4294967296.0) as u64 }
    }
}

impl Walker for NoisyRotor {
    const RANDOM_INIT: bool = true;
    fn initial_cell(&self, x: i64, y: i64) -> u8 {
        initial_arrow(self.seed, x, y)
    }
    #[inline(always)]
    fn step(&mut self, cell: &mut u8, heading: &mut u8) {
        let r = splitmix_next(&mut self.state);
        *cell = if (r >> 32) < self.eps32 { (r & 3) as u8 } else { (*cell + 1) & 3 };
        *heading = *cell;
    }
}

/// Ant with turn noise split by cell type (wall-vs-memory experiment,
/// `experiments/active/2026-10-wall-vs-memory/`). On a cell it stands on for the
/// first time (fresh) the turn is randomised with probability `ef`, elsewhere
/// with probability `ev`; the colour advances as in the ant either way. A
/// fresh cell is one never departed from, tracked in bit 7 so that a revisited
/// cell back at colour 0 is not mistaken for fresh ground.
///
/// One SplitMix64 draw per step: the low 32 bits decide whether the step is
/// noisy and the high 32 bits pick R (below 2^31) or L, the same test as
/// `PersistentWalk` at q = 0.5. So `ev = ef = 1` is `PersistentWalk::new(seed, 0.5)`
/// step for step, and `ev = 1, ef = 0` is the same trajectory for every rule
/// that turns R on colour 0 (the hybrid wall walker).
pub struct HybridWalker {
    turn: Vec<u8>,
    next: Vec<u8>,
    state: u64,
    ev32: u64,
    ef32: u64,
}

const DEPARTED: u8 = 0x80;

/// Specified noise semantics: a step is noisy iff the low 32 bits of the draw are strictly
/// below `floor(eps * 2^32)`. So `eps = 1` is always noisy (threshold 2^32) and a non-dyadic
/// `eps` has probability `floor(eps * 2^32) / 2^32`, up to 2^-32 below `eps`.
pub fn noise_threshold32(eps: f64) -> u64 {
    (eps * 4294967296.0).floor() as u64
}

impl HybridWalker {
    pub fn new(rule: &Rule, seed: u64, ev: f64, ef: f64) -> HybridWalker {
        let n = rule.len();
        assert!(n < DEPARTED as usize);
        assert!((0.0..=1.0).contains(&ev) && (0.0..=1.0).contains(&ef));
        HybridWalker {
            turn: rule.0.iter().map(|t| t.delta()).collect(),
            next: (0..n).map(|i| ((i + 1) % n) as u8).collect(),
            state: seed,
            ev32: noise_threshold32(ev),
            ef32: noise_threshold32(ef),
        }
    }
}

impl Walker for HybridWalker {
    const RANDOM_INIT: bool = false;
    fn initial_cell(&self, _: i64, _: i64) -> u8 {
        0
    }
    #[inline(always)]
    fn step(&mut self, cell: &mut u8, heading: &mut u8) {
        let r = splitmix_next(&mut self.state);
        let c = (*cell & !DEPARTED) as usize;
        let eps32 = if *cell & DEPARTED == 0 { self.ef32 } else { self.ev32 };
        let turn = if (r & 0xFFFF_FFFF) < eps32 { if (r >> 32) < 1 << 31 { 1 } else { 3 } } else { self.turn[c] };
        *heading = (*heading + turn) & 3;
        *cell = self.next[c] | DEPARTED;
    }
}

/// Multi-state turmite (`ext::Turmite`) as a probe/shape walker: same table semantics as
/// `ext::SqSim` (write colour, quarter-turn clockwise, next state), blank board, heading north.
pub struct TurmiteWalker {
    tm: crate::ext::Turmite,
    state: u8,
}

impl TurmiteWalker {
    pub fn new(tm: crate::ext::Turmite) -> TurmiteWalker {
        TurmiteWalker { tm, state: 0 }
    }
}

impl Walker for TurmiteWalker {
    const RANDOM_INIT: bool = false;
    fn initial_cell(&self, _: i64, _: i64) -> u8 {
        0
    }
    #[inline(always)]
    fn step(&mut self, cell: &mut u8, heading: &mut u8) {
        let (w, turn, ns) = self.tm.table[self.state as usize * self.tm.colours + *cell as usize];
        *cell = w;
        self.state = ns;
        *heading = (*heading + turn) & 3;
    }
}
