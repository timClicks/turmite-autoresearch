//! `HybridWalker` (wall-vs-memory experiment) against an independent sparse reference written
//! from the README semantics, plus the three exact corner identities the experiment relies on:
//! no noise is the ant, full noise is `PersistentWalk` at q = 0.5, and revisit-only noise is the
//! same trajectory for every rule that turns R on colour 0.
use proptest::prelude::*;
use std::collections::{HashMap, HashSet};
use turmite::probe::{probe, probe_walker};
use turmite::reference::Ant;
use turmite::walkers::{HybridWalker, PersistentWalk, Walker, splitmix_next};
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
        let u_noise = (r & 0xFFFF_FFFF) as f64 / 4294967296.0;
        let u_dir = (r >> 32) as f64 / 4294967296.0;
        let fresh = !self.departed.contains(&self.pos);
        let eps = if fresh { self.ef } else { self.ev };
        let c = *self.colours.get(&self.pos).unwrap_or(&0);
        let turn = if u_noise < eps { if u_dir < 0.5 { 1 } else { 3 } } else { self.rule.0[c].delta() };
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
