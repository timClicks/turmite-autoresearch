//! `FreshSetWalker` (wall-vs-memory Stage 3c, gate T0') against an independent sparse reference
//! written from the README semantics; the identity `fs:RULE:RL:SEED` = F1 (`HybridWalker` with
//! ev = 0, ef = 1); the registered fresh-run bound for `RU`/`LU` (at most 4 cells, 5 for the run
//! that starts at the origin); and, as a non-vacuity control, a longer run for `RLU`.
use proptest::prelude::*;
use std::collections::{HashMap, HashSet};
use turmite::probe::probe_walker;
use turmite::walkers::{FreshSetWalker, HybridWalker, Walker, splitmix_next};
use turmite::{DIRS, Rule};

struct RefFreshSet {
    rule: Rule,
    set: Vec<u8>,
    colours: HashMap<(i32, i32), usize>,
    departed: HashSet<(i32, i32)>,
    pos: (i32, i32),
    heading: u8,
    rng: u64,
}

impl RefFreshSet {
    fn new(rule: Rule, set: &str, seed: u64) -> RefFreshSet {
        let set = set.chars().map(|c| match c { 'R' => 1, 'L' => 3, 'U' => 2, _ => unreachable!() }).collect();
        RefFreshSet { rule, set, colours: HashMap::new(), departed: HashSet::new(), pos: (0, 0), heading: 0, rng: seed }
    }

    /// One step; returns whether it was taken from a fresh cell.
    fn step(&mut self) -> bool {
        let r = splitmix_next(&mut self.rng);
        // uniform index from the high 32 bits, restated as a fraction of 2^32
        let u = (r >> 32) as f64 / 4294967296.0;
        let fresh = !self.departed.contains(&self.pos);
        let c = *self.colours.get(&self.pos).unwrap_or(&0);
        let turn = if fresh { self.set[(u * self.set.len() as f64).floor() as usize] } else { self.rule.0[c].delta() };
        self.heading = (self.heading + turn) % 4;
        self.colours.insert(self.pos, (c + 1) % self.rule.len());
        self.departed.insert(self.pos);
        let (dx, dy) = DIRS[self.heading as usize];
        self.pos = (self.pos.0 + dx, self.pos.1 + dy);
        fresh
    }
}

fn rule_strategy() -> impl Strategy<Value = Rule> {
    (2usize..=12).prop_flat_map(|n| (0u32..(1 << n)).prop_map(move |b| Rule::from_bits(b, n)))
}

fn set_strategy() -> impl Strategy<Value = &'static str> {
    prop_oneof![Just("RU"), Just("LU"), Just("RL"), Just("RLU"), Just("R"), Just("U")]
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 96, rng_seed: proptest::test_runner::RngSeed::Fixed(20261028), ..ProptestConfig::default() })]

    #[test]
    fn matches_sparse_reference_and_bounds_fresh_runs(rule in rule_strategy(), set in set_strategy(), seed in any::<u64>()) {
        let mut w = FreshSetWalker::new(&rule, set, seed);
        let mut r = RefFreshSet::new(rule, set, seed);
        let mut cells: HashMap<(i32, i32), u8> = HashMap::new();
        let (mut pos, mut h) = ((0i32, 0i32), 0u8);
        let bounded = !(set.contains('R') && set.contains('L'));
        let (mut run, mut first_run_over) = (0usize, false);
        for _ in 0..20_000 {
            let cell = cells.entry(pos).or_insert_with(|| w.initial_cell(pos.0 as i64, pos.1 as i64));
            w.step(cell, &mut h);
            let fresh = r.step();
            prop_assert_eq!(h, r.heading);
            let (dx, dy) = DIRS[h as usize];
            pos = (pos.0 + dx, pos.1 + dy);
            prop_assert_eq!(pos, r.pos);
            if fresh { run += 1 } else { first_run_over = true; run = 0 }
            if bounded {
                prop_assert!(run <= if first_run_over { 4 } else { 5 }, "fresh run {} for {}", run, set);
            }
        }
    }

    #[test]
    fn rl_is_f1(rule in rule_strategy(), seed in any::<u64>()) {
        let mut a = FreshSetWalker::new(&rule, "RL", seed);
        let mut b = HybridWalker::new(&rule, seed, 0.0, 1.0);
        let mut ca: HashMap<(i32, i32), u8> = HashMap::new();
        let mut cb: HashMap<(i32, i32), u8> = HashMap::new();
        let (mut pa, mut ha, mut pb, mut hb) = ((0i32, 0i32), 0u8, (0i32, 0i32), 0u8);
        for _ in 0..20_000 {
            a.step(ca.entry(pa).or_insert(0), &mut ha);
            b.step(cb.entry(pb).or_insert(0), &mut hb);
            prop_assert_eq!(ha, hb);
            let (dx, dy) = DIRS[ha as usize];
            pa = (pa.0 + dx, pa.1 + dy);
            pb = (pb.0 + dx, pb.1 + dy);
        }
    }
}

#[test]
fn rl_probe_equals_f1_probe() {
    for (rule, seed) in [("RL", 1u64), ("RRLLLRLRRRLL", 2026102601), ("RRRLLLLR", 2026102602)] {
        let rule: Rule = rule.parse().unwrap();
        let a = probe_walker(FreshSetWalker::new(&rule, "RL", seed), 1024, 8, 18);
        let b = probe_walker(HybridWalker::new(&rule, seed, 0.0, 1.0), 1024, 8, 18);
        assert_eq!(a.windows, b.windows, "{rule}");
        assert_eq!(a.escaped, b.escaped);
    }
}

/// Non-vacuity: the unbounded sets do produce fresh runs longer than the bounded sets' maximum.
#[test]
fn rlu_has_long_fresh_runs() {
    let rule: Rule = "RRLLLRLRRRLL".parse().unwrap();
    let mut r = RefFreshSet::new(rule, "RLU", 2026102601);
    let (mut run, mut longest) = (0usize, 0usize);
    for _ in 0..200_000 {
        run = if r.step() { run + 1 } else { 0 };
        longest = longest.max(run);
    }
    assert!(longest > 5, "longest fresh run {longest}");
}
