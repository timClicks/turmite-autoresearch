//! `HybridWalker` (wall-vs-memory experiment) against an independent sparse reference written
//! from the README semantics, plus the three exact corner identities the experiment relies on:
//! no noise is the ant, full noise is `PersistentWalk` at q = 0.5, and revisit-only noise is the
//! same trajectory for every rule that turns R on colour 0.
use proptest::prelude::*;
use std::collections::{HashMap, HashSet};
use turmite::probe::{probe, probe_walker};
use turmite::reference::Ant;
use turmite::walkers::{HybridWalker, PersistentWalk, Walker, noise_threshold32, splitmix_next};
use turmite::{DIRS, Rule};

/// Sparse reference: colours and the set of cells departed from, kept apart.
struct RefHybrid {
    rule: Rule,
    colours: HashMap<(i32, i32), usize>,
    departed: HashSet<(i32, i32)>,
    pos: (i32, i32),
    heading: u8,
    rng: u64,
    ev: f64,
    ef: f64,
}

impl RefHybrid {
    fn step(&mut self) {
        let r = splitmix_next(&mut self.rng);
        let u_dir = (r >> 32) as f64 / 4294967296.0;
        let fresh = !self.departed.contains(&self.pos);
        let eps = if fresh { self.ef } else { self.ev };
        // Specified integer semantics (see `noise_threshold32`), restated here independently of
        // the walker: noisy iff low32 < floor(eps * 2^32).
        let noisy = (r & 0xFFFF_FFFF) < (eps * 4294967296.0).floor() as u64;
        let c = *self.colours.get(&self.pos).unwrap_or(&0);
        let turn = if noisy { if u_dir < 0.5 { 1 } else { 3 } } else { self.rule.0[c].delta() };
        self.heading = (self.heading + turn) % 4;
        self.colours.insert(self.pos, (c + 1) % self.rule.len());
        self.departed.insert(self.pos);
        let (dx, dy) = DIRS[self.heading as usize];
        self.pos = (self.pos.0 + dx, self.pos.1 + dy);
    }
}

fn rule_strategy() -> impl Strategy<Value = Rule> {
    (2usize..=12).prop_flat_map(|n| (0u32..(1 << n)).prop_map(move |b| Rule::from_bits(b, n)))
}

fn eps_strategy() -> impl Strategy<Value = f64> {
    prop_oneof![Just(0.0), Just(0.01), Just(0.1), Just(0.5), Just(1.0), 0.0f64..=1.0]
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, rng_seed: proptest::test_runner::RngSeed::Fixed(20261026), ..ProptestConfig::default() })]

    #[test]
    fn matches_sparse_reference(rule in rule_strategy(), seed in any::<u64>(), ev in eps_strategy(), ef in eps_strategy()) {
        let mut w = HybridWalker::new(&rule, seed, ev, ef);
        let mut r = RefHybrid { rule, colours: HashMap::new(), departed: HashSet::new(), pos: (0, 0), heading: 0, rng: seed, ev, ef };
        let mut cells: HashMap<(i32, i32), u8> = HashMap::new();
        let (mut pos, mut h) = ((0i32, 0i32), 0u8);
        for _ in 0..20_000 {
            let cell = cells.entry(pos).or_insert_with(|| w.initial_cell(pos.0 as i64, pos.1 as i64));
            w.step(cell, &mut h);
            r.step();
            prop_assert_eq!(h, r.heading);
            let (dx, dy) = DIRS[h as usize];
            pos = (pos.0 + dx, pos.1 + dy);
            prop_assert_eq!(pos, r.pos);
        }
    }

    #[test]
    fn no_noise_is_the_reference_ant(rule in rule_strategy(), seed in any::<u64>()) {
        let mut w = HybridWalker::new(&rule, seed, 0.0, 0.0);
        let mut ant = Ant::new(rule);
        let mut cells: HashMap<(i32, i32), u8> = HashMap::new();
        let mut h = 0u8;
        for _ in 0..20_000 {
            let p = ant.pos;
            let cell = cells.entry(p).or_insert(0);
            w.step(cell, &mut h);
            ant.step();
            prop_assert_eq!(h, ant.heading);
            prop_assert_eq!(*cells.get(&p).unwrap() & 0x7f, ant.colour_at(p));
        }
    }
}

#[test]
fn no_noise_probe_equals_ant_probe() {
    for (rule, seed) in [("RL", 0), ("RLR", 7), ("RRLLLRLRRRLL", 2026102601), ("RRRLLLLR", 3)] {
        let rule: Rule = rule.parse().unwrap();
        let a = probe(&rule, 1024, 8, 18);
        let b = probe_walker(HybridWalker::new(&rule, seed, 0.0, 0.0), 1024, 8, 18);
        assert_eq!(a.windows, b.windows, "{rule}");
        assert_eq!(a.escaped, b.escaped);
    }
}

#[test]
fn full_noise_is_persistent_walk_half() {
    for seed in [1u64, 2026102601, u64::MAX] {
        for rule in ["RL", "RLR", "RRRRLLLLLLLR"] {
            let a = probe_walker(PersistentWalk::new(seed, 0.5), 2048, 8, 18);
            let b = probe_walker(HybridWalker::new(&rule.parse().unwrap(), seed, 1.0, 1.0), 2048, 8, 18);
            assert_eq!(a.windows, b.windows, "{rule} {seed}");
            assert_eq!(a.escaped, b.escaped);
        }
    }
}

#[test]
fn revisit_noise_only_is_rule_free() {
    for seed in [1u64, 2026102601] {
        let base = probe_walker(HybridWalker::new(&"RL".parse().unwrap(), seed, 1.0, 0.0), 2048, 8, 18);
        for rule in ["RL", "RLR", "RLRLLRRRRRRR", "RRRRLLLLLLLR"] {
            let b = probe_walker(HybridWalker::new(&rule.parse().unwrap(), seed, 1.0, 0.0), 2048, 8, 18);
            assert_eq!(base.windows, b.windows, "{rule} {seed}");
        }
        // The control: removing the wall changes the trajectory.
        let nowall = probe_walker(HybridWalker::new(&"RL".parse().unwrap(), seed, 1.0, 1.0), 2048, 8, 18);
        assert_ne!(base.windows, nowall.windows);
    }
}

/// Inverse of `mix64` (xorshift-multiply steps undone in reverse), so a test can aim a draw.
fn unmix64(z: u64) -> u64 {
    fn unxorshift(z: u64, s: u32) -> u64 {
        let mut x = z;
        for _ in 0..(64 / s + 1) {
            x = z ^ (x >> s);
        }
        x
    }
    fn inverse(a: u64) -> u64 {
        let mut x = a;
        for _ in 0..6 {
            x = x.wrapping_mul(2u64.wrapping_sub(a.wrapping_mul(x)));
        }
        x
    }
    let z = unxorshift(z, 31);
    let z = unxorshift(z.wrapping_mul(inverse(0x94D0_49BB_1331_11EB)), 27);
    unxorshift(z.wrapping_mul(inverse(0xBF58_476D_1CE4_E5B9)), 30)
}

/// Seed whose first draw has the given low 32 bits (high bits: `high`).
fn seed_for_first_draw(low32: u64, high: u64) -> u64 {
    let seed = unmix64((high << 32) | low32).wrapping_sub(0x9E37_79B9_7F4A_7C15);
    let mut s = seed;
    assert_eq!(splitmix_next(&mut s), (high << 32) | low32);
    seed
}

/// The float-vs-floor discrepancy the review found: for non-dyadic eps the draw with
/// low32 == floor(eps * 2^32) is NOT noisy (strict `<`), while `low32 / 2^32 < eps` would say
/// it is. Aim the first draw at threshold - 1, threshold and threshold + 1 and check that the
/// first step (fresh cell, so `ef` applies) is noisy exactly for the first of them. With the
/// rule's colour-0 turn R, a noisy step with high32 >= 2^31 turns L, so noise is visible.
#[test]
fn noise_threshold_boundary_is_strict_integer_comparison() {
    let rule: Rule = "RL".parse().unwrap();
    for eps in [0.1, 0.3, 1.0 / 3.0, 0.01, 0.9] {
        let thr = noise_threshold32(eps);
        assert_eq!(thr, (eps * 4294967296.0).floor() as u64);
        assert!(thr < 1 << 32);
        for (low, noisy) in [(thr - 1, true), (thr, false), (thr + 1, false)] {
            let seed = seed_for_first_draw(low, 0xFFFF_FFFF); // high bits would pick L if noisy
            let mut w = HybridWalker::new(&rule, seed, 0.0, eps);
            let (mut cell, mut h) = (0u8, 0u8);
            w.step(&mut cell, &mut h);
            assert_eq!(h, if noisy { 3 } else { 1 }, "eps {eps} low32 {low}");
        }
    }
    // eps = 1 is always noisy, even at the largest possible low32; eps = 0 never is.
    let mut w = HybridWalker::new(&rule, seed_for_first_draw(0xFFFF_FFFF, 0xFFFF_FFFF), 0.0, 1.0);
    let (mut cell, mut h) = (0u8, 0u8);
    w.step(&mut cell, &mut h);
    assert_eq!(h, 3);
    let mut w = HybridWalker::new(&rule, seed_for_first_draw(0, 0xFFFF_FFFF), 0.0, 0.0);
    let (mut cell, mut h) = (0u8, 0u8);
    w.step(&mut cell, &mut h);
    assert_eq!(h, 1);
}
